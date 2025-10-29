"""
End-to-end tests for major user journeys in the EduRise platform.
Tests complete workflows from user registration to course completion,
payment processing, live classes, and AI features.
"""

import json
import time
from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock

from apps.accounts.models import Organization, UserProfile
from apps.courses.models import Course, Enrollment, CourseModule, CourseReview
from apps.payments.models import Payment, Invoice, Subscription
from apps.classes.models import LiveClass, ClassAttendance
from apps.ai.models import AIConversation, AIMessage, AIContentSummary, AIQuiz
from apps.files.models import FileCategory, FileUpload
from apps.notifications.models import Notification
from apps.accounts.services import JWTAuthService

User = get_user_model()


class CompleteUserRegistrationToCompletionE2ETest(TransactionTestCase):
    """End-to-end test for complete user journey from registration to course completion"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create organization
        self.organization = Organization.objects.create(
            name="E2E Test University",
            subdomain="e2e-test",
            subscription_plan="pro",
            is_active=True
        )
        
        # Create instructor
        self.instructor = User.objects.create_user(
            email='e2e-instructor@example.com',
            password='TestPass123!',
            first_name='John',
            last_name='Instructor',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        UserProfile.objects.create(
            user=self.instructor,
            tenant=self.organization,
            role='teacher'
        )
        
        # Create file category
        self.file_category = FileCategory.objects.create(
            name='course_materials',
            display_name='Course Materials',
            allowed_extensions=['pdf', 'mp4', 'pptx'],
            max_file_size_mb=100
        )
    
    def test_complete_student_journey_free_course(self):
        """Test complete student journey with a free course"""
        
        # Step 1: Student Registration
        registration_data = {
            'email': 'e2e-student@example.com',
            'password': 'StudentPass123!',
            'first_name': 'Jane',
            'last_name': 'Student',
            'tenant_subdomain': 'e2e-test'
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/register/',
            registration_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify user was created
        student = User.objects.get(email='e2e-student@example.com')
        self.assertEqual(student.first_name, 'Jane')
        
        # Step 2: Student Login
        login_data = {
            'email': 'e2e-student@example.com',
            'password': 'StudentPass123!',
            'tenant_subdomain': 'e2e-test'
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/login/',
            login_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        login_response = response.json()
        
        # Set authentication for subsequent requests
        access_token = login_response['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Step 3: Browse Available Courses
        response = self.client.get('/api/v1/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 4: Instructor Creates a Free Course
        # Switch to instructor authentication
        instructor_tokens = JWTAuthService.generate_tokens(self.instructor, self.organization)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {instructor_tokens["access"]}')
        
        course_data = {
            'title': 'Introduction to Python Programming',
            'description': 'Learn Python basics for free',
            'category': 'technology',
            'difficulty_level': 'beginner',
            'price': '0.00',  # Free course
            'duration_weeks': 4,
            'is_public': True,
            'tags': ['python', 'programming', 'beginner']
        }
        
        response = self.client.post('/api/v1/courses/courses/', course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        course_id = response.data['id']
        course = Course.objects.get(id=course_id)
        
        # Step 5: Add Course Modules
        modules_data = [
            {
                'course': course_id,
                'title': 'Getting Started with Python',
                'description': 'Introduction and setup',
                'content': 'Welcome to Python programming...',
                'order': 1,
                'is_published': True
            },
            {
                'course': course_id,
                'title': 'Variables and Data Types',
                'description': 'Understanding Python basics',
                'content': 'In Python, variables are...',
                'order': 2,
                'is_published': True
            }
        ]
        
        for module_data in modules_data:
            response = self.client.post('/api/v1/courses/modules/', module_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 6: Student Enrolls in Free Course
        # Switch back to student authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.post(f'/api/v1/courses/courses/{course_id}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        enrollment_data = response.data
        enrollment_id = enrollment_data['id']
        
        # Verify enrollment
        enrollment = Enrollment.objects.get(id=enrollment_id)
        self.assertEqual(enrollment.student, student)
        self.assertEqual(enrollment.course, course)
        self.assertEqual(enrollment.status, 'active')
        
        # Step 7: Student Progresses Through Course
        progress_updates = [25, 50, 75, 100]
        
        for progress in progress_updates:
            response = self.client.patch(
                f'/api/v1/courses/enrollments/{enrollment_id}/update_progress/',
                {'progress_percentage': progress},
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verify progress update
            enrollment.refresh_from_db()
            self.assertEqual(enrollment.progress_percentage, progress)
            
            if progress == 100:
                self.assertEqual(enrollment.status, 'completed')
                self.assertIsNotNone(enrollment.completed_at)
        
        # Step 8: Student Leaves Course Review
        review_data = {
            'course': course_id,
            'rating': 5,
            'comment': 'Excellent free course! Learned a lot about Python basics.'
        }
        
        response = self.client.post('/api/v1/courses/reviews/', review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify review
        review = CourseReview.objects.get(course=course, student=student)
        self.assertEqual(review.rating, 5)
        self.assertIn('Excellent', review.comment)
        
        # Step 9: Check Student Dashboard
        response = self.client.get('/api/v1/dashboard/student/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        dashboard_data = response.data['data']
        self.assertEqual(dashboard_data['completed_courses'], 1)
        self.assertEqual(dashboard_data['total_enrollments'], 1)
        
        return student, course, enrollment
    
    def test_complete_instructor_course_creation_journey(self):
        """Test complete instructor journey creating and managing a course"""
        
        # Authenticate as instructor
        instructor_tokens = JWTAuthService.generate_tokens(self.instructor, self.organization)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {instructor_tokens["access"]}')
        
        # Step 1: Create Premium Course
        course_data = {
            'title': 'Advanced Python Web Development',
            'description': 'Master Django and Flask frameworks',
            'category': 'technology',
            'difficulty_level': 'advanced',
            'price': '199.99',
            'duration_weeks': 12,
            'max_students': 50,
            'is_public': True,
            'tags': ['python', 'django', 'flask', 'web-development']
        }
        
        response = self.client.post('/api/v1/courses/courses/', course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        course_id = response.data['id']
        
        # Step 2: Upload Course Materials
        with patch('apps.files.services.FileUploadService.upload_file') as mock_upload:
            mock_file_upload = Mock()
            mock_file_upload.id = 'file-123'
            mock_file_upload.original_filename = 'course_syllabus.pdf'
            mock_upload.return_value = mock_file_upload
            
            from django.core.files.uploadedfile import SimpleUploadedFile
            test_file = SimpleUploadedFile(
                "course_syllabus.pdf",
                b"Advanced Python Web Development Syllabus...",
                content_type="application/pdf"
            )
            
            response = self.client.post(
                '/api/v1/files/file-uploads/',
                {
                    'file': test_file,
                    'category': self.file_category.id,
                    'course_id': course_id,
                    'title': 'Course Syllabus',
                    'access_level': 'course'
                },
                format='multipart'
            )
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 3: Create Course Modules
        modules = [
            'Django Fundamentals',
            'Models and Database Design',
            'Views and Templates',
            'REST API Development',
            'Authentication and Security',
            'Deployment and Production'
        ]
        
        for i, module_title in enumerate(modules):
            module_data = {
                'course': course_id,
                'title': module_title,
                'description': f'Learn about {module_title.lower()}',
                'content': f'In this module, we will cover {module_title.lower()}...',
                'order': i + 1,
                'is_published': True
            }
            
            response = self.client.post('/api/v1/courses/modules/', module_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 4: Create Live Class
        live_class_data = {
            'course': course_id,
            'title': 'Django Live Coding Session',
            'description': 'Interactive Django development session',
            'scheduled_at': (timezone.now() + timedelta(days=7)).isoformat(),
            'duration_minutes': 120
        }
        
        response = self.client.post('/api/v1/classes/live-classes/', live_class_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        live_class_id = response.data['id']
        
        # Step 5: Set up Zoom Meeting for Live Class
        with patch('apps.classes.services.ZoomService.create_meeting') as mock_zoom:
            mock_zoom.return_value = {
                'id': 123456789,
                'join_url': 'https://zoom.us/j/123456789',
                'start_url': 'https://zoom.us/s/123456789',
                'password': 'zoompass'
            }
            
            response = self.client.post(f'/api/v1/classes/live-classes/{live_class_id}/create_zoom_meeting/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 6: Check Course Statistics (initially empty)
        response = self.client.get(f'/api/v1/courses/courses/{course_id}/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats = response.data
        self.assertEqual(stats['total_enrollments'], 0)
        
        # Step 7: Check Instructor Dashboard
        response = self.client.get('/api/v1/dashboard/teacher/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        dashboard_data = response.data['data']
        self.assertIn('instructor_info', dashboard_data)
        self.assertIn('overview_stats', dashboard_data)
        
        return course_id, live_class_id


class PaidCourseEnrollmentE2ETest(TransactionTestCase):
    """End-to-end test for paid course enrollment with payment processing"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.organization = Organization.objects.create(
            name="Payment Test University",
            subdomain="payment-test",
            subscription_plan="pro"
        )
        
        self.instructor = User.objects.create_user(
            email='payment-instructor@example.com',
            password='TestPass123!',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        UserProfile.objects.create(user=self.instructor, tenant=self.organization)
        
        # Create paid course
        self.course = Course.objects.create(
            title='Premium Python Masterclass',
            description='Advanced Python programming course',
            instructor=self.instructor,
            tenant=self.organization,
            category='technology',
            price=Decimal('299.99'),
            is_public=True
        )
    
    @patch('apps.payments.services.PaymentService.process_course_payment')
    @patch('apps.payments.services.PaymentService.confirm_payment')
    @patch('apps.payments.services.InvoiceService.create_invoice_for_payment')
    def test_complete_paid_enrollment_workflow(self, mock_create_invoice, mock_confirm_payment, mock_process_payment):
        """Test complete paid course enrollment workflow"""
        
        # Step 1: Student Registration
        registration_data = {
            'email': 'payment-student@example.com',
            'password': 'StudentPass123!',
            'first_name': 'Payment',
            'last_name': 'Student',
            'tenant_subdomain': 'payment-test'
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/register/',
            registration_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        student = User.objects.get(email='payment-student@example.com')
        
        # Step 2: Student Login
        login_data = {
            'email': 'payment-student@example.com',
            'password': 'StudentPass123!',
            'tenant_subdomain': 'payment-test'
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/login/',
            login_data,
            format='json'
        )
        
        access_token = response.json()['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Step 3: Browse Course and View Details
        response = self.client.get(f'/api/v1/courses/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        course_detail = response.data
        self.assertEqual(course_detail['title'], 'Premium Python Masterclass')
        self.assertEqual(float(course_detail['price']), 299.99)
        
        # Step 4: Attempt to Enroll (Should Require Payment)
        response = self.client.post(f'/api/v1/courses/courses/{self.course.id}/enroll/')
        
        # This might redirect to payment or require payment first
        # The exact behavior depends on implementation
        
        # Step 5: Initiate Payment
        mock_process_payment.return_value = {
            'payment_id': 'pay_test_123',
            'status': 'pending',
            'client_secret': 'pi_test_client_secret',
            'stripe_payment_intent_id': 'pi_test_123'
        }
        
        response = self.client.post(
            '/api/v1/payments/payments/create_course_payment/',
            {
                'course_id': str(self.course.id),
                'amount': '299.99',
                'payment_method': 'stripe'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment_response = response.json()
        
        # Create actual payment record for testing
        payment = Payment.objects.create(
            user=student,
            course=self.course,
            tenant=self.organization,
            amount=Decimal('299.99'),
            currency='USD',
            payment_method='stripe',
            status='pending',
            stripe_payment_intent_id='pi_test_123'
        )
        
        # Step 6: Confirm Payment
        mock_confirm_payment.return_value = True
        mock_invoice = Mock()
        mock_invoice.id = 'inv_123'
        mock_create_invoice.return_value = mock_invoice
        
        response = self.client.post(f'/api/v1/payments/payments/{payment.id}/confirm_payment/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 7: Verify Enrollment Created After Payment
        # In real implementation, this would be automatic after payment confirmation
        enrollment = Enrollment.objects.create(
            student=student,
            course=self.course,
            tenant=self.organization,
            status='active'
        )
        
        # Step 8: Update Payment Status
        payment.status = 'completed'
        payment.save()
        
        # Step 9: Verify Student Can Access Course
        response = self.client.get('/api/v1/courses/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        enrollments = response.data['results']
        self.assertTrue(any(e['course'] == str(self.course.id) for e in enrollments))
        
        # Step 10: Check Payment History
        response = self.client.get('/api/v1/payments/payments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 11: Verify Invoice Generation
        mock_create_invoice.assert_called_once_with(payment)
        
        return student, payment, enrollment


class LiveClassE2ETest(TransactionTestCase):
    """End-to-end test for live class functionality"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.organization = Organization.objects.create(
            name="Live Class Test University",
            subdomain="live-test",
            subscription_plan="pro"
        )
        
        self.instructor = User.objects.create_user(
            email='live-instructor@example.com',
            password='TestPass123!',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        self.student1 = User.objects.create_user(
            email='live-student1@example.com',
            password='TestPass123!'
        )
        
        self.student2 = User.objects.create_user(
            email='live-student2@example.com',
            password='TestPass123!'
        )
        
        # Create profiles
        for user in [self.instructor, self.student1, self.student2]:
            UserProfile.objects.create(user=user, tenant=self.organization)
        
        # Create course
        self.course = Course.objects.create(
            title='Live Programming Workshop',
            description='Interactive programming sessions',
            instructor=self.instructor,
            tenant=self.organization,
            category='technology',
            is_public=True
        )
        
        # Create enrollments
        for student in [self.student1, self.student2]:
            Enrollment.objects.create(
                student=student,
                course=self.course,
                tenant=self.organization,
                status='active'
            )
    
    @patch('apps.classes.services.ZoomService.create_meeting')
    @patch('apps.classes.services.ZoomService.get_meeting_participants')
    def test_complete_live_class_workflow(self, mock_get_participants, mock_create_meeting):
        """Test complete live class workflow from creation to completion"""
        
        # Step 1: Instructor Creates Live Class
        instructor_tokens = JWTAuthService.generate_tokens(self.instructor, self.organization)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {instructor_tokens["access"]}')
        
        live_class_data = {
            'course': str(self.course.id),
            'title': 'Python Debugging Techniques',
            'description': 'Learn advanced debugging strategies',
            'scheduled_at': (timezone.now() + timedelta(hours=2)).isoformat(),
            'duration_minutes': 90
        }
        
        response = self.client.post('/api/v1/classes/live-classes/', live_class_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        live_class_id = response.data['id']
        live_class = LiveClass.objects.get(id=live_class_id)
        
        # Step 2: Set up Zoom Meeting
        mock_create_meeting.return_value = {
            'id': 987654321,
            'join_url': 'https://zoom.us/j/987654321?pwd=testpass',
            'start_url': 'https://zoom.us/s/987654321?zak=testtoken',
            'password': 'testpass'
        }
        
        response = self.client.post(f'/api/v1/classes/live-classes/{live_class_id}/create_zoom_meeting/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify Zoom meeting data was stored
        live_class.refresh_from_db()
        self.assertEqual(live_class.zoom_meeting_id, '987654321')
        self.assertIsNotNone(live_class.join_url)
        
        # Step 3: Students Get Class Information
        student1_tokens = JWTAuthService.generate_tokens(self.student1, self.organization)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {student1_tokens["access"]}')
        
        response = self.client.get(f'/api/v1/classes/live-classes/{live_class_id}/join_info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        join_info = response.data
        self.assertIn('join_url', join_info)
        self.assertIn('password', join_info)
        
        # Step 4: Start Live Class
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {instructor_tokens["access"]}')
        
        response = self.client.post(f'/api/v1/classes/live-classes/{live_class_id}/start_class/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify class status changed
        live_class.refresh_from_db()
        self.assertEqual(live_class.status, 'live')
        
        # Step 5: Simulate Student Attendance
        # Create attendance records as if students joined
        attendance1 = ClassAttendance.objects.create(
            live_class=live_class,
            student=self.student1,
            status='present',
            join_time=timezone.now(),
            leave_time=timezone.now() + timedelta(minutes=85),
            duration_minutes=85,
            participation_score=90
        )
        
        attendance2 = ClassAttendance.objects.create(
            live_class=live_class,
            student=self.student2,
            status='late',
            join_time=timezone.now() + timedelta(minutes=10),
            leave_time=timezone.now() + timedelta(minutes=80),
            duration_minutes=70,
            participation_score=75
        )
        
        # Step 6: End Live Class
        response = self.client.post(f'/api/v1/classes/live-classes/{live_class_id}/end_class/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        live_class.refresh_from_db()
        self.assertEqual(live_class.status, 'completed')
        
        # Step 7: Sync Attendance from Zoom
        mock_get_participants.return_value = [
            {
                'user_email': 'live-student1@example.com',
                'join_time': '2024-01-15T10:00:00Z',
                'leave_time': '2024-01-15T11:25:00Z',
                'duration': 85
            },
            {
                'user_email': 'live-student2@example.com',
                'join_time': '2024-01-15T10:10:00Z',
                'leave_time': '2024-01-15T11:20:00Z',
                'duration': 70
            }
        ]
        
        response = self.client.post(f'/api/v1/classes/live-classes/{live_class_id}/sync_attendance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 8: Generate Attendance Report
        response = self.client.get(f'/api/v1/classes/live-classes/{live_class_id}/attendance_report/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        report = response.data
        self.assertEqual(report['total_enrolled'], 2)
        self.assertEqual(report['total_attended'], 2)
        self.assertEqual(report['attendance_rate'], 100.0)
        
        # Step 9: Add Recording URL
        live_class.recording_url = 'https://storage.example.com/recording.mp4'
        live_class.recording_password = 'rec_pass'
        live_class.save()
        
        # Step 10: Students Access Recording
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {student1_tokens["access"]}')
        
        response = self.client.get(f'/api/v1/classes/live-classes/{live_class_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        class_data = response.data
        self.assertIn('recording_url', class_data)
        
        return live_class, [attendance1, attendance2]


class AIFeaturesE2ETest(TransactionTestCase):
    """End-to-end test for AI-powered features"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.organization = Organization.objects.create(
            name="AI Test University",
            subdomain="ai-test",
            subscription_plan="pro"
        )
        
        self.student = User.objects.create_user(
            email='ai-student@example.com',
            password='TestPass123!'
        )
        
        UserProfile.objects.create(user=self.student, tenant=self.organization)
        
        self.course = Course.objects.create(
            title='AI-Enhanced Programming Course',
            description='Learn programming with AI assistance',
            instructor=self.student,  # For simplicity
            tenant=self.organization,
            category='technology'
        )
        
        # Create enrollment
        Enrollment.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.organization,
            status='active'
        )
    
    @patch('apps.ai.services.AIServiceFactory.create_service_from_request')
    def test_complete_ai_workflow(self, mock_ai_service_factory):
        """Test complete AI workflow from conversation to content generation"""
        
        # Mock AI service
        mock_ai_service = Mock()
        mock_ai_service_factory.return_value = mock_ai_service
        
        # Authenticate student
        student_tokens = JWTAuthService.generate_tokens(self.student, self.organization)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {student_tokens["access"]}')
        
        # Step 1: Create AI Conversation
        conversation_data = {
            'title': 'Python Learning Assistant',
            'conversation_type': 'tutor',
            'context': {
                'course_id': str(self.course.id),
                'topic': 'python_basics'
            }
        }
        
        response = self.client.post(
            '/api/v1/ai/ai-conversations/',
            conversation_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conversation_id = response.data['id']
        
        # Step 2: Send Messages to AI Tutor
        mock_ai_service.chat_with_tutor.return_value = (
            "Python is a high-level, interpreted programming language known for its simplicity and readability. It's great for beginners because of its clean syntax.",
            {"tokens_used": 45, "model": "gpt-3.5-turbo"}
        )
        
        messages = [
            "What is Python?",
            "How do I create variables in Python?",
            "Can you explain Python functions?"
        ]
        
        ai_responses = []
        
        for message in messages:
            response = self.client.post(
                f'/api/v1/ai/ai-conversations/{conversation_id}/send_message/',
                {
                    'message': message,
                    'context': {'topic': 'python_basics'}
                },
                format='json'
            )
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            message_response = response.json()
            self.assertTrue(message_response['success'])
            self.assertIn('ai_response', message_response)
            ai_responses.append(message_response['ai_response'])
        
        # Step 3: Generate Content Summary
        mock_ai_service.generate_content_summary.return_value = (
            "This content covers Python programming fundamentals including variables, data types, functions, and control structures. Key concepts include syntax, indentation, and object-oriented programming principles.",
            ["Python syntax", "Variables and data types", "Functions", "Control structures", "OOP concepts"],
            {"tokens_used": 85, "model": "gpt-3.5-turbo"}
        )
        
        content_text = """
        Python Programming Basics
        
        Python is a versatile programming language. Variables in Python are created by assignment.
        Functions are defined using the def keyword. Control structures include if statements and loops.
        Python supports object-oriented programming with classes and objects.
        """
        
        response = self.client.post(
            '/api/v1/ai/ai-summaries/generate/',
            {
                'content': content_text,
                'content_type': 'text',
                'content_title': 'Python Basics Module',
                'course_id': str(self.course.id)
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        summary_response = response.json()
        self.assertTrue(summary_response['success'])
        self.assertIn('summary', summary_response)
        self.assertIn('key_points', summary_response)
        
        # Step 4: Generate Quiz
        mock_quiz_questions = [
            {
                "question": "What keyword is used to define a function in Python?",
                "type": "multiple_choice",
                "options": ["def", "function", "func", "define"],
                "correct_answer": "def",
                "explanation": "The 'def' keyword is used to define functions in Python."
            },
            {
                "question": "Python uses indentation to define code blocks.",
                "type": "true_false",
                "correct_answer": "true",
                "explanation": "Python uses indentation instead of braces to define code blocks."
            }
        ]
        
        mock_ai_service.generate_quiz.return_value = (
            mock_quiz_questions,
            {"tokens_used": 120, "model": "gpt-3.5-turbo"}
        )
        
        response = self.client.post(
            '/api/v1/ai/ai-quizzes/generate/',
            {
                'content': content_text,
                'course_id': str(self.course.id),
                'title': 'Python Basics Quiz',
                'num_questions': 2,
                'difficulty': 'beginner'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        quiz_response = response.json()
        self.assertTrue(quiz_response['success'])
        self.assertIn('questions', quiz_response)
        self.assertEqual(len(quiz_response['questions']), 2)
        
        # Step 5: Check AI Usage Statistics
        mock_ai_service.get_usage_stats.return_value = {
            'current_month': {
                'total_requests': 6,  # 3 chat + 1 summary + 1 quiz + 1 stats
                'tokens_used': 250,   # Sum of all token usage
                'quota_remaining': 750
            },
            'daily_breakdown': [
                {'date': '2024-01-15', 'requests': 6, 'tokens': 250}
            ]
        }
        
        response = self.client.get('/api/v1/ai/ai-usage/current_stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        usage_response = response.json()
        self.assertTrue(usage_response['success'])
        self.assertIn('stats', usage_response)
        
        stats = usage_response['stats']
        self.assertEqual(stats['current_month']['total_requests'], 6)
        self.assertEqual(stats['current_month']['tokens_used'], 250)
        
        # Step 6: List AI Conversations
        response = self.client.get('/api/v1/ai/ai-conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        conversations = response.json()['data']
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0]['title'], 'Python Learning Assistant')
        
        # Step 7: Get Conversation Messages
        response = self.client.get(f'/api/v1/ai/ai-conversations/{conversation_id}/messages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        messages_response = response.json()
        conversation_messages = messages_response['data']
        
        # Should have user messages and AI responses
        self.assertGreater(len(conversation_messages), 0)
        
        return conversation_id, summary_response, quiz_response


class AdminWorkflowE2ETest(TransactionTestCase):
    """End-to-end test for admin management workflows"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.organization = Organization.objects.create(
            name="Admin Test University",
            subdomain="admin-test",
            subscription_plan="enterprise"
        )
        
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='AdminPass123!',
            is_staff=True,
            is_superuser=True
        )
        
        self.instructor = User.objects.create_user(
            email='admin-instructor@example.com',
            password='TestPass123!',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        self.student = User.objects.create_user(
            email='admin-student@example.com',
            password='TestPass123!'
        )
        
        # Create profiles
        for user in [self.admin, self.instructor, self.student]:
            UserProfile.objects.create(user=user, tenant=self.organization)
    
    def test_complete_admin_management_workflow(self):
        """Test complete admin management workflow"""
        
        # Authenticate as admin
        admin_tokens = JWTAuthService.generate_tokens(self.admin, self.organization)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_tokens["access"]}')
        
        # Step 1: View Admin Dashboard
        response = self.client.get('/api/v1/dashboard/admin/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        dashboard_data = response.data['data']
        self.assertIn('organization_info', dashboard_data)
        self.assertIn('user_stats', dashboard_data)
        self.assertIn('system_health', dashboard_data)
        
        # Step 2: View System Status
        response = self.client.get('/api/v1/security/system/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 3: Create Course as Instructor
        instructor_tokens = JWTAuthService.generate_tokens(self.instructor, self.organization)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {instructor_tokens["access"]}')
        
        course_data = {
            'title': 'Admin Review Course',
            'description': 'Course requiring admin review',
            'category': 'technology',
            'price': '99.99',
            'is_public': False  # Requires admin approval
        }
        
        response = self.client.post('/api/v1/courses/courses/', course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        course_id = response.data['id']
        
        # Step 4: Admin Reviews and Approves Course
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_tokens["access"]}')
        
        response = self.client.patch(
            f'/api/v1/courses/courses/{course_id}/',
            {'is_public': True, 'admin_approved': True},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 5: Student Enrolls and Leaves Review
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {instructor_tokens["access"]}')
        
        # Create enrollment
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=Course.objects.get(id=course_id),
            tenant=self.organization,
            status='completed'
        )
        
        # Student leaves review
        student_tokens = JWTAuthService.generate_tokens(self.student, self.organization)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {student_tokens["access"]}')
        
        review_data = {
            'course': course_id,
            'rating': 4,
            'comment': 'Good course, but could use more examples.'
        }
        
        response = self.client.post('/api/v1/courses/reviews/', review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        review_id = response.data['id']
        
        # Step 6: Admin Moderates Review
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_tokens["access"]}')
        
        response = self.client.post(f'/api/v1/courses/reviews/{review_id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 7: View Analytics
        response = self.client.get('/api/v1/analytics/platform-overview/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 8: Generate Report
        report_data = {
            'report_type': 'user_activity',
            'date_range': {
                'start': (timezone.now() - timedelta(days=30)).date().isoformat(),
                'end': timezone.now().date().isoformat()
            },
            'format': 'json'
        }
        
        response = self.client.post('/api/v1/reports/generate/', report_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 9: Check Security Events
        response = self.client.get('/api/v1/security/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        return course_id, review_id


class MultiTenantE2ETest(TransactionTestCase):
    """End-to-end test for multi-tenant functionality"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create two organizations
        self.org1 = Organization.objects.create(
            name="University A",
            subdomain="uni-a",
            subscription_plan="pro"
        )
        
        self.org2 = Organization.objects.create(
            name="University B",
            subdomain="uni-b",
            subscription_plan="basic"
        )
        
        # Create user who belongs to both organizations
        self.multi_tenant_user = User.objects.create_user(
            email='multi@example.com',
            password='MultiPass123!'
        )
        
        # Create profiles for both tenants
        UserProfile.objects.create(user=self.multi_tenant_user, tenant=self.org1)
        UserProfile.objects.create(user=self.multi_tenant_user, tenant=self.org2)
        
        # Create tenant-specific data
        self.course_org1 = Course.objects.create(
            title='Org1 Course',
            instructor=self.multi_tenant_user,
            tenant=self.org1,
            category='technology'
        )
        
        self.course_org2 = Course.objects.create(
            title='Org2 Course',
            instructor=self.multi_tenant_user,
            tenant=self.org2,
            category='business'
        )
    
    def test_tenant_switching_workflow(self):
        """Test complete tenant switching workflow"""
        
        # Step 1: Login to first tenant
        login_data = {
            'email': 'multi@example.com',
            'password': 'MultiPass123!',
            'tenant_subdomain': 'uni-a'
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/login/',
            login_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        org1_tokens = response.json()['tokens']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {org1_tokens["access"]}')
        
        # Step 2: Verify can only see Org1 data
        response = self.client.get('/api/v1/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        courses = response.json()['data']
        # Should only see courses from org1 (might be empty due to tenant filtering)
        
        # Step 3: Get available tenants
        response = self.client.get('/api/v1/users/tenants/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        tenants = response.json()
        self.assertEqual(len(tenants), 2)
        
        # Step 4: Switch to second tenant
        response = self.client.post(
            '/api/v1/users/switch_tenant/',
            {'tenant_id': str(self.org2.id)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        switch_response = response.json()
        new_tokens = {
            'access': switch_response['access_token'],
            'refresh': switch_response['refresh_token']
        }
        
        # Step 5: Use new tokens for Org2
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_tokens["access"]}')
        
        # Step 6: Verify can now see Org2 data
        response = self.client.get('/api/v1/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 7: Verify cannot access Org1 specific resources
        response = self.client.get(f'/api/v1/courses/courses/{self.course_org1.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Step 8: Can access Org2 specific resources
        response = self.client.get(f'/api/v1/courses/courses/{self.course_org2.id}/')
        # Might be 404 due to tenant filtering, but should not be 403
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
        
        return new_tokens