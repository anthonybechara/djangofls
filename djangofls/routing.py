from django.urls import path
from djangofls import consumers

websocket_urlpatterns = [
    path('ws/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
    # path('ws/user/online/', consumers.OnlineStatus.as_asgi()),
]