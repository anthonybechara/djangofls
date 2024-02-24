from rest_framework import serializers

from payment.models import Point, Bid, TransactionLog


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ("id", "balance")


class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ("id", "nb_bid")


class TransactionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionLog
        exclude = ("user",)
