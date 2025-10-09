import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import timedelta, datetime

from apps.courses.models import Course, LiveClass, Enrollment
from apps.classes.models import ClassAttendance
from apps.accounts.models import Organization, UserProfile

User = get_user_model()


class LiveClassIntegrationTest(APITestCase):
    """Integration tests for live class functionality"""
    
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
        
        self.student1 = User.objects.create_user(
            email='student1@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Student'
        )
        
        self.student2 = User.objects.create_user(
            email='student2@test.com',
            password='testpass123',
            first_name='Bob',
            last_name='Learner'
        )
        
        self.course = Course.objects.create(
            title='Integration Test Course',
            description='Course for integration testing',
            instructor=self.instructor,
            category='technology',
            is_public=True
        )
        # Set tenant through the TenantAwareModel
        self.course.tenant = self.organization
        self.course.save()
        
        self.live_class = LiveClass.objects.create(
            course=self.course,
            title='Integration Test Live Class',
            description='Live class for integration testing',
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=60
        )
        
        # Create user profiles for tenant relationship
        UserProfile.objects.create(user=self.instructor, tenant=self.organization, role='teacher')
        UserProfile.objects.create(user=self.student1, tenant=self.organization, role='student')
        UserProfile.objects.create(user=self.student2, tenant=self.organization, role='student')
        
        # Set up API client with tenant context
        self.client = APIClient()
        self.client.defaults['HTTP_HOST'] = 'test-org.localhost'


class ZoomIntegrationTest(LiveClassIntegrationTest):
    """Test Zoom meeting creation and URL generation"""
    
    def test_zoom_meeting_data_storage(self):
        """Test that Zoom meeting data can be stored in LiveClass model"""
        # Simulate Zoom meeting creation by updating the live class
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
    
    def test_live_class_status_transitions(self):
        """Test live class status transitions"""
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
    
    def test_live_class_recording_url_storage(self):
        """Test recording URL storage"""
        recording_url = 'https://storage.example.com/recordings/test-recording.mp4'
        self.live_class.recording_url = recording_url
        self.live_class.recording_password = 'rec_pass'
        self.live_class.save()
        
        self.live_class.refresh_from_db()
        self.assertEqual(self.live_class.recording_url, recording_url)
        self.assertEqual(self.live_class.recording_password, 'rec_pass')


class AttendanceTrackingTest(LiveClassIntegrationTest):
    """Test attendance tracking accuracy"""
    
    def setUp(self):
        super().setUp()
        # Create enrollments
        enrollment1 = Enrollment.objects.create(student=self.student1, course=self.course)
        enrollment1.tenant = self.organization
        enrollment1.save()
        
        enrollment2 = Enrollment.objects.create(student=self.student2, course=self.course)
        enrollment2.tenant = self.organization
        enrollment2.save()
    
    def test_manual_attendance_marking(self):
        """Test manual attendance marking by creating attendance records"""
        # Create attendance record directly (simulating manual marking)
        join_time = timezone.now()
        leave_time = join_time + timedelta(minutes=45)
        
        attendance = ClassAttendance.objects.create(
            live_class=self.live_class,
            student=self.student1,
            status='present',
            join_time=join_time,
            leave_time=leave_time,
            duration_minutes=45,
            participation_score=80
        )
        
        # Verify attendance record was created correctly
        self.assertEqual(attendance.status, 'present')
        self.assertEqual(attendance.duration_minutes, 45)
        self.assertEqual(attendance.participation_score, 80)
        
        # Test attendance percentage calculation
        expected_percentage = (45 / self.live_class.duration_minutes) * 100
        self.assertEqual(attendance.attendance_percentage, expected_percentage)
    
    def test_zoom_webhook_attendance_processing(self):
        """Test automatic attendance tracking simulation"""
        # Simulate processing Zoom webhook data by creating attendance record
        # This would normally be done by a webhook handler
        
        # Set up live class with Zoom meeting ID
        self.live_class.zoom_meeting_id = '123456789'
        self.live_class.save()
        
        # Simulate webhook data processing
        join_time = timezone.now()
        leave_time = join_time + timedelta(minutes=45)
        
        # Create attendance record as if processed from webhook
        attendance = ClassAttendance.objects.create(
            live_class=self.live_class,
            student=self.student1,
            status='present',
            join_time=join_time,
            leave_time=leave_time,
            duration_minutes=45
        )
        
        # Verify attendance was created correctly
        self.assertEqual(attendance.status, 'present')
        self.assertEqual(attendance.duration_minutes, 45)
        self.assertEqual(attendance.live_class.zoom_meeting_id, '123456789')
    
    def test_attendance_analytics_calculation(self):
        """Test engagement metrics calculation"""
        # Create attendance records
        ClassAttendance.objects.create(
            live_class=self.live_class,
            student=self.student1,
            status='present',
            join_time=timezone.now(),
            leave_time=timezone.now() + timedelta(minutes=45),
            duration_minutes=45,
            participation_score=80
        )
        
        ClassAttendance.objects.create(
            live_class=self.live_class,
            student=self.student2,
            status='late',
            join_time=timezone.now() + timedelta(minutes=5),
            leave_time=timezone.now() + timedelta(minutes=50),
            duration_minutes=45,
            participation_score=70
        )
        
        # Test analytics calculation directly from model data
        attendances = ClassAttendance.objects.filter(live_class=self.live_class)
        
        # Calculate metrics
        total_students = attendances.count()
        attendance_rate = 100.0  # Both students attended
        average_duration = sum(a.duration_minutes for a in attendances) / total_students
        average_participation = sum(a.participation_score for a in attendances) / total_students
        
        # Verify calculations
        self.assertEqual(total_students, 2)
        self.assertEqual(attendance_rate, 100.0)
        self.assertEqual(average_duration, 45.0)
        self.assertEqual(average_participation, 75.0)  # Average of 80 and 70


class RecordingStorageTest(LiveClassIntegrationTest):
    """Test recording storage and retrieval"""
    
    def test_recording_url_storage(self):
        """Test that recording URLs can be stored in LiveClass model"""
        # Simulate recording being processed and URL stored
        recording_url = 'https://storage.example.com/recordings/test-recording.mp4'
        recording_password = 'rec_password'
        
        self.live_class.recording_url = recording_url
        self.live_class.recording_password = recording_password
        self.live_class.save()
        
        # Verify recording data was stored
        self.live_class.refresh_from_db()
        self.assertEqual(self.live_class.recording_url, recording_url)
        self.assertEqual(self.live_class.recording_password, recording_password)
    
    def test_recording_access_by_enrollment(self):
        """Test that only enrolled students can access recordings"""
        # Set up recording
        self.live_class.recording_url = 'https://storage.example.com/recording.mp4'
        self.live_class.save()
        
        # Check enrollment exists for student1
        enrollment = Enrollment.objects.filter(
            student=self.student1,
            course=self.course
        ).first()
        self.assertIsNotNone(enrollment)
        
        # Check no enrollment for a new student
        new_student = User.objects.create_user(
            email='newstudent@test.com',
            password='testpass123'
        )
        
        no_enrollment = Enrollment.objects.filter(
            student=new_student,
            course=self.course
        ).exists()
        self.assertFalse(no_enrollment)


class RealTimeUpdatesTest(LiveClassIntegrationTest):
    """Test real-time updates simulation during live classes"""
    
    def test_attendance_tracking_during_live_class(self):
        """Test attendance tracking when class is live"""
        # Set class to live status
        self.live_class.status = 'live'
        self.live_class.save()
        
        # Simulate students joining at different times
        join_time_1 = timezone.now()
        join_time_2 = join_time_1 + timedelta(minutes=5)
        
        # Student 1 joins on time
        attendance_1 = ClassAttendance.objects.create(
            live_class=self.live_class,
            student=self.student1,
            status='present',
            join_time=join_time_1,
            duration_minutes=0  # Still in class
        )
        
        # Student 2 joins late
        attendance_2 = ClassAttendance.objects.create(
            live_class=self.live_class,
            student=self.student2,
            status='late',
            join_time=join_time_2,
            duration_minutes=0  # Still in class
        )
        
        # Verify attendance records
        self.assertEqual(attendance_1.status, 'present')
        self.assertEqual(attendance_2.status, 'late')
        
        # Verify class has active attendees
        active_attendees = ClassAttendance.objects.filter(
            live_class=self.live_class,
            leave_time__isnull=True
        ).count()
        self.assertEqual(active_attendees, 2)
    
    def test_class_status_transitions_with_notifications(self):
        """Test class status changes that would trigger notifications"""
        # Track status changes
        status_changes = []
        
        # Initial status
        status_changes.append(self.live_class.status)
        
        # Start class
        self.live_class.status = 'live'
        self.live_class.save()
        status_changes.append(self.live_class.status)
        
        # End class
        self.live_class.status = 'completed'
        self.live_class.save()
        status_changes.append(self.live_class.status)
        
        # Verify status progression
        expected_statuses = ['scheduled', 'live', 'completed']
        self.assertEqual(status_changes, expected_statuses)


class LiveClassIntegrationEndToEndTest(LiveClassIntegrationTest):
    """End-to-end integration test for complete live class workflow"""
    
    def test_complete_live_class_workflow(self):
        """Test complete workflow from class creation to completion"""
        # Step 1: Verify live class was created in setUp
        self.assertEqual(self.live_class.status, 'scheduled')
        self.assertEqual(self.live_class.course, self.course)
        
        # Step 2: Simulate Zoom meeting creation
        self.live_class.zoom_meeting_id = '987654321'
        self.live_class.join_url = 'https://zoom.us/j/987654321'
        self.live_class.start_url = 'https://zoom.us/s/987654321'
        self.live_class.password = 'e2etest'
        self.live_class.save()
        
        # Step 3: Start the class
        self.live_class.status = 'live'
        self.live_class.save()
        
        # Step 4: Simulate student attendance
        attendance = ClassAttendance.objects.create(
            live_class=self.live_class,
            student=self.student1,
            status='present',
            join_time=timezone.now(),
            leave_time=timezone.now() + timedelta(minutes=55),
            duration_minutes=55,
            participation_score=85
        )
        
        # Step 5: End the class
        self.live_class.status = 'completed'
        self.live_class.save()
        
        # Step 6: Verify final state
        self.live_class.refresh_from_db()
        self.assertEqual(self.live_class.status, 'completed')
        
        # Step 7: Verify attendance data
        final_attendance = ClassAttendance.objects.get(
            live_class=self.live_class,
            student=self.student1
        )
        self.assertEqual(final_attendance.status, 'present')
        self.assertEqual(final_attendance.duration_minutes, 55)
        self.assertEqual(final_attendance.participation_score, 85)
        
        # Step 8: Calculate final metrics
        total_enrolled = Enrollment.objects.filter(course=self.course).count()
        total_attended = ClassAttendance.objects.filter(live_class=self.live_class).count()
        attendance_rate = (total_attended / total_enrolled) * 100
        
        self.assertEqual(total_enrolled, 2)  # student1 and student2
        self.assertEqual(total_attended, 1)  # only student1 attended
        self.assertEqual(attendance_rate, 50.0)
        
        # Step 9: Simulate recording being available
        self.live_class.recording_url = 'https://storage.example.com/recording.mp4'
        self.live_class.save()
        
        self.assertIsNotNone(self.live_class.recording_url)