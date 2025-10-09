from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AIConversation, AIUsageQuota
from .providers import GeminiProvider


class AIConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for AI conversations"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter conversations by tenant and user"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return AIConversation.objects.filter(
                tenant=self.request.tenant,
                user=self.request.user
            )
        return AIConversation.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send message to AI conversation"""
        conversation = self.get_object()
        message_content = request.data.get('message')
        
        if not message_content:
            return Response({'error': 'Message content required'}, status=400)
        
        try:
            # Check usage quota
            quota = AIUsageQuota.objects.get_or_create(
                user=request.user,
                month=timezone.now().date().replace(day=1),
                tenant=request.tenant
            )[0]
            
            if quota.chat_messages_used >= quota.chat_messages_limit:
                return Response({'error': 'Chat message quota exceeded'}, status=429)
            
            # Add user message
            user_message = conversation.messages.create(
                role='user',
                content=message_content
            )
            
            # Generate AI response
            provider = GeminiProvider()
            messages = [{'role': msg.role, 'content': msg.content} 
                       for msg in conversation.messages.all()]
            
            ai_response = provider.generate_response(messages, conversation.context)
            
            # Add AI message
            ai_message = conversation.messages.create(
                role='assistant',
                content=ai_response
            )
            
            # Update usage
            quota.chat_messages_used += 1
            quota.save()
            
            return Response({
                'user_message': {'id': user_message.id, 'content': user_message.content},
                'ai_message': {'id': ai_message.id, 'content': ai_message.content}
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class AIUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI usage tracking"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter usage by tenant and user"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return AIUsageQuota.objects.filter(
                tenant=self.request.tenant,
                user=self.request.user
            )
        return AIUsageQuota.objects.filter(user=self.request.user)