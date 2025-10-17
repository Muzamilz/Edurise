from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.payments.services import StripeService, PayPalService, PaymentService
from apps.courses.models import Course
from apps.accounts.models import Organization

User = get_user_model()


class Command(BaseCommand):
    help = 'Test payment services'

    def add_arguments(self, parser):
        parser.add_argument(
            '--stripe',
            action='store_true',
            help='Test Stripe integration',
        )
        parser.add_argument(
            '--paypal',
            action='store_true',
            help='Test PayPal integration',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Test all payment services',
        )

    def handle(self, *args, **options):
        if options['stripe'] or options['all']:
            self.test_stripe()
        
        if options['paypal'] or options['all']:
            self.test_paypal()

    def test_stripe(self):
        """Test Stripe service"""
        self.stdout.write("Testing Stripe service...")
        
        try:
            stripe_service = StripeService()
            
            # Test payment intent creation
            intent = stripe_service.create_payment_intent(
                amount=Decimal('99.99'),
                metadata={'test': 'true'}
            )
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ Stripe payment intent created: {intent.id}")
            )
            
            # Test customer creation
            customer = stripe_service.create_customer(
                email="test@example.com",
                name="Test Customer"
            )
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ Stripe customer created: {customer.id}")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Stripe test failed: {e}")
            )

    def test_paypal(self):
        """Test PayPal service"""
        self.stdout.write("Testing PayPal service...")
        
        try:
            paypal_service = PayPalService()
            
            # Test access token
            token = paypal_service.get_access_token()
            self.stdout.write(
                self.style.SUCCESS("✓ PayPal access token obtained")
            )
            
            # Test order creation
            order = paypal_service.create_order(
                amount=Decimal('99.99'),
                description="Test Course Payment"
            )
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ PayPal order created: {order.get('id')}")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ PayPal test failed: {e}")
            )