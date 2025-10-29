from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock
from apps.accounts.models import Organization, UserProfile
from apps.courses.models import Course
from apps.ai.models import AIConversation, AIMessage, AIContentSummary, AIQuiz, AIUsageQuota
from apps.ai.services import QuotaExceededError, RateLimitExceededError, AIServiceError
from apps.accounts.services import JWTAuthService

User = get_user_model()


class AIConversationViewSetTest(TestCase):
    """Test cases for AIConversationViewSet"""
    
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
        
        self.instructor = User.objects.create_user(
            email='instructor@example.com',
            password='testpass123',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
        UserProfile.objects.create(user=self.instructor, tenant=self.tenant)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology'
        )
        
        self.conversation = AIConversation.objects.create(
            user=self.user,
            tenant=self.tenant,
            title='Test Conversation',
            conversation_type='tutor',
            context={'course_id': str(self.course.id)}
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_create_conversation(self):
        """Test creating AI conversation"""
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/ai/ai-conversations/',
            {
                'title': 'New Conversation',
                'conversation_type': 'tutor',
                'context': {'course_id': str(self.course.id)}
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify conversation was created
        conversation = AIConversation.objects.get(title='New Conversation')
        self.assertEqual(conversation.user, self.user)
        self.assertEqual(conversation.tenant, self.tenant)
    
    def test_list_conversations(self):
        """Test listing user's conversations"""
        self.authenticate_user(self.user)
        
        response = self.client.get('/api/v1/ai/ai-conversations/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], 'Test Conversation')
    
    @patch('apps.ai.services.AIServiceFactory.create_service_from_request')
    def test_send_message_success(self, mock_create_service):
        """Test sending message to AI tutor successfully"""
        mock_ai_service = Mock()
        mock_ai_service.chat_with_tutor.return_value = (
            "This is the AI response",
            {"tokens_used": 50, "model": "gpt-3.5-turbo"}
        )
        mock_create_service.return_value = mock_ai_service
        
        self.authenticate_user(self.user)
        
        response = self.client.post(
            f'/api/v1/ai/ai-conversations/{self.conversation.id}/send_message/',
            {
                'message': 'What is Python?',
                'context': {'topic': 'programming'}
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['ai_response'], "This is the AI response")
        self.assertIn('metadata', data)
        
        mock_ai_service.chat_with_tutor.assert_called_once_with(
            str(self.conversation.id),
            'What is Python?',
            {'topic': 'programming'}
        )
    
    def test_send_message_empty_content(self):
        """Test sending empty message"""
        self.authenticate_user(self.user)
        
        response = self.client.post(
            f'/api/v1/ai/ai-conversations/{self.conversation.id}/send_message/',
            {
                'message': '',
                'context': {}
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)
    
    @patch('apps.ai.services.AIServiceFactory.create_service_from_request')
    def test_send_message_quota_exceeded(self, mock_create_service):
        """Test sending message when quota is exceeded"""
        mock_ai_service = Mock()
        mock_ai_service.chat_with_tutor.side_effect = QuotaExceededError("Monthly quota exceeded")
        mock_create_service.return_value = mock_ai_service
        
        self.authenticate_user(self.user)
        
        response = self.client.post(
            f'/api/v1/ai/ai-conversations/{self.conversation.id}/send_message/',
            {
                'message': 'What is Python?',
                'context': {}
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        data = response.json()
        self.assertEqual(data['error_type'], 'quota_exceeded')
    
    @patch('apps.ai.services.AIServiceFactory.create_service_from_request')
    def test_send_message_rate_limit(self, mock_create_service):
        """Test sending message when rate limited"""
        mock_ai_service = Mock()
        mock_ai_service.chat_with_tutor.side_effect = RateLimitExceededError("Rate limit exceeded")
        mock_create_service.return_value = mock_ai_service
        
        self.authenticate_user(self.user)
        
        response = self.client.post(
            f'/api/v1/ai/ai-conversations/{self.conversation.id}/send_message/',
            {
                'message': 'What is Python?',
                'context': {}
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        data = response.json()
        self.assertEqual(data['error_type'], 'rate_limit_exceeded')
    
    @patch('apps.ai.services.AIServiceFactory.create_service_from_request')
    def test_send_message_ai_service_error(self, mock_create_service):
        """Test sending message when AI service fails"""
        mock_ai_service = Mock()
        mock_ai_service.chat_with_tutor.side_effect = AIServiceError("AI service unavailable")
        mock_create_service.return_value = mock_ai_service
        
        self.authenticate_user(self.user)
        
        response = self.client.post(
            f'/api/v1/ai/ai-conversations/{self.conversation.id}/send_message/',
            {
                'message': 'What is Python?',
                'context': {}
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        data = response.json()
        self.assertEqual(data['error_type'], 'ai_service_error')
    
    def test_get_conversation_messages(self):
        """Test getting conversation messages"""
        # Create test messages
        AIMessage.objects.create(
            conversation=self.conversation,
            role='user',
            content='Hello AI',
            tenant=self.tenant
        )
        
        AIMessage.objects.create(
            conversation=self.conversation,
            role='assistant',
            content='Hello! How can I help you?',
            tenant=self.tenant
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.get(f'/api/v1/ai/ai-conversations/{self.conversation.id}/messages/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['role'], 'user')
        self.assertEqual(data[1]['role'], 'assistant')


class AIContentSummaryViewSetTest(TestCase):
    """Test cases for AIContentSummaryViewSet"""
    
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
            title='Test Course',
            description='Test Description',
            instructor=self.user,
            tenant=self.tenant,
            category='technology'
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    @patch('apps.ai.services.AIServiceFactory.create_service_from_request')
    def test_generate_content_summary(self, mock_create_service):
        """Test generating content summary"""
        mock_ai_service = Mock()
        mock_ai_service.generate_content_summary.return_value = (
            "This is a summary of the content",
            ["Key point 1", "Key point 2", "Key point 3"],
            {"tokens_used": 100, "model": "gpt-3.5-turbo"}
        )
        mock_create_service.return_value = mock_ai_service
        
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/ai/ai-summaries/generate/',
            {
                'content': 'This is a long piece of content that needs to be summarized...',
                'content_type': 'text',
                'content_title': 'Introduction to Python',
                'course_id': str(self.course.id)
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['summary'], "This is a summary of the content")
        self.assertEqual(len(data['key_points']), 3)
        self.assertIn('metadata', data)
    
    def test_generate_summary_missing_content(self):
        """Test generating summary without content"""
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/ai/ai-summaries/generate/',
            {
                'content_type': 'text',
                'content_title': 'Test'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)
    
    @patch('apps.ai.services.AIServiceFactory.create_service_from_request')
    def test_generate_summary_quota_exceeded(self, mock_create_service):
        """Test generating summary when quota exceeded"""
        mock_ai_service = Mock()
        mock_ai_service.generate_content_summary.side_effect = QuotaExceededError("Quota exceeded")
        mock_create_service.return_value = mock_ai_service
        
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/ai/ai-summaries/generate/',
            {
                'content': 'Test content',
                'content_type': 'text'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        data = response.json()
        self.assertEqual(data['error_type'], 'quota_exceeded')


class AIQuizViewSetTest(TestCase):
    """Test cases for AIQuizViewSet"""
    
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
            title='Test Course',
            description='Test Description',
            instructor=self.user,
            tenant=self.tenant,
            category='technology'
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    @patch('apps.ai.services.AIServiceFactory.create_service_from_request')
    def test_generate_quiz(self, mock_create_service):
        """Test generating quiz from content"""
        mock_questions = [
            {
                "question": "What is Python?",
                "type": "multiple_choice",
                "options": ["A programming language", "A snake", "A tool", "A framework"],
                "correct_answer": "A programming language",
                "explanation": "Python is a high-level programming language"
            },
            {
                "question": "Is Python interpreted?",
                "type": "true_false",
                "correct_answer": True,
                "explanation": "Python is an interpreted language"
            }
        ]
        
        mock_ai_service = Mock()
        mock_ai_service.generate_quiz.return_value = (
            mock_questions,
            {"tokens_used": 150, "model": "gpt-3.5-turbo"}
        )
        mock_create_service.return_value = mock_ai_service
        
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/ai/ai-quizzes/generate/',
            {
                'content': 'Python is a programming language...',
                'course_id': str(self.course.id),
                'title': 'Python Basics Quiz',
                'num_questions': 2,
                'difficulty': 'medium'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(len(data['questions']), 2)
        self.assertIn('metadata', data)
    
    def test_generate_quiz_missing_content(self):
        """Test generating quiz without content"""
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/ai/ai-quizzes/generate/',
            {
                'course_id': str(self.course.id),
                'title': 'Test Quiz'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)
    
    def test_generate_quiz_missing_course_id(self):
        """Test generating quiz without course ID"""
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/ai/ai-quizzes/generate/',
            {
                'content': 'Test content',
                'title': 'Test Quiz'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)
    
    def test_generate_quiz_invalid_num_questions(self):
        """Test generating quiz with invalid number of questions"""
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/ai/ai-quizzes/generate/',
            {
                'content': 'Test content',
                'course_id': str(self.course.id),
                'num_questions': 25  # Too many
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)


class AIUsageViewSetTest(TestCase):
    """Test cases for AIUsageViewSet"""
    
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
        
        # Create usage quota
        self.usage_quota = AIUsageQuota.objects.create(
            user=self.user,
            tenant=self.tenant,
            quota_type='monthly',
            total_quota=1000,
            used_quota=250
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_list_usage_quotas(self):
        """Test listing user's usage quotas"""
        self.authenticate_user(self.user)
        
        response = self.client.get('/api/v1/ai/ai-usage/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['total_quota'], 1000)
        self.assertEqual(data['results'][0]['used_quota'], 250)
    
    @patch('apps.ai.services.AIServiceFactory.create_service_from_request')
    def test_current_stats(self, mock_create_service):
        """Test getting current usage statistics"""
        mock_stats = {
            'current_month': {
                'total_requests': 25,
                'tokens_used': 1250,
                'quota_remaining': 750,
                'quota_percentage': 25.0
            },
            'breakdown': {
                'chat_requests': 15,
                'summary_requests': 7,
                'quiz_requests': 3
            },
            'daily_usage': [
                {'date': '2024-01-01', 'requests': 5, 'tokens': 250},
                {'date': '2024-01-02', 'requests': 8, 'tokens': 400}
            ]
        }
        
        mock_ai_service = Mock()
        mock_ai_service.get_usage_stats.return_value = mock_stats
        mock_create_service.return_value = mock_ai_service
        
        self.authenticate_user(self.user)
        
        response = self.client.get('/api/v1/ai/ai-usage/current_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertIn('stats', data)
        self.assertEqual(data['stats']['current_month']['total_requests'], 25)
        self.assertEqual(data['stats']['breakdown']['chat_requests'], 15)
    
    @patch('apps.ai.services.AIServiceFactory.create_service_from_request')
    def test_current_stats_error(self, mock_create_service):
        """Test getting usage stats when service fails"""
        mock_create_service.side_effect = Exception("Service unavailable")
        
        self.authenticate_user(self.user)
        
        response = self.client.get('/api/v1/ai/ai-usage/current_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = response.json()
        self.assertIn('error', data)