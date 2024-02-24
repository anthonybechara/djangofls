from django.contrib import admin

from payment.models import Point, Bid, TransactionLog


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "balance")


@admin.register(Bid)
class PointAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "nb_bid")


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "username", "transaction_type", "amount", "description", "timestamp")
