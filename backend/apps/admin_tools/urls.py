# Note: AuditLogViewSet is registered in the centralized API router (apps/api/urls.py)
# AdminDashboardView is a ViewSet but admin dashboard functionality is handled 
# by the centralized dashboard views in apps/api/dashboard_views.py

urlpatterns = [
    # Future admin-specific endpoints (non-ViewSet) can be added here
    # For example: system maintenance, backup management, etc.
]