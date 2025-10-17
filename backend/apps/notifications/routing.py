from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]

# Import live class WebSocket routes
try:
    from apps.classes.routing import websocket_urlpatterns as classes_websocket_urlpatterns
    # Combine all WebSocket URL patterns
    websocket_urlpatterns += classes_websocket_urlpatterns
except ImportError:
    # Classes app routing might not exist yet
    pass