"""
Security app URL configuration.
"""

from django.urls import path
from .views import (
    SecurityOverviewView, SecurityAlertsView, SecurityEventsView, 
    SecuritySettingsView, SecurityPoliciesView, AuditLogViewSet,
    ComplianceView, ComplianceReportingView, DataRetentionView,
    SecurityHealthView, FileUploadSecurityView, SecurityConfigView,
    csrf_failure
)
from .system_views import (
    BulkUserManagementView, OrganizationManagementView, SystemHealthCheckView
)

urlpatterns = [
    # Security monitoring
    path('overview/', SecurityOverviewView.as_view(), name='security-overview'),
    path('alerts/', SecurityAlertsView.as_view(), name='security-alerts'),
    path('events/', SecurityEventsView.as_view(), name='security-events'),
    path('settings/', SecuritySettingsView.as_view(), name='security-settings'),
    path('policies/', SecurityPoliciesView.as_view(), name='security-policies'),
    path('config/', SecurityConfigView.as_view(), name='security-config'),
    
    # Audit logging
    path('audit-logs/', AuditLogViewSet.as_view({'get': 'list'}), name='audit-logs'),
    
    # File security
    path('file-scan/', FileUploadSecurityView.as_view(), name='file-security-scan'),
    
    # Health check
    path('health/', SecurityHealthView.as_view(), name='security-health'),
    
    # CSRF failure
    path('csrf-failure/', csrf_failure, name='csrf-failure'),
    
    # GDPR Compliance endpoints
    path('compliance/export/', ComplianceView.as_view(), {'action': 'export_user_data'}, name='gdpr-export'),
    path('compliance/delete/', ComplianceView.as_view(), {'action': 'delete_user_data'}, name='gdpr-delete'),
    path('compliance/report/', ComplianceReportingView.as_view(), name='compliance-report'),
    
    # Data retention
    path('data-retention/', DataRetentionView.as_view(), name='data-retention'),
    
    # Administrative tools
    path('admin/bulk-users/', BulkUserManagementView.as_view(), name='bulk-user-management'),
    path('admin/organizations/', OrganizationManagementView.as_view(), name='organization-management'),
    path('admin/organizations/<uuid:org_id>/', OrganizationManagementView.as_view(), name='organization-detail'),
    
    # System health
    path('system/health/', SystemHealthCheckView.as_view(), name='system-health'),
]