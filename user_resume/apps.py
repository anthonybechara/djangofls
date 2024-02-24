from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UserResumeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_resume"
    verbose_name = _("User Resume Application")
