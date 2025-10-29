"""
Security views for monitoring, alerts, and administrative functions.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework import viewsets, status
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import timedelta
from django.contrib.auth import get_user_model

from apps.api.responses import StandardAPIResponse
from apps.api.mixins import APIResponseMixin
from .models import SecurityEvent, SecurityAlert, SecurityPolicy
from apps.admin_tools.models import AuditLog
from .services import (
    SecurityMonitoringService, 
    SecurityAlertService, 
    AuditService, 
    ComplianceService
)

User = get_user_model()


class SecurityOverviewView(APIView):
    """
    Security overview for admin/super-admin.
    Endpoint: /security/overview/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied(
                message="Only administrators can access security overview"
            )
        
        tenant = getattr(request, 'tenant', None)
        overview_data = SecurityMonitoringService.get_security_overview(tenant=tenant)
        
        return StandardAPIResponse.success(
            data=overview_data,
            message="Security overview retrieved successfully"
        )


class SecurityAlertsView(APIView):
    """Security alerts endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        tenant = getattr(request, 'tenant', None)
        alerts = SecurityAlertService.get_active_alerts(tenant=tenant)
        
        return StandardAPIResponse.success(
            data={'results': alerts},
            message="Security alerts retrieved successfully"
        )
    
    def post(self, request):
        """Create a manual security alert"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied()
        
        data = request.data
        tenant = getattr(request, 'tenant', None)
        
        alert = SecurityAlertService.create_alert(
            alert_type=data.get('alert_type', 'manual'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            severity=data.get('severity', 'medium'),
            tenant=tenant
        )
        
        return StandardAPIResponse.success(
            data={'alert_id': str(alert.id)},
            message="Security alert created successfully"
        )


class SecurityEventsView(APIView):
    """Security events endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        tenant = getattr(request, 'tenant', None)
        
        # Get query parameters
        event_type = request.GET.get('event_type')
        severity = request.GET.get('severity')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        limit = int(request.GET.get('limit', 100))
        
        # Build queryset
        events_qs = SecurityEvent.objects.all()
        if tenant:
            events_qs = events_qs.filter(tenant=tenant)
        
        if event_type:
            events_qs = events_qs.filter(event_type=event_type)
        
        if severity:
            events_qs = events_qs.filter(severity=severity)
        
        if start_date:
            events_qs = events_qs.filter(created_at__gte=start_date)
        
        if end_date:
            events_qs = events_qs.filter(created_at__lte=end_date)
        
        events = events_qs.order_by('-created_at')[:limit]
        
        # Format response
        events_data = []
        for event in events:
            events_data.append({
                'id': str(event.id),
                'event_type': event.event_type,
                'severity': event.severity,
                'description': event.description,
                'user': event.user.email if event.user else None,
                'ip_address': event.ip_address,
                'endpoint': event.endpoint,
                'method': event.method,
                'is_resolved': event.is_resolved,
                'created_at': event.created_at.isoformat()
            })
        
        return StandardAPIResponse.success(
            data={'results': events_data},
            message="Security events retrieved successfully"
        )


class SecuritySettingsView(APIView):
    """Security settings endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        tenant = getattr(request, 'tenant', None)
        
        # Get security policies
        policies_qs = SecurityPolicy.objects.filter(is_active=True)
        if tenant:
            policies_qs = policies_qs.filter(tenant=tenant)
        
        settings_data = {
            'password_policy': {
                'min_length': 8,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_numbers': True,
                'require_special_chars': True
            },
            'session_management': {
                'session_timeout': 3600,
                'max_concurrent_sessions': 3
            },
            'login_restrictions': {
                'max_failed_attempts': 5,
                'lockout_duration': 900
            },
            'policies_count': policies_qs.count(),
            'enforced_policies': policies_qs.filter(is_enforced=True).count()
        }
        
        return StandardAPIResponse.success(
            data=settings_data,
            message="Security settings retrieved successfully"
        )
    
    def put(self, request):
        """Update security settings"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied()
        
        # In a real implementation, this would update security configurations
        return StandardAPIResponse.success(
            data=request.data,
            message="Security settings updated successfully"
        )


class SecurityPoliciesView(APIView):
    """Security policies endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        tenant = getattr(request, 'tenant', None)
        
        policies_qs = SecurityPolicy.objects.all()
        if tenant:
            policies_qs = policies_qs.filter(tenant=tenant)
        
        policies = policies_qs.order_by('-created_at')
        
        policies_data = []
        for policy in policies:
            policies_data.append({
                'id': str(policy.id),
                'name': policy.name,
                'policy_type': policy.policy_type,
                'description': policy.description,
                'is_active': policy.is_active,
                'is_enforced': policy.is_enforced,
                'compliance_frameworks': policy.compliance_frameworks,
                'created_at': policy.created_at.isoformat(),
                'updated_at': policy.updated_at.isoformat()
            })
        
        return StandardAPIResponse.success(
            data={'results': policies_data},
            message="Security policies retrieved successfully"
        )


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for comprehensive audit logs"""
    
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Filter audit logs by tenant"""
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            return AuditLog.objects.filter(tenant=tenant)
        return AuditLog.objects.all()
    
    def list(self, request):
        """Get filtered audit logs"""
        tenant = getattr(request, 'tenant', None)
        
        # Get query parameters
        user_id = request.GET.get('user_id')
        action = request.GET.get('action')
        resource_type = request.GET.get('resource_type')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        limit = int(request.GET.get('limit', 100))
        
        audit_logs = AuditService.get_audit_logs(
            tenant=tenant,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return StandardAPIResponse.success(
            data={'results': audit_logs},
            message="Audit logs retrieved successfully"
        )


class ComplianceView(APIView):
    """GDPR compliance and data management"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def export_user_data(self, request):
        """Export user data for GDPR compliance"""
        user_id = request.GET.get('user_id')
        
        # Users can only export their own data unless they're admin
        if user_id and user_id != str(request.user.id):
            if not request.user.is_staff:
                return StandardAPIResponse.permission_denied(
                    message="You can only export your own data"
                )
        
        target_user = request.user
        if user_id and request.user.is_staff:
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return StandardAPIResponse.not_found(message="User not found")
        
        user_data = ComplianceService.export_user_data(target_user)
        
        return StandardAPIResponse.success(
            data=user_data,
            message="User data exported successfully"
        )
    
    @action(detail=False, methods=['post'])
    def delete_user_data(self, request):
        """Delete user data for GDPR compliance"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can delete user data"
            )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return StandardAPIResponse.bad_request(message="User ID is required")
        
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return StandardAPIResponse.not_found(message="User not found")
        
        # Prevent deletion of superuser accounts
        if target_user.is_superuser:
            return StandardAPIResponse.bad_request(
                message="Cannot delete superuser accounts"
            )
        
        deletion_summary = ComplianceService.delete_user_data(target_user)
        
        return StandardAPIResponse.success(
            data=deletion_summary,
            message="User data deleted successfully"
        )


class ComplianceReportingView(APIView):
    """GDPR and compliance reporting"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Generate compliance report"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied()
        
        tenant = getattr(request, 'tenant', None)
        
        # Get compliance metrics
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        
        # Data processing activities
        audit_logs_qs = AuditLog.objects.all()
        if tenant:
            audit_logs_qs = audit_logs_qs.filter(tenant=tenant)
        
        # User data requests
        data_exports = audit_logs_qs.filter(
            action='export',
            resource_type='user_data',
            created_at__gte=last_30_days
        ).count()
        
        data_deletions = audit_logs_qs.filter(
            action='delete',
            resource_type='user_data',
            created_at__gte=last_30_days
        ).count()
        
        # Security incidents
        security_events_qs = SecurityEvent.objects.all()
        if tenant:
            security_events_qs = security_events_qs.filter(tenant=tenant)
        
        security_incidents = security_events_qs.filter(
            severity__in=['high', 'critical'],
            created_at__gte=last_30_days
        ).count()
        
        # Data retention compliance
        old_data_count = audit_logs_qs.filter(
            created_at__lt=now - timedelta(days=365)  # Data older than 1 year
        ).count()
        
        # User consent tracking (simplified)
        total_users = User.objects.count()
        active_users = User.objects.filter(
            is_active=True,
            last_login__gte=last_30_days
        ).count()
        
        compliance_report = {
            'report_period': {
                'start_date': last_30_days.isoformat(),
                'end_date': now.isoformat()
            },
            'data_subject_requests': {
                'data_exports': data_exports,
                'data_deletions': data_deletions,
                'total_requests': data_exports + data_deletions
            },
            'security_incidents': {
                'high_severity': security_incidents,
                'total_events': security_events_qs.filter(created_at__gte=last_30_days).count()
            },
            'data_retention': {
                'old_data_entries': old_data_count,
                'retention_policy_days': 365,
                'compliance_status': 'compliant' if old_data_count < 1000 else 'needs_attention'
            },
            'user_metrics': {
                'total_users': total_users,
                'active_users_30d': active_users,
                'user_activity_rate': round((active_users / max(total_users, 1)) * 100, 2)
            },
            'compliance_frameworks': [
                'GDPR',
                'CCPA',
                'SOC2'
            ],
            'generated_at': now.isoformat()
        }
        
        return StandardAPIResponse.success(
            data=compliance_report,
            message="Compliance report generated successfully"
        )


class DataRetentionView(APIView):
    """Data retention policy management"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get data retention policies"""
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        # Default retention policies
        retention_policies = {
            'audit_logs': {
                'retention_days': 365,
                'description': 'Audit logs are retained for 1 year for compliance',
                'auto_cleanup': True
            },
            'security_events': {
                'retention_days': 90,
                'description': 'Security events are retained for 90 days',
                'auto_cleanup': True
            },
            'user_data': {
                'retention_days': None,  # Retained until user deletion
                'description': 'User data is retained until account deletion',
                'auto_cleanup': False
            },
            'payment_records': {
                'retention_days': 2555,  # 7 years for tax purposes
                'description': 'Payment records retained for 7 years for tax compliance',
                'auto_cleanup': False
            }
        }
        
        return StandardAPIResponse.success(
            data={'policies': retention_policies},
            message="Data retention policies retrieved successfully"
        )
    
    def post(self, request):
        """Execute data retention cleanup"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied()
        
        # This would trigger the cleanup process
        # For now, return a mock response
        return StandardAPIResponse.success(
            data={
                'cleanup_scheduled': True,
                'estimated_completion': (timezone.now() + timedelta(hours=1)).isoformat()
            },
            message="Data retention cleanup scheduled successfully"
        )

@csrf_exempt
@require_http_methods(["POST", "PUT", "PATCH", "DELETE"])
def csrf_failure(request, reason=""):
    """Custom CSRF failure view"""
    
    # Log CSRF failure
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or request.META.get('REMOTE_ADDR', '')
    
    SecurityMonitoringService.log_security_event(
        event_type='intrusion_attempt',
        severity='medium',
        description=f'CSRF verification failed: {reason}',
        user=getattr(request, 'user', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        endpoint=request.path,
        method=request.method,
        additional_data={'csrf_failure_reason': reason}
    )
    
    return JsonResponse({
        'error': 'CSRF verification failed',
        'message': 'Cross-Site Request Forgery protection triggered',
        'code': 'CSRF_FAILURE'
    }, status=403)


class SecurityHealthView(APIView):
    """Security health check endpoint"""
    
    permission_classes = []  # Public endpoint for monitoring
    
    def get(self, request):
        """Get security health status"""
        
        # Basic security checks
        health_status = {
            'status': 'healthy',
            'checks': {
                'middleware_active': True,
                'rate_limiting': getattr(settings, 'RATE_LIMIT_ENABLE', False),
                'virus_scanning': getattr(settings, 'VIRUS_SCAN_ENABLED', False),
                'audit_logging': getattr(settings, 'AUDIT_LOG_ENABLED', False),
                'security_monitoring': getattr(settings, 'SECURITY_MONITORING_ENABLED', False),
            },
            'timestamp': timezone.now().isoformat()
        }
        
        # Check for recent security incidents
        recent_incidents = SecurityEvent.objects.filter(
            severity__in=['high', 'critical'],
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        if recent_incidents > 10:
            health_status['status'] = 'warning'
            health_status['warnings'] = [f'{recent_incidents} security incidents in last 24 hours']
        
        return JsonResponse(health_status)


class FileUploadSecurityView(APIView):
    """File upload security validation endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Validate file upload security"""
        
        if 'file' not in request.FILES:
            return StandardAPIResponse.bad_request(message="No file provided")
        
        uploaded_file = request.FILES['file']
        
        try:
            from apps.security.file_scanner import FileUploadSecurityScanner
            scanner = FileUploadSecurityScanner()
            
            scan_results = scanner.scan_uploaded_file(uploaded_file)
            
            return StandardAPIResponse.success(
                data={
                    'safe': scan_results['safe'],
                    'threats': scan_results.get('threats', []),
                    'warnings': scan_results.get('warnings', []),
                    'scan_summary': scanner.get_scan_summary(scan_results),
                    'file_info': scan_results.get('file_info', {}),
                    'risk_score': scan_results.get('analysis', {}).get('risk_score', 0)
                },
                message="File security scan completed"
            )
        
        except Exception as e:
            return StandardAPIResponse.error(
                message=f"Security scan failed: {str(e)}"
            )


class SecurityConfigView(APIView):
    """Security configuration management"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current security configuration"""
        
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied()
        
        config = {
            'rate_limiting': {
                'enabled': getattr(settings, 'RATE_LIMIT_ENABLE', True),
                'per_minute': getattr(settings, 'RATE_LIMIT_PER_MINUTE', 100),
                'per_hour': getattr(settings, 'RATE_LIMIT_PER_HOUR', 1000),
                'per_day': getattr(settings, 'RATE_LIMIT_PER_DAY', 10000),
            },
            'file_security': {
                'virus_scan_enabled': getattr(settings, 'VIRUS_SCAN_ENABLED', True),
                'quarantine_enabled': getattr(settings, 'FILE_QUARANTINE_ENABLED', True),
                'max_file_size_mb': getattr(settings, 'MAX_FILE_SIZE_MB', 100),
                'allowed_extensions': getattr(settings, 'ALLOWED_FILE_EXTENSIONS', []),
                'blocked_extensions': getattr(settings, 'BLOCKED_FILE_EXTENSIONS', []),
            },
            'monitoring': {
                'security_monitoring_enabled': getattr(settings, 'SECURITY_MONITORING_ENABLED', True),
                'failed_login_threshold': getattr(settings, 'FAILED_LOGIN_THRESHOLD', 5),
                'account_lockout_duration': getattr(settings, 'ACCOUNT_LOCKOUT_DURATION', 900),
                'intrusion_detection_enabled': getattr(settings, 'INTRUSION_DETECTION_ENABLED', True),
            },
            'audit_logging': {
                'enabled': getattr(settings, 'AUDIT_LOG_ENABLED', True),
                'retention_days': getattr(settings, 'AUDIT_LOG_RETENTION_DAYS', 365),
            },
            'gdpr_compliance': {
                'enabled': getattr(settings, 'GDPR_COMPLIANCE_ENABLED', True),
                'data_retention_days': getattr(settings, 'DATA_RETENTION_DAYS', 365),
                'auto_delete_inactive_users_days': getattr(settings, 'AUTO_DELETE_INACTIVE_USERS_DAYS', 730),
                'consent_tracking_enabled': getattr(settings, 'CONSENT_TRACKING_ENABLED', True),
            }
        }
        
        return StandardAPIResponse.success(
            data=config,
            message="Security configuration retrieved successfully"
        )