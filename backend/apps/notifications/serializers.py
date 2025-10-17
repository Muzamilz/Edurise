from rest_framework import serializers
from .models import Notification, EmailDeliveryLog, NotificationTemplate, ChatMessage, WebSocketConnection


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_name', 'user_email', 'title', 'message',
            'notification_type', 'is_read', 'sent_email', 'sent_push',
            'related_object_id', 'related_object_type', 'created_at',
            'read_at', 'time_since_created'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'read_at', 'sent_email', 'sent_push']
    
    def get_time_since_created(self, obj):
        """Get human-readable time since notification was created"""
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        return timesince(obj.created_at, timezone.now())


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'notification_type', 'related_object_id', 
            'related_object_type'
        ]
    
    def create(self, validated_data):
        # Add user and tenant from request context
        validated_data['user'] = self.context['request'].user
        if hasattr(self.context['request'], 'tenant'):
            validated_data['tenant'] = self.context['request'].tenant
        
        return super().create(validated_data)


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics"""
    
    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    read_notifications = serializers.IntegerField()
    notifications_by_type = serializers.DictField()
    recent_notifications = NotificationSerializer(many=True)


class NotificationPreferencesSerializer(serializers.Serializer):
    """Serializer for notification preferences"""
    
    email_notifications = serializers.BooleanField(default=True)
    push_notifications = serializers.BooleanField(default=True)
    course_enrollment_notifications = serializers.BooleanField(default=True)
    class_reminder_notifications = serializers.BooleanField(default=True)
    assignment_due_notifications = serializers.BooleanField(default=True)
    payment_notifications = serializers.BooleanField(default=True)
    system_notifications = serializers.BooleanField(default=True)
    
    def update(self, instance, validated_data):
        """Update user notification preferences"""
        # This would update user profile or separate preferences model
        # For now, we'll store in user profile's notification_preferences JSON field
        if hasattr(instance, 'userprofile'):
            profile = instance.userprofile
            if not profile.notification_preferences:
                profile.notification_preferences = {}
            
            profile.notification_preferences.update(validated_data)
            profile.save()
        
        return instance


class EmailDeliveryLogSerializer(serializers.ModelSerializer):
    """Serializer for EmailDeliveryLog model"""
    
    notification_title = serializers.CharField(source='notification.title', read_only=True)
    
    class Meta:
        model = EmailDeliveryLog
        fields = [
            'id', 'notification', 'notification_title', 'recipient_email', 
            'status', 'details', 'sent_at', 'delivered_at', 'opened_at', 
            'clicked_at', 'subject', 'template_used'
        ]
        read_only_fields = ['id', 'sent_at']


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate model"""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'subject_template', 
            'html_template', 'text_template', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Add tenant from request context
        if hasattr(self.context['request'], 'tenant'):
            validated_data['tenant'] = self.context['request'].tenant
        
        return super().create(validated_data)


class EmailTemplateListSerializer(serializers.Serializer):
    """Serializer for available email templates"""
    
    template_name = serializers.CharField()
    display_name = serializers.CharField()
    notification_type = serializers.CharField()
    is_available = serializers.BooleanField()


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for ChatMessage model"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'room_name', 'user', 'user_name', 'user_email', 
            'content', 'is_edited', 'edited_at', 'is_deleted', 
            'deleted_at', 'created_at', 'updated_at', 'time_since_created'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_time_since_created(self, obj):
        """Get human-readable time since message was created"""
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        return timesince(obj.created_at, timezone.now())


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = ['room_name', 'content']
    
    def create(self, validated_data):
        # Add user and tenant from request context
        validated_data['user'] = self.context['request'].user
        if hasattr(self.context['request'], 'tenant'):
            validated_data['tenant'] = self.context['request'].tenant
        
        return super().create(validated_data)


class WebSocketConnectionSerializer(serializers.ModelSerializer):
    """Serializer for WebSocketConnection model"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    connection_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = WebSocketConnection
        fields = [
            'id', 'user', 'user_name', 'user_email', 'connection_type',
            'channel_name', 'room_name', 'ip_address', 'user_agent',
            'is_active', 'connected_at', 'disconnected_at', 'last_activity',
            'connection_duration'
        ]
        read_only_fields = ['id', 'connected_at', 'last_activity']
    
    def get_connection_duration(self, obj):
        """Get connection duration in seconds"""
        from django.utils import timezone
        
        end_time = obj.disconnected_at if obj.disconnected_at else timezone.now()
        duration = end_time - obj.connected_at
        return int(duration.total_seconds())


class WebSocketStatsSerializer(serializers.Serializer):
    """Serializer for WebSocket connection statistics"""
    
    total_connections = serializers.IntegerField()
    active_connections = serializers.IntegerField()
    connections_by_type = serializers.DictField()
    average_connection_duration = serializers.FloatField()
    peak_concurrent_connections = serializers.IntegerField()
    recent_connections = WebSocketConnectionSerializer(many=True)