import uuid
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import (
    AIConversation, AIMessage, AIContentSummary, 
    AIQuiz, AIUsageQuota
)
from .services import AIServiceFactory, QuotaExceededError, RateLimitExceededError, AIServiceError
from .serializers import (
    AIConversationSerializer, AIMessageSerializer, 
    AIContentSummarySerializer, AIQuizSerializer, AIUsageQuotaSerializer
)
from apps.courses.models import Course


class AIConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for AI conversations with enhanced functionality"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AIConversationSerializer
    
    def get_queryset(self):
        """Filter conversations by tenant and user"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return AIConversation.objects.filter(
                tenant=self.request.tenant,
                user=self.request.user
            )
        return AIConversation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create conversation with tenant and user"""
        tenant = getattr(self.request, 'tenant', None)
        serializer.save(user=self.request.user, tenant=tenant)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send message to AI tutor"""
        conversation = self.get_object()
        message_content = request.data.get('message', '').strip()
        context = request.data.get('context', {})
        
        if not message_content:
            return Response(
                {'error': 'Message content is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create AI service
            ai_service = AIServiceFactory.create_service_from_request(request)
            
            # Send message to AI tutor
            ai_response, metadata = ai_service.chat_with_tutor(
                str(conversation.id), message_content, context
            )
            
            return Response({
                'success': True,
                'ai_response': ai_response,
                'metadata': metadata
            })
            
        except QuotaExceededError as e:
            return Response(
                {'error': str(e), 'error_type': 'quota_exceeded'}, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        except RateLimitExceededError as e:
            return Response(
                {'error': str(e), 'error_type': 'rate_limit_exceeded'}, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        except AIServiceError as e:
            return Response(
                {'error': str(e), 'error_type': 'ai_service_error'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': 'An unexpected error occurred', 'error_type': 'internal_error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get conversation messages"""
        conversation = self.get_object()
        messages = conversation.messages.order_by('created_at')
        serializer = AIMessageSerializer(messages, many=True)
        return Response(serializer.data)


class AIContentSummaryViewSet(viewsets.ModelViewSet):
    """ViewSet for AI content summaries"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AIContentSummarySerializer
    
    def get_queryset(self):
        """Filter summaries by tenant and user"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return AIContentSummary.objects.filter(
                tenant=self.request.tenant,
                user=self.request.user
            )
        return AIContentSummary.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate content summary"""
        content = request.data.get('content', '').strip()
        content_type = request.data.get('content_type', 'text')
        content_id = request.data.get('content_id')
        content_title = request.data.get('content_title', 'Untitled Content')
        course_id = request.data.get('course_id')
        
        if not content:
            return Response(
                {'error': 'Content is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not content_id:
            content_id = str(uuid.uuid4())
        
        try:
            # Create AI service
            ai_service = AIServiceFactory.create_service_from_request(request)
            
            # Generate summary
            summary, key_points, metadata = ai_service.generate_content_summary(
                content, content_type, content_id, content_title, course_id
            )
            
            return Response({
                'success': True,
                'summary': summary,
                'key_points': key_points,
                'metadata': metadata
            })
            
        except QuotaExceededError as e:
            return Response(
                {'error': str(e), 'error_type': 'quota_exceeded'}, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        except RateLimitExceededError as e:
            return Response(
                {'error': str(e), 'error_type': 'rate_limit_exceeded'}, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        except AIServiceError as e:
            return Response(
                {'error': str(e), 'error_type': 'ai_service_error'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': 'An unexpected error occurred', 'error_type': 'internal_error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AIQuizViewSet(viewsets.ModelViewSet):
    """ViewSet for AI-generated quizzes"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AIQuizSerializer
    
    def get_queryset(self):
        """Filter quizzes by tenant and user"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return AIQuiz.objects.filter(
                tenant=self.request.tenant,
                user=self.request.user
            )
        return AIQuiz.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate quiz from content"""
        content = request.data.get('content', '').strip()
        course_id = request.data.get('course_id')
        title = request.data.get('title', 'AI Generated Quiz')
        num_questions = request.data.get('num_questions', 5)
        difficulty = request.data.get('difficulty', 'medium')
        
        if not content:
            return Response(
                {'error': 'Content is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not course_id:
            return Response(
                {'error': 'Course ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Validate num_questions
            num_questions = int(num_questions)
            if num_questions < 1 or num_questions > 20:
                return Response(
                    {'error': 'Number of questions must be between 1 and 20'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid number of questions'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create AI service
            ai_service = AIServiceFactory.create_service_from_request(request)
            
            # Generate quiz
            questions, metadata = ai_service.generate_quiz(
                content, course_id, title, num_questions, difficulty
            )
            
            return Response({
                'success': True,
                'questions': questions,
                'metadata': metadata
            })
            
        except QuotaExceededError as e:
            return Response(
                {'error': str(e), 'error_type': 'quota_exceeded'}, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        except RateLimitExceededError as e:
            return Response(
                {'error': str(e), 'error_type': 'rate_limit_exceeded'}, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        except AIServiceError as e:
            return Response(
                {'error': str(e), 'error_type': 'ai_service_error'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': 'An unexpected error occurred', 'error_type': 'internal_error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AIUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI usage tracking and statistics"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AIUsageQuotaSerializer
    
    def get_queryset(self):
        """Filter usage by tenant and user"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return AIUsageQuota.objects.filter(
                tenant=self.request.tenant,
                user=self.request.user
            )
        return AIUsageQuota.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current_stats(self, request):
        """Get current month usage statistics"""
        try:
            # Create AI service
            ai_service = AIServiceFactory.create_service_from_request(request)
            
            # Get usage stats
            stats = ai_service.get_usage_stats()
            
            return Response({
                'success': True,
                'stats': stats
            })
            
        except Exception as e:
            return Response(
                {'error': 'Failed to retrieve usage statistics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )