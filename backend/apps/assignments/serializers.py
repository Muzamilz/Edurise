from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Assignment, Submission, Certificate, CourseProgress
from apps.courses.models import Course

User = get_user_model()


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Assignment model"""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    instructor_name = serializers.SerializerMethodField()
    submission_count = serializers.ReadOnlyField()
    graded_submission_count = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'course', 'course_title', 'instructor_name', 'title', 'description', 
            'instructions', 'assignment_type', 'max_score', 'passing_score',
            'allow_file_upload', 'max_file_size_mb', 'allowed_file_types',
            'due_date', 'late_submission_allowed', 'late_penalty_percent',
            'status', 'is_required', 'weight_percentage', 'created_at', 
            'updated_at', 'published_at', 'submission_count', 
            'graded_submission_count', 'is_overdue', 'days_until_due'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at']
    
    def get_instructor_name(self, obj):
        """Get instructor full name"""
        return f"{obj.course.instructor.first_name} {obj.course.instructor.last_name}"
    
    def validate_due_date(self, value):
        """Validate due date is in the future"""
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("Due date must be in the future")
        return value
    
    def validate_passing_score(self, value):
        """Validate passing score is not greater than max score"""
        max_score = self.initial_data.get('max_score', 100)
        if value > max_score:
            raise serializers.ValidationError("Passing score cannot be greater than max score")
        return value


class AssignmentDetailSerializer(AssignmentSerializer):
    """Detailed serializer for Assignment with additional information"""
    
    submissions = serializers.SerializerMethodField()
    student_submission = serializers.SerializerMethodField()
    
    class Meta(AssignmentSerializer.Meta):
        fields = AssignmentSerializer.Meta.fields + ['submissions', 'student_submission']
    
    def get_submissions(self, obj):
        """Get submissions for instructors/admins"""
        request = self.context.get('request')
        if not request:
            return []
        
        # Only show submissions to instructor or admin
        if obj.course.instructor == request.user or request.user.is_staff:
            submissions = obj.submissions.select_related('student').order_by('-submitted_at')
            return SubmissionSerializer(submissions, many=True, context=self.context).data
        
        return []
    
    def get_student_submission(self, obj):
        """Get current user's submission if exists"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            submission = obj.submissions.get(student=request.user)
            return SubmissionSerializer(submission, context=self.context).data
        except Submission.DoesNotExist:
            return None


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Submission model"""
    
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    student_name = serializers.SerializerMethodField()
    student_email = serializers.CharField(source='student.email', read_only=True)
    final_score = serializers.ReadOnlyField()
    grade_percentage = serializers.ReadOnlyField()
    is_passing = serializers.ReadOnlyField()
    graded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'assignment_title', 'student', 'student_name', 
            'student_email', 'text_content', 'file_upload', 'score', 'feedback',
            'is_graded', 'graded_by', 'graded_by_name', 'status', 'is_late',
            'late_penalty_applied', 'final_score', 'grade_percentage', 'is_passing',
            'created_at', 'submitted_at', 'graded_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'student', 'is_graded', 'graded_by', 'is_late', 
            'late_penalty_applied', 'created_at', 'submitted_at', 
            'graded_at', 'updated_at'
        ]
    
    def get_student_name(self, obj):
        """Get student full name"""
        return f"{obj.student.first_name} {obj.student.last_name}"
    
    def get_graded_by_name(self, obj):
        """Get grader full name"""
        if obj.graded_by:
            return f"{obj.graded_by.first_name} {obj.graded_by.last_name}"
        return None
    
    def validate_score(self, value):
        """Validate score is within assignment max score"""
        if hasattr(self, 'instance') and self.instance:
            max_score = self.instance.assignment.max_score
            if value > max_score:
                raise serializers.ValidationError(f"Score cannot exceed {max_score}")
        return value


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating submissions by students"""
    
    class Meta:
        model = Submission
        fields = ['assignment', 'text_content', 'file_upload']
    
    def validate_assignment(self, value):
        """Validate assignment is published and not closed"""
        if value.status != 'published':
            raise serializers.ValidationError("Assignment is not published")
        return value
    
    def validate_file_upload(self, value):
        """Validate file upload based on assignment settings"""
        if not value:
            return value
        
        assignment = self.initial_data.get('assignment')
        if not assignment:
            return value
        
        # Check file size
        if hasattr(assignment, 'max_file_size_mb'):
            max_size = assignment.max_file_size_mb * 1024 * 1024  # Convert to bytes
            if value.size > max_size:
                raise serializers.ValidationError(
                    f"File size exceeds maximum allowed size of {assignment.max_file_size_mb}MB"
                )
        
        # Check file type
        if hasattr(assignment, 'allowed_file_types') and assignment.allowed_file_types:
            file_extension = value.name.split('.')[-1].lower()
            if file_extension not in assignment.allowed_file_types:
                raise serializers.ValidationError(
                    f"File type '{file_extension}' is not allowed. "
                    f"Allowed types: {', '.join(assignment.allowed_file_types)}"
                )
        
        return value


class SubmissionGradeSerializer(serializers.ModelSerializer):
    """Serializer for grading submissions"""
    
    class Meta:
        model = Submission
        fields = ['score', 'feedback']
    
    def validate_score(self, value):
        """Validate score is within assignment max score"""
        if self.instance:
            max_score = self.instance.assignment.max_score
            if value > max_score:
                raise serializers.ValidationError(f"Score cannot exceed {max_score}")
        return value


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for Certificate model with centralized API data"""
    
    student = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()
    is_valid = serializers.ReadOnlyField()
    certificate_file_url = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'student', 'course', 'instructor', 'certificate_type', 
            'certificate_number', 'final_grade', 'completion_date',
            'qr_code', 'qr_code_url', 'verification_url', 'status', 
            'pdf_file', 'certificate_file_url', 'is_valid', 
            'created_at', 'issued_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'certificate_number', 'qr_code', 'verification_url',
            'created_at', 'issued_at', 'updated_at'
        ]
    
    def get_student(self, obj):
        """Get comprehensive student data from centralized API"""
        return {
            'id': str(obj.student.id),
            'email': obj.student.email,
            'first_name': obj.student.first_name,
            'last_name': obj.student.last_name,
            'full_name': obj.student.get_full_name() or obj.student.email
        }
    
    def get_course(self, obj):
        """Get comprehensive course data from centralized API"""
        return {
            'id': str(obj.course.id),
            'title': obj.course.title,
            'description': obj.course.description,
            'category': obj.course.category,
            'duration_weeks': obj.course.duration_weeks
        }
    
    def get_instructor(self, obj):
        """Get instructor data from centralized API"""
        return {
            'id': str(obj.course.instructor.id),
            'email': obj.course.instructor.email,
            'first_name': obj.course.instructor.first_name,
            'last_name': obj.course.instructor.last_name,
            'full_name': obj.course.instructor.get_full_name() or obj.course.instructor.email
        }
    
    def get_certificate_file_url(self, obj):
        """Get secure certificate file URL from centralized API"""
        if obj.certificate_file:
            return obj.certificate_file.get_secure_url()
        return None
    
    def get_qr_code_url(self, obj):
        """Get QR code URL from centralized API"""
        if obj.qr_code:
            return obj.qr_code.url
        return None


class CourseProgressSerializer(serializers.ModelSerializer):
    """Serializer for CourseProgress model"""
    
    student_name = serializers.SerializerMethodField()
    student_email = serializers.CharField(source='student.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = CourseProgress
        fields = [
            'id', 'student', 'student_name', 'student_email', 'course', 
            'course_title', 'modules_completed', 'assignments_completed',
            'live_classes_attended', 'overall_progress_percentage',
            'assignment_average_score', 'attendance_percentage',
            'is_completed', 'completion_requirements_met',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'overall_progress_percentage', 'assignment_average_score',
            'attendance_percentage', 'is_completed', 'completion_requirements_met',
            'created_at', 'updated_at', 'completed_at'
        ]
    
    def get_student_name(self, obj):
        """Get student full name"""
        return f"{obj.student.first_name} {obj.student.last_name}"


class CourseCompletionAnalyticsSerializer(serializers.Serializer):
    """Serializer for course completion analytics"""
    
    total_students = serializers.IntegerField()
    completed_students = serializers.IntegerField()
    completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_progress = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_assignment_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_attendance = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Progress distribution
    progress_distribution = serializers.DictField()
    
    # Top performers
    top_performers = CourseProgressSerializer(many=True)
    
    # Students needing attention
    students_at_risk = CourseProgressSerializer(many=True)