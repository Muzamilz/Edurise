from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Assignment, Submission, Certificate, CourseProgress


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Admin interface for Assignment model"""
    
    list_display = [
        'title', 'course', 'instructor_name', 'assignment_type', 'status',
        'due_date', 'max_score', 'is_required', 'submission_count', 'created_at'
    ]
    list_filter = [
        'assignment_type', 'status', 'is_required', 'late_submission_allowed',
        'allow_file_upload', 'created_at', 'due_date'
    ]
    search_fields = ['title', 'description', 'course__title', 'course__instructor__email']
    readonly_fields = ['created_at', 'updated_at', 'published_at', 'submission_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'description', 'instructions')
        }),
        ('Assignment Settings', {
            'fields': (
                'assignment_type', 'max_score', 'passing_score', 'weight_percentage',
                'is_required', 'status'
            )
        }),
        ('File Upload Settings', {
            'fields': (
                'allow_file_upload', 'max_file_size_mb', 'allowed_file_types'
            ),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': (
                'due_date', 'late_submission_allowed', 'late_penalty_percent'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        })
    )
    
    def instructor_name(self, obj):
        """Display instructor name"""
        return f"{obj.course.instructor.first_name} {obj.course.instructor.last_name}"
    instructor_name.short_description = 'Instructor'
    
    def submission_count(self, obj):
        """Display submission count with link"""
        count = obj.submissions.count()
        if count > 0:
            url = reverse('admin:assignments_submission_changelist')
            return format_html(
                '<a href="{}?assignment__id__exact={}">{} submissions</a>',
                url, obj.id, count
            )
        return '0 submissions'
    submission_count.short_description = 'Submissions'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'course', 'course__instructor', 'tenant'
        ).prefetch_related('submissions')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Admin interface for Submission model"""
    
    list_display = [
        'assignment_title', 'student_name', 'status', 'score', 'final_score',
        'is_late', 'is_graded', 'submitted_at', 'graded_at'
    ]
    list_filter = [
        'status', 'is_graded', 'is_late', 'submitted_at', 'graded_at',
        'assignment__course', 'assignment__assignment_type'
    ]
    search_fields = [
        'assignment__title', 'student__email', 'student__first_name',
        'student__last_name', 'text_content'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'submitted_at', 'graded_at',
        'final_score', 'grade_percentage', 'is_passing'
    ]
    
    fieldsets = (
        ('Assignment Information', {
            'fields': ('assignment', 'student')
        }),
        ('Submission Content', {
            'fields': ('text_content', 'file_upload')
        }),
        ('Grading', {
            'fields': (
                'score', 'feedback', 'is_graded', 'graded_by',
                'final_score', 'grade_percentage', 'is_passing'
            )
        }),
        ('Status and Timing', {
            'fields': (
                'status', 'is_late', 'late_penalty_applied',
                'submitted_at', 'graded_at'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def assignment_title(self, obj):
        """Display assignment title with link"""
        url = reverse('admin:assignments_assignment_change', args=[obj.assignment.id])
        return format_html('<a href="{}">{}</a>', url, obj.assignment.title)
    assignment_title.short_description = 'Assignment'
    
    def student_name(self, obj):
        """Display student name"""
        return f"{obj.student.first_name} {obj.student.last_name}"
    student_name.short_description = 'Student'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'assignment', 'assignment__course', 'student', 'graded_by', 'tenant'
        )


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Admin interface for Certificate model"""
    
    list_display = [
        'certificate_number', 'student_name', 'course_title', 'certificate_type',
        'status', 'final_grade', 'completion_date', 'issued_at'
    ]
    list_filter = [
        'certificate_type', 'status', 'completion_date', 'issued_at',
        'course__category'
    ]
    search_fields = [
        'certificate_number', 'student__email', 'student__first_name',
        'student__last_name', 'course__title'
    ]
    readonly_fields = [
        'certificate_number', 'qr_code', 'verification_url',
        'created_at', 'updated_at', 'issued_at', 'is_valid'
    ]
    
    fieldsets = (
        ('Certificate Information', {
            'fields': (
                'student', 'course', 'certificate_type', 'certificate_number'
            )
        }),
        ('Achievement Data', {
            'fields': ('final_grade', 'completion_date')
        }),
        ('Verification', {
            'fields': ('qr_code', 'verification_url', 'status')
        }),
        ('Files', {
            'fields': ('pdf_file',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'issued_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def student_name(self, obj):
        """Display student name"""
        return f"{obj.student.first_name} {obj.student.last_name}"
    student_name.short_description = 'Student'
    
    def course_title(self, obj):
        """Display course title with link"""
        url = reverse('admin:courses_course_change', args=[obj.course.id])
        return format_html('<a href="{}">{}</a>', url, obj.course.title)
    course_title.short_description = 'Course'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'student', 'course', 'course__instructor', 'tenant'
        )


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    """Admin interface for CourseProgress model"""
    
    list_display = [
        'student_name', 'course_title', 'overall_progress_percentage',
        'assignment_average_score', 'attendance_percentage', 'is_completed',
        'completion_requirements_met', 'updated_at'
    ]
    list_filter = [
        'is_completed', 'completion_requirements_met', 'course__category',
        'updated_at', 'completed_at'
    ]
    search_fields = [
        'student__email', 'student__first_name', 'student__last_name',
        'course__title'
    ]
    readonly_fields = [
        'overall_progress_percentage', 'assignment_average_score',
        'attendance_percentage', 'is_completed', 'completion_requirements_met',
        'created_at', 'updated_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Student and Course', {
            'fields': ('student', 'course')
        }),
        ('Progress Tracking', {
            'fields': (
                'modules_completed', 'assignments_completed', 'live_classes_attended'
            )
        }),
        ('Calculated Metrics', {
            'fields': (
                'overall_progress_percentage', 'assignment_average_score',
                'attendance_percentage'
            )
        }),
        ('Completion Status', {
            'fields': (
                'is_completed', 'completion_requirements_met', 'completed_at'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def student_name(self, obj):
        """Display student name"""
        return f"{obj.student.first_name} {obj.student.last_name}"
    student_name.short_description = 'Student'
    
    def course_title(self, obj):
        """Display course title with link"""
        url = reverse('admin:courses_course_change', args=[obj.course.id])
        return format_html('<a href="{}">{}</a>', url, obj.course.title)
    course_title.short_description = 'Course'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'student', 'course', 'course__instructor', 'tenant'
        )
    
    actions = ['recalculate_progress']
    
    def recalculate_progress(self, request, queryset):
        """Admin action to recalculate progress for selected records"""
        updated_count = 0
        for progress in queryset:
            progress.calculate_progress()
            updated_count += 1
        
        self.message_user(
            request,
            f'Successfully recalculated progress for {updated_count} records.'
        )
    recalculate_progress.short_description = 'Recalculate progress for selected records'