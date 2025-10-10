import logging
import time
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta

from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from django.contrib.auth import get_user_model

from .models import (
    AIConversation, AIMessage, AIContentSummary, 
    AIQuiz, AIUsageQuota, AIRateLimit
)
from .providers import GeminiProvider
from apps.courses.models import Course

User = get_user_model()
logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass


class QuotaExceededError(AIServiceError):
    """Exception raised when usage quota is exceeded"""
    pass


class RateLimitExceededError(AIServiceError):
    """Exception raised when rate limit is exceeded"""
    pass


class AIService:
    """
    Main AI service class that orchestrates all AI functionality
    including chat, summarization, quiz generation, and quota management
    """
    
    def __init__(self, user: User, tenant=None):
        self.user = user
        self.tenant = tenant
        self.provider = GeminiProvider()
    
    def chat_with_tutor(
        self, 
        conversation_id: str, 
        message: str, 
        context: Optional[Dict] = None
    ) -> Tuple[str, Dict]:
        """
        Send a message to AI tutor and get response
        
        Args:
            conversation_id: UUID of the conversation
            message: User's message
            context: Optional context (course info, etc.)
            
        Returns:
            Tuple of (ai_response, metadata)
            
        Raises:
            QuotaExceededError: If user has exceeded chat quota
            RateLimitExceededError: If rate limit is exceeded
            AIServiceError: For other AI service errors
        """
        try:
            # Check rate limits
            self._check_rate_limits()
            
            # Check usage quota
            quota = self._get_or_create_quota()
            if quota.is_chat_quota_exceeded():
                raise QuotaExceededError("Chat message quota exceeded for this month")
            
            # Get or create conversation
            conversation = self._get_conversation(conversation_id, context)
            
            # Add user message
            user_message = AIMessage.objects.create(
                conversation=conversation,
                role='user',
                content=message
            )
            
            # Get conversation history
            messages = self._get_conversation_history(conversation)
            
            # Generate AI response
            start_time = time.time()
            ai_response, tokens_used, response_time_ms = self.provider.generate_response(
                messages, conversation.context
            )
            
            # Add AI message
            ai_message = AIMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=ai_response,
                tokens_used=tokens_used,
                response_time_ms=response_time_ms
            )
            
            # Update usage tracking
            self._update_chat_usage(quota, tokens_used)
            
            # Update conversation activity
            conversation.last_activity = timezone.now()
            conversation.save()
            
            # Record rate limit usage
            self._record_rate_limit_usage()
            
            metadata = {
                'conversation_id': str(conversation.id),
                'user_message_id': str(user_message.id),
                'ai_message_id': str(ai_message.id),
                'tokens_used': tokens_used,
                'response_time_ms': response_time_ms,
                'remaining_quota': quota.chat_messages_limit - quota.chat_messages_used
            }
            
            return ai_response, metadata
            
        except (QuotaExceededError, RateLimitExceededError):
            raise
        except Exception as e:
            logger.error(f"AI chat error for user {self.user.id}: {str(e)}")
            raise AIServiceError(f"Chat service temporarily unavailable: {str(e)}")
    
    def generate_content_summary(
        self, 
        content: str, 
        content_type: str, 
        content_id: str,
        content_title: str,
        course_id: Optional[str] = None
    ) -> Tuple[str, List[str], Dict]:
        """
        Generate AI summary of content
        
        Args:
            content: Content to summarize
            content_type: Type of content (live_class, course_module, etc.)
            content_id: ID of the content being summarized
            content_title: Title of the content
            course_id: Optional course ID
            
        Returns:
            Tuple of (summary, key_points, metadata)
        """
        try:
            # Check rate limits
            self._check_rate_limits()
            
            # Check usage quota
            quota = self._get_or_create_quota()
            if quota.is_summary_quota_exceeded():
                raise QuotaExceededError("Summary generation quota exceeded for this month")
            
            # Check if summary already exists (caching)
            cache_key = f"ai_summary_{content_id}_{self.user.id}"
            cached_summary = cache.get(cache_key)
            if cached_summary:
                return cached_summary['summary'], cached_summary['key_points'], cached_summary['metadata']
            
            # Generate summary
            start_time = time.time()
            summary, key_points, tokens_used, generation_time_ms = self.provider.generate_summary(
                content, content_type
            )
            
            # Get course if provided
            course = None
            if course_id:
                try:
                    course = Course.objects.get(id=course_id, tenant=self.tenant)
                except Course.DoesNotExist:
                    pass
            
            # Save summary to database
            ai_summary = AIContentSummary.objects.create(
                user=self.user,
                tenant=self.tenant,
                course=course,
                content_type=content_type,
                content_id=content_id,
                content_title=content_title,
                original_content=content[:5000],  # Store first 5000 chars
                summary=summary,
                key_points=key_points,
                tokens_used=tokens_used,
                generation_time_ms=generation_time_ms
            )
            
            # Update usage tracking
            self._update_summary_usage(quota, tokens_used)
            
            # Record rate limit usage
            self._record_rate_limit_usage()
            
            # Cache the result
            result = {
                'summary': summary,
                'key_points': key_points,
                'metadata': {
                    'summary_id': str(ai_summary.id),
                    'tokens_used': tokens_used,
                    'generation_time_ms': generation_time_ms,
                    'remaining_quota': quota.summaries_limit - quota.summaries_generated
                }
            }
            cache.set(cache_key, result, 3600)  # Cache for 1 hour
            
            return summary, key_points, result['metadata']
            
        except (QuotaExceededError, RateLimitExceededError):
            raise
        except Exception as e:
            logger.error(f"AI summary error for user {self.user.id}: {str(e)}")
            raise AIServiceError(f"Summary service temporarily unavailable: {str(e)}")
    
    def generate_quiz(
        self,
        content: str,
        course_id: str,
        title: str,
        num_questions: int = 5,
        difficulty: str = 'medium'
    ) -> Tuple[List[Dict], Dict]:
        """
        Generate AI quiz from content
        
        Args:
            content: Content to generate quiz from
            course_id: Course ID
            title: Quiz title
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            Tuple of (questions, metadata)
        """
        try:
            # Check rate limits
            self._check_rate_limits()
            
            # Check usage quota
            quota = self._get_or_create_quota()
            if quota.is_quiz_quota_exceeded():
                raise QuotaExceededError("Quiz generation quota exceeded for this month")
            
            # Validate parameters
            if num_questions < 1 or num_questions > 20:
                raise AIServiceError("Number of questions must be between 1 and 20")
            
            if difficulty not in ['easy', 'medium', 'hard']:
                raise AIServiceError("Difficulty must be 'easy', 'medium', or 'hard'")
            
            # Get course
            try:
                course = Course.objects.get(id=course_id, tenant=self.tenant)
            except Course.DoesNotExist:
                raise AIServiceError("Course not found")
            
            # Generate quiz
            start_time = time.time()
            questions, tokens_used, generation_time_ms = self.provider.generate_quiz(
                content, num_questions, difficulty
            )
            
            if not questions:
                raise AIServiceError("Failed to generate quiz questions")
            
            # Save quiz to database
            ai_quiz = AIQuiz.objects.create(
                user=self.user,
                tenant=self.tenant,
                course=course,
                title=title,
                description=f"AI-generated quiz from course content ({difficulty} difficulty)",
                difficulty_level=difficulty,
                source_content=content[:5000],  # Store first 5000 chars
                questions=questions,
                tokens_used=tokens_used,
                generation_time_ms=generation_time_ms
            )
            
            # Update usage tracking
            self._update_quiz_usage(quota, tokens_used)
            
            # Record rate limit usage
            self._record_rate_limit_usage()
            
            metadata = {
                'quiz_id': str(ai_quiz.id),
                'tokens_used': tokens_used,
                'generation_time_ms': generation_time_ms,
                'remaining_quota': quota.quizzes_limit - quota.quizzes_generated,
                'difficulty': difficulty,
                'num_questions': len(questions)
            }
            
            return questions, metadata
            
        except (QuotaExceededError, RateLimitExceededError):
            raise
        except Exception as e:
            logger.error(f"AI quiz error for user {self.user.id}: {str(e)}")
            raise AIServiceError(f"Quiz service temporarily unavailable: {str(e)}")
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics for the user"""
        quota = self._get_or_create_quota()
        
        return {
            'chat': {
                'messages_used': quota.chat_messages_used,
                'messages_limit': quota.chat_messages_limit,
                'tokens_used': quota.chat_tokens_used,
                'tokens_limit': quota.chat_tokens_limit,
                'percentage_used': (quota.chat_messages_used / quota.chat_messages_limit) * 100
            },
            'summaries': {
                'summaries_used': quota.summaries_generated,
                'summaries_limit': quota.summaries_limit,
                'tokens_used': quota.summary_tokens_used,
                'tokens_limit': quota.summary_tokens_limit,
                'percentage_used': (quota.summaries_generated / quota.summaries_limit) * 100
            },
            'quizzes': {
                'quizzes_used': quota.quizzes_generated,
                'quizzes_limit': quota.quizzes_limit,
                'tokens_used': quota.quiz_tokens_used,
                'tokens_limit': quota.quiz_tokens_limit,
                'percentage_used': (quota.quizzes_generated / quota.quizzes_limit) * 100
            },
            'cost': {
                'total_cost_usd': float(quota.total_cost_usd),
                'cost_limit_usd': float(quota.cost_limit_usd),
                'percentage_used': (float(quota.total_cost_usd) / float(quota.cost_limit_usd)) * 100
            },
            'month': quota.month.strftime('%Y-%m')
        }
    
    def _get_conversation(self, conversation_id: str, context: Optional[Dict] = None) -> AIConversation:
        """Get or create AI conversation"""
        try:
            conversation = AIConversation.objects.get(
                id=conversation_id,
                user=self.user,
                tenant=self.tenant
            )
        except AIConversation.DoesNotExist:
            # Create new conversation
            conversation = AIConversation.objects.create(
                user=self.user,
                tenant=self.tenant,
                title=f"AI Chat - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                context=context or {}
            )
        
        return conversation
    
    def _get_conversation_history(self, conversation: AIConversation) -> List[Dict]:
        """Get conversation message history"""
        messages = conversation.messages.order_by('created_at')
        return [
            {
                'role': msg.role,
                'content': msg.content
            }
            for msg in messages
        ]
    
    def _get_or_create_quota(self) -> AIUsageQuota:
        """Get or create usage quota for current month"""
        return AIUsageQuota.get_or_create_for_user(self.user, self.tenant)
    
    def _check_rate_limits(self):
        """Check if user has exceeded rate limits"""
        rate_limit, created = AIRateLimit.objects.get_or_create(
            user=self.user,
            defaults={
                'requests_per_minute': 10,
                'requests_per_hour': 100,
                'requests_per_day': 500
            }
        )
        
        if not rate_limit.can_make_request():
            raise RateLimitExceededError("Rate limit exceeded. Please try again later.")
    
    def _record_rate_limit_usage(self):
        """Record a request in rate limiting"""
        rate_limit, _ = AIRateLimit.objects.get_or_create(
            user=self.user,
            defaults={
                'requests_per_minute': 10,
                'requests_per_hour': 100,
                'requests_per_day': 500
            }
        )
        rate_limit.record_request()
    
    @transaction.atomic
    def _update_chat_usage(self, quota: AIUsageQuota, tokens_used: int):
        """Update chat usage statistics"""
        quota.chat_messages_used += 1
        quota.chat_tokens_used += tokens_used
        
        # Calculate and add cost
        cost = self.provider.calculate_cost(tokens_used // 2, tokens_used // 2)  # Rough split
        quota.total_cost_usd += cost
        
        quota.save()
    
    @transaction.atomic
    def _update_summary_usage(self, quota: AIUsageQuota, tokens_used: int):
        """Update summary usage statistics"""
        quota.summaries_generated += 1
        quota.summary_tokens_used += tokens_used
        
        # Calculate and add cost
        cost = self.provider.calculate_cost(tokens_used // 2, tokens_used // 2)  # Rough split
        quota.total_cost_usd += cost
        
        quota.save()
    
    @transaction.atomic
    def _update_quiz_usage(self, quota: AIUsageQuota, tokens_used: int):
        """Update quiz usage statistics"""
        quota.quizzes_generated += 1
        quota.quiz_tokens_used += tokens_used
        
        # Calculate and add cost
        cost = self.provider.calculate_cost(tokens_used // 2, tokens_used // 2)  # Rough split
        quota.total_cost_usd += cost
        
        quota.save()


class AIServiceFactory:
    """Factory class for creating AI service instances"""
    
    @staticmethod
    def create_service(user: User, tenant=None) -> AIService:
        """Create AI service instance for user"""
        return AIService(user, tenant)
    
    @staticmethod
    def create_service_from_request(request) -> AIService:
        """Create AI service instance from Django request"""
        tenant = getattr(request, 'tenant', None)
        return AIService(request.user, tenant)