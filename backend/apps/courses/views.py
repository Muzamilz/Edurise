from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Avg, Q
from django.utils import timezone
from .models import Course, LiveClass, CourseModule, CourseReview, CourseLicense, Enrollment, Wishlist, RecommendationInteraction
from .serializers import (
    CourseSerializer, CourseDetailSerializer, LiveClassSerializer,
    CourseModuleSerializer, CourseReviewSerializer, CourseLicenseSerializer,
    EnrollmentSerializer, WishlistSerializer
)
from .filters import CourseFilter, LiveClassFilter, EnrollmentFilter
from .services import CourseService, EnrollmentService
from apps.api.responses import StandardAPIResponse
from apps.api.mixins import StandardViewSetMixin


class CourseViewSet(StandardViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Course model with enhanced query optimization"""
    
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'title', 'price']
    ordering = ['-created_at']
    
    # Query optimization fields
    select_related_fields = ['instructor', 'tenant']
    prefetch_related_fields = ['enrollments', 'reviews', 'modules', 'live_classes']
    
    def get_queryset(self):
        """Filter courses by tenant with optimized queries"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Course.objects.filter(tenant=self.request.tenant).select_related(
                'instructor', 'tenant'
            ).prefetch_related(
                'enrollments', 'reviews', 'modules', 'live_classes'
            )
        return Course.objects.none()
    
    def get_permissions(self):
        """Override permissions for public marketplace actions"""
        if self.action in ['marketplace', 'featured', 'categories', 'marketplace_enhanced']:
            # Public marketplace actions don't require authentication
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer
    
    def perform_create(self, serializer):
        """Set instructor and tenant when creating course"""
        serializer.save(
            instructor=self.request.user,
            tenant=self.request.tenant
        )
    
    @action(detail=False, methods=['get'])
    def marketplace(self, request):
        """Get public marketplace courses"""
        courses = Course.objects.filter(is_public=True)
        
        # Apply filters
        filterset = CourseFilter(request.GET, queryset=courses)
        if filterset.is_valid():
            courses = filterset.qs
        
        page = self.paginate_queryset(courses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(courses, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message='Marketplace courses retrieved successfully'
        )
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """Enroll in a course"""
        course = self.get_object()
        
        # Check if already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return self.error_response(
                message='Already enrolled in this course',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Create enrollment
        enrollment = Enrollment.objects.create(
            student=request.user,
            course=course,
            tenant=getattr(request, 'tenant', None)
        )
        
        serializer = EnrollmentSerializer(enrollment)
        return self.success_response(
            data=serializer.data,
            message='Successfully enrolled in course',
            status_code=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get enrolled students for a course"""
        course = self.get_object()
        
        # Check if user is instructor or admin
        if course.instructor != request.user and not request.user.is_staff:
            return self.permission_denied_response(
                message='Only course instructors and administrators can view enrolled students'
            )
        
        enrollments = course.enrollments.all()
        serializer = EnrollmentSerializer(enrollments, many=True)
        return self.success_response(
            data=serializer.data,
            message=f'Retrieved {enrollments.count()} enrolled students'
        )
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get course categories with counts"""
        categories = Course.objects.filter(
            tenant=request.tenant if hasattr(request, 'tenant') else None
        ).values('category').annotate(
            count=Count('id'),
            avg_rating=Avg('reviews__rating')
        ).order_by('category')
        
        return StandardAPIResponse.success(
            data=list(categories),
            message='Course categories retrieved successfully'
        )
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured courses (high rated, popular)"""
        courses = Course.objects.filter(
            tenant=request.tenant if hasattr(request, 'tenant') else None,
            is_public=True
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            enrollment_count=Count('enrollments')
        ).filter(
            Q(avg_rating__gte=4.0) | Q(enrollment_count__gte=10)
        ).order_by('-avg_rating', '-enrollment_count')[:10]
        
        serializer = self.get_serializer(courses, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message='Featured courses retrieved successfully'
        )
    
    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        """Get courses where user is instructor"""
        if not request.user.is_teacher:
            return StandardAPIResponse.permission_denied(
                message='Only teachers can access this endpoint'
            )
        
        courses = self.get_queryset().filter(instructor=request.user)
        
        page = self.paginate_queryset(courses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def enrolled_courses(self, request):
        """Get courses where user is enrolled"""
        enrollments = Enrollment.objects.filter(
            student=request.user,
            tenant=request.tenant if hasattr(request, 'tenant') else None
        ).select_related('course')
        
        courses = [enrollment.course for enrollment in enrollments]
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a course (for instructors)"""
        original_course = self.get_object()
        
        # Check if user is instructor or admin
        if original_course.instructor != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create duplicate course
        new_course = Course.objects.create(
            title=f"{original_course.title} (Copy)",
            description=original_course.description,
            instructor=request.user,
            tenant=request.tenant,
            category=original_course.category,
            tags=original_course.tags.copy(),
            price=original_course.price,
            max_students=original_course.max_students,
            duration_weeks=original_course.duration_weeks,
            difficulty_level=original_course.difficulty_level,
            is_public=False  # Start as private
        )
        
        # Duplicate modules
        for module in original_course.modules.all():
            CourseModule.objects.create(
                course=new_course,
                title=module.title,
                description=module.description,
                content=module.content,
                order=module.order,
                is_published=False,  # Start as unpublished
                video_url=module.video_url,
                materials=module.materials.copy()
            )
        
        serializer = self.get_serializer(new_course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get detailed statistics for a course"""
        course = self.get_object()
        
        # Check if user is instructor or admin
        if course.instructor != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = CourseService.get_course_statistics(course)
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get intelligent course recommendations based on user behavior and preferences"""
        limit = int(request.query_params.get('limit', 10))
        
        # Get user's enrollment history for better recommendations
        user_enrollments = Enrollment.objects.filter(
            student=request.user,
            tenant=getattr(request, 'tenant', None)
        ).select_related('course').prefetch_related('course__reviews')
        
        # Get user's preferred categories
        user_categories = user_enrollments.values_list('course__category', flat=True).distinct()
        
        # Get user's skill level based on completed courses
        completed_courses = user_enrollments.filter(status='completed')
        user_skill_level = 'beginner'
        if completed_courses.count() > 5:
            user_skill_level = 'intermediate'
        if completed_courses.count() > 15:
            user_skill_level = 'advanced'
        
        # Build recommendation query with multiple criteria
        recommendations_query = Course.objects.filter(
            tenant=getattr(request, 'tenant', None),
            is_public=True
        ).exclude(
            id__in=user_enrollments.values_list('course_id', flat=True)
        ).select_related('instructor').prefetch_related('reviews', 'enrollments')
        
        # Apply intelligent filtering
        recommendations = []
        
        # 1. Courses in user's preferred categories (40% weight)
        if user_categories:
            category_recommendations = recommendations_query.filter(
                category__in=user_categories
            ).annotate(
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
                enrollment_count=Count('enrollments')
            ).order_by('-avg_rating', '-enrollment_count')[:limit//2]
            
            for course in category_recommendations:
                recommendations.append({
                    'course': course,
                    'reason': f"Based on your interest in {course.category} courses",
                    'confidence': 0.8,
                    'recommendation_type': 'category_based'
                })
        
        # 2. Popular courses with high ratings (30% weight)
        popular_recommendations = recommendations_query.annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            enrollment_count=Count('enrollments')
        ).filter(
            avg_rating__gte=4.0,
            enrollment_count__gte=10
        ).order_by('-enrollment_count', '-avg_rating')[:limit//3]
        
        for course in popular_recommendations:
            if not any(r['course'].id == course.id for r in recommendations):
                recommendations.append({
                    'course': course,
                    'reason': "Highly rated and popular among students",
                    'confidence': 0.7,
                    'recommendation_type': 'popularity_based'
                })
        
        # 3. Courses by instructors of completed courses (20% weight)
        if completed_courses.exists():
            instructor_ids = completed_courses.values_list('course__instructor_id', flat=True).distinct()
            instructor_recommendations = recommendations_query.filter(
                instructor_id__in=instructor_ids
            ).annotate(
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
            ).order_by('-avg_rating')[:limit//4]
            
            for course in instructor_recommendations:
                if not any(r['course'].id == course.id for r in recommendations):
                    recommendations.append({
                        'course': course,
                        'reason': f"From {course.instructor.first_name} {course.instructor.last_name}, whose courses you've completed",
                        'confidence': 0.6,
                        'recommendation_type': 'instructor_based'
                    })
        
        # 4. New and trending courses (10% weight)
        from datetime import timedelta
        recent_date = timezone.now() - timedelta(days=30)
        trending_recommendations = recommendations_query.filter(
            created_at__gte=recent_date
        ).annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count')[:limit//5]
        
        for course in trending_recommendations:
            if not any(r['course'].id == course.id for r in recommendations):
                recommendations.append({
                    'course': course,
                    'reason': "New and trending course",
                    'confidence': 0.5,
                    'recommendation_type': 'trending'
                })
        
        # Sort by confidence and limit results
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        recommendations = recommendations[:limit]
        
        # Format response data
        recommendations_data = []
        for rec in recommendations:
            course = rec['course']
            course_data = self.get_serializer(course).data
            
            # Add recommendation metadata
            course_data.update({
                'recommendation_reason': rec['reason'],
                'recommendation_confidence': rec['confidence'],
                'recommendation_type': rec['recommendation_type'],
                'enrollment_count': course.enrollments.count(),
                'average_rating': round(course.reviews.filter(is_approved=True).aggregate(
                    avg_rating=Avg('rating')
                )['avg_rating'] or 0, 2),
                'instructor_name': f"{course.instructor.first_name} {course.instructor.last_name}",
                'is_new': (timezone.now() - course.created_at).days < 30,
                'difficulty_match': course.difficulty_level == user_skill_level,
                'estimated_completion_time': f"{course.duration_weeks} weeks"
            })
            
            recommendations_data.append(course_data)
        
        # Add user context to response
        user_context = {
            'enrolled_courses_count': user_enrollments.count(),
            'completed_courses_count': completed_courses.count(),
            'preferred_categories': list(user_categories),
            'skill_level': user_skill_level,
            'recommendation_criteria': {
                'category_based': len([r for r in recommendations if r['recommendation_type'] == 'category_based']),
                'popularity_based': len([r for r in recommendations if r['recommendation_type'] == 'popularity_based']),
                'instructor_based': len([r for r in recommendations if r['recommendation_type'] == 'instructor_based']),
                'trending': len([r for r in recommendations if r['recommendation_type'] == 'trending'])
            }
        }
        
        return StandardAPIResponse.success(
            data={
                'recommendations': recommendations_data,
                'user_context': user_context,
                'total_count': len(recommendations_data),
                'generated_at': timezone.now().isoformat()
            },
            message='Course recommendations generated successfully'
        )
    
    @action(detail=False, methods=['get'])
    def instructor_analytics(self, request):
        """Get analytics for instructor's courses"""
        if not request.user.is_teacher:
            return StandardAPIResponse.permission_denied(
                message='Only teachers can access analytics'
            )
        
        analytics = CourseService.get_course_analytics_for_instructor(
            instructor=request.user,
            tenant=request.tenant
        )
        
        return StandardAPIResponse.success(
            data=analytics,
            message='Instructor analytics retrieved successfully'
        )
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get comprehensive course statistics for dashboard display with real data aggregation"""
        from datetime import timedelta
        
        tenant = getattr(request, 'tenant', None)
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        # Base queryset filtered by tenant with optimized queries
        courses = self.get_queryset()
        
        # Calculate comprehensive statistics with single queries
        course_stats = courses.aggregate(
            total_courses=Count('id'),
            published_courses=Count('id', filter=Q(is_public=True)),
            private_courses=Count('id', filter=Q(is_public=False)),
            avg_price=Avg('price'),
            total_modules=Count('modules'),
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
        )
        
        # Enrollment statistics with optimized queries
        enrollment_stats = Enrollment.objects.filter(
            course__in=courses
        ).aggregate(
            total_enrollments=Count('id'),
            active_enrollments=Count('id', filter=Q(status='active')),
            completed_enrollments=Count('id', filter=Q(status='completed')),
            dropped_enrollments=Count('id', filter=Q(status='dropped')),
            recent_enrollments=Count('id', filter=Q(enrolled_at__gte=thirty_days_ago)),
            avg_progress=Avg('progress_percentage')
        )
        
        # Review statistics
        review_stats = CourseReview.objects.filter(
            course__in=courses
        ).aggregate(
            total_reviews=Count('id'),
            approved_reviews=Count('id', filter=Q(is_approved=True)),
            pending_reviews=Count('id', filter=Q(is_approved=False)),
            recent_reviews=Count('id', filter=Q(created_at__gte=thirty_days_ago))
        )
        
        # Live class statistics
        live_class_stats = LiveClass.objects.filter(
            course__in=courses
        ).aggregate(
            total_classes=Count('id'),
            scheduled_classes=Count('id', filter=Q(status='scheduled')),
            completed_classes=Count('id', filter=Q(status='completed')),
            upcoming_classes=Count('id', filter=Q(
                status='scheduled',
                scheduled_at__gte=now
            ))
        )
        
        # Calculate completion rate
        completion_rate = 0
        if enrollment_stats['total_enrollments'] > 0:
            completion_rate = (enrollment_stats['completed_enrollments'] / 
                             enrollment_stats['total_enrollments']) * 100
        
        # Base statistics
        stats = {
            **course_stats,
            **enrollment_stats,
            **review_stats,
            **live_class_stats,
            'completion_rate': round(completion_rate, 2),
            'avg_price': float(course_stats['avg_price'] or 0),
            'avg_rating': round(course_stats['avg_rating'] or 0, 2),
            'avg_progress': round(enrollment_stats['avg_progress'] or 0, 2)
        }
        
        # Add role-specific statistics
        if request.user.is_teacher:
            # Teacher-specific stats with optimized queries
            teacher_courses = courses.filter(instructor=request.user)
            teacher_enrollments = Enrollment.objects.filter(course__in=teacher_courses)
            
            teacher_stats = teacher_courses.aggregate(
                my_courses=Count('id'),
                my_published_courses=Count('id', filter=Q(is_public=True)),
                my_avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
            )
            
            teacher_enrollment_stats = teacher_enrollments.aggregate(
                my_total_students=Count('student', distinct=True),
                my_total_enrollments=Count('id'),
                my_completed_enrollments=Count('id', filter=Q(status='completed'))
            )
            
            # Calculate revenue
            my_total_revenue = sum(
                float(course.price or 0) * course.enrollments.count()
                for course in teacher_courses.prefetch_related('enrollments')
            )
            
            stats.update({
                **teacher_stats,
                **teacher_enrollment_stats,
                'my_total_revenue': my_total_revenue,
                'my_avg_rating': round(teacher_stats['my_avg_rating'] or 0, 2),
                'my_completion_rate': (
                    (teacher_enrollment_stats['my_completed_enrollments'] / 
                     max(teacher_enrollment_stats['my_total_enrollments'], 1)) * 100
                ) if teacher_enrollment_stats['my_total_enrollments'] > 0 else 0
            })
        
        if request.user.is_staff:
            # Admin-specific stats with category breakdown
            categories_data = courses.values('category').annotate(
                count=Count('id'),
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
                total_enrollments=Count('enrollments'),
                avg_price=Avg('price')
            ).order_by('-count')
            
            # Top performing courses
            top_courses = courses.annotate(
                enrollment_count=Count('enrollments'),
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
            ).order_by('-enrollment_count')[:5]
            
            top_courses_data = []
            for course in top_courses:
                top_courses_data.append({
                    'id': course.id,
                    'title': course.title,
                    'instructor_name': f"{course.instructor.first_name} {course.instructor.last_name}",
                    'enrollment_count': course.enrollment_count,
                    'avg_rating': round(course.avg_rating or 0, 2),
                    'price': float(course.price or 0)
                })
            
            stats.update({
                'categories_count': len(categories_data),
                'courses_by_category': list(categories_data),
                'top_performing_courses': top_courses_data,
                'revenue_by_category': [
                    {
                        'category': cat['category'],
                        'revenue': cat['total_enrollments'] * (cat['avg_price'] or 0)
                    }
                    for cat in categories_data
                ]
            })
        
        # Add trend data (last 30 days)
        trend_data = []
        for i in range(30):
            date = thirty_days_ago + timedelta(days=i)
            daily_enrollments = Enrollment.objects.filter(
                course__in=courses,
                enrolled_at__date=date.date()
            ).count()
            trend_data.append({
                'date': date.date().isoformat(),
                'enrollments': daily_enrollments
            })
        
        stats['enrollment_trend'] = trend_data
        
        return StandardAPIResponse.success(
            data=stats,
            message='Course dashboard statistics retrieved successfully'
        )
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get comprehensive analytics for a specific course with enrollment trends and completion rates"""
        course = self.get_object()
        
        # Check permissions - only instructor, admin, or enrolled students
        if (course.instructor != request.user and 
            not request.user.is_staff and
            not Enrollment.objects.filter(student=request.user, course=course).exists()):
            return StandardAPIResponse.permission_denied(
                message='Only course instructors, administrators, or enrolled students can view analytics'
            )
        
        from datetime import timedelta
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        ninety_days_ago = now - timedelta(days=90)
        
        # Get comprehensive enrollment statistics with single query
        enrollment_stats = course.enrollments.aggregate(
            total_enrollments=Count('id'),
            active_enrollments=Count('id', filter=Q(status='active')),
            completed_enrollments=Count('id', filter=Q(status='completed')),
            dropped_enrollments=Count('id', filter=Q(status='dropped')),
            recent_enrollments=Count('id', filter=Q(enrolled_at__gte=thirty_days_ago)),
            avg_progress=Avg('progress_percentage'),
            students_above_50=Count('id', filter=Q(progress_percentage__gte=50)),
            students_above_80=Count('id', filter=Q(progress_percentage__gte=80)),
            recent_activity=Count('id', filter=Q(last_accessed__gte=now - timedelta(days=7)))
        )
        
        # Calculate completion rates by different time periods
        completion_rates = {
            'overall': 0,
            'last_30_days': 0,
            'last_90_days': 0
        }
        
        if enrollment_stats['total_enrollments'] > 0:
            completion_rates['overall'] = (enrollment_stats['completed_enrollments'] / 
                                         enrollment_stats['total_enrollments']) * 100
        
        # Recent completion rates
        recent_30_enrollments = course.enrollments.filter(enrolled_at__gte=thirty_days_ago)
        recent_90_enrollments = course.enrollments.filter(enrolled_at__gte=ninety_days_ago)
        
        if recent_30_enrollments.count() > 0:
            completion_rates['last_30_days'] = (
                recent_30_enrollments.filter(status='completed').count() / 
                recent_30_enrollments.count()
            ) * 100
        
        if recent_90_enrollments.count() > 0:
            completion_rates['last_90_days'] = (
                recent_90_enrollments.filter(status='completed').count() / 
                recent_90_enrollments.count()
            ) * 100
        
        # Get detailed enrollment trends (last 90 days)
        enrollment_trend = []
        completion_trend = []
        
        for i in range(90):
            date = ninety_days_ago + timedelta(days=i)
            daily_enrollments = course.enrollments.filter(
                enrolled_at__date=date.date()
            ).count()
            daily_completions = course.enrollments.filter(
                completed_at__date=date.date()
            ).count()
            
            enrollment_trend.append({
                'date': date.date().isoformat(),
                'enrollments': daily_enrollments
            })
            completion_trend.append({
                'date': date.date().isoformat(),
                'completions': daily_completions
            })
        
        # Get comprehensive engagement metrics
        engagement_metrics = {
            'average_progress': round(enrollment_stats['avg_progress'] or 0, 2),
            'students_above_50_percent': enrollment_stats['students_above_50'],
            'students_above_80_percent': enrollment_stats['students_above_80'],
            'recent_activity_7_days': enrollment_stats['recent_activity'],
            'engagement_rate': (enrollment_stats['recent_activity'] / 
                              max(enrollment_stats['active_enrollments'], 1)) * 100,
            'average_time_to_complete': self._calculate_avg_completion_time(course),
            'dropout_rate': (enrollment_stats['dropped_enrollments'] / 
                           max(enrollment_stats['total_enrollments'], 1)) * 100
        }
        
        # Get detailed rating breakdown and review analytics
        reviews = course.reviews.filter(is_approved=True)
        rating_breakdown = {
            '5_star': reviews.filter(rating=5).count(),
            '4_star': reviews.filter(rating=4).count(),
            '3_star': reviews.filter(rating=3).count(),
            '2_star': reviews.filter(rating=2).count(),
            '1_star': reviews.filter(rating=1).count(),
        }
        
        # Calculate rating distribution percentages
        total_reviews = reviews.count()
        rating_distribution = {}
        for star, count in rating_breakdown.items():
            rating_distribution[star] = {
                'count': count,
                'percentage': (count / max(total_reviews, 1)) * 100
            }
        
        # Get module completion analytics
        module_analytics = []
        for module in course.modules.all():
            # This would require a ModuleProgress model in a real implementation
            # For now, we'll provide placeholder data
            module_analytics.append({
                'module_id': module.id,
                'module_title': module.title,
                'completion_rate': 85,  # Placeholder
                'average_time_spent': 45,  # Placeholder in minutes
                'difficulty_rating': 3.5  # Placeholder
            })
        
        # Revenue analytics
        revenue_data = {
            'total_revenue': float(course.price or 0) * enrollment_stats['total_enrollments'],
            'revenue_last_30_days': float(course.price or 0) * enrollment_stats['recent_enrollments'],
            'average_revenue_per_student': float(course.price or 0),
            'projected_monthly_revenue': float(course.price or 0) * (enrollment_stats['recent_enrollments'] * 30 / 30)
        }
        
        # Live class analytics
        live_class_stats = course.live_classes.aggregate(
            total_classes=Count('id'),
            completed_classes=Count('id', filter=Q(status='completed')),
            upcoming_classes=Count('id', filter=Q(status='scheduled', scheduled_at__gte=now)),
            avg_duration=Avg('duration_minutes')
        )
        
        analytics_data = {
            'course_info': {
                'id': course.id,
                'title': course.title,
                'instructor_name': f"{course.instructor.first_name} {course.instructor.last_name}",
                'category': course.category,
                'created_at': course.created_at,
                'price': float(course.price or 0)
            },
            'enrollment_statistics': enrollment_stats,
            'completion_rates': completion_rates,
            'enrollment_trend': enrollment_trend,
            'completion_trend': completion_trend,
            'engagement_metrics': engagement_metrics,
            'rating_analytics': {
                'average_rating': round(reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0, 2),
                'total_reviews': total_reviews,
                'rating_breakdown': rating_breakdown,
                'rating_distribution': rating_distribution,
                'recent_reviews': reviews.filter(created_at__gte=thirty_days_ago).count()
            },
            'module_analytics': module_analytics,
            'revenue_analytics': revenue_data,
            'live_class_analytics': live_class_stats,
            'performance_indicators': {
                'is_high_performing': (
                    enrollment_stats['total_enrollments'] > 50 and
                    completion_rates['overall'] > 70 and
                    reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] > 4.0
                ),
                'needs_attention': (
                    completion_rates['overall'] < 30 or
                    engagement_metrics['dropout_rate'] > 50
                ),
                'trending_up': enrollment_stats['recent_enrollments'] > (enrollment_stats['total_enrollments'] * 0.1)
            }
        }
        
        return StandardAPIResponse.success(
            data=analytics_data,
            message='Course analytics retrieved successfully'
        )
    
    def _calculate_avg_completion_time(self, course):
        """Calculate average time to complete course in days"""
        completed_enrollments = course.enrollments.filter(
            status='completed',
            completed_at__isnull=False
        )
        
        if not completed_enrollments.exists():
            return 0
        
        total_days = 0
        count = 0
        
        for enrollment in completed_enrollments:
            if enrollment.completed_at and enrollment.enrolled_at:
                days = (enrollment.completed_at - enrollment.enrolled_at).days
                total_days += days
                count += 1
        
        return round(total_days / max(count, 1), 1)
    
    @action(detail=False, methods=['get'])
    def marketplace_enhanced(self, request):
        """Enhanced marketplace endpoint with advanced filtering and search"""
        courses = Course.objects.filter(is_public=True)
        
        # Apply search query
        search_query = request.query_params.get('search', '')
        if search_query:
            courses = CourseService.search_courses(
                query=search_query,
                tenant=getattr(request, 'tenant', None)
            ).filter(is_public=True)
        
        # Apply filters
        category = request.query_params.get('category')
        if category:
            courses = courses.filter(category=category)
        
        difficulty = request.query_params.get('difficulty')
        if difficulty:
            courses = courses.filter(difficulty_level=difficulty)
        
        min_price = request.query_params.get('min_price')
        if min_price:
            courses = courses.filter(price__gte=float(min_price))
        
        max_price = request.query_params.get('max_price')
        if max_price:
            courses = courses.filter(price__lte=float(max_price))
        
        min_rating = request.query_params.get('min_rating')
        if min_rating:
            courses = courses.annotate(
                avg_rating=Avg('reviews__rating')
            ).filter(avg_rating__gte=float(min_rating))
        
        # Apply sorting
        sort_by = request.query_params.get('sort_by', 'created_at')
        sort_order = request.query_params.get('sort_order', 'desc')
        
        if sort_by == 'rating':
            courses = courses.annotate(avg_rating=Avg('reviews__rating'))
            sort_field = 'avg_rating'
        elif sort_by == 'enrollments':
            courses = courses.annotate(enrollment_count=Count('enrollments'))
            sort_field = 'enrollment_count'
        elif sort_by == 'price':
            sort_field = 'price'
        else:
            sort_field = 'created_at'
        
        if sort_order == 'desc':
            sort_field = f'-{sort_field}'
        
        courses = courses.order_by(sort_field)
        
        # Add metadata for each course
        courses = courses.select_related('instructor').prefetch_related('reviews', 'enrollments')
        
        # Paginate results
        page = self.paginate_queryset(courses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # Add marketplace-specific data to each course
            for i, course_data in enumerate(serializer.data):
                course = page[i]
                course_data.update({
                    'enrollment_count': course.enrollments.count(),
                    'average_rating': course.reviews.filter(is_approved=True).aggregate(
                        avg_rating=Avg('rating')
                    )['avg_rating'] or 0,
                    'review_count': course.reviews.filter(is_approved=True).count(),
                    'instructor_name': f"{course.instructor.first_name} {course.instructor.last_name}",
                    'is_bestseller': course.enrollments.count() > 100,  # Example criteria
                    'is_new': (timezone.now() - course.created_at).days < 30
                })
            
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)


class LiveClassViewSet(StandardViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for LiveClass model with Zoom integration through centralized API"""
    
    serializer_class = LiveClassSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = LiveClassFilter
    ordering_fields = ['scheduled_at', 'created_at']
    ordering = ['scheduled_at']
    
    # Query optimization fields
    select_related_fields = ['course', 'course__instructor', 'course__tenant']
    prefetch_related_fields = ['attendances', 'attendances__student']
    
    def get_queryset(self):
        """Filter live classes by tenant with optimized queries"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return LiveClass.objects.filter(
                course__tenant=self.request.tenant
            ).select_related(
                'course', 'course__instructor', 'course__tenant'
            ).prefetch_related(
                'attendances', 'attendances__student'
            )
        return LiveClass.objects.none()
    
    def perform_create(self, serializer):
        """Create live class and automatically create Zoom meeting"""
        live_class = serializer.save()
        
        # Check if user is instructor of the course
        if live_class.course.instructor != self.request.user and not self.request.user.is_staff:
            raise PermissionError("Only course instructors can create live classes")
        
        # Automatically create Zoom meeting
        try:
            from apps.classes.services import ZoomService
            zoom_service = ZoomService()
            meeting_info = zoom_service.create_meeting(live_class)
            
            # Broadcast class creation via WebSocket
            from apps.classes.websocket_service import broadcast_class_status_update
            broadcast_class_status_update(
                str(live_class.id),
                'scheduled',
                {
                    'meeting_created': True,
                    'meeting_id': live_class.zoom_meeting_id,
                    'join_url': live_class.join_url
                }
            )
            
        except Exception as e:
            # Log error but don't fail the creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create Zoom meeting for live class {live_class.id}: {str(e)}")
    
    def perform_update(self, serializer):
        """Update live class and sync with Zoom meeting"""
        live_class = serializer.save()
        
        # Check permissions
        if live_class.course.instructor != self.request.user and not self.request.user.is_staff:
            raise PermissionError("Only course instructors can update live classes")
        
        # Update Zoom meeting if it exists
        if live_class.zoom_meeting_id:
            try:
                from apps.classes.services import ZoomService
                zoom_service = ZoomService()
                zoom_service.update_meeting(live_class)
                
                # Broadcast class update via WebSocket
                from apps.classes.websocket_service import broadcast_class_status_update
                broadcast_class_status_update(
                    str(live_class.id),
                    live_class.status,
                    {
                        'meeting_updated': True,
                        'scheduled_at': live_class.scheduled_at.isoformat(),
                        'duration_minutes': live_class.duration_minutes
                    }
                )
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to update Zoom meeting for live class {live_class.id}: {str(e)}")
    
    @action(detail=True, methods=['post'])
    def create_zoom_meeting(self, request, pk=None):
        """Manually create or recreate Zoom meeting for live class"""
        live_class = self.get_object()
        
        # Check permissions
        if live_class.course.instructor != request.user and not request.user.is_staff:
            return self.error_response(
                message='Permission denied',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from apps.classes.services import ZoomService
            zoom_service = ZoomService()
            meeting_info = zoom_service.create_meeting(live_class)
            
            # Broadcast meeting creation via WebSocket
            from apps.classes.websocket_service import broadcast_class_status_update
            broadcast_class_status_update(
                str(live_class.id),
                live_class.status,
                {
                    'meeting_created': True,
                    'meeting_id': live_class.zoom_meeting_id,
                    'join_url': live_class.join_url
                }
            )
            
            return self.success_response(
                data={
                    'meeting_id': meeting_info['id'],
                    'join_url': meeting_info['join_url'],
                    'start_url': meeting_info['start_url'],
                    'password': meeting_info.get('password', ''),
                    'live_class_id': str(live_class.id),
                    'status': live_class.status
                },
                message='Zoom meeting created successfully'
            )
            
        except Exception as e:
            return self.error_response(
                message=f'Failed to create Zoom meeting: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def start_class(self, request, pk=None):
        """Start the live class (update status to live)"""
        live_class = self.get_object()
        
        # Check permissions
        if live_class.course.instructor != request.user and not request.user.is_staff:
            return self.error_response(
                message='Permission denied',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        if live_class.status != 'scheduled':
            return self.error_response(
                message='Class can only be started if it is scheduled',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        live_class.status = 'live'
        live_class.save()
        
        # Broadcast class started via WebSocket
        from apps.classes.websocket_service import broadcast_class_status_update
        broadcast_class_status_update(
            str(live_class.id),
            'live',
            {
                'class_started': True,
                'start_time': timezone.now().isoformat(),
                'join_url': live_class.join_url
            }
        )
        
        return self.success_response(
            data={
                'live_class_id': str(live_class.id),
                'status': 'live',
                'start_url': live_class.start_url,
                'join_url': live_class.join_url,
                'meeting_id': live_class.zoom_meeting_id,
                'password': live_class.password
            },
            message='Class started successfully'
        )
    
    @action(detail=True, methods=['post'])
    def end_class(self, request, pk=None):
        """End the live class (update status to completed)"""
        live_class = self.get_object()
        
        # Check permissions
        if live_class.course.instructor != request.user and not request.user.is_staff:
            return self.error_response(
                message='Permission denied',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        if live_class.status != 'live':
            return self.error_response(
                message='Class can only be ended if it is currently live',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        live_class.status = 'completed'
        live_class.save()
        
        # Calculate final attendance metrics
        from apps.classes.services import AttendanceService
        final_metrics = AttendanceService.calculate_engagement_metrics(live_class)
        
        # Broadcast class ended via WebSocket
        from apps.classes.websocket_service import broadcast_class_status_update
        broadcast_class_status_update(
            str(live_class.id),
            'completed',
            {
                'class_ended': True,
                'end_time': timezone.now().isoformat(),
                'final_metrics': final_metrics
            }
        )
        
        return self.success_response(
            data={
                'live_class_id': str(live_class.id),
                'status': 'completed',
                'end_time': timezone.now().isoformat(),
                'final_metrics': final_metrics
            },
            message='Class ended successfully'
        )
    
    @action(detail=True, methods=['get'])
    def attendance_report(self, request, pk=None):
        """Get detailed attendance report for the live class"""
        live_class = self.get_object()
        
        # Check permissions
        if live_class.course.instructor != request.user and not request.user.is_staff:
            return self.error_response(
                message='Permission denied',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from apps.classes.services import AttendanceService
            report = AttendanceService.get_class_analytics_report(live_class)
            
            return self.success_response(
                data=report,
                message='Attendance report generated successfully'
            )
            
        except Exception as e:
            return self.error_response(
                message=f'Failed to generate report: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def join_info(self, request, pk=None):
        """Get join information for students"""
        live_class = self.get_object()
        
        # Check if user is enrolled in the course
        from apps.courses.models import Enrollment
        if not Enrollment.objects.filter(
            student=request.user,
            course=live_class.course,
            status='active'
        ).exists() and not request.user.is_staff:
            return self.error_response(
                message='You must be enrolled in this course to join the class',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        if not live_class.join_url:
            return self.error_response(
                message='Zoom meeting not yet created for this class',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return self.success_response(
            data={
                'join_url': live_class.join_url,
                'password': live_class.password,
                'meeting_id': live_class.zoom_meeting_id,
                'class_title': live_class.title,
                'course_title': live_class.course.title,
                'instructor_name': live_class.course.instructor.get_full_name(),
                'scheduled_at': live_class.scheduled_at,
                'duration_minutes': live_class.duration_minutes,
                'status': live_class.status,
                'live_class_id': str(live_class.id),
                'course_id': str(live_class.course.id)
            },
            message='Join information retrieved successfully'
        )
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming live classes for the user"""
        now = timezone.now()
        
        if request.user.is_teacher:
            # For instructors, show their upcoming classes
            upcoming_classes = self.get_queryset().filter(
                course__instructor=request.user,
                scheduled_at__gte=now,
                status='scheduled'
            ).order_by('scheduled_at')[:10]
        else:
            # For students, show classes from enrolled courses
            from apps.courses.models import Enrollment
            enrolled_courses = Enrollment.objects.filter(
                student=request.user,
                status='active'
            ).values_list('course_id', flat=True)
            
            upcoming_classes = self.get_queryset().filter(
                course_id__in=enrolled_courses,
                scheduled_at__gte=now,
                status='scheduled'
            ).order_by('scheduled_at')[:10]
        
        serializer = self.get_serializer(upcoming_classes, many=True)
        return self.success_response(
            data=serializer.data,
            message='Upcoming live classes retrieved successfully'
        )
    
    @action(detail=True, methods=['get'])
    def recordings(self, request, pk=None):
        """Get recordings for a live class"""
        live_class = self.get_object()
        
        # Check if user can access recordings
        if not live_class.is_accessible_to_user(request.user):
            return self.error_response(
                message='Permission denied',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        from apps.courses.models import ClassRecording
        recordings = ClassRecording.objects.filter(
            live_class=live_class
        ).order_by('-recorded_at')
        
        # Filter recordings based on user access level
        accessible_recordings = []
        for recording in recordings:
            if recording.can_access(request.user):
                accessible_recordings.append({
                    'id': str(recording.id),
                    'title': recording.title,
                    'description': recording.description,
                    'recording_type': recording.recording_type,
                    'file_url': recording.file_url,
                    'file_size_mb': recording.file_size_mb,
                    'duration_minutes': recording.duration_minutes,
                    'file_format': recording.file_format,
                    'access_level': recording.access_level,
                    'password_protected': recording.password_protected,
                    'is_processed': recording.is_processed,
                    'processing_status': recording.processing_status,
                    'thumbnail_url': recording.thumbnail_url,
                    'view_count': recording.view_count,
                    'download_count': recording.download_count,
                    'recorded_at': recording.recorded_at,
                    'uploaded_at': recording.uploaded_at
                })
        
        return self.success_response(
            data={
                'live_class_id': str(live_class.id),
                'live_class_title': live_class.title,
                'recordings': accessible_recordings,
                'total_recordings': len(accessible_recordings)
            },
            message='Recordings retrieved successfully'
        )
    
    @action(detail=True, methods=['post'])
    def upload_recording(self, request, pk=None):
        """Upload or link a recording to a live class"""
        live_class = self.get_object()
        
        # Check permissions - only instructor or staff can upload recordings
        if live_class.course.instructor != request.user and not request.user.is_staff:
            return self.error_response(
                message='Permission denied',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        from apps.courses.models import ClassRecording
        
        # Get recording data from request
        title = request.data.get('title', f"{live_class.title} Recording")
        description = request.data.get('description', '')
        file_url = request.data.get('file_url')
        recording_type = request.data.get('recording_type', 'manual_upload')
        access_level = request.data.get('access_level', 'enrolled')
        file_size_mb = request.data.get('file_size_mb', 0)
        duration_minutes = request.data.get('duration_minutes', 0)
        recorded_at = request.data.get('recorded_at', timezone.now())
        
        if not file_url:
            return self.error_response(
                message='file_url is required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Create recording record
        recording = ClassRecording.objects.create(
            live_class=live_class,
            title=title,
            description=description,
            recording_type=recording_type,
            file_url=file_url,
            file_size_mb=file_size_mb,
            duration_minutes=duration_minutes,
            access_level=access_level,
            recorded_at=recorded_at
        )
        
        # Update live class recording status
        live_class.has_recording = True
        live_class.recording_url = file_url
        live_class.save()
        
        # Broadcast recording uploaded via WebSocket
        from apps.classes.websocket_service import broadcast_class_status_update
        broadcast_class_status_update(
            str(live_class.id),
            live_class.status,
            {
                'recording_uploaded': True,
                'recording_id': str(recording.id),
                'recording_title': recording.title
            }
        )
        
        return self.success_response(
            data={
                'recording_id': str(recording.id),
                'live_class_id': str(live_class.id),
                'title': recording.title,
                'file_url': recording.file_url,
                'access_level': recording.access_level,
                'recorded_at': recording.recorded_at
            },
            message='Recording uploaded successfully'
        )
    
    @action(detail=True, methods=['post'])
    def process_zoom_recording(self, request, pk=None):
        """Process Zoom cloud recording for a live class"""
        live_class = self.get_object()
        
        # Check permissions
        if live_class.course.instructor != request.user and not request.user.is_staff:
            return self.error_response(
                message='Permission denied',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        if not live_class.zoom_meeting_id:
            return self.error_response(
                message='No Zoom meeting associated with this class',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.classes.services import ZoomService
            zoom_service = ZoomService()
            
            # Get recording information from Zoom
            recording_info = zoom_service.get_meeting_recordings(live_class.zoom_meeting_id)
            
            if not recording_info:
                return self.error_response(
                    message='No recordings found for this meeting',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            from apps.courses.models import ClassRecording
            
            # Process each recording file
            created_recordings = []
            for recording_file in recording_info.get('recording_files', []):
                if recording_file.get('file_type') in ['MP4', 'M4A']:
                    recording = ClassRecording.objects.create(
                        live_class=live_class,
                        title=f"{live_class.title} - {recording_file.get('recording_type', 'Recording')}",
                        recording_type='zoom_cloud',
                        file_url=recording_file.get('download_url', ''),
                        file_size_mb=recording_file.get('file_size', 0) // (1024 * 1024),
                        duration_minutes=recording_info.get('duration', 0),
                        file_format=recording_file.get('file_extension', 'mp4').lower(),
                        access_level='enrolled',
                        password_protected=bool(recording_file.get('password')),
                        access_password=recording_file.get('password', ''),
                        recorded_at=recording_info.get('start_time', timezone.now())
                    )
                    
                    created_recordings.append({
                        'id': str(recording.id),
                        'title': recording.title,
                        'file_url': recording.file_url,
                        'file_format': recording.file_format,
                        'duration_minutes': recording.duration_minutes
                    })
            
            # Update live class
            if created_recordings:
                live_class.has_recording = True
                live_class.recording_processed = True
                live_class.recording_url = created_recordings[0]['file_url']
                live_class.save()
                
                # Broadcast recording processed via WebSocket
                from apps.classes.websocket_service import broadcast_class_status_update
                broadcast_class_status_update(
                    str(live_class.id),
                    live_class.status,
                    {
                        'recordings_processed': True,
                        'recording_count': len(created_recordings)
                    }
                )
            
            return self.success_response(
                data={
                    'live_class_id': str(live_class.id),
                    'recordings': created_recordings,
                    'total_recordings': len(created_recordings)
                },
                message=f'Processed {len(created_recordings)} recordings successfully'
            )
            
        except Exception as e:
            return self.error_response(
                message=f'Failed to process Zoom recordings: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def instructor_dashboard(self, request):
        """Get dashboard data for instructors"""
        if not request.user.is_teacher:
            return Response(
                {'error': 'Only instructors can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        now = timezone.now()
        instructor_classes = self.get_queryset().filter(course__instructor=request.user)
        
        dashboard_data = {
            'total_classes': instructor_classes.count(),
            'upcoming_classes': instructor_classes.filter(
                scheduled_at__gte=now,
                status='scheduled'
            ).count(),
            'completed_classes': instructor_classes.filter(status='completed').count(),
            'live_classes': instructor_classes.filter(status='live').count(),
            'recent_classes': []
        }
        
        # Get recent completed classes with basic metrics
        recent_classes = instructor_classes.filter(
            status='completed'
        ).order_by('-scheduled_at')[:5]
        
        for live_class in recent_classes:
            try:
                from apps.classes.services import AttendanceService
                metrics = AttendanceService.calculate_engagement_metrics(live_class)
                dashboard_data['recent_classes'].append({
                    'id': live_class.id,
                    'title': live_class.title,
                    'scheduled_at': live_class.scheduled_at,
                    'course_title': live_class.course.title,
                    'attendance_rate': metrics['attendance_rate'],
                    'engagement_score': metrics['engagement_score']
                })
            except Exception:
                # Skip if metrics calculation fails
                continue
        
        return Response(dashboard_data)


class CourseModuleViewSet(viewsets.ModelViewSet):
    """ViewSet for CourseModule model"""
    
    serializer_class = CourseModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter modules by tenant and course"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return CourseModule.objects.filter(course__tenant=self.request.tenant)
        return CourseModule.objects.none()


class CourseReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for CourseReview model"""
    
    serializer_class = CourseReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter reviews by tenant"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return CourseReview.objects.filter(course__tenant=self.request.tenant)
        return CourseReview.objects.none()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a course review"""
        review = self.get_object()
        review.is_approved = True
        review.save()
        return Response({'message': 'Review approved'})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        """Reject a course review"""
        review = self.get_object()
        review.is_approved = False
        review.save()
        return Response({'message': 'Review rejected'})


class EnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Enrollment model"""
    
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EnrollmentFilter
    ordering_fields = ['enrolled_at', 'progress_percentage', 'completed_at']
    ordering = ['-enrolled_at']
    
    def get_queryset(self):
        """Filter enrollments by tenant and user"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Enrollment.objects.filter(tenant=self.request.tenant)
            
            # Students can only see their own enrollments
            if not self.request.user.is_staff:
                queryset = queryset.filter(student=self.request.user)
            
            return queryset
        return Enrollment.objects.none()
    
    @action(detail=True, methods=['patch'])
    def update_progress(self, request, pk=None):
        """Update enrollment progress"""
        enrollment = self.get_object()
        
        # Only student or instructor can update progress
        if (enrollment.student != request.user and 
            enrollment.course.instructor != request.user and 
            not request.user.is_staff):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        progress = request.data.get('progress_percentage')
        if progress is not None:
            enrollment.progress_percentage = min(100, max(0, int(progress)))
            
            # Mark as completed if 100%
            if enrollment.progress_percentage == 100:
                from django.utils import timezone
                enrollment.completed_at = timezone.now()
                enrollment.status = 'completed'
            
            enrollment.save()
        
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get enrollment analytics for instructor"""
        if not request.user.is_teacher:
            return Response(
                {'error': 'Only teachers can access analytics'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get enrollments for instructor's courses (bypass tenant filtering for this query)
        enrollments = Enrollment.objects.filter(
            course__instructor=request.user,
            tenant=request.tenant if hasattr(request, 'tenant') else None
        )
        
        analytics = {
            'total_enrollments': enrollments.count(),
            'active_enrollments': enrollments.filter(status='active').count(),
            'completed_enrollments': enrollments.filter(status='completed').count(),
            'dropped_enrollments': enrollments.filter(status='dropped').count(),
            'average_progress': enrollments.aggregate(
                avg_progress=Avg('progress_percentage')
            )['avg_progress'] or 0,
            'completion_rate': (
                enrollments.filter(status='completed').count() / 
                max(enrollments.count(), 1) * 100
            )
        }
        
        return Response(analytics)
    
    @action(detail=True, methods=['post'])
    def drop(self, request, pk=None):
        """Drop from course"""
        enrollment = self.get_object()
        
        # Only student can drop themselves
        if enrollment.student != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        enrollment.status = 'dropped'
        enrollment.save()
        
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get student dashboard data"""
        dashboard_data = EnrollmentService.get_student_dashboard_data(
            student=request.user,
            tenant=request.tenant
        )
        
        # Serialize the enrollment data
        dashboard_data['recent_enrollments'] = EnrollmentSerializer(
            dashboard_data['recent_enrollments'], many=True
        ).data
        dashboard_data['courses_in_progress'] = EnrollmentSerializer(
            dashboard_data['courses_in_progress'], many=True
        ).data
        
        return Response(dashboard_data)
    
    @action(detail=True, methods=['get'])
    def progress_detail(self, request, pk=None):
        """Get detailed progress information for an enrollment"""
        enrollment = self.get_object()
        
        # Only student or instructor can view progress
        if (enrollment.student != request.user and 
            enrollment.course.instructor != request.user and 
            not request.user.is_staff):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        progress_data = CourseService.calculate_course_progress(enrollment)
        
        # Add enrollment data
        progress_data['enrollment'] = self.get_serializer(enrollment).data
        
        return Response(progress_data)


class WishlistViewSet(StandardViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Wishlist model with comprehensive wishlist management"""
    
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['course__title', 'course__description', 'notes']
    ordering_fields = ['added_at', 'priority', 'course__title', 'course__price']
    ordering = ['-priority', '-added_at']
    
    # Query optimization fields
    select_related_fields = ['user', 'course', 'course__instructor', 'tenant']
    prefetch_related_fields = ['course__reviews', 'course__enrollments']
    
    def get_queryset(self):
        """Filter wishlist items by current user and tenant"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Wishlist.objects.filter(
                user=self.request.user,
                tenant=self.request.tenant
            ).select_related(
                'user', 'course', 'course__instructor', 'tenant'
            ).prefetch_related(
                'course__reviews', 'course__enrollments'
            )
        return Wishlist.objects.none()
    
    def perform_create(self, serializer):
        """Set user and tenant when creating wishlist item"""
        # Check if course is already in wishlist
        course = serializer.validated_data['course']
        existing_item = Wishlist.objects.filter(
            user=self.request.user,
            course=course,
            tenant=self.request.tenant
        ).first()
        
        if existing_item:
            raise serializers.ValidationError({
                'course': 'This course is already in your wishlist'
            })
        
        # Check if user is already enrolled
        if Enrollment.objects.filter(
            student=self.request.user,
            course=course,
            tenant=self.request.tenant
        ).exists():
            raise serializers.ValidationError({
                'course': 'You are already enrolled in this course'
            })
        
        serializer.save(
            user=self.request.user,
            tenant=self.request.tenant
        )
    
    @action(detail=False, methods=['post'])
    def add_course(self, request):
        """Add a course to wishlist by course ID"""
        course_id = request.data.get('course_id')
        
        if not course_id:
            return StandardAPIResponse.validation_error(
                errors={'course_id': ['This field is required']},
                message='Course ID is required'
            )
        
        try:
            course = Course.objects.get(
                id=course_id,
                tenant=request.tenant if hasattr(request, 'tenant') else None
            )
        except Course.DoesNotExist:
            return StandardAPIResponse.not_found(
                message='Course not found'
            )
        
        # Check if already in wishlist
        if Wishlist.objects.filter(
            user=request.user,
            course=course,
            tenant=request.tenant
        ).exists():
            return StandardAPIResponse.validation_error(
                errors={'course': ['This course is already in your wishlist']},
                message='Course already in wishlist'
            )
        
        # Check if already enrolled
        if Enrollment.objects.filter(
            student=request.user,
            course=course,
            tenant=request.tenant
        ).exists():
            return StandardAPIResponse.validation_error(
                errors={'course': ['You are already enrolled in this course']},
                message='Already enrolled in course'
            )
        
        # Create wishlist item
        wishlist_item = Wishlist.objects.create(
            user=request.user,
            course=course,
            tenant=request.tenant,
            priority=request.data.get('priority', 2),
            notes=request.data.get('notes', ''),
            notify_price_change=request.data.get('notify_price_change', True),
            notify_course_updates=request.data.get('notify_course_updates', True),
            notify_enrollment_opening=request.data.get('notify_enrollment_opening', True)
        )
        
        serializer = self.get_serializer(wishlist_item)
        return StandardAPIResponse.success(
            data=serializer.data,
            message='Course added to wishlist successfully',
            status_code=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['delete'])
    def remove_course(self, request):
        """Remove a course from wishlist by course ID"""
        course_id = request.data.get('course_id')
        
        if not course_id:
            return StandardAPIResponse.validation_error(
                errors={'course_id': ['This field is required']},
                message='Course ID is required'
            )
        
        try:
            wishlist_item = Wishlist.objects.get(
                user=request.user,
                course_id=course_id,
                tenant=request.tenant if hasattr(request, 'tenant') else None
            )
            wishlist_item.delete()
            
            return StandardAPIResponse.success(
                message='Course removed from wishlist successfully'
            )
        except Wishlist.DoesNotExist:
            return StandardAPIResponse.not_found(
                message='Course not found in wishlist'
            )
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get wishlist analytics and insights"""
        wishlist_items = self.get_queryset()
        
        # Basic statistics
        total_items = wishlist_items.count()
        
        if total_items == 0:
            return StandardAPIResponse.success(
                data={
                    'total_items': 0,
                    'categories': [],
                    'price_ranges': [],
                    'priority_distribution': [],
                    'availability_status': [],
                    'recommendations': []
                },
                message='No wishlist items found'
            )
        
        # Category distribution
        categories = wishlist_items.values('course__category').annotate(
            count=Count('id'),
            avg_price=Avg('course__price')
        ).order_by('-count')
        
        # Price range analysis
        price_ranges = [
            {'range': 'Free', 'count': wishlist_items.filter(course__price__isnull=True).count()},
            {'range': '$1-$50', 'count': wishlist_items.filter(course__price__gte=1, course__price__lte=50).count()},
            {'range': '$51-$100', 'count': wishlist_items.filter(course__price__gte=51, course__price__lte=100).count()},
            {'range': '$101-$200', 'count': wishlist_items.filter(course__price__gte=101, course__price__lte=200).count()},
            {'range': '$200+', 'count': wishlist_items.filter(course__price__gt=200).count()},
        ]
        
        # Priority distribution
        priority_distribution = wishlist_items.values('priority').annotate(
            count=Count('id')
        ).order_by('priority')
        
        # Availability status
        available_count = sum(1 for item in wishlist_items if item.is_course_available)
        enrolled_count = sum(1 for item in wishlist_items if item.is_enrolled())
        
        availability_status = [
            {'status': 'Available', 'count': available_count},
            {'status': 'Already Enrolled', 'count': enrolled_count},
            {'status': 'Unavailable', 'count': total_items - available_count - enrolled_count}
        ]
        
        # Generate recommendations based on wishlist
        recommendations = self._generate_wishlist_recommendations(wishlist_items)
        
        analytics_data = {
            'total_items': total_items,
            'categories': list(categories),
            'price_ranges': [pr for pr in price_ranges if pr['count'] > 0],
            'priority_distribution': list(priority_distribution),
            'availability_status': availability_status,
            'recommendations': recommendations,
            'total_estimated_value': sum(
                float(item.course.price or 0) for item in wishlist_items
            ),
            'average_item_price': wishlist_items.aggregate(
                avg_price=Avg('course__price')
            )['avg_price'] or 0
        }
        
        return StandardAPIResponse.success(
            data=analytics_data,
            message='Wishlist analytics retrieved successfully'
        )
    
    @action(detail=False, methods=['post'])
    def bulk_enroll(self, request):
        """Enroll in multiple courses from wishlist"""
        course_ids = request.data.get('course_ids', [])
        
        if not course_ids:
            return StandardAPIResponse.validation_error(
                errors={'course_ids': ['This field is required']},
                message='Course IDs are required'
            )
        
        # Get wishlist items for the specified courses
        wishlist_items = self.get_queryset().filter(course_id__in=course_ids)
        
        enrolled_courses = []
        failed_enrollments = []
        
        for item in wishlist_items:
            try:
                # Check if already enrolled
                if not item.is_enrolled():
                    # Create enrollment
                    enrollment = Enrollment.objects.create(
                        student=request.user,
                        course=item.course,
                        tenant=request.tenant
                    )
                    enrolled_courses.append({
                        'course_id': item.course.id,
                        'course_title': item.course.title,
                        'enrollment_id': enrollment.id
                    })
                    
                    # Remove from wishlist after successful enrollment
                    item.delete()
                else:
                    failed_enrollments.append({
                        'course_id': item.course.id,
                        'course_title': item.course.title,
                        'reason': 'Already enrolled'
                    })
            except Exception as e:
                failed_enrollments.append({
                    'course_id': item.course.id,
                    'course_title': item.course.title,
                    'reason': str(e)
                })
        
        return StandardAPIResponse.success(
            data={
                'enrolled_courses': enrolled_courses,
                'failed_enrollments': failed_enrollments,
                'total_enrolled': len(enrolled_courses),
                'total_failed': len(failed_enrollments)
            },
            message=f'Bulk enrollment completed: {len(enrolled_courses)} successful, {len(failed_enrollments)} failed'
        )
    
    @action(detail=False, methods=['post'])
    def update_notifications(self, request):
        """Update notification preferences for all wishlist items"""
        notify_price_change = request.data.get('notify_price_change')
        notify_course_updates = request.data.get('notify_course_updates')
        notify_enrollment_opening = request.data.get('notify_enrollment_opening')
        
        update_data = {}
        if notify_price_change is not None:
            update_data['notify_price_change'] = notify_price_change
        if notify_course_updates is not None:
            update_data['notify_course_updates'] = notify_course_updates
        if notify_enrollment_opening is not None:
            update_data['notify_enrollment_opening'] = notify_enrollment_opening
        
        if not update_data:
            return StandardAPIResponse.validation_error(
                message='At least one notification preference must be provided'
            )
        
        updated_count = self.get_queryset().update(**update_data)
        
        return StandardAPIResponse.success(
            data={'updated_count': updated_count},
            message=f'Updated notification preferences for {updated_count} wishlist items'
        )
    
    def _generate_wishlist_recommendations(self, wishlist_items):
        """Generate course recommendations based on wishlist items"""
        if not wishlist_items.exists():
            return []
        
        # Get categories from wishlist
        wishlist_categories = wishlist_items.values_list('course__category', flat=True).distinct()
        
        # Find similar courses not in wishlist
        similar_courses = Course.objects.filter(
            category__in=wishlist_categories,
            tenant=self.request.tenant,
            is_public=True
        ).exclude(
            id__in=wishlist_items.values_list('course_id', flat=True)
        ).exclude(
            id__in=Enrollment.objects.filter(
                student=self.request.user,
                tenant=self.request.tenant
            ).values_list('course_id', flat=True)
        ).annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            enrollment_count=Count('enrollments')
        ).order_by('-avg_rating', '-enrollment_count')[:5]
        
        recommendations = []
        for course in similar_courses:
            recommendations.append({
                'course_id': course.id,
                'title': course.title,
                'instructor': course.instructor.get_full_name(),
                'category': course.category,
                'price': float(course.price or 0),
                'average_rating': round(course.avg_rating or 0, 2),
                'enrollment_count': course.enrollment_count,
                'reason': f'Similar to courses in your {course.category} wishlist'
            })
        
        return recommendations


class RecommendationViewSet(StandardViewSetMixin, viewsets.ViewSet):
    """ViewSet for course recommendation system with advanced algorithms"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get personalized course recommendations"""
        from .services import RecommendationService
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 10))
        algorithm = request.query_params.get('algorithm', 'hybrid')
        context = request.query_params.get('context', 'general')  # homepage, course_detail, etc.
        
        # Validate algorithm
        valid_algorithms = ['collaborative', 'content_based', 'popularity', 'hybrid']
        if algorithm not in valid_algorithms:
            algorithm = 'hybrid'
        
        try:
            # Get recommendations
            recommendations = RecommendationService.get_personalized_recommendations(
                user=request.user,
                tenant=request.tenant,
                limit=limit,
                algorithm=algorithm
            )
            
            # Format response
            recommendations_data = []
            for i, rec in enumerate(recommendations):
                course = rec['course']
                
                # Serialize course data
                from .serializers import CourseSerializer
                course_data = CourseSerializer(course, context={'request': request}).data
                
                # Add recommendation metadata
                course_data.update({
                    'recommendation_score': rec['score'],
                    'recommendation_reason': rec['reason'],
                    'recommendation_algorithm': rec['algorithm'],
                    'recommendation_metadata': rec.get('metadata', {}),
                    'position_in_list': i + 1
                })
                
                recommendations_data.append(course_data)
                
                # Track view interaction
                RecommendationService.track_recommendation_interaction(
                    user=request.user,
                    course_id=course.id,
                    interaction_type='view',
                    tenant=request.tenant
                )
            
            # Add user context
            user_context = self._get_user_context(request.user, request.tenant)
            
            return StandardAPIResponse.success(
                data={
                    'recommendations': recommendations_data,
                    'user_context': user_context,
                    'algorithm_used': algorithm,
                    'context': context,
                    'total_count': len(recommendations_data),
                    'generated_at': timezone.now().isoformat()
                },
                message='Personalized recommendations generated successfully'
            )
            
        except Exception as e:
            return StandardAPIResponse.error(
                message='Failed to generate recommendations',
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def similar_courses(self, request):
        """Get courses similar to a specific course"""
        course_id = request.query_params.get('course_id')
        limit = int(request.query_params.get('limit', 5))
        
        if not course_id:
            return StandardAPIResponse.validation_error(
                errors={'course_id': ['This parameter is required']},
                message='Course ID is required'
            )
        
        try:
            # Get the reference course
            reference_course = Course.objects.get(
                id=course_id,
                tenant=request.tenant
            )
            
            # Find similar courses
            similar_courses = Course.objects.filter(
                tenant=request.tenant,
                is_public=True,
                category=reference_course.category
            ).exclude(
                id=course_id
            ).exclude(
                id__in=Enrollment.objects.filter(
                    student=request.user,
                    tenant=request.tenant
                ).values_list('course_id', flat=True)
            ).annotate(
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
                enrollment_count=Count('enrollments')
            ).order_by('-avg_rating', '-enrollment_count')[:limit]
            
            # Format response
            from .serializers import CourseSerializer
            similar_courses_data = []
            
            for course in similar_courses:
                course_data = CourseSerializer(course, context={'request': request}).data
                course_data.update({
                    'similarity_reason': f"Similar {course.category} course",
                    'similarity_score': 0.8  # Could be enhanced with more sophisticated similarity calculation
                })
                similar_courses_data.append(course_data)
            
            return StandardAPIResponse.success(
                data={
                    'similar_courses': similar_courses_data,
                    'reference_course': CourseSerializer(reference_course, context={'request': request}).data,
                    'total_count': len(similar_courses_data)
                },
                message='Similar courses retrieved successfully'
            )
            
        except Course.DoesNotExist:
            return StandardAPIResponse.not_found(
                message='Reference course not found'
            )
        except Exception as e:
            return StandardAPIResponse.error(
                message='Failed to get similar courses',
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def track_interaction(self, request):
        """Track user interaction with a recommendation"""
        from .services import RecommendationService
        
        course_id = request.data.get('course_id')
        interaction_type = request.data.get('interaction_type')
        algorithm_used = request.data.get('algorithm_used')
        recommendation_score = request.data.get('recommendation_score')
        context = request.data.get('context', 'general')
        position = request.data.get('position_in_list')
        
        if not course_id or not interaction_type:
            return StandardAPIResponse.validation_error(
                errors={
                    'course_id': ['This field is required'] if not course_id else [],
                    'interaction_type': ['This field is required'] if not interaction_type else []
                },
                message='Course ID and interaction type are required'
            )
        
        # Validate interaction type
        valid_interactions = ['view', 'click', 'wishlist', 'enroll', 'dismiss']
        if interaction_type not in valid_interactions:
            return StandardAPIResponse.validation_error(
                errors={'interaction_type': [f'Must be one of: {", ".join(valid_interactions)}']},
                message='Invalid interaction type'
            )
        
        try:
            # Track the interaction
            from .models import RecommendationInteraction
            
            interaction = RecommendationInteraction.objects.create(
                user=request.user,
                course_id=course_id,
                interaction_type=interaction_type,
                algorithm_used=algorithm_used,
                recommendation_score=recommendation_score,
                page_context=context,
                position_in_list=position,
                tenant=request.tenant
            )
            
            return StandardAPIResponse.success(
                data={'interaction_id': interaction.id},
                message='Interaction tracked successfully'
            )
            
        except Exception as e:
            return StandardAPIResponse.error(
                message='Failed to track interaction',
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get recommendation system analytics (admin only)"""
        if not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message='Only administrators can access recommendation analytics'
            )
        
        from .services import RecommendationService
        
        days = int(request.query_params.get('days', 30))
        
        try:
            analytics = RecommendationService.get_recommendation_analytics(
                tenant=request.tenant,
                days=days
            )
            
            return StandardAPIResponse.success(
                data=analytics,
                message='Recommendation analytics retrieved successfully'
            )
            
        except Exception as e:
            return StandardAPIResponse.error(
                message='Failed to get recommendation analytics',
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending courses based on recent activity"""
        limit = int(request.query_params.get('limit', 10))
        days = int(request.query_params.get('days', 7))
        
        try:
            from datetime import timedelta
            
            # Get courses with high recent activity
            since_date = timezone.now() - timedelta(days=days)
            
            trending_courses = Course.objects.filter(
                tenant=request.tenant,
                is_public=True,
                created_at__gte=since_date - timedelta(days=30)  # Only consider relatively new courses
            ).annotate(
                recent_enrollments=Count(
                    'enrollments',
                    filter=Q(enrollments__enrolled_at__gte=since_date)
                ),
                recent_views=Count(
                    'recommendation_interactions',
                    filter=Q(
                        recommendation_interactions__interaction_type='view',
                        recommendation_interactions__created_at__gte=since_date
                    )
                ),
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
            ).filter(
                recent_enrollments__gte=1
            ).order_by('-recent_enrollments', '-recent_views', '-avg_rating')[:limit]
            
            # Format response
            from .serializers import CourseSerializer
            trending_data = []
            
            for course in trending_courses:
                course_data = CourseSerializer(course, context={'request': request}).data
                course_data.update({
                    'trending_score': course.recent_enrollments + (course.recent_views * 0.1),
                    'recent_enrollments': course.recent_enrollments,
                    'recent_views': course.recent_views,
                    'trending_reason': f"{course.recent_enrollments} new enrollments in the last {days} days"
                })
                trending_data.append(course_data)
            
            return StandardAPIResponse.success(
                data={
                    'trending_courses': trending_data,
                    'period_days': days,
                    'total_count': len(trending_data)
                },
                message='Trending courses retrieved successfully'
            )
            
        except Exception as e:
            return StandardAPIResponse.error(
                message='Failed to get trending courses',
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_user_context(self, user, tenant):
        """Get user context for recommendations"""
        from .models import Enrollment, Wishlist
        
        enrollments = Enrollment.objects.filter(student=user, tenant=tenant)
        wishlist_items = Wishlist.objects.filter(user=user, tenant=tenant)
        
        # Analyze user preferences
        enrolled_categories = enrollments.values_list('course__category', flat=True)
        wishlist_categories = wishlist_items.values_list('course__category', flat=True)
        
        from collections import Counter
        all_categories = list(enrolled_categories) + list(wishlist_categories)
        category_preferences = Counter(all_categories)
        
        # Determine user skill level
        completed_courses = enrollments.filter(status='completed').count()
        if completed_courses >= 10:
            skill_level = 'advanced'
        elif completed_courses >= 3:
            skill_level = 'intermediate'
        else:
            skill_level = 'beginner'
        
        return {
            'total_enrollments': enrollments.count(),
            'completed_courses': completed_courses,
            'wishlist_items': wishlist_items.count(),
            'preferred_categories': dict(category_preferences.most_common(5)),
            'skill_level': skill_level,
            'is_new_user': enrollments.count() == 0
        }