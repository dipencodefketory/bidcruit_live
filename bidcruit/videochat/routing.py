from django.urls import re_path
from . import consumers
from django.urls import path
websocket_urlpatterns = [
  # re_path(r"",consumers.ChatConsumer.as_asgi()),
  path("<str:link>/",consumers.ChatConsumer.as_asgi()),
  # path("<int:pk>/")
]