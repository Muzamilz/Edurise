from rest_framework import serializers
from .models import (
    AIConversation, AIMessage, AIContentSummary, 
    AIQuiz, AIUsageQuota, AIRateLimit
)


class AIMessageSerializer(serializers.ModelSerializer):
    """Serializer for AI messages"""
    
    class Meta:
        model = AIMessage
        fields = [
            'id', 'role', 'content', 'tokens_used', 
            'response_time_ms', 'created_at'
        ]
        read_only_fields = ['id', 'tokens_used', 'response_time_ms', 'created_at']


class AIConversationSerializer(serializers.ModelSerializer):
    """Serializer for AI conversations"""
    
    messages = AIMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AIConversation
        fields = [
            'id', 'title', 'conversation_type', 'context', 
            'course', 'is_active', 'last_activity', 
            'created_at', 'updated_at', 'messages', 'message_count'
        ]
        read_only_fields = ['id', 'last_activity', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        """Get total message count for the conversation"""
        return obj.messages.count()


class AIContentSummarySerializer(serializers.ModelSerializer):
    """Serializer for AI content summaries"""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = AIContentSummary
        fields = [
            'id', 'content_type', 'content_id', 'content_title',
            'course', 'course_title', 'summary', 'key_points',
            'tokens_used', 'generation_time_ms', 'created_at'
        ]
        read_only_fields = [
            'id', 'tokens_used', 'generation_time_ms', 'created_at'
        ]


class AIQuizSerializer(serializers.ModelSerializer):
    """Serializer for AI-generated quizzes"""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AIQuiz
        fields = [
            'id', 'title', 'description', 'difficulty_level',
            'course', 'course_title', 'questions', 'question_count',
            'tokens_used', 'generation_time_ms', 'created_at'
        ]
        read_only_fields = [
            'id', 'tokens_used', 'generation_time_ms', 'created_at'
        ]
    
    def get_question_count(self, obj):
        """Get number of questions in the quiz"""
        return len(obj.questions) if obj.questions else 0


class AIUsageQuotaSerializer(serializers.ModelSerializer):
    """Serializer for AI usage quotas"""
    
    chat_usage_percentage = serializers.SerializerMethodField()
    summary_usage_percentage = serializers.SerializerMethodField()
    quiz_usage_percentage = serializers.SerializerMethodField()
    cost_usage_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = AIUsageQuota
        fields = [
            'id', 'month', 
            # Chat usage
            'chat_messages_used', 'chat_messages_limit', 'chat_usage_percentage',
            'chat_tokens_used', 'chat_tokens_limit',
            # Summary usage
            'summaries_generated', 'summaries_limit', 'summary_usage_percentage',
            'summary_tokens_used', 'summary_tokens_limit',
            # Quiz usage
            'quizzes_generated', 'quizzes_limit', 'quiz_usage_percentage',
            'quiz_tokens_used', 'quiz_tokens_limit',
            # Cost tracking
            'total_cost_usd', 'cost_limit_usd', 'cost_usage_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'chat_usage_percentage', 'summary_usage_percentage',
            'quiz_usage_percentage', 'cost_usage_percentage'
        ]
    
    def get_chat_usage_percentage(self, obj):
        """Calculate chat usage percentage"""
        if obj.chat_messages_limit == 0:
            return 0
        return (obj.chat_messages_used / obj.chat_messages_limit) * 100
    
    def get_summary_usage_percentage(self, obj):
        """Calculate summary usage percentage"""
        if obj.summaries_limit == 0:
            return 0
        return (obj.summaries_generated / obj.summaries_limit) * 100
    
    def get_quiz_usage_percentage(self, obj):
        """Calculate quiz usage percentage"""
        if obj.quizzes_limit == 0:
            return 0
        return (obj.quizzes_generated / obj.quizzes_limit) * 100
    
    def get_cost_usage_percentage(self, obj):
        """Calculate cost usage percentage"""
        if obj.cost_limit_usd == 0:
            return 0
        return (float(obj.total_cost_usd) / float(obj.cost_limit_usd)) * 100


class AIRateLimitSerializer(serializers.ModelSerializer):
    """Serializer for AI rate limits"""
    
    can_make_request = serializers.SerializerMethodField()
    
    class Meta:
        model = AIRateLimit
        fields = [
            'id', 'requests_per_minute', 'requests_per_hour', 'requests_per_day',
            'minute_requests', 'hour_requests', 'day_requests',
            'can_make_request', 'updated_at'
        ]
        read_only_fields = [
            'id', 'minute_requests', 'hour_requests', 'day_requests',
            'can_make_request', 'updated_at'
        ]
    
    def get_can_make_request(self, obj):
        """Check if user can make another request"""
        return obj.can_make_request()


# Request/Response serializers for API endpoints

class ChatMessageRequestSerializer(serializers.Serializer):
    """Serializer for chat message requests"""
    
    message = serializers.CharField(max_length=2000, required=True)
    context = serializers.JSONField(required=False, default=dict)


class ChatMessageResponseSerializer(serializers.Serializer):
    """Serializer for chat message responses"""
    
    success = serializers.BooleanField()
    ai_response = serializers.CharField()
    metadata = serializers.JSONField()


class SummaryRequestSerializer(serializers.Serializer):
    """Serializer for summary generation requests"""
    
    content = serializers.CharField(required=True)
    content_type = serializers.ChoiceField(
        choices=['live_class', 'course_module', 'video', 'text'],
        default='text'
    )
    content_id = serializers.CharField(required=False)
    content_title = serializers.CharField(max_length=200, default='Untitled Content')
    course_id = serializers.UUIDField(required=False)


class SummaryResponseSerializer(serializers.Serializer):
    """Serializer for summary generation responses"""
    
    success = serializers.BooleanField()
    summary = serializers.CharField()
    key_points = serializers.ListField(child=serializers.CharField())
    metadata = serializers.JSONField()


class QuizRequestSerializer(serializers.Serializer):
    """Serializer for quiz generation requests"""
    
    content = serializers.CharField(required=True)
    course_id = serializers.UUIDField(required=True)
    title = serializers.CharField(max_length=200, default='AI Generated Quiz')
    num_questions = serializers.IntegerField(min_value=1, max_value=20, default=5)
    difficulty = serializers.ChoiceField(
        choices=['easy', 'medium', 'hard'],
        default='medium'
    )


class QuizResponseSerializer(serializers.Serializer):
    """Serializer for quiz generation responses"""
    
    success = serializers.BooleanField()
    questions = serializers.ListField(child=serializers.JSONField())
    metadata = serializers.JSONField()


class UsageStatsResponseSerializer(serializers.Serializer):
    """Serializer for usage statistics responses"""
    
    success = serializers.BooleanField()
    stats = serializers.JSONField()