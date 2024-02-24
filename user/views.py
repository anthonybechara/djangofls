import secrets
import string

import pyotp

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework import permissions as drf_permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from user.models import UserProfile
from . import permissions
from user.serializers import EmailChangeSerializer, UserCreateSerializer, ResendAccountActivationSerializer, \
    PasswordChangeSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, PasswordSerializer, \
    UserSerializer, UserDeletionSerializer, UserProfileSerializer, User2FA, Token, TwoFactorMethods

from post_office import mail


User = get_user_model()


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.CurrentUserOrAdmin]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == "list":
            queryset = queryset.filter(pk=user.pk)
        return queryset

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [permissions.IsNotAuthenticated]
        elif self.action == "partial_update" or self.action == "update" or self.action == "retrieve":
            self.permission_classes = [permissions.CurrentUserOrAdmin]
        elif self.action == "resend_activation":
            self.permission_classes = [permissions.IsNotAuthenticated]
        elif self.action == "change_password":
            self.permission_classes = [permissions.CurrentUserOrAdmin]
        elif self.action == "change_email":
            self.permission_classes = [permissions.CurrentUserOrAdmin]
        elif self.action == "reset_password":
            self.permission_classes = [permissions.IsNotAuthenticated]
        elif self.action == "reset_password_confirm":
            self.permission_classes = [permissions.IsNotAuthenticated]
        elif self.action == "delete_user":
            self.permission_classes = [permissions.CurrentUserOrAdmin]
        elif self.action == "deactivate_user":
            self.permission_classes = [permissions.CurrentUserOrAdmin]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "resend_activation":
            return ResendAccountActivationSerializer
        elif self.action == "change_password":
            return PasswordChangeSerializer
        elif self.action == "change_email":
            return EmailChangeSerializer
        elif self.action == "reset_password":
            return PasswordResetSerializer
        elif self.action == "reset_password_confirm":
            return PasswordResetConfirmSerializer
        elif self.action == "delete_user" or self.action == "deactivate_user":
            return UserDeletionSerializer
        return self.serializer_class

    def send_email(self, user, email_type):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(self.request)

        subject = ""
        message = ""

        if email_type == "account_activation":
            link = f"http://{current_site.domain}/activate-account/{uid}/{token}/"
            subject = _("Activate Your Account")
            message = _("To activate your account, please click the following link:")
            message = f"{message}\n{link}"
        elif email_type == "email_verification":
            link = f"http://{current_site.domain}/verify-email/{uid}/{token}/"
            subject = _("Verify your email address")
            message = _("To verify your new email, please click the following link:")
            message = f"{message}\n{link}"
        elif email_type == "reset_password":
            link = f"http://{current_site.domain}/password-reset/{uid}/{token}"
            subject = _("Password Reset")
            message = _("To reset your password, please click the following link:")
            message = f"{message}\n{link}"

        recipient_list = [user.email]

        try:
            mail.send(subject=subject, message=message, sender=settings.EMAIL_HOST_USER, recipients=recipient_list)
            return True
        except Exception as e:
            print(_(f"Email sending failed: {e}"))
            return False

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        self.send_email(user, "account_activation")

    # @action(["get", "put", "patch"], detail=False)
    # def user(self, request, *args, **kwargs):
    #     user = self.request.user
    #     serializer = self.get_serializer(user)
    #     serializerp = self.get_serializer(user, data=request.data)
    #     if request.method == "GET":
    #         return Response(serializer.data)
    #     if request.method in ["PUT", "PATCH"]:
    #         if serializerp.is_valid():
    #             serializerp.save()
    #             return Response(serializerp.data)
    #         return Response(serializerp.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(["delete"], detail=False)
    def delete_user(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        user.delete()
        if not user:
            return Response({"user": _("User Not Found.")}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"account": _("Account Deleted.")}, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def deactivate_user(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.is_active = False
        self.request.user.save()
        if not self.request.user:
            return Response({"user": _("No active user found.")}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"account": _("Deactivation Done.")}, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def resend_activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user(is_active=False)
        if not user:
            return Response({"user": _("No inactive user found.")}, status=status.HTTP_400_BAD_REQUEST)
        self.send_email(user, "account_activation")
        return Response({"email": _("Activation email resent.")}, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.validated_data["new_password"])
        self.request.user.save()
        return Response({"password": _("Password changed successfully.")}, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def change_email(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["new_email"]
        new_email = email.lower()
        user = self.request.user
        user.new_email = new_email
        user.save()
        self.send_email(user, "email_verification")
        return Response({"email": _("Verification email sent to the new email.")}, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"user": _("No user found with this email address.")}, status=status.HTTP_400_BAD_REQUEST)

        self.send_email(user, "reset_password")
        return Response({"email": _("Password reset instructions sent to your email.")}, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.user.set_password(serializer.validated_data["new_password"])
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.save()
        return Response({"password": _("Password reset successfully.")}, status=status.HTTP_200_OK)


class AccountVerificationView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()

            return Response({"account": _("Account verified successfully.")}, status=status.HTTP_200_OK)
        else:
            return Response({"error": _("Invalid activation link. Please contact support.")},
                            status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.email = user.new_email
            user.new_email = None
            user.save()

            return Response({"email": _("Email verified successfully.")}, status=status.HTTP_200_OK)
        else:
            return Response({"error": _("Invalid activation link. Please contact support.")},
                            status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(GenericAPIView):
    serializer_class = PasswordSerializer
    permission_classes = [drf_permissions.AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data["new_password"])
            if hasattr(user, "last_login"):
                user.last_login = now()
            user.save()
            return Response({"password": _("Password reset successfully.")}, status=status.HTTP_200_OK)

        else:
            return Response({"error": _("Invalid reset link. Please contact support.")},
                            status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.CurrentUserOrAdmin]

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = [permissions.ReadOnlyPortfolio]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == "list":
            queryset = queryset.filter(user=user)
        return queryset


class UserTwoFactorAuthentication(mixins.ListModelMixin,
                                  GenericViewSet):
    serializer_class = User2FA
    permission_classes = [permissions.CurrentUserOrAdmin]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(pk=user.pk)

    def get_permissions(self):
        if self.action == "activate_2fa_otp" or self.action == "verify_2fa_otp" \
                or self.action == "activate_2fa_email" or self.action == "verify_2fa_email":
            self.permission_classes = [permissions.Is2FAEnabled]
        elif self.action == "change_primary_method":
            self.permission_classes = [permissions.BothMethodsEnabled]
        elif self.action == "deactivate_2fa" or self.action == "backup_tokens":
            self.permission_classes = [permissions.IsNotOTPEnabled]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "verify_2fa_email" or self.action == "verify_2fa_otp":
            return Token
        elif self.action == "change_primary_method" or self.action == "deactivate_2fa":
            return TwoFactorMethods
        return super().get_serializer_class()

    @staticmethod
    def send_email(user, token):
        subject = _("Activate Two-Factor Authentication using Email")
        message = _(f"To activate Two-Factor Authentication using Email, please use this token: {token}")
        recipient_list = [user.email]
        try:
            mail.send(subject=subject, message=message, sender=settings.EMAIL_HOST_USER, recipients=recipient_list)
            return True
        except Exception as e:
            print(_(f"Email sending failed: {e}"))
            return False

    @staticmethod
    def generate_backup_tokens():
        tokens = [''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10)) for _ in range(10)]
        return '|'.join(tokens)

    @action(["post"], detail=False)
    def activate_2fa_email(self, request, *args, **kwargs):
        user = self.request.user
        email_secret = pyotp.random_base32()
        user.email_base32 = email_secret
        user.save()
        email_otp = pyotp.TOTP(email_secret)
        if self.send_email(user, email_otp.now()):
            return Response({"email_sent": True})
        return Response({"email_sent": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(["post"], detail=False)
    def verify_2fa_email(self, request, *args, **kwargs):
        user = self.request.user
        email_token = request.data.get("token", None)
        totp = pyotp.TOTP(user.email_base32)
        if not totp.verify(email_token, valid_window=4):
            return Response({"status": _("fail"), "message": _("Token is invalid")}, status=status.HTTP_400_BAD_REQUEST)
        user.email_verification_enabled = True
        if user.primary_verification_method is None:
            user.primary_verification_method = "EMAIL"
            backup_tokens = self.generate_backup_tokens()
            user.backup_tokens = backup_tokens
            user.backup_enabled = True
        user.save()
        serializer = self.serializer_class(user)
        return Response({"email_verified": True, "user": serializer.data})

    @action(["post"], detail=False)
    def activate_2fa_otp(self, request, *args, **kwargs):
        user = self.request.user
        otp_base32 = pyotp.random_base32()
        otp_auth_url = pyotp.totp.TOTP(otp_base32).provisioning_uri(name=user.email.lower(), issuer_name="")
        user.otp_auth_url = otp_auth_url
        user.otp_base32 = otp_base32
        user.save()
        return Response({"base32": otp_base32, "otpauth_url": otp_auth_url})

    @action(["post"], detail=False)
    def verify_2fa_otp(self, request, *args, **kwargs):
        user = self.request.user
        otp_token = request.data.get("token", None)
        totp = pyotp.TOTP(user.otp_base32)
        if not totp.verify(otp_token):
            return Response({"status": _("fail"), "message": _("Token is invalid")}, status=status.HTTP_400_BAD_REQUEST)
        user.otp_enabled = True
        if user.primary_verification_method is None:
            user.primary_verification_method = "OTP"
            backup_tokens = self.generate_backup_tokens()
            user.backup_tokens = backup_tokens
            user.backup_enabled = True
        user.save()
        serializer = self.serializer_class(user)
        return Response({"otp_verified": True, "user": serializer.data})

    @action(["post", "get"], detail=False)
    def backup_tokens(self, request, *args, **kwargs):
        user = self.request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response({"backup_tokens": serializer.data["backup_tokens"]})
        else:
            tokens_serializer = self.generate_backup_tokens()
            tokens = tokens_serializer.split("|")
            user.backup_tokens = tokens_serializer
            user.save()
            return Response({"backup_tokens": tokens})

    @action(["post", "get"], detail=False)
    def change_primary_method(self, request, *args, **kwargs):
        user = self.request.user
        if request.method == "GET":
            serializer = user.primary_verification_method
            return Response({"primary_verification_method": serializer})
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            selected_method = serializer.validated_data["type"]

            if user.otp_enabled and user.email_verification_enabled:
                if selected_method == "OTP" and user.primary_verification_method != "OTP":
                    user.primary_verification_method = "OTP"
                    user.save()
                    return Response({"primary_method_changed": _("OTP"), "user": self.serializer_class(user).data})
                elif selected_method == "EMAIL" and user.primary_verification_method != "EMAIL":
                    user.primary_verification_method = "EMAIL"
                    user.save()
                    return Response({"primary_method_changed": _("EMAIL"), "user": self.serializer_class(user).data})
                else:
                    return Response({"primary_method": _(f"already {selected_method} is selected")})

    @action(["post"], detail=False)
    def deactivate_2fa(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected_2fa = request.data.get("type", None)
        if selected_2fa == "OTP":
            user.otp_enabled = False
            user.otp_base32 = None
            user.otp_auth_url = None
            if user.primary_verification_method == "OTP" and user.email_verification_enabled:
                user.primary_verification_method = "EMAIL"
            elif user.primary_verification_method == "OTP" and not user.email_verification_enabled:
                user.primary_verification_method = None
                user.backup_tokens = None
                user.backup_enabled = False
            user.save()
            return Response({"otp_disabled": True, "user": self.serializer_class(user).data})
        elif selected_2fa == "EMAIL":
            user.email_verification_enabled = False
            user.email_base32 = None
            if user.primary_verification_method == "EMAIL" and user.otp_enabled:
                user.primary_verification_method = "OTP"
            elif user.primary_verification_method == "EMAIL" and not user.otp_enabled:
                user.primary_verification_method = None
                user.backup_tokens = None
                user.backup_enabled = False
            user.save()
            return Response({"email_disabled": True, "user": self.serializer_class(user).data})

# class SimplePasswordResetTokenGenerator:
#     key_salt = "simple_password_reset_token_generator"
#     expiry_duration = timedelta(minutes=3)
#
#     def make_token(self, user):
#         timestamp = int((datetime.now() - datetime(2001, 1, 1)).total_seconds())
#         token = random.randint(100000, 999999)
#         return f"{timestamp}-{token}"
#
#     def check_token(self, user, token):
#         if not (user and token):
#             return False
#         try:
#             ts_str, token_str = token.split("-")
#             timestamp = int(ts_str)
#             if (datetime.now() - datetime(2001, 1, 1)) - timedelta(seconds=timestamp) > self.expiry_duration:
#                 return False
#             if len(token_str) != 6 or not token_str.isdigit():
#                 return False
#         except (ValueError, TypeError):
#             return False
#
#         return True
#
#
# token_generator = SimplePasswordResetTokenGenerator()
