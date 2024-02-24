from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User, UserProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    readonly_fields = ("created_date", "modified_date", "last_login", "last_logout")
    list_display = (
        "id", "username", "email", "first_name", "last_name", "is_online", "is_active",
        "is_admin", "is_superuser", "last_login", "last_logout")

    list_display_links = ["id", "username", "email"]

    list_filter = ("is_admin", "is_superuser", "is_active", "groups")

    fieldsets = (
        (None, {
            "fields": ("first_name", "last_name", "username", "email", "password", "slug")
        }),

        ("Two Factor Authentication", {
            "fields": (
                "primary_verification_method", "email_verification_enabled", "email_base32", "otp_enabled",
                "otp_base32", "otp_auth_url", "backup_enabled", "backup_tokens"),
        }),

        ("Email Change", {
            "fields": ("new_email", "new_email_modified")
        }),

        ("Permissions", {
            "fields": ("is_online", "is_active", "is_admin", "is_superuser", "groups", "user_permissions")
        }),
        ("Dates", {
            "fields": ("created_date", "modified_date", "last_login", "last_logout")
        }),
    )

    add_fieldsets = (
        (None,
         {"fields": (
             "first_name", "last_name", "username", "email", "password1", "password2")}),
    )

    search_fields = ("username", "email", "first_name", "last_name")

    ordering = ("first_name",)

    filter_horizontal = ("user_permissions", "groups")


admin.site.site_header = "Admin"
admin.site.site_title = "Admin"
admin.site.index_title = "Welcome To the Admin Page"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "middle_name", "age", "birth_date", "gender", "avg_rating_and_reviews_as_freelancer",
        "avg_rating_and_reviews_as_client")
    list_filter = ("gender",)
    search_fields = ("user__username", "user__first_name", "user__last_name")
