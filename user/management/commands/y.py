from django.core.management.base import BaseCommand

from chat.models import ChatRoom
from user.models import User
from project.models import Project, ProjectProposal, ChosenProposal
from user_resume.models import UserReview


class Command(BaseCommand):
    help = "Deletes created users along with their projects and project proposals"

    def handle(self, *args, **kwargs):
        users_to_delete = User.objects.filter(username__in=["c", "d", "q", "f"])

        for user in users_to_delete:
            ProjectProposal.objects.filter(proposer=user).delete()
            Project.objects.filter(published_user=user).delete()
            UserReview.objects.filter(reviewed_user=user).delete()
            UserReview.objects.filter(reviewer=user).delete()
            ChatRoom.objects.filter(participants__in=user).delete()
            ChosenProposal.objects.filter(selected_proposal__proposer=user).delete()
            ProjectProposal.objects.filter(proposer__isnull=True).delete()
            Project.objects.filter(published_user__isnull=True).delete()
            UserReview.objects.filter(reviewed_user__isnull=True).delete()
            UserReview.objects.filter(reviewer__isnull=True).delete()
            ChatRoom.objects.filter(participants__isnull=True).delete()
            ChosenProposal.objects.filter(selected_proposal__proposer__isnull=True).delete()
            user.delete()

        self.stdout.write(self.style.SUCCESS("Users, projects, and project proposals deleted successfully"))
