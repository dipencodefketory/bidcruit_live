from django.urls import path, include
from . import views

from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from chat.api import MessageModelViewSet, UserModelViewSet
from .views import get_unread_messages,update_unread_messages,get_user_image
router = DefaultRouter()
router.register(r'message', MessageModelViewSet, basename='message-api')
router.register(r'user', UserModelViewSet, basename='user-api')

app_name= 'chat'

urlpatterns = [
    path('get_message', views.get_message, name='get_message'),
    path('', views.chatlist, name="chatlist"),

    path(r'api/v1/', include(router.urls)),
    path('get_unread_messages/', get_unread_messages, name='get_unread_messages'),
    path('update_unread_messages/<int:id>', update_unread_messages, name='update_unread_messages'),
    path('get_user_image/<str:email>', get_user_image, name='get_user_image'),
    path('create_privatemsg/<str:type_chat>/<int:id>', views.create_privatemsg, name='create_privatemsg'),
    path('', TemplateView.as_view(template_name='chat/chat.html'), name='home'),
    path('get_chat',views.get_chat,name='get_chat'),

]
