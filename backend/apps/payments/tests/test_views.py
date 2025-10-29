from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from unittest.mock import patch, Mock
from apps.accounts.models import Organization, UserProfile
from apps.courses.models import Course
from apps.payments.models import Payment, Subscription, SubscriptionPlan, Invoice
from apps.accounts.services import JWTAuthService

User = get_user_model()


class PaymentViewSetTest(TestCase):
    """Test cases for PaymentViewSet"""
    
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
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create profiles
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
        UserProfile.objects.create(user=self.instructor, tenant=self.tenant)
        UserProfile.objects.create(user=self.admin_user, tenant=self.tenant)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            price=Decimal('99.99')
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    @patch('apps.payments.services.PaymentService.process_course_payment')
    def test_create_course_payment(self, mock_process_payment):
        """Test creating a course payment"""
        mock_process_payment.return_value = {
            'payment_id': 'test_payment_123',
            'status': 'pending',
            'client_secret': 'pi_test_client_secret'
        }
        
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/payments/payments/create_course_payment/',
            {
                'course_id': str(self.course.id),
                'amount': '99.99',
                'payment_method': 'stripe'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_process_payment.assert_called_once()
    
    def test_create_course_payment_missing_data(self):
        """Test course payment creation with missing data"""
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/payments/payments/create_course_payment/',
            {
                'course_id': str(self.course.id),
                # Missing amount and payment_method
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())
    
    def test_create_course_payment_invalid_course(self):
        """Test course payment creation with invalid course"""
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/payments/payments/create_course_payment/',
            {
                'course_id': '00000000-0000-0000-0000-000000000000',
                'amount': '99.99',
                'payment_method': 'stripe'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('apps.payments.services.PaymentService.confirm_payment')
    def test_confirm_payment(self, mock_confirm_payment):
        """Test payment confirmation"""
        mock_confirm_payment.return_value = True
        
        payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            tenant=self.tenant,
            amount=Decimal('99.99'),
            currency='USD',
            payment_method='stripe',
            status='pending'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.post(f'/api/v1/payments/payments/{payment.id}/confirm_payment/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_confirm_payment.assert_called_once_with(payment.id)
    
    def test_confirm_payment_permission_denied(self):
        """Test payment confirmation with wrong user"""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=other_user, tenant=self.tenant)
        
        payment = Payment.objects.create(
            user=other_user,
            course=self.course,
            tenant=self.tenant,
            amount=Decimal('99.99'),
            currency='USD',
            payment_method='stripe',
            status='pending'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.post(f'/api/v1/payments/payments/{payment.id}/confirm_payment/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('apps.payments.services.BankTransferService.approve_bank_transfer')
    @patch('apps.payments.services.InvoiceService.create_invoice_for_payment')
    @patch('apps.payments.services.InvoiceService.send_invoice')
    def test_approve_bank_transfer(self, mock_send_invoice, mock_create_invoice, mock_approve_transfer):
        """Test bank transfer approval by admin"""
        mock_approve_transfer.return_value = True
        mock_invoice = Mock()
        mock_create_invoice.return_value = mock_invoice
        
        payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            tenant=self.tenant,
            amount=Decimal('99.99'),
            currency='USD',
            payment_method='bank_transfer',
            status='pending'
        )
        
        self.authenticate_user(self.admin_user)
        
        response = self.client.post(f'/api/v1/payments/payments/{payment.id}/approve_bank_transfer/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_approve_transfer.assert_called_once_with(payment.id, self.admin_user)
        mock_create_invoice.assert_called_once_with(payment)
        mock_send_invoice.assert_called_once_with(mock_invoice)
    
    def test_approve_bank_transfer_non_admin(self):
        """Test bank transfer approval by non-admin user"""
        payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            tenant=self.tenant,
            amount=Decimal('99.99'),
            currency='USD',
            payment_method='bank_transfer',
            status='pending'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.post(f'/api/v1/payments/payments/{payment.id}/approve_bank_transfer/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_approve_non_bank_transfer(self):
        """Test approving non-bank transfer payment"""
        payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            tenant=self.tenant,
            amount=Decimal('99.99'),
            currency='USD',
            payment_method='stripe',
            status='pending'
        )
        
        self.authenticate_user(self.admin_user)
        
        response = self.client.post(f'/api/v1/payments/payments/{payment.id}/approve_bank_transfer/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_revenue_stats_admin_only(self):
        """Test revenue stats endpoint requires admin access"""
        self.authenticate_user(self.user)
        
        response = self.client.get('/api/v1/payments/payments/revenue_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_revenue_stats_success(self):
        """Test revenue stats calculation"""
        # Create test payments
        Payment.objects.create(
            user=self.user,
            course=self.course,
            tenant=self.tenant,
            amount=Decimal('99.99'),
            currency='USD',
            payment_method='stripe',
            status='completed'
        )
        
        Payment.objects.create(
            user=self.user,
            course=self.course,
            tenant=self.tenant,
            amount=Decimal('49.99'),
            currency='USD',
            payment_method='paypal',
            status='failed'
        )
        
        self.authenticate_user(self.admin_user)
        
        response = self.client.get('/api/v1/payments/payments/revenue_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('total_revenue', data)
        self.assertIn('total_transactions', data)
        self.assertIn('successful_payments', data)
        self.assertIn('failed_payments', data)
        self.assertEqual(data['total_revenue'], 99.99)
        self.assertEqual(data['successful_payments'], 1)
        self.assertEqual(data['failed_payments'], 1)


class SubscriptionViewSetTest(TestCase):
    """Test cases for SubscriptionViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='basic'
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        
        UserProfile.objects.create(user=self.admin_user, tenant=self.tenant)
        
        self.subscription_plan = SubscriptionPlan.objects.create(
            name='Pro Plan',
            description='Professional features',
            price=Decimal('29.99'),
            currency='USD',
            billing_cycle='monthly',
            features={'max_courses': 100, 'ai_features': True}
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    @patch('apps.payments.services.SubscriptionService.create_subscription')
    @patch('apps.payments.services.SubscriptionService.process_subscription_payment')
    def test_create_subscription(self, mock_process_payment, mock_create_subscription):
        """Test subscription creation"""
        mock_subscription = Mock()
        mock_subscription.id = 'test_sub_123'
        mock_create_subscription.return_value = mock_subscription
        mock_process_payment.return_value = {'status': 'success', 'payment_id': 'pay_123'}
        
        self.authenticate_user(self.admin_user)
        
        response = self.client.post(
            '/api/v1/payments/subscriptions/create_subscription/',
            {
                'plan': 'pro',
                'billing_cycle': 'monthly',
                'payment_method': 'stripe'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn('subscription_id', data)
        self.assertIn('payment_result', data)
    
    def test_create_subscription_missing_plan(self):
        """Test subscription creation without plan"""
        self.authenticate_user(self.admin_user)
        
        response = self.client.post(
            '/api/v1/payments/subscriptions/create_subscription/',
            {
                'billing_cycle': 'monthly'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cancel_subscription(self):
        """Test subscription cancellation"""
        subscription = Subscription.objects.create(
            organization=self.tenant,
            plan='pro',
            status='active',
            amount=Decimal('29.99'),
            currency='USD',
            billing_cycle='monthly'
        )
        
        self.authenticate_user(self.admin_user)
        
        response = self.client.post(f'/api/v1/payments/subscriptions/{subscription.id}/cancel_subscription/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify subscription was cancelled
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'cancelled')


class InvoiceViewSetTest(TestCase):
    """Test cases for InvoiceViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
        UserProfile.objects.create(user=self.admin_user, tenant=self.tenant)
        
        self.invoice = Invoice.objects.create(
            user=self.user,
            tenant=self.tenant,
            invoice_number='INV-001',
            total_amount=Decimal('99.99'),
            currency='USD',
            status='sent'
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    @patch('apps.payments.services.InvoiceService.send_invoice')
    def test_send_invoice(self, mock_send_invoice):
        """Test sending invoice via email"""
        self.authenticate_user(self.admin_user)
        
        response = self.client.post(f'/api/v1/payments/invoices/{self.invoice.id}/send_invoice/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_invoice.assert_called_once_with(self.invoice)
    
    def test_send_invoice_non_admin(self):
        """Test sending invoice by non-admin user"""
        self.authenticate_user(self.user)
        
        response = self.client.post(f'/api/v1/payments/invoices/{self.invoice.id}/send_invoice/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('apps.payments.services.InvoiceService.mark_invoice_paid')
    def test_mark_invoice_paid(self, mock_mark_paid):
        """Test marking invoice as paid"""
        self.authenticate_user(self.admin_user)
        
        response = self.client.post(f'/api/v1/payments/invoices/{self.invoice.id}/mark_paid/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_mark_paid.assert_called_once_with(self.invoice)
    
    def test_overdue_invoices(self):
        """Test getting overdue invoices"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Create overdue invoice
        overdue_invoice = Invoice.objects.create(
            user=self.user,
            tenant=self.tenant,
            invoice_number='INV-002',
            total_amount=Decimal('49.99'),
            currency='USD',
            status='sent',
            due_date=(timezone.now() - timedelta(days=5)).date()
        )
        
        self.authenticate_user(self.admin_user)
        
        response = self.client.get('/api/v1/payments/invoices/overdue_invoices/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should contain the overdue invoice
        invoice_ids = [invoice['id'] for invoice in data]
        self.assertIn(str(overdue_invoice.id), invoice_ids)