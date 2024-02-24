from rest_framework import permissions
from django.utils.translation import gettext as _


class CurrentUserOrAdmin(permissions.IsAuthenticated):
    message = _("You dont have access to perform this action.")

    def has_object_permission(self, request, view, obj):
        return obj.pk == request.user.pk or request.user.is_admin


class IsNotAuthenticated(permissions.BasePermission):
    message = _("You must logout to perform this action.")

    def has_permission(self, request, view):
        return bool(not request.user.is_authenticated)


class ReadOnlyPortfolio(permissions.IsAuthenticated):
    message = _("You don't have access to perform this action.")

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.pk == request.user.pk


class Is2FAEnabled(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        activated_method = None
        if view.action in ['activate_2fa_email', 'verify_2fa_email'] and user.email_verification_enabled:
            activated_method = "Email"
        elif view.action in ['activate_2fa_otp', 'verify_2fa_otp'] and user.otp_enabled:
            activated_method = "OTP"
        if activated_method:
            self.message = _(f"{activated_method} is already enabled for two-factor authentication.")
            return False
        return True


class IsNotOTPEnabled(permissions.IsAuthenticated):
    message = _("OTP nor email are not enabled for this user.")

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if view.action == "backup_tokens" and not user.backup_enabled:
            self.message = _("Backup tokens are not enabled for this user.")
        return user.otp_enabled or user.email_verification_enabled


class BothMethodsEnabled(permissions.IsAuthenticated):
    message = "Both OTP and Email verification methods must be enabled to change the primary method."

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        return user.otp_enabled and user.email_verification_enabled
