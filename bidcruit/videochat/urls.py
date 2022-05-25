from django.urls import path
from videochat.views import main_view,capture_image,set_interview
app_name = 'videochat'

urlpatterns=[
    path("<str:link>/",main_view,name="main_view"),
    path("capture_image",capture_image,name="capture_image"),
    path("set_interview",set_interview,name="set_interview"),
]