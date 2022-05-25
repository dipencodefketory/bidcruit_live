
import os
from django.conf.urls import url
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bidcruit.settings')
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()
django.setup()
from channels.auth import AuthMiddlewareStack
import chat.routing
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    )
})