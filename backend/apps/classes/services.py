import requests
import json
import jwt
import time
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.courses.models import LiveClass
from .models import ClassAttendance


class ZoomService:
    """Service for Zoom API integration"""
    
    def __init__(self):
        self.api_key = settings.ZOOM_API_KEY
        self.api_secret = settings.ZOOM_API_SECRET
        self.base_url = "https://api.zoom.us/v2"
    
    def get_access_token(self):
        """Get Zoom access token using JWT"""
        if not self.api_key or not self.api_secret:
            raise ValidationError("Zoom API credentials not configured")
        
        # JWT payload
        payload = {
            'iss': self.api_key,
            'exp': int(time.time() + 3600),  # Token expires in 1 hour
            'iat': int(time.time()),
            'aud': 'zoom',
            'appKey': self.api_key,
            'tokenExp': int(time.time() + 3600),
            'alg': 'HS256'
        }
        
        # Generate JWT token
        token = jwt.encode(payload, self.api_secret, algorithm='HS256')
        return token
    
    def create_meeting(self, live_class):
        """Create a Zoom meeting for a live class"""
        try:
            headers = {
                'Authorization': f'Bearer {self.get_access_token()}',
                'Content-Type': 'application/json'
            }
            
            # Format start time for Zoom API
            start_time = live_class.scheduled_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            meeting_data = {
                'topic': live_class.title,
                'type': 2,  # Scheduled meeting
                'start_time': start_time,
                'duration': live_class.duration_minutes,
                'timezone': 'UTC',
                'agenda': live_class.description or '',
                'settings': {
                    'host_video': True,
                    'participant_video': True,
                    'join_before_host': False,
                    'mute_upon_entry': True,
                    'waiting_room': True,
                    'auto_recording': 'none',  # No recording for live-only classes
                    'allow_multiple_devices': True,
                    'approval_type': 0,  # Automatically approve
                    'registration_type': 1,  # Attendees register once
                    'enforce_login': False,
                    'alternative_hosts': '',
                    'close_registration': False,
                    'show_share_button': True,
                    'meeting_authentication': False
                }
            }
            
            response = requests.post(
                f"{self.base_url}/users/me/meetings",
                headers=headers,
                json=meeting_data,
                timeout=30
            )
            
            if response.status_code == 201:
                meeting_info = response.json()
                
                # Update live class with Zoom details
                live_class.zoom_meeting_id = str(meeting_info['id'])
                live_class.join_url = meeting_info['join_url']
                live_class.start_url = meeting_info['start_url']
                live_class.password = meeting_info.get('password', '')
                live_class.save()
                
                return meeting_info
            else:
                error_msg = f"Failed to create Zoom meeting. Status: {response.status_code}, Response: {response.text}"
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error while creating Zoom meeting: {str(e)}")
        except Exception as e:
            raise Exception(f"Zoom API error: {str(e)}")
    
    def update_meeting(self, live_class):
        """Update a Zoom meeting"""
        if not live_class.zoom_meeting_id:
            return self.create_meeting(live_class)
        
        try:
            headers = {
                'Authorization': f'Bearer {self.get_access_token()}',
                'Content-Type': 'application/json'
            }
            
            # Format start time for Zoom API
            start_time = live_class.scheduled_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            meeting_data = {
                'topic': live_class.title,
                'start_time': start_time,
                'duration': live_class.duration_minutes,
                'agenda': live_class.description or '',
                'settings': {
                    'host_video': True,
                    'participant_video': True,
                    'join_before_host': False,
                    'mute_upon_entry': True,
                    'waiting_room': True,
                    'auto_recording': 'none'
                }
            }
            
            response = requests.patch(
                f"{self.base_url}/meetings/{live_class.zoom_meeting_id}",
                headers=headers,
                json=meeting_data,
                timeout=30
            )
            
            if response.status_code == 204:
                return True
            else:
                error_msg = f"Failed to update Zoom meeting. Status: {response.status_code}, Response: {response.text}"
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error while updating Zoom meeting: {str(e)}")
        except Exception as e:
            raise Exception(f"Zoom API error: {str(e)}")
    
    def delete_meeting(self, meeting_id):
        """Delete a Zoom meeting"""
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
        }
        
        try:
            response = requests.delete(
                f"{self.base_url}/meetings/{meeting_id}",
                headers=headers
            )
            
            return response.status_code == 204
            
        except Exception as e:
            raise Exception(f"Zoom API error: {str(e)}")
    
    def get_meeting_info(self, meeting_id):
        """Get meeting information"""
        try:
            headers = {
                'Authorization': f'Bearer {self.get_access_token()}',
            }
            
            response = requests.get(
                f"{self.base_url}/meetings/{meeting_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error while getting meeting info: {str(e)}")
        except Exception as e:
            raise Exception(f"Zoom API error: {str(e)}")
    
    def get_meeting_participants(self, meeting_id):
        """Get meeting participants for attendance tracking"""
        try:
            headers = {
                'Authorization': f'Bearer {self.get_access_token()}',
            }
            
            response = requests.get(
                f"{self.base_url}/report/meetings/{meeting_id}/participants",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error while getting participants: {str(e)}")
        except Exception as e:
            raise Exception(f"Zoom API error: {str(e)}")


class AttendanceService:
    """Service for managing class attendance"""
    
    @staticmethod
    def mark_attendance(live_class, student, status='present', join_time=None, leave_time=None):
        """Mark attendance for a student"""
        attendance, created = ClassAttendance.objects.get_or_create(
            live_class=live_class,
            student=student,
            defaults={
                'status': status,
                'join_time': join_time or timezone.now(),
                'leave_time': leave_time
            }
        )
        
        if not created:
            attendance.status = status
            if join_time:
                attendance.join_time = join_time
            if leave_time:
                attendance.leave_time = leave_time
            attendance.save()
        
        # Calculate duration if both times are available
        if attendance.join_time and attendance.leave_time:
            duration = attendance.leave_time - attendance.join_time
            attendance.duration_minutes = int(duration.total_seconds() / 60)
            attendance.save()
        
        return attendance
    
    @staticmethod
    def process_zoom_webhook(webhook_data):
        """Process Zoom webhook for attendance tracking"""
        event_type = webhook_data.get('event')
        
        try:
            if event_type == 'meeting.participant_joined':
                # Handle participant join
                meeting_id = str(webhook_data['payload']['object']['id'])
                participant = webhook_data['payload']['object']['participant']
                
                live_class = LiveClass.objects.get(zoom_meeting_id=meeting_id)
                
                # Find student by email
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                try:
                    student = User.objects.get(email=participant['email'])
                    AttendanceService.mark_attendance(
                        live_class=live_class,
                        student=student,
                        status='present',
                        join_time=timezone.now()
                    )
                except User.DoesNotExist:
                    # Log unknown participant
                    pass
            
            elif event_type == 'meeting.participant_left':
                # Handle participant leave
                meeting_id = str(webhook_data['payload']['object']['id'])
                participant = webhook_data['payload']['object']['participant']
                
                live_class = LiveClass.objects.get(zoom_meeting_id=meeting_id)
                
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                try:
                    student = User.objects.get(email=participant['email'])
                    attendance = ClassAttendance.objects.get(
                        live_class=live_class,
                        student=student
                    )
                    attendance.leave_time = timezone.now()
                    
                    # Calculate duration
                    if attendance.join_time:
                        duration = attendance.leave_time - attendance.join_time
                        attendance.duration_minutes = int(duration.total_seconds() / 60)
                    
                    attendance.save()
                except (User.DoesNotExist, ClassAttendance.DoesNotExist):
                    pass
            
            elif event_type == 'meeting.ended':
                # Process final attendance when meeting ends
                meeting_id = str(webhook_data['payload']['object']['id'])
                
                live_class = LiveClass.objects.get(zoom_meeting_id=meeting_id)
                live_class.status = 'completed'
                live_class.save()
                
                # Update attendance for participants who didn't leave properly
                attendances = live_class.attendances.filter(leave_time__isnull=True)
                for attendance in attendances:
                    if attendance.join_time:
                        # Estimate leave time as meeting end time
                        attendance.leave_time = timezone.now()
                        duration = attendance.leave_time - attendance.join_time
                        attendance.duration_minutes = int(duration.total_seconds() / 60)
                        attendance.save()
                        
        except LiveClass.DoesNotExist:
            # Meeting not found in our system
            pass
        except Exception as e:
            # Log error but don't fail webhook processing
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing Zoom webhook: {str(e)}")
    
    @staticmethod
    def calculate_engagement_metrics(live_class):
        """Calculate comprehensive engagement metrics for a live class"""
        attendances = live_class.attendances.all()
        
        if not attendances.exists():
            return {
                'total_students': 0,
                'attendance_rate': 0,
                'average_duration': 0,
                'engagement_score': 0,
                'status_breakdown': {
                    'present': 0,
                    'absent': 0,
                    'partial': 0,
                    'late': 0
                },
                'duration_stats': {
                    'min_duration': 0,
                    'max_duration': 0,
                    'median_duration': 0
                },
                'participation_stats': {
                    'average_participation': 0,
                    'total_questions': 0,
                    'active_participants': 0
                }
            }
        
        total_students = attendances.count()
        present_students = attendances.filter(status__in=['present', 'partial', 'late']).count()
        attendance_rate = (present_students / total_students) * 100 if total_students > 0 else 0
        
        # Status breakdown
        status_breakdown = {
            'present': attendances.filter(status='present').count(),
            'absent': attendances.filter(status='absent').count(),
            'partial': attendances.filter(status='partial').count(),
            'late': attendances.filter(status='late').count()
        }
        
        # Duration statistics
        durations = [att.duration_minutes for att in attendances if att.duration_minutes > 0]
        if durations:
            durations.sort()
            average_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            median_duration = durations[len(durations) // 2] if durations else 0
        else:
            average_duration = min_duration = max_duration = median_duration = 0
        
        # Participation statistics
        participation_scores = [att.participation_score for att in attendances if att.participation_score > 0]
        average_participation = sum(participation_scores) / len(participation_scores) if participation_scores else 0
        total_questions = sum(att.questions_asked for att in attendances)
        active_participants = attendances.filter(participation_score__gt=0).count()
        
        # Calculate comprehensive engagement score
        # Factors: attendance rate (40%), duration retention (30%), participation (30%)
        duration_retention = 0
        if live_class.duration_minutes > 0 and average_duration > 0:
            duration_retention = min(100, (average_duration / live_class.duration_minutes) * 100)
        
        engagement_score = (
            (attendance_rate * 0.4) + 
            (duration_retention * 0.3) + 
            (average_participation * 0.3)
        )
        
        return {
            'total_students': total_students,
            'attendance_rate': round(attendance_rate, 2),
            'average_duration': round(average_duration, 2),
            'engagement_score': round(engagement_score, 2),
            'status_breakdown': status_breakdown,
            'duration_stats': {
                'min_duration': round(min_duration, 2),
                'max_duration': round(max_duration, 2),
                'median_duration': round(median_duration, 2),
                'duration_retention_rate': round(duration_retention, 2)
            },
            'participation_stats': {
                'average_participation': round(average_participation, 2),
                'total_questions': total_questions,
                'active_participants': active_participants,
                'participation_rate': round((active_participants / total_students) * 100, 2) if total_students > 0 else 0
            }
        }
    
    @staticmethod
    def get_class_analytics_report(live_class):
        """Generate comprehensive analytics report for a live class"""
        metrics = AttendanceService.calculate_engagement_metrics(live_class)
        
        # Add time-based analysis
        attendances = live_class.attendances.all().order_by('join_time')
        
        # Peak attendance time analysis
        join_times = [att.join_time for att in attendances if att.join_time]
        if join_times:
            # Group by 5-minute intervals to find peak join time
            from collections import defaultdict
            time_buckets = defaultdict(int)
            
            for join_time in join_times:
                # Round to nearest 5-minute interval
                minutes = join_time.minute
                rounded_minutes = (minutes // 5) * 5
                bucket_time = join_time.replace(minute=rounded_minutes, second=0, microsecond=0)
                time_buckets[bucket_time] += 1
            
            peak_join_time = max(time_buckets.items(), key=lambda x: x[1]) if time_buckets else None
        else:
            peak_join_time = None
        
        # Attendance patterns
        on_time_students = attendances.filter(
            join_time__lte=live_class.scheduled_at + timedelta(minutes=5)
        ).count() if live_class.scheduled_at else 0
        
        late_students = attendances.filter(status='late').count()
        
        report = {
            **metrics,
            'class_info': {
                'title': live_class.title,
                'scheduled_at': live_class.scheduled_at,
                'duration_minutes': live_class.duration_minutes,
                'status': live_class.status,
                'zoom_meeting_id': live_class.zoom_meeting_id
            },
            'timing_analysis': {
                'on_time_students': on_time_students,
                'late_students': late_students,
                'peak_join_time': peak_join_time[0] if peak_join_time else None,
                'peak_join_count': peak_join_time[1] if peak_join_time else 0
            },
            'recommendations': AttendanceService._generate_recommendations(metrics)
        }
        
        return report
    
    @staticmethod
    def _generate_recommendations(metrics):
        """Generate recommendations based on engagement metrics"""
        recommendations = []
        
        if metrics['attendance_rate'] < 70:
            recommendations.append({
                'type': 'attendance',
                'message': 'Consider sending reminder notifications before class starts',
                'priority': 'high'
            })
        
        if metrics['duration_stats']['duration_retention_rate'] < 60:
            recommendations.append({
                'type': 'engagement',
                'message': 'Students are leaving early. Consider adding interactive elements or breaks',
                'priority': 'high'
            })
        
        if metrics['participation_stats']['participation_rate'] < 30:
            recommendations.append({
                'type': 'participation',
                'message': 'Low participation rate. Try adding polls, Q&A sessions, or breakout rooms',
                'priority': 'medium'
            })
        
        if metrics['engagement_score'] > 80:
            recommendations.append({
                'type': 'success',
                'message': 'Excellent engagement! Consider sharing your teaching methods with other instructors',
                'priority': 'low'
            })
        
        return recommendations