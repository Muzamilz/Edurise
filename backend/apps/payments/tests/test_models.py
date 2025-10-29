from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.accounts.models import Organization
from apps.courses.models import Course
from apps.payments.models import (
    Payment, Subscription, SubscriptionPlan, Invoice, 
    PaymentMethod, Refund
)

User = get_user_model()


class PaymentModelTest(TestCase):
    """Test cases for the Payment model"""
    
    def setUp(self):
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
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            price=Decimal('99.99')
        )
    
    def test_create_payment(self):
        """Test creating a payment"""
        payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            tenant=self.tenant,
            amount=Decimal('99.99'),
            currency='USD',
            payment_method='stripe',
            status='pending'
        )
        
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.course, self.course)
        self.assertEqual(payment.amount, Decimal('99.99'))
        self.assertEqual(payment.currency, 'USD')
        self.assertEqual(payment.payment_method, 'stripe')
        self.assertEqual(payment.status, 'pending')
    
    def test_payment_string_representation(self):
        """Test the string representation of Payment"""
        payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            tenant=self.tenant,
            amount=Decimal('99.99'),
            currency='USD',
            payment_method='stripe',
            status='pending'
        )
        expected = f"Payment {payment.id} - {self.user.email} - $99.99"
        self.assertEqual(str(payment), expected)
    
    def test_payment_completion(self):
        """Test payment completion"""
        payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            tenant=self.tenant,
            amount=Decimal('99.99'),
            currency='USD',
            payment_method='stripe',
            status='pending',
            stripe_payment_intent_id='pi_test123'
        )
        
        # Complete the payment
        payment.status = 'completed'
        payment.save()
        
        self.assertEqual(payment.status, 'completed')
    
    def test_payment_failure(self):
        """Test payment failure"""
        payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            tenant=self.tenant,
            amount=Decimal('99.99'),
            currency='USD',
            payment_method='stripe',
            status='pending'
        )
        
        # Fail the payment
        payment.status = 'failed'
        payment.failure_reason = 'Insufficient funds'
        payment.save()
        
        self.assertEqual(payment.status, 'failed')
        self.assertEqual(payment.failure_reason, 'Insufficient funds')


class SubscriptionPlanModelTest(TestCase):
    """Test cases for the SubscriptionPlan model"""
    
    def test_create_subscription_plan(self):
        """Test creating a subscription plan"""
        plan = SubscriptionPlan.objects.create(
            name='Pro Plan',
            description='Professional subscription with advanced features',
            price=Decimal('29.99'),
            currency='USD',
            billing_cycle='monthly',
            features={
                'max_courses': 100,
                'max_students': 1000,
                'ai_features': True,
                'analytics': True
            }
        )
        
        self.assertEqual(plan.name, 'Pro Plan')
        self.assertEqual(plan.price, Decimal('29.99'))
   