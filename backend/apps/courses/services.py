from django.db.models import Count, Avg, Q
from django.utils import timezone
from .models import Course, Enrollment, CourseReview, CourseModule


class CourseService:
    """Service class for course-related operations"""
    
    @staticmethod
    def get_course_statistics(course):
        """Get comprehensive statistics for a course"""
        enrollments = course.enrollments.all()
        reviews = course.reviews.filter(is_approved=True)
        
        return {
            'total_enrollments': enrollments.count(),
            'active_enrollments': enrollments.filter(status='active').count(),
            'completed_enrollments': enrollments.filter(status='completed').count(),
            'completion_rate': (
                enrollments.filter(status='completed').count() / 
                max(enrollments.count(), 1) * 100
            ),
            'average_progress': enrollments.aggregate(
                avg_progress=Avg('progress_percentage')
            )['avg_progress'] or 0,
            'total_reviews': reviews.count(),
            'average_rating': reviews.aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0,
            'rating_distribution': {
                '5_star': reviews.filter(rating=5).count(),
                '4_star': reviews.filter(rating=4).count(),
                '3_star': reviews.filter(rating=3).count(),
                '2_star': reviews.filter(rating=2).count(),
                '1_star': reviews.filter(rating=1).count(),
            }
        }
    
    @staticmethod
    def get_recommended_courses(user, tenant, limit=10):
        """Get recommended courses for a user based on their enrollments and preferences"""
        # Get user's enrolled courses
        enrolled_courses = Course.objects.filter(
            enrollments__student=user,
            tenant=tenant
        )
        
        if not enrolled_courses.exists():
            # New user - return popular courses
            return Course.objects.filter(
                tenant=tenant,
                is_public=True
            ).annotate(
                enrollment_count=Count('enrollments')
            ).order_by('-enrollment_count')[:limit]
        
        # Get categories and tags from enrolled courses
        enrolled_categories = enrolled_courses.values_list('category', flat=True).distinct()
        enrolled_tags = []
        for course in enrolled_courses:
            enrolled_tags.extend(course.tags)
        
        # Find similar courses
        recommended = Course.objects.filter(
            tenant=tenant,
            is_public=True
        ).exclude(
            id__in=enrolled_courses.values_list('id', flat=True)
        ).annotate(
            enrollment_count=Count('enrollments'),
            avg_rating=Avg('reviews__rating')
        )
        
        # Score courses based on similarity
        category_q = Q(category__in=enrolled_categories)
        tag_q = Q()
        for tag in set(enrolled_tags):
            tag_q |= Q(tags__icontains=tag)
        
        # Prioritize courses with similar categories or tags
        recommended = recommended.filter(category_q | tag_q).order_by(
            '-avg_rating', '-enrollment_count'
        )[:limit]
        
        return recommended
    
    @staticmethod
    def calculate_course_progress(enrollment):
        """Calculate detailed progress for a course enrollment"""
        course = enrollment.course
        modules = course.modules.filter(is_published=True).order_by('order')
        
        if not modules.exists():
            return {
                'overall_progress': enrollment.progress_percentage,
                'modules_completed': 0,
                'total_modules': 0,
                'current_module': None,
                'next_module': None
            }
        
        # This is a simplified calculation
        # In a real system, you'd track module completion separately
        total_modules = modules.count()
        completed_modules = int((enrollment.progress_percentage / 100) * total_modules)
        
        current_module = None
        next_module = None
        
        if completed_modules < total_modules:
            current_module = modules[completed_modules]
            if completed_modules + 1 < total_modules:
                next_module = modules[completed_modules + 1]
        
        return {
            'overall_progress': enrollment.progress_percentage,
            'modules_completed': completed_modules,
            'total_modules': total_modules,
            'current_module': current_module,
            'next_module': next_module
        }
    
    @staticmethod
    def can_enroll_in_course(user, course):
        """Check if a user can enroll in a course"""
        # Check if already enrolled
        if Enrollment.objects.filter(student=user, course=course).exists():
            return False, "Already enrolled in this course"
        
        # Check if course has available spots
        if course.max_students:
            current_enrollments = course.enrollments.filter(
                status__in=['active', 'completed']
            ).count()
            if current_enrollments >= course.max_students:
                return False, "Course is full"
        
        # Check if user has required permissions (for private courses)
        if not course.is_public:
            # Add logic for private course access
            pass
        
        return True, "Can enroll"
    
    @staticmethod
    def get_course_analytics_for_instructor(instructor, tenant):
        """Get analytics for all courses by an instructor"""
        courses = Course.objects.filter(
            instructor=instructor,
            tenant=tenant
        )
        
        total_enrollments = Enrollment.objects.filter(
            course__in=courses
        )
        
        return {
            'total_courses': courses.count(),
            'published_courses': courses.filter(is_public=True).count(),
            'total_students': total_enrollments.values('student').distinct().count(),
            'total_enrollments': total_enrollments.count(),
            'completed_enrollments': total_enrollments.filter(status='completed').count(),
            'average_rating': CourseReview.objects.filter(
                course__in=courses,
                is_approved=True
            ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0,
            'total_revenue': sum(
                float(course.price or 0) * course.enrollments.count()
                for course in courses
            ),
            'courses_by_category': courses.values('category').annotate(
                count=Count('id')
            ).order_by('-count')
        }
    
    @staticmethod
    def search_courses(query, tenant, filters=None):
        """Advanced course search with ranking"""
        courses = Course.objects.filter(tenant=tenant)
        
        if query:
            # Search in title (highest priority)
            title_matches = courses.filter(title__icontains=query)
            
            # Search in description (medium priority)
            description_matches = courses.filter(description__icontains=query)
            
            # Search in tags (lower priority)
            tag_matches = courses.filter(tags__icontains=query)
            
            # Combine results with ranking
            courses = (title_matches | description_matches | tag_matches).distinct()
        
        # Apply additional filters
        if filters:
            if 'category' in filters:
                courses = courses.filter(category=filters['category'])
            if 'difficulty_level' in filters:
                courses = courses.filter(difficulty_level=filters['difficulty_level'])
            if 'min_price' in filters:
                courses = courses.filter(price__gte=filters['min_price'])
            if 'max_price' in filters:
                courses = courses.filter(price__lte=filters['max_price'])
        
        # Add annotations for sorting
        courses = courses.annotate(
            enrollment_count=Count('enrollments'),
            avg_rating=Avg('reviews__rating')
        )
        
        return courses.order_by('-avg_rating', '-enrollment_count')


class EnrollmentService:
    """Service class for enrollment-related operations"""
    
    @staticmethod
    def enroll_student(student, course, tenant):
        """Enroll a student in a course with validation"""
        can_enroll, message = CourseService.can_enroll_in_course(student, course)
        
        if not can_enroll:
            raise ValueError(message)
        
        enrollment = Enrollment.objects.create(
            student=student,
            course=course,
            tenant=tenant
        )
        
        return enrollment
    
    @staticmethod
    def update_progress(enrollment, progress_percentage):
        """Update enrollment progress with validation"""
        progress_percentage = max(0, min(100, progress_percentage))
        enrollment.progress_percentage = progress_percentage
        
        # Auto-complete if 100%
        if progress_percentage == 100 and enrollment.status != 'completed':
            enrollment.status = 'completed'
            enrollment.completed_at = timezone.now()
        
        enrollment.save()
        return enrollment
    
    @staticmethod
    def get_student_dashboard_data(student, tenant):
        """Get dashboard data for a student"""
        enrollments = Enrollment.objects.filter(
            student=student,
            tenant=tenant
        ).select_related('course')
        
        return {
            'total_enrollments': enrollments.count(),
            'active_courses': enrollments.filter(status='active').count(),
            'completed_courses': enrollments.filter(status='completed').count(),
            'average_progress': enrollments.aggregate(
                avg_progress=Avg('progress_percentage')
            )['avg_progress'] or 0,
            'recent_enrollments': enrollments.order_by('-enrolled_at')[:5],
            'courses_in_progress': enrollments.filter(
                status='active',
                progress_percentage__lt=100
            ).order_by('-last_accessed')[:5]
        }