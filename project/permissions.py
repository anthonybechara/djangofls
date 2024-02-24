from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from project.models import Project, ProjectProposal, ProjectFile, ChosenProposal, Dispute

from django.utils.translation import gettext as _

statuses = [_("in_progress"), _("completed"), _("canceled"), _("expired")]


class IsProjectOwner(permissions.IsAuthenticated):
    message = _("You are not the owner of this project")

    def has_object_permission(self, request, view, obj):
        return obj.published_user == request.user


class ProjectProposals(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return request.user == view.get_object().published_user

    def has_object_permission(self, request, view, obj):
        project = obj
        if request.method in permissions.SAFE_METHODS:
            return True

        elif request.method == "POST":
            existing_chosen_proposal = ChosenProposal.objects.filter(project=project).exists()
            if existing_chosen_proposal:
                self.message = _("A proposal has already been selected for this project.")
                return False
        return True


# class IsProjectOwnerFileUpload(permissions.IsAuthenticated):
#     def has_permission(self, request, view):
#         project = view.get_object()
#         if isinstance(project, Project):
#             if project.status in statuses and not request.user.is_admin:
#                 return False
#         return request.user == project.published_user or request.user.is_admin


class ProjectFileDelete(permissions.IsAuthenticated):
    message = _("You dont have permission to delete this file")

    def has_permission(self, request, view):
        file = view.get_object()
        if isinstance(file, ProjectFile):
            project = file.project
            if project.status in statuses:
                return False
            return request.user == project.published_user
        return False


class IsNotProjectOwnerOrHasNotProposed(permissions.IsAuthenticated):
    message = _("You have already proposed for this project.")

    def has_permission(self, request, view):
        project = view.get_object()
        user = request.user
        if project and project.published_user != user and not user.is_anonymous:
            existing_proposal = ProjectProposal.objects.filter(project=project, proposer=user).exists()
            return not existing_proposal
        return True


class IsProposalOwner(permissions.IsAuthenticated):
    message = _("You are not the proposal owner")

    def has_object_permission(self, request, view, obj):
        return obj.proposer == request.user


class ProjectAndProposalModification(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if view.action in ["update", "partial_update", "destroy"]:
            if isinstance(obj, Project):
                if obj.status in statuses:
                    raise PermissionDenied(_("Cannot modify projects."))

            if isinstance(obj, ProjectProposal):
                if obj.project.status in statuses:
                    raise PermissionDenied(_("Cannot modify proposals"))
        return True


class CanMarkProjectAsComplete(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        obj = view.get_object()
        chosen_proposal = ChosenProposal.objects.get(project=obj)
        dispute = Dispute.objects.filter(proposal=chosen_proposal)
        if isinstance(obj, Project):
            if obj.status != "in_progress":
                self.message = _("The project is not in progress and cannot be marked as complete.")
                return False
            if obj.published_user != request.user:
                self.message = _("You are not the owner of this project and cannot mark it as complete.")
                return False
            if dispute.exists():
                self.message = _("There is an open dispute for this project. Cannot mark as complete.")
                return False
            return True
        return False


class DisputePermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        user = request.user
        project_status = self.is_project_in_progress(view)
        chosen_proposal = self.get_project_and_chosen_proposal(view, user)
        existing_dispute = Dispute.objects.filter(proposal=chosen_proposal, opened_by=user).exists()
        if project_status != "in_progress":
            self.message = _("You can only open a dispute for a project that is in progress")
            return False
        if existing_dispute:
            self.message = _("You have already opened a dispute for this project")
            return False
        return True

    @staticmethod
    def is_project_in_progress(view):
        project = view.get_object().project if hasattr(view.get_object(), "proposer") else view.get_object()
        return project.status

    @staticmethod
    def get_project_and_chosen_proposal(view, user):
        if hasattr(view.get_object(), "proposer"):
            project = view.get_object().project
            return ChosenProposal.objects.get(project=project, selected_proposal__proposer=user)
        else:
            project = view.get_object()
            return ChosenProposal.objects.get(project=project, project__published_user=user)


class CanReview(permissions.IsAuthenticated):
    message = _("You dont have access to perform this action.")

    def has_object_permission(self, request, view, obj):
        # if request.method in permissions.SAFE_METHODS:
        #     return True

        user_review = obj
        if request.user == user_review.project.published_user:
            return True
        if request.user == user_review.project.chosenproposal.selected_proposal.proposer:
            return True
        return False

    # def has_permission(self, request, view):
    #     if request.method in permissions.SAFE_METHODS:
    #         return True
    #
    #     user_review = view.get_object()
    #     if request.user == user_review.project.published_user:
    #         return True
    #     if request.user == user_review.project.chosenproposal.selected_proposal.proposer:
    #         return True
    #     return False
