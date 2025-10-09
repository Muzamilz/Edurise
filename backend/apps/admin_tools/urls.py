from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, AdminDashboardView

router = DefaultRouter()
router.register(r'audit-logs', AuditLogViewSet, basename='auditlog')
router.register(r'dashboard', AdminDashboardView, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]