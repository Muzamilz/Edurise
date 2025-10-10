from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/live-class/(?P<live_class_id>[0-9a-f-]+)/$', consumers.LiveClassConsumer.as_asgi()),
    re_path(r'ws/live-class/(?P<live_class_id>[0-9a-f-]+)/instructor/$', consumers.LiveClassInstructorConsumer.as_asgi()),
]