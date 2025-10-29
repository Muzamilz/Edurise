from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from apps.common.responses import StandardAPIResponse
from .models import Notification, EmailDeliveryLog, NotificationTemplate, ChatMessage, WebSocketConnection
from .serializers import (
    NotificationSerializer, NotificationCreateSerializer, 
    NotificationStatsSerializer, NotificationPreferencesSerializer,
    EmailDeliveryLogSerializer, NotificationTemplateSerializer,
    EmailTemplateListSerializer, ChatMessageSerializer, ChatMessageCreateSerializer,
    WebSocketConnectionSerializer, WebSocketStatsSerializer,
    NotificationLanguageSerializer, LocalizedNotificationPreferencesSerializer
)
from .services import EmailService, WebSocketNotificationService
from .i18n_service import NotificationI18nService

User = get_user_model()


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notification model with centralized API integration"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    def get_queryset(self):
        """Filter notifications by tenant and user with optimizations"""
        queryset = Notification.objects.select_related('user').filter(user=self.request.user)
        
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = queryset.filter(tenant=self.request.tenant)
        
        # Apply filters
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """List notifications with standardized response"""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Notifications retrieved successfully"
        )
    
    def create(self, request, *args, **kwargs):
        """Create notification with standardized response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()
        
        response_serializer = NotificationSerializer(notification)
        return StandardAPIResponse.success(
            data=response_serializer.data,
            message="Notification created successfully",
            status_code=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        
        serializer = self.get_serializer(notification)
        return StandardAPIResponse.success(
            data=serializer.data,
            message='Notification marked as read'
        )
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        notifications = self.get_queryset().filter(is_read=False)
        count = 0
        
        for notification in notifications:
            notification.mark_as_read()
            count += 1
        
        return StandardAPIResponse.success(
            data={'marked_count': count},
            message=f'{count} notifications marked as read'
        )
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = self.get_queryset().filter(is_read=False).count()
        return StandardAPIResponse.success(
            data={'unread_count': count},
            message="Unread count retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get notification statistics"""
        queryset = self.get_queryset()
        
        total_notifications = queryset.count()
        unread_notifications = queryset.filter(is_read=False).count()
        read_notifications = total_notifications - unread_notifications
        
        # Get notifications by type
        notifications_by_type = dict(
            queryset.values('notification_type')
            .annotate(count=Count('id'))
            .values_list('notification_type', 'count')
        )
        
        # Get recent notifications (last 10)
        recent_notifications = queryset[:10]
        
        stats_data = {
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'read_notifications': read_notifications,
            'notifications_by_type': notifications_by_type,
            'recent_notifications': NotificationSerializer(recent_notifications, many=True).data
        }
        
        return StandardAPIResponse.success(
            data=stats_data,
            message="Notification statistics retrieved successfully"
        )
    
    @action(detail=False, methods=['get', 'put'])
    def preferences(self, request):
        """Get or update notification preferences"""
        user = request.user
        
        if request.method == 'GET':
            # Get current preferences from user profile
            preferences = {}
            if hasattr(user, 'userprofile') and user.userprofile.notification_preferences:
                preferences = user.userprofile.notification_preferences
            else:
                # Default preferences
                preferences = {
                    'email_notifications': True,
                    'push_notifications': True,
                    'course_enrollment_notifications': True,
                    'class_reminder_notifications': True,
                    'assignment_due_notifications': True,
                    'payment_notifications': True,
                    'system_notifications': True,
                }
            
            return StandardAPIResponse.success(
                data=preferences,
                message="Notification preferences retrieved successfully"
            )
        
        elif request.method == 'PUT':
            # Update preferences
            serializer = NotificationPreferencesSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.update(user, serializer.validated_data)
            
            return StandardAPIResponse.success(
                data=serializer.validated_data,
                message="Notification preferences updated successfully"
            )
    
    @action(detail=False, methods=['delete'])
    def clear_read(self, request):
        """Clear all read notifications"""
        deleted_count = self.get_queryset().filter(is_read=True).delete()[0]
        
        return StandardAPIResponse.success(
            data={'deleted_count': deleted_count},
            message=f'{deleted_count} read notifications cleared'
        )
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get notifications grouped by type"""
        queryset = self.get_queryset()
        
        # Group notifications by type
        grouped_notifications = {}
        for notification_type, _ in Notification.TYPE_CHOICES:
            type_notifications = queryset.filter(notification_type=notification_type)
            if type_notifications.exists():
                grouped_notifications[notification_type] = NotificationSerializer(
                    type_notifications, many=True
                ).data
        
        return StandardAPIResponse.success(
            data=grouped_notifications,
            message="Notifications grouped by type retrieved successfully"
        )
    
    @action(detail=True, methods=['get'])
    def delivery_status(self, request, pk=None):
        """Get delivery status for a specific notification"""
        notification = self.get_object()
        
        from .services import NotificationDeliveryTracker
        delivery_stats = NotificationDeliveryTracker.get_delivery_stats(notification)
        
        return StandardAPIResponse.success(
            data=delivery_stats,
            message="Notification delivery status retrieved successfully"
        )
    
    @action(detail=False, methods=['post'])
    def retry_failed(self, request):
        """Retry failed notification deliveries"""
        if not request.user.is_staff:
            return StandardAPIResponse.error(
                message="Only staff can retry failed deliveries",
                status_code=403
            )
        
        from .services import NotificationDeliveryTracker
        retry_count = NotificationDeliveryTracker.retry_failed_deliveries()
        
        return StandardAPIResponse.success(
            data={'retried_count': retry_count},
            message=f"Retried {retry_count} failed deliveries"
        )
    
    @action(detail=False, methods=['post'])
    def push_subscription(self, request):
        """Handle push notification subscription"""
        subscription_data = request.data.get('subscription')
        if not subscription_data:
            return StandardAPIResponse.error(
                message="Subscription data is required",
                status_code=400
            )
        
        # Store subscription data in user profile or separate model
        # For now, we'll just return success
        return StandardAPIResponse.success(
            data={'subscribed': True},
            message="Push notification subscription saved successfully"
        )
    
    @action(detail=False, methods=['delete'])
    def push_subscription(self, request):
        """Handle push notification unsubscription"""
        subscription_data = request.data.get('subscription')
        if not subscription_data:
            return StandardAPIResponse.error(
                message="Subscription data is required",
                status_code=400
            )
        
        # Remove subscription data
        # For now, we'll just return success
        return StandardAPIResponse.success(
            data={'unsubscribed': True},
            message="Push notification subscription removed successfully"
        )
    
    @action(detail=False, methods=['get'])
    def email_analytics(self, request):
        """Get email notification analytics"""
        if not request.user.is_staff:
            return StandardAPIResponse.error(
                message="Only staff can view email analytics",
                status_code=403
            )
        
        from .services import EmailAutomationService
        analytics = EmailAutomationService.get_email_analytics()
        
        return StandardAPIResponse.success(
            data=analytics,
            message="Email analytics retrieved successfully"
        )
    
    @action(detail=False, methods=['post'])
    def trigger_automation(self, request):
        """Trigger automated notification for testing"""
        if not request.user.is_staff:
            return StandardAPIResponse.error(
                message="Only staff can trigger automated notifications",
                status_code=403
            )
        
        event_type = request.data.get('event_type')
        user_id = request.data.get('user_id')
        context_data = request.data.get('context_data', {})
        
        if not event_type or not user_id:
            return StandardAPIResponse.error(
                message="event_type and user_id are required",
                status_code=400
            )
        
        try:
            from django.contrib.auth import get_user_model
            from .services import EmailAutomationService
            
            User = get_user_model()
            user = User.objects.get(id=user_id)
            
            success = EmailAutomationService.trigger_event_notification(
                event_type, user, context_data
            )
            
            if success:
                return StandardAPIResponse.success(
                    message="Automated notification triggered successfully"
                )
            else:
                return StandardAPIResponse.error(
                    message="Failed to trigger automated notification",
                    status_code=500
                )
                
        except User.DoesNotExist:
            return StandardAPIResponse.error(
                message="User not found",
                status_code=404
            )
        except Exception as e:
            return StandardAPIResponse.error(
                message=f"Error triggering notification: {str(e)}",
                status_code=500
            )
    
    @action(detail=False, methods=['get'])
    def supported_languages(self, request):
        """Get supported notification languages"""
        languages = []
        for code, name in NotificationI18nService.get_all_supported_languages().items():
            languages.append({
                'code': code,
                'name': name,
                'is_rtl': NotificationI18nService.is_rtl_language(code)
            })
        
        serializer = NotificationLanguageSerializer(languages, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Supported languages retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def localized_preferences(self, request):
        """Get localized notification preference labels"""
        language = request.query_params.get('language', 'en')
        
        if language not in NotificationI18nService.get_all_supported_languages():
            return StandardAPIResponse.error(
                message="Unsupported language",
                status_code=400
            )
        
        data = {'language': language}
        serializer = LocalizedNotificationPreferencesSerializer(data)
        
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Localized preference labels retrieved successfully"
        )


class EmailDeliveryLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for EmailDeliveryLog model - read-only for monitoring"""
    
    serializer_class = EmailDeliveryLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter email logs by tenant and user notifications"""
        queryset = EmailDeliveryLog.objects.select_related('notification', 'notification__user')
        
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = queryset.filter(tenant=self.request.tenant)
        
        # Users can only see logs for their own notifications
        if not self.request.user.is_staff:
            queryset = queryset.filter(notification__user=self.request.user)
        
        return queryset.order_by('-sent_at')
    
    @action(detail=False, methods=['get'])
    def delivery_stats(self, request):
        """Get email delivery statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_emails': queryset.count(),
            'sent_emails': queryset.filter(status='sent').count(),
            'failed_emails': queryset.filter(status='failed').count(),
            'delivered_emails': queryset.filter(status='delivered').count(),
            'opened_emails': queryset.filter(status='opened').count(),
            'clicked_emails': queryset.filter(status='clicked').count(),
        }
        
        # Calculate rates
        if stats['total_emails'] > 0:
            stats['delivery_rate'] = round((stats['delivered_emails'] / stats['total_emails']) * 100, 2)
            stats['open_rate'] = round((stats['opened_emails'] / stats['total_emails']) * 100, 2)
            stats['click_rate'] = round((stats['clicked_emails'] / stats['total_emails']) * 100, 2)
        else:
            stats['delivery_rate'] = 0
            stats['open_rate'] = 0
            stats['click_rate'] = 0
        
        return StandardAPIResponse.success(
            data=stats,
            message="Email delivery statistics retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def delivery_trends(self, request):
        """Get email delivery trends over time"""
        queryset = self.get_queryset()
        
        from django.db.models import Count, Q
        from django.utils import timezone
        from datetime import timedelta
        
        # Get trends for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Group by day
        daily_stats = []
        for i in range(30):
            day = thirty_days_ago + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_logs = queryset.filter(sent_at__gte=day_start, sent_at__lt=day_end)
            
            daily_stats.append({
                'date': day_start.date().isoformat(),
                'total_sent': day_logs.count(),
                'successful': day_logs.filter(status__in=['sent', 'delivered']).count(),
                'failed': day_logs.filter(status='failed').count(),
                'opened': day_logs.filter(status='opened').count(),
                'clicked': day_logs.filter(status='clicked').count()
            })
        
        return StandardAPIResponse.success(
            data=daily_stats,
            message="Email delivery trends retrieved successfully"
        )


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for NotificationTemplate model"""
    
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter templates by tenant"""
        queryset = NotificationTemplate.objects.all()
        
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = queryset.filter(tenant=self.request.tenant)
        
        # Only staff can manage templates
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('notification_type', 'name')
    
    @action(detail=False, methods=['get'])
    def available_templates(self, request):
        """Get list of available email templates"""
        templates = EmailService.get_available_templates()
        
        template_data = []
        for template_name in templates:
            template_data.append({
                'template_name': template_name,
                'display_name': template_name.replace('_', ' ').title(),
                'notification_type': template_name,
                'is_available': EmailService.validate_template(template_name)
            })
        
        serializer = EmailTemplateListSerializer(template_data, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Available email templates retrieved successfully"
        )
    
    @action(detail=True, methods=['post'])
    def test_template(self, request, pk=None):
        """Test email template by sending a test email"""
        template = self.get_object()
        
        # Create a test notification
        test_notification = Notification(
            user=request.user,
            title="Test Email Template",
            message="This is a test email to verify the template works correctly.",
            notification_type=template.notification_type,
            tenant=request.tenant if hasattr(request, 'tenant') else None
        )
        
        try:
            success = EmailService.send_notification_email(test_notification)
            
            if success:
                return StandardAPIResponse.success(
                    data={'sent': True},
                    message="Test email sent successfully"
                )
            else:
                return StandardAPIResponse.error(
                    message="Failed to send test email",
                    status_code=500
                )
        except Exception as e:
            return StandardAPIResponse.error(
                message=f"Error sending test email: {str(e)}",
                status_code=500
            )


class ChatMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for ChatMessage model with real-time chat features"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ChatMessageCreateSerializer
        return ChatMessageSerializer
    
    def get_queryset(self):
        """Filter chat messages by room and tenant"""
        queryset = ChatMessage.objects.select_related('user').filter(is_deleted=False)
        
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = queryset.filter(tenant=self.request.tenant)
        
        # Filter by room if specified
        room_name = self.request.query_params.get('room')
        if room_name:
            queryset = queryset.filter(room_name=room_name)
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Create chat message and send real-time notification"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        
        # Send real-time message via WebSocket
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            if channel_layer:
                room_group_name = f'chat_{message.room_name}'
                
                async_to_sync(channel_layer.group_send)(
                    room_group_name,
                    {
                        'type': 'chat_message',
                        'message': {
                            'id': str(message.id),
                            'content': message.content,
                            'user': {
                                'id': str(message.user.id),
                                'name': message.user.get_full_name() or message.user.email,
                                'email': message.user.email
                            },
                            'timestamp': message.created_at.isoformat(),
                            'room': message.room_name
                        }
                    }
                )
        except Exception as e:
            print(f"Failed to send real-time chat message: {str(e)}")
        
        response_serializer = ChatMessageSerializer(message)
        return StandardAPIResponse.success(
            data=response_serializer.data,
            message="Chat message sent successfully",
            status_code=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['put'])
    def edit_message(self, request, pk=None):
        """Edit chat message"""
        message = self.get_object()
        
        # Only allow user to edit their own messages
        if message.user != request.user:
            return StandardAPIResponse.error(
                message="You can only edit your own messages",
                status_code=403
            )
        
        new_content = request.data.get('content', '').strip()
        if not new_content:
            return StandardAPIResponse.error(
                message="Message content cannot be empty",
                status_code=400
            )
        
        from django.utils import timezone
        message.content = new_content
        message.is_edited = True
        message.edited_at = timezone.now()
        message.save()
        
        serializer = self.get_serializer(message)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Message edited successfully"
        )
    
    @action(detail=True, methods=['delete'])
    def delete_message(self, request, pk=None):
        """Soft delete chat message"""
        message = self.get_object()
        
        # Only allow user to delete their own messages or staff
        if message.user != request.user and not request.user.is_staff:
            return StandardAPIResponse.error(
                message="You can only delete your own messages",
                status_code=403
            )
        
        from django.utils import timezone
        message.is_deleted = True
        message.deleted_at = timezone.now()
        message.save()
        
        return StandardAPIResponse.success(
            message="Message deleted successfully"
        )
    
    @action(detail=False, methods=['get'])
    def room_history(self, request):
        """Get chat history for a specific room"""
        room_name = request.query_params.get('room')
        if not room_name:
            return StandardAPIResponse.error(
                message="Room name is required",
                status_code=400
            )
        
        messages = self.get_queryset().filter(room_name=room_name)[:50]
        serializer = self.get_serializer(messages, many=True)
        
        return StandardAPIResponse.success(
            data=serializer.data,
            message=f"Chat history for room '{room_name}' retrieved successfully"
        )


class WebSocketConnectionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for WebSocketConnection model - monitoring only"""
    
    serializer_class = WebSocketConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter WebSocket connections by tenant and permissions"""
        queryset = WebSocketConnection.objects.select_related('user')
        
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = queryset.filter(tenant=self.request.tenant)
        
        # Regular users can only see their own connections
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset.order_by('-connected_at')
    
    @action(detail=False, methods=['get'])
    def active_connections(self, request):
        """Get currently active WebSocket connections"""
        active_connections = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_connections, many=True)
        
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Active WebSocket connections retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def connection_stats(self, request):
        """Get WebSocket connection statistics"""
        queryset = self.get_queryset()
        
        total_connections = queryset.count()
        active_connections = queryset.filter(is_active=True).count()
        
        # Connections by type
        from django.db.models import Count
        connections_by_type = dict(
            queryset.values('connection_type')
            .annotate(count=Count('id'))
            .values_list('connection_type', 'count')
        )
        
        # Average connection duration
        from django.db.models import Avg, F
        avg_duration = queryset.filter(disconnected_at__isnull=False).aggregate(
            avg_duration=Avg(F('disconnected_at') - F('connected_at'))
        )['avg_duration']
        
        avg_duration_seconds = avg_duration.total_seconds() if avg_duration else 0
        
        # Recent connections
        recent_connections = queryset[:10]
        
        stats_data = {
            'total_connections': total_connections,
            'active_connections': active_connections,
            'connections_by_type': connections_by_type,
            'average_connection_duration': avg_duration_seconds,
            'peak_concurrent_connections': active_connections,  # Simplified for now
            'recent_connections': WebSocketConnectionSerializer(recent_connections, many=True).data
        }
        
        return StandardAPIResponse.success(
            data=stats_data,
            message="WebSocket connection statistics retrieved successfully"
        )
    
    @action(detail=False, methods=['post'])
    def send_broadcast(self, request):
        """Send broadcast message to all connected users"""
        if not request.user.is_staff:
            return StandardAPIResponse.error(
                message="Only staff can send broadcast messages",
                status_code=403
            )
        
        message = request.data.get('message', '').strip()
        title = request.data.get('title', 'System Announcement')
        priority = request.data.get('priority', 'normal')
        
        if not message:
            return StandardAPIResponse.error(
                message="Message content is required",
                status_code=400
            )
        
        # Send broadcast via WebSocket
        from django.utils import timezone
        tenant = request.tenant if hasattr(request, 'tenant') else None
        success = WebSocketNotificationService.send_system_broadcast(
            {
                'title': title,
                'message': message,
                'priority': priority,
                'timestamp': timezone.now().isoformat()
            },
            tenant=tenant
        )
        
        if success:
            return StandardAPIResponse.success(
                message="Broadcast message sent successfully"
            )
        else:
            return StandardAPIResponse.error(
                message="Failed to send broadcast message",
                status_code=500
            )