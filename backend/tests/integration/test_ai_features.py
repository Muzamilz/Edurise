"""
Integration tests for AI features including chat, summarization, quiz generation,
and quota enforcement as specified in requirements 6.1, 6.2, 6.3, 6.5
"""

import json
import uuid
from decimal import Decimal
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.accounts.models import Organization
from apps.courses.models import Course
from apps.ai.models import (
    AIConversation, AIMessage, AIContentSummary, 
    AIQuiz, AIUsageQuota, AIRateLimit
)
from apps.ai.services import AIService, QuotaExceededError, RateLimitExceededError
from apps.ai.providers import GeminiProvider

User = get_user_model()


class AIIntegrationTestCase(APITestCase):
    """Base test case for AI integration tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create tenant (organization)
        self.tenant = Organization.objects.create(
            name="Test University",
            subdomain="testuni",
            subscription_plan="pro"
        )
        
        # Create users
        self.student = User.objects.create_user(
            email="student@testuni.edu",
            password="testpass123",
            first_name="Test",
            last_name="Student"
        )
        
        self.instructor = User.objects.create_user(
            email="instructor@testuni.edu",
            password="testpass123",
            first_name="Test",
            last_name="Instructor",
            is_teacher=True,
            is_approved_teacher=True
        )
        
        # Create course
        self.course = Course.objects.create(
            title="Introduction to AI",
            description="Learn the basics of artificial intelligence",
            instructor=self.instructor,
            tenant=self.tenant,
            price=Decimal('99.99'),
            category='technology',
            is_public=True
        )
        
        # Set up API client
        self.client = APIClient()
        
        # Mock Gemini provider responses
        self.mock_gemini_responses()
    
    def mock_gemini_responses(self):
        """Mock Gemini API responses for consistent testing"""
        self.mock_chat_response = {
            'response': "This is a helpful AI tutor response about the topic you asked about.",
            'tokens_used': 150,
            'response_time_ms': 800
        }
        
        self.mock_summary_response = {
            'summary': "This is a concise summary of the provided content covering the main points.",
            'key_points': [
                "Key concept 1: Important learning objective",
                "Key concept 2: Critical understanding point",
                "Key concept 3: Practical application"
            ],
            'tokens_used': 200,
            'generation_time_ms': 1200
        }
        
        self.mock_quiz_response = {
            'questions': [
                {
                    'question': 'What is artificial intelligence?',
                    'type': 'multiple_choice',
                    'options': [
                        'A computer program',
                        'Machine learning algorithms',
                        'Simulation of human intelligence',
                        'Data processing system'
                    ],
                    'correct_answer': 2,
                    'explanation': 'AI is the simulation of human intelligence in machines.'
                },
                {
                    'question': 'Which of the following is a type of machine learning?',
                    'type': 'multiple_choice',
                    'options': [
                        'Supervised learning',
                        'Unsupervised learning',
                        'Reinforcement learning',
                        'All of the above'
                    ],
                    'correct_answer': 3,
                    'explanation': 'All three are major types of machine learning.'
                }
            ],
            'tokens_used': 300,
            'generation_time_ms': 1500
        }
    
    def authenticate_user(self, user):
        """Authenticate user for API requests"""
        self.client.force_authenticate(user=user)
        # Simulate tenant middleware
        self.client.defaults['HTTP_HOST'] = f"{self.tenant.subdomain}.edurise.com"


class AITutorChatIntegrationTest(AIIntegrationTestCase):
    """Integration tests for AI tutor chat functionality and context retention (Requirement 6.1)"""
    
    @patch.object(GeminiProvider, 'generate_response')
    def test_ai_tutor_chat_conversation_flow(self, mock_generate):
        """Test complete AI tutor chat conversation with context retention"""
        # Mock Gemini response
        mock_generate.return_value = (
            self.mock_chat_response['response'],
            self.mock_chat_response['tokens_used'],
            self.mock_chat_response['response_time_ms']
        )
        
        self.authenticate_user(self.student)
        
        # Create conversation
        conversation_data = {
            'title': 'AI Learning Session',
            'conversation_type': 'tutor',
            'context': {
                'course_id': str(self.course.id),
                'topic': 'machine learning basics'
            }
        }
        
        response = self.client.post('/api/v1/ai/conversations/', conversation_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        conversation_id = response.data['id']
        
        # Send first message
        message_data = {
            'message': 'What is machine learning?',
            'context': {'topic': 'machine learning basics'}
        }
        
        response = self.client.post(
            f'/api/v1/ai/conversations/{conversation_id}/send_message/',
            message_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('ai_response', response.data)
        self.assertIn('metadata', response.data)
        
        # Verify conversation context is maintained
        conversation = AIConversation.objects.get(id=conversation_id)
        self.assertEqual(conversation.context['course_id'], str(self.course.id))
        self.assertEqual(conversation.context['topic'], 'machine learning basics')
        
        # Send follow-up message to test context retention
        followup_data = {
            'message': 'Can you give me an example?',
            'context': {}
        }
        
        response = self.client.post(
            f'/api/v1/ai/conversations/{conversation_id}/send_message/',
            followup_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify message history is maintained
        messages_response = self.client.get(f'/api/v1/ai/conversations/{conversation_id}/messages/')
        self.assertEqual(messages_response.status_code, status.HTTP_200_OK)
        
        messages = messages_response.data
        self.assertEqual(len(messages), 4)  # 2 user messages + 2 AI responses
        
        # Verify message order and content
        self.assertEqual(messages[0]['role'], 'user')
        self.assertEqual(messages[0]['content'], 'What is machine learning?')
        self.assertEqual(messages[1]['role'], 'assistant')
        self.assertEqual(messages[2]['role'], 'user')
        self.assertEqual(messages[2]['content'], 'Can you give me an example?')
        self.assertEqual(messages[3]['role'], 'assistant')
        
        # Verify Gemini was called with conversation history
        self.assertEqual(mock_generate.call_count, 2)
        
        # Check that second call includes previous messages for context
        second_call_args = mock_generate.call_args_list[1]
        messages_arg = second_call_args[0][0]  # First positional argument
        self.assertGreater(len(messages_arg), 2)  # Should include previous messages
    
    @patch.object(GeminiProvider, 'generate_response')
    def test_ai_tutor_context_retention_across_sessions(self, mock_generate):
        """Test that conversation context is retained across multiple sessions"""
        mock_generate.return_value = (
            self.mock_chat_response['response'],
            self.mock_chat_response['tokens_used'],
            self.mock_chat_response['response_time_ms']
        )
        
        self.authenticate_user(self.student)
        
        # Create conversation with course context
        conversation_data = {
            'title': 'Persistent Learning Session',
            'conversation_type': 'course_help',
            'context': {
                'course_id': str(self.course.id),
                'learning_objectives': ['understand ML basics', 'apply algorithms'],
                'current_module': 'introduction'
            },
            'course': str(self.course.id)
        }
        
        response = self.client.post('/api/v1/ai/conversations/', conversation_data, format='json')
        conversation_id = response.data['id']
        
        # Send message in first session
        self.client.post(
            f'/api/v1/ai/conversations/{conversation_id}/send_message/',
            {'message': 'Explain supervised learning'},
            format='json'
        )
        
        # Simulate new session - get conversation and verify context
        conversation_response = self.client.get(f'/api/v1/ai/conversations/{conversation_id}/')
        self.assertEqual(conversation_response.status_code, status.HTTP_200_OK)
        
        conversation_data = conversation_response.data
        self.assertEqual(conversation_data['context']['course_id'], str(self.course.id))
        self.assertIn('learning_objectives', conversation_data['context'])
        self.assertEqual(conversation_data['context']['current_module'], 'introduction')
        
        # Send follow-up message that should use retained context
        response = self.client.post(
            f'/api/v1/ai/conversations/{conversation_id}/send_message/',
            {'message': 'How does this relate to what we discussed before?'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the AI service received the full context
        call_args = mock_generate.call_args_list[-1]
        context_arg = call_args[0][1]  # Second positional argument (context)
        self.assertEqual(context_arg['course_id'], str(self.course.id))
        self.assertIn('learning_objectives', context_arg)


class AIContentSummarizationIntegrationTest(AIIntegrationTestCase):
    """Integration tests for content summarization accuracy and display (Requirement 6.2)"""
    
    @patch.object(GeminiProvider, 'generate_summary')
    def test_content_summarization_generation_and_display(self, mock_generate_summary):
        """Test AI content summarization generation and accurate display"""
        # Mock Gemini summary response
        mock_generate_summary.return_value = (
            self.mock_summary_response['summary'],
            self.mock_summary_response['key_points'],
            self.mock_summary_response['tokens_used'],
            self.mock_summary_response['generation_time_ms']
        )
        
        self.authenticate_user(self.student)
        
        # Test content to summarize
        test_content = """
        Machine learning is a subset of artificial intelligence that focuses on algorithms
        that can learn and make decisions from data. There are three main types of machine
        learning: supervised learning, unsupervised learning, and reinforcement learning.
        
        Supervised learning uses labeled training data to learn a mapping function from
        inputs to outputs. Common examples include classification and regression problems.
        
        Unsupervised learning finds patterns in data without labeled examples. Clustering
        and dimensionality reduction are typical unsupervised learning tasks.
        
        Reinforcement learning involves an agent learning to make decisions by interacting
        with an environment and receiving rewards or penalties for its actions.
        """
        
        # Generate summary
        summary_data = {
            'content': test_content,
            'content_type': 'course_module',
            'content_id': str(uuid.uuid4()),
            'content_title': 'Introduction to Machine Learning Types',
            'course_id': str(self.course.id)
        }
        
        response = self.client.post('/api/v1/ai/summaries/generate/', summary_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify summary content
        summary_response = response.data
        self.assertIn('summary', summary_response)
        self.assertIn('key_points', summary_response)
        self.assertIn('metadata', summary_response)
        
        # Verify summary is saved to database
        summary_id = summary_response['metadata']['summary_id']
        saved_summary = AIContentSummary.objects.get(id=summary_id)
        
        self.assertEqual(saved_summary.user, self.student)
        self.assertEqual(saved_summary.course, self.course)
        self.assertEqual(saved_summary.content_type, 'course_module')
        self.assertEqual(saved_summary.content_title, 'Introduction to Machine Learning Types')
        self.assertEqual(saved_summary.summary, self.mock_summary_response['summary'])
        self.assertEqual(saved_summary.key_points, self.mock_summary_response['key_points'])
        
        # Test retrieving summaries list
        summaries_response = self.client.get('/api/v1/ai/summaries/')
        self.assertEqual(summaries_response.status_code, status.HTTP_200_OK)
        
        # Verify we get a paginated response with our summary
        self.assertIn('results', summaries_response.data)
        summaries = summaries_response.data['results']
        self.assertGreater(len(summaries), 0)
        
        # Find our specific summary
        our_summary = next((s for s in summaries if s['content_title'] == 'Introduction to Machine Learning Types'), None)
        self.assertIsNotNone(our_summary)
        
        # Test retrieving specific summary
        summary_detail_response = self.client.get(f'/api/v1/ai/summaries/{summary_id}/')
        self.assertEqual(summary_detail_response.status_code, status.HTTP_200_OK)
        
        summary_detail = summary_detail_response.data
        self.assertEqual(summary_detail['summary'], self.mock_summary_response['summary'])
        self.assertEqual(summary_detail['key_points'], self.mock_summary_response['key_points'])
    
    @patch.object(GeminiProvider, 'generate_summary')
    def test_summary_caching_and_performance(self, mock_generate_summary):
        """Test that summaries are cached for performance"""
        mock_generate_summary.return_value = (
            self.mock_summary_response['summary'],
            self.mock_summary_response['key_points'],
            self.mock_summary_response['tokens_used'],
            self.mock_summary_response['generation_time_ms']
        )
        
        self.authenticate_user(self.student)
        
        content_id = str(uuid.uuid4())
        summary_data = {
            'content': 'Test content for caching',
            'content_type': 'video',
            'content_id': content_id,
            'content_title': 'Test Video',
            'course_id': str(self.course.id)
        }
        
        # First request - should call Gemini
        response1 = self.client.post('/api/v1/ai/summaries/generate/', summary_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(mock_generate_summary.call_count, 1)
        
        # Second request with same content_id - should use cache
        response2 = self.client.post('/api/v1/ai/summaries/generate/', summary_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Verify same response but no additional Gemini call
        self.assertEqual(response1.data['summary'], response2.data['summary'])
        self.assertEqual(mock_generate_summary.call_count, 1)  # Still only 1 call


class AIQuizGenerationIntegrationTest(AIIntegrationTestCase):
    """Integration tests for quiz generation and submission process (Requirement 6.3)"""
    
    @patch.object(GeminiProvider, 'generate_quiz')
    def test_quiz_generation_and_submission_process(self, mock_generate_quiz):
        """Test complete quiz generation and submission workflow"""
        # Mock Gemini quiz response
        mock_generate_quiz.return_value = (
            self.mock_quiz_response['questions'],
            self.mock_quiz_response['tokens_used'],
            self.mock_quiz_response['generation_time_ms']
        )
        
        self.authenticate_user(self.student)
        
        # Test content for quiz generation
        quiz_content = """
        Artificial Intelligence (AI) is the simulation of human intelligence in machines.
        Machine learning is a subset of AI that enables computers to learn without being
        explicitly programmed. Deep learning is a subset of machine learning that uses
        neural networks with multiple layers.
        """
        
        # Generate quiz
        quiz_data = {
            'content': quiz_content,
            'course_id': str(self.course.id),
            'title': 'AI Fundamentals Quiz',
            'num_questions': 2,
            'difficulty': 'medium'
        }
        
        response = self.client.post('/api/v1/ai/quizzes/generate/', quiz_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify quiz content
        quiz_response = response.data
        self.assertIn('questions', quiz_response)
        self.assertIn('metadata', quiz_response)
        
        questions = quiz_response['questions']
        self.assertEqual(len(questions), 2)
        
        # Verify question structure
        for question in questions:
            self.assertIn('question', question)
            self.assertIn('type', question)
            self.assertIn('options', question)
            self.assertIn('correct_answer', question)
            self.assertIn('explanation', question)
            
            # Verify question has proper multiple choice structure
            self.assertEqual(question['type'], 'multiple_choice')
            self.assertEqual(len(question['options']), 4)
            self.assertIsInstance(question['correct_answer'], int)
            self.assertGreaterEqual(question['correct_answer'], 0)
            self.assertLess(question['correct_answer'], len(question['options']))
        
        # Verify quiz is saved to database
        quiz_id = quiz_response['metadata']['quiz_id']
        saved_quiz = AIQuiz.objects.get(id=quiz_id)
        
        self.assertEqual(saved_quiz.user, self.student)
        self.assertEqual(saved_quiz.course, self.course)
        self.assertEqual(saved_quiz.title, 'AI Fundamentals Quiz')
        self.assertEqual(saved_quiz.difficulty_level, 'medium')
        self.assertEqual(len(saved_quiz.questions), 2)
        
        # Test retrieving quiz
        quiz_detail_response = self.client.get(f'/api/v1/ai/quizzes/{quiz_id}/')
        self.assertEqual(quiz_detail_response.status_code, status.HTTP_200_OK)
        
        quiz_detail = quiz_detail_response.data
        self.assertEqual(quiz_detail['title'], 'AI Fundamentals Quiz')
        self.assertEqual(len(quiz_detail['questions']), 2)
    
    @patch.object(GeminiProvider, 'generate_quiz')
    def test_quiz_generation_validation(self, mock_generate_quiz):
        """Test quiz generation input validation"""
        mock_generate_quiz.return_value = (
            self.mock_quiz_response['questions'],
            self.mock_quiz_response['tokens_used'],
            self.mock_quiz_response['generation_time_ms']
        )
        
        self.authenticate_user(self.student)
        
        # Test missing content
        response = self.client.post('/api/v1/ai/quizzes/generate/', {
            'course_id': str(self.course.id),
            'title': 'Test Quiz'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Content is required', response.data['error'])
        
        # Test missing course_id
        response = self.client.post('/api/v1/ai/quizzes/generate/', {
            'content': 'Test content',
            'title': 'Test Quiz'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Course ID is required', response.data['error'])
        
        # Test invalid num_questions
        response = self.client.post('/api/v1/ai/quizzes/generate/', {
            'content': 'Test content',
            'course_id': str(self.course.id),
            'title': 'Test Quiz',
            'num_questions': 25  # Too many
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('between 1 and 20', response.data['error'])
        
        # Test invalid course_id
        response = self.client.post('/api/v1/ai/quizzes/generate/', {
            'content': 'Test content',
            'course_id': str(uuid.uuid4()),  # Non-existent course
            'title': 'Test Quiz'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('Course not found', response.data['error'])


class AIQuotaEnforcementIntegrationTest(TransactionTestCase):
    """Integration tests for quota enforcement and rate limiting (Requirement 6.5)"""
    
    def setUp(self):
        """Set up test data"""
        super().setUp()
        
        # Create tenant (organization) with basic plan (lower limits)
        self.tenant = Organization.objects.create(
            name="Basic University",
            subdomain="basicuni",
            subscription_plan="basic"
        )
        
        # Create user
        self.user = User.objects.create_user(
            email="student@basicuni.edu",
            password="testpass123"
        )
        
        # Create course
        self.course = Course.objects.create(
            title="Test Course",
            description="Test course for quota testing",
            instructor=self.user,
            tenant=self.tenant,
            category='technology'
        )
        
        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.client.defaults['HTTP_HOST'] = f"{self.tenant.subdomain}.edurise.com"
    
    @patch.object(GeminiProvider, 'generate_response')
    def test_chat_quota_enforcement(self, mock_generate):
        """Test that chat quota limits are enforced"""
        mock_generate.return_value = ("Response", 100, 500)
        
        # Create quota with low limits for testing
        current_month = timezone.now().date().replace(day=1)
        quota = AIUsageQuota.objects.create(
            user=self.user,
            tenant=self.tenant,
            month=current_month,
            chat_messages_limit=2,  # Very low limit
            chat_tokens_limit=1000
        )
        
        # Create conversation
        conversation_response = self.client.post('/api/v1/ai/conversations/', {
            'title': 'Quota Test',
            'conversation_type': 'tutor'
        }, format='json')
        conversation_id = conversation_response.data['id']
        
        # First message - should succeed
        response1 = self.client.post(
            f'/api/v1/ai/conversations/{conversation_id}/send_message/',
            {'message': 'First message'},
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Second message - should succeed
        response2 = self.client.post(
            f'/api/v1/ai/conversations/{conversation_id}/send_message/',
            {'message': 'Second message'},
            format='json'
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Third message - should fail due to quota
        response3 = self.client.post(
            f'/api/v1/ai/conversations/{conversation_id}/send_message/',
            {'message': 'Third message'},
            format='json'
        )
        self.assertEqual(response3.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response3.data['error_type'], 'quota_exceeded')
        self.assertIn('quota exceeded', response3.data['error'].lower())
        
        # Verify quota usage is tracked
        quota.refresh_from_db()
        self.assertEqual(quota.chat_messages_used, 2)
    
    @patch.object(GeminiProvider, 'generate_summary')
    def test_summary_quota_enforcement(self, mock_generate_summary):
        """Test that summary generation quota limits are enforced"""
        mock_generate_summary.return_value = ("Summary", ["Point 1"], 200, 1000)
        
        # Create quota with low limits
        current_month = timezone.now().date().replace(day=1)
        quota = AIUsageQuota.objects.create(
            user=self.user,
            tenant=self.tenant,
            month=current_month,
            summaries_limit=1,  # Very low limit
            summary_tokens_limit=1000
        )
        
        # First summary - should succeed
        response1 = self.client.post('/api/v1/ai/summaries/generate/', {
            'content': 'Test content for summary',
            'content_type': 'text',
            'content_id': str(uuid.uuid4()),
            'content_title': 'Test Content',
            'course_id': str(self.course.id)
        }, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Second summary - should fail due to quota
        response2 = self.client.post('/api/v1/ai/summaries/generate/', {
            'content': 'Another test content',
            'content_type': 'text',
            'content_id': str(uuid.uuid4()),
            'content_title': 'Another Test',
            'course_id': str(self.course.id)
        }, format='json')
        self.assertEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response2.data['error_type'], 'quota_exceeded')
        
        # Verify quota usage
        quota.refresh_from_db()
        self.assertEqual(quota.summaries_generated, 1)
    
    @patch.object(GeminiProvider, 'generate_quiz')
    def test_quiz_quota_enforcement(self, mock_generate_quiz):
        """Test that quiz generation quota limits are enforced"""
        mock_generate_quiz.return_value = ([{"question": "Test?"}], 300, 1500)
        
        # Create quota with low limits
        current_month = timezone.now().date().replace(day=1)
        quota = AIUsageQuota.objects.create(
            user=self.user,
            tenant=self.tenant,
            month=current_month,
            quizzes_limit=1,  # Very low limit
            quiz_tokens_limit=1000
        )
        
        # First quiz - should succeed
        response1 = self.client.post('/api/v1/ai/quizzes/generate/', {
            'content': 'Test content for quiz',
            'course_id': str(self.course.id),
            'title': 'Test Quiz 1',
            'num_questions': 1
        }, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Second quiz - should fail due to quota
        response2 = self.client.post('/api/v1/ai/quizzes/generate/', {
            'content': 'Another test content',
            'course_id': str(self.course.id),
            'title': 'Test Quiz 2',
            'num_questions': 1
        }, format='json')
        self.assertEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response2.data['error_type'], 'quota_exceeded')
        
        # Verify quota usage
        quota.refresh_from_db()
        self.assertEqual(quota.quizzes_generated, 1)
    
    def test_rate_limiting_enforcement(self):
        """Test that rate limiting is enforced"""
        # Create rate limit with very low limits
        rate_limit = AIRateLimit.objects.create(
            user=self.user,
            requests_per_minute=2,  # Very low limit
            requests_per_hour=10,
            requests_per_day=50
        )
        
        # Create conversation for testing
        conversation_response = self.client.post('/api/v1/ai/conversations/', {
            'title': 'Rate Limit Test'
        }, format='json')
        conversation_id = conversation_response.data['id']
        
        with patch.object(GeminiProvider, 'generate_response') as mock_generate:
            mock_generate.return_value = ("Response", 100, 500)
            
            # First two requests should succeed
            for i in range(2):
                response = self.client.post(
                    f'/api/v1/ai/conversations/{conversation_id}/send_message/',
                    {'message': f'Message {i+1}'},
                    format='json'
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Third request should fail due to rate limit
            response = self.client.post(
                f'/api/v1/ai/conversations/{conversation_id}/send_message/',
                {'message': 'Message 3'},
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
            self.assertEqual(response.data['error_type'], 'rate_limit_exceeded')
    
    def test_usage_stats_endpoint(self):
        """Test that usage statistics are accurately reported"""
        # Create quota with some usage
        current_month = timezone.now().date().replace(day=1)
        quota = AIUsageQuota.objects.create(
            user=self.user,
            tenant=self.tenant,
            month=current_month,
            chat_messages_used=5,
            chat_messages_limit=50,
            chat_tokens_used=1000,
            chat_tokens_limit=25000,
            summaries_generated=2,
            summaries_limit=10,
            summary_tokens_used=500,
            summary_tokens_limit=50000,
            quizzes_generated=1,
            quizzes_limit=5,
            quiz_tokens_used=300,
            quiz_tokens_limit=25000,
            total_cost_usd=Decimal('2.50'),
            cost_limit_usd=Decimal('5.00')
        )
        
        # Get usage stats
        response = self.client.get('/api/v1/ai/usage/current_stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats = response.data['stats']
        
        # Verify chat stats
        self.assertEqual(stats['chat']['messages_used'], 5)
        self.assertEqual(stats['chat']['messages_limit'], 50)
        self.assertEqual(stats['chat']['percentage_used'], 10.0)
        
        # Verify summary stats
        self.assertEqual(stats['summaries']['summaries_used'], 2)
        self.assertEqual(stats['summaries']['summaries_limit'], 10)
        self.assertEqual(stats['summaries']['percentage_used'], 20.0)
        
        # Verify quiz stats
        self.assertEqual(stats['quizzes']['quizzes_used'], 1)
        self.assertEqual(stats['quizzes']['quizzes_limit'], 5)
        self.assertEqual(stats['quizzes']['percentage_used'], 20.0)
        
        # Verify cost stats
        self.assertEqual(stats['cost']['total_cost_usd'], 2.50)
        self.assertEqual(stats['cost']['cost_limit_usd'], 5.00)
        self.assertEqual(stats['cost']['percentage_used'], 50.0)


class AIServiceIntegrationTest(TestCase):
    """Integration tests for AI service layer functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.tenant = Organization.objects.create(
            name="Service Test Uni",
            subdomain="servicetest",
            subscription_plan="pro"
        )
        
        self.user = User.objects.create_user(
            email="test@servicetest.edu",
            password="testpass123"
        )
        
        self.course = Course.objects.create(
            title="Service Test Course",
            description="Course for service testing",
            instructor=self.user,
            tenant=self.tenant,
            category='technology'
        )
    
    @patch.object(GeminiProvider, 'generate_response')
    def test_ai_service_error_handling(self, mock_generate):
        """Test that AI service properly handles and propagates errors"""
        # Test Gemini API error
        mock_generate.side_effect = Exception("Gemini API error")
        
        ai_service = AIService(self.user, self.tenant)
        
        with self.assertRaises(Exception):
            ai_service.chat_with_tutor(
                str(uuid.uuid4()),
                "Test message",
                {}
            )
    
    def test_quota_creation_based_on_tenant_plan(self):
        """Test that quotas are created with correct limits based on tenant subscription plan"""
        ai_service = AIService(self.user, self.tenant)
        quota = ai_service._get_or_create_quota()
        
        # Pro plan should have higher limits than basic
        self.assertEqual(quota.chat_messages_limit, 200)
        self.assertEqual(quota.summaries_limit, 50)
        self.assertEqual(quota.quizzes_limit, 25)
        self.assertEqual(quota.cost_limit_usd, Decimal('25.00'))
        
        # Test basic plan
        basic_tenant = Organization.objects.create(
            name="Basic Tenant",
            subdomain="basic",
            subscription_plan="basic"
        )
        
        basic_user = User.objects.create_user(
            email="basic@basic.edu",
            password="testpass123"
        )
        
        basic_service = AIService(basic_user, basic_tenant)
        basic_quota = basic_service._get_or_create_quota()
        
        # Basic plan should have lower limits
        self.assertEqual(basic_quota.chat_messages_limit, 50)
        self.assertEqual(basic_quota.summaries_limit, 10)
        self.assertEqual(basic_quota.quizzes_limit, 5)
        self.assertEqual(basic_quota.cost_limit_usd, Decimal('5.00'))