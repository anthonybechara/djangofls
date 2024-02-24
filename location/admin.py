from django.contrib import admin

from location.models import Nationality, Location


@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ("id", "nationality",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "city", "country")
