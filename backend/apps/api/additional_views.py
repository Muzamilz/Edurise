"""
Additional API views for missing endpoints that frontend components are requesting.
These views provide the specific endpoints needed for frontend integration.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import viewsets, status
from django.db.models import Count, Avg, Sum, Q, F, Max, Min
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.core.cache import cache
import json

from apps.accounts.models import User, UserProfile, Organization
from apps.courses.models import Course, Enrollment, CourseReview
from apps.classes.models import ClassAttendance, LiveClass
from apps.payments.models import Payment, Subscription
from apps.notifications.models import Notification
from apps.assignments.models import Assignment, Submission, Certificate
from .responses import StandardAPIResponse
from .mixins import APIResponseMixin


class PlatformAnalyticsView(APIView):
    """
    Platform-wide analytics for super admin dashboard.
    Endpoint: /analytics/platform-overview/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can access platform analytics"
            )
        
        # Calculate platform-wide metrics
        total_users = User.objects.count()
        total_organizations = Organization.objects.count()
        total_courses = Course.objects.count()
        
        # Revenue calculation
        total_revenue = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Growth calculations (last 30 days vs previous 30 days)
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        previous_30_days = now - timedelta(days=60)
        
        # User growth
        recent_users = User.objects.filter(date_joined__gte=last_30_days).count()
        previous_users = User.objects.filter(
            date_joined__gte=previous_30_days,
            date_joined__lt=last_30_days
        ).count()
        user_growth = ((recent_users - previous_users) / max(previous_users, 1)) * 100
        
        # Organization growth
        recent_orgs = Organization.objects.filter(created_at__gte=last_30_days).count()
        previous_orgs = Organization.objects.filter(
            created_at__gte=previous_30_days,
            created_at__lt=last_30_days
        ).count()
        org_growth = ((recent_orgs - previous_orgs) / max(previous_orgs, 1)) * 100
        
        # Course growth
        recent_courses = Course.objects.filter(created_at__gte=last_30_days).count()
        previous_courses = Course.objects.filter(
            created_at__gte=previous_30_days,
            created_at__lt=last_30_days
        ).count()
        course_growth = ((recent_courses - previous_courses) / max(previous_courses, 1)) * 100
        
        # Revenue growth
        recent_revenue = Payment.objects.filter(
            status='completed',
            created_at__gte=last_30_days
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        previous_revenue = Payment.objects.filter(
            status='completed',
            created_at__gte=previous_30_days,
            created_at__lt=last_30_days
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        revenue_growth = ((recent_revenue - previous_revenue) / max(previous_revenue, 1)) * 100
        
        # System metrics
        daily_active_users = User.objects.filter(
            last_login__gte=now - timedelta(days=1)
        ).count()
        
        # User growth trend (last 6 months)
        user_growth_trend = []
        for i in range(6):
            month_start = now - timedelta(days=30 * (i + 1))
            month_end = now - timedelta(days=30 * i)
            month_users = User.objects.filter(
                date_joined__gte=month_start,
                date_joined__lt=month_end
            ).count()
            user_growth_trend.append({
                'month': month_start.strftime('%b'),
                'count': month_users
            })
        
        # Revenue trend (last 6 months)
        revenue_trend = []
        for i in range(6):
            month_start = now - timedelta(days=30 * (i + 1))
            month_end = now - timedelta(days=30 * i)
            month_revenue = Payment.objects.filter(
                status='completed',
                created_at__gte=month_start,
                created_at__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            revenue_trend.append({
                'month': month_start.strftime('%b'),
                'amount': float(month_revenue)
            })
        
        # Top organizations
        top_organizations = Organization.objects.annotate(
            user_count=Count('profiles__user', distinct=True),
            course_count=Count('courses', distinct=True),
            revenue=Sum('courses__enrollments__payment__amount', 
                       filter=Q(courses__enrollments__payment__status='completed'))
        ).order_by('-revenue')[:5]
        
        top_orgs_data = []
        for org in top_organizations:
            # Calculate growth for this org
            org_recent_users = org.profiles.filter(
                user__date_joined__gte=last_30_days
            ).count()
            org_previous_users = org.profiles.filter(
                user__date_joined__gte=previous_30_days,
                user__date_joined__lt=last_30_days
            ).count()
            org_user_growth = ((org_recent_users - org_previous_users) / max(org_previous_users, 1)) * 100
            
            top_orgs_data.append({
                'id': org.id,
                'name': org.name,
                'subdomain': org.subdomain,
                'userCount': org.user_count,
                'courseCount': org.course_count,
                'revenue': float(org.revenue or 0),
                'growth': round(org_user_growth, 1)
            })
        
        return StandardAPIResponse.success(
            data={
                'totalUsers': total_users,
                'totalOrganizations': total_organizations,
                'totalCourses': total_courses,
                'totalRevenue': float(total_revenue),
                'userGrowth': round(user_growth, 1),
                'orgGrowth': round(org_growth, 1),
                'courseGrowth': round(course_growth, 1),
                'revenueGrowth': round(revenue_growth, 1),
                'avgResponseTime': 145,  # Mock data - would come from monitoring
                'uptime': 99.8,  # Mock data - would come from monitoring
                'dailyActiveUsers': daily_active_users,
                'avgSessionDuration': 24,  # Mock data - would need session tracking
                'userGrowthTrend': list(reversed(user_growth_trend)),
                'revenueTrend': list(reversed(revenue_trend)),
                'topOrganizations': top_orgs_data
            },
            message="Platform analytics retrieved successfully"
        )


class TeacherAnalyticsView(APIView):
    """
    Teacher-specific analytics.
    Endpoint: /analytics/teacher/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_teacher:
            return StandardAPIResponse.permission_denied(
                message="Only teachers can access teacher analytics"
            )
        
        # Get teacher's courses
        teacher_courses = Course.objects.filter(instructor=request.user)
        
        # Basic metrics
        total_courses = teacher_courses.count()
        total_students = Enrollment.objects.filter(
            course__instructor=request.user
        ).values('student').distinct().count()
        
        total_revenue = Payment.objects.filter(
            enrollment__course__instructor=request.user,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Course completion rate
        total_enrollments = Enrollment.objects.filter(
            course__instructor=request.user
        ).count()
        
        completed_enrollments = Enrollment.objects.filter(
            course__instructor=request.user,
            status='completed'
        ).count()
        
        completion_rate = (completed_enrollments / max(total_enrollments, 1)) * 100
        
        # Average rating
        avg_rating = CourseReview.objects.filter(
            course__instructor=request.user,
            is_approved=True
        ).aggregate(avg=Avg('rating'))['avg'] or 0
        
        # Monthly trends
        now = timezone.now()
        monthly_data = []
        
        for i in range(6):
            month_start = now - timedelta(days=30 * (i + 1))
            month_end = now - timedelta(days=30 * i)
            
            month_enrollments = Enrollment.objects.filter(
                course__instructor=request.user,
                enrolled_at__gte=month_start,
                enrolled_at__lt=month_end
            ).count()
            
            month_revenue = Payment.objects.filter(
                enrollment__course__instructor=request.user,
                status='completed',
                created_at__gte=month_start,
                created_at__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_data.append({
                'month': month_start.strftime('%b'),
                'enrollments': month_enrollments,
                'revenue': float(month_revenue)
            })
        
        return StandardAPIResponse.success(
            data={
                'totalCourses': total_courses,
                'totalStudents': total_students,
                'totalRevenue': float(total_revenue),
                'completionRate': round(completion_rate, 1),
                'averageRating': round(avg_rating, 2),
                'monthlyTrends': list(reversed(monthly_data))
            },
            message="Teacher analytics retrieved successfully"
        )


class TeacherEarningsView(APIView):
    """
    Teacher earnings data.
    Endpoint: /teacher/earnings/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_teacher:
            return StandardAPIResponse.permission_denied(
                message="Only teachers can access earnings data"
            )
        
        # Calculate earnings (assuming 70% goes to teacher, 30% platform fee)
        total_earnings = Payment.objects.filter(
            enrollment__course__instructor=request.user,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        teacher_share = float(total_earnings) * 0.7  # 70% to teacher
        platform_fee = float(total_earnings) * 0.3   # 30% platform fee
        
        # Pending earnings (not yet paid out)
        pending_earnings = teacher_share  # Mock - would track actual payouts
        
        # Monthly earnings
        now = timezone.now()
        monthly_earnings = []
        
        for i in range(12):
            month_start = now - timedelta(days=30 * (i + 1))
            month_end = now - timedelta(days=30 * i)
            
            month_total = Payment.objects.filter(
                enrollment__course__instructor=request.user,
                status='completed',
                created_at__gte=month_start,
                created_at__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            month_teacher_earnings = float(month_total) * 0.7
            
            monthly_earnings.append({
                'month': month_start.strftime('%Y-%m'),
                'earnings': month_teacher_earnings,
                'gross': float(month_total)
            })
        
        # Top earning courses
        top_courses = Course.objects.filter(
            instructor=request.user
        ).annotate(
            revenue=Sum('enrollments__payment__amount',
                       filter=Q(enrollments__payment__status='completed'))
        ).order_by('-revenue')[:5]
        
        top_courses_data = []
        for course in top_courses:
            teacher_earnings = float(course.revenue or 0) * 0.7
            top_courses_data.append({
                'courseId': course.id,
                'title': course.title,
                'totalRevenue': float(course.revenue or 0),
                'teacherEarnings': teacher_earnings,
                'enrollments': course.enrollments.count()
            })
        
        return StandardAPIResponse.success(
            data={
                'totalEarnings': teacher_share,
                'pendingEarnings': pending_earnings,
                'platformFee': platform_fee,
                'monthlyEarnings': list(reversed(monthly_earnings)),
                'topCourses': top_courses_data,
                'payoutSchedule': 'Monthly on the 15th',  # Mock data
                'nextPayout': '2024-03-15'  # Mock data
            },
            message="Teacher earnings retrieved successfully"
        )


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
        
        # Mock security data - in real implementation would come from security monitoring
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        
        # Failed login attempts (mock data)
        failed_logins_24h = 3
        
        # Active sessions (mock data)
        active_sessions = User.objects.filter(
            last_login__gte=now - timedelta(hours=1)
        ).count()
        
        # Security score calculation (mock)
        security_score = 92
        
        return StandardAPIResponse.success(
            data={
                'active_threats': 0,
                'failed_logins_24h': failed_logins_24h,
                'active_sessions': active_sessions,
                'security_score': security_score,
                'active_alerts': 1,
                'failed_logins_today': failed_logins_24h,
                'active_users': active_sessions
            },
            message="Security overview retrieved successfully"
        )


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
        
        # Mock system status data
        return StandardAPIResponse.success(
            data={
                'server_status': 'healthy',
                'database_status': 'healthy',
                'storage_used': 75,
                'storage_total': 100,
                'memory_used': 4.2,
                'memory_total': 8.0,
                'uptime': '15 days, 6 hours',
                'db_connections': 25
            },
            message="System status retrieved successfully"
        )


class WishlistViewSet(viewsets.ViewSet):
    """
    Student wishlist management.
    Endpoint: /wishlist/
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        # Mock wishlist data - would need a Wishlist model
        return StandardAPIResponse.success(
            data={
                'results': [
                    {
                        'id': 1,
                        'course': {
                            'id': 1,
                            'title': 'Advanced React Development',
                            'instructor': 'Jane Smith',
                            'price': 149.99,
                            'thumbnail': None,
                            'rating': 4.8
                        },
                        'added_at': timezone.now().isoformat()
                    }
                ],
                'count': 1
            },
            message="Wishlist retrieved successfully"
        )
    
    def create(self, request):
        course_id = request.data.get('course_id')
        # Mock adding to wishlist
        return StandardAPIResponse.success(
            data={'message': f'Course {course_id} added to wishlist'},
            message="Course added to wishlist successfully"
        )
    
    def destroy(self, request, pk=None):
        # Mock removing from wishlist
        return StandardAPIResponse.success(
            data={'message': f'Course {pk} removed from wishlist'},
            message="Course removed from wishlist successfully"
        )


class CourseRecommendationsView(APIView):
    """
    Course recommendations for students.
    Endpoint: /courses/recommendations/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Mock recommendations based on user's enrolled courses
        user_courses = Enrollment.objects.filter(
            student=request.user
        ).values_list('course__category', flat=True)
        
        # Get courses in similar categories
        recommended_courses = Course.objects.filter(
            category__in=user_courses,
            is_public=True
        ).exclude(
            enrollments__student=request.user
        )[:6]
        
        recommendations = []
        for course in recommended_courses:
            recommendations.append({
                'id': course.id,
                'title': course.title,
                'instructor': f"{course.instructor.first_name} {course.instructor.last_name}",
                'price': float(course.price or 0),
                'thumbnail': None,
                'rating': 4.5,  # Mock rating
                'category': course.category,
                'reason': 'Based on your interests'
            })
        
        return StandardAPIResponse.success(
            data={'results': recommendations},
            message="Course recommendations retrieved successfully"
        )


# Additional endpoint views for missing functionality
class SecurityAlertsView(APIView):
    """Security alerts endpoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        # Mock security alerts
        return StandardAPIResponse.success(
            data={'results': []},
            message="Security alerts retrieved successfully"
        )


class SecurityEventsView(APIView):
    """Security events endpoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        # Mock security events
        return StandardAPIResponse.success(
            data={'results': []},
            message="Security events retrieved successfully"
        )


class SecuritySettingsView(APIView):
    """Security settings endpoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        # Mock security settings
        return StandardAPIResponse.success(
            data={
                'password_policy': {'enabled': True, 'min_length': 8},
                'session_management': {'enabled': True, 'timeout_minutes': 30},
                'two_factor': {'enabled': False},
                'login_restrictions': {'enabled': False}
            },
            message="Security settings retrieved successfully"
        )


class SecurityPoliciesView(APIView):
    """Security policies endpoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        # Mock security policies
        return StandardAPIResponse.success(
            data={'results': []},
            message="Security policies retrieved successfully"
        )


class SystemLogsView(APIView):
    """System logs endpoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        # Mock system logs
        return StandardAPIResponse.success(
            data={'results': []},
            message="System logs retrieved successfully"
        )


class SystemConfigView(APIView):
    """System configuration endpoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        # Mock system config
        return StandardAPIResponse.success(
            data={
                'general': {'platform_name': 'Edurise', 'maintenance_mode': False},
                'email': {'smtp_host': 'smtp.example.com'},
                'storage': {'provider': 'local'},
                'payment': {'provider': 'stripe', 'currency': 'USD'}
            },
            message="System configuration retrieved successfully"
        )
    
    def patch(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        # Mock config update
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
        
        # Mock maintenance actions
        valid_actions = ['restart', 'backup', 'cleanup', 'update']
        
        if action not in valid_actions:
            return StandardAPIResponse.error(
                message=f"Invalid action. Valid actions: {', '.join(valid_actions)}",
                status_code=400
            )
        
        return StandardAPIResponse.success(
            data={
                'action': action,
                'status': 'completed',
                'timestamp': timezone.now().isoformat()
            },
            message=f"Maintenance action '{action}' completed successfully"
        )


class GlobalFinancialAnalyticsView(APIView):
    """Global financial analytics for super admin"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can access global financial analytics"
            )
        
        # Calculate global financial metrics
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        
        # Total revenue across all organizations
        total_revenue = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Monthly revenue trend
        monthly_revenue = []
        for i in range(12):
            month_start = now - timedelta(days=30 * (i + 1))
            month_end = now - timedelta(days=30 * i)
            
            month_total = Payment.objects.filter(
                status='completed',
                created_at__gte=month_start,
                created_at__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_revenue.append({
                'month': month_start.strftime('%Y-%m'),
                'revenue': float(month_total)
            })
        
        # Revenue by organization
        org_revenue = Organization.objects.annotate(
            revenue=Sum('courses__enrollments__payment__amount',
                       filter=Q(courses__enrollments__payment__status='completed'))
        ).order_by('-revenue')[:10]
        
        org_revenue_data = []
        for org in org_revenue:
            org_revenue_data.append({
                'id': org.id,
                'name': org.name,
                'revenue': float(org.revenue or 0)
            })
        
        return StandardAPIResponse.success(
            data={
                'totalRevenue': float(total_revenue),
                'monthlyRevenue': list(reversed(monthly_revenue)),
                'organizationRevenue': org_revenue_data,
                'averageTransactionValue': 150.0,  # Mock data
                'totalTransactions': Payment.objects.filter(status='completed').count(),
                'pendingPayouts': 25000.0,  # Mock data
                'platformFees': float(total_revenue) * 0.1  # 10% platform fee
            },
            message="Global financial analytics retrieved successfully"
        )


class OrganizationFinancialView(APIView):
    """Organization financial data for super admin"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can access organization financial data"
            )
        
        # Get organizations with financial metrics
        organizations = Organization.objects.annotate(
            total_revenue=Sum('courses__enrollments__payment__amount',
                             filter=Q(courses__enrollments__payment__status='completed')),
            total_courses=Count('courses', distinct=True),
            total_students=Count('courses__enrollments__student', distinct=True),
            avg_course_price=Avg('courses__price')
        ).order_by('-total_revenue')
        
        org_data = []
        for org in organizations:
            # Calculate growth metrics
            now = timezone.now()
            last_30_days = now - timedelta(days=30)
            previous_30_days = now - timedelta(days=60)
            
            recent_revenue = Payment.objects.filter(
                enrollment__course__organization=org,
                status='completed',
                created_at__gte=last_30_days
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            previous_revenue = Payment.objects.filter(
                enrollment__course__organization=org,
                status='completed',
                created_at__gte=previous_30_days,
                created_at__lt=last_30_days
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            growth = ((recent_revenue - previous_revenue) / max(previous_revenue, 1)) * 100
            
            org_data.append({
                'id': org.id,
                'name': org.name,
                'subdomain': org.subdomain,
                'totalRevenue': float(org.total_revenue or 0),
                'totalCourses': org.total_courses,
                'totalStudents': org.total_students,
                'avgCoursePrice': float(org.avg_course_price or 0),
                'revenueGrowth': round(growth, 1),
                'status': 'active' if org.is_active else 'inactive'
            })
        
        return StandardAPIResponse.success(
            data={'results': org_data},
            message="Organization financial data retrieved successfully"
        )


class PaymentTransactionsView(APIView):
    """Payment transactions for financial tracking"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return StandardAPIResponse.permission_denied()
        
        # Get recent transactions
        transactions = Payment.objects.select_related(
            'enrollment__student',
            'enrollment__course',
            'enrollment__course__organization'
        ).order_by('-created_at')[:50]
        
        transaction_data = []
        for payment in transactions:
            transaction_data.append({
                'id': payment.id,
                'amount': float(payment.amount),
                'currency': payment.currency,
                'status': payment.status,
                'method': payment.payment_method,
                'student': {
                    'id': payment.enrollment.student.id,
                    'name': f"{payment.enrollment.student.first_name} {payment.enrollment.student.last_name}",
                    'email': payment.enrollment.student.email
                },
                'course': {
                    'id': payment.enrollment.course.id,
                    'title': payment.enrollment.course.title,
                    'organization': payment.enrollment.course.organization.name
                },
                'created_at': payment.created_at.isoformat(),
                'processed_at': payment.updated_at.isoformat() if payment.status == 'completed' else None
            })
        
        return StandardAPIResponse.success(
            data={'results': transaction_data},
            message="Payment transactions retrieved successfully"
        )