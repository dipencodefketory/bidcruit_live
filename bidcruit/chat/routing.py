from django.urls import path

from chat import consumers

websocket_urlpatterns = [
    path('ws/chat/<str:chat_id>/', consumers.ChatConsumer.as_asgi()),
    path('ws/privatechat/<str:chat_id>/', consumers.ChatPrivate.as_asgi()),
    path('ws/chat_chat/', consumers.Chat_chat.as_asgi()),



]
