import django_filters
from django.db.models import Q, F
from django.utils import timezone
from .models import Assignment, Submission, Certificate, CourseProgress


class AssignmentFilter(django_filters.FilterSet):
    """Filter for Assignment model"""
    
    # Basic filters
    course = django_filters.UUIDFilter(field_name='course__id')
    course_title = django_filters.CharFilter(field_name='course__title', lookup_expr='icontains')
    instructor = django_filters.UUIDFilter(field_name='course__instructor__id')
    assignment_type = django_filters.ChoiceFilter(choices=Assignment.ASSIGNMENT_TYPE_CHOICES)
    status = django_filters.ChoiceFilter(choices=Assignment.STATUS_CHOICES)
    
    # Date filters
    due_date_from = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='gte')
    due_date_to = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='lte')
    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Score filters
    max_score_min = django_filters.NumberFilter(field_name='max_score', lookup_expr='gte')
    max_score_max = django_filters.NumberFilter(field_name='max_score', lookup_expr='lte')
    
    # Boolean filters
    is_required = django_filters.BooleanFilter()
    late_submission_allowed = django_filters.BooleanFilter()
    allow_file_upload = django_filters.BooleanFilter()
    
    # Custom filters
    is_overdue = django_filters.BooleanFilter(method='filter_overdue')
    upcoming = django_filters.BooleanFilter(method='filter_upcoming')
    
    class Meta:
        model = Assignment
        fields = [
            'course', 'course_title', 'instructor', 'assignment_type', 'status',
            'due_date_from', 'due_date_to', 'created_from', 'created_to',
            'max_score_min', 'max_score_max', 'is_required', 'late_submission_allowed',
            'allow_file_upload', 'is_overdue', 'upcoming'
        ]
    
    def filter_overdue(self, queryset, name, value):
        """Filter overdue assignments"""
        now = timezone.now()
        if value:
            return queryset.filter(due_date__lt=now)
        else:
            return queryset.filter(due_date__gte=now)
    
    def filter_upcoming(self, queryset, name, value):
        """Filter upcoming assignments (due within next 7 days)"""
        now = timezone.now()
        week_from_now = now + timezone.timedelta(days=7)
        
        if value:
            return queryset.filter(due_date__gte=now, due_date__lte=week_from_now)
        else:
            return queryset.exclude(due_date__gte=now, due_date__lte=week_from_now)


class SubmissionFilter(django_filters.FilterSet):
    """Filter for Submission model"""
    
    # Basic filters
    assignment = django_filters.UUIDFilter(field_name='assignment__id')
    assignment_title = django_filters.CharFilter(field_name='assignment__title', lookup_expr='icontains')
    student = django_filters.UUIDFilter(field_name='student__id')
    student_email = django_filters.CharFilter(field_name='student__email', lookup_expr='icontains')
    graded_by = django_filters.UUIDFilter(field_name='graded_by__id')
    status = django_filters.ChoiceFilter(choices=Submission.STATUS_CHOICES)
    
    # Date filters
    submitted_from = django_filters.DateTimeFilter(field_name='submitted_at', lookup_expr='gte')
    submitted_to = django_filters.DateTimeFilter(field_name='submitted_at', lookup_expr='lte')
    graded_from = django_filters.DateTimeFilter(field_name='graded_at', lookup_expr='gte')
    graded_to = django_filters.DateTimeFilter(field_name='graded_at', lookup_expr='lte')
    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Score filters
    score_min = django_filters.NumberFilter(field_name='score', lookup_expr='gte')
    score_max = django_filters.NumberFilter(field_name='score', lookup_expr='lte')
    
    # Boolean filters
    is_graded = django_filters.BooleanFilter()
    is_late = django_filters.BooleanFilter()
    
    # Custom filters
    is_passing = django_filters.BooleanFilter(method='filter_passing')
    needs_grading = django_filters.BooleanFilter(method='filter_needs_grading')
    
    class Meta:
        model = Submission
        fields = [
            'assignment', 'assignment_title', 'student', 'student_email', 'graded_by',
            'status', 'submitted_from', 'submitted_to', 'graded_from', 'graded_to',
            'created_from', 'created_to', 'score_min', 'score_max', 'is_graded',
            'is_late', 'is_passing', 'needs_grading'
        ]
    
    def filter_passing(self, queryset, name, value):
        """Filter passing submissions"""
        if value:
            return queryset.filter(
                is_graded=True,
                score__gte=F('assignment__passing_score')
            )
        else:
            return queryset.filter(
                Q(is_graded=False) | Q(score__lt=F('assignment__passing_score'))
            )
    
    def filter_needs_grading(self, queryset, name, value):
        """Filter submissions that need grading"""
        if value:
            return queryset.filter(
                is_graded=False,
                status__in=['submitted', 'late']
            )
        else:
            return queryset.exclude(
                is_graded=False,
                status__in=['submitted', 'late']
            )


class CertificateFilter(django_filters.FilterSet):
    """Filter for Certificate model"""
    
    # Basic filters
    student = django_filters.UUIDFilter(field_name='student__id')
    student_email = django_filters.CharFilter(field_name='student__email', lookup_expr='icontains')
    course = django_filters.UUIDFilter(field_name='course__id')
    course_title = django_filters.CharFilter(field_name='course__title', lookup_expr='icontains')
    instructor = django_filters.UUIDFilter(field_name='course__instructor__id')
    certificate_type = django_filters.ChoiceFilter(choices=Certificate.CERTIFICATE_TYPE_CHOICES)
    status = django_filters.ChoiceFilter(choices=Certificate.STATUS_CHOICES)
    certificate_number = django_filters.CharFilter(lookup_expr='icontains')
    
    # Date filters
    completion_date_from = django_filters.DateTimeFilter(field_name='completion_date', lookup_expr='gte')
    completion_date_to = django_filters.DateTimeFilter(field_name='completion_date', lookup_expr='lte')
    issued_from = django_filters.DateTimeFilter(field_name='issued_at', lookup_expr='gte')
    issued_to = django_filters.DateTimeFilter(field_name='issued_at', lookup_expr='lte')
    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Grade filters
    final_grade_min = django_filters.NumberFilter(field_name='final_grade', lookup_expr='gte')
    final_grade_max = django_filters.NumberFilter(field_name='final_grade', lookup_expr='lte')
    
    # Custom filters
    is_valid = django_filters.BooleanFilter(method='filter_valid')
    
    class Meta:
        model = Certificate
        fields = [
            'student', 'student_email', 'course', 'course_title', 'instructor',
            'certificate_type', 'status', 'certificate_number', 'completion_date_from',
            'completion_date_to', 'issued_from', 'issued_to', 'created_from',
            'created_to', 'final_grade_min', 'final_grade_max', 'is_valid'
        ]
    
    def filter_valid(self, queryset, name, value):
        """Filter valid certificates"""
        if value:
            return queryset.filter(status='issued')
        else:
            return queryset.exclude(status='issued')


class CourseProgressFilter(django_filters.FilterSet):
    """Filter for CourseProgress model"""
    
    # Basic filters
    student = django_filters.UUIDFilter(field_name='student__id')
    student_email = django_filters.CharFilter(field_name='student__email', lookup_expr='icontains')
    course = django_filters.UUIDFilter(field_name='course__id')
    course_title = django_filters.CharFilter(field_name='course__title', lookup_expr='icontains')
    instructor = django_filters.UUIDFilter(field_name='course__instructor__id')
    
    # Progress filters
    progress_min = django_filters.NumberFilter(field_name='overall_progress_percentage', lookup_expr='gte')
    progress_max = django_filters.NumberFilter(field_name='overall_progress_percentage', lookup_expr='lte')
    assignment_score_min = django_filters.NumberFilter(field_name='assignment_average_score', lookup_expr='gte')
    assignment_score_max = django_filters.NumberFilter(field_name='assignment_average_score', lookup_expr='lte')
    attendance_min = django_filters.NumberFilter(field_name='attendance_percentage', lookup_expr='gte')
    attendance_max = django_filters.NumberFilter(field_name='attendance_percentage', lookup_expr='lte')
    
    # Boolean filters
    is_completed = django_filters.BooleanFilter()
    completion_requirements_met = django_filters.BooleanFilter()
    
    # Date filters
    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_from = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_to = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    completed_from = django_filters.DateTimeFilter(field_name='completed_at', lookup_expr='gte')
    completed_to = django_filters.DateTimeFilter(field_name='completed_at', lookup_expr='lte')
    
    # Custom filters
    at_risk = django_filters.BooleanFilter(method='filter_at_risk')
    high_performers = django_filters.BooleanFilter(method='filter_high_performers')
    
    class Meta:
        model = CourseProgress
        fields = [
            'student', 'student_email', 'course', 'course_title', 'instructor',
            'progress_min', 'progress_max', 'assignment_score_min', 'assignment_score_max',
            'attendance_min', 'attendance_max', 'is_completed', 'completion_requirements_met',
            'created_from', 'created_to', 'updated_from', 'updated_to',
            'completed_from', 'completed_to', 'at_risk', 'high_performers'
        ]
    
    def filter_at_risk(self, queryset, name, value):
        """Filter students at risk (low progress or low assignment scores)"""
        if value:
            return queryset.filter(
                Q(overall_progress_percentage__lt=50) |
                Q(assignment_average_score__lt=60)
            )
        else:
            return queryset.exclude(
                Q(overall_progress_percentage__lt=50) |
                Q(assignment_average_score__lt=60)
            )
    
    def filter_high_performers(self, queryset, name, value):
        """Filter high-performing students"""
        if value:
            return queryset.filter(
                overall_progress_percentage__gte=80,
                assignment_average_score__gte=85
            )
        else:
            return queryset.exclude(
                overall_progress_percentage__gte=80,
                assignment_average_score__gte=85
            )