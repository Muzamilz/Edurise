from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIConversationViewSet, AIContentSummaryViewSet, 
    AIQuizViewSet, AIUsageViewSet
)

router = DefaultRouter()
router.register(r'conversations', AIConversationViewSet, basename='aiconversation')
router.register(r'summaries', AIContentSummaryViewSet, basename='aisummary')
router.register(r'quizzes', AIQuizViewSet, basename='aiquiz')
router.register(r'usage', AIUsageViewSet, basename='aiusage')

urlpatterns = [
    path('', include(router.urls)),
]