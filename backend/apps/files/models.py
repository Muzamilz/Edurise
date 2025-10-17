import uuid
import os
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from apps.common.models import TenantAwareModel
from apps.courses.models import Course

User = get_user_model()


class FileCategory(models.Model):
    """File categories for organization"""
    
    CATEGORY_CHOICES = [
        ('course_material', 'Course Material'),
        ('assignment_submission', 'Assignment Submission'),
        ('certificate', 'Certificate'),
        ('user_avatar', 'User Avatar'),
        ('course_thumbnail', 'Course Thumbnail'),
        ('recording', 'Class Recording'),
        ('document', 'Document'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    allowed_extensions = models.JSONField(default=list)  # List of allowed file extensions
    max_file_size_mb = models.PositiveIntegerField(default=10)  # Max file size in MB
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'file_categories'
        verbose_name_plural = 'File Categories'
    
    def __str__(self):
        return self.display_name


class FileUpload(TenantAwareModel):
    """Central file upload model with metadata and access controls"""
    
    ACCESS_LEVEL_CHOICES = [
        ('public', 'Public'),
        ('tenant', 'Tenant Only'),
        ('enrolled', 'Enrolled Students Only'),
        ('instructor', 'Instructor Only'),
        ('private', 'Private'),
    ]
    
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # File information
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    file_size = models.PositiveIntegerField()  # Size in bytes
    file_type = models.CharField(max_length=100)  # MIME type
    file_extension = models.CharField(max_length=10)
    
    # Metadata
    category = models.ForeignKey(FileCategory, on_delete=models.PROTECT, related_name='files')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Ownership and access
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES, default='private')
    allowed_users = models.ManyToManyField(User, blank=True, related_name='accessible_files')
    
    # Course association (optional)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='files')
    
    # Status and processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    processing_status = models.JSONField(default=dict, blank=True)  # Processing metadata
    
    # Usage tracking
    download_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # Optional expiration
    
    class Meta:
        db_table = 'file_uploads'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['uploaded_by', 'created_at']),
            models.Index(fields=['course', 'access_level']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} ({self.uploaded_by.email})"
    
    def save(self, *args, **kwargs):
        # Extract file information on first save
        if not self.pk and self.file:
            self.file_size = self.file.size
            self.file_type = getattr(self.file.file, 'content_type', 'application/octet-stream')
            self.file_extension = os.path.splitext(self.original_filename)[1].lower().lstrip('.')
            
            if not self.title:
                self.title = os.path.splitext(self.original_filename)[0]
        
        super().save(*args, **kwargs)
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def is_image(self):
        """Check if file is an image"""
        return self.file_type.startswith('image/')
    
    @property
    def is_video(self):
        """Check if file is a video"""
        return self.file_type.startswith('video/')
    
    @property
    def is_document(self):
        """Check if file is a document"""
        document_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
        ]
        return self.file_type in document_types
    
    @property
    def is_expired(self):
        """Check if file has expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    def can_access(self, user):
        """Check if user can access this file"""
        if self.status == 'deleted':
            return False
        
        if self.is_expired:
            return False
        
        # Owner can always access
        if self.uploaded_by == user:
            return True
        
        # Check access level
        if self.access_level == 'public':
            return True
        
        if self.access_level == 'tenant':
            return user.tenant == self.tenant
        
        if self.access_level == 'enrolled' and self.course:
            return self.course.enrollments.filter(student=user).exists()
        
        if self.access_level == 'instructor' and self.course:
            return self.course.instructor == user or user.is_staff
        
        if self.access_level == 'private':
            return self.allowed_users.filter(id=user.id).exists()
        
        return False
    
    def record_access(self, user=None):
        """Record file access"""
        self.download_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['download_count', 'last_accessed'])
        
        # Create access log
        FileAccessLog.objects.create(
            file=self,
            user=user,
            tenant=self.tenant
        )
    
    def get_secure_url(self, expires_in_seconds=3600):
        """Generate secure URL for file access"""
        # This would integrate with cloud storage for signed URLs
        # For now, return the regular URL
        return self.file.url
    
    def delete_file(self):
        """Soft delete the file"""
        self.status = 'deleted'
        self.save()


class FileAccessLog(TenantAwareModel):
    """Log file access for analytics and security"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    accessed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'file_access_logs'
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['file', 'accessed_at']),
            models.Index(fields=['user', 'accessed_at']),
        ]
    
    def __str__(self):
        user_info = self.user.email if self.user else f"Anonymous ({self.ip_address})"
        return f"{self.file.original_filename} accessed by {user_info}"


class FileProcessingJob(TenantAwareModel):
    """Track file processing jobs (thumbnails, conversions, etc.)"""
    
    JOB_TYPE_CHOICES = [
        ('thumbnail', 'Generate Thumbnail'),
        ('video_transcode', 'Video Transcoding'),
        ('document_preview', 'Document Preview'),
        ('virus_scan', 'Virus Scan'),
        ('metadata_extraction', 'Metadata Extraction'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='processing_jobs')
    job_type = models.CharField(max_length=30, choices=JOB_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Job configuration
    parameters = models.JSONField(default=dict, blank=True)
    
    # Results
    result_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'file_processing_jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['file', 'job_type']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.job_type} for {self.file.original_filename} ({self.status})"