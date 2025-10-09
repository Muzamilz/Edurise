from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Payment, Invoice
from .services import PaymentService


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment model"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter payments by tenant and user"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Payment.objects.filter(tenant=self.request.tenant)
            
            # Non-staff users can only see their own payments
            if not self.request.user.is_staff:
                queryset = queryset.filter(user=self.request.user)
            
            return queryset
        return Payment.objects.none()
    
    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        """Create a new payment"""
        course_id = request.data.get('course_id')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        
        if not all([amount, payment_method]):
            return Response(
                {'error': 'amount and payment_method are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            course = None
            if course_id:
                from apps.courses.models import Course
                course = Course.objects.get(id=course_id, tenant=request.tenant)
            
            result = PaymentService.process_payment(
                user=request.user,
                course=course,
                amount=float(amount),
                payment_method=payment_method,
                tenant=request.tenant
            )
            
            return Response(result, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """Confirm payment completion"""
        payment = self.get_object()
        
        if payment.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        success = PaymentService.confirm_payment(payment.id)
        
        if success:
            return Response({'message': 'Payment confirmed successfully'})
        else:
            return Response(
                {'error': 'Failed to confirm payment'},
                status=status.HTTP_400_BAD_REQUEST
            )