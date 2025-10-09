import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.common.models import TenantAwareModel

User = get_user_model()


class AIConversation(TenantAwareModel):
    """AI conversation sessions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    title = models.CharField(max_length=200, blank=True)
    context = models.JSONField(default=dict)  # Course context, etc.
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_conversations'
        ordering = ['-updated_at']


class AIMessage(models.Model):
    """Individual AI messages"""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_messages'
        ordering = ['created_at']


class AIUsageQuota(TenantAwareModel):
    """AI usage tracking and quotas"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_usage')
    
    # Monthly quotas
    month = models.DateField()
    chat_messages_used = models.PositiveIntegerField(default=0)
    chat_messages_limit = models.PositiveIntegerField(default=100)
    
    summaries_generated = models.PositiveIntegerField(default=0)
    summaries_limit = models.PositiveIntegerField(default=20)
    
    quizzes_generated = models.PositiveIntegerField(default=0)
    quizzes_limit = models.PositiveIntegerField(default=10)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_usage_quotas'
        unique_together = ['user', 'month', 'tenant']