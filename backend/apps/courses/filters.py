import django_filters
from django.db import models
from .models import Course, LiveClass, Enrollment, CourseCategory


class CourseFilter(django_filters.FilterSet):
    """Filter for Course model"""
    
    title = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(queryset=None)  # Will be set dynamically
    difficulty_level = django_filters.ChoiceFilter(choices=Course.DIFFICULTY_CHOICES)
    is_public = django_filters.BooleanFilter()
    instructor = django_filters.CharFilter(field_name='instructor__email', lookup_expr='icontains')
    instructor_name = django_filters.CharFilter(method='filter_instructor_name')
    
    # Price range filters
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    is_free = django_filters.BooleanFilter(method='filter_free_courses')
    
    # Duration filters
    min_duration = django_filters.NumberFilter(field_name='duration_weeks', lookup_expr='gte')
    max_duration = django_filters.NumberFilter(field_name='duration_weeks', lookup_expr='lte')
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Rating filter
    min_rating = django_filters.NumberFilter(method='filter_min_rating')
    
    # Enrollment filters
    has_spots = django_filters.BooleanFilter(method='filter_has_spots')
    
    # Search across multiple fields
    search = django_filters.CharFilter(method='filter_search')
    
    # Tags filter
    tags = django_filters.CharFilter(method='filter_tags')
    
    class Meta:
        model = Course
        fields = [
            'title', 'category', 'difficulty_level', 'is_public', 
            'instructor', 'instructor_name', 'min_price', 'max_price', 
            'is_free', 'min_duration', 'max_duration', 'created_after', 
            'created_before', 'min_rating', 'has_spots', 'search', 'tags'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set category queryset to active categories
        self.filters['category'].queryset = CourseCategory.objects.filter(is_active=True)
    
    def filter_search(self, queryset, name, value):
        """Search across title, description, and tags"""
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(tags__icontains=value)
        )
    
    def filter_instructor_name(self, queryset, name, value):
        """Filter by instructor's full name"""
        return queryset.filter(
            models.Q(instructor__first_name__icontains=value) |
            models.Q(instructor__last_name__icontains=value)
        )
    
    def filter_free_courses(self, queryset, name, value):
        """Filter free courses"""
        if value:
            return queryset.filter(models.Q(price__isnull=True) | models.Q(price=0))
        else:
            return queryset.filter(price__gt=0)
    
    def filter_min_rating(self, queryset, name, value):
        """Filter by minimum average rating"""
        return queryset.annotate(
            avg_rating=models.Avg('reviews__rating')
        ).filter(avg_rating__gte=value)
    
    def filter_has_spots(self, queryset, name, value):
        """Filter courses that have available spots"""
        if value:
            return queryset.annotate(
                enrollment_count=models.Count('enrollments')
            ).filter(
                models.Q(max_students__isnull=True) |
                models.Q(enrollment_count__lt=models.F('max_students'))
            )
        return queryset
    
    def filter_tags(self, queryset, name, value):
        """Filter by tags (comma-separated)"""
        tags = [tag.strip() for tag in value.split(',')]
        query = models.Q()
        for tag in tags:
            query |= models.Q(tags__icontains=tag)
        return queryset.filter(query)


class LiveClassFilter(django_filters.FilterSet):
    """Filter for LiveClass model"""
    
    course = django_filters.UUIDFilter(field_name='course__id')
    course_title = django_filters.CharFilter(field_name='course__title', lookup_expr='icontains')
    instructor = django_filters.UUIDFilter(field_name='course__instructor__id')
    status = django_filters.ChoiceFilter(choices=LiveClass.STATUS_CHOICES)
    title = django_filters.CharFilter(lookup_expr='icontains')
    
    # Date filters
    scheduled_after = django_filters.DateTimeFilter(field_name='scheduled_at', lookup_expr='gte')
    scheduled_before = django_filters.DateTimeFilter(field_name='scheduled_at', lookup_expr='lte')
    scheduled_today = django_filters.BooleanFilter(method='filter_scheduled_today')
    scheduled_this_week = django_filters.BooleanFilter(method='filter_scheduled_this_week')
    
    # Duration filters
    min_duration = django_filters.NumberFilter(field_name='duration_minutes', lookup_expr='gte')
    max_duration = django_filters.NumberFilter(field_name='duration_minutes', lookup_expr='lte')
    
    # Zoom integration filters
    has_zoom_meeting = django_filters.BooleanFilter(method='filter_has_zoom_meeting')
    
    # Search filter
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = LiveClass
        fields = [
            'course', 'course_title', 'instructor', 'status', 'title',
            'scheduled_after', 'scheduled_before', 'scheduled_today', 'scheduled_this_week',
            'min_duration', 'max_duration', 'has_zoom_meeting', 'search'
        ]
    
    def filter_scheduled_today(self, queryset, name, value):
        """Filter classes scheduled for today"""
        if value:
            from django.utils import timezone
            today = timezone.now().date()
            return queryset.filter(scheduled_at__date=today)
        return queryset
    
    def filter_scheduled_this_week(self, queryset, name, value):
        """Filter classes scheduled for this week"""
        if value:
            from django.utils import timezone
            from datetime import timedelta
            now = timezone.now()
            week_start = now - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=6)
            return queryset.filter(
                scheduled_at__gte=week_start.replace(hour=0, minute=0, second=0, microsecond=0),
                scheduled_at__lte=week_end.replace(hour=23, minute=59, second=59, microsecond=999999)
            )
        return queryset
    
    def filter_has_zoom_meeting(self, queryset, name, value):
        """Filter classes that have Zoom meetings created"""
        if value:
            return queryset.exclude(zoom_meeting_id='')
        else:
            return queryset.filter(zoom_meeting_id='')
    
    def filter_search(self, queryset, name, value):
        """Search across title, description, and course title"""
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(course__title__icontains=value)
        )


class EnrollmentFilter(django_filters.FilterSet):
    """Filter for Enrollment model"""
    
    course = django_filters.UUIDFilter(field_name='course__id')
    student = django_filters.UUIDFilter(field_name='student__id')
    status = django_filters.ChoiceFilter(choices=Enrollment.STATUS_CHOICES)
    
    # Progress filters
    min_progress = django_filters.NumberFilter(field_name='progress_percentage', lookup_expr='gte')
    max_progress = django_filters.NumberFilter(field_name='progress_percentage', lookup_expr='lte')
    
    # Date filters
    enrolled_after = django_filters.DateTimeFilter(field_name='enrolled_at', lookup_expr='gte')
    enrolled_before = django_filters.DateTimeFilter(field_name='enrolled_at', lookup_expr='lte')
    completed_after = django_filters.DateTimeFilter(field_name='completed_at', lookup_expr='gte')
    completed_before = django_filters.DateTimeFilter(field_name='completed_at', lookup_expr='lte')
    
    class Meta:
        model = Enrollment
        fields = [
            'course', 'student', 'status', 'min_progress', 'max_progress',
            'enrolled_after', 'enrolled_before', 'completed_after', 'completed_before'
        ]