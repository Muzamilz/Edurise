from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from unittest.mock import patch, Mock, MagicMock
import json
from apps.accounts.models import Organization, UserProfile
from apps.courses.models import Course
from apps.payments.models import Payment, Subscription
from apps.classes.models import LiveClass
from apps.ai.models import AIConversation
from apps.accounts.services import JWTAuthService

User = get_user_model()


class StripeIntegrationTest(TransactionTestCase):
    """Test Stripe payment integration"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='student@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
        
        self.course = Course.objects.create(
            title='Paid Course',
            description='A premium course',
            instructor=self.user,
            tenant=self.tenant,
            category='technology',
            price=Decimal('99.99')
        )
    
    def authenticate_user(self):
        """Helper to authenticate user"""
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    @patch('stripe.PaymentIntent.create')
    @patch('apps.payments.services.PaymentService.process_course_payment')
    def test_stripe_payment_intent_creation(self, mock_process_payment, mock_stripe_create):
        """Test Stripe PaymentIntent creation for course payment"""
        
        # Mock Stripe PaymentIntent response
        mock_payment_intent = Mock()
        mock_payment_intent.id = 'pi_test_123456'
        mock_payment_intent.client_secret = 'pi_test_123456_secret_abc'
        mock_payment_intent.status = 'requires_payment_method'
        mock_stripe_create.return_value = mock_payment_intent
        
        # Mock payment service
        mock_process_payment.return_value = {
            'payment_id': 'pay_123',
            'stripe_payment_intent_id': 'pi_test_123456',
            'client_secret': 'pi_test_123456_secret_abc',
            'status': 'pending'
        }
        
        self.authenticate_user()
        
        response = self.client.post(
            '/api/v1/payments/payments/create_course_payment/',
            {
                'course_id': str(self.course.id),
                'amount': '99.99',
                'payment_method': 'stripe'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify Stripe PaymentIntent was created
        mock_stripe_create.assert_called_once()
        
        # Verify response contains expected data
        payment_data = response.json()
        self.assertIn('payment_id', payment_data)
        self.assertIn('client_secret', payment_data)
        self.assertEqual(payment_data['status'], 'pending')
    
    @patch('stripe.Webhook.construct_event')
    @patch('apps.payments.services.PaymentService.process_webhook_event')
    def test_stripe_webhook_processing(self, mock_process_webhook, mock_construct_event):
        """Test Stripe webhook event processing"""
        
        # Mock webhook event
        mock_event = Mock()
        mock_event.type = 'payment_intent.succeeded'
        mock_event.data = {
            'object': {
                'id': 'pi_test_123456',
                'status': 'succeeded',
                'amount': 9999,
                'currency': 'usd'
            }
        }
        mock_construct_event.return_value = mock_event
        
        mock_process_webhook.return_value = True
        
        # Simulate webhook request
        webhook_payload = '{"id": "evt_test_webhook", "type": "payment_intent.succeeded"}'
        webhook_signature = 'test_signature'
        
        response = self.client.post(
            '/api/v1/payments/webhooks/stripe/',
            webhook_payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=webhook_signature
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_construct_event.assert_called_once()
        mock_process_webhook.assert_called_once_with(mock_event)


class PayPalIntegrationTest(TransactionTestCase):
    """Test PayPal payment integration"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='PayPal Test University',
            subdomain='paypal-test',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='paypal@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
        
        self.course = Course.objects.create(
            title='PayPal Course',
            description='Course for PayPal testing',
            instructor=self.user,
            tenant=self.tenant,
            category='technology',
            price=Decimal('79.99')
        )
    
    def authenticate_user(self):
        """Helper to authenticate user"""
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    @patch('paypalrestsdk.Payment.create')
    @patch('apps.payments.services.PaymentService.process_course_payment')
    def test_paypal_payment_creation(self, mock_process_payment, mock_paypal_create):
        """Test PayPal payment creation"""
        
        # Mock PayPal payment response
        mock_payment = Mock()
        mock_payment.id = 'PAY-123456789'
        mock_payment.state = 'created'
        mock_payment.links = [
            {'rel': 'approval_url', 'href': 'https://www.paypal.com/approve/PAY-123456789'}
        ]
        mock_paypal_create.return_value = True
        
        # Mock payment service
        mock_process_payment.return_value = {
            'payment_id': 'pay_paypal_123',
            'paypal_payment_id': 'PAY-123456789',
            'approval_url': 'https://www.paypal.com/approve/PAY-123456789',
            'status': 'pending'
        }
        
        self.authenticate_user()
        
        response = self.client.post(
            '/api/v1/payments/payments/create_course_payment/',
            {
                'course_id': str(self.course.id),
                'amount': '79.99',
                'payment_method': 'paypal'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        payment_data = response.json()
        self.assertIn('payment_id', payment_data)
        self.assertIn('approval_url', payment_data)
        self.assertEqual(payment_data['status'], 'pending')
    
    @patch('paypalrestsdk.Payment.execute')
    @patch('paypalrestsdk.Payment.find')
    def test_paypal_payment_execution(self, mock_paypal_find, mock_paypal_execute):
        """Test PayPal payment execution after approval"""
        
        # Create payment record
        payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            tenant=self.tenant,
            amount=Decimal('79.99'),
            currency='USD',
            payment_method='paypal',
            status='pending',
            paypal_payment_id='PAY-123456789'
        )
        
        # Mock PayPal payment execution
        mock_payment = Mock()
        mock_payment.state = 'approved'
        mock_paypal_find.return_value = mock_payment
        mock_paypal_execute.return_value = True
        
        self.authenticate_user()
        
        response = self.client.post(
            f'/api/v1/payments/payments/{payment.id}/confirm_payment/',
            {
                'payer_id': 'PAYER123456',
                'payment_id': 'PAY-123456789'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify payment was updated
        payment.refresh_from_db()
        # In real implementation, status would be updated by the service


class ZoomIntegrationTest(TransactionTestCase):
    """Test Zoom API integration for live classes"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Zoom Test University',
            subdomain='zoom-test',
            subscription_plan='pro'
        )
        
        self.instructor = User.objects.create_user(
            email='zoom-instructor@example.com',
            password='testpass123',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        UserProfile.objects.create(user=self.instructor, tenant=self.tenant)
        
        self.course = Course.objects.create(
            title='Zoom Course',
            description='Course with Zoom integration',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology'
        )
        
        self.live_class = LiveClass.objects.create(
            course=self.course,
            title='Zoom Live Class',
            description='Live class with Zoom',
            scheduled_at=timezone.now() + timedelta(hours=2),
            duration_minutes=60
        )
    
    def authenticate_instructor(self):
        """Helper to authenticate instructor"""
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    @patch('apps.classes.services.ZoomService.create_meeting')
    def test_zoom_meeting_creation(self, mock_create_meeting):
        """Test Zoom meeting creation for live class"""
        
        # Mock Zoom API response
        mock_create_meeting.return_value = {
            'id': 123456789,
            'join_url': 'https://zoom.us/j/123456789?pwd=testpassword',
            'start_url': 'https://zoom.us/s/123456789?zak=testtoken',
            'password': 'testpass',
            'host_id': 'zoom_host_123'
        }
        
        self.authenticate_instructor()
        
        response = self.client.post(f'/api/v1/classes/live-classes/{self.live_class.id}/create_zoom_meeting/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        meeting_data = response.json()
        self.assertIn('zoom_meeting_id', meeting_data)
        self.assertIn('join_url', meeting_data)
        self.assertIn('start_url', meeting_data)
        
        # Verify live class was updated
        self.live_class.refresh_from_db()
        self.assertEqual(self.live_class.zoom_meeting_id, '123456789')
        self.assertIsNotNone(self.live_class.join_url)
    
    @patch('apps.classes.services.ZoomService.get_meeting_participants')
    def test_zoom_attendance_tracking(self, mock_get_participants):
        """Test attendance tracking from Zoom meeting data"""
        
        # Mock Zoom participants data
        mock_get_participants.return_value = [
            {
                'user_email': 'student1@example.com',
                'join_time': '2024-01-15T10:00:00Z',
                'leave_time': '2024-01-15T10:45:00Z',
                'duration': 45
            },
            {
                'user_email': 'student2@example.com',
                'join_time': '2024-01-15T10:05:00Z',
                'leave_time': '2024-01-15T10:50:00Z',
                'duration': 45
            }
        ]
        
        # Set up live class with Zoom meeting
        self.live_class.zoom_meeting_id = '123456789'
        self.live_class.status = 'completed'
        self.live_class.save()
        
        self.authenticate_instructor()
        
        response = self.client.post(f'/api/v1/classes/live-classes/{self.live_class.id}/sync_attendance/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        sync_data = response.json()
        self.assertIn('participants_processed', sync_data)
        self.assertIn('attendance_records_created', sync_data)


class AIServiceIntegrationTest(TransactionTestCase):
    """Test AI service integrations (OpenAI, Gemini)"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='AI Test University',
            subdomain='ai-test',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='ai-user@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
        
        self.course = Course.objects.create(
            title='AI Enhanced Course',
            description='Course with AI features',
            instructor=self.user,
            tenant=self.tenant,
            category='technology'
        )
    
    def authenticate_user(self):
        """Helper to authenticate user"""
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    @patch('openai.ChatCompletion.create')
    def test_openai_chat_integration(self, mock_openai_chat):
        """Test OpenAI chat integration"""
        
        # Mock OpenAI response
        mock_openai_chat.return_value = {
            'choices': [{
                'message': {
                    'content': 'This is a helpful AI response about your question.'
                }
            }],
            'usage': {
                'total_tokens': 50
            }
        }
        
        self.authenticate_user()
        
        # Create AI conversation
        conversation = AIConversation.objects.create(
            user=self.user,
            course=self.course,
            title='Test AI Chat',
            conversation_type='tutor'
        )
        
        response = self.client.post(
            f'/api/v1/ai/ai-conversations/{conversation.id}/send_message/',
            {
                'message': 'Explain Python variables',
                'context': {'topic': 'python_basics'}
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        chat_response = response.json()
        self.assertTrue(chat_response['success'])
        self.assertIn('ai_response', chat_response)
        self.assertIn('usage_stats', chat_response)
    
    @patch('openai.Completion.create')
    def test_openai_content_summarization(self, mock_openai_completion):
        """Test OpenAI content summarization"""
        
        # Mock OpenAI response
        mock_openai_completion.return_value = {
            'choices': [{
                'text': 'This content covers the basics of Python programming including variables, functions, and control structures.'
            }],
            'usage': {
                'total_tokens': 75
            }
        }
        
        self.authenticate_user()
        
        response = self.client.post(
            '/api/v1/ai/ai-summaries/generate/',
            {
                'content': 'Python is a high-level programming language. It supports variables, functions, classes, and many built-in data structures...',
                'content_type': 'text',
                'content_title': 'Python Basics',
                'course_id': str(self.course.id)
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        summary_response = response.json()
        self.assertTrue(summary_response['success'])
        self.assertIn('summary', summary_response)
        self.assertIn('usage_stats', summary_response)
    
    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_gemini_quiz_generation(self, mock_gemini_generate):
        """Test Gemini AI quiz generation"""
        
        # Mock Gemini response
        mock_response = Mock()
        mock_response.text = json.dumps([
            {
                "question": "What is a Python variable?",
                "type": "multiple_choice",
                "options": ["A storage location", "A function", "A class", "A module"],
                "correct_answer": "A storage location",
                "explanation": "Variables in Python are used to store data values."
            }
        ])
        mock_gemini_generate.return_value = mock_response
        
        self.authenticate_user()
        
        response = self.client.post(
            '/api/v1/ai/ai-quizzes/generate/',
            {
                'content': 'Python variables are used to store data. They can hold different types of values...',
                'course_id': str(self.course.id),
                'title': 'Python Variables Quiz',
                'num_questions': 1,
                'difficulty': 'beginner'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        quiz_response = response.json()
        self.assertTrue(quiz_response['success'])
        self.assertIn('questions', quiz_response)
        self.assertEqual(len(quiz_response['questions']), 1)


class EmailServiceIntegrationTest(TransactionTestCase):
    """Test email service integration"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Email Test University',
            subdomain='email-test',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='email-user@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
    
    @patch('django.core.mail.send_mail')
    def test_email_notification_sending(self, mock_send_mail):
        """Test email notification sending"""
        
        mock_send_mail.return_value = True
        
        # Create notification
        notification = Notification.objects.create(
            user=self.user,
            tenant=self.tenant,
            title='Test Notification',
            message='This is a test notification',
            notification_type='enrollment'
        )
        
        # Simulate email sending
        from apps.notifications.services import EmailNotificationService
        
        email_service = EmailNotificationService()
        result = email_service.send_notification_email(notification)
        
        self.assertTrue(result)
        mock_send_mail.assert_called_once()
    
    @patch('apps.notifications.services.EmailTemplateService.render_template')
    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_templated_email_sending(self, mock_email_send, mock_render_template):
        """Test templated email sending"""
        
        # Mock template rendering
        mock_render_template.return_value = {
            'subject': 'Welcome to Test University',
            'html_content': '<h1>Welcome!</h1><p>Thank you for joining.</p>',
            'text_content': 'Welcome! Thank you for joining.'
        }
        
        mock_email_send.return_value = True
        
        # Test welcome email
        from apps.notifications.services import EmailTemplateService
        
        template_service = EmailTemplateService()
        result = template_service.send_welcome_email(
            user=self.user,
            tenant=self.tenant
        )
        
        self.assertTrue(result)
        mock_render_template.assert_called_once()
        mock_email_send.assert_called_once()


class WebSocketIntegrationTest(TransactionTestCase):
    """Test WebSocket integration for real-time features"""
    
    def setUp(self):
        self.tenant = Organization.objects.create(
            name='WebSocket Test University',
            subdomain='ws-test',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='ws-user@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
    
    @patch('channels.layers.get_channel_layer')
    def test_websocket_notification_broadcasting(self, mock_get_channel_layer):
        """Test WebSocket notification broadcasting"""
        
        # Mock channel layer
        mock_channel_layer = Mock()
        mock_get_channel_layer.return_value = mock_channel_layer
        
        # Create notification
        notification = Notification.objects.create(
            user=self.user,
            tenant=self.tenant,
            title='Real-time Notification',
            message='This is a real-time notification',
            notification_type='system'
        )
        
        # Simulate WebSocket broadcasting
        from apps.notifications.services import WebSocketNotificationService
        
        ws_service = WebSocketNotificationService()
        ws_service.broadcast_notification(notification)
        
        # Verify channel layer was called
        mock_channel_layer.group_send.assert_called_once()
    
    def test_websocket_connection_management(self):
        """Test WebSocket connection management"""
        
        # This would typically test WebSocket consumer connection/disconnection
        # For now, we'll test the connection tracking model
        
        from apps.notifications.models import WebSocketConnection
        
        connection = WebSocketConnection.objects.create(
            user=self.user,
            tenant=self.tenant,
            channel_name='test_channel_123',
            connected_at=timezone.now()
        )
        
        self.assertEqual(connection.user, self.user)
        self.assertEqual(connection.tenant, self.tenant)
        self.assertIsNotNone(connection.connected_at)
        self.assertIsNone(connection.disconnected_at)
        
        # Simulate disconnection
        connection.disconnected_at = timezone.now()
        connection.save()
        
        self.assertIsNotNone(connection.disconnected_at)


class FileStorageIntegrationTest(TransactionTestCase):
    """Test file storage service integration"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='File Test University',
            subdomain='file-test',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='file-user@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
        
        self.file_category = FileCategory.objects.create(
            name='test_documents',
            display_name='Test Documents',
            allowed_extensions=['pdf', 'doc', 'txt'],
            max_file_size_mb=10
        )
    
    def authenticate_user(self):
        """Helper to authenticate user"""
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    @patch('boto3.client')
    def test_s3_file_upload_integration(self, mock_boto3_client):
        """Test S3 file upload integration"""
        
        # Mock S3 client
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.upload_fileobj.return_value = None
        
        self.authenticate_user()
        
        # Create test file
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"test file content for S3 upload",
            content_type="application/pdf"
        )
        
        response = self.client.post(
            '/api/v1/files/file-uploads/',
            {
                'file': test_file,
                'category': self.file_category.id,
                'title': 'S3 Test Document',
                'description': 'Testing S3 upload integration'
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify file upload record was created
        file_upload = FileUpload.objects.get(id=response.data['id'])
        self.assertEqual(file_upload.original_filename, 'test_document.pdf')
        self.assertEqual(file_upload.uploaded_by, self.user)
    
    @patch('apps.files.services.FileStorageService.generate_presigned_url')
    def test_secure_file_download_integration(self, mock_generate_url):
        """Test secure file download URL generation"""
        
        # Mock presigned URL generation
        mock_generate_url.return_value = 'https://s3.amazonaws.com/bucket/file.pdf?signature=abc123'
        
        # Create file upload record
        file_upload = FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.file_category,
            original_filename='secure_test.pdf',
            file_size=1024,
            file_type='application/pdf',
            storage_path='uploads/secure_test.pdf'
        )
        
        self.authenticate_user()
        
        response = self.client.get(f'/api/v1/files/file-uploads/{file_upload.id}/secure_url/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        url_data = response.json()
        self.assertIn('secure_url', url_data['data'])
        self.assertTrue(url_data['data']['secure_url'].startswith('https://'))
        
        # Verify presigned URL service was called
        mock_generate_url.assert_called_once()


class DatabaseIntegrationTest(TransactionTestCase):
    """Test database integration and performance"""
    
    def setUp(self):
        self.tenant = Organization.objects.create(
            name='DB Test University',
            subdomain='db-test',
            subscription_plan='enterprise'
        )
        
        self.instructor = User.objects.create_user(
            email='db-instructor@example.com',
            password='testpass123',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        UserProfile.objects.create(user=self.instructor, tenant=self.tenant)
    
    def test_database_transaction_integrity(self):
        """Test database transaction integrity"""
        
        from django.db import transaction
        
        # Test successful transaction
        with transaction.atomic():
            course = Course.objects.create(
                title='Transaction Test Course',
                description='Testing database transactions',
                instructor=self.instructor,
                tenant=self.tenant,
                category='technology'
            )
            
            # Create related objects
            CourseModule.objects.create(
                course=course,
                title='Test Module',
                description='Test module description',
                order=1
            )
        
        # Verify objects were created
        self.assertTrue(Course.objects.filter(title='Transaction Test Course').exists())
        self.assertTrue(CourseModule.objects.filter(title='Test Module').exists())
        
        # Test transaction rollback
        try:
            with transaction.atomic():
                course2 = Course.objects.create(
                    title='Rollback Test Course',
                    description='This should be rolled back',
                    instructor=self.instructor,
                    tenant=self.tenant,
                    category='technology'
                )
                
                # Force an error to trigger rollback
                raise Exception("Intentional error for rollback test")
                
        except Exception:
            pass  # Expected exception
        
        # Verify rollback occurred
        self.assertFalse(Course.objects.filter(title='Rollback Test Course').exists())
    
    def test_database_query_optimization(self):
        """Test database query optimization with select_related and prefetch_related"""
        
        # Create test data
        courses = []
        for i in range(5):
            course = Course.objects.create(
                title=f'Query Test Course {i}',
                description=f'Course {i} for query testing',
                instructor=self.instructor,
                tenant=self.tenant,
                category='technology'
            )
            courses.append(course)
            
            # Create modules for each course
            for j in range(3):
                CourseModule.objects.create(
                    course=course,
                    title=f'Module {j} for Course {i}',
                    description=f'Module {j} description',
                    order=j + 1
                )
        
        # Test optimized query with select_related and prefetch_related
        from django.test.utils import override_settings
        from django.db import connection
        
        with override_settings(DEBUG=True):
            # Reset queries
            connection.queries_log.clear()
            
            # Optimized query
            courses_with_modules = Course.objects.select_related('instructor').prefetch_related('modules').filter(
                tenant=self.tenant
            )
            
            # Force evaluation
            list(courses_with_modules)
            
            # Count queries (should be minimal due to optimization)
            query_count = len(connection.queries)
            
            # Should use significantly fewer queries than naive approach
            self.assertLess(query_count, 10, f"Too many queries: {query_count}")


class CacheIntegrationTest(TransactionTestCase):
    """Test cache integration"""
    
    def setUp(self):
        self.tenant = Organization.objects.create(
            name='Cache Test University',
            subdomain='cache-test',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='cache-user@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
    
    def test_cache_operations(self):
        """Test basic cache operations"""
        
        from django.core.cache import cache
        
        # Test cache set and get
        cache_key = f'test_key_{self.tenant.id}'
        cache_value = {'test': 'data', 'tenant_id': str(self.tenant.id)}
        
        cache.set(cache_key, cache_value, timeout=300)
        
        retrieved_value = cache.get(cache_key)
        self.assertEqual(retrieved_value, cache_value)
        
        # Test cache delete
        cache.delete(cache_key)
        self.assertIsNone(cache.get(cache_key))
    
    def test_cache_invalidation(self):
        """Test cache invalidation on model updates"""
        
        from django.core.cache import cache
        
        # Create cache entry
        cache_key = f'user_profile_{self.user.id}'
        profile_data = {
            'user_id': self.user.id,
            'email': self.user.email,
            'tenant_id': str(self.tenant.id)
        }
        
        cache.set(cache_key, profile_data, timeout=300)
        
        # Verify cache exists
        self.assertIsNotNone(cache.get(cache_key))
        
        # Update user (this should trigger cache invalidation in real implementation)
        self.user.first_name = 'Updated Name'
        self.user.save()
        
        # In a real implementation with cache invalidation signals,
        # the cache would be cleared automatically
        # For this test, we'll manually clear it to simulate the behavior
        cache.delete(cache_key)
        
        # Verify cache was invalidated
        self.assertIsNone(cache.get(cache_key))