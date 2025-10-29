import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.common.models import TenantAwareModel

User = get_user_model()


class ScheduledReport(TenantAwareModel):
    """Model for scheduled report generation and management"""
    
    REPORT_TYPE_CHOICES = [
        ('overview', 'Overview Report'),
        ('enrollment', 'Enrollment Report'),
        ('financial', 'Financial Report'),
        ('course', 'Course Performance Report'),
    ]
    
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_reports')
    
    # Report configuration
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    format_type = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    email = models.EmailField()
    
    # Filters and parameters
    filters = models.JSONField(default=dict, blank=True)
    
    # Scheduling
    scheduled_at = models.DateTimeField(auto_now_add=True)
    execute_at = models.DateTimeField(null=True, blank=True)  # For future scheduling
    
    # Status and results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # File storage
    file_path = models.CharField(max_length=500, blank=True)
    download_url = models.URLField(blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)  # in bytes
    
    # Metadata
    estimated_completion = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        db_table = 'scheduled_reports'
        ordering = ['-scheduled_at']
        indexes = [
            models.Index(fields=['created_by', 'scheduled_at']),
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['report_type', 'scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.email} ({self.status})"


class AuditLog(TenantAwareModel):
    """Audit log for tracking system changes"""
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('read', 'Read'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('payment', 'Payment'),
        ('enrollment', 'Enrollment'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance'),
        ('bulk_operation', 'Bulk Operation'),
        ('export', 'Export'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50)  # Model name
    resource_id = models.CharField(max_length=100, null=True, blank=True)  # Changed to CharField for flexibility
    description = models.CharField(max_length=500, blank=True)
    
    # Change details
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['resource_type', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]
    
    def __str__(self):
        user_str = self.user.email if self.user else 'Anonymous'
        return f"{user_str} - {self.action} {self.resource_type} at {self.created_at}"