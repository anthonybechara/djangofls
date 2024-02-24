from django.urls import path, include
from rest_framework.routers import DefaultRouter

from chat.views import ChatRoomView

router = DefaultRouter()
router.register("chat", ChatRoomView, basename="chat")

urlpatterns = [
    path("", include(router.urls)),
]
