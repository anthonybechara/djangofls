import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from djangofls import routing, jwt_middleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangofls.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": jwt_middleware.JWTAuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
