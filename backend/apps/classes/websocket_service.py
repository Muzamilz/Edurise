import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

logger = logging.getLogger(__name__)


class LiveClassWebSocketService:
    """Service for broadcasting WebSocket messages to live class participants"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def broadcast_class_status_update(self, live_class_id, status, additional_data=None):
        """Broadcast class status update to all participants"""
        group_name = f'live_class_{live_class_id}'
        
        data = {
            'status': status,
            'timestamp': timezone.now().isoformat()
        }
        
        if additional_data:
            data.update(additional_data)
        
        message = {
            'type': 'class_status_update',
            'data': data
        }
        
        self._send_to_group(group_name, message)
    
    def broadcast_attendance_update(self, live_class_id, attendance_data):
        """Broadcast attendance update to participants"""
        group_name = f'live_class_{live_class_id}'
        
        message = {
            'type': 'attendance_update',
            'data': {
                'attendance': attendance_data,
                'timestamp': timezone.now().isoformat()
            }
        }
        
        self._send_to_group(group_name, message)
    
    def broadcast_participant_joined(self, live_class_id, user_data):
        """Broadcast when a participant joins"""
        group_name = f'live_class_{live_class_id}'
        
        message = {
            'type': 'participant_joined',
            'data': {
                **user_data,
                'timestamp': timezone.now().isoformat()
            }
        }
        
        self._send_to_group(group_name, message)
    
    def broadcast_participant_left(self, live_class_id, user_data):
        """Broadcast when a participant leaves"""
        group_name = f'live_class_{live_class_id}'
        
        message = {
            'type': 'participant_left',
            'data': {
                **user_data,
                'timestamp': timezone.now().isoformat()
            }
        }
        
        self._send_to_group(group_name, message)
    
    def broadcast_engagement_update(self, live_class_id, metrics):
        """Broadcast engagement metrics update"""
        group_name = f'live_class_{live_class_id}'
        
        message = {
            'type': 'engagement_update',
            'data': {
                'metrics': metrics,
                'timestamp': timezone.now().isoformat()
            }
        }
        
        self._send_to_group(group_name, message)
    
    def broadcast_question_asked(self, live_class_id, question_data):
        """Broadcast when a question is asked"""
        group_name = f'live_class_{live_class_id}'
        
        message = {
            'type': 'question_asked',
            'data': {
                **question_data,
                'timestamp': timezone.now().isoformat()
            }
        }
        
        self._send_to_group(group_name, message)
    
    def broadcast_announcement(self, live_class_id, announcement):
        """Broadcast instructor announcement"""
        group_name = f'live_class_{live_class_id}'
        
        message = {
            'type': 'class_announcement',
            'data': {
                'message': announcement,
                'timestamp': timezone.now().isoformat()
            }
        }
        
        self._send_to_group(group_name, message)
    
    def send_instructor_dashboard_update(self, live_class_id, dashboard_data):
        """Send dashboard update to instructor"""
        group_name = f'instructor_live_class_{live_class_id}'
        
        message = {
            'type': 'dashboard_update',
            'data': {
                'dashboard': dashboard_data,
                'timestamp': timezone.now().isoformat()
            }
        }
        
        self._send_to_group(group_name, message)
    
    def send_attendance_report(self, live_class_id, report_data):
        """Send attendance report to instructor"""
        group_name = f'instructor_live_class_{live_class_id}'
        
        message = {
            'type': 'attendance_report',
            'data': {
                'report': report_data,
                'timestamp': timezone.now().isoformat()
            }
        }
        
        self._send_to_group(group_name, message)
    
    def _send_to_group(self, group_name, message):
        """Send message to WebSocket group"""
        if self.channel_layer:
            try:
                async_to_sync(self.channel_layer.group_send)(group_name, message)
                logger.info(f"Sent WebSocket message to group {group_name}: {message['type']}")
            except Exception as e:
                logger.error(f"Failed to send WebSocket message to group {group_name}: {str(e)}")
        else:
            logger.warning("Channel layer not available, cannot send WebSocket message")


# Singleton instance
websocket_service = LiveClassWebSocketService()


# Convenience functions for easy import
def broadcast_class_status_update(live_class_id, status, additional_data=None):
    """Convenience function to broadcast class status update"""
    websocket_service.broadcast_class_status_update(live_class_id, status, additional_data)


def broadcast_attendance_update(live_class_id, attendance_data):
    """Convenience function to broadcast attendance update"""
    websocket_service.broadcast_attendance_update(live_class_id, attendance_data)


def broadcast_participant_joined(live_class_id, user_data):
    """Convenience function to broadcast participant joined"""
    websocket_service.broadcast_participant_joined(live_class_id, user_data)


def broadcast_participant_left(live_class_id, user_data):
    """Convenience function to broadcast participant left"""
    websocket_service.broadcast_participant_left(live_class_id, user_data)


def broadcast_engagement_update(live_class_id, metrics):
    """Convenience function to broadcast engagement update"""
    websocket_service.broadcast_engagement_update(live_class_id, metrics)


def send_instructor_dashboard_update(live_class_id, dashboard_data):
    """Convenience function to send instructor dashboard update"""
    websocket_service.send_instructor_dashboard_update(live_class_id, dashboard_data)