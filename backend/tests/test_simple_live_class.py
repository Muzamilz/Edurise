from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.courses.models import Course, LiveClass, Enrollment
from apps.classes.models import ClassAttendance
from apps.accounts.models import Organization, UserProfile

User = get_user_model()


class SimpleLiveClassTest(TestCase):
    """Simple integration test for live class functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = Organization.objects.create(
            name='Test Organization',
            subdomain='test-org',
            subscription_plan='pro'
        )
        
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            password='testpass123',
            first_name='John',
            last_name='Instructor',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        self.student = User.objects.create_user(
            email='student@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Student'
        )
        
        # Create user profiles
        UserProfile.objects.create(user=self.instructor, tenant=self.organization, role='teacher')
        UserProfile.objects.create(user=self.student, tenant=self.organization, role='student')
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Course for testing',
            instructor=self.instructor,
            category='technology',
            is_public=True,
            tenant=self.organization
        )
        
        self.live_class = LiveClass.objects.create(
            course=self.course,
            title='Test Live Class',
            description='Live class for testing',
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=60
        )
        
        # Create enrollment
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.organization
        )
    
    def test_zoom_meeting_data_storage(self):
        """Test that Zoom meeting data can be stored in LiveClass model"""
        # Simulate Zoom meeting creation
        self.live_class.zoom_meeting_id = '123456789'
        self.live_class.join_url = 'https://zoom.us/j/123456789?pwd=testpassword'
        self.live_class.start_url = 'https://zoom.us/s/123456789?zak=testtoken'
        self.live_class.password = 'testpass'
        self.live_class.save()
        
        # Verify data was stored correctly
        self.live_class.refresh_from_db()
        self.assertEqual(self.live_class.zoom_meeting_id, '123456789')
        self.assertEqual(self.live_class.join_url, 'https://zoom.us/j/123456789?pwd=testpassword')
        self.assertEqual(self.live_class.start_url, 'https://zoom.us/s/123456789?zak=testtoken')
        self.assertEqual(self.live_class.password, 'testpass')
    
    def test_attendance_tracking_accuracy(self):
        """Test attendance tracking functionality"""
        # Create attendance record
        join_time = timezone.now()
        leave_time = join_time + timedelta(minutes=45)
        
        attendance = ClassAttendance.objects.create(
            live_class=self.live_class,
            student=self.student,
            status='present',
            join_time=join_time,
            leave_time=leave_time,
            duration_minutes=45,
            participation_score=80
        )
        
        # Verify attendance record
        self.assertEqual(attendance.status, 'present')
        self.assertEqual(attendance.duration_minutes, 45)
        self.assertEqual(attendance.participation_score, 80)
        
        # Test attendance percentage calculation
        expected_percentage = (45 / self.live_class.duration_minutes) * 100
        self.assertEqual(attendance.attendance_percentage, expected_percentage)
    
    def test_recording_storage_and_retrieval(self):
        """Test recording URL storage"""
        recording_url = 'https://storage.example.com/recordings/test-recording.mp4'
        recording_password = 'rec_password'
        
        self.live_class.recording_url = recording_url
        self.live_class.recording_password = recording_password
        self.live_class.save()
        
        # Verify recording data was stored
        self.live_class.refresh_from_db()
        self.assertEqual(self.live_class.recording_url, recording_url)
        self.assertEqual(self.live_class.recording_password, recording_password)
    
    def test_live_class_status_updates(self):
        """Test real-time status updates simulation"""
        # Initial status should be scheduled
        self.assertEqual(self.live_class.status, 'scheduled')
        
        # Transition to live
        self.live_class.status = 'live'
        self.live_class.save()
        self.live_class.refresh_from_db()
        self.assertEqual(self.live_class.status, 'live')
        
        # Transition to completed
        self.live_class.status = 'completed'
        self.live_class.save()
        self.live_class.refresh_from_db()
        self.assertEqual(self.live_class.status, 'completed')
    
    def test_complete_workflow_integration(self):
        """Test complete live class workflow"""
        # Step 1: Set up Zoom meeting
        self.live_class.zoom_meeting_id = '987654321'
        self.live_class.join_url = 'https://zoom.us/j/987654321'
        self.live_class.save()
        
        # Step 2: Start class
        self.live_class.status = 'live'
        self.live_class.save()
        
        # Step 3: Student attends
        attendance = ClassAttendance.objects.create(
            live_class=self.live_class,
            student=self.student,
            status='present',
            join_time=timezone.now(),
            duration_minutes=55,
            participation_score=85
        )
        
        # Step 4: End class
        self.live_class.status = 'completed'
        self.live_class.recording_url = 'https://storage.example.com/recording.mp4'
        self.live_class.save()
        
        # Step 5: Verify final state
        self.assertEqual(self.live_class.status, 'completed')
        self.assertIsNotNone(self.live_class.recording_url)
        self.assertEqual(attendance.status, 'present')
        self.assertEqual(attendance.duration_minutes, 55)
        
        # Step 6: Calculate metrics
        total_enrolled = Enrollment.objects.filter(course=self.course).count()
        total_attended = ClassAttendance.objects.filter(live_class=self.live_class).count()
        attendance_rate = (total_attended / total_enrolled) * 100
        
        self.assertEqual(total_enrolled, 1)
        self.assertEqual(total_attended, 1)
        self.assertEqual(attendance_rate, 100.0)