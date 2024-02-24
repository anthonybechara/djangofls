from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, status, generics, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from user_resume import permissions
from user_resume.models import UserEducation, UserReview, UserSkill, UserPortfolio, PortfolioFile, UserExperience, \
    UserStatistics, UserSavedProject
from user_resume.pagination import ReviewPagination
from user_resume.serializers import UserEducationSerializer, UserReviewSerializer, UserSkillSerializer, \
    UserPortfolioSerializer, PortfolioFileSerializer, UserExperienceSerializer, UserSavedProjectSerializer, \
    UserStatisticSerializer


class UserEducationViewSet(viewsets.ModelViewSet):
    queryset = UserEducation.objects.all()
    serializer_class = UserEducationSerializer
    permission_classes = [permissions.CurrentUser]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == "list":
            queryset = queryset.filter(user=user)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class UserSkillsViewSet(viewsets.ModelViewSet):
    queryset = UserSkill.objects.all()
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.CurrentUser]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == "list":
            queryset = queryset.filter(user=user)
        return queryset

    def create(self, request, *args, **kwargs):
        existing_skills = UserSkill.objects.filter(user=request.user)
        if existing_skills.exists():
            return Response({"detail": _("User already has skills. Cannot create new skills.")},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class UserPortfolioViewSet(viewsets.ModelViewSet):
    queryset = UserPortfolio.objects.all()
    serializer_class = UserPortfolioSerializer
    permission_classes = [permissions.CurrentUser]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == "list":
            queryset = queryset.filter(user=user)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class UserPortfolioFileDelete(generics.DestroyAPIView):
    queryset = PortfolioFile.objects.all()
    serializer_class = PortfolioFileSerializer
    permission_classes = [permissions.PortfolioFileDelete]


class UserExperienceViewSet(viewsets.ModelViewSet):
    queryset = UserExperience.objects.all()
    serializer_class = UserExperienceSerializer
    permission_classes = [permissions.CurrentUser]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if self.action == "list":
            queryset = queryset.filter(user=user)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class UserSavedProjectViewSet(mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              GenericViewSet):
    serializer_class = UserSavedProjectSerializer
    permission_classes = [permissions.CurrentUser]
    pagination_class = ReviewPagination

    def get_queryset(self):
        user = self.request.user
        return UserSavedProject.objects.filter(user=user, project__status="active")


class UserReviewViewSet(mixins.ListModelMixin,
                        GenericViewSet):
    serializer_class = UserReviewSerializer
    permission_classes = [permissions.CurrentUser]
    pagination_class = ReviewPagination

    def get_queryset(self):
        user = self.request.user
        if self.action == "is_freelancer":
            return UserReview.objects.filter(reviewed_user=user, reviewed_user_title="freelancer")
        elif self.action == "is_client":
            return UserReview.objects.filter(reviewed_user=user, reviewed_user_title="client")
        else:
            return UserReview.objects.filter(reviewer=user)

    @action(detail=False, methods=["GET"])
    def is_freelancer(self, request):
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serialized_reviews = self.get_serializer(page, many=True)
            return self.get_paginated_response(serialized_reviews.data)
        else:
            serialized_reviews = self.get_serializer(self.get_queryset(), many=True)
            return Response(serialized_reviews.data)

    @action(detail=False, methods=["GET"])
    def is_client(self, request):
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serialized_reviews = self.get_serializer(page, many=True)
            return self.get_paginated_response(serialized_reviews.data)
        else:
            serialized_reviews = self.get_serializer(self.get_queryset(), many=True)
            return Response(serialized_reviews.data)


class UserStatisticsViewSet(mixins.ListModelMixin,
                            GenericViewSet):
    serializer_class = UserStatisticSerializer
    permission_classes = [permissions.CurrentUser]

    def get_queryset(self):
        user = self.request.user
        return UserStatistics.objects.filter(user=user)
