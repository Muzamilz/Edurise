from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import viewsets
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import User, UserProfile, Organization
from apps.courses.models import Course, Enrollment, CourseReview
from apps.classes.models import ClassAttendance
from apps.courses.models import LiveClass
from apps.payments.models import Payment, Subscription
from apps.notifications.models import Notification
from .responses import StandardAPIResponse
from .mixins import APIResponseMixin


class StudentDashboardView(APIView):
    """
    Comprehensive student dashboard endpoint with enrollment, progress, and recommendation data.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get student dashboard data"""
        try:
            user = request.user
            tenant = getattr(request, 'tenant', None)
            
            # Check if tenant exists
            if not tenant:
                return StandardAPIResponse.error(
                    message="Tenant information is required",
                    status_code=400
                )
            
            # Get user's enrollments with optimized queries
            try:
                enrollments = Enrollment.objects.filter(
                    student=user,
                    tenant=tenant
                ).select_related('course', 'course__instructor', 'course__tenant').prefetch_related(
                    'course__reviews', 'course__live_classes', 'course__modules'
                )
            except Exception as e:
                import traceback
                print(f"Error fetching student enrollments: {str(e)}")
                print(traceback.format_exc())
                return StandardAPIResponse.error(
                    message=f"Error fetching enrollment data: {str(e)}",
                    status_code=500
                )
            
            try:
                # Basic enrollment statistics
                total_enrollments = enrollments.count()
                active_enrollments = enrollments.filter(status='active')
                completed_enrollments = enrollments.filter(status='completed')
                
                # Calculate progress metrics
                average_progress = enrollments.aggregate(
                    avg_progress=Avg('progress_percentage')
                )['avg_progress'] or 0
                
                # Get courses in progress (not completed, with some progress)
                courses_in_progress = active_enrollments.filter(
                    progress_percentage__gt=0,
                    progress_percentage__lt=100
                ).order_by('-last_accessed')[:5]
                
                # Get recently enrolled courses
                recent_enrollments = enrollments.order_by('-enrolled_at')[:5]
                
                # Get upcoming live classes
                upcoming_classes = LiveClass.objects.filter(
                    course__in=enrollments.values_list('course', flat=True),
                    scheduled_at__gte=timezone.now(),
                    status='scheduled'
                ).select_related('course').order_by('scheduled_at')[:5]
                
                # Get recommendations with enhanced logic
                from apps.courses.services import CourseService
                recommendations = CourseService.get_recommended_courses(
                    user=user,
                    tenant=tenant,
                    limit=6
                )
                
                # Get recent notifications
                recent_notifications = Notification.objects.filter(
                    user=user,
                    tenant=tenant
                ).order_by('-created_at')[:5]
                
                # Calculate learning streak (simplified)
                learning_streak = self.calculate_learning_streak(user, tenant)
                
                # Get certificates earned
                certificates_earned = completed_enrollments.count()  # Simplified
                
                # Total learning hours (simplified calculation)
                total_hours = sum(
                    enrollment.course.duration_weeks * 5  # Assume 5 hours per week
                    for enrollment in completed_enrollments
                )
            except Exception as e:
                import traceback
                print(f"Error calculating student dashboard statistics: {str(e)}")
                print(traceback.format_exc())
                return StandardAPIResponse.error(
                    message=f"Error calculating dashboard statistics: {str(e)}",
                    status_code=500
                )
        except Exception as e:
            import traceback
            print(f"Error in student dashboard: {str(e)}")
            print(traceback.format_exc())
            return StandardAPIResponse.error(
                message=f"Error loading dashboard: {str(e)}",
                status_code=500
            )
        
        try:
            # Get user profile info safely
            user_profile = user.profiles.filter(tenant=tenant).first()
            avatar_url = None
            if user_profile and hasattr(user_profile, 'avatar') and user_profile.avatar:
                try:
                    avatar_url = user_profile.avatar.url
                except:
                    avatar_url = None
            
            dashboard_data = {
                'user_info': {
                    'name': f"{user.first_name} {user.last_name}",
                    'email': user.email,
                    'avatar': avatar_url
                },
                'enrollment_stats': {
                    'total_enrollments': total_enrollments,
                    'active_courses': active_enrollments.count(),
                    'completed_courses': completed_enrollments.count(),
                    'average_progress': round(average_progress, 1),
                    'certificates_earned': certificates_earned,
                    'total_learning_hours': total_hours,
                    'learning_streak_days': learning_streak
                },
                'courses_in_progress': [
                    {
                        'id': enrollment.course.id,
                        'title': enrollment.course.title,
                        'progress_percentage': enrollment.progress_percentage,
                        'last_accessed': enrollment.last_accessed,
                        'instructor_name': f"{enrollment.course.instructor.first_name} {enrollment.course.instructor.last_name}",
                        'thumbnail': enrollment.course.thumbnail.url if enrollment.course.thumbnail else None
                    }
                    for enrollment in courses_in_progress
                ],
                'recent_enrollments': [
                    {
                        'id': enrollment.course.id,
                        'title': enrollment.course.title,
                        'enrolled_at': enrollment.enrolled_at,
                        'status': enrollment.status,
                        'progress_percentage': enrollment.progress_percentage,
                        'instructor_name': f"{enrollment.course.instructor.first_name} {enrollment.course.instructor.last_name}"
                    }
                    for enrollment in recent_enrollments
                ],
                'upcoming_classes': [
                    {
                        'id': live_class.id,
                        'title': live_class.title,
                        'course_title': live_class.course.title,
                        'scheduled_at': live_class.scheduled_at,
                        'duration_minutes': live_class.duration_minutes,
                        'join_url': live_class.join_url if live_class.join_url else None
                    }
                    for live_class in upcoming_classes
                ],
                'recommendations': [
                    {
                        'id': course.id,
                        'title': course.title,
                        'description': course.description[:200] + '...' if len(course.description) > 200 else course.description,
                        'price': float(course.price) if course.price else 0,
                        'instructor_name': f"{course.instructor.first_name} {course.instructor.last_name}",
                        'average_rating': course.reviews.filter(is_approved=True).aggregate(
                            avg_rating=Avg('rating')
                        )['avg_rating'] or 0,
                        'enrollment_count': course.enrollments.count(),
                        'thumbnail': course.thumbnail.url if course.thumbnail else None
                    }
                    for course in recommendations
                ],
                'recent_notifications': [
                    {
                        'id': notification.id,
                        'title': notification.title,
                        'message': notification.message,
                        'created_at': notification.created_at,
                        'is_read': notification.is_read,
                        'notification_type': notification.notification_type
                    }
                    for notification in recent_notifications
                ]
            }
            
            return StandardAPIResponse.success(
                data=dashboard_data,
                message="Student dashboard data retrieved successfully"
            )
        except Exception as e:
            import traceback
            print(f"Error serializing student dashboard data: {str(e)}")
            print(traceback.format_exc())
            return StandardAPIResponse.error(
                message=f"Error preparing dashboard data: {str(e)}",
                status_code=500
            )
    
    def calculate_learning_streak(self, user, tenant):
        """Calculate learning streak in days (simplified implementation)"""
        # This is a simplified calculation
        # In a real system, you'd track daily learning activity
        recent_activity = Enrollment.objects.filter(
            student=user,
            tenant=tenant,
            last_accessed__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        return min(recent_activity, 7)  # Max 7 days for this simple calculation


class TeacherDashboardView(APIView):
    """
    Comprehensive teacher dashboard endpoint with course statistics and student analytics.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get teacher dashboard data"""
        try:
            user = request.user
            tenant = getattr(request, 'tenant', None)
            
            # Check if tenant exists
            if not tenant:
                return StandardAPIResponse.error(
                    message="Tenant information is required",
                    status_code=400
                )
            
            # Check if user is a teacher - either by profile role or by having courses
            try:
                profile = UserProfile.objects.get(user=user, tenant=tenant)
                is_teacher = profile.role == 'teacher' or profile.is_approved_teacher
            except UserProfile.DoesNotExist:
                # If no profile exists, check if user has any courses (fallback)
                is_teacher = Course.objects.filter(instructor=user, tenant=tenant).exists()
                
            if not is_teacher:
                return StandardAPIResponse.permission_denied(
                    message="Only teachers can access this dashboard"
                )
        except Exception as e:
            import traceback
            print(f"Error in teacher dashboard permission check: {str(e)}")
            print(traceback.format_exc())
            return StandardAPIResponse.error(
                message=f"Error checking permissions: {str(e)}",
                status_code=500
            )
        
        try:
            # Get teacher's courses with optimized queries
            courses = Course.objects.filter(
                instructor=user,
                tenant=tenant
            ).select_related('instructor', 'tenant').prefetch_related(
                'enrollments__student', 'reviews', 'live_classes', 'modules'
            )
            
            # Get all enrollments for teacher's courses
            enrollments = Enrollment.objects.filter(
                course__in=courses
            ).select_related('student', 'course')
        except Exception as e:
            import traceback
            print(f"Error fetching teacher courses: {str(e)}")
            print(traceback.format_exc())
            return StandardAPIResponse.error(
                message=f"Error fetching course data: {str(e)}",
                status_code=500
            )
        
        try:
            # Basic statistics
            total_courses = courses.count()
            published_courses = courses.filter(is_public=True).count()
            total_students = enrollments.values('student').distinct().count()
            total_enrollments = enrollments.count()
            
            # Revenue calculation
            total_revenue = sum(
                float(course.price or 0) * course.enrollments.count()
                for course in courses
            )
            
            # Average rating
            average_rating = CourseReview.objects.filter(
                course__in=courses,
                is_approved=True
            ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
            
            # Recent enrollments
            recent_enrollments = enrollments.order_by('-enrolled_at')[:10]
            
            # Course performance
            course_performance = []
            for course in courses:
                course_enrollments = course.enrollments.all()
                course_reviews = course.reviews.filter(is_approved=True)
                
                performance = {
                    'id': course.id,
                    'title': course.title,
                    'total_enrollments': course_enrollments.count(),
                    'active_enrollments': course_enrollments.filter(status='active').count(),
                    'completed_enrollments': course_enrollments.filter(status='completed').count(),
                    'average_progress': course_enrollments.aggregate(
                        avg_progress=Avg('progress_percentage')
                    )['avg_progress'] or 0,
                    'average_rating': course_reviews.aggregate(
                        avg_rating=Avg('rating')
                    )['avg_rating'] or 0,
                    'total_reviews': course_reviews.count(),
                    'revenue': float(course.price or 0) * course_enrollments.count(),
                    'completion_rate': (
                        course_enrollments.filter(status='completed').count() / 
                        max(course_enrollments.count(), 1) * 100
                    )
                }
                course_performance.append(performance)
            
            # Upcoming live classes
            upcoming_classes = LiveClass.objects.filter(
                course__in=courses,
                scheduled_at__gte=timezone.now(),
                status='scheduled'
            ).select_related('course').order_by('scheduled_at')[:5]
            
            # Monthly enrollment trend (last 6 months)
            enrollment_trend = []
            for i in range(6):
                month_start = timezone.now().replace(day=1) - timedelta(days=32*i)
                month_start = month_start.replace(day=1)
                if month_start.month == 12:
                    month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
                else:
                    month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
                
                monthly_enrollments = enrollments.filter(
                    enrolled_at__gte=month_start,
                    enrolled_at__lte=month_end
                ).count()
                
                enrollment_trend.append({
                    'month': month_start.strftime('%Y-%m'),
                    'enrollments': monthly_enrollments
                })
            
            enrollment_trend.reverse()
        except Exception as e:
            import traceback
            print(f"Error calculating teacher dashboard statistics: {str(e)}")
            print(traceback.format_exc())
            return StandardAPIResponse.error(
                message=f"Error calculating dashboard statistics: {str(e)}",
                status_code=500
            )
        
        # Get instructor profile info safely
        instructor_profile = user.profiles.filter(tenant=tenant).first()
        avatar_url = None
        if instructor_profile and hasattr(instructor_profile, 'avatar') and instructor_profile.avatar:
            try:
                avatar_url = instructor_profile.avatar.url
            except:
                avatar_url = None
        
        dashboard_data = {
            'instructor_info': {
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'avatar': avatar_url
            },
            'overview_stats': {
                'total_courses': total_courses,
                'published_courses': published_courses,
                'total_students': total_students,
                'total_enrollments': total_enrollments,
                'total_revenue': total_revenue,
                'average_rating': round(average_rating, 1)
            },
            'recent_enrollments': [
                {
                    'student_name': f"{enrollment.student.first_name} {enrollment.student.last_name}",
                    'student_email': enrollment.student.email,
                    'course_title': enrollment.course.title,
                    'enrolled_at': enrollment.enrolled_at,
                    'progress_percentage': enrollment.progress_percentage,
                    'status': enrollment.status
                }
                for enrollment in recent_enrollments
            ],
            'course_performance': sorted(course_performance, key=lambda x: x['total_enrollments'], reverse=True),
            'upcoming_classes': [
                {
                    'id': live_class.id,
                    'title': live_class.title,
                    'course_title': live_class.course.title,
                    'scheduled_at': live_class.scheduled_at,
                    'duration_minutes': live_class.duration_minutes,
                    'enrolled_students': live_class.course.enrollments.filter(status='active').count()
                }
                for live_class in upcoming_classes
            ],
            'enrollment_trend': enrollment_trend
        }
        
        return StandardAPIResponse.success(
            data=dashboard_data,
            message="Teacher dashboard data retrieved successfully"
        )


class AdminDashboardView(APIView):
    """
    Comprehensive admin dashboard endpoint with organizational metrics and user statistics.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get admin dashboard data"""
        try:
            user = request.user
            tenant = getattr(request, 'tenant', None)
            
            # Check if tenant exists
            if not tenant:
                return StandardAPIResponse.error(
                    message="Tenant information is required",
                    status_code=400
                )
            
            if not user.is_staff:
                return StandardAPIResponse.permission_denied(
                    message="Only administrators can access this dashboard"
                )
            
            # Optimized statistics with single queries
            thirty_days_ago = timezone.now() - timedelta(days=30)
        except Exception as e:
            import traceback
            print(f"Error in admin dashboard initialization: {str(e)}")
            print(traceback.format_exc())
            return StandardAPIResponse.error(
                message=f"Error initializing dashboard: {str(e)}",
                status_code=500
            )
        
        try:
            # User statistics with single query
            users = User.objects.filter(profiles__tenant=tenant)
            user_stats = users.aggregate(
                total_users=Count('id'),
                active_users=Count('id', filter=Q(last_login__gte=thirty_days_ago)),
                new_users_this_month=Count('id', filter=Q(date_joined__gte=thirty_days_ago))
            )
            
            # Teacher statistics from UserProfile for this tenant
            teacher_profiles = UserProfile.objects.filter(tenant=tenant)
            teacher_stats = teacher_profiles.aggregate(
                total_teachers=Count('id', filter=Q(role='teacher')),
                approved_teachers=Count('id', filter=Q(role='teacher', is_approved_teacher=True))
            )
            
            # Merge teacher stats into user stats
            user_stats.update(teacher_stats)
            
            # Course statistics with single query
            courses = Course.objects.filter(tenant=tenant)
            course_stats = courses.aggregate(
                total_courses=Count('id'),
                published_courses=Count('id', filter=Q(is_public=True)),
                courses_this_month=Count('id', filter=Q(created_at__gte=thirty_days_ago)),
                avg_price=Avg('price'),
                total_modules=Count('modules')
            )
            
            # Enrollment statistics with single query
            enrollments = Enrollment.objects.filter(tenant=tenant)
            enrollment_stats = enrollments.aggregate(
                total_enrollments=Count('id'),
                active_enrollments=Count('id', filter=Q(status='active')),
                completed_enrollments=Count('id', filter=Q(status='completed')),
                dropped_enrollments=Count('id', filter=Q(status='dropped')),
                enrollments_this_month=Count('id', filter=Q(enrolled_at__gte=thirty_days_ago)),
                avg_progress=Avg('progress_percentage')
            )
            
            # Revenue statistics with single query
            payments = Payment.objects.filter(tenant=tenant, status='completed')
            revenue_stats = payments.aggregate(
                total_revenue=Sum('amount'),
                revenue_this_month=Sum('amount', filter=Q(created_at__gte=thirty_days_ago)),
                total_payments=Count('id'),
                avg_payment=Avg('amount')
            )
        except Exception as e:
            import traceback
            print(f"Error calculating admin dashboard statistics: {str(e)}")
            print(traceback.format_exc())
            return StandardAPIResponse.error(
                message=f"Error calculating dashboard statistics: {str(e)}",
                status_code=500
            )
        
        # Live class statistics with single query
        live_classes = LiveClass.objects.filter(course__tenant=tenant)
        class_stats = live_classes.aggregate(
            total_classes=Count('id'),
            completed_classes=Count('id', filter=Q(status='completed')),
            upcoming_classes=Count('id', filter=Q(
                scheduled_at__gte=timezone.now(),
                status='scheduled'
            )),
            avg_duration=Avg('duration_minutes')
        )
        
        # Popular courses
        popular_courses = courses.annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count')[:5]
        
        # Recent activity
        recent_enrollments = enrollments.select_related('student', 'course').order_by('-enrolled_at')[:10]
        recent_courses = courses.select_related('instructor').order_by('-created_at')[:5]
        
        # User growth trend (last 6 months)
        user_growth_trend = []
        for i in range(6):
            month_start = timezone.now().replace(day=1) - timedelta(days=32*i)
            month_start = month_start.replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
            
            monthly_users = users.filter(
                date_joined__gte=month_start,
                date_joined__lte=month_end
            ).count()
            
            user_growth_trend.append({
                'month': month_start.strftime('%Y-%m'),
                'new_users': monthly_users
            })
        
        user_growth_trend.reverse()
        
        # System health metrics
        system_health = {
            'database_status': 'healthy',  # Could add actual health checks
            'cache_status': 'healthy',
            'storage_status': 'healthy',
            'last_backup': timezone.now() - timedelta(days=1)  # Mock data
        }
        
        # Get organization info safely
        org_name = tenant.name if tenant else 'System'
        subscription_plan = 'enterprise'
        if tenant and hasattr(tenant, 'subscription') and tenant.subscription:
            try:
                subscription_plan = tenant.subscription.plan.name
            except:
                subscription_plan = 'enterprise'
        
        logo_url = None
        if tenant and hasattr(tenant, 'logo') and tenant.logo:
            try:
                logo_url = tenant.logo.url
            except:
                logo_url = None
        
        dashboard_data = {
            'organization_info': {
                'name': org_name,
                'subscription_plan': subscription_plan,
                'logo': logo_url
            },
            'user_stats': {
                **user_stats,
                'pending_teacher_approvals': user_stats['total_teachers'] - user_stats['approved_teachers'],
                'user_growth_rate': (user_stats['new_users_this_month'] / max(user_stats['total_users'], 1)) * 100
            },
            'course_stats': {
                **course_stats,
                'private_courses': course_stats['total_courses'] - course_stats['published_courses'],
                'avg_price': float(course_stats['avg_price'] or 0),
                'average_rating': CourseReview.objects.filter(
                    course__tenant=tenant,
                    is_approved=True
                ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0,
                'avg_modules_per_course': (course_stats['total_modules'] / max(course_stats['total_courses'], 1))
            },
            'enrollment_stats': {
                **enrollment_stats,
                'completion_rate': (enrollment_stats['completed_enrollments'] / 
                                  max(enrollment_stats['total_enrollments'], 1)) * 100,
                'dropout_rate': (enrollment_stats['dropped_enrollments'] / 
                               max(enrollment_stats['total_enrollments'], 1)) * 100,
                'avg_progress': round(enrollment_stats['avg_progress'] or 0, 2)
            },
            'revenue_stats': {
                'total_revenue': float(revenue_stats['total_revenue'] or 0),
                'revenue_this_month': float(revenue_stats['revenue_this_month'] or 0),
                'avg_payment': float(revenue_stats['avg_payment'] or 0),
                'total_payments': revenue_stats['total_payments'],
                'revenue_growth_rate': (
                    (float(revenue_stats['revenue_this_month'] or 0) / 
                     max(float(revenue_stats['total_revenue'] or 1), 1)) * 100
                ) if revenue_stats['total_revenue'] else 0
            },
            'class_stats': {
                **class_stats,
                'class_completion_rate': (class_stats['completed_classes'] / 
                                        max(class_stats['total_classes'], 1)) * 100,
                'avg_duration': round(class_stats['avg_duration'] or 0, 1)
            },
            'popular_courses': [
                {
                    'id': course.id,
                    'title': course.title,
                    'instructor_name': f"{course.instructor.first_name} {course.instructor.last_name}",
                    'enrollment_count': course.enrollment_count,
                    'average_rating': course.reviews.filter(is_approved=True).aggregate(
                        avg_rating=Avg('rating')
                    )['avg_rating'] or 0
                }
                for course in popular_courses
            ],
            'recent_activity': {
                'recent_enrollments': [
                    {
                        'student_name': f"{enrollment.student.first_name} {enrollment.student.last_name}",
                        'course_title': enrollment.course.title,
                        'enrolled_at': enrollment.enrolled_at
                    }
                    for enrollment in recent_enrollments
                ],
                'recent_courses': [
                    {
                        'id': course.id,
                        'title': course.title,
                        'instructor_name': f"{course.instructor.first_name} {course.instructor.last_name}",
                        'created_at': course.created_at,
                        'is_public': course.is_public
                    }
                    for course in recent_courses
                ]
            },
            'user_growth_trend': user_growth_trend,
            'system_health': system_health
        }
        
        return StandardAPIResponse.success(
            data=dashboard_data,
            message="Admin dashboard data retrieved successfully"
        )


class SuperAdminDashboardView(APIView):
    """
    Comprehensive super admin dashboard endpoint with platform-wide analytics.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get super admin dashboard data"""
        try:
            user = request.user
            
            if not user.is_superuser:
                return StandardAPIResponse.permission_denied(
                    message="Only super administrators can access this dashboard"
                )
            
            # Platform-wide statistics with optimized queries
            thirty_days_ago = timezone.now() - timedelta(days=30)
        except Exception as e:
            import traceback
            print(f"Error in super admin dashboard initialization: {str(e)}")
            print(traceback.format_exc())
            return StandardAPIResponse.error(
                message=f"Error initializing dashboard: {str(e)}",
                status_code=500
            )
        
        try:
            # Organization statistics
            org_stats = Organization.objects.aggregate(
                total_organizations=Count('id'),
                active_organizations=Count('id', filter=Q(is_active=True)),
                new_organizations=Count('id', filter=Q(created_at__gte=thirty_days_ago))
            )
            
            # User statistics across all tenants
            user_stats = User.objects.aggregate(
                total_users=Count('id'),
                active_users=Count('id', filter=Q(last_login__gte=thirty_days_ago)),
                new_users=Count('id', filter=Q(date_joined__gte=thirty_days_ago))
            )
            
            # Teacher statistics from UserProfile
            teacher_stats = UserProfile.objects.aggregate(
                total_teachers=Count('id', filter=Q(role='teacher')),
                approved_teachers=Count('id', filter=Q(role='teacher', is_approved_teacher=True))
            )
            
            # Merge teacher stats into user stats
            user_stats.update(teacher_stats)
            
            # Course statistics across all tenants
            course_stats = Course.objects.aggregate(
                total_courses=Count('id'),
                published_courses=Count('id', filter=Q(is_public=True)),
                new_courses=Count('id', filter=Q(created_at__gte=thirty_days_ago)),
                avg_price=Avg('price')
            )
            
            # Enrollment statistics across all tenants
            enrollment_stats = Enrollment.objects.aggregate(
                total_enrollments=Count('id'),
                completed_enrollments=Count('id', filter=Q(status='completed')),
                active_enrollments=Count('id', filter=Q(status='active')),
                new_enrollments=Count('id', filter=Q(enrolled_at__gte=thirty_days_ago))
            )
            
            # Revenue statistics across all tenants
            revenue_stats = Payment.objects.filter(status='completed').aggregate(
                total_revenue=Sum('amount'),
                revenue_this_month=Sum('amount', filter=Q(created_at__gte=thirty_days_ago)),
                total_payments=Count('id')
            )
        except Exception as e:
            import traceback
            print(f"Error calculating super admin dashboard statistics: {str(e)}")
            print(traceback.format_exc())
            return StandardAPIResponse.error(
                message=f"Error calculating dashboard statistics: {str(e)}",
                status_code=500
            )
        
        # Organization performance
        org_performance = []
        for org in Organization.objects.filter(is_active=True):
            org_users = User.objects.filter(profiles__tenant=org).count()
            org_courses = Course.objects.filter(tenant=org).count()
            org_enrollments = Enrollment.objects.filter(tenant=org).count()
            org_revenue = Payment.objects.filter(tenant=org, status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            # Get subscription plan name
            subscription_plan_name = 'No Plan'
            try:
                if hasattr(org, 'subscription') and org.subscription:
                    subscription_plan_name = org.subscription.plan.name
            except:
                subscription_plan_name = 'No Plan'
            
            org_performance.append({
                'id': org.id,
                'name': org.name,
                'subdomain': org.subdomain,
                'subscription_plan': subscription_plan_name,
                'total_users': org_users,
                'total_courses': org_courses,
                'total_enrollments': org_enrollments,
                'total_revenue': float(org_revenue),
                'created_at': org.created_at
            })
        
        # Platform growth trend (last 12 months)
        growth_trend = []
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=32*i)
            month_start = month_start.replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
            
            monthly_users = User.objects.filter(
                date_joined__gte=month_start,
                date_joined__lte=month_end
            ).count()
            
            monthly_orgs = Organization.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end
            ).count()
            
            monthly_revenue = Payment.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            growth_trend.append({
                'month': month_start.strftime('%Y-%m'),
                'new_users': monthly_users,
                'new_organizations': monthly_orgs,
                'revenue': float(monthly_revenue)
            })
        
        growth_trend.reverse()
        
        dashboard_data = {
            'platform_stats': {
                **org_stats,
                **user_stats,
                **course_stats,
                **enrollment_stats,
                'total_revenue': float(revenue_stats['total_revenue'] or 0),
                'revenue_this_month': float(revenue_stats['revenue_this_month'] or 0),
                'total_payments': revenue_stats['total_payments'],
                'platform_completion_rate': (enrollment_stats['completed_enrollments'] / 
                                           max(enrollment_stats['total_enrollments'], 1)) * 100,
                'avg_price': float(course_stats['avg_price'] or 0),
                'growth_metrics': {
                    'user_growth_rate': (user_stats['new_users'] / max(user_stats['total_users'], 1)) * 100,
                    'org_growth_rate': (org_stats['new_organizations'] / max(org_stats['total_organizations'], 1)) * 100,
                    'course_growth_rate': (course_stats['new_courses'] / max(course_stats['total_courses'], 1)) * 100,
                    'enrollment_growth_rate': (enrollment_stats['new_enrollments'] / max(enrollment_stats['total_enrollments'], 1)) * 100
                }
            },
            'organization_performance': sorted(org_performance, key=lambda x: x['total_revenue'], reverse=True),
            'growth_trend': growth_trend,
            'subscription_breakdown': {
                'basic': Organization.objects.filter(subscription__plan__name='basic').count(),
                'pro': Organization.objects.filter(subscription__plan__name='pro').count(),
                'enterprise': Organization.objects.filter(subscription__plan__name='enterprise').count()
            }
        }
        
        return StandardAPIResponse.success(
            data=dashboard_data,
            message="Super admin dashboard data retrieved successfully"
        )