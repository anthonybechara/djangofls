from django.contrib import admin

from user_resume.models import UserEducation, UserSkill, UserReview, UserPortfolio, PortfolioFile, UserExperience, \
    UserStatistics, UserSavedProject


@admin.register(UserEducation)
class UserEducationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "start_date", "end_date")
    list_filter = ("university", "major", "degree")
    search_fields = ("user__username", "education__name")


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user",)


@admin.register(UserPortfolio)
class UserPortfolioAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "work_type", "title", "created_at")
    search_fields = ("user",)


@admin.register(PortfolioFile)
class PortfolioFileAdmin(admin.ModelAdmin):
    list_display = ("id", "file")


@admin.register(UserExperience)
class UserExperienceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "company_name", "position", "start_date", "end_date", "present")
    search_fields = ("user",)


@admin.register(UserSavedProject)
class UserSavedProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "project", "saved_time")
    search_fields = ("user",)


@admin.register(UserReview)
class UserReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "reviewer", "reviewed_user_title", "reviewed_user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("reviewed_user__username", "reviewer__username")


@admin.register(UserStatistics)
class UserStatisticsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_proposal", "projects_taken", "projects_taken_completed",
                    "projects_made", "projects_made_completed", "total_earning", "total_paid")
    search_fields = ("user",)
