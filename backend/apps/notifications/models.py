import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.common.models import TenantAwareModel

User = get_user_model()


class Notification(TenantAwareModel):
    """User notifications"""
    
    TYPE_CHOICES = [
        ('course_enrollment', 'Course Enrollment'),
        ('class_reminder', 'Class Reminder'),
        ('assignment_due', 'Assignment Due'),
        ('payment_success', 'Payment Success'),
        ('teacher_approval', 'Teacher Approval'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    
    # Delivery channels
    is_read = models.BooleanField(default=False)
    sent_email = models.BooleanField(default=False)
    sent_push = models.BooleanField(default=False)
    
    # Related objects
    related_object_id = models.UUIDField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()