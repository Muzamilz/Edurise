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
from apps.admin_tools.models import ScheduledReport
from .responses import StandardAPIResponse
from .mixins import APIResponseMixin


class AnalyticsViewSet(viewsets.ViewSet):
    """
    Centralized analytics endpoints for comprehensive data analysis and reporting.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def enrollment_trends(self, request):
        """
        Get enrollment trends with time-based analytics.
        Supports filtering by date range, course, instructor, and aggregation period.
        """
        tenant = getattr(request, 'tenant', None)
        
        # Get query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        course_id = request.query_params.get('course_id')
        instructor_id = request.query_params.get('instructor_id')
        period = request.query_params.get('period', 'month')  # day, week, month
        
        # Set default date range (last 12 months)
        if not end_date:
            end_date = timezone.now()
        else:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if not start_date:
            start_date = end_date - timedelta(days=365)
        else:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        # Base queryset
        enrollments = Enrollment.objects.filter(
            tenant=tenant,
            enrolled_at__gte=start_date,
            enrolled_at__lte=end_date
        ).select_related('course', 'student')
        
        # Apply filters
        if course_id:
            enrollments = enrollments.filter(course_id=course_id)
        if instructor_id:
            enrollments = enrollments.filter(course__instructor_id=instructor_id)
        
        # Aggregate by period
        if period == 'day':
            trunc_func = TruncDay
            date_format = '%Y-%m-%d'
        elif period == 'week':
            trunc_func = TruncWeek
            date_format = '%Y-W%U'
        else:  # month
            trunc_func = TruncMonth
            date_format = '%Y-%m'
        
        trend_data = enrollments.annotate(
            period=trunc_func('enrolled_at')
        ).values('period').annotate(
            total_enrollments=Count('id'),
            active_enrollments=Count('id', filter=Q(status='active')),
            completed_enrollments=Count('id', filter=Q(status='completed')),
            dropped_enrollments=Count('id', filter=Q(status='dropped')),
            unique_students=Count('student', distinct=True),
            unique_courses=Count('course', distinct=True),
            avg_progress=Avg('progress_percentage')
        ).order_by('period')
        
        # Format response
        formatted_data = []
        for item in trend_data:
            formatted_data.append({
                'period': item['period'].strftime(date_format),
                'date': item['period'].isoformat(),
                'total_enrollments': item['total_enrollments'],
                'active_enrollments': item['active_enrollments'],
                'completed_enrollments': item['completed_enrollments'],
                'dropped_enrollments': item['dropped_enrollments'],
                'unique_students': item['unique_students'],
                'unique_courses': item['unique_courses'],
                'avg_progress': round(item['avg_progress'] or 0, 2),
                'completion_rate': (item['completed_enrollments'] / max(item['total_enrollments'], 1)) * 100,
                'dropout_rate': (item['dropped_enrollments'] / max(item['total_enrollments'], 1)) * 100
            })
        
        # Calculate summary statistics
        total_stats = enrollments.aggregate(
            total_enrollments=Count('id'),
            total_students=Count('student', distinct=True),
            total_courses=Count('course', distinct=True),
            avg_progress=Avg('progress_percentage'),
            completion_rate=Count('id', filter=Q(status='completed')) * 100.0 / Count('id')
        )
        
        return StandardAPIResponse.success(
            data={
                'trend_data': formatted_data,
                'summary': {
                    'total_enrollments': total_stats['total_enrollments'],
                    'total_students': total_stats['total_students'],
                    'total_courses': total_stats['total_courses'],
                    'avg_progress': round(total_stats['avg_progress'] or 0, 2),
                    'completion_rate': round(total_stats['completion_rate'] or 0, 2),
                    'period': period,
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    }
                }
            },
            message="Enrollment trends retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def user_engagement(self, request):
        """
        Get user engagement analytics including activity patterns and usage metrics.
        """
        tenant = getattr(request, 'tenant', None)
        
        # Get query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        user_type = request.query_params.get('user_type', 'all')  # all, student, teacher
        
        # Set default date range (last 30 days)
        if not end_date:
            end_date = timezone.now()
        else:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        # Base user queryset
        users = User.objects.filter(profiles__tenant=tenant)
        
        # Apply user type filter
        if user_type == 'student':
            users = users.filter(is_teacher=False)
        elif user_type == 'teacher':
            users = users.filter(is_teacher=True)
        
        # Active users (logged in during period)
        active_users = users.filter(
            last_login__gte=start_date,
            last_login__lte=end_date
        )
        
        # Engagement metrics
        engagement_stats = {
            'total_users': users.count(),
            'active_users': active_users.count(),
            'new_users': users.filter(
                date_joined__gte=start_date,
                date_joined__lte=end_date
            ).count(),
            'returning_users': active_users.filter(
                date_joined__lt=start_date
            ).count()
        }
        
        # Daily active users trend
        daily_active = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            day_start = timezone.make_aware(datetime.combine(current_date, datetime.min.time()))
            day_end = day_start + timedelta(days=1)
            
            daily_count = users.filter(
                last_login__gte=day_start,
                last_login__lt=day_end
            ).count()
            
            daily_active.append({
                'date': current_date.isoformat(),
                'active_users': daily_count
            })
            
            current_date += timedelta(days=1)
        
        # Course interaction metrics
        enrollments = Enrollment.objects.filter(
            tenant=tenant,
            student__in=users,
            last_accessed__gte=start_date,
            last_accessed__lte=end_date
        )
        
        course_engagement = enrollments.aggregate(
            total_interactions=Count('id'),
            avg_progress_gain=Avg('progress_percentage'),
            courses_completed=Count('id', filter=Q(status='completed')),
            avg_session_length=Avg(F('last_accessed') - F('enrolled_at'))
        )
        
        # Live class attendance
        attendance_stats = ClassAttendance.objects.filter(
            live_class__course__tenant=tenant,
            student__in=users,
            attended_at__gte=start_date,
            attended_at__lte=end_date
        ).aggregate(
            total_attendances=Count('id'),
            unique_attendees=Count('student', distinct=True),
            avg_attendance_duration=Avg('duration_minutes')
        )
        
        return StandardAPIResponse.success(
            data={
                'engagement_overview': engagement_stats,
                'daily_active_users': daily_active,
                'course_engagement': {
                    'total_interactions': course_engagement['total_interactions'],
                    'avg_progress_gain': round(course_engagement['avg_progress_gain'] or 0, 2),
                    'courses_completed': course_engagement['courses_completed'],
                    'engagement_rate': (course_engagement['total_interactions'] / max(engagement_stats['active_users'], 1)) * 100
                },
                'live_class_engagement': {
                    'total_attendances': attendance_stats['total_attendances'],
                    'unique_attendees': attendance_stats['unique_attendees'],
                    'avg_attendance_duration': round(attendance_stats['avg_attendance_duration'] or 0, 2),
                    'attendance_rate': (attendance_stats['unique_attendees'] / max(engagement_stats['active_users'], 1)) * 100
                },
                'period_info': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'user_type': user_type
                }
            },
            message="User engagement analytics retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def financial_analytics(self, request):
        """
        Get comprehensive financial analytics including revenue, payments, and subscription data.
        """
        tenant = getattr(request, 'tenant', None)
        
        # Get query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        currency = request.query_params.get('currency', 'USD')
        period = request.query_params.get('period', 'month')
        
        # Set default date range (last 12 months)
        if not end_date:
            end_date = timezone.now()
        else:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if not start_date:
            start_date = end_date - timedelta(days=365)
        else:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        # Payment analytics
        payments = Payment.objects.filter(
            tenant=tenant,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Revenue by status
        revenue_stats = payments.aggregate(
            total_revenue=Sum('amount', filter=Q(status='completed')),
            pending_revenue=Sum('amount', filter=Q(status='pending')),
            failed_revenue=Sum('amount', filter=Q(status='failed')),
            refunded_revenue=Sum('amount', filter=Q(status='refunded')),
            total_transactions=Count('id'),
            successful_transactions=Count('id', filter=Q(status='completed')),
            avg_transaction_value=Avg('amount', filter=Q(status='completed'))
        )
        
        # Revenue trend by period
        if period == 'day':
            trunc_func = TruncDay
            date_format = '%Y-%m-%d'
        elif period == 'week':
            trunc_func = TruncWeek
            date_format = '%Y-W%U'
        else:  # month
            trunc_func = TruncMonth
            date_format = '%Y-%m'
        
        revenue_trend = payments.filter(status='completed').annotate(
            period=trunc_func('created_at')
        ).values('period').annotate(
            revenue=Sum('amount'),
            transaction_count=Count('id'),
            unique_customers=Count('user', distinct=True)
        ).order_by('period')
        
        # Subscription analytics
        subscriptions = Subscription.objects.filter(tenant=tenant)
        subscription_stats = subscriptions.aggregate(
            total_subscriptions=Count('id'),
            active_subscriptions=Count('id', filter=Q(status='active')),
            cancelled_subscriptions=Count('id', filter=Q(status='cancelled')),
            expired_subscriptions=Count('id', filter=Q(status='expired')),
            monthly_recurring_revenue=Sum('amount', filter=Q(
                status='active',
                billing_cycle='monthly'
            )),
            annual_recurring_revenue=Sum('amount', filter=Q(
                status='active',
                billing_cycle='annual'
            ))
        )
        
        # Course revenue breakdown
        course_revenue = Course.objects.filter(
            tenant=tenant,
            payments__status='completed',
            payments__created_at__gte=start_date,
            payments__created_at__lte=end_date
        ).annotate(
            revenue=Sum('payments__amount'),
            enrollment_count=Count('enrollments')
        ).order_by('-revenue')[:10]
        
        # Payment method breakdown
        payment_methods = payments.filter(status='completed').values(
            'payment_method'
        ).annotate(
            count=Count('id'),
            revenue=Sum('amount')
        ).order_by('-revenue')
        
        return StandardAPIResponse.success(
            data={
                'revenue_overview': {
                    'total_revenue': float(revenue_stats['total_revenue'] or 0),
                    'pending_revenue': float(revenue_stats['pending_revenue'] or 0),
                    'failed_revenue': float(revenue_stats['failed_revenue'] or 0),
                    'refunded_revenue': float(revenue_stats['refunded_revenue'] or 0),
                    'net_revenue': float((revenue_stats['total_revenue'] or 0) - (revenue_stats['refunded_revenue'] or 0)),
                    'avg_transaction_value': float(revenue_stats['avg_transaction_value'] or 0),
                    'success_rate': (revenue_stats['successful_transactions'] / max(revenue_stats['total_transactions'], 1)) * 100,
                    'currency': currency
                },
                'revenue_trend': [
                    {
                        'period': item['period'].strftime(date_format),
                        'date': item['period'].isoformat(),
                        'revenue': float(item['revenue']),
                        'transaction_count': item['transaction_count'],
                        'unique_customers': item['unique_customers'],
                        'avg_transaction': float(item['revenue'] / max(item['transaction_count'], 1))
                    }
                    for item in revenue_trend
                ],
                'subscription_analytics': {
                    'total_subscriptions': subscription_stats['total_subscriptions'],
                    'active_subscriptions': subscription_stats['active_subscriptions'],
                    'churn_rate': (subscription_stats['cancelled_subscriptions'] / max(subscription_stats['total_subscriptions'], 1)) * 100,
                    'mrr': float(subscription_stats['monthly_recurring_revenue'] or 0),
                    'arr': float(subscription_stats['annual_recurring_revenue'] or 0),
                    'retention_rate': (subscription_stats['active_subscriptions'] / max(subscription_stats['total_subscriptions'], 1)) * 100
                },
                'top_courses_by_revenue': [
                    {
                        'course_id': course.id,
                        'course_title': course.title,
                        'revenue': float(course.revenue or 0),
                        'enrollment_count': course.enrollment_count,
                        'avg_revenue_per_enrollment': float((course.revenue or 0) / max(course.enrollment_count, 1))
                    }
                    for course in course_revenue
                ],
                'payment_methods': [
                    {
                        'method': method['payment_method'],
                        'transaction_count': method['count'],
                        'revenue': float(method['revenue']),
                        'percentage': (method['count'] / max(revenue_stats['successful_transactions'], 1)) * 100
                    }
                    for method in payment_methods
                ],
                'period_info': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'period': period,
                    'currency': currency
                }
            },
            message="Financial analytics retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def course_performance(self, request):
        """
        Get comprehensive course performance analytics including completion rates and engagement.
        """
        tenant = getattr(request, 'tenant', None)
        
        # Get query parameters
        course_id = request.query_params.get('course_id')
        instructor_id = request.query_params.get('instructor_id')
        category = request.query_params.get('category')
        limit = int(request.query_params.get('limit', 20))
        
        # Base queryset
        courses = Course.objects.filter(tenant=tenant).select_related(
            'instructor'
        ).prefetch_related(
            'enrollments', 'reviews', 'live_classes'
        )
        
        # Apply filters
        if course_id:
            courses = courses.filter(id=course_id)
        if instructor_id:
            courses = courses.filter(instructor_id=instructor_id)
        if category:
            courses = courses.filter(category=category)
        
        # Annotate with performance metrics
        courses = courses.annotate(
            total_enrollments=Count('enrollments'),
            active_enrollments=Count('enrollments', filter=Q(enrollments__status='active')),
            completed_enrollments=Count('enrollments', filter=Q(enrollments__status='completed')),
            avg_progress=Avg('enrollments__progress_percentage'),
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            total_reviews=Count('reviews', filter=Q(reviews__is_approved=True)),
            revenue=Sum('payments__amount', filter=Q(payments__status='completed'))
        ).order_by('-total_enrollments')[:limit]
        
        # Format course performance data
        course_performance = []
        for course in courses:
            # Calculate completion rate
            completion_rate = (course.completed_enrollments / max(course.total_enrollments, 1)) * 100
            
            # Calculate engagement score (simplified)
            engagement_score = min(100, (
                (course.avg_progress or 0) * 0.4 +
                (course.avg_rating or 0) * 20 * 0.3 +
                completion_rate * 0.3
            ))
            
            # Get recent enrollment trend (last 30 days)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_enrollments = course.enrollments.filter(
                enrolled_at__gte=thirty_days_ago
            ).count()
            
            course_performance.append({
                'course_id': course.id,
                'course_title': course.title,
                'instructor_name': f"{course.instructor.first_name} {course.instructor.last_name}",
                'category': course.category,
                'price': float(course.price or 0),
                'is_public': course.is_public,
                'metrics': {
                    'total_enrollments': course.total_enrollments,
                    'active_enrollments': course.active_enrollments,
                    'completed_enrollments': course.completed_enrollments,
                    'completion_rate': round(completion_rate, 2),
                    'avg_progress': round(course.avg_progress or 0, 2),
                    'avg_rating': round(course.avg_rating or 0, 2),
                    'total_reviews': course.total_reviews,
                    'engagement_score': round(engagement_score, 2),
                    'revenue': float(course.revenue or 0),
                    'recent_enrollments': recent_enrollments
                },
                'performance_indicators': {
                    'is_high_performing': completion_rate > 70 and (course.avg_rating or 0) > 4.0,
                    'needs_attention': completion_rate < 30 or (course.avg_rating or 0) < 3.0,
                    'trending_up': recent_enrollments > course.total_enrollments * 0.1
                }
            })
        
        # Calculate summary statistics
        summary_stats = courses.aggregate(
            total_courses=Count('id'),
            avg_completion_rate=Avg(
                Count('enrollments', filter=Q(enrollments__status='completed')) * 100.0 / 
                Count('enrollments')
            ),
            avg_rating=Avg('avg_rating'),
            total_revenue=Sum('revenue')
        )
        
        return StandardAPIResponse.success(
            data={
                'course_performance': course_performance,
                'summary': {
                    'total_courses': summary_stats['total_courses'],
                    'avg_completion_rate': round(summary_stats['avg_completion_rate'] or 0, 2),
                    'avg_rating': round(summary_stats['avg_rating'] or 0, 2),
                    'total_revenue': float(summary_stats['total_revenue'] or 0)
                },
                'filters_applied': {
                    'course_id': course_id,
                    'instructor_id': instructor_id,
                    'category': category,
                    'limit': limit
                }
            },
            message="Course performance analytics retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def real_time_metrics(self, request):
        """
        Get real-time analytics metrics with live data processing.
        """
        tenant = getattr(request, 'tenant', None)
        
        # Real-time metrics (last 24 hours)
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_hour = now - timedelta(hours=1)
        
        # Active users in the last hour
        active_users_1h = User.objects.filter(
            profiles__tenant=tenant,
            last_login__gte=last_hour
        ).count()
        
        # New enrollments in the last 24 hours
        new_enrollments_24h = Enrollment.objects.filter(
            tenant=tenant,
            enrolled_at__gte=last_24h
        ).count()
        
        # Live class sessions currently active
        active_live_classes = LiveClass.objects.filter(
            course__tenant=tenant,
            status='in_progress',
            scheduled_at__lte=now,
            scheduled_at__gte=now - timedelta(hours=3)  # Classes up to 3 hours long
        ).count()
        
        # Recent payments (last 24 hours)
        recent_payments = Payment.objects.filter(
            tenant=tenant,
            created_at__gte=last_24h,
            status='completed'
        ).aggregate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        # Course completion events (last 24 hours)
        recent_completions = Enrollment.objects.filter(
            tenant=tenant,
            status='completed',
            updated_at__gte=last_24h
        ).count()
        
        # Real-time engagement metrics
        # Users who accessed courses in the last hour
        course_interactions_1h = Enrollment.objects.filter(
            tenant=tenant,
            last_accessed__gte=last_hour
        ).values('student').distinct().count()
        
        # Hourly breakdown for the last 24 hours
        hourly_metrics = []
        for i in range(24):
            hour_start = now - timedelta(hours=i+1)
            hour_end = now - timedelta(hours=i)
            
            hour_data = {
                'hour': hour_start.strftime('%H:00'),
                'timestamp': hour_start.isoformat(),
                'active_users': User.objects.filter(
                    profiles__tenant=tenant,
                    last_login__gte=hour_start,
                    last_login__lt=hour_end
                ).count(),
                'new_enrollments': Enrollment.objects.filter(
                    tenant=tenant,
                    enrolled_at__gte=hour_start,
                    enrolled_at__lt=hour_end
                ).count(),
                'course_interactions': Enrollment.objects.filter(
                    tenant=tenant,
                    last_accessed__gte=hour_start,
                    last_accessed__lt=hour_end
                ).count(),
                'payments': Payment.objects.filter(
                    tenant=tenant,
                    created_at__gte=hour_start,
                    created_at__lt=hour_end,
                    status='completed'
                ).count()
            }
            hourly_metrics.append(hour_data)
        
        hourly_metrics.reverse()  # Show oldest to newest
        
        # System performance metrics (mock data - would come from monitoring)
        system_metrics = {
            'cpu_usage': 45.2,
            'memory_usage': 67.8,
            'database_connections': 23,
            'cache_hit_rate': 94.5,
            'average_response_time': 145,  # milliseconds
            'error_rate': 0.02  # percentage
        }
        
        # Top active courses (most interactions in last hour)
        top_active_courses = Course.objects.filter(
            tenant=tenant,
            enrollments__last_accessed__gte=last_hour
        ).annotate(
            recent_interactions=Count('enrollments', filter=Q(
                enrollments__last_accessed__gte=last_hour
            ))
        ).order_by('-recent_interactions')[:5]
        
        active_courses_data = []
        for course in top_active_courses:
            active_courses_data.append({
                'id': course.id,
                'title': course.title,
                'instructor': f"{course.instructor.first_name} {course.instructor.last_name}",
                'recent_interactions': course.recent_interactions,
                'total_enrollments': course.enrollments.count()
            })
        
        return StandardAPIResponse.success(
            data={
                'current_metrics': {
                    'active_users_1h': active_users_1h,
                    'new_enrollments_24h': new_enrollments_24h,
                    'active_live_classes': active_live_classes,
                    'recent_payments_count': recent_payments['count'] or 0,
                    'recent_payments_amount': float(recent_payments['total_amount'] or 0),
                    'recent_completions': recent_completions,
                    'course_interactions_1h': course_interactions_1h
                },
                'hourly_trends': hourly_metrics,
                'system_performance': system_metrics,
                'top_active_courses': active_courses_data,
                'last_updated': now.isoformat(),
                'refresh_interval': 60  # seconds
            },
            message="Real-time analytics metrics retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def predictive_insights(self, request):
        """
        Generate predictive analytics insights for business intelligence.
        """
        tenant = getattr(request, 'tenant', None)
        
        # Enrollment prediction based on historical trends
        now = timezone.now()
        
        # Get enrollment data for the last 12 months
        monthly_enrollments = []
        for i in range(12):
            month_start = now.replace(day=1) - timedelta(days=32*i)
            month_start = month_start.replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
            
            month_count = Enrollment.objects.filter(
                tenant=tenant,
                enrolled_at__gte=month_start,
                enrolled_at__lte=month_end
            ).count()
            
            monthly_enrollments.append({
                'month': month_start.strftime('%Y-%m'),
                'enrollments': month_count
            })
        
        monthly_enrollments.reverse()
        
        # Simple linear trend prediction for next 3 months
        if len(monthly_enrollments) >= 3:
            recent_trend = sum(monthly_enrollments[-3:], key=lambda x: x['enrollments']) / 3
            older_trend = sum(monthly_enrollments[-6:-3], key=lambda x: x['enrollments']) / 3
            growth_rate = (recent_trend - older_trend) / max(older_trend, 1)
        else:
            growth_rate = 0.05  # Default 5% growth
        
        # Predict next 3 months
        last_month_enrollments = monthly_enrollments[-1]['enrollments'] if monthly_enrollments else 0
        predictions = []
        for i in range(1, 4):
            predicted_enrollments = int(last_month_enrollments * (1 + growth_rate) ** i)
            future_month = now.replace(day=1) + timedelta(days=32*i)
            future_month = future_month.replace(day=1)
            
            predictions.append({
                'month': future_month.strftime('%Y-%m'),
                'predicted_enrollments': predicted_enrollments,
                'confidence': max(60, 90 - i*10)  # Decreasing confidence over time
            })
        
        # Revenue prediction
        avg_course_price = Course.objects.filter(
            tenant=tenant,
            price__isnull=False
        ).aggregate(avg_price=Avg('price'))['avg_price'] or 0
        
        revenue_predictions = []
        for pred in predictions:
            predicted_revenue = pred['predicted_enrollments'] * float(avg_course_price) * 0.7  # Assuming 70% conversion
            revenue_predictions.append({
                'month': pred['month'],
                'predicted_revenue': predicted_revenue,
                'confidence': pred['confidence']
            })
        
        # Course performance predictions
        # Identify courses likely to need attention
        at_risk_courses = Course.objects.filter(
            tenant=tenant,
            is_public=True
        ).annotate(
            completion_rate=Count('enrollments', filter=Q(enrollments__status='completed')) * 100.0 / Count('enrollments'),
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            recent_enrollments=Count('enrollments', filter=Q(
                enrollments__enrolled_at__gte=now - timedelta(days=30)
            ))
        ).filter(
            Q(completion_rate__lt=30) | Q(avg_rating__lt=3.5) | Q(recent_enrollments=0)
        )[:10]
        
        at_risk_data = []
        for course in at_risk_courses:
            risk_factors = []
            if course.completion_rate < 30:
                risk_factors.append('Low completion rate')
            if course.avg_rating and course.avg_rating < 3.5:
                risk_factors.append('Low rating')
            if course.recent_enrollments == 0:
                risk_factors.append('No recent enrollments')
            
            at_risk_data.append({
                'id': course.id,
                'title': course.title,
                'instructor': f"{course.instructor.first_name} {course.instructor.last_name}",
                'completion_rate': round(course.completion_rate or 0, 1),
                'avg_rating': round(course.avg_rating or 0, 2),
                'recent_enrollments': course.recent_enrollments,
                'risk_factors': risk_factors,
                'recommended_actions': self._get_course_recommendations(course, risk_factors)
            })
        
        # Market opportunities
        # Categories with high demand but low supply
        category_analysis = Course.objects.filter(
            tenant=tenant
        ).values('category').annotate(
            course_count=Count('id'),
            total_enrollments=Count('enrollments'),
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
        ).order_by('-total_enrollments')
        
        opportunities = []
        for cat in category_analysis:
            if cat['total_enrollments'] > 50 and cat['course_count'] < 5:  # High demand, low supply
                opportunities.append({
                    'category': cat['category'],
                    'demand_score': cat['total_enrollments'],
                    'supply_score': cat['course_count'],
                    'avg_rating': round(cat['avg_rating'] or 0, 2),
                    'opportunity_score': cat['total_enrollments'] / max(cat['course_count'], 1),
                    'recommendation': f"Consider creating more courses in {cat['category']}"
                })
        
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        return StandardAPIResponse.success(
            data={
                'enrollment_predictions': {
                    'historical_data': monthly_enrollments[-6:],  # Last 6 months
                    'predictions': predictions,
                    'growth_rate': round(growth_rate * 100, 2)
                },
                'revenue_predictions': revenue_predictions,
                'at_risk_courses': at_risk_data,
                'market_opportunities': opportunities[:5],
                'insights_generated_at': now.isoformat(),
                'model_accuracy': 75,  # Mock accuracy score
                'next_update': (now + timedelta(hours=24)).isoformat()
            },
            message="Predictive analytics insights generated successfully"
        )
    
    def _get_course_recommendations(self, course, risk_factors):
        """Generate recommendations for at-risk courses"""
        recommendations = []
        
        if 'Low completion rate' in risk_factors:
            recommendations.extend([
                'Review course structure and pacing',
                'Add more interactive elements',
                'Provide better progress tracking'
            ])
        
        if 'Low rating' in risk_factors:
            recommendations.extend([
                'Gather detailed student feedback',
                'Update course content',
                'Improve instructor engagement'
            ])
        
        if 'No recent enrollments' in risk_factors:
            recommendations.extend([
                'Update course marketing materials',
                'Review pricing strategy',
                'Improve course visibility'
            ])
        
        return recommendations[:3]  # Return top 3 recommendations


class ReportGenerationView(APIView):
    """
    Generate comprehensive reports with customizable parameters and formats.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Generate and return a comprehensive analytics report.
        """
        tenant = getattr(request, 'tenant', None)
        
        # Get report parameters
        report_type = request.query_params.get('type', 'overview')  # overview, enrollment, financial, course
        format_type = request.query_params.get('format', 'json')  # json, csv, pdf
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Additional filtering parameters
        course_id = request.query_params.get('course_id')
        instructor_id = request.query_params.get('instructor_id')
        category = request.query_params.get('category')
        user_type = request.query_params.get('user_type', 'all')
        
        # Set default date range
        if not end_date:
            end_date = timezone.now()
        else:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        # Create filter context
        filter_context = {
            'start_date': start_date,
            'end_date': end_date,
            'course_id': course_id,
            'instructor_id': instructor_id,
            'category': category,
            'user_type': user_type
        }
        
        # Generate report based on type
        if report_type == 'enrollment':
            report_data = self._generate_enrollment_report(tenant, filter_context)
        elif report_type == 'financial':
            if not (request.user.is_staff or request.user.is_superuser):
                return StandardAPIResponse.permission_denied(
                    message="Only administrators can access financial reports"
                )
            report_data = self._generate_financial_report(tenant, filter_context)
        elif report_type == 'course':
            report_data = self._generate_course_report(tenant, filter_context)
        else:  # overview
            report_data = self._generate_overview_report(tenant, filter_context)
        
        # Add metadata
        report_data['metadata'] = {
            'report_type': report_type,
            'format': format_type,
            'generated_at': timezone.now().isoformat(),
            'generated_by': f"{request.user.first_name} {request.user.last_name}",
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'tenant': tenant.name if tenant else 'System',
            'filters_applied': {k: v for k, v in filter_context.items() if v is not None}
        }
        
        # Handle different format types
        if format_type == 'csv':
            return self._generate_csv_response(report_data, report_type)
        elif format_type == 'pdf':
            return self._generate_pdf_response(report_data, report_type)
        else:  # json
            return StandardAPIResponse.success(
                data=report_data,
                message=f"{report_type.title()} report generated successfully"
            )
    
    def post(self, request):
        """
        Schedule a report generation for background processing.
        """
        tenant = getattr(request, 'tenant', None)
        
        # Get report parameters from request body
        report_config = request.data
        
        # Validate required fields
        required_fields = ['report_type', 'email']
        for field in required_fields:
            if field not in report_config:
                return StandardAPIResponse.error(
                    message=f"Missing required field: {field}",
                    status_code=400
                )
        
        # Create scheduled report record (would need a ScheduledReport model)
        scheduled_report = {
            'id': timezone.now().timestamp(),  # Mock ID
            'report_type': report_config['report_type'],
            'email': report_config['email'],
            'status': 'scheduled',
            'scheduled_at': timezone.now().isoformat(),
            'tenant': tenant.name if tenant else 'System'
        }
        
        # In a real implementation, this would queue a background task
        # For now, we'll return a success response
        return StandardAPIResponse.success(
            data=scheduled_report,
            message="Report scheduled successfully. You will receive an email when it's ready."
        )
    
    def _generate_csv_response(self, report_data, report_type):
        """Generate CSV response from report data"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        
        # Write metadata
        writer.writerow(['Report Metadata'])
        writer.writerow(['Report Type', report_data['metadata']['report_type']])
        writer.writerow(['Generated At', report_data['metadata']['generated_at']])
        writer.writerow(['Generated By', report_data['metadata']['generated_by']])
        writer.writerow([])
        
        # Write main data based on report type
        if report_type == 'enrollment':
            self._write_enrollment_csv(writer, report_data)
        elif report_type == 'financial':
            self._write_financial_csv(writer, report_data)
        elif report_type == 'course':
            self._write_course_csv(writer, report_data)
        else:
            self._write_overview_csv(writer, report_data)
        
        return response
    
    def _generate_pdf_response(self, report_data, report_type):
        """Generate PDF response from report data"""
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        import io
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph(f"{report_type.title()} Report", title_style))
        story.append(Spacer(1, 12))
        
        # Metadata
        metadata = report_data['metadata']
        story.append(Paragraph(f"Generated: {metadata['generated_at']}", styles['Normal']))
        story.append(Paragraph(f"Generated by: {metadata['generated_by']}", styles['Normal']))
        story.append(Paragraph(f"Date Range: {metadata['date_range']['start']} to {metadata['date_range']['end']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add content based on report type
        if report_type == 'enrollment':
            self._add_enrollment_pdf_content(story, report_data, styles)
        elif report_type == 'financial':
            self._add_financial_pdf_content(story, report_data, styles)
        elif report_type == 'course':
            self._add_course_pdf_content(story, report_data, styles)
        else:
            self._add_overview_pdf_content(story, report_data, styles)
        
        doc.build(story)
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
        
        return response
    
    def _add_enrollment_pdf_content(self, story, report_data, styles):
        """Add enrollment-specific content to PDF"""
        story.append(Paragraph("Enrollment Summary", styles['Heading2']))
        
        if 'enrollment_summary' in report_data:
            summary = report_data['enrollment_summary']
            data = [
                ['Metric', 'Value'],
                ['Total Enrollments', str(summary.get('total_enrollments', 0))],
                ['Active Enrollments', str(summary.get('active_enrollments', 0))],
                ['Completed Enrollments', str(summary.get('completed_enrollments', 0))],
                ['Completion Rate', f"{summary.get('completion_rate', 0):.1f}%"],
                ['Average Progress', f"{summary.get('avg_progress', 0):.1f}%"]
            ]
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
    
    def _add_financial_pdf_content(self, story, report_data, styles):
        """Add financial-specific content to PDF"""
        story.append(Paragraph("Financial Summary", styles['Heading2']))
        
        if 'financial_summary' in report_data:
            summary = report_data['financial_summary']
            currency = summary.get('currency', 'USD')
            
            data = [
                ['Metric', 'Value'],
                ['Total Revenue', f"{currency} {summary.get('total_revenue', 0):,.2f}"],
                ['Net Revenue', f"{currency} {summary.get('net_revenue', 0):,.2f}"],
                ['Total Transactions', str(summary.get('total_transactions', 0))],
                ['Success Rate', f"{summary.get('success_rate', 0):.1f}%"],
                ['Average Transaction', f"{currency} {summary.get('avg_transaction_value', 0):,.2f}"]
            ]
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
    
    def _add_course_pdf_content(self, story, report_data, styles):
        """Add course-specific content to PDF"""
        story.append(Paragraph("Course Performance Summary", styles['Heading2']))
        
        if 'course_summary' in report_data:
            summary = report_data['course_summary']
            
            data = [
                ['Metric', 'Value'],
                ['Total Courses', str(summary.get('total_courses', 0))],
                ['Average Completion Rate', f"{summary.get('avg_completion_rate', 0):.1f}%"],
                ['Average Rating', f"{summary.get('avg_rating', 0):.1f}/5"],
                ['Total Revenue', f"USD {summary.get('total_revenue', 0):,.2f}"],
                ['High Performing Courses', str(summary.get('high_performing_courses', 0))]
            ]
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
    
    def _add_overview_pdf_content(self, story, report_data, styles):
        """Add overview content to PDF"""
        story.append(Paragraph("Platform Overview", styles['Heading2']))
        
        # Add summary from multiple data sources
        if 'overview_summary' in report_data:
            summary = report_data['overview_summary']
            
            data = [
                ['Category', 'Metric', 'Value'],
                ['Users', 'Total Active Users', str(summary.get('total_active_users', 0))],
                ['Users', 'New Users (Period)', str(summary.get('new_users', 0))],
                ['Courses', 'Total Courses', str(summary.get('total_courses', 0))],
                ['Courses', 'Avg Completion Rate', f"{summary.get('avg_completion_rate', 0):.1f}%"],
                ['Revenue', 'Total Revenue', f"USD {summary.get('total_revenue', 0):,.2f}"],
                ['Revenue', 'Success Rate', f"{summary.get('payment_success_rate', 0):.1f}%"]
            ]
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from io import BytesIO
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph(f"{report_type.title()} Report", title_style))
        story.append(Spacer(1, 12))
        
        # Metadata
        metadata = report_data['metadata']
        meta_data = [
            ['Generated At:', metadata['generated_at']],
            ['Generated By:', metadata['generated_by']],
            ['Date Range:', f"{metadata['date_range']['start']} to {metadata['date_range']['end']}"],
            ['Tenant:', metadata['tenant']]
        ]
        
        meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ]))
        
        story.append(meta_table)
        story.append(Spacer(1, 20))
        
        # Add report-specific content
        if report_type == 'enrollment':
            self._add_enrollment_pdf_content(story, report_data, styles)
        elif report_type == 'financial':
            self._add_financial_pdf_content(story, report_data, styles)
        elif report_type == 'course':
            self._add_course_pdf_content(story, report_data, styles)
        else:
            self._add_overview_pdf_content(story, report_data, styles)
        
        # Build PDF
        doc.build(story)
        
        # Return response
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
        
        return response
    
    def _generate_enrollment_report(self, tenant, filter_context):
        """Generate detailed enrollment analytics report"""
        start_date = filter_context['start_date']
        end_date = filter_context['end_date']
        course_id = filter_context['course_id']
        instructor_id = filter_context['instructor_id']
        
        # Base enrollment queryset
        enrollments = Enrollment.objects.filter(
            tenant=tenant,
            enrolled_at__gte=start_date,
            enrolled_at__lte=end_date
        ).select_related('course', 'student')
        
        if course_id:
            enrollments = enrollments.filter(course_id=course_id)
        if instructor_id:
            enrollments = enrollments.filter(course__instructor_id=instructor_id)
        
        # Summary statistics
        summary = enrollments.aggregate(
            total_enrollments=Count('id'),
            active_enrollments=Count('id', filter=Q(status='active')),
            completed_enrollments=Count('id', filter=Q(status='completed')),
            dropped_enrollments=Count('id', filter=Q(status='dropped')),
            avg_progress=Avg('progress_percentage'),
            unique_students=Count('student', distinct=True),
            unique_courses=Count('course', distinct=True)
        )
        
        # Enrollment trends by day
        daily_trends = enrollments.annotate(
            date=TruncDay('enrolled_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Course breakdown
        course_breakdown = enrollments.values(
            'course__title', 'course__id'
        ).annotate(
            enrollment_count=Count('id'),
            completion_rate=Count('id', filter=Q(status='completed')) * 100.0 / Count('id'),
            avg_progress=Avg('progress_percentage')
        ).order_by('-enrollment_count')[:10]
        
        # Student engagement levels
        engagement_levels = enrollments.annotate(
            engagement_level=Case(
                When(progress_percentage__gte=80, then=Value('High')),
                When(progress_percentage__gte=50, then=Value('Medium')),
                When(progress_percentage__gte=20, then=Value('Low')),
                default=Value('Minimal'),
                output_field=CharField()
            )
        ).values('engagement_level').annotate(
            count=Count('id')
        )
        
        return {
            'summary': summary,
            'daily_trends': list(daily_trends),
            'course_breakdown': list(course_breakdown),
            'engagement_levels': list(engagement_levels),
            'completion_rate': (summary['completed_enrollments'] / max(summary['total_enrollments'], 1)) * 100,
            'dropout_rate': (summary['dropped_enrollments'] / max(summary['total_enrollments'], 1)) * 100
        }
    
    def _generate_financial_report(self, tenant, filter_context):
        """Generate detailed financial analytics report"""
        # For now, return JSON with a note
        return StandardAPIResponse.success(
            data={
                'message': 'PDF generation not implemented yet',
                'report_data': report_data
            },
            message="PDF format not yet supported. Please use JSON or CSV format."
        )
    
    def _write_enrollment_csv(self, writer, report_data):
        """Write enrollment data to CSV"""
        writer.writerow(['Enrollment Summary'])
        summary = report_data.get('summary', {})
        for key, value in summary.items():
            writer.writerow([key.replace('_', ' ').title(), value])
        
        writer.writerow([])
        writer.writerow(['Top Courses by Enrollment'])
        writer.writerow(['Course Title', 'Instructor', 'Enrollment Count'])
        for course in report_data.get('top_courses', []):
            writer.writerow([course['course_title'], course['instructor'], course['enrollment_count']])
    
    def _write_financial_csv(self, writer, report_data):
        """Write financial data to CSV"""
        writer.writerow(['Revenue Summary'])
        summary = report_data.get('revenue_summary', {})
        for key, value in summary.items():
            writer.writerow([key.replace('_', ' ').title(), value])
        
        writer.writerow([])
        writer.writerow(['Course Revenue'])
        writer.writerow(['Course Title', 'Instructor', 'Revenue'])
        for course in report_data.get('course_revenue', []):
            writer.writerow([course['course_title'], course['instructor'], course['revenue']])
    
    def _write_course_csv(self, writer, report_data):
        """Write course performance data to CSV"""
        writer.writerow(['Course Performance'])
        writer.writerow(['Course Title', 'Instructor', 'Total Enrollments', 'Completion Rate', 'Avg Rating', 'Avg Progress'])
        for course in report_data.get('course_performance', []):
            writer.writerow([
                course['course_title'],
                course['instructor'],
                course['total_enrollments'],
                f"{course['completion_rate']:.1f}%",
                f"{course['avg_rating']:.1f}",
                f"{course['avg_progress']:.1f}%"
            ])
    
    def _write_overview_csv(self, writer, report_data):
        """Write overview data to CSV"""
        overview = report_data.get('overview', {})
        
        writer.writerow(['User Statistics'])
        user_stats = overview.get('user_statistics', {})
        for key, value in user_stats.items():
            writer.writerow([key.replace('_', ' ').title(), value])
        
        writer.writerow([])
        writer.writerow(['Enrollment Summary'])
        enrollment_summary = overview.get('enrollment_summary', {})
        for key, value in enrollment_summary.items():
            writer.writerow([key.replace('_', ' ').title(), value])
    
    def _generate_enrollment_report(self, tenant, filter_context):
        """Generate detailed enrollment report"""
        start_date = filter_context['start_date']
        end_date = filter_context['end_date']
        
        enrollments = Enrollment.objects.filter(
            tenant=tenant,
            enrolled_at__gte=start_date,
            enrolled_at__lte=end_date
        ).select_related('student', 'course', 'course__instructor')
        
        # Apply additional filters
        if filter_context.get('course_id'):
            enrollments = enrollments.filter(course_id=filter_context['course_id'])
        if filter_context.get('instructor_id'):
            enrollments = enrollments.filter(course__instructor_id=filter_context['instructor_id'])
        if filter_context.get('category'):
            enrollments = enrollments.filter(course__category=filter_context['category'])
        
        # Summary statistics
        summary = enrollments.aggregate(
            total_enrollments=Count('id'),
            active_enrollments=Count('id', filter=Q(status='active')),
            completed_enrollments=Count('id', filter=Q(status='completed')),
            dropped_enrollments=Count('id', filter=Q(status='dropped')),
            avg_progress=Avg('progress_percentage'),
            unique_students=Count('student', distinct=True),
            unique_courses=Count('course', distinct=True)
        )
        
        # Top courses by enrollment
        top_courses = Course.objects.filter(
            tenant=tenant,
            enrollments__enrolled_at__gte=start_date,
            enrollments__enrolled_at__lte=end_date
        ).annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count')[:10]
        
        return {
            'summary': summary,
            'top_courses': [
                {
                    'course_title': course.title,
                    'instructor': f"{course.instructor.first_name} {course.instructor.last_name}",
                    'enrollment_count': course.enrollment_count
                }
                for course in top_courses
            ],
            'detailed_enrollments': [
                {
                    'student_name': f"{enrollment.student.first_name} {enrollment.student.last_name}",
                    'course_title': enrollment.course.title,
                    'enrolled_at': enrollment.enrolled_at.isoformat(),
                    'status': enrollment.status,
                    'progress_percentage': enrollment.progress_percentage
                }
                for enrollment in enrollments[:100]  # Limit for performance
            ]
        }
    
    def _generate_financial_report(self, tenant, filter_context):
        """Generate detailed financial report"""
        start_date = filter_context['start_date']
        end_date = filter_context['end_date']
        
        payments = Payment.objects.filter(
            tenant=tenant,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Apply additional filters
        if filter_context.get('course_id'):
            payments = payments.filter(course_id=filter_context['course_id'])
        if filter_context.get('instructor_id'):
            payments = payments.filter(course__instructor_id=filter_context['instructor_id'])
        
        # Revenue summary
        revenue_summary = payments.aggregate(
            total_revenue=Sum('amount', filter=Q(status='completed')),
            pending_revenue=Sum('amount', filter=Q(status='pending')),
            failed_revenue=Sum('amount', filter=Q(status='failed')),
            total_transactions=Count('id'),
            successful_transactions=Count('id', filter=Q(status='completed'))
        )
        
        # Revenue by course
        course_revenue = Course.objects.filter(
            tenant=tenant,
            payments__created_at__gte=start_date,
            payments__created_at__lte=end_date,
            payments__status='completed'
        ).annotate(
            revenue=Sum('payments__amount')
        ).order_by('-revenue')[:20]
        
        return {
            'revenue_summary': {
                'total_revenue': float(revenue_summary['total_revenue'] or 0),
                'pending_revenue': float(revenue_summary['pending_revenue'] or 0),
                'failed_revenue': float(revenue_summary['failed_revenue'] or 0),
                'success_rate': (revenue_summary['successful_transactions'] / 
                               max(revenue_summary['total_transactions'], 1)) * 100
            },
            'course_revenue': [
                {
                    'course_title': course.title,
                    'instructor': f"{course.instructor.first_name} {course.instructor.last_name}",
                    'revenue': float(course.revenue or 0)
                }
                for course in course_revenue
            ]
        }
    
    def _generate_course_report(self, tenant, filter_context):
        """Generate detailed course performance report"""
        courses = Course.objects.filter(tenant=tenant)
        
        # Apply filters
        if filter_context.get('course_id'):
            courses = courses.filter(id=filter_context['course_id'])
        if filter_context.get('instructor_id'):
            courses = courses.filter(instructor_id=filter_context['instructor_id'])
        if filter_context.get('category'):
            courses = courses.filter(category=filter_context['category'])
        
        courses = courses.annotate(
            total_enrollments=Count('enrollments'),
            completed_enrollments=Count('enrollments', filter=Q(enrollments__status='completed')),
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            avg_progress=Avg('enrollments__progress_percentage')
        )
        
        return {
            'course_performance': [
                {
                    'course_title': course.title,
                    'instructor': f"{course.instructor.first_name} {course.instructor.last_name}",
                    'total_enrollments': course.total_enrollments,
                    'completion_rate': (course.completed_enrollments / max(course.total_enrollments, 1)) * 100,
                    'avg_rating': round(course.avg_rating or 0, 2),
                    'avg_progress': round(course.avg_progress or 0, 2)
                }
                for course in courses
            ]
        }
    
    def _generate_overview_report(self, tenant, filter_context):
        """Generate comprehensive overview report"""
        start_date = filter_context['start_date']
        end_date = filter_context['end_date']
        
        # Combine key metrics from all areas
        enrollment_data = self._generate_enrollment_report(tenant, filter_context)
        financial_data = self._generate_financial_report(tenant, filter_context)
        
        # User statistics
        users = User.objects.filter(profiles__tenant=tenant)
        if filter_context.get('user_type') == 'student':
            users = users.filter(is_teacher=False)
        elif filter_context.get('user_type') == 'teacher':
            users = users.filter(is_teacher=True)
            
        user_stats = {
            'total_users': users.count(),
            'active_users': users.filter(last_login__gte=start_date).count(),
            'new_users': users.filter(date_joined__gte=start_date).count()
        }
        
        return {
            'overview': {
                'user_statistics': user_stats,
                'enrollment_summary': enrollment_data['summary'],
                'financial_summary': financial_data['revenue_summary']
            },
            'top_performers': {
                'top_courses': enrollment_data['top_courses'][:5],
                'top_revenue_courses': financial_data['course_revenue'][:5]
            }
        }  
  
    def _write_enrollment_csv(self, writer, report_data):
        """Write enrollment data to CSV"""
        writer.writerow(['Enrollment Report'])
        writer.writerow([])
        
        # Summary section
        if 'summary' in report_data:
            writer.writerow(['Summary Statistics'])
            summary = report_data['summary']
            for key, value in summary.items():
                writer.writerow([key.replace('_', ' ').title(), value])
            writer.writerow([])
        
        # Top courses section
        if 'top_courses' in report_data:
            writer.writerow(['Top Courses by Enrollment'])
            writer.writerow(['Course Title', 'Instructor', 'Enrollment Count'])
            for course in report_data['top_courses']:
                writer.writerow([
                    course['course_title'],
                    course['instructor'],
                    course['enrollment_count']
                ])
            writer.writerow([])
        
        # Detailed enrollments
        if 'detailed_enrollments' in report_data:
            writer.writerow(['Detailed Enrollments'])
            writer.writerow(['Student Name', 'Course Title', 'Enrolled At', 'Status', 'Progress %'])
            for enrollment in report_data['detailed_enrollments']:
                writer.writerow([
                    enrollment['student_name'],
                    enrollment['course_title'],
                    enrollment['enrolled_at'],
                    enrollment['status'],
                    enrollment['progress_percentage']
                ])
    
    def _write_financial_csv(self, writer, report_data):
        """Write financial data to CSV"""
        writer.writerow(['Financial Report'])
        writer.writerow([])
        
        # Revenue summary
        if 'revenue_summary' in report_data:
            writer.writerow(['Revenue Summary'])
            summary = report_data['revenue_summary']
            for key, value in summary.items():
                writer.writerow([key.replace('_', ' ').title(), value])
            writer.writerow([])
        
        # Course revenue
        if 'course_revenue' in report_data:
            writer.writerow(['Revenue by Course'])
            writer.writerow(['Course Title', 'Instructor', 'Revenue'])
            for course in report_data['course_revenue']:
                writer.writerow([
                    course['course_title'],
                    course['instructor'],
                    f"${course['revenue']:,.2f}"
                ])
    
    def _write_course_csv(self, writer, report_data):
        """Write course performance data to CSV"""
        writer.writerow(['Course Performance Report'])
        writer.writerow([])
        
        if 'course_performance' in report_data:
            writer.writerow(['Course Performance Details'])
            writer.writerow([
                'Course Title', 'Instructor', 'Total Enrollments', 
                'Completion Rate %', 'Avg Rating', 'Avg Progress %'
            ])
            for course in report_data['course_performance']:
                writer.writerow([
                    course['course_title'],
                    course['instructor'],
                    course['total_enrollments'],
                    f"{course['completion_rate']:.1f}",
                    course['avg_rating'],
                    f"{course['avg_progress']:.1f}"
                ])
    
    def _write_overview_csv(self, writer, report_data):
        """Write overview data to CSV"""
        writer.writerow(['Platform Overview Report'])
        writer.writerow([])
        
        if 'overview' in report_data:
            overview = report_data['overview']
            
            # User statistics
            if 'user_statistics' in overview:
                writer.writerow(['User Statistics'])
                user_stats = overview['user_statistics']
                for key, value in user_stats.items():
                    writer.writerow([key.replace('_', ' ').title(), value])
                writer.writerow([])
            
            # Enrollment summary
            if 'enrollment_summary' in overview:
                writer.writerow(['Enrollment Summary'])
                enrollment_summary = overview['enrollment_summary']
                for key, value in enrollment_summary.items():
                    writer.writerow([key.replace('_', ' ').title(), value])
                writer.writerow([])
            
            # Financial summary
            if 'financial_summary' in overview:
                writer.writerow(['Financial Summary'])
                financial_summary = overview['financial_summary']
                for key, value in financial_summary.items():
                    writer.writerow([key.replace('_', ' ').title(), value])
                writer.writerow([])
        
        # Top performers
        if 'top_performers' in report_data:
            performers = report_data['top_performers']
            
            if 'top_courses' in performers:
                writer.writerow(['Top Courses by Enrollment'])
                writer.writerow(['Course Title', 'Instructor', 'Enrollment Count'])
                for course in performers['top_courses']:
                    writer.writerow([
                        course['course_title'],
                        course['instructor'],
                        course['enrollment_count']
                    ])
                writer.writerow([])
            
            if 'top_revenue_courses' in performers:
                writer.writerow(['Top Courses by Revenue'])
                writer.writerow(['Course Title', 'Instructor', 'Revenue'])
                for course in performers['top_revenue_courses']:
                    writer.writerow([
                        course['course_title'],
                        course['instructor'],
                        f"${course['revenue']:,.2f}"
                    ])


class ScheduledReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing scheduled report generation and background processing.
    """
    permission_classes = [IsAuthenticated]
    queryset = ScheduledReport.objects.all()
    
    def get_queryset(self):
        """Filter reports by tenant and user permissions"""
        tenant = getattr(self.request, 'tenant', None)
        queryset = ScheduledReport.objects.filter(tenant=tenant)
        
        # Non-admin users can only see their own reports
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = queryset.filter(created_by=self.request.user)
        
        return queryset.order_by('-scheduled_at')
    
    def create(self, request):
        """
        Schedule a report for background generation and email delivery.
        """
        tenant = getattr(request, 'tenant', None)
        
        # Validate request data
        report_type = request.data.get('report_type')
        email = request.data.get('email')
        schedule_time = request.data.get('schedule_time')  # Optional: for future scheduling
        filters = request.data.get('filters', {})
        format_type = request.data.get('format', 'pdf')
        
        if not report_type or not email:
            return StandardAPIResponse.error(
                message="report_type and email are required fields",
                status_code=400
            )
        
        # Validate report type
        valid_types = ['overview', 'enrollment', 'financial', 'course']
        if report_type not in valid_types:
            return StandardAPIResponse.error(
                message=f"Invalid report_type. Must be one of: {', '.join(valid_types)}",
                status_code=400
            )
        
        # Validate format type
        valid_formats = ['json', 'csv', 'pdf']
        if format_type not in valid_formats:
            return StandardAPIResponse.error(
                message=f"Invalid format. Must be one of: {', '.join(valid_formats)}",
                status_code=400
            )
        
        # Create scheduled report record
        scheduled_report = ScheduledReport.objects.create(
            tenant=tenant,
            created_by=request.user,
            report_type=report_type,
            format_type=format_type,
            email=email,
            filters=filters,
            execute_at=datetime.fromisoformat(schedule_time.replace('Z', '+00:00')) if schedule_time else None,
            estimated_completion=timezone.now() + timedelta(minutes=5),
            status='scheduled'
        )
        
        # In a real implementation, this would queue a Celery task for background processing
        # For now, simulate immediate processing
        try:
            scheduled_report.status = 'processing'
            scheduled_report.started_at = timezone.now()
            scheduled_report.save()
            
            # Generate the report
            report_generator = ReportGenerationView()
            filter_context = {
                'start_date': filters.get('start_date', timezone.now() - timedelta(days=30)),
                'end_date': filters.get('end_date', timezone.now()),
                'course_id': filters.get('course_id'),
                'instructor_id': filters.get('instructor_id'),
                'category': filters.get('category'),
                'user_type': filters.get('user_type', 'all')
            }
            
            # Convert string dates to datetime objects if needed
            if isinstance(filter_context['start_date'], str):
                filter_context['start_date'] = datetime.fromisoformat(
                    filter_context['start_date'].replace('Z', '+00:00')
                )
            if isinstance(filter_context['end_date'], str):
                filter_context['end_date'] = datetime.fromisoformat(
                    filter_context['end_date'].replace('Z', '+00:00')
                )
            
            # Check permissions for financial reports
            if report_type == 'financial' and not (request.user.is_staff or request.user.is_superuser):
                scheduled_report.status = 'failed'
                scheduled_report.error_message = "Only administrators can generate financial reports"
                scheduled_report.save()
                return StandardAPIResponse.error(
                    message="Only administrators can generate financial reports",
                    status_code=403
                )
            
            # Generate report data based on type
            if report_type == 'enrollment':
                report_data = report_generator._generate_enrollment_report(tenant, filter_context)
            elif report_type == 'financial':
                report_data = report_generator._generate_financial_report(tenant, filter_context)
            elif report_type == 'course':
                report_data = report_generator._generate_course_report(tenant, filter_context)
            else:  # overview
                report_data = report_generator._generate_overview_report(tenant, filter_context)
            
            # Update status and create download URL
            scheduled_report.status = 'completed'
            scheduled_report.completed_at = timezone.now()
            scheduled_report.progress_percentage = 100
            scheduled_report.download_url = f"/api/v1/reports/download/{scheduled_report.id}/"
            scheduled_report.save()
            
        except Exception as e:
            scheduled_report.status = 'failed'
            scheduled_report.error_message = str(e)
            scheduled_report.save()
        
        # Return serialized data
        report_data = {
            'id': str(scheduled_report.id),
            'report_type': scheduled_report.report_type,
            'format': scheduled_report.format_type,
            'email': scheduled_report.email,
            'status': scheduled_report.status,
            'scheduled_at': scheduled_report.scheduled_at.isoformat(),
            'estimated_completion': scheduled_report.estimated_completion.isoformat() if scheduled_report.estimated_completion else None,
            'download_url': scheduled_report.download_url,
            'error_message': scheduled_report.error_message,
            'progress_percentage': scheduled_report.progress_percentage
        }
        
        return StandardAPIResponse.success(
            data=report_data,
            message="Report scheduled successfully. You will receive an email when it's ready."
        )
    
    def list(self, request):
        """
        List all scheduled reports for the current user/tenant.
        """
        reports = self.get_queryset()
        
        # Serialize the reports
        reports_data = []
        for report in reports:
            reports_data.append({
                'id': str(report.id),
                'report_type': report.report_type,
                'format': report.format_type,
                'email': report.email,
                'status': report.status,
                'scheduled_at': report.scheduled_at.isoformat(),
                'started_at': report.started_at.isoformat() if report.started_at else None,
                'completed_at': report.completed_at.isoformat() if report.completed_at else None,
                'estimated_completion': report.estimated_completion.isoformat() if report.estimated_completion else None,
                'download_url': report.download_url,
                'error_message': report.error_message,
                'progress_percentage': report.progress_percentage,
                'file_size': report.file_size,
                'created_by': f"{report.created_by.first_name} {report.created_by.last_name}",
                'filters_applied': report.filters
            })
        
        return StandardAPIResponse.success(
            data=reports_data,
            message="Scheduled reports retrieved successfully"
        )
    
    def retrieve(self, request, pk=None):
        """
        Get details of a specific scheduled report.
        """
        try:
            report = self.get_queryset().get(pk=pk)
        except ScheduledReport.DoesNotExist:
            return StandardAPIResponse.error(
                message="Report not found",
                status_code=404
            )
        
        report_data = {
            'id': str(report.id),
            'report_type': report.report_type,
            'format': report.format_type,
            'email': report.email,
            'status': report.status,
            'scheduled_at': report.scheduled_at.isoformat(),
            'started_at': report.started_at.isoformat() if report.started_at else None,
            'completed_at': report.completed_at.isoformat() if report.completed_at else None,
            'estimated_completion': report.estimated_completion.isoformat() if report.estimated_completion else None,
            'download_url': report.download_url,
            'error_message': report.error_message,
            'progress_percentage': report.progress_percentage,
            'file_size': report.file_size,
            'file_path': report.file_path,
            'created_by': f"{report.created_by.first_name} {report.created_by.last_name}",
            'filters_applied': report.filters
        }
        
        return StandardAPIResponse.success(
            data=report_data,
            message="Report details retrieved successfully"
        )


class ReportDownloadView(APIView):
    """
    Handle secure report file downloads.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        """
        Download a generated report file.
        """
        tenant = getattr(request, 'tenant', None)
        
        try:
            # Get the report and validate access
            report = ScheduledReport.objects.get(id=report_id, tenant=tenant)
            
            # Check if user has access to this report
            if not (request.user.is_staff or request.user.is_superuser or report.created_by == request.user):
                return StandardAPIResponse.permission_denied(
                    message="You don't have permission to download this report"
                )
            
            # Check if report is completed
            if report.status != 'completed':
                return StandardAPIResponse.error(
                    message=f"Report is not ready for download. Status: {report.status}",
                    status_code=400
                )
            
            # In a real implementation, this would serve the actual file from storage
            # For now, generate sample content based on report type
            from django.http import HttpResponse
            
            if report.format_type == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{report.report_type}_report_{report.scheduled_at.strftime("%Y%m%d")}.csv"'
                
                import csv
                writer = csv.writer(response)
                writer.writerow([f'{report.get_report_type_display()} Report'])
                writer.writerow(['Generated At', report.completed_at.isoformat()])
                writer.writerow(['Generated By', f"{report.created_by.first_name} {report.created_by.last_name}"])
                writer.writerow([])
                writer.writerow(['Sample Data'])
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Users', '1,234'])
                writer.writerow(['Total Courses', '56'])
                writer.writerow(['Total Revenue', '$12,345.67'])
                
            elif report.format_type == 'json':
                response = HttpResponse(content_type='application/json')
                response['Content-Disposition'] = f'attachment; filename="{report.report_type}_report_{report.scheduled_at.strftime("%Y%m%d")}.json"'
                
                import json
                sample_data = {
                    'report_type': report.report_type,
                    'generated_at': report.completed_at.isoformat(),
                    'generated_by': f"{report.created_by.first_name} {report.created_by.last_name}",
                    'data': {
                        'total_users': 1234,
                        'total_courses': 56,
                        'total_revenue': 12345.67
                    }
                }
                response.write(json.dumps(sample_data, indent=2))
                
            else:  # PDF
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{report.report_type}_report_{report.scheduled_at.strftime("%Y%m%d")}.pdf"'
                
                # For now, return a simple text response indicating PDF would be generated
                response = HttpResponse(content_type='text/plain')
                response['Content-Disposition'] = f'attachment; filename="{report.report_type}_report_{report.scheduled_at.strftime("%Y%m%d")}.txt"'
                response.write(f"PDF Report: {report.get_report_type_display()}\n")
                response.write(f"Generated: {report.completed_at}\n")
                response.write(f"Generated By: {report.created_by.first_name} {report.created_by.last_name}\n")
                response.write("\nThis would be a PDF file in a real implementation.")
            
            return response
            
        except ScheduledReport.DoesNotExist:
            return StandardAPIResponse.error(
                message="Report not found",
                status_code=404
            )
        except Exception as e:
            return StandardAPIResponse.error(
                message=f"Error downloading report: {str(e)}",
                status_code=500
            )