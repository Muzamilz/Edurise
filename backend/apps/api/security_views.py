from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from django.db.models import Count, Q, Sum
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session

from apps.accounts.models import Organization
from apps.courses.models import Course, Enrollment
from apps.payments.models import Payment
from .responses import StandardAPIResponse

User = get_user_model()


class SecurityOverviewView(APIView):
    """
    Security overview endpoint for super admin dashboard
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get security overview data"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can access security data"
            )
        
        # Calculate security metrics
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        
        # Mock failed login attempts (would need proper logging system)
        failed_logins_24h = 0  # Placeholder
        
        # Active sessions count
        active_sessions = Session.objects.filter(expire_date__gte=now).count()
        
        # Active threats (placeholder - would need security monitoring)
        active_threats = 0
        
        # Compliance score calculation (basic)
        total_users = User.objects.count()
        users_with_recent_activity = User.objects.filter(
            last_login__gte=now - timedelta(days=30)
        ).count()
        
        # Basic compliance score based on user activity
        compliance_score = min(100, int((users_with_recent_activity / max(total_users, 1)) * 100))
        
        security_data = {
            'active_threats': active_threats,
            'failed_logins_24h': failed_logins_24h,
            'active_sessions': active_sessions,
            'compliance_score': compliance_score,
            'last_updated': now.isoformat()
        }
        
        return StandardAPIResponse.success(
            data=security_data,
            message="Security overview retrieved successfully"
        )


class PlatformAnalyticsView(APIView):
    """
    Platform analytics endpoint for super admin
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get platform analytics data"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can access platform analytics"
            )
        
        # Time periods
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        # User analytics
        total_users = User.objects.count()
        new_users_30d = User.objects.filter(date_joined__gte=last_30_days).count()
        active_users_7d = User.objects.filter(last_login__gte=last_7_days).count()
        
        # Organization analytics
        total_orgs = Organization.objects.count()
        active_orgs = Organization.objects.filter(is_active=True).count()
        
        # Course analytics
        total_courses = Course.objects.count()
        published_courses = Course.objects.filter(is_public=True).count()
        new_courses_30d = Course.objects.filter(created_at__gte=last_30_days).count()
        
        # Enrollment analytics
        total_enrollments = Enrollment.objects.count()
        new_enrollments_30d = Enrollment.objects.filter(enrolled_at__gte=last_30_days).count()
        active_enrollments = Enrollment.objects.filter(status='active').count()
        
        # Revenue analytics
        total_revenue = Payment.objects.filter(status='completed').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        revenue_30d = Payment.objects.filter(
            status='completed',
            created_at__gte=last_30_days
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        # Growth calculations
        user_growth_rate = (new_users_30d / max(total_users - new_users_30d, 1)) * 100
        course_growth_rate = (new_courses_30d / max(total_courses - new_courses_30d, 1)) * 100
        enrollment_growth_rate = (new_enrollments_30d / max(total_enrollments - new_enrollments_30d, 1)) * 100
        
        analytics_data = {
            'user_metrics': {
                'total_users': total_users,
                'new_users_30d': new_users_30d,
                'active_users_7d': active_users_7d,
                'growth_rate': round(user_growth_rate, 2)
            },
            'organization_metrics': {
                'total_organizations': total_orgs,
                'active_organizations': active_orgs,
                'activation_rate': round((active_orgs / max(total_orgs, 1)) * 100, 2)
            },
            'course_metrics': {
                'total_courses': total_courses,
                'published_courses': published_courses,
                'new_courses_30d': new_courses_30d,
                'growth_rate': round(course_growth_rate, 2),
                'publish_rate': round((published_courses / max(total_courses, 1)) * 100, 2)
            },
            'enrollment_metrics': {
                'total_enrollments': total_enrollments,
                'new_enrollments_30d': new_enrollments_30d,
                'active_enrollments': active_enrollments,
                'growth_rate': round(enrollment_growth_rate, 2)
            },
            'revenue_metrics': {
                'total_revenue': float(total_revenue),
                'revenue_30d': float(revenue_30d),
                'average_revenue_per_user': float(total_revenue / max(total_users, 1))
            },
            'generated_at': now.isoformat()
        }
        
        return StandardAPIResponse.success(
            data=analytics_data,
            message="Platform analytics retrieved successfully"
        )


class GlobalFinancialView(APIView):
    """
    Global financial data endpoint for super admin
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get global financial data"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can access financial data"
            )
        
        # Time periods
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        
        # Revenue by status
        completed_payments = Payment.objects.filter(status='completed')
        total_revenue = completed_payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        current_month_revenue = completed_payments.filter(
            created_at__gte=current_month_start
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        last_month_revenue = completed_payments.filter(
            created_at__gte=last_month_start,
            created_at__lt=current_month_start
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        # Revenue by organization
        revenue_by_org = []
        for org in Organization.objects.filter(is_active=True):
            org_revenue = completed_payments.filter(tenant=org).aggregate(
                total=models.Sum('amount')
            )['total'] or 0
            
            # Get additional org stats
            org_payments_count = completed_payments.filter(tenant=org).count()
            org_current_month = completed_payments.filter(
                tenant=org,
                created_at__gte=current_month_start
            ).aggregate(total=models.Sum('amount'))['total'] or 0
            
            org_last_month = completed_payments.filter(
                tenant=org,
                created_at__gte=last_month_start,
                created_at__lt=current_month_start
            ).aggregate(total=models.Sum('amount'))['total'] or 0
            
            org_growth = 0
            if org_last_month > 0:
                org_growth = ((org_current_month - org_last_month) / org_last_month) * 100
            
            revenue_by_org.append({
                'organization_id': str(org.id),
                'organization_name': org.name,
                'subdomain': org.subdomain,
                'total_revenue': float(org_revenue),
                'monthly_growth': round(org_growth, 2),
                'transactions': org_payments_count,
                'commission_earned': float(float(org_revenue) * 0.05),  # 5% commission
                'pending_payout': float(float(org_revenue) * 0.95),  # 95% to organization
                'status': 'active' if org.is_active else 'inactive'
            })
        
        # Sort by revenue
        revenue_by_org.sort(key=lambda x: x['total_revenue'], reverse=True)
        
        # Growth calculation
        growth_rate = 0
        if last_month_revenue > 0:
            growth_rate = ((current_month_revenue - last_month_revenue) / last_month_revenue) * 100
        
        # Revenue trend (last 6 months)
        revenue_trend = []
        for i in range(6):
            month_start = now - timedelta(days=30 * (i + 1))
            month_end = now - timedelta(days=30 * i)
            month_revenue = completed_payments.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).aggregate(total=models.Sum('amount'))['total'] or 0
            
            revenue_trend.append({
                'month': month_start.strftime('%b %Y'),
                'revenue': float(month_revenue),
                'transactions': completed_payments.filter(
                    created_at__gte=month_start,
                    created_at__lt=month_end
                ).count()
            })
        
        financial_data = {
            'total_revenue': float(total_revenue),
            'current_month_revenue': float(current_month_revenue),
            'last_month_revenue': float(last_month_revenue),
            'growth_rate': round(growth_rate, 2),
            'revenue_by_organization': revenue_by_org,
            'revenue_trend': list(reversed(revenue_trend)),
            'total_transactions': completed_payments.count(),
            'average_transaction': float(total_revenue / max(completed_payments.count(), 1)),
            'total_commission': float(float(total_revenue) * 0.05),
            'total_payouts': float(float(total_revenue) * 0.95),
            'generated_at': now.isoformat()
        }
        
        return StandardAPIResponse.success(
            data=financial_data,
            message="Global financial data retrieved successfully"
        )


class SystemHealthView(APIView):
    """
    System health endpoint for super admin
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get system health data"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can access system health data"
            )
        
        # Basic system health checks
        try:
            # Database health
            db_healthy = True
            user_count = User.objects.count()  # Simple DB query test
        except Exception:
            db_healthy = False
            user_count = 0
        
        # Calculate system metrics
        now = timezone.now()
        
        # Active sessions as a proxy for system load
        active_sessions = Session.objects.filter(expire_date__gte=now).count()
        
        # Recent activity as system usage indicator
        recent_logins = User.objects.filter(
            last_login__gte=now - timedelta(hours=1)
        ).count()
        
        # System status
        system_status = 'healthy' if db_healthy else 'degraded'
        
        health_data = {
            'database_status': 'healthy' if db_healthy else 'error',
            'cache_status': 'healthy',  # Placeholder
            'storage_status': 'healthy',  # Placeholder
            'api_status': 'healthy',
            'system_status': system_status,
            'active_sessions': active_sessions,
            'recent_logins_1h': recent_logins,
            'total_users': user_count,
            'uptime_percentage': 99.9,  # Placeholder
            'last_check': now.isoformat()
        }
        
        return StandardAPIResponse.success(
            data=health_data,
            message="System health data retrieved successfully"
        )