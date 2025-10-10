import json
from unittest.mock import patch, MagicMock
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from .models import (
    AIConversation, AIMessage, AIContentSummary, 
    AIQuiz, AIUsageQuota, AIRateLimit
)
from .services import AIService, AIServiceFactory, QuotaExceededError, RateLimitExceededError
from .providers import GeminiProvider
from apps.courses.models import Course
from apps.accounts.models import Organization

User = get_user_model()


class AIModelsTestCase(TestCase):
    """Test AI models functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.tenant = Organization.objects.create(
            name='Test Organization',
            subdomain='test-org'
        )
    
    def test_ai_conversation_creation(self):
        """Test AI conversation model creation"""
        conversation = AIConversation.objects.create(
            user=self.user,
            tenant=self.tenant,
            title='Test Conversation',
            conversation_type='tutor'
        )
        
        self.assertEqual(conversation.user, self.user)
        self.assertEqual(conversation.title, 'Test Conversation')
        self.assertEqual(conversation.conversation_type, 'tutor')
        self.assertTrue(conversation.is_active)
    
    def test_ai_message_creation(self):
        """Test AI message model creation"""
        conversation = AIConversation.objects.create(
            user=self.user,
            tenant=self.tenant,
            title='Test Conversation'
        )
        
        message = AIMessage.objects.create(
            conversation=conversation,
            role='user',
            content='Hello AI!',
            tokens_used=10
        )
        
        self.assertEqual(message.conversation, conversation)
        self.assertEqual(message.role, 'user')
        self.assertEqual(message.content, 'Hello AI!')
        self.assertEqual(message.tokens_used, 10)
    
    def test_ai_usage_quota_methods(self):
        """Test AI usage quota model methods"""
        quota = AIUsageQuota.objects.create(
            user=self.user,
            tenant=self.tenant,
            month=timezone.now().date().replace(day=1),
            chat_messages_used=50,
            chat_messages_limit=100,
            summaries_generated=5,
            summaries_limit=10,
            quizzes_generated=2,
            quizzes_limit=5
        )
        
        # Test quota checking methods
        self.assertFalse(quota.is_chat_quota_exceeded())
        self.assertFalse(quota.is_summary_quota_exceeded())
        self.assertFalse(quota.is_quiz_quota_exceeded())
        
        # Test when limits are exceeded
        quota.chat_messages_used = 100
        quota.summaries_generated = 10
        quota.quizzes_generated = 5
        quota.save()
        
        self.assertTrue(quota.is_chat_quota_exceeded())
        self.assertTrue(quota.is_summary_quota_exceeded())
        self.assertTrue(quota.is_quiz_quota_exceeded())
    
    def test_ai_rate_limit_functionality(self):
        """Test AI rate limit model functionality"""
        rate_limit = AIRateLimit.objects.create(
            user=self.user,
            requests_per_minute=10,
            requests_per_hour=100,
            requests_per_day=500
        )
        
        # Should be able to make requests initially
        self.assertTrue(rate_limit.can_make_request())
        
        # Record requests up to the limit
        for _ in range(10):
            rate_limit.record_request()
        
        # Should not be able to make more requests
        self.assertFalse(rate_limit.can_make_request())


class GeminiProviderTestCase(TestCase):
    """Test Gemini AI provider functionality"""
    
    @patch('apps.ai.providers.genai.configure')
    @patch('apps.ai.providers.genai.GenerativeModel')
    def setUp(self, mock_model, mock_configure):
        self.mock_model_instance = MagicMock()
        mock_model.return_value = self.mock_model_instance
        self.provider = GeminiProvider()
    
    def test_token_estimation(self):
        """Test token estimation functionality"""
        text = "This is a test message for token estimation."
        tokens = self.provider._estimate_tokens(text)
        
        # Should estimate roughly 1 token per 4 characters
        expected_tokens = len(text) // 4
        self.assertEqual(tokens, expected_tokens)
    
    def test_cost_calculation(self):
        """Test cost calculation functionality"""
        input_tokens = 1000
        output_tokens = 500
        
        cost = self.provider.calculate_cost(input_tokens, output_tokens)
        
        expected_cost = Decimal(str(input_tokens * self.provider.INPUT_TOKEN_COST + 
                                   output_tokens * self.provider.OUTPUT_TOKEN_COST))
        self.assertEqual(cost, expected_cost)
    
    def test_quiz_question_validation(self):
        """Test quiz question validation"""
        valid_question = {
            'question': 'What is Python?',
            'options': ['A language', 'A snake', 'A tool', 'A framework'],
            'correct_answer': 0,
            'explanation': 'Python is a programming language.'
        }
        
        invalid_question = {
            'question': 'What is Python?',
            'options': ['A language', 'A snake'],  # Only 2 options
            'correct_answer': 0
            # Missing explanation
        }
        
        self.assertTrue(self.provider._validate_quiz_question(valid_question))
        self.assertFalse(self.provider._validate_quiz_question(invalid_question))


class AIServiceTestCase(TestCase):
    """Test AI service functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.tenant = Organization.objects.create(
            name='Test Organization',
            subdomain='test-org'
        )
        self.ai_service = AIService(self.user, tenant=self.tenant)
    
    @patch('apps.ai.services.GeminiProvider')
    def test_get_usage_stats(self, mock_provider):
        """Test getting usage statistics"""
        # Create a usage quota
        quota = AIUsageQuota.objects.create(
            user=self.user,
            tenant=self.tenant,
            month=timezone.now().date().replace(day=1),
            chat_messages_used=25,
            chat_messages_limit=100,
            summaries_generated=5,
            summaries_limit=20,
            quizzes_generated=2,
            quizzes_limit=10,
            total_cost_usd=Decimal('2.50'),
            cost_limit_usd=Decimal('10.00')
        )
        
        stats = self.ai_service.get_usage_stats()
        
        self.assertEqual(stats['chat']['messages_used'], 25)
        self.assertEqual(stats['chat']['messages_limit'], 100)
        self.assertEqual(stats['chat']['percentage_used'], 25.0)
        
        self.assertEqual(stats['summaries']['summaries_used'], 5)
        self.assertEqual(stats['summaries']['summaries_limit'], 20)
        self.assertEqual(stats['summaries']['percentage_used'], 25.0)
        
        self.assertEqual(stats['quizzes']['quizzes_used'], 2)
        self.assertEqual(stats['quizzes']['quizzes_limit'], 10)
        self.assertEqual(stats['quizzes']['percentage_used'], 20.0)
        
        self.assertEqual(stats['cost']['total_cost_usd'], 2.50)
        self.assertEqual(stats['cost']['cost_limit_usd'], 10.00)
        self.assertEqual(stats['cost']['percentage_used'], 25.0)
    
    @patch('apps.ai.services.GeminiProvider')
    def test_quota_exceeded_error(self, mock_provider):
        """Test quota exceeded error handling"""
        # Create a quota that's already exceeded
        AIUsageQuota.objects.create(
            user=self.user,
            tenant=self.tenant,
            month=timezone.now().date().replace(day=1),
            chat_messages_used=100,
            chat_messages_limit=100
        )
        
        with self.assertRaises(QuotaExceededError):
            self.ai_service.chat_with_tutor('test-conv', 'Hello')
    
    @patch('apps.ai.services.GeminiProvider')
    def test_rate_limit_exceeded_error(self, mock_provider):
        """Test rate limit exceeded error handling"""
        # Create a rate limit that's exceeded
        rate_limit = AIRateLimit.objects.create(
            user=self.user,
            requests_per_minute=1,
            minute_requests=1
        )
        
        with patch.object(rate_limit, 'can_make_request', return_value=False):
            with self.assertRaises(RateLimitExceededError):
                self.ai_service.chat_with_tutor('test-conv', 'Hello')


class AIServiceFactoryTestCase(TestCase):
    """Test AI service factory functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.tenant = Organization.objects.create(
            name='Test Organization',
            subdomain='test-org'
        )
    
    def test_create_service(self):
        """Test creating AI service instance"""
        service = AIServiceFactory.create_service(self.user, tenant=self.tenant)
        
        self.assertIsInstance(service, AIService)
        self.assertEqual(service.user, self.user)
        self.assertEqual(service.tenant, self.tenant)
    
    def test_create_service_from_request(self):
        """Test creating AI service from request"""
        # Mock request object
        request = MagicMock()
        request.user = self.user
        request.tenant = self.tenant
        
        service = AIServiceFactory.create_service_from_request(request)
        
        self.assertIsInstance(service, AIService)
        self.assertEqual(service.user, self.user)


class AIAPITestCase(APITestCase):
    """Test AI API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.tenant = Organization.objects.create(
            name='Test Organization',
            subdomain='test-org'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_conversation(self):
        """Test creating AI conversation via API"""
        data = {
            'title': 'Test Conversation',
            'conversation_type': 'tutor'
        }
        
        response = self.client.post('/api/v1/ai/conversations/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AIConversation.objects.count(), 1)
        
        conversation = AIConversation.objects.first()
        self.assertEqual(conversation.title, 'Test Conversation')
        self.assertEqual(conversation.user, self.user)
    
    def test_list_conversations(self):
        """Test listing AI conversations"""
        # Create test conversations
        AIConversation.objects.create(
            user=self.user,
            tenant=self.tenant,
            title='Conversation 1'
        )
        AIConversation.objects.create(
            user=self.user,
            tenant=self.tenant,
            title='Conversation 2'
        )
        
        response = self.client.get('/api/v1/ai/conversations/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    @patch('apps.ai.views.AIServiceFactory.create_service_from_request')
    def test_send_message_success(self, mock_service_factory):
        """Test sending message to AI conversation"""
        # Create conversation
        conversation = AIConversation.objects.create(
            user=self.user,
            tenant=self.tenant,
            title='Test Conversation'
        )
        
        # Mock AI service
        mock_service = MagicMock()
        mock_service.chat_with_tutor.return_value = (
            'Hello! How can I help you?',
            {'tokens_used': 20, 'response_time_ms': 500}
        )
        mock_service_factory.return_value = mock_service
        
        data = {
            'message': 'Hello AI!',
            'context': {'course_id': 'test-course'}
        }
        
        response = self.client.post(
            f'/api/v1/ai/conversations/{conversation.id}/send_message/',
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['ai_response'], 'Hello! How can I help you?')
    
    @patch('apps.ai.views.AIServiceFactory.create_service_from_request')
    def test_send_message_quota_exceeded(self, mock_service_factory):
        """Test sending message when quota is exceeded"""
        conversation = AIConversation.objects.create(
            user=self.user,
            tenant=self.tenant,
            title='Test Conversation'
        )
        
        # Mock AI service to raise quota exceeded error
        mock_service = MagicMock()
        mock_service.chat_with_tutor.side_effect = QuotaExceededError('Quota exceeded')
        mock_service_factory.return_value = mock_service
        
        data = {'message': 'Hello AI!'}
        
        response = self.client.post(
            f'/api/v1/ai/conversations/{conversation.id}/send_message/',
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.data['error_type'], 'quota_exceeded')
    
    @patch('apps.ai.views.AIServiceFactory.create_service_from_request')
    def test_generate_summary_success(self, mock_service_factory):
        """Test generating content summary"""
        # Mock AI service
        mock_service = MagicMock()
        mock_service.generate_content_summary.return_value = (
            'This is a test summary.',
            ['Key point 1', 'Key point 2'],
            {'tokens_used': 50, 'generation_time_ms': 1000}
        )
        mock_service_factory.return_value = mock_service
        
        data = {
            'content': 'This is test content for summarization.',
            'content_type': 'text',
            'content_title': 'Test Content'
        }
        
        response = self.client.post('/api/v1/ai/summaries/generate/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['summary'], 'This is a test summary.')
        self.assertEqual(len(response.data['key_points']), 2)
    
    @patch('apps.ai.views.AIServiceFactory.create_service_from_request')
    def test_generate_quiz_success(self, mock_service_factory):
        """Test generating quiz from content"""
        # Create a test course
        course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.user,
            tenant=self.tenant
        )
        
        # Mock AI service
        mock_questions = [
            {
                'question': 'What is Python?',
                'options': ['A language', 'A snake', 'A tool', 'A framework'],
                'correct_answer': 0,
                'explanation': 'Python is a programming language.'
            }
        ]
        mock_service = MagicMock()
        mock_service.generate_quiz.return_value = (
            mock_questions,
            {'tokens_used': 75, 'generation_time_ms': 1500}
        )
        mock_service_factory.return_value = mock_service
        
        data = {
            'content': 'Python is a programming language...',
            'course_id': str(course.id),
            'title': 'Python Quiz',
            'num_questions': 1,
            'difficulty': 'easy'
        }
        
        response = self.client.post('/api/v1/ai/quizzes/generate/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['questions']), 1)
        self.assertEqual(response.data['questions'][0]['question'], 'What is Python?')
    
    @patch('apps.ai.views.AIServiceFactory.create_service_from_request')
    def test_get_usage_stats(self, mock_service_factory):
        """Test getting current usage statistics"""
        # Mock AI service
        mock_stats = {
            'chat': {'messages_used': 10, 'messages_limit': 100, 'percentage_used': 10.0},
            'summaries': {'summaries_used': 2, 'summaries_limit': 20, 'percentage_used': 10.0},
            'quizzes': {'quizzes_used': 1, 'quizzes_limit': 10, 'percentage_used': 10.0},
            'cost': {'total_cost_usd': 1.25, 'cost_limit_usd': 10.00, 'percentage_used': 12.5},
            'month': '2024-01'
        }
        mock_service = MagicMock()
        mock_service.get_usage_stats.return_value = mock_stats
        mock_service_factory.return_value = mock_service
        
        response = self.client.get('/api/v1/ai/usage/current_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['stats']['chat']['messages_used'], 10)
        self.assertEqual(response.data['stats']['month'], '2024-01')