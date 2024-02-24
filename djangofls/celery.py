import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangofls.settings")

app = Celery("djangofls")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    'send_queued': {
        'task': 'post_office.tasks.send_queued_mail',
        'schedule': 600,
    },
    "cleanup_new_emails": {
        "task": "user.tasks.cleanup_new_emails",
        "schedule": crontab(minute="0", hour="0"),
    },
    "remove_newly_deactivated_account": {
        "task": "user.tasks.remove_newly_deactivated_account",
        "schedule": crontab(minute="0", hour="0"),
    },
    "deactivate_expired_projects": {
        "task": "project.tasks.deactivate_expired_projects",
        "schedule": crontab(minute="0", hour="0"),
        # "schedule": crontab(minute="*/1"),

    },
    "add_bids_to_users": {
        "task": "payment.tasks.add_bids_to_users",
        "schedule": crontab(hour="0", minute="0", day_of_week="1"),
        # "schedule": crontab(minute="*/1"),

    },
}

app.autodiscover_tasks()
