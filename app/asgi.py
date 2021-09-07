import os
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from .consumers import chatroom
from django.core.asgi import get_asgi_application
from django.urls import path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tictac.settings')

application = get_asgi_application()


ws_pattern = [
        path('ws/chat/<username>/' , chatroom)
]


application= ProtocolTypeRouter(
    {
        'websocket':AuthMiddlewareStack(URLRouter(
            ws_pattern
        ))
    }
)
