from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import AuditLog
from apps.accounts.models import User, Organization
from apps.courses.models import Course, Enrollment
from apps.payments.models import Payment


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AuditLog model - read only"""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter audit logs by tenant"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return AuditLog.objects.filter(tenant=self.request.tenant)
        return AuditLog.objects.all()


class AdminDashboardView(viewsets.ViewSet):
    """Admin dashboard with analytics"""
    
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get dashboard statistics"""
        tenant = getattr(request, 'tenant', None)
        
        # Base querysets
        users_qs = User.objects.all()
        courses_qs = Course.objects.all()
        enrollments_qs = Enrollment.objects.all()
        payments_qs = Payment.objects.all()
        
        # Filter by tenant if available
        if tenant:
            users_qs = users_qs.filter(profile__tenant=tenant)
            courses_qs = courses_qs.filter(tenant=tenant)
            enrollments_qs = enrollments_qs.filter(tenant=tenant)
            payments_qs = payments_qs.filter(tenant=tenant)
        
        # Calculate stats
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        
        stats = {
            'users': {
                'total': users_qs.count(),
                'new_this_month': users_qs.filter(date_joined__gte=last_30_days).count(),
                'teachers': users_qs.filter(is_teacher=True).count(),
                'approved_teachers': users_qs.filter(is_approved_teacher=True).count(),
            },
            'courses': {
                'total': courses_qs.count(),
                'public': courses_qs.filter(is_public=True).count(),
                'private': courses_qs.filter(is_public=False).count(),
                'new_this_month': courses_qs.filter(created_at__gte=last_30_days).count(),
            },
            'enrollments': {
                'total': enrollments_qs.count(),
                'active': enrollments_qs.filter(status='active').count(),
                'completed': enrollments_qs.filter(status='completed').count(),
                'new_this_month': enrollments_qs.filter(enrolled_at__gte=last_30_days).count(),
            },
            'payments': {
                'total': payments_qs.count(),
                'completed': payments_qs.filter(status='completed').count(),
                'total_revenue': payments_qs.filter(status='completed').aggregate(
                    total=models.Sum('amount')
                )['total'] or 0,
                'this_month_revenue': payments_qs.filter(
                    status='completed',
                    completed_at__gte=last_30_days
                ).aggregate(total=models.Sum('amount'))['total'] or 0,
            }
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Get recent system activity"""
        tenant = getattr(request, 'tenant', None)
        
        audit_logs = AuditLog.objects.all()
        if tenant:
            audit_logs = audit_logs.filter(tenant=tenant)
        
        recent_logs = audit_logs[:50]  # Last 50 activities
        
        activity_data = []
        for log in recent_logs:
            activity_data.append({
                'id': log.id,
                'user': log.user.email if log.user else 'System',
                'action': log.action,
                'object_type': log.object_type,
                'object_repr': log.object_repr,
                'timestamp': log.timestamp,
                'ip_address': log.ip_address
            })
        
        return Response(activity_data)
    
    @action(detail=False, methods=['get'])
    def user_analytics(self, request):
        """Get user analytics"""
        tenant = getattr(request, 'tenant', None)
        
        users_qs = User.objects.all()
        if tenant:
            users_qs = users_qs.filter(profile__tenant=tenant)
        
        # User registration trends (last 12 months)
        registration_trends = []
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            count = users_qs.filter(
                date_joined__gte=month_start,
                date_joined__lt=month_end
            ).count()
            
            registration_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })
        
        # User activity by role
        role_stats = {
            'students': users_qs.filter(is_teacher=False).count(),
            'teachers': users_qs.filter(is_teacher=True, is_approved_teacher=True).count(),
            'pending_teachers': users_qs.filter(is_teacher=True, is_approved_teacher=False).count(),
            'staff': users_qs.filter(is_staff=True).count(),
        }
        
        return Response({
            'registration_trends': registration_trends,
            'role_stats': role_stats
        })