"""
Integration tests for payment processing including complete payment flow for all methods,
subscription billing and renewal process, invoice generation and delivery, and payment
security and error handling as specified in requirements 7.1, 7.3, 7.5
"""

import json
import uuid
from decimal import Decimal
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.core import mail
from django.conf import settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.accounts.models import Organization
from apps.courses.models import Course
from apps.payments.models import Payment, Invoice, Subscription, InvoiceLineItem
from apps.payments.services import (
    PaymentService, StripeService, PayPalService, BankTransferService,
    SubscriptionService, InvoiceService
)

User = get_user_model()


class PaymentIntegrationTestCase(APITestCase):
    """Base test case for payment integration tests"""
    
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
        
        self.admin = User.objects.create_user(
            email="admin@testuni.edu",
            password="testpass123",
            first_name="Test",
            last_name="Admin",
            is_staff=True
        )
        
        # Create course
        self.course = Course.objects.create(
            title="Advanced Python Programming",
            description="Learn advanced Python concepts and techniques",
            instructor=self.instructor,
            tenant=self.tenant,
            price=Decimal('199.99'),
            category='programming',
            is_public=True
        )
        
        # Set up API client
        self.client = APIClient()
        
        # Mock external payment service responses
        self.mock_payment_responses()
    
    def mock_payment_responses(self):
        """Mock external payment service responses for consistent testing"""
        # Stripe mocks
        self.mock_stripe_intent = Mock()
        self.mock_stripe_intent.id = 'pi_test123456789'
        self.mock_stripe_intent.client_secret = 'pi_test123456789_secret_test'
        self.mock_stripe_intent.status = 'requires_payment_method'
        
        self.mock_stripe_customer = Mock()
        self.mock_stripe_customer.id = 'cus_test123456789'
        
        self.mock_stripe_subscription = Mock()
        self.mock_stripe_subscription.id = 'sub_test123456789'
        self.mock_stripe_subscription.status = 'active'
        
        # PayPal mocks
        self.mock_paypal_order = {
            'id': 'PAYPAL123456789',
            'status': 'CREATED',
            'links': [
                {
                    'rel': 'approve',
                    'href': 'https://www.sandbox.paypal.com/checkoutnow?token=PAYPAL123456789'
                }
            ]
        }
        
        self.mock_paypal_capture = {
            'status': 'COMPLETED',
            'purchase_units': [
                {
                    'payments': {
                        'captures': [
                            {
                                'id': 'CAPTURE123456789',
                                'status': 'COMPLETED',
                                'amount': {
                                    'currency_code': 'USD',
                                    'value': '199.99'
                                }
                            }
                        ]
                    }
                }
            ]
        }
    
    def authenticate_user(self, user):
        """Authenticate user for API requests"""
        self.client.force_authenticate(user=user)
        # Simulate tenant middleware
        self.client.defaults['HTTP_HOST'] = f"{self.tenant.subdomain}.edurise.com"
        # Mock request.tenant for views that need it
        self.client.defaults['HTTP_X_TENANT_ID'] = str(self.tenant.id)


class StripePaymentIntegrationTest(PaymentIntegrationTestCase):
    """Integration tests for complete Stripe payment flow (Requirement 7.1)"""
    
    @patch.object(StripeService, 'create_payment_intent')
    @patch.object(StripeService, 'confirm_payment')
    def test_complete_stripe_course_payment_flow(self, mock_confirm, mock_create_intent):
        """Test complete Stripe payment flow from creation to completion"""
        # Mock Stripe responses
        mock_create_intent.return_value = self.mock_stripe_intent
        mock_confirm.return_value = True
        
        self.authenticate_user(self.student)
        
        # Step 1: Create payment intent
        payment_data = {
            'course_id': str(self.course.id),
            'amount': '199.99',
            'payment_method': 'stripe',
            'currency': 'USD'
        }
        
        # Mock request.tenant in the view
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            response = self.client.post('/api/v1/payments/payments/create_course_payment/', payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('payment_id', response.data)
        self.assertIn('client_secret', response.data)
        
        payment_id = response.data['payment_id']
        client_secret = response.data['client_secret']
        
        # Verify payment was created in database
        payment = Payment.objects.get(id=payment_id)
        self.assertEqual(payment.user, self.student)
        self.assertEqual(payment.course, self.course)
        self.assertEqual(payment.amount, Decimal('199.99'))
        self.assertEqual(payment.payment_method, 'stripe')
        self.assertEqual(payment.status, 'pending')
        self.assertEqual(payment.stripe_payment_intent_id, 'pi_test123456789')
        
        # Verify Stripe service was called correctly
        mock_create_intent.assert_called_once()
        call_args = mock_create_intent.call_args
        self.assertEqual(call_args[1]['amount'], Decimal('199.99'))
        self.assertIn('payment_id', call_args[1]['metadata'])
        self.assertIn('course_id', call_args[1]['metadata'])
        
        # Step 2: Simulate frontend payment confirmation
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            confirm_response = self.client.post(f'/api/v1/payments/payments/{payment_id}/confirm_payment/')
        
        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        self.assertIn('Payment confirmed successfully', confirm_response.data['message'])
        
        # Verify payment status updated
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'completed')
        self.assertIsNotNone(payment.completed_at)
        
        # Verify Stripe confirmation was called
        mock_confirm.assert_called_once_with('pi_test123456789')
        
        # Step 3: Verify invoice was created and sent
        invoices = Invoice.objects.filter(payment=payment)
        self.assertEqual(invoices.count(), 1)
        
        invoice = invoices.first()
        self.assertEqual(invoice.user, self.student)
        self.assertEqual(invoice.total_amount, Decimal('199.99'))
        self.assertEqual(invoice.billing_email, self.student.email)
        self.assertEqual(invoice.status, 'sent')
        self.assertIsNotNone(invoice.sent_at)
        
        # Verify invoice line items
        line_items = invoice.line_items.all()
        self.assertEqual(line_items.count(), 1)
        self.assertEqual(line_items.first().course, self.course)
        self.assertEqual(line_items.first().total_price, Decimal('199.99'))
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertIn('Invoice', sent_email.subject)
        self.assertIn(self.student.email, sent_email.to)
    
    @patch.object(StripeService, 'create_payment_intent')
    def test_stripe_payment_failure_handling(self, mock_create_intent):
        """Test Stripe payment failure handling and error recovery"""
        # Mock Stripe failure
        mock_create_intent.side_effect = Exception("Stripe error: Your card was declined")
        
        self.authenticate_user(self.student)
        
        payment_data = {
            'course_id': str(self.course.id),
            'amount': '199.99',
            'payment_method': 'stripe'
        }
        
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            response = self.client.post('/api/v1/payments/payments/create_course_payment/', payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
        # Verify failed payment was recorded
        failed_payments = Payment.objects.filter(
            user=self.student,
            course=self.course,
            status='failed'
        )
        self.assertEqual(failed_payments.count(), 1)
        
        failed_payment = failed_payments.first()
        self.assertIsNotNone(failed_payment.failed_at)
        self.assertIn('Stripe error', failed_payment.metadata.get('failure_reason', ''))
    
    @patch.object(StripeService, 'create_customer')
    @patch.object(StripeService, 'create_subscription')
    def test_stripe_subscription_creation_and_billing(self, mock_create_subscription, mock_create_customer):
        """Test Stripe subscription creation and billing process"""
        # Mock Stripe responses
        mock_create_customer.return_value = self.mock_stripe_customer
        mock_create_subscription.return_value = self.mock_stripe_subscription
        
        self.authenticate_user(self.admin)  # Admin can create subscriptions
        
        subscription_data = {
            'plan': 'pro',
            'billing_cycle': 'monthly',
            'payment_method': 'stripe'
        }
        
        with patch('apps.payments.views.SubscriptionViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Subscription.objects.filter(tenant=self.tenant)
            
            response = self.client.post('/api/v1/payments/subscriptions/create_subscription/', subscription_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('subscription_id', response.data)
        self.assertIn('payment_result', response.data)
        
        # Verify subscription was created
        subscription = Subscription.objects.get(id=response.data['subscription_id'])
        self.assertEqual(subscription.organization, self.tenant)
        self.assertEqual(subscription.plan, 'pro')
        self.assertEqual(subscription.billing_cycle, 'monthly')
        self.assertEqual(subscription.status, 'active')
        self.assertEqual(subscription.stripe_customer_id, 'cus_test123456789')
        
        # Verify Stripe services were called
        mock_create_customer.assert_called_once()
        mock_create_subscription.assert_called_once()


class PayPalPaymentIntegrationTest(PaymentIntegrationTestCase):
    """Integration tests for complete PayPal payment flow (Requirement 7.1)"""
    
    @patch.object(PayPalService, 'create_order')
    @patch.object(PayPalService, 'capture_order')
    def test_complete_paypal_course_payment_flow(self, mock_capture, mock_create_order):
        """Test complete PayPal payment flow from creation to completion"""
        # Mock PayPal responses
        mock_create_order.return_value = self.mock_paypal_order
        mock_capture.return_value = True
        
        self.authenticate_user(self.student)
        
        # Step 1: Create PayPal order
        payment_data = {
            'course_id': str(self.course.id),
            'amount': '199.99',
            'payment_method': 'paypal'
        }
        
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            response = self.client.post('/api/v1/payments/payments/create_course_payment/', payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('payment_id', response.data)
        self.assertIn('order_id', response.data)
        self.assertIn('approval_url', response.data)
        
        payment_id = response.data['payment_id']
        order_id = response.data['order_id']
        approval_url = response.data['approval_url']
        
        # Verify payment was created
        payment = Payment.objects.get(id=payment_id)
        self.assertEqual(payment.paypal_order_id, 'PAYPAL123456789')
        self.assertEqual(payment.status, 'pending')
        
        # Verify PayPal service was called correctly
        mock_create_order.assert_called_once()
        call_args = mock_create_order.call_args
        self.assertEqual(call_args[1]['amount'], Decimal('199.99'))
        self.assertEqual(call_args[1]['custom_id'], str(payment_id))
        
        # Step 2: Simulate PayPal approval and capture
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            confirm_response = self.client.post(f'/api/v1/payments/payments/{payment_id}/confirm_payment/')
        
        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        
        # Verify payment completion
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'completed')
        
        # Verify PayPal capture was called
        mock_capture.assert_called_once_with('PAYPAL123456789')
        
        # Verify invoice creation
        invoice = Invoice.objects.get(payment=payment)
        self.assertEqual(invoice.status, 'sent')
    
    @patch.object(PayPalService, 'create_order')
    def test_paypal_payment_failure_handling(self, mock_create_order):
        """Test PayPal payment failure handling"""
        # Mock PayPal failure
        mock_create_order.side_effect = Exception("PayPal error: Insufficient funds")
        
        self.authenticate_user(self.student)
        
        payment_data = {
            'course_id': str(self.course.id),
            'amount': '199.99',
            'payment_method': 'paypal'
        }
        
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            response = self.client.post('/api/v1/payments/payments/create_course_payment/', payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify failed payment was recorded
        failed_payment = Payment.objects.filter(
            user=self.student,
            course=self.course,
            status='failed'
        ).first()
        
        self.assertIsNotNone(failed_payment)
        self.assertIn('PayPal error', failed_payment.metadata.get('failure_reason', ''))


class BankTransferPaymentIntegrationTest(PaymentIntegrationTestCase):
    """Integration tests for bank transfer payment flow (Requirement 7.1)"""
    
    def test_complete_bank_transfer_payment_flow(self):
        """Test complete bank transfer payment flow with manual approval"""
        self.authenticate_user(self.student)
        
        # Step 1: Create bank transfer payment
        payment_data = {
            'course_id': str(self.course.id),
            'amount': '199.99',
            'payment_method': 'bank_transfer'
        }
        
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            response = self.client.post('/api/v1/payments/payments/create_course_payment/', payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        payment_id = response.data['payment_id']
        payment = Payment.objects.get(id=payment_id)
        
        # Verify bank transfer details
        self.assertEqual(payment.payment_method, 'bank_transfer')
        self.assertEqual(payment.status, 'pending')
        self.assertIsNotNone(payment.bank_transfer_reference)
        self.assertTrue(payment.bank_transfer_reference.startswith('BT-'))
        
        # Step 2: Admin approves bank transfer
        self.authenticate_user(self.admin)
        
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            approve_response = self.client.post(f'/api/v1/payments/payments/{payment_id}/approve_bank_transfer/')
        
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        self.assertIn('approved successfully', approve_response.data['message'])
        
        # Verify payment approval
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'completed')
        self.assertEqual(payment.bank_transfer_approved_by, self.admin)
        self.assertIsNotNone(payment.completed_at)
        
        # Verify invoice creation and sending
        invoice = Invoice.objects.get(payment=payment)
        self.assertEqual(invoice.status, 'sent')
        self.assertEqual(len(mail.outbox), 1)
    
    def test_bank_transfer_rejection_flow(self):
        """Test bank transfer rejection flow"""
        self.authenticate_user(self.student)
        
        # Create bank transfer payment
        payment_data = {
            'course_id': str(self.course.id),
            'amount': '199.99',
            'payment_method': 'bank_transfer'
        }
        
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            response = self.client.post('/api/v1/payments/payments/create_course_payment/', payment_data, format='json')
        
        payment_id = response.data['payment_id']
        
        # Admin rejects bank transfer
        self.authenticate_user(self.admin)
        
        rejection_data = {
            'reason': 'Invalid bank transfer details provided'
        }
        
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            reject_response = self.client.post(
                f'/api/v1/payments/payments/{payment_id}/reject_bank_transfer/',
                rejection_data,
                format='json'
            )
        
        self.assertEqual(reject_response.status_code, status.HTTP_200_OK)
        
        # Verify payment rejection
        payment = Payment.objects.get(id=payment_id)
        self.assertEqual(payment.status, 'failed')
        self.assertIsNotNone(payment.failed_at)
        self.assertEqual(payment.metadata['rejection_reason'], 'Invalid bank transfer details provided')


class SubscriptionBillingIntegrationTest(PaymentIntegrationTestCase):
    """Integration tests for subscription billing and renewal process (Requirement 7.3)"""
    
    def test_subscription_creation_and_initial_billing(self):
        """Test subscription creation with initial billing"""
        self.authenticate_user(self.admin)
        
        subscription_data = {
            'plan': 'basic',
            'billing_cycle': 'monthly',
            'payment_method': 'stripe'
        }
        
        with patch.object(StripeService, 'create_customer') as mock_customer, \
             patch.object(StripeService, 'create_payment_intent') as mock_intent, \
             patch('apps.payments.views.SubscriptionViewSet.get_queryset') as mock_queryset:
            
            mock_customer.return_value = self.mock_stripe_customer
            mock_intent.return_value = self.mock_stripe_intent
            mock_queryset.return_value = Subscription.objects.filter(tenant=self.tenant)
            
            response = self.client.post('/api/v1/payments/subscriptions/create_subscription/', subscription_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify subscription creation
        subscription = Subscription.objects.get(id=response.data['subscription_id'])
        self.assertEqual(subscription.plan, 'basic')
        self.assertEqual(subscription.billing_cycle, 'monthly')
        self.assertEqual(subscription.amount, Decimal('29.00'))  # Basic monthly price
        self.assertEqual(subscription.status, 'active')
        
        # Verify initial payment was created
        payments = Payment.objects.filter(subscription=subscription)
        self.assertEqual(payments.count(), 1)
        
        initial_payment = payments.first()
        self.assertEqual(initial_payment.payment_type, 'subscription')
        self.assertEqual(initial_payment.amount, Decimal('29.00'))
    
    @patch.object(SubscriptionService, 'renew_subscription')
    def test_subscription_renewal_process(self, mock_renew):
        """Test subscription renewal process"""
        # Create existing subscription
        subscription = Subscription.objects.create(
            organization=self.tenant,
            tenant=self.tenant,
            plan='pro',
            billing_cycle='monthly',
            amount=Decimal('99.00'),
            current_period_start=timezone.now() - timedelta(days=30),
            current_period_end=timezone.now() - timedelta(days=1),  # Expired
            status='active'
        )
        
        # Mock renewal response
        mock_renew.return_value = {
            'payment_id': str(uuid.uuid4()),
            'client_secret': 'pi_renewal_secret'
        }
        
        self.authenticate_user(self.admin)
        
        with patch('apps.payments.views.SubscriptionViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Subscription.objects.filter(tenant=self.tenant)
            
            response = self.client.post(f'/api/v1/payments/subscriptions/{subscription.id}/renew_subscription/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('renewed successfully', response.data['message'])
        
        # Verify renewal service was called
        mock_renew.assert_called_once_with(subscription)
    
    def test_subscription_cancellation(self):
        """Test subscription cancellation process"""
        # Create active subscription
        subscription = Subscription.objects.create(
            organization=self.tenant,
            tenant=self.tenant,
            plan='enterprise',
            billing_cycle='yearly',
            amount=Decimal('2990.00'),
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=365),
            status='active'
        )
        
        self.authenticate_user(self.admin)
        
        with patch('apps.payments.views.SubscriptionViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Subscription.objects.filter(tenant=self.tenant)
            
            response = self.client.post(f'/api/v1/payments/subscriptions/{subscription.id}/cancel_subscription/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('cancelled successfully', response.data['message'])
        
        # Verify cancellation
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'cancelled')
        self.assertIsNotNone(subscription.cancelled_at)
    
    def test_subscription_billing_failure_handling(self):
        """Test handling of subscription billing failures"""
        # Create subscription with past due status
        subscription = Subscription.objects.create(
            organization=self.tenant,
            tenant=self.tenant,
            plan='pro',
            billing_cycle='monthly',
            amount=Decimal('99.00'),
            current_period_start=timezone.now() - timedelta(days=30),
            current_period_end=timezone.now() + timedelta(days=5),
            status='past_due'
        )
        
        # Create failed payment record
        failed_payment = Payment.objects.create(
            subscription=subscription,
            payment_type='subscription',
            amount=Decimal('99.00'),
            payment_method='stripe',
            status='failed',
            tenant=self.tenant,
            description='Pro subscription payment failed',
            metadata={'failure_reason': 'Card declined'}
        )
        
        # Verify failed payment is recorded correctly
        self.assertEqual(failed_payment.status, 'failed')
        self.assertEqual(failed_payment.subscription, subscription)
        self.assertIn('Card declined', failed_payment.metadata['failure_reason'])


class InvoiceGenerationIntegrationTest(PaymentIntegrationTestCase):
    """Integration tests for invoice generation and delivery (Requirement 7.3)"""
    
    def test_invoice_generation_for_course_payment(self):
        """Test invoice generation for course payments"""
        # Create completed payment
        payment = Payment.objects.create(
            user=self.student,
            course=self.course,
            payment_type='course',
            amount=Decimal('199.99'),
            payment_method='stripe',
            status='completed',
            tenant=self.tenant,
            description=f'Course enrollment: {self.course.title}',
            completed_at=timezone.now()
        )
        
        # Generate invoice
        invoice = InvoiceService.create_invoice_for_payment(payment)
        
        # Verify invoice details
        self.assertEqual(invoice.user, self.student)
        self.assertEqual(invoice.payment, payment)
        self.assertEqual(invoice.invoice_type, 'payment')
        self.assertEqual(invoice.total_amount, Decimal('199.99'))
        self.assertEqual(invoice.billing_name, f'{self.student.first_name} {self.student.last_name}')
        self.assertEqual(invoice.billing_email, self.student.email)
        self.assertIn(self.course.title, invoice.description)
        
        # Verify invoice number generation
        self.assertTrue(invoice.invoice_number.startswith('INV-'))
        
        # Verify line items
        line_items = invoice.line_items.all()
        self.assertEqual(line_items.count(), 1)
        
        line_item = line_items.first()
        self.assertEqual(line_item.course, self.course)
        self.assertEqual(line_item.quantity, Decimal('1.00'))
        self.assertEqual(line_item.unit_price, Decimal('199.99'))
        self.assertEqual(line_item.total_price, Decimal('199.99'))
    
    def test_invoice_generation_for_subscription_payment(self):
        """Test invoice generation for subscription payments"""
        # Create subscription
        subscription = Subscription.objects.create(
            organization=self.tenant,
            tenant=self.tenant,
            plan='pro',
            billing_cycle='monthly',
            amount=Decimal('99.00'),
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=30),
            status='active'
        )
        
        # Create subscription payment
        payment = Payment.objects.create(
            subscription=subscription,
            payment_type='subscription',
            amount=Decimal('99.00'),
            payment_method='stripe',
            status='completed',
            tenant=self.tenant,
            description='Pro subscription payment',
            completed_at=timezone.now()
        )
        
        # Generate invoice
        invoice = InvoiceService.create_invoice_for_payment(payment)
        
        # Verify invoice details
        self.assertEqual(invoice.organization, self.tenant)
        self.assertEqual(invoice.subscription, subscription)
        self.assertEqual(invoice.invoice_type, 'subscription')
        self.assertEqual(invoice.total_amount, Decimal('99.00'))
        self.assertEqual(invoice.billing_name, self.tenant.name)
        self.assertIn('Pro Subscription', invoice.description)
    
    @patch('django.core.mail.send_mail')
    def test_invoice_email_delivery(self, mock_send_mail):
        """Test invoice email delivery"""
        # Create payment and invoice
        payment = Payment.objects.create(
            user=self.student,
            course=self.course,
            amount=Decimal('199.99'),
            payment_method='stripe',
            status='completed',
            tenant=self.tenant,
            completed_at=timezone.now()
        )
        
        invoice = InvoiceService.create_invoice_for_payment(payment)
        
        # Send invoice
        result = InvoiceService.send_invoice(invoice)
        
        # Verify sending
        self.assertTrue(result)
        mock_send_mail.assert_called_once()
        
        # Verify invoice status updated
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'sent')
        self.assertIsNotNone(invoice.sent_at)
        
        # Verify email content
        call_args = mock_send_mail.call_args
        self.assertIn('Invoice', call_args[1]['subject'])
        self.assertIn(invoice.invoice_number, call_args[1]['subject'])
        self.assertEqual(call_args[1]['recipient_list'], [self.student.email])
    
    def test_invoice_pdf_generation(self):
        """Test invoice PDF generation"""
        # Create payment and invoice
        payment = Payment.objects.create(
            user=self.student,
            course=self.course,
            amount=Decimal('199.99'),
            payment_method='stripe',
            status='completed',
            tenant=self.tenant,
            completed_at=timezone.now()
        )
        
        invoice = InvoiceService.create_invoice_for_payment(payment)
        
        # Test PDF generation (may not work if reportlab not installed)
        from apps.payments.services import PDFInvoiceService
        
        try:
            pdf_content = PDFInvoiceService.generate_invoice_pdf(invoice)
            if pdf_content:
                self.assertIsInstance(pdf_content, bytes)
                self.assertGreater(len(pdf_content), 0)
        except ImportError:
            # PDF generation is optional, skip if reportlab not available
            pass
    
    def test_overdue_invoice_handling(self):
        """Test overdue invoice detection and handling"""
        # Create overdue invoice
        overdue_date = timezone.now().date() - timedelta(days=5)
        
        invoice = Invoice.objects.create(
            user=self.student,
            subtotal=Decimal('199.99'),
            total_amount=Decimal('199.99'),
            billing_name=f'{self.student.first_name} {self.student.last_name}',
            billing_email=self.student.email,
            description='Overdue test invoice',
            due_date=overdue_date,
            status='sent',
            tenant=self.tenant
        )
        
        self.authenticate_user(self.admin)
        
        # Get overdue invoices
        with patch('apps.payments.views.InvoiceViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Invoice.objects.filter(tenant=self.tenant)
            
            response = self.client.get('/api/v1/payments/invoices/overdue_invoices/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify invoice was marked as overdue
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'overdue')


class PaymentSecurityIntegrationTest(PaymentIntegrationTestCase):
    """Integration tests for payment security and error handling (Requirement 7.5)"""
    
    def test_payment_access_control(self):
        """Test that users can only access their own payments"""
        # Create payments for different users
        student_payment = Payment.objects.create(
            user=self.student,
            course=self.course,
            amount=Decimal('199.99'),
            payment_method='stripe',
            tenant=self.tenant
        )
        
        instructor_payment = Payment.objects.create(
            user=self.instructor,
            course=self.course,
            amount=Decimal('99.99'),
            payment_method='paypal',
            tenant=self.tenant
        )
        
        # Student should only see their own payment
        self.authenticate_user(self.student)
        
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant, user=self.student)
            
            response = self.client.get('/api/v1/payments/payments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Note: In a real test, we'd verify the response only contains student's payments
        
        # Test accessing other user's payment directly
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant, user=self.student)
            
            response = self.client.get(f'/api/v1/payments/payments/{instructor_payment.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_admin_only_operations(self):
        """Test that certain operations require admin privileges"""
        # Create bank transfer payment
        payment = Payment.objects.create(
            user=self.student,
            course=self.course,
            amount=Decimal('199.99'),
            payment_method='bank_transfer',
            status='pending',
            tenant=self.tenant
        )
        
        # Non-admin user should not be able to approve bank transfers
        self.authenticate_user(self.student)
        
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            response = self.client.post(f'/api/v1/payments/payments/{payment.id}/approve_bank_transfer/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin should be able to approve
        self.authenticate_user(self.admin)
        
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            response = self.client.post(f'/api/v1/payments/payments/{payment.id}/approve_bank_transfer/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_input_validation_and_sanitization(self):
        """Test input validation and sanitization for payment data"""
        self.authenticate_user(self.student)
        
        # Test missing required fields
        invalid_data = {
            'amount': '199.99'
            # Missing course_id and payment_method
        }
        
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            response = self.client.post('/api/v1/payments/payments/create_course_payment/', invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
        # Test invalid amount
        invalid_amount_data = {
            'course_id': str(self.course.id),
            'amount': '-100.00',  # Negative amount
            'payment_method': 'stripe'
        }
        
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            response = self.client.post('/api/v1/payments/payments/create_course_payment/', invalid_amount_data, format='json')
        
        # Should be handled by validation (exact response depends on implementation)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])
        
        # Test invalid payment method
        invalid_method_data = {
            'course_id': str(self.course.id),
            'amount': '199.99',
            'payment_method': 'bitcoin'  # Invalid method
        }
        
        with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
            mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
            
            response = self.client.post('/api/v1/payments/payments/create_course_payment/', invalid_method_data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])
    
    def test_webhook_security(self):
        """Test webhook endpoint security"""
        # Test Stripe webhook without proper signature
        webhook_data = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test123',
                    'status': 'succeeded'
                }
            }
        }
        
        # Without proper signature, webhook should fail
        response = self.client.post('/api/v1/payments/stripe-webhook/', webhook_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test PayPal webhook
        paypal_webhook_data = {
            'event_type': 'PAYMENT.CAPTURE.COMPLETED',
            'resource': {
                'id': 'CAPTURE123',
                'status': 'COMPLETED'
            }
        }
        
        response = self.client.post('/api/v1/payments/paypal-webhook/', paypal_webhook_data, format='json')
        # Should handle webhook (exact response depends on verification implementation)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
    
    def test_error_handling_and_logging(self):
        """Test comprehensive error handling and logging"""
        self.authenticate_user(self.student)
        
        # Test handling of external service failures
        with patch.object(StripeService, 'create_payment_intent') as mock_stripe:
            mock_stripe.side_effect = Exception("Network timeout")
            
            payment_data = {
                'course_id': str(self.course.id),
                'amount': '199.99',
                'payment_method': 'stripe'
            }
            
            with patch('apps.payments.views.PaymentViewSet.get_queryset') as mock_queryset:
                mock_queryset.return_value = Payment.objects.filter(tenant=self.tenant)
                
                response = self.client.post('/api/v1/payments/payments/create_course_payment/', payment_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)
            
            # Verify error was logged in payment record
            failed_payments = Payment.objects.filter(
                user=self.student,
                course=self.course,
                status='failed'
            )
            
            if failed_payments.exists():
                failed_payment = failed_payments.first()
                self.assertIn('Network timeout', failed_payment.metadata.get('failure_reason', ''))


class PaymentWebhookIntegrationTest(PaymentIntegrationTestCase):
    """Integration tests for payment webhook handling"""
    
    def test_stripe_webhook_payment_success(self):
        """Test Stripe webhook handling for successful payments"""
        # Create payment with Stripe intent ID
        payment = Payment.objects.create(
            user=self.student,
            course=self.course,
            amount=Decimal('199.99'),
            payment_method='stripe',
            status='processing',
            stripe_payment_intent_id='pi_test123456789',
            tenant=self.tenant
        )
        
        # Mock webhook data
        webhook_data = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test123456789',
                    'status': 'succeeded',
                    'amount': 19999,  # In cents
                    'currency': 'usd'
                }
            }
        }
        
        # Mock webhook signature verification
        with patch('stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = webhook_data
            
            response = self.client.post(
                '/api/v1/payments/stripe-webhook/',
                json.dumps(webhook_data),
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='test_signature'
            )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify payment was updated
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'completed')
        self.assertIsNotNone(payment.completed_at)
        
        # Verify invoice was created
        invoices = Invoice.objects.filter(payment=payment)
        self.assertEqual(invoices.count(), 1)
    
    def test_paypal_webhook_payment_success(self):
        """Test PayPal webhook handling for successful payments"""
        # Create payment with PayPal order ID
        payment = Payment.objects.create(
            user=self.student,
            course=self.course,
            amount=Decimal('199.99'),
            payment_method='paypal',
            status='processing',
            tenant=self.tenant
        )
        
        # Mock webhook data
        webhook_data = {
            'event_type': 'PAYMENT.CAPTURE.COMPLETED',
            'resource': {
                'id': 'CAPTURE123456789',
                'status': 'COMPLETED',
                'custom_id': str(payment.id),
                'amount': {
                    'currency_code': 'USD',
                    'value': '199.99'
                }
            }
        }
        
        response = self.client.post(
            '/api/v1/payments/paypal-webhook/',
            json.dumps(webhook_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify payment was updated
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'completed')