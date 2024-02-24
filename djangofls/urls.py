from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from django.apps import apps

from user.authentication import FirstStepTokenView, SecondStepTokenView

main_router = routers.DefaultRouter()
app_configs = list(apps.get_app_configs())

for app_config in app_configs:
    try:
        urls_module = app_config.module.__name__ + '.urls'
        urls = __import__(urls_module, fromlist=['router'])
        if hasattr(urls, 'router'):
            app_router = getattr(urls, 'router')
            main_router.registry.extend(app_router.registry)
    except ImportError:
        pass

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("", include(main_router.urls)),

    path("", include("user.urls")),
    path("", include("user_resume.urls")),
    path("", include("project.urls")),
    path("", include("chat.urls")),
    path("", include("payment.urls")),

    path("jwt/login/", FirstStepTokenView.as_view(), name="jwt-login-1"),
    path("jwt/login/token/", SecondStepTokenView.as_view(), name="jwt-login-2"),

    # path("jwt/create/", views.TokenObtainPairView.as_view(), name="jwt-create"),
    # path("jwt/refresh/", views.TokenRefreshView.as_view(), name="jwt-refresh"),
    # path("jwt/verify/", views.TokenVerifyView.as_view(), name="jwt-verify"),

]

urlpatterns += [
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
