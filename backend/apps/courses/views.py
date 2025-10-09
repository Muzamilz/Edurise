from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Avg, Q
from django.utils import timezone
from .models import Course, LiveClass, CourseModule, CourseReview, CourseLicense, Enrollment
from .serializers import (
    CourseSerializer, CourseDetailSerializer, LiveClassSerializer,
    CourseModuleSerializer, CourseReviewSerializer, CourseLicenseSerializer,
    EnrollmentSerializer
)
from .filters import CourseFilter, LiveClassFilter, EnrollmentFilter
from .services import CourseService, EnrollmentService


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for Course model"""
    
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'title', 'price']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter courses by tenant"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Course.objects.filter(tenant=self.request.tenant)
        return Course.objects.none()
    
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
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """Enroll in a course"""
        course = self.get_object()
        
        # Check if already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {'error': 'Already enrolled in this course'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create enrollment
        enrollment = Enrollment.objects.create(
            student=request.user,
            course=course,
            tenant=request.tenant
        )
        
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get enrolled students for a course"""
        course = self.get_object()
        
        # Check if user is instructor or admin
        if course.instructor != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        enrollments = course.enrollments.all()
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get course categories with counts"""
        categories = Course.objects.filter(
            tenant=request.tenant if hasattr(request, 'tenant') else None
        ).values('category').annotate(
            count=Count('id'),
            avg_rating=Avg('reviews__rating')
        ).order_by('category')
        
        return Response(categories)
    
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
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        """Get courses where user is instructor"""
        if not request.user.is_teacher:
            return Response(
                {'error': 'Only teachers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
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
        """Get recommended courses for the user"""
        recommendations = CourseService.get_recommended_courses(
            user=request.user,
            tenant=request.tenant,
            limit=10
        )
        
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def instructor_analytics(self, request):
        """Get analytics for instructor's courses"""
        if not request.user.is_teacher:
            return Response(
                {'error': 'Only teachers can access analytics'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        analytics = CourseService.get_course_analytics_for_instructor(
            instructor=request.user,
            tenant=request.tenant
        )
        
        return Response(analytics)


class LiveClassViewSet(viewsets.ModelViewSet):
    """ViewSet for LiveClass model with Zoom integration"""
    
    serializer_class = LiveClassSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = LiveClassFilter
    ordering_fields = ['scheduled_at', 'created_at']
    ordering = ['scheduled_at']
    
    def get_queryset(self):
        """Filter live classes by tenant"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return LiveClass.objects.filter(course__tenant=self.request.tenant)
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
            zoom_service.create_meeting(live_class)
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
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from apps.classes.services import ZoomService
            zoom_service = ZoomService()
            meeting_info = zoom_service.create_meeting(live_class)
            
            return Response({
                'message': 'Zoom meeting created successfully',
                'meeting_info': {
                    'meeting_id': meeting_info['id'],
                    'join_url': meeting_info['join_url'],
                    'start_url': meeting_info['start_url'],
                    'password': meeting_info.get('password', '')
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to create Zoom meeting: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def start_class(self, request, pk=None):
        """Start the live class (update status to live)"""
        live_class = self.get_object()
        
        # Check permissions
        if live_class.course.instructor != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if live_class.status != 'scheduled':
            return Response(
                {'error': 'Class can only be started if it is scheduled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        live_class.status = 'live'
        live_class.save()
        
        return Response({
            'message': 'Class started successfully',
            'start_url': live_class.start_url,
            'join_url': live_class.join_url
        })
    
    @action(detail=True, methods=['post'])
    def end_class(self, request, pk=None):
        """End the live class (update status to completed)"""
        live_class = self.get_object()
        
        # Check permissions
        if live_class.course.instructor != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if live_class.status != 'live':
            return Response(
                {'error': 'Class can only be ended if it is currently live'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        live_class.status = 'completed'
        live_class.save()
        
        return Response({'message': 'Class ended successfully'})
    
    @action(detail=True, methods=['get'])
    def attendance_report(self, request, pk=None):
        """Get detailed attendance report for the live class"""
        live_class = self.get_object()
        
        # Check permissions
        if live_class.course.instructor != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from apps.classes.services import AttendanceService
            report = AttendanceService.get_class_analytics_report(live_class)
            return Response(report)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
            return Response(
                {'error': 'You must be enrolled in this course to join the class'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not live_class.join_url:
            return Response(
                {'error': 'Zoom meeting not yet created for this class'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'join_url': live_class.join_url,
            'password': live_class.password,
            'meeting_id': live_class.zoom_meeting_id,
            'class_title': live_class.title,
            'scheduled_at': live_class.scheduled_at,
            'duration_minutes': live_class.duration_minutes,
            'status': live_class.status
        })
    
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
        return Response(serializer.data)
    
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