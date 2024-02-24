from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, status, generics, permissions, mixins, filters
from rest_framework.reverse import reverse
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import GenericViewSet

from chat.models import ChatRoom
from payment.models import Bid, Point, TransactionLog
from project.models import Project, ProjectFile, ProjectProposal, ChosenProposal
from project.pagination import ProjectPagination

from project.permissions import ProjectProposals, ProjectFileDelete, IsNotProjectOwnerOrHasNotProposed, IsProposalOwner, \
    IsProjectOwner, ProjectAndProposalModification, CanMarkProjectAsComplete, CanReview, DisputePermission

from project.serializers import ProjectWithURLSerializer, ProjectFileSerializer, ProjectProposalCreateSerializer, \
    ProjectProposalDetailSerializer, ChoosingProposalSerializer, UserProjectSerializer, ChosenProposalSerializer, \
    ProjectSerializer, MarkCompleted, UserProjectInProgressSerializer, UserProjectProposalDetailSerializer, \
    CompleteReviewSerializer, SaveUnsavedSerializer, ProjectProposalSerializer, OpenDispute, \
    InProgressProposalDetailSerializer
from user.models import User
from user_resume.models import UserReview, UserSavedProject


class ProjectViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = ProjectWithURLSerializer
    permission_classes = [permissions.IsAuthenticated]
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["skill_needed"]
    search_fields = ["title", "skill_needed__name"]
    # ordering_fields = ["min_price", "max_price"]
    pagination_class = ProjectPagination

    def get_queryset(self):
        queryset = Project.objects.filter(status="active", published_user__isnull=False)
        if self.action == "list":
            queryset = Project.objects.filter(status="active").exclude(published_user=self.request.user)
            ordering = self.request.query_params.get("ordering", "-created")
            queryset = queryset.order_by(ordering)
        return queryset

    def filter_queryset(self, queryset):
        if self.action == "project_proposals":
            self.filterset_fields = []
            self.search_fields = []
        return super().filter_queryset(queryset)

    def get_permissions(self):
        if self.action == "create_project_proposal":
            self.permission_classes = [IsNotProjectOwnerOrHasNotProposed]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "project_proposals":
            return ProjectProposalDetailSerializer
        elif self.action == "create_project_proposal":
            return ProjectProposalCreateSerializer
        elif self.action == "Save_Unsaved":
            return SaveUnsavedSerializer
        return self.serializer_class

    @action(detail=True, methods=["get"])
    def project_proposals(self, request, pk=None):
        try:
            project = self.get_object()
            project_proposals = ProjectProposal.objects.filter(project=project, proposer__isnull=False)
            ordering = self.request.query_params.get("ordering", "-proposal_date")
            project_proposals = project_proposals.order_by(ordering)
            page = self.paginate_queryset(project_proposals)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            else:
                serializer = self.get_serializer(project_proposals, many=True)
                return Response(serializer.data)

        except Project.DoesNotExist:
            return Response({"error": _("Project not found")}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def create_project_proposal(self, request, pk=None):
        try:
            project = self.get_object()
            user = self.request.user

            serializer = self.get_serializer(data=request.data)
            user_bid = Bid.objects.get(user=request.user)
            if user_bid.nb_bid > 0:
                if serializer.is_valid():
                    serializer.save(project=project, proposer=user)
                    user_bid.nb_bid -= 1
                    user_bid.save()
                    TransactionLog.objects.create(user=user, transaction_type="BIDS_SPENT", amount=1,
                                                  description=f"Spent 1 bid to propose on '{project.title}' project.")
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": _("Insufficient bids")}, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({"error": _("Project not found")}, status=status.HTTP_404_NOT_FOUND)
        except Bid.DoesNotExist:
            return Response({"error": _("Bid not found")}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def Save_Unsaved(self, request, pk=None):
        user = self.request.user
        project = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            save_unsaved = serializer.validated_data.get("Save_Unsaved", False)
            try:
                saved_project = UserSavedProject.objects.get(user=user, project=project)
                if not save_unsaved:
                    saved_project.delete()
                    return Response({"message": _("Project unsaved")}, status=status.HTTP_200_OK)
            except UserSavedProject.DoesNotExist:
                if save_unsaved:
                    UserSavedProject.objects.create(user=user, project=project)
                    return Response({"message": _("Project saved")}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProjectViewSet(viewsets.ModelViewSet):
    serializer_class = UserProjectSerializer
    permission_classes = [IsProjectOwner, ProjectAndProposalModification]
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", "skill_needed"]
    search_fields = ["title"]
    # ordering_fields = ["due_date", "created"]
    pagination_class = ProjectPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Project.objects.filter(published_user=user) if not user.is_anonymous else None
        ordering = self.request.query_params.get("ordering", "-created")
        if self.action == "list":
            queryset = queryset.filter(status="active")
            queryset = queryset.order_by(ordering)
        elif self.action == "expired_project":
            queryset = queryset.filter(status="expired")
            queryset = queryset.order_by(ordering)
        elif self.action == "complete":
            queryset = queryset.filter(status="in_progress")
        return queryset

    def filter_queryset(self, queryset):
        if self.action == "project_proposals":
            self.filterset_fields = []
            self.search_fields = []
        elif self.action in ["in_progress_project", "canceled_project", "completed_project"]:
            self.filterset_fields = ["skill_needed"]
            self.search_fields = ["title"]
        return super().filter_queryset(queryset)

    def get_permissions(self):
        # if self.action == "upload_file":
        #     self.permission_classes = [IsProjectOwnerFileUpload]
        if self.action == "project_proposals":
            self.permission_classes = [ProjectProposals]
        elif self.action == "complete":
            self.permission_classes = [CanMarkProjectAsComplete]
        elif self.action == "dispute":
            self.permission_classes = [DisputePermission]
        return super().get_permissions()

    def get_serializer_class(self):
        # if self.action == "upload_file":
        #     return ProjectFileSerializer
        if self.action == "project_proposals":
            return ChoosingProposalSerializer
        elif self.action == "in_progress_project":
            return UserProjectInProgressSerializer
        elif self.action == "complete":
            return MarkCompleted
        elif self.action == "completed_project" or self.action == "canceled_project":
            return ChosenProposalSerializer
        elif self.action == "expired_project":
            return ProjectSerializer
        elif self.action == "dispute":
            return OpenDispute
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        max_price = int(request.data.get("max_price"))
        user = self.request.user
        superuser = User.objects.get(is_superuser=True, username="a")
        title = self.request.data.get("title")
        try:
            user_points = Point.objects.get(user=user)
            superuser_points = Point.objects.get(user=superuser)
        except Point.DoesNotExist:
            return Response({"message": "User points not found"}, status=status.HTTP_404_NOT_FOUND)

        if user_points.balance >= max_price:
            with transaction.atomic():
                user_points.balance -= max_price
                user_points.save()
                TransactionLog.objects.create(user=user, transaction_type="POINTS_SPENT", amount=max_price,
                                              description=f"Spent {max_price} to create '{title}' project.")

                superuser_points.balance += max_price
                superuser_points.save()
                TransactionLog.objects.create(user=superuser, transaction_type="SUPER_POINTS_RECEIVED",
                                              amount=max_price,
                                              description=f"Received {max_price} form '{user}' to create '{title}' project.")

                return super().create(request, *args, **kwargs)
        else:
            return Response({"message": "Insufficient points"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        user = self.request.user
        superuser = User.objects.get(is_superuser=True, username="a")
        max_price = project.max_price

        try:
            user_points = Point.objects.get(user=user)
            superuser_points = Point.objects.get(user=superuser)
        except Point.DoesNotExist:
            return Response({"message": "User points not found"}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            user_points.balance += max_price
            user_points.save()
            TransactionLog.objects.create(user=user, transaction_type="POINTS_RECEIVED", amount=max_price,
                                          description=f"Restored {max_price} points for deleting '{project.title}' project.")

            superuser_points.balance -= max_price
            superuser_points.save()
            TransactionLog.objects.create(user=superuser, transaction_type="SUPER_POINTS_SPENT",
                                          amount=max_price,
                                          description=f"Restored {max_price} points to '{user}' for deleting '{project.title}' project.")

            super().destroy(request, *args, **kwargs)

        return Response({"message": "Project deleted and points restored"}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(published_user=user)

    # def perform_create(self, serializer):
    #     user = self.request.user
    #     files_data = self.request.FILES.getlist("file")
    #     project = serializer.save(published_user=user)
    #
    #     for file in files_data:
    #         ProjectFile.objects.create(project=project, file=file)

    # @action(detail=True, methods=["post"])
    # def upload_file(self, request, pk=None):
    #     try:
    #         project = self.get_object()
    #         file = request.FILES.get("file")
    #         serializer = self.get_serializer(data=request.data)
    #         if serializer.is_valid():
    #             serializer.save(project=project, file=file)
    #             return Response({"message": _("File uploaded successfully")}, status=status.HTTP_201_CREATED)
    #         else:
    #             return Response({"error": _("No file provided")}, status=status.HTTP_400_BAD_REQUEST)
    #     except Project.DoesNotExist:
    #         return Response({"error": _("Project not found")}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["get", "post"])
    def project_proposals(self, request, pk=None):
        project = self.get_object()
        user = self.request.user
        if request.method == "GET":
            try:
                project_proposals = ProjectProposal.objects.filter(project=project, proposer__isnull=False)
                ordering = self.request.query_params.get("ordering", "-proposal_date")
                project_proposals = project_proposals.order_by(ordering)
                page = self.paginate_queryset(project_proposals)
                if page is not None:
                    serializer = ProjectProposalSerializer(page, many=True, context={"request": request})
                    return self.get_paginated_response(serializer.data)
                else:
                    serializer = ProjectProposalSerializer(project_proposals, many=True, context={"request": request})
                    return Response(serializer.data)
            except Project.DoesNotExist:
                return Response({"error": _("Project not found")}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                selected_proposal_id = request.data.get("selected_proposal")
                try:
                    selected_proposal = ProjectProposal.objects.get(pk=selected_proposal_id, project=project,
                                                                    proposer__isnull=False)
                except ProjectProposal.DoesNotExist:
                    return Response(
                        {"error": _("Selected proposal not found for this project or the proposer not found.")},
                        status=status.HTTP_400_BAD_REQUEST)

                superuser = User.objects.get(is_superuser=True, username="a")
                user_points = Point.objects.get(user=user)
                superuser_points = Point.objects.get(user=superuser)

                amount_to_add = selected_proposal.proposed_price - project.max_price

                if amount_to_add > 0:
                    if user_points.balance < amount_to_add:
                        return Response({
                            "message": _(
                                "Insufficient points, you need to add extra {x} points to be able to choose this proposal").format(
                                x=amount_to_add - user_points.balance)},
                            status=status.HTTP_400_BAD_REQUEST)

                    with transaction.atomic():
                        user_points.balance -= amount_to_add
                        user_points.save()
                        TransactionLog.objects.create(user=user, transaction_type="POINTS_SPENT",
                                                      amount=amount_to_add,
                                                      description=f"Spent extra {amount_to_add} points to choose '{selected_proposal.proposer}' proposal for '{project.title}' project.")

                        superuser_points.balance += amount_to_add
                        superuser_points.save()
                        TransactionLog.objects.create(user=superuser, transaction_type="SUPER_POINTS_RECEIVED",
                                                      amount=amount_to_add,
                                                      description=f"Received extra {amount_to_add} points form {user} to choose '{selected_proposal.proposer}' proposal for '{project.title}' project.")

                serializer.save(project=project, selected_proposal=selected_proposal)

                chat_room = ChatRoom.objects.get(project=project)
                chat_room_url = reverse("chat-detail", kwargs={"slug": chat_room.slug}, request=request)

                amount_to_return = project.max_price - selected_proposal.proposed_price

                if amount_to_return > 0:
                    with transaction.atomic():
                        superuser_points.balance -= amount_to_return
                        superuser_points.save()
                        TransactionLog.objects.create(user=superuser, transaction_type="SUPER_POINTS_SPENT",
                                                      amount=amount_to_return,
                                                      description=f"Spent {amount_to_return} points for '{user}' - {selected_proposal.proposer} bid lower than the expected price for '{project.title}' project.")
                        user_points.balance += amount_to_return
                        user_points.save()
                        TransactionLog.objects.create(user=user, transaction_type="POINTS_RECEIVED",
                                                      amount=amount_to_return,
                                                      description=f"Received {amount_to_return} points - {selected_proposal.proposer} bid lower than the expected price for '{project.title}' project.")

                return Response({"message": _("Proposal chosen successfully"), "chat_room_url": chat_room_url},
                                status=status.HTTP_201_CREATED)
            except Project.DoesNotExist:
                return Response({"error": _("Project not found")}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["put"], url_name="complete")
    def complete(self, request, pk=None):
        project = self.get_object()
        try:
            serializer = self.get_serializer(data=request.data, context={"project": project})
            if serializer.is_valid():
                project = serializer.save()
                if project.status == "completed":
                    proposal = ChosenProposal.objects.get(project=project).selected_proposal
                    price = proposal.proposed_price
                    proposer = proposal.proposer
                    superuser = User.objects.get(is_superuser=True, username="a")
                    proposer_points = Point.objects.get(user=proposer)
                    superuser_points = Point.objects.get(user=superuser)
                    with transaction.atomic():
                        superuser_points.balance -= price
                        superuser_points.save()
                        TransactionLog.objects.create(user=superuser, transaction_type="SUPER_POINTS_SPENT",
                                                      amount=price,
                                                      description=f"Spent {price} points to '{proposer}' for completing '{project.title}' project.")
                        proposer_points.balance += price
                        proposer_points.save()
                        TransactionLog.objects.create(user=proposer, transaction_type="POINTS_RECEIVED", amount=price,
                                                      description=f"Received {price} points for completing '{project.title}' project.")

                        review = UserReview.objects.get(project=project, reviewer=self.request.user)
                        review_url = reverse("complete-review-detail", kwargs={"pk": review.pk}, request=request)

                        return Response({"message": _("Project marked as completed"), "review_url": review_url},
                                        status=status.HTTP_200_OK)
                else:
                    return Response({"message": _("Project status not updated")},
                                    status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({"error": _("Project not found")}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def dispute(self, request, pk=None):
        project = self.get_object()
        chosen_proposal = ChosenProposal.objects.get(project=project)
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(proposal=chosen_proposal, opened_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def common_project_action(self, request, status_filter):
        projects = self.filter_queryset(self.get_queryset().filter(status=status_filter))
        proposals = ChosenProposal.objects.filter(project__in=projects)
        ordering = self.request.query_params.get("ordering", "-chosen_date")
        proposals = proposals.order_by(ordering)
        page = self.paginate_queryset(proposals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(proposals, many=True)
            return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def in_progress_project(self, request):
        return self.common_project_action(request, status_filter="in_progress")

    @action(detail=False, methods=["get"])
    def canceled_project(self, request):
        return self.common_project_action(request, status_filter="canceled")

    @action(detail=False, methods=["get"])
    def completed_project(self, request):
        return self.common_project_action(request, status_filter="completed")

    @action(detail=False, methods=["get"])
    def expired_project(self, request):
        expired_projects = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(expired_projects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(expired_projects, many=True)
            return Response(serializer.data)


class UserProjectFileDelete(generics.DestroyAPIView):
    queryset = ProjectFile.objects.all()
    serializer_class = ProjectFileSerializer
    permission_classes = [ProjectFileDelete]


class UserProjectProposalViewSet(mixins.ListModelMixin,
                                 mixins.RetrieveModelMixin,
                                 mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin,
                                 viewsets.GenericViewSet):
    serializer_class = UserProjectProposalDetailSerializer
    permission_classes = [IsProposalOwner, ProjectAndProposalModification]
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["project__skill_needed"]
    search_fields = ["project__title"]
    # ordering_fields = ["submission_date", "proposal_date"]
    pagination_class = ProjectPagination

    def get_queryset(self):
        queryset = ProjectProposal.objects.filter(proposer=self.request.user)
        ordering = self.request.query_params.get("ordering", "-proposal_date")
        if self.action == "list":
            queryset = queryset.filter(project__status="active")
        return queryset.order_by(ordering)

    def get_serializer_class(self):
        if self.action == "in_progress":
            return InProgressProposalDetailSerializer
        elif self.action == "dispute":
            return OpenDispute
        return self.serializer_class

    def get_permissions(self):
        if self.action == "dispute":
            self.permission_classes = [DisputePermission]
        return super().get_permissions()

    def get_serialize(self, status_filter):
        queryset = self.filter_queryset(self.get_queryset().filter(project__status=status_filter))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def dispute(self, request, pk=None):
        project = self.get_object().project
        chosen_proposal = ChosenProposal.objects.get(project=project)
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(proposal=chosen_proposal, opened_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def in_progress(self, request):
        return self.get_serialize(status_filter="in_progress")

    @action(detail=False, methods=["get"])
    def canceled(self, request):
        return self.get_serialize(status_filter="canceled")

    @action(detail=False, methods=["get"])
    def completed(self, request):
        return self.get_serialize(status_filter="completed")

    @action(detail=False, methods=["get"])
    def expired(self, request):
        return self.get_serialize(status_filter="expired")


class CompleteReviewViewSet(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            GenericViewSet):
    serializer_class = CompleteReviewSerializer
    permission_classes = [CanReview]

    def get_queryset(self):
        user = self.request.user
        return UserReview.objects.filter(reviewer=user, rating__isnull=True)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()

        if review.rating is not None:
            project_reviews = UserReview.objects.filter(project=review.project)
            client_review = project_reviews.filter(reviewed_user_title="client", rating__isnull=False).first()
            freelancer_review = project_reviews.filter(reviewed_user_title="freelancer", rating__isnull=False).first()

            if client_review and freelancer_review:
                freelancer_bid = Bid.objects.get(user=freelancer_review.reviewed_user)
                freelancer_bid.nb_bid += 1
                freelancer_bid.save()
                TransactionLog.objects.create(user=freelancer_review.reviewed_user,
                                              transaction_type="BIDS_RECEIVED", amount=1,
                                              description=f"Received 1 bid upon completing the review for the '{review.project.title}' project.")
        return Response(serializer.data)
