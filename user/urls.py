from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import UserViewSet, AccountVerificationView, EmailVerificationView, PasswordResetView, \
    UserTwoFactorAuthentication
from user.views import UserProfileViewSet

router = DefaultRouter()
router.register("user", UserViewSet, basename="user")
router.register("user-profile", UserProfileViewSet, basename="user-profile")
router.register("user-2fa", UserTwoFactorAuthentication, basename="user-2fa")

urlpatterns = [
    path("", include(router.urls)),

    path("activate-account/<str:uidb64>/<str:token>/", AccountVerificationView.as_view(), name="user-verification"),
    path("verify-email/<str:uidb64>/<str:token>/", EmailVerificationView.as_view(), name="email-verification"),
    path("password-reset/<str:uidb64>/<str:token>/", PasswordResetView.as_view(), name="email-verification"),

]
