from django.db import models
from django.conf import settings

from django.utils.translation import gettext_lazy as _


class Point(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="points")
    balance = models.IntegerField(default=0, verbose_name=_("Balance"))

    class Meta:
        verbose_name = "Point"
        verbose_name_plural = "Points"

    def __str__(self):
        return f"{self.balance} points for {self.user}"


class Bid(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bids")
    nb_bid = models.IntegerField(default=5, verbose_name=_("Number of Bids"))

    class Meta:
        verbose_name = "Bid"
        verbose_name_plural = "Bids"

    def __str__(self):
        return f"{self.nb_bid} bids for {self.user}"


class TransactionLog(models.Model):
    TRANSACTION_CHOICES = [
        ("POINTS_SPENT", "Points Spent"),
        ("POINTS_RECEIVED", "Points Received"),
        ("SUPER_POINTS_SPENT", "Super Points Spent"),
        ("SUPER_POINTS_RECEIVED", "Super Points Received"),
        ("BIDS_SPENT", "Bids Spent"),
        ("BIDS_RECEIVED", "Bids Received"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="transactions")
    username = models.CharField(max_length=200, blank=True, verbose_name=_("Username"))
    transaction_type = models.CharField(max_length=25, choices=TRANSACTION_CHOICES, verbose_name=_("Transaction Type"))
    amount = models.IntegerField(default=0, verbose_name=_("Amount"))
    description = models.CharField(max_length=100, verbose_name=_("Description"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))

    class Meta:
        verbose_name = "Transaction Log"
        verbose_name_plural = "Transaction Logs"
        ordering = ("-timestamp",)

    def __str__(self):
        if self.user:
            return f"{self.user} - {self.get_transaction_type_display()} - Amount: {self.amount}"
        return f"{self.username} - {self.get_transaction_type_display()} - Amount: {self.amount}"

