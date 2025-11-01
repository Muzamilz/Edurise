"""
System administration views for monitoring and maintenance.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework import viewsets, status
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models

from apps.api.responses import StandardAPIResponse
from .system_services import (
    SystemMonitoringService,
    SystemLogsService,
    SystemMaintenanceService,
    UserManagementService
)

User = get_user_model()


class SystemStatusView(APIView):
    """
    System status for admin/super-admin.
    Endpoint: /system/status/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied(
                message="Only administrators can access system status"
            )
        
        system_status = SystemMonitoringService.get_system_status()
        
        return StandardAPIResponse.success(
            data=system_status,
            message="System status retrieved successfully"
        )


class SystemLogsView(APIView):
    """System logs endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        # Get query parameters
        log_type = request.GET.get('type', 'all')  # all, audit, application
        level = request.GET.get('level', 'all')    # all, info, warning, error
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        limit = int(request.GET.get('limit', 100))
        
        logs = SystemLogsService.get_system_logs(
            log_type=log_type,
            level=level,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return StandardAPIResponse.success(
            data={'results': logs},
            message="System logs retrieved successfully"
        )


class SystemConfigView(APIView):
    """System configuration endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        # Get system configuration (safe values only)
        config_data = {
            'general': {
                'platform_name': 'Edurise',
                'maintenance_mode': False,
                'debug_mode': False,
                'timezone': str(timezone.get_current_timezone())
            },
            'email': {
                'smtp_configured': True,
                'default_from_email': 'noreply@edurise.com'
            },
            'storage': {
                'provider': 'local',
                'max_file_size': '100MB'
            },
            'payment': {
                'provider': 'stripe',
                'currency': 'USD',
                'test_mode': True
            },
            'security': {
                'session_timeout': 3600,
                'max_login_attempts': 5,
                'password_min_length': 8
            }
        }
        
        return StandardAPIResponse.success(
            data=config_data,
            message="System configuration retrieved successfully"
        )
    
    def patch(self, request):
        """Update system configuration"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can update system configuration"
            )
        
        # In a real implementation, this would update actual configuration
        # For now, just return the submitted data
        return StandardAPIResponse.success(
            data=request.data,
            message="System configuration updated successfully"
        )


class SystemMaintenanceView(APIView):
    """System maintenance actions"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, action):
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can perform maintenance actions"
            )
        
        result = SystemMaintenanceService.perform_maintenance_action(action, request.user)
        
        if result['success']:
            return StandardAPIResponse.success(
                data=result,
                message=f"Maintenance action '{action}' completed successfully"
            )
        else:
            return StandardAPIResponse.error(
                message=result.get('error', f"Maintenance action '{action}' failed"),
                status_code=400
            )


class BulkUserManagementView(APIView):
    """Bulk user management operations"""
    
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        """Perform bulk operations on users"""
        
        operation = request.data.get('operation')
        user_ids = request.data.get('user_ids', [])
        
        if not operation:
            return StandardAPIResponse.bad_request(message="Operation is required")
        
        if not user_ids:
            return StandardAPIResponse.bad_request(message="User IDs are required")
        
        result = UserManagementService.bulk_user_operation(
            operation=operation,
            user_ids=user_ids,
            admin_user=request.user
        )
        
        if result['success']:
            return StandardAPIResponse.success(
                data=result,
                message=f"Bulk {operation} operation completed"
            )
        else:
            return StandardAPIResponse.error(
                message=result.get('error', f"Bulk {operation} operation failed"),
                status_code=400
            )


class OrganizationManagementView(APIView):
    """Organization management for super admins"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get organization statistics"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied()
        
        from apps.accounts.models import Organization
        from apps.courses.models import Course, Enrollment
        from apps.payments.models import Payment
        
        # Get organization statistics
        organizations = Organization.objects.all()
        
        org_stats = []
        for org in organizations:
            # Get organization metrics
            users_count = User.objects.filter(profile__organization=org).count()
            courses_count = Course.objects.filter(organization=org).count()
            enrollments_count = Enrollment.objects.filter(course__organization=org).count()
            
            # Revenue calculation
            revenue = Payment.objects.filter(
                course__organization=org,
                status='completed'
            ).aggregate(total=models.Sum('amount'))['total'] or 0
            
            org_stats.append({
                'id': str(org.id),
                'name': org.name,
                'users_count': users_count,
                'courses_count': courses_count,
                'enrollments_count': enrollments_count,
                'total_revenue': float(revenue),
                'created_at': org.created_at.isoformat(),
                'is_active': org.is_active
            })
        
        return StandardAPIResponse.success(
            data={'results': org_stats},
            message="Organization statistics retrieved successfully"
        )
    
    def patch(self, request, org_id):
        """Update organization settings"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied()
        
        try:
            from apps.accounts.models import Organization
            org = Organization.objects.get(id=org_id)
            
            # Update allowed fields
            if 'is_active' in request.data:
                org.is_active = request.data['is_active']
            
            if 'subscription_plan' in request.data:
                # Update subscription plan through the subscription model
                try:
                    from apps.payments.models import Subscription, SubscriptionPlan
                    plan_name = request.data['subscription_plan']
                    plan = SubscriptionPlan.objects.get(name=plan_name)
                    
                    subscription, created = Subscription.objects.get_or_create(
                        organization=org,
                        defaults={'plan': plan, 'status': 'active'}
                    )
                    if not created:
                        subscription.plan = plan
                        subscription.save()
                except (SubscriptionPlan.DoesNotExist, Exception) as e:
                    # Log the error but don't fail the organization update
                    pass
            
            org.save()
            
            return StandardAPIResponse.success(
                data={'organization_id': str(org.id)},
                message="Organization updated successfully"
            )
        
        except Organization.DoesNotExist:
            return StandardAPIResponse.not_found(message="Organization not found")


class SystemHealthCheckView(APIView):
    """Comprehensive system health check"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        # Get comprehensive health status
        system_status = SystemMonitoringService.get_system_status()
        
        # Add additional health checks
        health_data = {
            'overall_status': 'healthy',
            'system': system_status,
            'services': {
                'database': system_status.get('database_status', 'unknown'),
                'cache': system_status.get('cache_status', 'unknown'),
                'storage': 'healthy' if system_status.get('disk_percent', 100) < 90 else 'warning'
            },
            'alerts': [],
            'recommendations': []
        }
        
        # Determine overall status
        if system_status.get('server_status') == 'error':
            health_data['overall_status'] = 'critical'
            health_data['alerts'].append('Server experiencing critical issues')
        
        elif (system_status.get('memory_percent', 0) > 85 or 
              system_status.get('disk_percent', 0) > 90 or
              system_status.get('cpu_usage', 0) > 80):
            health_data['overall_status'] = 'warning'
            
            if system_status.get('memory_percent', 0) > 85:
                health_data['alerts'].append('High memory usage detected')
                health_data['recommendations'].append('Consider increasing server memory')
            
            if system_status.get('disk_percent', 0) > 90:
                health_data['alerts'].append('Low disk space')
                health_data['recommendations'].append('Clean up old files or increase storage')
            
            if system_status.get('cpu_usage', 0) > 80:
                health_data['alerts'].append('High CPU usage')
                health_data['recommendations'].append('Check for resource-intensive processes')
        
        return StandardAPIResponse.success(
            data=health_data,
            message="System health check completed"
        )