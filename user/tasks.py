import datetime
from celery import shared_task

from user.models import User


@shared_task
def cleanup_new_emails():
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    users = User.objects.filter(new_email__isnull=False, new_email_modified__lt=one_day_ago)
    for user in users:
        user.new_email = None
        user.save()


@shared_task
def remove_newly_deactivated_account():
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    users = User.objects.filter(created_date__lte=one_day_ago, is_active=False, last_login__isnull=True)
    for user in users:
        user.delete()
