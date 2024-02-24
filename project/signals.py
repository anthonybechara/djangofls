from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from chat.models import ChatRoom
from payment.models import Point, TransactionLog
from project.models import ChosenProposal, Project, ProjectProposal, Dispute
from user.models import User
from user_resume.models import UserReview


@receiver(post_save, sender=ChosenProposal)
def set_is_accepted(sender, instance, created, **kwargs):
    if created:
        instance.selected_proposal.is_accepted = True
        instance.selected_proposal.save(update_fields=["is_accepted"])
        instance.project.status = "in_progress"
        instance.project.save(update_fields=["status"])
        chat_room, created = ChatRoom.objects.get_or_create(project=instance.project)
        if chat_room.status == "closed":
            chat_room.status = "active"
            chat_room.save(update_fields=["status"])
        chat_room.participants.add(instance.project.published_user, instance.selected_proposal.proposer)


@receiver(pre_delete, sender=User)
def cancel_projects_and_proposals_on_user_delete(sender, instance, **kwargs):
    projects_to_cancel = Project.objects.filter(published_user=instance, status__in=["active", "in_progress"])
    for project in projects_to_cancel:
        if project.status != "canceled":
            project.status = "canceled"
            username = project.published_user.username
            project.published_username = f"{username} (DELETED)"
            project.save(update_fields=["status", "published_username"])

            related_proposals = ProjectProposal.objects.filter(project=project)
            for proposal in related_proposals:
                proposal.is_canceled = True
                proposal.save(update_fields=["is_canceled"])
                try:
                    chosen_proposal = ChosenProposal.objects.get(project=proposal.project)
                    chosen_proposal.is_canceled = True
                    chosen_proposal.save(update_fields=["is_canceled"])
                except ObjectDoesNotExist:
                    pass

    related_proposals = ProjectProposal.objects.filter(proposer=instance)
    for proposal in related_proposals:
        username = proposal.proposer.username
        proposal.proposer_username = f"{username} (DELETED)"
        proposal.save(update_fields=["proposer_username"])
        if proposal.is_accepted:  #################################################################check if all need to be canceled even if they are not chosen
            proposal.is_canceled = True
            proposal.save(update_fields=["is_canceled"])
            if proposal.is_price_adjusted:
                user = proposal.project.published_user
                if user:
                    superuser = User.objects.get(is_superuser=True, username="a")
                    user_points = Point.objects.get(user=user)
                    superuser_points = Point.objects.get(user=superuser)

                    with transaction.atomic():
                        return_point = proposal.proposed_price - proposal.project.max_price
                        superuser_points.balance -= return_point
                        superuser_points.save()
                        TransactionLog.objects.create(user=superuser, transaction_type="SUPER_POINTS_SPENT",
                                                      amount=return_point,
                                                      description=f"Spent {return_point} points for '{user}' due to the deletion of user '{proposal.proposer}'.")
                        user_points.balance += return_point
                        user_points.save()
                        TransactionLog.objects.create(user=user, transaction_type="POINTS_RECEIVED",
                                                      amount=return_point,
                                                      description=f"Received {return_point} points due to the deletion of user '{proposal.proposer}'.")
            try:
                chosen_proposal = ChosenProposal.objects.get(project=proposal.project)
                chosen_proposal.is_canceled = True
                chosen_proposal.save(update_fields=["is_canceled"])
            except ObjectDoesNotExist:
                pass
            proposal.project.status = "active"
            proposal.project.save(update_fields=["status"])


@receiver(post_save, sender=Project)
def create_review(sender, instance, created, **kwargs):
    if instance.status == "completed":
        ChatRoom.objects.update(status="closed")
        project = instance
        project_owner = project.published_user
        chosen_proposal_instance = project.chosenproposal
        proposer = chosen_proposal_instance.selected_proposal.proposer

        if not UserReview.objects.filter(project=project, reviewed_user=project_owner, reviewer=proposer).exists():
            UserReview.objects.create(
                project=project,
                reviewer=proposer,
                reviewed_user_title="client",
                reviewed_user=project_owner,
            )

        if not UserReview.objects.filter(project=project, reviewed_user=proposer, reviewer=project_owner).exists():
            UserReview.objects.create(
                project=project,
                reviewer=project_owner,
                reviewed_user_title="freelancer",
                reviewed_user=proposer,
            )


@receiver(pre_delete, sender=User)
def close_chatroom_on_user_delete_or_delete_if_no_messages(sender, instance, **kwargs):
    chat_rooms = ChatRoom.objects.filter(participants__exact=instance, status="active")
    for chat_room in chat_rooms:
        if chat_room:
            if chat_room.messages.count() == 0:
                chat_room.delete()
            elif chat_room.status != "closed":
                chat_room.status = "closed"
                chat_room.save(update_fields=["status"])


@receiver(pre_delete, sender=User)
def fill_username_for_deleted_dispute_users(sender, instance, **kwargs):
    disputes = Dispute.objects.filter(opened_by=instance)
    for dispute in disputes:
        dispute.opened_by_username = f"{dispute.opened_by.username} (DELETED)"
        dispute.save(update_fields=["opened_by_username"])


# Should not be done because only active projects can be deleted
@receiver(pre_delete, sender=Project)
def cancel_proposals_on_project_delete(sender, instance, **kwargs):
    related_proposals = ProjectProposal.objects.filter(project=instance)
    for proposal in related_proposals:
        proposal.is_canceled = True
        proposal.save(update_fields=["is_canceled"])


# Should not be done because only active projects can be deleted
@receiver(pre_delete, sender=Project)
def close_chatroom_on_project_delete_or_delete_if_no_messages(sender, instance, **kwargs):
    chat_rooms = ChatRoom.objects.filter(project=instance, status="active")
    for chat_room in chat_rooms:
        if chat_room:
            if chat_room.messages.count() == 0:
                chat_room.delete()
            elif chat_room.status != "closed":
                chat_room.status = "closed"
                chat_room.save(update_fields=["status"])
