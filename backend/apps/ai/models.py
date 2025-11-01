import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.common.models import TenantAwareModel

User = get_user_model()


class AIConversation(TenantAwareModel):
    """AI conversation sessions with enhanced context tracking"""
    
    CONVERSATION_TYPES = [
        ('tutor', 'AI Tutor Chat'),
        ('general', 'General Chat'),
        ('course_help', 'Course Help'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    title = models.CharField(max_length=200, blank=True)
    conversation_type = models.CharField(max_length=20, choices=CONVERSATION_TYPES, default='tutor')
    
    # Enhanced context tracking
    context = models.JSONField(default=dict)  # Course context, learning objectives, etc.
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True, related_name='ai_conversations')
    
    # Conversation metadata
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_conversations'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.email} - {self.title or 'Untitled Conversation'}"


class AIMessage(models.Model):
    """Individual AI messages with enhanced metadata"""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    
    # Message metadata
    tokens_used = models.PositiveIntegerField(default=0)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class AIContentSummary(TenantAwareModel):
    """AI-generated content summaries"""
    
    CONTENT_TYPES = [
        ('live_class', 'Live Class Recording'),
        ('course_module', 'Course Module'),
        ('video', 'Video Content'),
        ('text', 'Text Content'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_summaries')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='ai_summaries')
    
    # Content reference
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.UUIDField()  # ID of the content being summarized
    content_title = models.CharField(max_length=200)
    
    # Summary data
    original_content = models.TextField()  # Original content or transcript
    summary = models.TextField()
    key_points = models.JSONField(default=list)  # List of key learning points
    
    # Metadata
    tokens_used = models.PositiveIntegerField(default=0)
    generation_time_ms = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_content_summaries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Summary: {self.content_title}"


class AIQuiz(TenantAwareModel):
    """AI-generated quizzes from course content"""
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_quizzes')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='ai_quizzes')
    
    # Quiz metadata
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty_level = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='medium')
    
    # Source content
    source_content = models.TextField()  # Content used to generate quiz
    questions = models.JSONField(default=list)  # List of question objects
    
    # Generation metadata
    tokens_used = models.PositiveIntegerField(default=0)
    generation_time_ms = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_quizzes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Quiz: {self.title}"


class AIUsageQuota(TenantAwareModel):
    """Enhanced AI usage tracking and quotas with subscription-based limits"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_usage')
    
    # Time period
    month = models.DateField()
    
    # Chat usage
    chat_messages_used = models.PositiveIntegerField(default=0)
    chat_messages_limit = models.PositiveIntegerField(default=100)
    chat_tokens_used = models.PositiveIntegerField(default=0)
    chat_tokens_limit = models.PositiveIntegerField(default=50000)
    
    # Summary usage
    summaries_generated = models.PositiveIntegerField(default=0)
    summaries_limit = models.PositiveIntegerField(default=20)
    summary_tokens_used = models.PositiveIntegerField(default=0)
    summary_tokens_limit = models.PositiveIntegerField(default=100000)
    
    # Quiz usage
    quizzes_generated = models.PositiveIntegerField(default=0)
    quizzes_limit = models.PositiveIntegerField(default=10)
    quiz_tokens_used = models.PositiveIntegerField(default=0)
    quiz_tokens_limit = models.PositiveIntegerField(default=50000)
    
    # Cost tracking
    total_cost_usd = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    cost_limit_usd = models.DecimalField(max_digits=10, decimal_places=4, default=10.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_usage_quotas'
        unique_together = ['user', 'month', 'tenant']
    
    def __str__(self):
        return f"{self.user.email} - {self.month}"
    
    def is_chat_quota_exceeded(self):
        """Check if chat quota is exceeded"""
        return (self.chat_messages_used >= self.chat_messages_limit or 
                self.chat_tokens_used >= self.chat_tokens_limit)
    
    def is_summary_quota_exceeded(self):
        """Check if summary quota is exceeded"""
        return (self.summaries_generated >= self.summaries_limit or 
                self.summary_tokens_used >= self.summary_tokens_limit)
    
    def is_quiz_quota_exceeded(self):
        """Check if quiz quota is exceeded"""
        return (self.quizzes_generated >= self.quizzes_limit or 
                self.quiz_tokens_used >= self.quiz_tokens_limit)
    
    def is_cost_limit_exceeded(self):
        """Check if cost limit is exceeded"""
        return self.total_cost_usd >= self.cost_limit_usd
    
    @classmethod
    def get_or_create_for_user(cls, user, tenant):
        """Get or create quota for current month"""
        current_month = timezone.now().date().replace(day=1)
        quota, created = cls.objects.get_or_create(
            user=user,
            tenant=tenant,
            month=current_month,
            defaults=cls._get_default_limits_for_tenant(tenant)
        )
        return quota
    
    @staticmethod
    def _get_default_limits_for_tenant(tenant):
        """Get default limits based on tenant subscription plan"""
        from apps.payments.models import Subscription
        
        try:
            # Get active subscription for tenant
            subscription = Subscription.objects.filter(
                organization=tenant,
                status='active'
            ).select_related('plan').first()
            
            if subscription and subscription.plan:
                plan = subscription.plan
                # Calculate AI limits based on subscription plan
                base_quota = plan.ai_quota_monthly
                
                return {
                    'chat_messages_limit': int(base_quota * 0.4),  # 40% for chat
                    'chat_tokens_limit': int(base_quota * 50),     # 50 tokens per message avg
                    'summaries_limit': int(base_quota * 0.2),     # 20% for summaries
                    'summary_tokens_limit': int(base_quota * 100), # 100 tokens per summary avg
                    'quizzes_limit': int(base_quota * 0.1),       # 10% for quizzes
                    'quiz_tokens_limit': int(base_quota * 200),   # 200 tokens per quiz avg
                    'cost_limit_usd': float(plan.price_monthly * 0.1),  # 10% of plan price
                }
        except Exception:
            pass
        
        # Fallback to basic limits
        return {
            'chat_messages_limit': 50,
            'chat_tokens_limit': 2500,
            'summaries_limit': 10,
            'summary_tokens_limit': 5000,
            'quizzes_limit': 5,
            'quiz_tokens_limit': 1000,
            'cost_limit_usd': 5.00,
        }


class AIRateLimit(models.Model):
    """Rate limiting for AI API calls"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_rate_limits')
    
    # Rate limiting windows
    requests_per_minute = models.PositiveIntegerField(default=10)
    requests_per_hour = models.PositiveIntegerField(default=100)
    requests_per_day = models.PositiveIntegerField(default=500)
    
    # Current usage tracking
    minute_window_start = models.DateTimeField(default=timezone.now)
    minute_requests = models.PositiveIntegerField(default=0)
    
    hour_window_start = models.DateTimeField(default=timezone.now)
    hour_requests = models.PositiveIntegerField(default=0)
    
    day_window_start = models.DateTimeField(default=timezone.now)
    day_requests = models.PositiveIntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_rate_limits'
        unique_together = ['user']
    
    def __str__(self):
        return f"Rate Limit: {self.user.email}"
    
    def can_make_request(self):
        """Check if user can make another request"""
        now = timezone.now()
        
        # Reset windows if needed
        if (now - self.minute_window_start).total_seconds() >= 60:
            self.minute_window_start = now
            self.minute_requests = 0
        
        if (now - self.hour_window_start).total_seconds() >= 3600:
            self.hour_window_start = now
            self.hour_requests = 0
        
        if (now - self.day_window_start).total_seconds() >= 86400:
            self.day_window_start = now
            self.day_requests = 0
        
        # Check limits
        return (self.minute_requests < self.requests_per_minute and
                self.hour_requests < self.requests_per_hour and
                self.day_requests < self.requests_per_day)
    
    def record_request(self):
        """Record a new request"""
        self.minute_requests += 1
        self.hour_requests += 1
        self.day_requests += 1
        self.save()