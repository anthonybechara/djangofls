from django.db.models.signals import pre_delete
from django.dispatch import receiver

from payment.models import TransactionLog
from user.models import User


@receiver(pre_delete, sender=User)
def fill_username_for_deleted_user(sender, instance, **kwargs):
    users = TransactionLog.objects.filter(user=instance)
    for a in users:
        username = a.user.username
        a.username = f"{username} (DELETED)"
        a.save(update_fields=["username"])
