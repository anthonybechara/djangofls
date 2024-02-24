from celery import shared_task
from django.db import transaction
from django.utils import timezone

from payment.models import Point, TransactionLog
from user.models import User
from .models import Project


@shared_task
def deactivate_expired_projects():
    expired_projects = Project.objects.filter(proposal_time_end__lt=timezone.now().date(), status="active")
    for project in expired_projects:
        project.status = "expired"
        project.save()
        user = project.published_user
        superuser = User.objects.get(is_superuser=True, username="a")

        user_points = Point.objects.get(user=user)
        superuser_points = Point.objects.get(user=superuser)

        with transaction.atomic():
            superuser_points.balance -= project.max_price
            superuser_points.save()
            TransactionLog.objects.create(user=superuser, transaction_type="SUPER_POINTS_SPENT",
                                          amount=project.max_price,
                                          description=f"Spent {project.max_price} points for '{user}' due to the expiry of '{project.title}' project.")
            user_points.balance += project.max_price
            user_points.save()
            TransactionLog.objects.create(user=user, transaction_type="POINTS_RECEIVED",
                                          amount=project.max_price,
                                          description=f"Received {project.max_price} points due to the expiry of '{project.title}' project.")

