from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
import pyotp
from django.utils.translation import gettext_lazy as _

from user.models import User

from post_office import mail


def time_elapsed(last_time_str, duration=90):
    last_time = datetime.fromisoformat(last_time_str) if last_time_str else None
    if last_time and (timezone.now() - last_time).seconds < duration:
        time_remaining = duration - (timezone.now() - last_time).seconds
        return time_remaining


class FirstStepTokenView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        last_email_sent_time = request.session.get("last_email_sent_time")
        time_remaining = time_elapsed(last_email_sent_time)

        if user.primary_verification_method is None:
            return generate_tokens(user)
        elif user.primary_verification_method == "EMAIL":
            if time_remaining is not None:
                return Response({"detail": _(f"Please wait {time_remaining} seconds before sending another email")})
            send_email(user)
            request.session["last_email_sent_time"] = timezone.now().isoformat()
            self.set_session_data(request, user.id, user.primary_verification_method)
            return Response({
                "detail": _(
                    "A verification email has been sent to your registered email address. Please check your inbox and follow the instructions to complete the second step of authentication.")})
        else:
            self.set_session_data(request, user.id, user.primary_verification_method)
            return Response({
                "detail": _(
                    "Second step of authentication is required. Please use the authenticator app to complete the verification process.")})

    @staticmethod
    def set_session_data(request, user_id, verification_method):
        request.session["user_id"] = user_id
        request.session["verification_method"] = verification_method
        request.session.set_expiry(600)


class SecondStepTokenView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        user_id = request.session.get("user_id")
        verification_method = request.session.get("verification_method")
        last_email_sent_time = request.session.get("last_email_sent_time")

        time_remaining = time_elapsed(last_email_sent_time)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        chosen_method = request.data.get("chosen_method")
        resend_email = request.data.get("resend_email")
        if verification_method == "EMAIL" and resend_email:
            if time_remaining is not None:
                return Response({"detail": _(f"Please wait {time_remaining} seconds before resending email")})
            send_email(user)
            request.session["last_email_sent_time"] = timezone.now().isoformat()
            return Response({"detail": _("Email resent for verification")})
        elif chosen_method:
            return self.handle_chosen_method(chosen_method, verification_method, user, time_remaining)

        self.verify_token(verification_method, user, request.data)
        request.session.flush()
        return generate_tokens(user)

    def handle_chosen_method(self, chosen_method, verification_method, user, time_remaining=None):
        enabled_methods = {"OTP": user.otp_enabled, "EMAIL": user.email_verification_enabled,
                           "BACKUP": bool(user.backup_tokens)}
        if chosen_method not in ["OTP", "EMAIL", "BACKUP"]:
            raise AuthenticationFailed(_("Invalid chosen method"))
        elif chosen_method == verification_method:
            raise AuthenticationFailed(_(f"Already using {chosen_method}"))
        elif not enabled_methods.get(chosen_method, False):
            raise AuthenticationFailed(_(f"{chosen_method} method is not available"))
        elif chosen_method == "EMAIL" and time_remaining is None:
            send_email(user)
            self.request.session["last_email_sent_time"] = timezone.now().isoformat()
        session_expiry = self.request.session.get_expiry_date()
        self.request.session["verification_method"] = chosen_method
        self.request.session.set_expiry(session_expiry)
        return Response({"detail": _(f"Chosen method for verification: {chosen_method}")})

    def verify_token(self, verification_method, user, data):
        if verification_method == "OTP":
            self.verify_otp(user, data.get("token"))
        elif verification_method == "EMAIL":
            self.verify_email(user, data.get("token"))
        elif verification_method == "BACKUP":
            self.verify_backup(user, data.get("token"))

    @staticmethod
    def verify_otp(user, otp_token):
        totp = pyotp.TOTP(user.otp_base32)
        if not totp.verify(otp_token):
            raise AuthenticationFailed(_("Invalid OTP token"))

    @staticmethod
    def verify_email(user, email_token):
        totp = pyotp.TOTP(user.email_base32)
        if not totp.verify(email_token, valid_window=4):
            raise AuthenticationFailed(_("Invalid email token"))

    @staticmethod
    def verify_backup(user, backup_token):
        saved_backup_tokens = user.backup_tokens.split("|") if user.backup_tokens else []
        if backup_token not in saved_backup_tokens:
            raise AuthenticationFailed(_("Invalid backup token"))
        saved_backup_tokens.remove(backup_token)
        user.backup_tokens = "|".join(saved_backup_tokens)
        user.save()


def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    response_data = {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
    return Response(response_data)


def send_email(user):
    secret = user.email_base32
    email_otp = pyotp.TOTP(secret)
    token = email_otp.now()

    subject = _("Login Token")
    message = _(f"To login, please use this token: {token}")
    recipient_list = [user.email]

    try:
        mail.send(subject=subject, message=message, sender=settings.EMAIL_HOST_USER, recipients=recipient_list)
        # send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
        return True
    except Exception as e:
        print(_(f"Email sending failed: {e}"))
        return False
