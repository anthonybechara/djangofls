from django.urls import path, include
from rest_framework.routers import DefaultRouter

from project.views import ProjectViewSet, UserProjectFileDelete, UserProjectProposalViewSet, UserProjectViewSet, \
    CompleteReviewViewSet

router = DefaultRouter()
router.register("project", ProjectViewSet, basename="projects")
router.register("user-project", UserProjectViewSet, basename="user-projects")
router.register("user-proposal", UserProjectProposalViewSet, basename="user-proposals")
router.register("complete-review", CompleteReviewViewSet, basename="complete-review")

urlpatterns = [
    path("", include(router.urls)),
    path("projectfile/<int:pk>/", UserProjectFileDelete.as_view(), name="proj-file-detail"),
]
