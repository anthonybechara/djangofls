from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user_resume.views import UserEducationViewSet, UserReviewViewSet, UserSkillsViewSet, UserPortfolioViewSet, \
    UserPortfolioFileDelete, UserExperienceViewSet, UserSavedProjectViewSet, UserStatisticsViewSet

router = DefaultRouter()
router.register("user-educations", UserEducationViewSet, basename="user-educations")
router.register("user-skills", UserSkillsViewSet, basename="user-skills")
router.register("user-experience", UserExperienceViewSet, basename="user-experience")
router.register("user-portfolio", UserPortfolioViewSet, basename="user-portfolio")
router.register("user-saved-project", UserSavedProjectViewSet, basename="user-saved-project")
router.register("user-reviews", UserReviewViewSet, basename="user-reviews")
router.register("user-statistics", UserStatisticsViewSet, basename="user-statistics")

urlpatterns = [
    path("", include(router.urls)),
    path("prev-workfile/<int:pk>/", UserPortfolioFileDelete.as_view(), name="portfolio-file"),
]
