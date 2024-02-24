# yourapp/management/commands/create_users.py
import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from project.models import Project, ProjectProposal
from user.models import User


class Command(BaseCommand):
    help = "Creates users with specific details"

    def handle(self, *args, **kwargs):
        users = [
            {"first_name": "c", "last_name": "c", "username": "c", "email": "c@c.com", "password": "Asdf.123"},
            {"first_name": "d", "last_name": "d", "username": "d", "email": "d@d.com", "password": "Asdf.123"},
            {"first_name": "q", "last_name": "q", "username": "q", "email": "q@q.com", "password": "Asdf.123"},
            {"first_name": "f", "last_name": "f", "username": "f", "email": "f@f.com", "password": "Asdf.123"},
        ]

        for user_data in users:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                password=user_data["password"],
                is_active=True,

            )
            if created:
                user.set_password(user_data["password"])
                user.save()

                Project.objects.create(
                    published_user=user,
                    title=f"{user.first_name}'s Project",
                    description=f"Description for {user.first_name}'s Project",
                    additional_notes="Additional notes if any",
                    min_price=random.randint(10, 50),
                    max_price=random.randint(51, 100),
                    due_date="2024-12-31",
                    proposal_time_end="2024-1-13",
                    status="active"
                )

                # project.skill_needed.set([1, 2, 3])

                other_projects = Project.objects.exclude(published_user=user).order_by("?")[:3]  # Select 3 random projects

                for project in other_projects:
                    submission_date = datetime.now() + timedelta(days=random.randint(1, 30))  # Random submission date

                    proposal = ProjectProposal.objects.create(
                        project=project,
                        proposer=user,
                        proposal_text=f"Proposal for {project.title}",
                        proposed_price=random.randint(project.min_price, project.max_price),
                        submission_date=submission_date.date(),
                        is_accepted=False
                    )

                self.stdout.write(self.style.SUCCESS(f"User {user.username} created successfully"))
            else:
                self.stdout.write(self.style.WARNING(f"User {user.username} already exists"))
