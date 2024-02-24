from django.urls import include, path
from rest_framework.routers import DefaultRouter

from payment.views import BidViewSet, PointViewSet, TransactionLogViewSet

router = DefaultRouter()
router.register("points", PointViewSet, basename="points")
router.register("bids", BidViewSet, basename="bids")
router.register("transactions", TransactionLogViewSet, basename="transactions")

urlpatterns = [
    path("", include(router.urls)),
]
