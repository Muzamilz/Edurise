from django.urls import path
from .views import ZoomWebhookView, ZoomMeetingView

# Note: ClassAttendanceViewSet is registered in the centralized API router (apps/api/urls.py)
# This file only contains Zoom integration endpoints and other non-ViewSet functionality

urlpatterns = [
    path('zoom/webhook/', ZoomWebhookView.as_view(), name='zoom_webhook'),
    path('zoom/meetings/<uuid:live_class_id>/', ZoomMeetingView.as_view(), name='zoom_meeting'),
]