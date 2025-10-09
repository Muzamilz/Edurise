from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notification model"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter notifications by tenant and user"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Notification.objects.filter(
                tenant=self.request.tenant,
                user=self.request.user
            )
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        notifications = self.get_queryset().filter(is_read=False)
        for notification in notifications:
            notification.mark_as_read()
        
        return Response({'message': f'{notifications.count()} notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})