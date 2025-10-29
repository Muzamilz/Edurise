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

    def broadcast_assignment_submission(self, assignment_id, submission_data):
        """Broadcast assignment submission to relevant users"""
        # Send to course instructors
        course_id = submission_data.get('course_id')
        if course_id:
            instructor_group = f'course_instructors_{course_id}'
            message = {
                'type': 'assignment_submitted',
                'data': {
                    'assignment_id': assignment_id,
                    'submission_id': submission_data.get('submission_id'),
                    'student_name': submission_data.get('student_name'),
                    'assignment_title': submission_data.get('assignment_title'),
                    'submitted_at': submission_data.get('submitted_at'),
                    'late': submission_data.get('late', False),
                    'timestamp': timezone.now().isoformat()
                }
            }
            self._send_to_group(instructor_group, message)

    def broadcast_grade_update(self, assignment_id, grade_data):
        """Broadcast grade update to student"""
        student_id = grade_data.get('student_id')
        if student_id:
            student_group = f'notifications_{student_id}'
            message = {
                'type': 'assignment_graded',
                'data': {
                    'assignment_id': assignment_id,
                    'grade_id': grade_data.get('grade_id'),
                    'assignment_title': grade_data.get('assignment_title'),
                    'score': grade_data.get('score'),
                    'max_score': grade_data.get('max_score'),
                    'feedback': grade_data.get('feedback'),
                    'graded_at': grade_data.get('graded_at'),
                    'timestamp': timezone.now().isoformat()
                }
            }
            self._send_to_group(student_group, message)

    def broadcast_course_enrollment(self, course_id, enrollment_data):
        """Broadcast course enrollment to instructors"""
        instructor_group = f'course_instructors_{course_id}'
        message = {
            'type': 'course_enrolled',
            'data': {
                'course_id': course_id,
                'enrollment_id': enrollment_data.get('enrollment_id'),
                'student_name': enrollment_data.get('student_name'),
                'course_title': enrollment_data.get('course_title'),
                'enrolled_at': enrollment_data.get('enrolled_at'),
                'timestamp': timezone.now().isoformat()
            }
        }
        self._send_to_group(instructor_group, message)

    def broadcast_system_announcement(self, announcement_data, target_groups=None):
        """Broadcast system announcement to specified groups or all users"""
        message = {
            'type': 'system_announcement',
            'data': {
                'announcement_id': announcement_data.get('announcement_id'),
                'title': announcement_data.get('title'),
                'message': announcement_data.get('message'),
                'priority': announcement_data.get('priority', 'normal'),
                'created_at': announcement_data.get('created_at'),
                'timestamp': timezone.now().isoformat()
            }
        }
        
        if target_groups:
            for group in target_groups:
                self._send_to_group(group, message)
        else:
            # Broadcast to all notification groups (this would need to be implemented
            # based on your specific requirements for system-wide broadcasts)
            logger.info("System announcement broadcast to all users")

    def broadcast_user_status_update(self, user_id, status_data):
        """Broadcast user status update to relevant groups"""
        # This could be sent to course groups, class groups, etc.
        # depending on your application's needs
        message = {
            'type': 'user_status_update',
            'data': {
                'user_id': user_id,
                'user_name': status_data.get('user_name'),
                'user_role': status_data.get('user_role'),
                'status': status_data.get('status'),
                'timestamp': timezone.now().isoformat()
            }
        }
        
        # Send to general notification groups or specific course groups
        # This implementation would depend on your specific requirements
        logger.info(f"User status update for user {user_id}: {status_data.get('status')}")

    def send_recording_status_update(self, live_class_id, recording_status):
        """Send recording status update to class participants"""
        group_name = f'live_class_{live_class_id}'
        
        message = {
            'type': 'recording_status',
            'data': {
                'status': recording_status,
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


def broadcast_assignment_submission(assignment_id, submission_data):
    """Convenience function to broadcast assignment submission"""
    websocket_service.broadcast_assignment_submission(assignment_id, submission_data)


def broadcast_grade_update(assignment_id, grade_data):
    """Convenience function to broadcast grade update"""
    websocket_service.broadcast_grade_update(assignment_id, grade_data)


def broadcast_course_enrollment(course_id, enrollment_data):
    """Convenience function to broadcast course enrollment"""
    websocket_service.broadcast_course_enrollment(course_id, enrollment_data)


def broadcast_system_announcement(announcement_data, target_groups=None):
    """Convenience function to broadcast system announcement"""
    websocket_service.broadcast_system_announcement(announcement_data, target_groups)


def broadcast_user_status_update(user_id, status_data):
    """Convenience function to broadcast user status update"""
    websocket_service.broadcast_user_status_update(user_id, status_data)


def send_recording_status_update(live_class_id, recording_status):
    """Convenience function to send recording status update"""
    websocket_service.send_recording_status_update(live_class_id, recording_status)