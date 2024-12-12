import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path
from .consumers import SuperUserConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                path('ws/', SuperUserConsumer.as_asgi()),
            ]
        )
    ),
})