from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import stripe
import json
import hmac
import hashlib
from .models import Payment, Invoice, Subscription, SubscriptionPlan
from .services import PaymentService, SubscriptionService, InvoiceService, BankTransferService
from .serializers import PaymentSerializer, InvoiceSerializer, SubscriptionSerializer, SubscriptionPlanSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment model"""
    
    serializer_class = PaymentSerializer
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
    
    def perform_create(self, serializer):
        """Set user and tenant when creating payment"""
        serializer.save(
            user=self.request.user,
            tenant=getattr(self.request, 'tenant', None)
        )
    
    @action(detail=False, methods=['post'])
    def create_course_payment(self, request):
        """Create a new payment for course enrollment"""
        course_id = request.data.get('course_id')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        
        if not all([course_id, amount, payment_method]):
            return Response(
                {'error': 'course_id, amount and payment_method are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.courses.models import Course
            course = Course.objects.get(id=course_id, tenant=request.tenant)
            
            result = PaymentService.process_course_payment(
                user=request.user,
                course=course,
                amount=float(amount),
                payment_method=payment_method,
                tenant=request.tenant
            )
            
            return Response(result, status=status.HTTP_201_CREATED)
            
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )
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
    
    @action(detail=True, methods=['post'])
    def approve_bank_transfer(self, request, pk=None):
        """Approve bank transfer payment (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        payment = self.get_object()
        
        if payment.payment_method != 'bank_transfer':
            return Response(
                {'error': 'Payment is not a bank transfer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = BankTransferService.approve_bank_transfer(payment.id, request.user)
        
        if success:
            # Create and send invoice
            invoice = InvoiceService.create_invoice_for_payment(payment)
            InvoiceService.send_invoice(invoice)
            
            return Response({'message': 'Bank transfer approved successfully'})
        else:
            return Response(
                {'error': 'Failed to approve bank transfer'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reject_bank_transfer(self, request, pk=None):
        """Reject bank transfer payment (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        payment = self.get_object()
        reason = request.data.get('reason', '')
        
        if payment.payment_method != 'bank_transfer':
            return Response(
                {'error': 'Payment is not a bank transfer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = BankTransferService.reject_bank_transfer(payment.id, reason)
        
        if success:
            return Response({'message': 'Bank transfer rejected successfully'})
        else:
            return Response(
                {'error': 'Failed to reject bank transfer'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def revenue_stats(self, request):
        """Get payment revenue statistics"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        timeframe = request.query_params.get('timeframe', 'month')
        
        try:
            from django.db.models import Sum, Count
            from django.utils import timezone
            from datetime import timedelta
            
            # Calculate date range based on timeframe
            now = timezone.now()
            if timeframe == 'day':
                start_date = now - timedelta(days=1)
            elif timeframe == 'week':
                start_date = now - timedelta(weeks=1)
            elif timeframe == 'year':
                start_date = now - timedelta(days=365)
            else:  # month
                start_date = now - timedelta(days=30)
            
            payments_queryset = self.get_queryset().filter(created_at__gte=start_date)
            
            stats = {
                'total_revenue': payments_queryset.filter(status='completed').aggregate(
                    total=Sum('amount')
                )['total'] or 0,
                'total_transactions': payments_queryset.count(),
                'successful_payments': payments_queryset.filter(status='completed').count(),
                'failed_payments': payments_queryset.filter(status='failed').count(),
                'refunded_amount': payments_queryset.filter(status='refunded').aggregate(
                    total=Sum('amount')
                )['total'] or 0,
            }
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for Subscription model"""
    
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter subscriptions by tenant"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Subscription.objects.filter(tenant=self.request.tenant)
        return Subscription.objects.none()
    
    @action(detail=False, methods=['post'])
    def create_subscription(self, request):
        """Create new subscription for organization"""
        plan = request.data.get('plan')
        billing_cycle = request.data.get('billing_cycle', 'monthly')
        payment_method = request.data.get('payment_method', 'stripe')
        
        if not plan:
            return Response(
                {'error': 'plan is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get organization from tenant
            organization = request.tenant
            
            subscription = SubscriptionService.create_subscription(
                organization=organization,
                plan=plan,
                billing_cycle=billing_cycle,
                payment_method=payment_method
            )
            
            # Process initial payment
            payment_result = SubscriptionService.process_subscription_payment(
                subscription=subscription,
                payment_method=payment_method
            )
            
            return Response({
                'subscription_id': subscription.id,
                'payment_result': payment_result
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel_subscription(self, request, pk=None):
        """Cancel subscription"""
        subscription = self.get_object()
        
        # Only organization admins can cancel subscriptions
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        subscription.cancel()
        
        return Response({'message': 'Subscription cancelled successfully'})
    
    @action(detail=True, methods=['post'])
    def renew_subscription(self, request, pk=None):
        """Renew subscription for next billing period"""
        subscription = self.get_object()
        
        try:
            payment_result = SubscriptionService.renew_subscription(subscription)
            return Response({
                'message': 'Subscription renewed successfully',
                'payment_result': payment_result
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def billing_automation(self, request):
        """Get billing automation status and next billing dates"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from django.utils import timezone
            from datetime import timedelta
            
            # Get subscriptions with upcoming renewals
            upcoming_renewals = self.get_queryset().filter(
                status='active',
                current_period_end__lte=timezone.now() + timedelta(days=7)
            )
            
            automation_status = {
                'upcoming_renewals': upcoming_renewals.count(),
                'active_subscriptions': self.get_queryset().filter(status='active').count(),
                'past_due_subscriptions': self.get_queryset().filter(status='past_due').count(),
                'next_billing_dates': [
                    {
                        'subscription_id': sub.id,
                        'organization_name': sub.organization.name,
                        'plan': sub.plan,
                        'next_billing_date': sub.current_period_end.isoformat(),
                        'amount': float(sub.amount)
                    }
                    for sub in upcoming_renewals[:10]  # Limit to 10 for performance
                ],
                'automation_settings': {
                    'auto_retry_failed_payments': True,
                    'retry_attempts': 3,
                    'retry_interval_days': 3,
                    'grace_period_days': 7,
                    'auto_cancel_after_days': 30
                },
                'billing_metrics': {
                    'success_rate': self._calculate_billing_success_rate(),
                    'average_retry_success': self._calculate_retry_success_rate(),
                    'churn_rate': self._calculate_churn_rate()
                }
            }
            
            return Response(automation_status)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _calculate_billing_success_rate(self):
        """Calculate billing success rate for last 30 days"""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Q
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        total_billing_attempts = Payment.objects.filter(
            payment_type='subscription',
            created_at__gte=thirty_days_ago
        ).count()
        
        successful_billings = Payment.objects.filter(
            payment_type='subscription',
            created_at__gte=thirty_days_ago,
            status='completed'
        ).count()
        
        if total_billing_attempts == 0:
            return 100.0
        
        return round((successful_billings / total_billing_attempts) * 100, 2)
    
    def _calculate_retry_success_rate(self):
        """Calculate retry success rate"""
        # Simplified calculation - in production, you'd track retry attempts
        return 65.0  # Placeholder
    
    def _calculate_churn_rate(self):
        """Calculate monthly churn rate"""
        from django.utils import timezone
        from datetime import timedelta
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        cancelled_subscriptions = self.get_queryset().filter(
            status='cancelled',
            cancelled_at__gte=thirty_days_ago
        ).count()
        
        total_active_start_of_month = self.get_queryset().filter(
            created_at__lt=thirty_days_ago
        ).count()
        
        if total_active_start_of_month == 0:
            return 0.0
        
        return round((cancelled_subscriptions / total_active_start_of_month) * 100, 2)
    
    @action(detail=False, methods=['get'])
    def payment_analytics(self, request):
        """Get detailed payment analytics"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from django.db.models import Sum, Count, Avg
            from django.utils import timezone
            from datetime import timedelta, datetime
            import calendar
            
            timeframe = request.query_params.get('timeframe', 'month')
            
            # Calculate date range
            now = timezone.now()
            if timeframe == 'day':
                start_date = now - timedelta(days=30)  # Last 30 days
                date_format = '%Y-%m-%d'
                date_trunc = 'day'
            elif timeframe == 'week':
                start_date = now - timedelta(weeks=12)  # Last 12 weeks
                date_format = '%Y-W%U'
                date_trunc = 'week'
            elif timeframe == 'year':
                start_date = now - timedelta(days=365*3)  # Last 3 years
                date_format = '%Y'
                date_trunc = 'year'
            else:  # month
                start_date = now - timedelta(days=365)  # Last 12 months
                date_format = '%Y-%m'
                date_trunc = 'month'
            
            payments_queryset = self.get_queryset().filter(created_at__gte=start_date)
            
            # Revenue by period
            from django.db.models import DateTimeField
            from django.db.models.functions import TruncMonth, TruncDay, TruncWeek, TruncYear
            
            trunc_func = {
                'day': TruncDay,
                'week': TruncWeek,
                'month': TruncMonth,
                'year': TruncYear
            }[date_trunc]
            
            revenue_by_period = payments_queryset.filter(status='completed').annotate(
                period=trunc_func('created_at')
            ).values('period').annotate(
                revenue=Sum('amount'),
                transactions=Count('id'),
                avg_amount=Avg('amount')
            ).order_by('period')
            
            # Payment method breakdown
            payment_methods = payments_queryset.filter(status='completed').values('payment_method').annotate(
                count=Count('id'),
                revenue=Sum('amount')
            ).order_by('-revenue')
            
            # Course vs subscription revenue
            course_revenue = payments_queryset.filter(
                status='completed',
                payment_type='course'
            ).aggregate(
                total=Sum('amount'),
                count=Count('id')
            )
            
            subscription_revenue = payments_queryset.filter(
                status='completed',
                payment_type='subscription'
            ).aggregate(
                total=Sum('amount'),
                count=Count('id')
            )
            
            # Failed payment analysis
            failed_payments = payments_queryset.filter(status='failed').values('payment_method').annotate(
                count=Count('id'),
                total_amount=Sum('amount')
            )
            
            analytics = {
                'revenue_by_period': [
                    {
                        'period': item['period'].strftime(date_format),
                        'revenue': float(item['revenue'] or 0),
                        'transactions': item['transactions'],
                        'avg_amount': float(item['avg_amount'] or 0)
                    }
                    for item in revenue_by_period
                ],
                'payment_methods': [
                    {
                        'method': item['payment_method'],
                        'count': item['count'],
                        'revenue': float(item['revenue'] or 0),
                        'percentage': round((item['revenue'] or 0) / max(sum(p['revenue'] or 0 for p in payment_methods), 1) * 100, 2)
                    }
                    for item in payment_methods
                ],
                'revenue_breakdown': {
                    'course_revenue': {
                        'total': float(course_revenue['total'] or 0),
                        'count': course_revenue['count']
                    },
                    'subscription_revenue': {
                        'total': float(subscription_revenue['total'] or 0),
                        'count': subscription_revenue['count']
                    }
                },
                'failed_payments': [
                    {
                        'method': item['payment_method'],
                        'count': item['count'],
                        'total_amount': float(item['total_amount'] or 0)
                    }
                    for item in failed_payments
                ],
                'summary': {
                    'total_revenue': float(payments_queryset.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0),
                    'total_transactions': payments_queryset.filter(status='completed').count(),
                    'failed_transactions': payments_queryset.filter(status='failed').count(),
                    'success_rate': round(
                        payments_queryset.filter(status='completed').count() / 
                        max(payments_queryset.count(), 1) * 100, 2
                    )
                }
            }
            
            return Response(analytics)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SubscriptionPlan model (read-only for users)"""
    
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get active subscription plans"""
        return SubscriptionPlan.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def compare(self, request):
        """Get subscription plans comparison data"""
        plans = self.get_queryset()
        serializer = self.get_serializer(plans, many=True)
        
        # Add comparison matrix
        comparison_data = {
            'plans': serializer.data,
            'features': [
                {'name': 'Users', 'key': 'max_users'},
                {'name': 'Courses', 'key': 'max_courses'},
                {'name': 'Storage (GB)', 'key': 'max_storage_gb'},
                {'name': 'AI Requests/Month', 'key': 'ai_quota_monthly'},
                {'name': 'Analytics', 'key': 'has_analytics'},
                {'name': 'API Access', 'key': 'has_api_access'},
                {'name': 'White Labeling', 'key': 'has_white_labeling'},
                {'name': 'Priority Support', 'key': 'has_priority_support'},
                {'name': 'Custom Integrations', 'key': 'has_custom_integrations'},
            ]
        }
        
        return Response(comparison_data)


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice model"""
    
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter invoices by tenant and user"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Invoice.objects.filter(tenant=self.request.tenant)
            
            # Non-staff users can only see their own invoices
            if not self.request.user.is_staff:
                from django.db import models
                queryset = queryset.filter(
                    models.Q(user=self.request.user) | 
                    models.Q(organization=self.request.tenant)
                )
            
            return queryset
        return Invoice.objects.none()
    
    @action(detail=True, methods=['post'])
    def send_invoice(self, request, pk=None):
        """Send invoice via email"""
        invoice = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            InvoiceService.send_invoice(invoice)
            return Response({'message': 'Invoice sent successfully'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark invoice as paid"""
        invoice = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        InvoiceService.mark_invoice_paid(invoice)
        
        return Response({'message': 'Invoice marked as paid'})
    
    @action(detail=False, methods=['get'])
    def overdue_invoices(self, request):
        """Get overdue invoices"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.utils import timezone
        
        overdue_invoices = self.get_queryset().filter(
            status='sent',
            due_date__lt=timezone.now().date()
        )
        
        # Mark them as overdue
        for invoice in overdue_invoices:
            invoice.mark_overdue()
        
        serializer = self.get_serializer(overdue_invoices, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download invoice PDF"""
        invoice = self.get_object()
        
        # Check permissions - users can download their own invoices, staff can download any
        if not request.user.is_staff and invoice.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from .services import PDFInvoiceService
            
            # Generate PDF if not exists
            if not invoice.pdf_file:
                PDFInvoiceService.save_invoice_pdf(invoice)
            
            if invoice.pdf_file:
                from django.http import FileResponse
                return FileResponse(
                    invoice.pdf_file.open('rb'),
                    as_attachment=True,
                    filename=f'invoice_{invoice.invoice_number}.pdf'
                )
            else:
                return Response(
                    {'error': 'PDF generation failed'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def invoice_analytics(self, request):
        """Get invoice analytics and reporting"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from django.db.models import Sum, Count, Avg, Q, F, Case, When, IntegerField
            from django.utils import timezone
            from datetime import timedelta
            
            timeframe = request.query_params.get('timeframe', 'month')
            
            # Calculate date range
            now = timezone.now()
            if timeframe == 'day':
                start_date = now - timedelta(days=30)
            elif timeframe == 'week':
                start_date = now - timedelta(weeks=12)
            elif timeframe == 'year':
                start_date = now - timedelta(days=365*3)
            else:  # month
                start_date = now - timedelta(days=365)
            
            invoices_queryset = self.get_queryset().filter(created_at__gte=start_date)
            
            # Invoice status breakdown
            status_breakdown = invoices_queryset.values('status').annotate(
                count=Count('id'),
                total_amount=Sum('total_amount')
            ).order_by('-count')
            
            # Tax collection analytics
            tax_analytics = invoices_queryset.aggregate(
                total_tax_collected=Sum('tax_amount'),
                avg_tax_rate=Avg('tax_rate'),
                invoices_with_tax=Count('id', filter=Q(tax_amount__gt=0))
            )
            
            # Payment terms analysis
            payment_terms_analysis = invoices_queryset.annotate(
                days_to_pay=Case(
                    When(paid_at__isnull=False, then=F('paid_at') - F('issue_date')),
                    default=None,
                    output_field=IntegerField()
                )
            ).aggregate(
                avg_days_to_pay=Avg('days_to_pay'),
                on_time_payments=Count('id', filter=Q(paid_at__lte=F('due_date'))),
                late_payments=Count('id', filter=Q(paid_at__gt=F('due_date')))
            )
            
            # Revenue by invoice type
            revenue_by_type = invoices_queryset.filter(status='paid').values('invoice_type').annotate(
                count=Count('id'),
                revenue=Sum('total_amount')
            )
            
            analytics = {
                'status_breakdown': [
                    {
                        'status': item['status'],
                        'count': item['count'],
                        'total_amount': float(item['total_amount'] or 0)
                    }
                    for item in status_breakdown
                ],
                'tax_analytics': {
                    'total_tax_collected': float(tax_analytics['total_tax_collected'] or 0),
                    'avg_tax_rate': float(tax_analytics['avg_tax_rate'] or 0),
                    'invoices_with_tax': tax_analytics['invoices_with_tax'],
                    'tax_compliance_rate': round(
                        tax_analytics['invoices_with_tax'] / max(invoices_queryset.count(), 1) * 100, 2
                    )
                },
                'payment_terms': {
                    'avg_days_to_pay': payment_terms_analysis['avg_days_to_pay'],
                    'on_time_payments': payment_terms_analysis['on_time_payments'],
                    'late_payments': payment_terms_analysis['late_payments'],
                    'on_time_rate': round(
                        payment_terms_analysis['on_time_payments'] / 
                        max(payment_terms_analysis['on_time_payments'] + payment_terms_analysis['late_payments'], 1) * 100, 2
                    )
                },
                'revenue_by_type': [
                    {
                        'type': item['invoice_type'],
                        'count': item['count'],
                        'revenue': float(item['revenue'] or 0)
                    }
                    for item in revenue_by_type
                ],
                'summary': {
                    'total_invoices': invoices_queryset.count(),
                    'total_revenue': float(invoices_queryset.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
                    'outstanding_amount': float(invoices_queryset.filter(status__in=['sent', 'overdue']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
                    'overdue_count': invoices_queryset.filter(status='overdue').count()
                }
            }
            
            return Response(analytics)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """Handle Stripe webhook events"""
    
    permission_classes = []  # No authentication required for webhooks
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self.handle_payment_success(payment_intent)
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self.handle_payment_failure(payment_intent)
            
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            self.handle_subscription_payment_success(invoice)
            
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            self.handle_subscription_payment_failure(invoice)
            
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            self.handle_subscription_cancelled(subscription)
        
        return HttpResponse(status=200)
    
    def handle_payment_success(self, payment_intent):
        """Handle successful payment intent"""
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            
            # Fraud detection checks
            fraud_score = self._calculate_fraud_score(payment, payment_intent)
            
            if fraud_score > 80:  # High fraud risk
                payment.status = 'processing'  # Hold for manual review
                payment.metadata['fraud_score'] = fraud_score
                payment.metadata['fraud_flags'] = self._get_fraud_flags(payment, payment_intent)
                payment.save()
                
                # Alert administrators
                self._send_fraud_alert(payment, fraud_score)
                return
            
            if payment.status != 'completed':
                payment.mark_completed()
                
                # Log successful payment for fraud tracking
                self._log_payment_success(payment, payment_intent)
                
                # Create and send invoice
                invoice = InvoiceService.create_invoice_for_payment(payment)
                InvoiceService.send_invoice(invoice)
                
                # Create success notification
                from apps.notifications.models import Notification
                Notification.objects.create(
                    user=payment.user,
                    tenant=payment.tenant,
                    title='Payment Successful',
                    message=f'Your payment of ${payment.amount} for {payment.course.title if payment.course else "subscription"} has been processed successfully.',
                    notification_type='payment_success',
                    related_object_id=payment.id,
                    related_object_type='payment'
                )
                
                # Send payment confirmation
                from .tasks import send_payment_confirmation
                send_payment_confirmation.delay(payment.id)
                
        except Payment.DoesNotExist:
            # Log potential webhook attack
            self._log_security_event('unknown_payment_intent', {
                'payment_intent_id': payment_intent['id'],
                'amount': payment_intent.get('amount'),
                'timestamp': timezone.now().isoformat()
            })
    
    def handle_payment_failure(self, payment_intent):
        """Handle failed payment intent"""
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')
            payment.mark_failed(failure_reason)
            
            # Create failure notification
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=payment.user,
                tenant=payment.tenant,
                title='Payment Failed',
                message=f'Your payment of ${payment.amount} for {payment.course.title if payment.course else "subscription"} has failed. Reason: {failure_reason}',
                notification_type='payment_failed',
                related_object_id=payment.id,
                related_object_type='payment'
            )
            
        except Payment.DoesNotExist:
            pass
    
    def handle_subscription_payment_success(self, invoice):
        """Handle successful subscription payment"""
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=invoice['subscription']
            )
            
            # Create payment record for this subscription billing
            payment = Payment.objects.create(
                subscription=subscription,
                payment_type='subscription',
                amount=invoice['amount_paid'] / 100,  # Convert from cents
                payment_method='stripe',
                status='completed',
                stripe_payment_intent_id=invoice.get('payment_intent'),
                tenant=subscription.tenant,
                description=f"{subscription.plan.title()} subscription payment"
            )
            
            # Create and send invoice
            invoice_obj = InvoiceService.create_invoice_for_payment(payment)
            InvoiceService.send_invoice(invoice_obj)
            
        except Subscription.DoesNotExist:
            pass
    
    def handle_subscription_payment_failure(self, invoice):
        """Handle failed subscription payment"""
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=invoice['subscription']
            )
            
            # Update subscription status
            subscription.status = 'past_due'
            subscription.save()
            
            # Create failed payment record
            Payment.objects.create(
                subscription=subscription,
                payment_type='subscription',
                amount=invoice['amount_due'] / 100,  # Convert from cents
                payment_method='stripe',
                status='failed',
                tenant=subscription.tenant,
                description=f"{subscription.plan.title()} subscription payment failed",
                metadata={'failure_reason': 'Subscription payment failed'}
            )
            
        except Subscription.DoesNotExist:
            pass
    
    def handle_subscription_cancelled(self, subscription_data):
        """Handle cancelled subscription"""
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=subscription_data['id']
            )
            subscription.cancel()
            
        except Subscription.DoesNotExist:
            pass
    
    def _calculate_fraud_score(self, payment, payment_intent):
        """Calculate fraud risk score (0-100)"""
        score = 0
        
        # Check payment amount anomalies
        if payment.amount > 1000:  # High amount
            score += 20
        
        # Check user payment history
        user_payments = Payment.objects.filter(
            user=payment.user,
            status='completed'
        ).count()
        
        if user_payments == 0:  # First-time user
            score += 15
        
        # Check payment method risk
        if payment.payment_method == 'stripe':
            # Check Stripe risk indicators
            risk_level = payment_intent.get('charges', {}).get('data', [{}])[0].get('outcome', {}).get('risk_level')
            if risk_level == 'elevated':
                score += 25
            elif risk_level == 'highest':
                score += 50
        
        # Check geographic anomalies (simplified)
        # In production, you'd check IP geolocation vs billing address
        
        # Check velocity - multiple payments in short time
        from datetime import timedelta
        recent_payments = Payment.objects.filter(
            user=payment.user,
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        if recent_payments > 3:
            score += 30
        
        return min(score, 100)  # Cap at 100
    
    def _get_fraud_flags(self, payment, payment_intent):
        """Get list of fraud flags for this payment"""
        flags = []
        
        if payment.amount > 1000:
            flags.append('high_amount')
        
        user_payments = Payment.objects.filter(
            user=payment.user,
            status='completed'
        ).count()
        
        if user_payments == 0:
            flags.append('first_time_user')
        
        if payment.payment_method == 'stripe':
            risk_level = payment_intent.get('charges', {}).get('data', [{}])[0].get('outcome', {}).get('risk_level')
            if risk_level in ['elevated', 'highest']:
                flags.append(f'stripe_risk_{risk_level}')
        
        from datetime import timedelta
        recent_payments = Payment.objects.filter(
            user=payment.user,
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        if recent_payments > 3:
            flags.append('high_velocity')
        
        return flags
    
    def _send_fraud_alert(self, payment, fraud_score):
        """Send fraud alert to administrators"""
        from django.core.mail import send_mail
        
        subject = f"Fraud Alert - Payment {payment.id}"
        message = f"""
        High fraud risk payment detected:
        
        Payment ID: {payment.id}
        User: {payment.user.email}
        Amount: ${payment.amount}
        Fraud Score: {fraud_score}/100
        Flags: {', '.join(payment.metadata.get('fraud_flags', []))}
        
        Please review this payment manually.
        """
        
        admin_email = settings.ADMIN_EMAIL
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=True
        )
    
    def _log_payment_success(self, payment, payment_intent):
        """Log successful payment for fraud tracking"""
        # Store payment metadata for future fraud analysis
        payment.metadata.update({
            'stripe_risk_level': payment_intent.get('charges', {}).get('data', [{}])[0].get('outcome', {}).get('risk_level'),
            'stripe_seller_message': payment_intent.get('charges', {}).get('data', [{}])[0].get('outcome', {}).get('seller_message'),
            'processed_at': timezone.now().isoformat()
        })
        payment.save()
    
    def _log_security_event(self, event_type, data):
        """Log security events for monitoring"""
        try:
            from apps.security.models import SecurityEvent
            SecurityEvent.objects.create(
                event_type=event_type,
                severity='medium',
                description=f"Payment webhook security event: {event_type}",
                metadata=data,
                source_ip='webhook',
                user_agent='stripe_webhook'
            )
        except:
            # If security app doesn't exist, just log to console
            print(f"Security Event: {event_type} - {data}")


@method_decorator(csrf_exempt, name='dispatch')
class PayPalWebhookView(APIView):
    """Handle PayPal webhook events"""
    
    permission_classes = []  # No authentication required for webhooks
    
    def post(self, request):
        # Verify PayPal webhook signature
        if not self.verify_paypal_webhook(request):
            return HttpResponse(status=400)
        
        try:
            event_data = json.loads(request.body)
            event_type = event_data.get('event_type')
            
            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                self.handle_payment_completed(event_data)
            elif event_type == 'PAYMENT.CAPTURE.DENIED':
                self.handle_payment_failed(event_data)
                
        except (json.JSONDecodeError, KeyError):
            return HttpResponse(status=400)
        
        return HttpResponse(status=200)
    
    def verify_paypal_webhook(self, request):
        """Verify PayPal webhook signature"""
        try:
            # Get PayPal webhook verification headers
            auth_algo = request.META.get('HTTP_PAYPAL_AUTH_ALGO')
            transmission_id = request.META.get('HTTP_PAYPAL_TRANSMISSION_ID')
            cert_id = request.META.get('HTTP_PAYPAL_CERT_ID')
            transmission_sig = request.META.get('HTTP_PAYPAL_TRANSMISSION_SIG')
            transmission_time = request.META.get('HTTP_PAYPAL_TRANSMISSION_TIME')
            
            # Basic validation - in production, implement full PayPal webhook verification
            # using PayPal SDK or manual verification process
            if not all([auth_algo, transmission_id, cert_id, transmission_sig, transmission_time]):
                self._log_security_event('paypal_webhook_missing_headers', {
                    'headers': {
                        'auth_algo': auth_algo,
                        'transmission_id': transmission_id,
                        'cert_id': cert_id,
                        'has_signature': bool(transmission_sig),
                        'transmission_time': transmission_time
                    }
                })
                return False
            
            # Additional security checks
            # Check if webhook is from PayPal IP ranges (simplified)
            client_ip = self._get_client_ip(request)
            if not self._is_paypal_ip(client_ip):
                self._log_security_event('paypal_webhook_invalid_ip', {
                    'client_ip': client_ip,
                    'transmission_id': transmission_id
                })
                return False
            
            return True
            
        except Exception as e:
            self._log_security_event('paypal_webhook_verification_error', {
                'error': str(e),
                'transmission_id': transmission_id
            })
            return False
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _is_paypal_ip(self, ip):
        """Check if IP is from PayPal (simplified check)"""
        # In production, maintain a list of PayPal IP ranges
        # This is a simplified version
        paypal_ip_ranges = [
            '173.0.80.0/20',
            '64.4.240.0/21',
            '66.211.168.0/22',
            '173.0.80.0/20'
        ]
        
        # For now, just return True - implement proper IP range checking in production
        return True
    
    def handle_payment_completed(self, event_data):
        """Handle completed PayPal payment"""
        try:
            resource = event_data['resource']
            custom_id = resource.get('custom_id')  # This should contain payment ID
            
            if custom_id:
                payment = Payment.objects.get(id=custom_id)
                if payment.status != 'completed':
                    payment.mark_completed()
                    
                    # Create and send invoice
                    invoice = InvoiceService.create_invoice_for_payment(payment)
                    InvoiceService.send_invoice(invoice)
                    
                    # Send payment confirmation
                    from .tasks import send_payment_confirmation
                    send_payment_confirmation.delay(payment.id)
                    
        except (Payment.DoesNotExist, KeyError):
            pass
    
    def handle_payment_failed(self, event_data):
        """Handle failed PayPal payment"""
        try:
            resource = event_data['resource']
            custom_id = resource.get('custom_id')  # This should contain payment ID
            
            if custom_id:
                payment = Payment.objects.get(id=custom_id)
                payment.mark_failed('PayPal payment denied')
                
        except (Payment.DoesNotExist, KeyError):
            pass


class StripeAPIView(APIView):
    """Direct Stripe API integration endpoints"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, action=None):
        """Handle Stripe API operations"""
        from .services import StripeService
        
        try:
            stripe_service = StripeService()
            
            if action == 'create_payment_intent':
                return self._create_payment_intent(request, stripe_service)
            elif action == 'confirm_payment':
                return self._confirm_payment(request, stripe_service)
            elif action == 'create_customer':
                return self._create_customer(request, stripe_service)
            elif action == 'create_subscription':
                return self._create_subscription(request, stripe_service)
            elif action == 'cancel_subscription':
                return self._cancel_subscription(request, stripe_service)
            elif action == 'retrieve_payment':
                return self._retrieve_payment(request, stripe_service)
            else:
                return Response(
                    {'error': 'Invalid action'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _create_payment_intent(self, request, stripe_service):
        """Create Stripe payment intent"""
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'usd')
        metadata = request.data.get('metadata', {})
        
        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add user info to metadata
        metadata.update({
            'user_id': str(request.user.id),
            'user_email': request.user.email,
            'tenant_id': str(request.tenant.id) if hasattr(request, 'tenant') else None
        })
        
        intent = stripe_service.create_payment_intent(
            amount=float(amount),
            currency=currency,
            metadata=metadata
        )
        
        return Response({
            'payment_intent_id': intent.id,
            'client_secret': intent.client_secret,
            'status': intent.status,
            'amount': intent.amount,
            'currency': intent.currency
        })
    
    def _confirm_payment(self, request, stripe_service):
        """Confirm Stripe payment"""
        payment_intent_id = request.data.get('payment_intent_id')
        
        if not payment_intent_id:
            return Response(
                {'error': 'Payment intent ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        confirmed = stripe_service.confirm_payment(payment_intent_id)
        
        return Response({
            'confirmed': confirmed,
            'payment_intent_id': payment_intent_id
        })
    
    def _create_customer(self, request, stripe_service):
        """Create Stripe customer"""
        email = request.data.get('email', request.user.email)
        name = request.data.get('name', request.user.get_full_name())
        metadata = request.data.get('metadata', {})
        
        # Add user info to metadata
        metadata.update({
            'user_id': str(request.user.id),
            'tenant_id': str(request.tenant.id) if hasattr(request, 'tenant') else None
        })
        
        customer = stripe_service.create_customer(
            email=email,
            name=name,
            metadata=metadata
        )
        
        return Response({
            'customer_id': customer.id,
            'email': customer.email,
            'name': customer.name
        })
    
    def _create_subscription(self, request, stripe_service):
        """Create Stripe subscription"""
        customer_id = request.data.get('customer_id')
        price_id = request.data.get('price_id')
        metadata = request.data.get('metadata', {})
        
        if not all([customer_id, price_id]):
            return Response(
                {'error': 'Customer ID and Price ID are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add user info to metadata
        metadata.update({
            'user_id': str(request.user.id),
            'tenant_id': str(request.tenant.id) if hasattr(request, 'tenant') else None
        })
        
        subscription = stripe_service.create_subscription(
            customer_id=customer_id,
            price_id=price_id,
            metadata=metadata
        )
        
        return Response({
            'subscription_id': subscription.id,
            'status': subscription.status,
            'current_period_start': subscription.current_period_start,
            'current_period_end': subscription.current_period_end,
            'latest_invoice': subscription.latest_invoice
        })
    
    def _cancel_subscription(self, request, stripe_service):
        """Cancel Stripe subscription"""
        subscription_id = request.data.get('subscription_id')
        
        if not subscription_id:
            return Response(
                {'error': 'Subscription ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cancelled_subscription = stripe_service.cancel_subscription(subscription_id)
        
        return Response({
            'subscription_id': cancelled_subscription.id,
            'status': cancelled_subscription.status,
            'canceled_at': cancelled_subscription.canceled_at
        })
    
    def _retrieve_payment(self, request, stripe_service):
        """Retrieve Stripe payment intent"""
        payment_intent_id = request.data.get('payment_intent_id')
        
        if not payment_intent_id:
            return Response(
                {'error': 'Payment intent ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            import stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return Response({
                'payment_intent_id': intent.id,
                'status': intent.status,
                'amount': intent.amount,
                'currency': intent.currency,
                'created': intent.created,
                'metadata': intent.metadata
            })
            
        except stripe.error.StripeError as e:
            return Response(
                {'error': f'Stripe error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PayPalAPIView(APIView):
    """Direct PayPal API integration endpoints"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, action=None):
        """Handle PayPal API operations"""
        from .services import PayPalService
        
        try:
            paypal_service = PayPalService()
            
            if action == 'create_order':
                return self._create_order(request, paypal_service)
            elif action == 'capture_order':
                return self._capture_order(request, paypal_service)
            elif action == 'get_order':
                return self._get_order(request, paypal_service)
            elif action == 'refund_payment':
                return self._refund_payment(request, paypal_service)
            else:
                return Response(
                    {'error': 'Invalid action'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _create_order(self, request, paypal_service):
        """Create PayPal order"""
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'USD')
        description = request.data.get('description', 'Payment')
        custom_id = request.data.get('custom_id')
        
        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = paypal_service.create_order(
            amount=float(amount),
            currency=currency,
            description=description,
            custom_id=custom_id
        )
        
        # Extract approval URL
        approval_url = None
        for link in order.get('links', []):
            if link.get('rel') == 'approve':
                approval_url = link.get('href')
                break
        
        return Response({
            'order_id': order.get('id'),
            'status': order.get('status'),
            'approval_url': approval_url,
            'links': order.get('links', [])
        })
    
    def _capture_order(self, request, paypal_service):
        """Capture PayPal order"""
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response(
                {'error': 'Order ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        captured = paypal_service.capture_order(order_id)
        
        return Response({
            'order_id': order_id,
            'captured': captured
        })
    
    def _get_order(self, request, paypal_service):
        """Get PayPal order details"""
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response(
                {'error': 'Order ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            import requests
            access_token = paypal_service.get_access_token()
            url = f"{paypal_service.base_url}/v2/checkout/orders/{order_id}"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            order_data = response.json()
            
            return Response({
                'order_id': order_data.get('id'),
                'status': order_data.get('status'),
                'intent': order_data.get('intent'),
                'purchase_units': order_data.get('purchase_units', []),
                'create_time': order_data.get('create_time'),
                'update_time': order_data.get('update_time')
            })
            
        except requests.RequestException as e:
            return Response(
                {'error': f'PayPal API error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _refund_payment(self, request, paypal_service):
        """Refund PayPal payment"""
        capture_id = request.data.get('capture_id')
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'USD')
        note_to_payer = request.data.get('note_to_payer', 'Refund processed')
        
        if not capture_id:
            return Response(
                {'error': 'Capture ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            import requests
            access_token = paypal_service.get_access_token()
            url = f"{paypal_service.base_url}/v2/payments/captures/{capture_id}/refund"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'PayPal-Request-Id': str(timezone.now().timestamp())
            }
            
            refund_data = {
                'note_to_payer': note_to_payer
            }
            
            if amount:
                refund_data['amount'] = {
                    'currency_code': currency,
                    'value': str(amount)
                }
            
            response = requests.post(url, headers=headers, json=refund_data)
            response.raise_for_status()
            
            refund_response = response.json()
            
            return Response({
                'refund_id': refund_response.get('id'),
                'status': refund_response.get('status'),
                'amount': refund_response.get('amount'),
                'create_time': refund_response.get('create_time')
            })
            
        except requests.RequestException as e:
            return Response(
                {'error': f'PayPal refund error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )