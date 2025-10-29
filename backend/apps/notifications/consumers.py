import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """Enhanced WebSocket consumer for real-time notifications through centralized API"""
    
    async def connect(self):
        """Handle WebSocket connection with authentication and tenant support"""
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            logger.warning("Anonymous user attempted WebSocket connection")
            await self.close(code=4001)
            return
        
        # Get tenant from scope if available
        self.tenant = getattr(self.scope.get('tenant'), 'id', None) if self.scope.get('tenant') else None
        
        # Join user-specific notification group
        self.notification_group_name = f"notifications_{self.user.id}"
        
        # Join tenant-specific group if tenant exists
        if self.tenant:
            self.tenant_group_name = f"tenant_{self.tenant}_notifications"
            await self.channel_layer.group_add(
                self.tenant_group_name,
                self.channel_name
            )
        
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Track WebSocket connection
        await self.track_connection()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'WebSocket connected to centralized notification API',
            'user_id': str(self.user.id),
            'tenant_id': self.tenant,
            'timestamp': timezone.now().isoformat()
        }))
        
        # Send unread count on connection
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
        
        # Update user presence
        await self.update_user_presence(True)
        
        logger.info(f"WebSocket connected for user {self.user.id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
        
        if hasattr(self, 'tenant_group_name'):
            await self.channel_layer.group_discard(
                self.tenant_group_name,
                self.channel_name
            )
        
        # Update connection tracking
        await self.untrack_connection()
        
        # Update user presence
        await self.update_user_presence(False)
        
        logger.info(f"WebSocket disconnected for user {self.user.id}")
    
    async def receive(self, text_data):
        """Handle messages from WebSocket client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_read':
                notification_id = data.get('notification_id')
                success = await self.mark_notification_read(notification_id)
                
                await self.send(text_data=json.dumps({
                    'type': 'mark_read_response',
                    'notification_id': notification_id,
                    'success': success
                }))
                
            elif message_type == 'mark_all_read':
                count = await self.mark_all_notifications_read()
                
                await self.send(text_data=json.dumps({
                    'type': 'mark_all_read_response',
                    'marked_count': count
                }))
                
            elif message_type == 'get_unread_count':
                count = await self.get_unread_count()
                
                await self.send(text_data=json.dumps({
                    'type': 'unread_count',
                    'count': count
                }))
                
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
                
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def notification_message(self, event):
        """Send notification to WebSocket client"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
    
    async def system_message(self, event):
        """Send system message to WebSocket client"""
        await self.send(text_data=json.dumps({
            'type': 'system_message',
            'message': event['message'],
            'level': event.get('level', 'info')
        }))
    
    async def broadcast_message(self, event):
        """Send broadcast message to WebSocket client"""
        await self.send(text_data=json.dumps({
            'type': 'broadcast',
            'message': event['message'],
            'title': event.get('title', 'System Announcement'),
            'priority': event.get('priority', 'normal')
        }))
    
    async def unread_count_update(self, event):
        """Send updated unread count to WebSocket client"""
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': event['count']
        }))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        try:
            from .models import Notification
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            logger.warning(f"Notification {notification_id} not found for user {self.user.id}")
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    @database_sync_to_async
    def mark_all_notifications_read(self):
        """Mark all notifications as read for the user"""
        try:
            from .models import Notification
            notifications = Notification.objects.filter(
                user=self.user,
                is_read=False
            )
            
            if hasattr(self, 'tenant') and self.tenant:
                notifications = notifications.filter(tenant_id=self.tenant)
            
            count = 0
            for notification in notifications:
                notification.mark_as_read()
                count += 1
            
            return count
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            return 0
    
    @database_sync_to_async
    def get_unread_count(self):
        """Get unread notification count for the user"""
        try:
            from .models import Notification
            queryset = Notification.objects.filter(
                user=self.user,
                is_read=False
            )
            
            if hasattr(self, 'tenant') and self.tenant:
                queryset = queryset.filter(tenant_id=self.tenant)
            
            return queryset.count()
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0
    
    @database_sync_to_async
    def track_connection(self):
        """Track WebSocket connection in database"""
        try:
            from .models import WebSocketConnection
            from django.utils import timezone
            
            # Get client IP and user agent
            headers = dict(self.scope.get('headers', []))
            user_agent = headers.get(b'user-agent', b'').decode('utf-8')
            
            # Create connection record
            WebSocketConnection.objects.create(
                user=self.user,
                connection_type='notifications',
                channel_name=self.channel_name,
                ip_address=self.scope.get('client', ['unknown'])[0],
                user_agent=user_agent,
                tenant_id=self.tenant,
                is_active=True
            )
        except Exception as e:
            logger.error(f"Error tracking connection: {e}")
    
    @database_sync_to_async
    def untrack_connection(self):
        """Update connection status on disconnect"""
        try:
            from .models import WebSocketConnection
            from django.utils import timezone
            
            connection = WebSocketConnection.objects.filter(
                user=self.user,
                channel_name=self.channel_name,
                is_active=True
            ).first()
            
            if connection:
                connection.is_active = False
                connection.disconnected_at = timezone.now()
                connection.save()
        except Exception as e:
            logger.error(f"Error untracking connection: {e}")
    
    @database_sync_to_async
    def update_user_presence(self, is_online):
        """Update user online presence status"""
        try:
            # Update user profile or create presence record
            if hasattr(self.user, 'userprofile'):
                profile = self.user.userprofile
                profile.is_online = is_online
                if is_online:
                    from django.utils import timezone
                    profile.last_seen = timezone.now()
                profile.save()
        except Exception as e:
            logger.error(f"Error updating user presence: {e}")


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat features through centralized API"""
    
    async def connect(self):
        """Handle chat WebSocket connection"""
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close(code=4001)
            return
        
        # Get room name from URL route
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Track chat connection
        await self.track_chat_connection()
        
        # Notify room that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user': {
                    'id': str(self.user.id),
                    'name': self.user.get_full_name() or self.user.email,
                    'email': self.user.email
                },
                'timestamp': timezone.now().isoformat()
            }
        )
        
        logger.info(f"User {self.user.id} joined chat room {self.room_name}")
    
    async def disconnect(self, close_code):
        """Handle chat WebSocket disconnection"""
        # Notify room that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user': {
                    'id': str(self.user.id),
                    'name': self.user.get_full_name() or self.user.email,
                    'email': self.user.email
                },
                'timestamp': timezone.now().isoformat()
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Update chat connection tracking
        await self.untrack_chat_connection()
        
        logger.info(f"User {self.user.id} left chat room {self.room_name}")
    
    async def receive(self, text_data):
        """Handle chat messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                message = data.get('message', '').strip()
                if message:
                    # Save message to database
                    chat_message = await self.save_chat_message(message)
                    
                    # Send message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': {
                                'id': str(chat_message.id),
                                'content': message,
                                'user': {
                                    'id': str(self.user.id),
                                    'name': self.user.get_full_name() or self.user.email,
                                    'email': self.user.email
                                },
                                'timestamp': chat_message.created_at.isoformat(),
                                'room': self.room_name
                            }
                        }
                    )
            
            elif message_type == 'typing':
                # Send typing indicator to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_indicator',
                        'user': {
                            'id': str(self.user.id),
                            'name': self.user.get_full_name() or self.user.email
                        },
                        'is_typing': data.get('is_typing', False)
                    }
                )
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in chat message: {e}")
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
    
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))
    
    async def user_joined(self, event):
        """Send user joined notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user': event['user'],
            'timestamp': event['timestamp']
        }))
    
    async def user_left(self, event):
        """Send user left notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user': event['user'],
            'timestamp': event['timestamp']
        }))
    
    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket"""
        # Don't send typing indicator back to the sender
        if event['user']['id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user': event['user'],
                'is_typing': event['is_typing']
            }))
    
    @database_sync_to_async
    def save_chat_message(self, message):
        """Save chat message to database"""
        from .models import ChatMessage
        return ChatMessage.objects.create(
            room_name=self.room_name,
            user=self.user,
            content=message,
            tenant=getattr(self.scope.get('tenant'), 'id', None) if self.scope.get('tenant') else None
        )
    
    @database_sync_to_async
    def track_chat_connection(self):
        """Track chat WebSocket connection"""
        try:
            from .models import WebSocketConnection
            
            # Get client IP and user agent
            headers = dict(self.scope.get('headers', []))
            user_agent = headers.get(b'user-agent', b'').decode('utf-8')
            
            WebSocketConnection.objects.create(
                user=self.user,
                connection_type='chat',
                channel_name=self.channel_name,
                room_name=self.room_name,
                ip_address=self.scope.get('client', ['unknown'])[0],
                user_agent=user_agent,
                tenant=getattr(self.scope.get('tenant'), 'id', None) if self.scope.get('tenant') else None,
                is_active=True
            )
        except Exception as e:
            logger.error(f"Error tracking chat connection: {e}")
    
    @database_sync_to_async
    def untrack_chat_connection(self):
        """Update chat connection status on disconnect"""
        try:
            from .models import WebSocketConnection
            from django.utils import timezone
            
            connection = WebSocketConnection.objects.filter(
                user=self.user,
                channel_name=self.channel_name,
                connection_type='chat',
                is_active=True
            ).first()
            
            if connection:
                connection.is_active = False
                connection.disconnected_at = timezone.now()
                connection.save()
        except Exception as e:
            logger.error(f"Error untracking chat connection: {e}")