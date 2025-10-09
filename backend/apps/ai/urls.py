from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIConversationViewSet, AIUsageViewSet

router = DefaultRouter()
router.register(r'conversations', AIConversationViewSet, basename='aiconversation')
router.register(r'usage', AIUsageViewSet, basename='aiusage')

urlpatterns = [
    path('', include(router.urls)),
]