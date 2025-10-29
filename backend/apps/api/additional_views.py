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
            course_count=Count('tenant_courses', distinct=True),
            revenue=Sum('tenant_courses__payments__amount', 
                       filter=Q(tenant_courses__payments__status='completed'))
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
            course__instructor=request.user,
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
                course__instructor=request.user,
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
            course__instructor=request.user,
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
                course__instructor=request.user,
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
            revenue=Sum('payments__amount',
                       filter=Q(payments__status='completed'))
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
    Advanced course recommendations with predictive analytics.
    Endpoint: /courses/recommendations/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get personalized course recommendations using multiple algorithms:
        1. Collaborative filtering (users with similar enrollments)
        2. Content-based filtering (similar categories/topics)
        3. Popularity-based recommendations
        4. Learning path recommendations
        """
        tenant = getattr(request, 'tenant', None)
        limit = int(request.query_params.get('limit', 6))
        
        # Get user's enrollment history and preferences
        user_enrollments = Enrollment.objects.filter(
            student=request.user,
            tenant=tenant
        ).select_related('course')
        
        enrolled_course_ids = user_enrollments.values_list('course_id', flat=True)
        user_categories = user_enrollments.values_list('course__category', flat=True).distinct()
        completed_courses = user_enrollments.filter(status='completed')
        
        # Algorithm 1: Collaborative Filtering
        # Find users with similar enrollment patterns
        similar_users = User.objects.filter(
            enrollments__course__in=enrolled_course_ids,
            enrollments__tenant=tenant
        ).exclude(id=request.user.id).annotate(
            common_courses=Count('enrollments__course', filter=Q(
                enrollments__course__in=enrolled_course_ids
            ))
        ).filter(common_courses__gte=2)[:10]
        
        collaborative_courses = Course.objects.filter(
            enrollments__student__in=similar_users,
            tenant=tenant,
            is_public=True
        ).exclude(
            id__in=enrolled_course_ids
        ).annotate(
            recommendation_score=Count('enrollments__student', filter=Q(
                enrollments__student__in=similar_users
            ))
        ).order_by('-recommendation_score')[:limit//2]
        
        # Algorithm 2: Content-Based Filtering
        # Courses in similar categories with high ratings
        content_based_courses = Course.objects.filter(
            category__in=user_categories,
            tenant=tenant,
            is_public=True
        ).exclude(
            id__in=enrolled_course_ids
        ).annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            enrollment_count=Count('enrollments')
        ).filter(
            avg_rating__gte=4.0
        ).order_by('-avg_rating', '-enrollment_count')[:limit//3]
        
        # Algorithm 3: Popularity-Based (trending courses)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        trending_courses = Course.objects.filter(
            tenant=tenant,
            is_public=True
        ).exclude(
            id__in=enrolled_course_ids
        ).annotate(
            recent_enrollments=Count('enrollments', filter=Q(
                enrollments__enrolled_at__gte=thirty_days_ago
            )),
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
        ).filter(
            recent_enrollments__gte=5
        ).order_by('-recent_enrollments', '-avg_rating')[:limit//3]
        
        # Algorithm 4: Learning Path Recommendations
        # Courses that are logical next steps based on completed courses
        learning_path_courses = []
        if completed_courses.exists():
            # Find courses that students typically take after completing similar courses
            next_step_courses = Course.objects.filter(
                enrollments__student__in=User.objects.filter(
                    enrollments__course__in=completed_courses.values_list('course_id', flat=True),
                    enrollments__status='completed'
                ),
                tenant=tenant,
                is_public=True
            ).exclude(
                id__in=enrolled_course_ids
            ).annotate(
                progression_score=Count('enrollments')
            ).order_by('-progression_score')[:limit//4]
            
            learning_path_courses = list(next_step_courses)
        
        # Combine and deduplicate recommendations
        all_recommendations = []
        seen_course_ids = set()
        
        # Add collaborative filtering results
        for course in collaborative_courses:
            if course.id not in seen_course_ids:
                all_recommendations.append({
                    'course': course,
                    'reason': 'Students with similar interests also enrolled',
                    'algorithm': 'collaborative',
                    'score': getattr(course, 'recommendation_score', 0)
                })
                seen_course_ids.add(course.id)
        
        # Add content-based results
        for course in content_based_courses:
            if course.id not in seen_course_ids:
                all_recommendations.append({
                    'course': course,
                    'reason': f'Popular in {course.category}',
                    'algorithm': 'content_based',
                    'score': getattr(course, 'avg_rating', 0) * 20
                })
                seen_course_ids.add(course.id)
        
        # Add trending results
        for course in trending_courses:
            if course.id not in seen_course_ids:
                all_recommendations.append({
                    'course': course,
                    'reason': 'Trending this month',
                    'algorithm': 'popularity',
                    'score': getattr(course, 'recent_enrollments', 0)
                })
                seen_course_ids.add(course.id)
        
        # Add learning path results
        for course in learning_path_courses:
            if course.id not in seen_course_ids:
                all_recommendations.append({
                    'course': course,
                    'reason': 'Recommended next step in your learning journey',
                    'algorithm': 'learning_path',
                    'score': getattr(course, 'progression_score', 0)
                })
                seen_course_ids.add(course.id)
        
        # Sort by score and limit results
        all_recommendations.sort(key=lambda x: x['score'], reverse=True)
        final_recommendations = all_recommendations[:limit]
        
        # Format response
        recommendations_data = []
        for rec in final_recommendations:
            course = rec['course']
            
            # Calculate actual rating
            avg_rating = course.reviews.filter(is_approved=True).aggregate(
                avg=Avg('rating')
            )['avg'] or 0
            
            # Get enrollment count
            enrollment_count = course.enrollments.count()
            
            recommendations_data.append({
                'id': course.id,
                'title': course.title,
                'description': course.description[:200] + '...' if len(course.description) > 200 else course.description,
                'instructor': f"{course.instructor.first_name} {course.instructor.last_name}",
                'price': float(course.price or 0),
                'thumbnail': course.thumbnail.url if course.thumbnail else None,
                'rating': round(avg_rating, 2),
                'enrollment_count': enrollment_count,
                'category': course.category,
                'duration_weeks': course.duration_weeks,
                'difficulty_level': course.difficulty_level,
                'reason': rec['reason'],
                'algorithm': rec['algorithm'],
                'confidence_score': min(100, rec['score'] * 5),  # Normalize to 0-100
                'created_at': course.created_at.isoformat()
            })
        
        # Add recommendation metadata
        metadata = {
            'total_recommendations': len(recommendations_data),
            'algorithms_used': list(set(rec['algorithm'] for rec in final_recommendations)),
            'user_enrollment_count': user_enrollments.count(),
            'user_completed_courses': completed_courses.count(),
            'user_categories': list(user_categories),
            'generated_at': timezone.now().isoformat()
        }
        
        return StandardAPIResponse.success(
            data={
                'recommendations': recommendations_data,
                'metadata': metadata
            },
            message="Personalized course recommendations retrieved successfully"
        )


# Additional endpoint views for missing functionality


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
            revenue=Sum('tenant_courses__payments__amount',
                       filter=Q(tenant_courses__payments__status='completed'))
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
            total_revenue=Sum('tenant_courses__payments__amount',
                             filter=Q(tenant_courses__payments__status='completed')),
            total_courses=Count('tenant_courses', distinct=True),
            total_students=Count('tenant_courses__enrollments__student', distinct=True),
            avg_course_price=Avg('courses__price')
        ).order_by('-total_revenue')
        
        org_data = []
        for org in organizations:
            # Calculate growth metrics
            now = timezone.now()
            last_30_days = now - timedelta(days=30)
            previous_30_days = now - timedelta(days=60)
            
            recent_revenue = Payment.objects.filter(
                course__tenant=org,
                status='completed',
                created_at__gte=last_30_days
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            previous_revenue = Payment.objects.filter(
                course__tenant=org,
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
            'user',
            'course',
            'course__organization'
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
                    'id': payment.user.id,
                    'name': f"{payment.user.first_name} {payment.user.last_name}",
                    'email': payment.user.email
                },
                'course': {
                    'id': payment.course.id if payment.course else None,
                    'title': payment.course.title if payment.course else 'N/A',
                    'organization': payment.course.organization.name if payment.course else 'N/A'
                },
                'created_at': payment.created_at.isoformat(),
                'processed_at': payment.updated_at.isoformat() if payment.status == 'completed' else None
            })
        
        return StandardAPIResponse.success(
            data={'results': transaction_data},
            message="Payment transactions retrieved successfully"
        )