# import os
# # from channels.asgi import get_channel_layer

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bidcruit.settings")

# # channel_layer = get_channel_layer()



import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bidcruit.settings')
django.setup()

from channels.auth import AuthMiddlewareStack
import videochat.routing
import chat.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            videochat.routing.websocket_urlpatterns +
            chat.routing.websocket_urlpatterns
        )
    )
})





