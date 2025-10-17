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
        ('payment_failed', 'Payment Failed'),
        ('payment_overdue', 'Payment Overdue'),
        ('subscription_renewed', 'Subscription Renewed'),
        ('subscription_cancelled', 'Subscription Cancelled'),
        ('invoice_sent', 'Invoice Sent'),
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


class EmailDeliveryLog(TenantAwareModel):
    """Log email delivery status for monitoring"""
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='email_logs')
    recipient_email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    details = models.TextField(blank=True)
    
    # Delivery tracking
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    # Email metadata
    subject = models.CharField(max_length=255, blank=True)
    template_used = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'email_delivery_logs'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.recipient_email} - {self.status} - {self.sent_at}"


class NotificationTemplate(TenantAwareModel):
    """Custom notification templates for different tenants"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=50, choices=Notification.TYPE_CHOICES)
    
    # Template content
    subject_template = models.CharField(max_length=255)
    html_template = models.TextField()
    text_template = models.TextField(blank=True)
    
    # Template metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        unique_together = ['tenant', 'notification_type', 'name']
    
    def __str__(self):
        return f"{self.tenant.name if self.tenant else 'Global'} - {self.name}"


class ChatMessage(TenantAwareModel):
    """Real-time chat messages"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    content = models.TextField()
    
    # Message metadata
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['room_name', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} in {self.room_name}: {self.content[:50]}..."


class WebSocketConnection(TenantAwareModel):
    """Track active WebSocket connections for monitoring"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='websocket_connections')
    connection_type = models.CharField(max_length=50, choices=[
        ('notifications', 'Notifications'),
        ('chat', 'Chat'),
        ('live_class', 'Live Class'),
    ])
    
    # Connection details
    channel_name = models.CharField(max_length=255)
    room_name = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Connection status
    is_active = models.BooleanField(default=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'websocket_connections'
        ordering = ['-connected_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['connection_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.connection_type} - {'Active' if self.is_active else 'Inactive'}"