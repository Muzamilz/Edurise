from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClassAttendanceViewSet, ZoomWebhookView, ZoomMeetingView

router = DefaultRouter()
router.register(r'attendance', ClassAttendanceViewSet, basename='classattendance')

urlpatterns = [
    path('', include(router.urls)),
    path('zoom/webhook/', ZoomWebhookView.as_view(), name='zoom_webhook'),
    path('zoom/meetings/<uuid:live_class_id>/', ZoomMeetingView.as_view(), name='zoom_meeting'),
]