from django.contrib import admin

from education.models import Skill, Degree, Major, University


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)


@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
