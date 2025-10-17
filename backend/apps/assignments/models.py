import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.base import ContentFile
from django.utils import timezone
from apps.common.models import TenantAwareModel
from apps.courses.models import Course

User = get_user_model()


class Assignment(TenantAwareModel):
    """Assignment model for course assignments"""
    
    ASSIGNMENT_TYPE_CHOICES = [
        ('essay', 'Essay'),
        ('project', 'Project'),
        ('quiz', 'Quiz'),
        ('presentation', 'Presentation'),
        ('code', 'Code Assignment'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField(blank=True)
    
    # Assignment settings
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPE_CHOICES, default='essay')
    max_score = models.PositiveIntegerField(default=100)
    passing_score = models.PositiveIntegerField(default=60)
    
    # File upload settings
    allow_file_upload = models.BooleanField(default=True)
    max_file_size_mb = models.PositiveIntegerField(default=10)  # Max file size in MB
    allowed_file_types = models.JSONField(default=list, blank=True)  # List of allowed extensions
    
    # Timing
    due_date = models.DateTimeField()
    late_submission_allowed = models.BooleanField(default=True)
    late_penalty_percent = models.PositiveIntegerField(default=10)  # Penalty per day late
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_required = models.BooleanField(default=True)
    weight_percentage = models.PositiveIntegerField(default=10)  # Weight in final grade
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'assignments'
        ordering = ['due_date', 'created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def is_overdue(self):
        """Check if assignment is overdue"""
        return timezone.now() > self.due_date
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.is_overdue:
            return 0
        delta = self.due_date - timezone.now()
        return delta.days
    
    @property
    def submission_count(self):
        """Get total number of submissions"""
        return self.submissions.count()
    
    @property
    def graded_submission_count(self):
        """Get number of graded submissions"""
        return self.submissions.filter(is_graded=True).count()
    
    def publish(self):
        """Publish the assignment"""
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()
    
    def close(self):
        """Close the assignment for submissions"""
        self.status = 'closed'
        self.save()


class Submission(TenantAwareModel):
    """Student submission for assignments"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('late', 'Late Submission'),
        ('graded', 'Graded'),
        ('returned', 'Returned for Revision'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    
    # Submission content
    text_content = models.TextField(blank=True)
    file_upload = models.FileField(upload_to='submissions/', blank=True, null=True)
    # New centralized file reference
    uploaded_file = models.ForeignKey(
        'files.FileUpload', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assignment_submissions'
    )
    
    # Grading
    score = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    is_graded = models.BooleanField(default=False)
    graded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='graded_submissions'
    )
    
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_late = models.BooleanField(default=False)
    late_penalty_applied = models.PositiveIntegerField(default=0)  # Penalty percentage applied
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'submissions'
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at', '-created_at']
    
    def __str__(self):
        return f"{self.assignment.title} - {self.student.email}"
    
    @property
    def final_score(self):
        """Calculate final score after late penalty"""
        if not self.score:
            return None
        
        if self.is_late and self.late_penalty_applied > 0:
            penalty = (self.score * self.late_penalty_applied) / 100
            return max(0, self.score - penalty)
        
        return self.score
    
    @property
    def grade_percentage(self):
        """Calculate grade as percentage"""
        if not self.final_score:
            return None
        return (self.final_score / self.assignment.max_score) * 100
    
    @property
    def is_passing(self):
        """Check if submission meets passing score"""
        if not self.final_score:
            return False
        return self.final_score >= self.assignment.passing_score
    
    def submit(self):
        """Submit the assignment"""
        now = timezone.now()
        self.submitted_at = now
        
        # Check if late
        if now > self.assignment.due_date:
            self.is_late = True
            self.status = 'late'
            
            # Calculate late penalty
            if self.assignment.late_penalty_percent > 0:
                days_late = (now - self.assignment.due_date).days
                self.late_penalty_applied = min(
                    days_late * self.assignment.late_penalty_percent,
                    100  # Maximum 100% penalty
                )
        else:
            self.status = 'submitted'
        
        self.save()
    
    def grade(self, score, feedback="", graded_by=None):
        """Grade the submission"""
        self.score = score
        self.feedback = feedback
        self.is_graded = True
        self.graded_by = graded_by
        self.graded_at = timezone.now()
        self.status = 'graded'
        self.save()


class Certificate(TenantAwareModel):
    """Certificate model for course completion"""
    
    CERTIFICATE_TYPE_CHOICES = [
        ('completion', 'Certificate of Completion'),
        ('achievement', 'Certificate of Achievement'),
        ('participation', 'Certificate of Participation'),
        ('excellence', 'Certificate of Excellence'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('issued', 'Issued'),
        ('revoked', 'Revoked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    
    # Certificate details
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPE_CHOICES, default='completion')
    certificate_number = models.CharField(max_length=50, unique=True)
    
    # Achievement data
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    completion_date = models.DateTimeField()
    
    # Verification
    qr_code = models.ImageField(upload_to='certificate_qr_codes/', blank=True, null=True)
    verification_url = models.URLField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # PDF generation
    pdf_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    # New centralized file reference
    certificate_file = models.ForeignKey(
        'files.FileUpload',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='certificates'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'certificates'
        unique_together = ['student', 'course']
        ordering = ['-issued_at', '-created_at']
    
    def __str__(self):
        return f"{self.certificate_type} - {self.student.email} - {self.course.title}"
    
    def save(self, *args, **kwargs):
        # Generate certificate number if not exists
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()
        
        # Generate verification URL
        if not self.verification_url:
            self.verification_url = f"/verify-certificate/{self.certificate_number}/"
        
        super().save(*args, **kwargs)
        
        # Generate QR code after saving (need ID)
        if not self.qr_code:
            self.generate_qr_code()
    
    def generate_certificate_number(self):
        """Generate unique certificate number"""
        import random
        import string
        
        # Format: CERT-YYYY-XXXXXXXX
        year = timezone.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"CERT-{year}-{random_part}"
    
    def generate_qr_code(self):
        """Generate QR code for certificate verification"""
        if not self.verification_url:
            return
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Full verification URL
        full_url = f"https://edurise.com{self.verification_url}"
        qr.add_data(full_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Save to model
        filename = f"qr_code_{self.certificate_number}.png"
        self.qr_code.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=True
        )
    
    def issue(self):
        """Issue the certificate"""
        self.status = 'issued'
        self.issued_at = timezone.now()
        self.save()
    
    def revoke(self):
        """Revoke the certificate"""
        self.status = 'revoked'
        self.save()
    
    @property
    def is_valid(self):
        """Check if certificate is valid"""
        return self.status == 'issued'


class CourseProgress(TenantAwareModel):
    """Track student progress in courses for completion analytics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_progress')
    
    # Progress tracking
    modules_completed = models.JSONField(default=list)  # List of completed module IDs
    assignments_completed = models.JSONField(default=list)  # List of completed assignment IDs
    live_classes_attended = models.JSONField(default=list)  # List of attended class IDs
    
    # Calculated metrics
    overall_progress_percentage = models.PositiveIntegerField(default=0)
    assignment_average_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Completion status
    is_completed = models.BooleanField(default=False)
    completion_requirements_met = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'course_progress'
        unique_together = ['student', 'course']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.student.email} - {self.course.title} ({self.overall_progress_percentage}%)"
    
    def calculate_progress(self):
        """Calculate overall progress based on modules, assignments, and attendance"""
        # Get course requirements
        total_modules = self.course.modules.filter(is_published=True).count()
        total_assignments = self.course.assignments.filter(status='published', is_required=True).count()
        total_classes = self.course.live_classes.filter(status__in=['completed', 'live']).count()
        
        # Calculate component progress
        module_progress = 0
        if total_modules > 0:
            module_progress = (len(self.modules_completed) / total_modules) * 100
        
        assignment_progress = 0
        if total_assignments > 0:
            assignment_progress = (len(self.assignments_completed) / total_assignments) * 100
        
        attendance_progress = 0
        if total_classes > 0:
            attendance_progress = (len(self.live_classes_attended) / total_classes) * 100
            self.attendance_percentage = attendance_progress
        
        # Weighted average (modules: 40%, assignments: 40%, attendance: 20%)
        self.overall_progress_percentage = int(
            (module_progress * 0.4) + 
            (assignment_progress * 0.4) + 
            (attendance_progress * 0.2)
        )
        
        # Calculate assignment average score
        if self.assignments_completed:
            from django.db.models import Avg
            avg_score = Submission.objects.filter(
                assignment__course=self.course,
                student=self.student,
                assignment_id__in=self.assignments_completed,
                is_graded=True
            ).aggregate(avg_score=Avg('score'))['avg_score']
            
            if avg_score:
                self.assignment_average_score = avg_score
        
        # Check completion requirements
        self.check_completion_requirements()
        
        self.save()
    
    def check_completion_requirements(self):
        """Check if student meets course completion requirements"""
        # Default requirements: 80% overall progress and 60% assignment average
        min_progress = 80
        min_assignment_average = 60
        
        requirements_met = (
            self.overall_progress_percentage >= min_progress and
            (self.assignment_average_score or 0) >= min_assignment_average
        )
        
        self.completion_requirements_met = requirements_met
        
        # Mark as completed if requirements are met
        if requirements_met and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
    
    def add_module_completion(self, module_id):
        """Mark a module as completed"""
        if str(module_id) not in self.modules_completed:
            self.modules_completed.append(str(module_id))
            self.calculate_progress()
    
    def add_assignment_completion(self, assignment_id):
        """Mark an assignment as completed"""
        if str(assignment_id) not in self.assignments_completed:
            self.assignments_completed.append(str(assignment_id))
            self.calculate_progress()
    
    def add_class_attendance(self, class_id):
        """Mark attendance for a live class"""
        if str(class_id) not in self.live_classes_attended:
            self.live_classes_attended.append(str(class_id))
            self.calculate_progress()