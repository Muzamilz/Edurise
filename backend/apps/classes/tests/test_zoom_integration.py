import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.courses.models import Course, LiveClass
from apps.classes.models import ClassAttendance
from apps.classes.services import ZoomService, AttendanceService
from apps.accounts.models import Organization

User = get_user_model()


class ZoomServiceTest(TestCase):
    """Test Zoom integration service"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test Organization',
            subdomain='test-org'
        )
        
        self.user = User.objects.create_user(
            email='instructor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Instructor',
            is_teacher=True
        )
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.user,
            category='technology',
            tenant=self.organization
        )
        
        self.live_class = LiveClass.objects.create(
            course=self.course,
            title='Test Live Class',
            description='Test live class description',
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=60
        )
    
    @patch('apps.classes.services.requests.post')
    @patch('apps.classes.services.ZoomService.get_access_token')
    def test_create_meeting_success(self, mock_get_token, mock_post):
        """Test successful Zoom meeting creation"""
        # Mock the access token
        mock_get_token.return_value = 'test_token'
        
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': '123456789',
            'join_url': 'https://zoom.us/j/123456789',
            'start_url': 'https://zoom.us/s/123456789',
            'password': 'testpass'
        }
        mock_post.return_value = mock_response
        
        # Create the service and test
        zoom_service = ZoomService()
        result = zoom_service.create_meeting(self.live_class)
        
        # Verify the result
        self.assertEqual(result['id'], '123456789')
        self.assertEqual(result['join_url'], 'https://zoom.us/j/123456789')
        
        # Verify the live class was updated
        self.live_class.refresh_from_db()
        self.assertEqual(self.live_class.zoom_meeting_id, '123456789')
        self.assertEqual(self.live_class.join_url, 'https://zoom.us/j/123456789')
    
    @patch('apps.classes.services.requests.post')
    @patch('apps.classes.services.ZoomService.get_access_token')
    def test_create_meeting_failure(self, mock_get_token, mock_post):
        """Test Zoom meeting creation failure"""
        # Mock the access token
        mock_get_token.return_value = 'test_token'
        
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value = mock_response
        
        # Create the service and test
        zoom_service = ZoomService()
        
        with self.assertRaises(Exception) as context:
            zoom_service.create_meeting(self.live_class)
        
        self.assertIn('Failed to create Zoom meeting', str(context.exception))


class AttendanceServiceTest(TestCase):
    """Test attendance tracking service"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test Organization',
            subdomain='test-org'
        )
        
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Instructor',
            is_teacher=True
        )
        
        self.student1 = User.objects.create_user(
            email='student1@test.com',
            password='testpass123',
            first_name='Student',
            last_name='One'
        )
        
        self.student2 = User.objects.create_user(
            email='student2@test.com',
            password='testpass123',
            first_name='Student',
            last_name='Two'
        )
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.instructor,
            category='technology',
            tenant=self.organization
        )
        
        self.live_class = LiveClass.objects.create(
            course=self.course,
            title='Test Live Class',
            description='Test live class description',
            scheduled_at=timezone.now() - timedelta(hours=1),
            duration_minutes=60,
            status='completed'
        )
    
    def test_mark_attendance(self):
        """Test marking attendance for a student"""
        join_time = timezone.now() - timedelta(minutes=30)
        leave_time = timezone.now()
        
        attendance = AttendanceService.mark_attendance(
            live_class=self.live_class,
            student=self.student1,
            status='present',
            join_time=join_time,
            leave_time=leave_time
        )
        
        self.assertEqual(attendance.status, 'present')
        self.assertEqual(attendance.duration_minutes, 30)
        self.assertEqual(attendance.live_class, self.live_class)
        self.assertEqual(attendance.student, self.student1)
    
    def test_calculate_engagement_metrics(self):
        """Test engagement metrics calculation"""
        # Create attendance records
        AttendanceService.mark_attendance(
            live_class=self.live_class,
            student=self.student1,
            status='present',
            join_time=timezone.now() - timedelta(minutes=60),
            leave_time=timezone.now()
        )
        
        AttendanceService.mark_attendance(
            live_class=self.live_class,
            student=self.student2,
            status='absent'
        )
        
        # Update participation scores
        attendance1 = ClassAttendance.objects.get(
            live_class=self.live_class,
            student=self.student1
        )
        attendance1.participation_score = 80
        attendance1.questions_asked = 3
        attendance1.save()
        
        # Calculate metrics
        metrics = AttendanceService.calculate_engagement_metrics(self.live_class)
        
        self.assertEqual(metrics['total_students'], 2)
        self.assertEqual(metrics['attendance_rate'], 50.0)  # 1 out of 2 present
        self.assertEqual(metrics['average_duration'], 60.0)
        self.assertEqual(metrics['participation_stats']['total_questions'], 3)
        self.assertEqual(metrics['participation_stats']['active_participants'], 1)
    
    def test_get_class_analytics_report(self):
        """Test comprehensive analytics report generation"""
        # Create attendance records
        AttendanceService.mark_attendance(
            live_class=self.live_class,
            student=self.student1,
            status='present',
            join_time=self.live_class.scheduled_at + timedelta(minutes=2),  # 2 minutes late
            leave_time=self.live_class.scheduled_at + timedelta(minutes=50)
        )
        
        AttendanceService.mark_attendance(
            live_class=self.live_class,
            student=self.student2,
            status='present',
            join_time=self.live_class.scheduled_at,  # On time
            leave_time=self.live_class.scheduled_at + timedelta(minutes=60)
        )
        
        # Generate report
        report = AttendanceService.get_class_analytics_report(self.live_class)
        
        self.assertIn('class_info', report)
        self.assertIn('timing_analysis', report)
        self.assertIn('recommendations', report)
        self.assertEqual(report['class_info']['title'], 'Test Live Class')
        self.assertEqual(report['timing_analysis']['on_time_students'], 1)
        self.assertEqual(report['total_students'], 2)
    
    def test_process_zoom_webhook_participant_joined(self):
        """Test processing Zoom webhook for participant join"""
        webhook_data = {
            'event': 'meeting.participant_joined',
            'payload': {
                'object': {
                    'id': '123456789',
                    'participant': {
                        'email': 'student1@test.com',
                        'user_name': 'Student One'
                    }
                }
            }
        }
        
        # Set up live class with Zoom meeting ID
        self.live_class.zoom_meeting_id = '123456789'
        self.live_class.save()
        
        # Process webhook
        AttendanceService.process_zoom_webhook(webhook_data)
        
        # Check if attendance was created
        attendance = ClassAttendance.objects.get(
            live_class=self.live_class,
            student=self.student1
        )
        self.assertEqual(attendance.status, 'present')
        self.assertIsNotNone(attendance.join_time)
    
    def test_process_zoom_webhook_meeting_ended(self):
        """Test processing Zoom webhook for meeting end"""
        # Create attendance without leave time
        attendance = AttendanceService.mark_attendance(
            live_class=self.live_class,
            student=self.student1,
            status='present',
            join_time=timezone.now() - timedelta(minutes=30)
        )
        
        webhook_data = {
            'event': 'meeting.ended',
            'payload': {
                'object': {
                    'id': '123456789'
                }
            }
        }
        
        # Set up live class with Zoom meeting ID
        self.live_class.zoom_meeting_id = '123456789'
        self.live_class.status = 'live'
        self.live_class.save()
        
        # Process webhook
        AttendanceService.process_zoom_webhook(webhook_data)
        
        # Check if live class status was updated
        self.live_class.refresh_from_db()
        self.assertEqual(self.live_class.status, 'completed')
        
        # Check if attendance was updated with leave time
        attendance.refresh_from_db()
        self.assertIsNotNone(attendance.leave_time)
        self.assertGreater(attendance.duration_minutes, 0)


class LiveClassIntegrationTest(TestCase):
    """Integration test for LiveClass with Zoom"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test Organization',
            subdomain='test-org'
        )
        
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Instructor',
            is_teacher=True
        )
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.instructor,
            category='technology',
            tenant=self.organization
        )
    
    def test_live_class_creation_flow(self):
        """Test the complete flow of creating a live class"""
        live_class = LiveClass.objects.create(
            course=self.course,
            title='Integration Test Class',
            description='Test description',
            scheduled_at=timezone.now() + timedelta(hours=2),
            duration_minutes=90
        )
        
        self.assertEqual(live_class.status, 'scheduled')
        self.assertEqual(live_class.course, self.course)
        self.assertEqual(live_class.duration_minutes, 90)
    
    def test_live_class_status_transitions(self):
        """Test live class status transitions"""
        live_class = LiveClass.objects.create(
            course=self.course,
            title='Status Test Class',
            description='Test description',
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=60
        )
        
        # Initial status should be scheduled
        self.assertEqual(live_class.status, 'scheduled')
        
        # Start the class
        live_class.status = 'live'
        live_class.save()
        self.assertEqual(live_class.status, 'live')
        
        # End the class
        live_class.status = 'completed'
        live_class.save()
        self.assertEqual(live_class.status, 'completed')