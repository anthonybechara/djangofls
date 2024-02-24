from rest_framework import mixins, filters, permissions
from rest_framework.viewsets import GenericViewSet

from payment.filters import TransactionFilterBackend, ExactWordSearchFilter
from payment.models import Point, Bid, TransactionLog
from payment.pagination import TransactionLogPagination
from payment.serializers import PointSerializer, BidSerializer, TransactionLogSerializer


class PointViewSet(mixins.ListModelMixin,
                   GenericViewSet):
    serializer_class = PointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Point.objects.filter(user=user)


class BidViewSet(mixins.ListModelMixin,
                 GenericViewSet):
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Bid.objects.filter(user=user)


class TransactionLogViewSet(mixins.ListModelMixin,
                            GenericViewSet):
    serializer_class = TransactionLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [TransactionFilterBackend, filters.OrderingFilter, ExactWordSearchFilter]

    pagination_class = TransactionLogPagination
    filterset_fields = ["transaction_type"]
    search_fields = ["description"]
    ordering_fields = ["timestamp"]

    def get_queryset(self):
        user = self.request.user
        return TransactionLog.objects.filter(user=user)
