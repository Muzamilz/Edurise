import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from apps.courses.models import LiveClass
from .models import ClassAttendance

User = get_user_model()
logger = logging.getLogger(__name__)


class LiveClassConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for live class real-time updates"""
    
    async def connect(self):
        """Handle WebSocket connection for live class"""
        self.user = self.scope["user"]
        self.live_class_id = self.scope['url_route']['kwargs']['live_class_id']
        self.live_class_group_name = f'live_class_{self.live_class_id}'
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Verify user has access to this live class
        has_access = await self.check_class_access()
        if not has_access:
            await self.close()
            return
        
        # Join live class group
        await self.channel_layer.group_add(
            self.live_class_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial class status
        await self.send_class_status()
        
        logger.info(f"User {self.user.id} connected to live class {self.live_class_id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'live_class_group_name'):
            await self.channel_layer.group_discard(
                self.live_class_group_name,
                self.channel_name
            )
        
        logger.info(f"User {self.user.id} disconnected from live class {self.live_class_id}")
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': text_data_json.get('timestamp')
                }))
            
            elif message_type == 'join_class':
                await self.handle_join_class()
            
            elif message_type == 'leave_class':
                await self.handle_leave_class()
            
            elif message_type == 'update_participation':
                await self.handle_participation_update(text_data_json.get('data', {}))
            
            elif message_type == 'ask_question':
                await self.handle_question(text_data_json.get('data', {}))
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from user {self.user.id}")
        except Exception as e:
            logger.error(f"Error handling message from user {self.user.id}: {str(e)}")
    
    # Group message handlers
    async def class_status_update(self, event):
        """Send class status update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'class_status_update',
            'data': event['data']
        }))
    
    async def attendance_update(self, event):
        """Send attendance update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'attendance_update',
            'data': event['data']
        }))
    
    async def participant_joined(self, event):
        """Send participant joined notification"""
        await self.send(text_data=json.dumps({
            'type': 'participant_joined',
            'data': event['data']
        }))
    
    async def participant_left(self, event):
        """Send participant left notification"""
        await self.send(text_data=json.dumps({
            'type': 'participant_left',
            'data': event['data']
        }))
    
    async def engagement_update(self, event):
        """Send engagement metrics update"""
        await self.send(text_data=json.dumps({
            'type': 'engagement_update',
            'data': event['data']
        }))
    
    async def question_asked(self, event):
        """Send new question notification"""
        await self.send(text_data=json.dumps({
            'type': 'question_asked',
            'data': event['data']
        }))
    
    async def class_announcement(self, event):
        """Send class announcement"""
        await self.send(text_data=json.dumps({
            'type': 'class_announcement',
            'data': event['data']
        }))
    
    # Helper methods
    @database_sync_to_async
    def check_class_access(self):
        """Check if user has access to the live class"""
        try:
            live_class = LiveClass.objects.get(id=self.live_class_id)
            
            # Check if user is instructor
            if live_class.course.instructor == self.user:
                return True
            
            # Check if user is enrolled in the course
            from apps.courses.models import Enrollment
            enrollment = Enrollment.objects.filter(
                course=live_class.course,
                student=self.user,
                status='active'
            ).exists()
            
            return enrollment
            
        except LiveClass.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_class_status(self):
        """Get current class status"""
        try:
            live_class = LiveClass.objects.get(id=self.live_class_id)
            return {
                'id': str(live_class.id),
                'title': live_class.title,
                'status': live_class.status,
                'scheduled_at': live_class.scheduled_at.isoformat() if live_class.scheduled_at else None,
                'duration_minutes': live_class.duration_minutes,
                'zoom_meeting_id': live_class.zoom_meeting_id,
                'join_url': live_class.join_url if self.user != live_class.course.instructor else live_class.start_url,
                'participant_count': self.get_participant_count(live_class)
            }
        except LiveClass.DoesNotExist:
            return None
    
    def get_participant_count(self, live_class):
        """Get current participant count"""
        return ClassAttendance.objects.filter(
            live_class=live_class,
            status__in=['present', 'partial']
        ).count()
    
    async def send_class_status(self):
        """Send current class status to client"""
        status = await self.get_class_status()
        if status:
            await self.send(text_data=json.dumps({
                'type': 'class_status',
                'data': status
            }))
    
    async def handle_join_class(self):
        """Handle user joining the class"""
        await self.mark_attendance('present')
        
        # Notify other participants
        await self.channel_layer.group_send(
            self.live_class_group_name,
            {
                'type': 'participant_joined',
                'data': {
                    'user_id': str(self.user.id),
                    'user_name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.email,
                    'timestamp': self.get_current_timestamp()
                }
            }
        )
    
    async def handle_leave_class(self):
        """Handle user leaving the class"""
        await self.mark_attendance('absent')
        
        # Notify other participants
        await self.channel_layer.group_send(
            self.live_class_group_name,
            {
                'type': 'participant_left',
                'data': {
                    'user_id': str(self.user.id),
                    'user_name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.email,
                    'timestamp': self.get_current_timestamp()
                }
            }
        )
    
    async def handle_participation_update(self, data):
        """Handle participation score update"""
        score = data.get('score', 0)
        await self.update_participation_score(score)
        
        # Send engagement update to instructor
        await self.send_engagement_update()
    
    async def handle_question(self, data):
        """Handle student question"""
        question_text = data.get('question', '')
        if question_text:
            await self.record_question(question_text)
            
            # Notify instructor and other participants
            await self.channel_layer.group_send(
                self.live_class_group_name,
                {
                    'type': 'question_asked',
                    'data': {
                        'user_id': str(self.user.id),
                        'user_name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.email,
                        'question': question_text,
                        'timestamp': self.get_current_timestamp()
                    }
                }
            )
    
    @database_sync_to_async
    def mark_attendance(self, status):
        """Mark user attendance"""
        from django.utils import timezone
        from .services import AttendanceService
        
        try:
            live_class = LiveClass.objects.get(id=self.live_class_id)
            AttendanceService.mark_attendance(
                live_class=live_class,
                student=self.user,
                status=status,
                join_time=timezone.now() if status == 'present' else None
            )
        except Exception as e:
            logger.error(f"Error marking attendance: {str(e)}")
    
    @database_sync_to_async
    def update_participation_score(self, score):
        """Update user participation score"""
        try:
            attendance = ClassAttendance.objects.get(
                live_class_id=self.live_class_id,
                student=self.user
            )
            attendance.participation_score = max(attendance.participation_score, score)
            attendance.save()
        except ClassAttendance.DoesNotExist:
            pass
    
    @database_sync_to_async
    def record_question(self, question_text):
        """Record student question"""
        try:
            attendance = ClassAttendance.objects.get(
                live_class_id=self.live_class_id,
                student=self.user
            )
            attendance.questions_asked += 1
            attendance.save()
        except ClassAttendance.DoesNotExist:
            pass
    
    async def send_engagement_update(self):
        """Send engagement metrics update"""
        metrics = await self.get_engagement_metrics()
        if metrics:
            await self.channel_layer.group_send(
                self.live_class_group_name,
                {
                    'type': 'engagement_update',
                    'data': metrics
                }
            )
    
    @database_sync_to_async
    def get_engagement_metrics(self):
        """Get current engagement metrics"""
        try:
            from .services import AttendanceService
            live_class = LiveClass.objects.get(id=self.live_class_id)
            return AttendanceService.calculate_engagement_metrics(live_class)
        except Exception as e:
            logger.error(f"Error getting engagement metrics: {str(e)}")
            return None
    
    def get_current_timestamp(self):
        """Get current timestamp in ISO format"""
        from django.utils import timezone
        return timezone.now().isoformat()


class LiveClassInstructorConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for instructor-specific live class features"""
    
    async def connect(self):
        """Handle WebSocket connection for instructor"""
        self.user = self.scope["user"]
        self.live_class_id = self.scope['url_route']['kwargs']['live_class_id']
        self.instructor_group_name = f'instructor_live_class_{self.live_class_id}'
        
        # Check if user is authenticated and is instructor
        if not self.user.is_authenticated:
            await self.close()
            return
        
        is_instructor = await self.check_instructor_access()
        if not is_instructor:
            await self.close()
            return
        
        # Join instructor group
        await self.channel_layer.group_add(
            self.instructor_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial dashboard data
        await self.send_dashboard_data()
        
        logger.info(f"Instructor {self.user.id} connected to live class {self.live_class_id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'instructor_group_name'):
            await self.channel_layer.group_discard(
                self.instructor_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'start_class':
                await self.handle_start_class()
            
            elif message_type == 'end_class':
                await self.handle_end_class()
            
            elif message_type == 'send_announcement':
                await self.handle_announcement(text_data_json.get('data', {}))
            
            elif message_type == 'update_attendance':
                await self.handle_attendance_update(text_data_json.get('data', {}))
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from instructor {self.user.id}")
        except Exception as e:
            logger.error(f"Error handling instructor message: {str(e)}")
    
    # Group message handlers
    async def dashboard_update(self, event):
        """Send dashboard update to instructor"""
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': event['data']
        }))
    
    async def attendance_report(self, event):
        """Send attendance report to instructor"""
        await self.send(text_data=json.dumps({
            'type': 'attendance_report',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def check_instructor_access(self):
        """Check if user is instructor for this class"""
        try:
            live_class = LiveClass.objects.get(id=self.live_class_id)
            return live_class.course.instructor == self.user
        except LiveClass.DoesNotExist:
            return False
    
    async def handle_start_class(self):
        """Handle starting the class"""
        await self.update_class_status('live')
        
        # Notify all participants
        await self.broadcast_class_update('live')
    
    async def handle_end_class(self):
        """Handle ending the class"""
        await self.update_class_status('completed')
        
        # Notify all participants
        await self.broadcast_class_update('completed')
        
        # Generate final report
        await self.send_final_report()
    
    async def handle_announcement(self, data):
        """Handle instructor announcement"""
        message = data.get('message', '')
        if message:
            # Broadcast to all class participants
            live_class_group_name = f'live_class_{self.live_class_id}'
            await self.channel_layer.group_send(
                live_class_group_name,
                {
                    'type': 'class_announcement',
                    'data': {
                        'message': message,
                        'timestamp': self.get_current_timestamp()
                    }
                }
            )
    
    async def handle_attendance_update(self, data):
        """Handle manual attendance update"""
        student_id = data.get('student_id')
        status = data.get('status')
        
        if student_id and status:
            await self.update_student_attendance(student_id, status)
            await self.send_dashboard_data()
    
    @database_sync_to_async
    def update_class_status(self, status):
        """Update class status"""
        try:
            live_class = LiveClass.objects.get(id=self.live_class_id)
            live_class.status = status
            live_class.save()
        except LiveClass.DoesNotExist:
            pass
    
    async def broadcast_class_update(self, status):
        """Broadcast class status update to all participants"""
        live_class_group_name = f'live_class_{self.live_class_id}'
        await self.channel_layer.group_send(
            live_class_group_name,
            {
                'type': 'class_status_update',
                'data': {
                    'status': status,
                    'timestamp': self.get_current_timestamp()
                }
            }
        )
    
    @database_sync_to_async
    def update_student_attendance(self, student_id, status):
        """Update student attendance manually"""
        try:
            from .services import AttendanceService
            live_class = LiveClass.objects.get(id=self.live_class_id)
            student = User.objects.get(id=student_id)
            
            AttendanceService.mark_attendance(
                live_class=live_class,
                student=student,
                status=status
            )
        except (LiveClass.DoesNotExist, User.DoesNotExist):
            pass
    
    async def send_dashboard_data(self):
        """Send current dashboard data to instructor"""
        data = await self.get_dashboard_data()
        if data:
            await self.send(text_data=json.dumps({
                'type': 'dashboard_data',
                'data': data
            }))
    
    @database_sync_to_async
    def get_dashboard_data(self):
        """Get instructor dashboard data"""
        try:
            from .services import AttendanceService
            live_class = LiveClass.objects.get(id=self.live_class_id)
            
            # Get attendance data
            attendances = list(live_class.attendances.select_related('student').all())
            
            # Get engagement metrics
            metrics = AttendanceService.calculate_engagement_metrics(live_class)
            
            return {
                'class_info': {
                    'id': str(live_class.id),
                    'title': live_class.title,
                    'status': live_class.status,
                    'scheduled_at': live_class.scheduled_at.isoformat() if live_class.scheduled_at else None,
                    'duration_minutes': live_class.duration_minutes
                },
                'attendance': [
                    {
                        'student_id': str(att.student.id),
                        'student_name': f"{att.student.first_name} {att.student.last_name}".strip() or att.student.email,
                        'status': att.status,
                        'join_time': att.join_time.isoformat() if att.join_time else None,
                        'duration_minutes': att.duration_minutes,
                        'participation_score': att.participation_score,
                        'questions_asked': att.questions_asked
                    }
                    for att in attendances
                ],
                'metrics': metrics
            }
        except LiveClass.DoesNotExist:
            return None
    
    async def send_final_report(self):
        """Send final class report to instructor"""
        report = await self.get_final_report()
        if report:
            await self.send(text_data=json.dumps({
                'type': 'final_report',
                'data': report
            }))
    
    @database_sync_to_async
    def get_final_report(self):
        """Get final class analytics report"""
        try:
            from .services import AttendanceService
            live_class = LiveClass.objects.get(id=self.live_class_id)
            return AttendanceService.get_class_analytics_report(live_class)
        except LiveClass.DoesNotExist:
            return None
    
    def get_current_timestamp(self):
        """Get current timestamp in ISO format"""
        from django.utils import timezone
        return timezone.now().isoformat()