from celery import shared_task

from user.models import User
from payment.models import Bid, TransactionLog


@shared_task
def add_bids_to_users():
    all_users = User.objects.all()
    for user in all_users:
        user_bid = Bid.objects.get(user=user)
        initial_nb_bid = user_bid.nb_bid
        if user_bid.nb_bid < 5:
            user_bid.nb_bid = min(user_bid.nb_bid + 2, 5)
            user_bid.save()
            amount_received = user_bid.nb_bid - initial_nb_bid
            TransactionLog.objects.create(user=user, transaction_type="BIDS_RECEIVED", amount=amount_received,
                                          description=f"Received bids as part of weekly allocation.")
