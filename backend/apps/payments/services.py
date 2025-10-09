import stripe
from django.conf import settings
from .models import Payment, Invoice


class StripeService:
    """Stripe payment processing service"""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def create_payment_intent(self, amount, currency='usd', metadata=None):
        """Create Stripe payment intent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                metadata=metadata or {}
            )
            return intent
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    def confirm_payment(self, payment_intent_id):
        """Confirm payment intent"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent.status == 'succeeded'
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")


class PayPalService:
    """PayPal payment processing service"""
    
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.base_url = settings.PAYPAL_BASE_URL
    
    def create_order(self, amount, currency='USD'):
        """Create PayPal order"""
        # Implementation would use PayPal SDK
        pass
    
    def capture_order(self, order_id):
        """Capture PayPal order"""
        # Implementation would use PayPal SDK
        pass


class PaymentService:
    """Main payment processing service"""
    
    @staticmethod
    def process_payment(user, course, amount, payment_method, tenant):
        """Process payment for course enrollment"""
        
        # Create payment record
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=amount,
            payment_method=payment_method,
            tenant=tenant
        )
        
        try:
            if payment_method == 'stripe':
                stripe_service = StripeService()
                intent = stripe_service.create_payment_intent(
                    amount=amount,
                    metadata={
                        'payment_id': str(payment.id),
                        'course_id': str(course.id) if course else None,
                        'user_id': str(user.id)
                    }
                )
                payment.stripe_payment_intent_id = intent.id
                payment.save()
                
                return {
                    'payment_id': payment.id,
                    'client_secret': intent.client_secret
                }
                
            elif payment_method == 'paypal':
                paypal_service = PayPalService()
                order = paypal_service.create_order(amount)
                payment.paypal_order_id = order.get('id')
                payment.save()
                
                return {
                    'payment_id': payment.id,
                    'order_id': order.get('id')
                }
                
            elif payment_method == 'bank_transfer':
                # Bank transfer requires manual approval
                payment.status = 'pending'
                payment.save()
                
                return {
                    'payment_id': payment.id,
                    'message': 'Bank transfer payment created. Awaiting manual approval.'
                }
                
        except Exception as e:
            payment.status = 'failed'
            payment.save()
            raise e
    
    @staticmethod
    def confirm_payment(payment_id, external_id=None):
        """Confirm payment completion"""
        try:
            payment = Payment.objects.get(id=payment_id)
            
            if payment.payment_method == 'stripe' and payment.stripe_payment_intent_id:
                stripe_service = StripeService()
                if stripe_service.confirm_payment(payment.stripe_payment_intent_id):
                    payment.status = 'completed'
                    payment.save()
                    return True
                    
            elif payment.payment_method == 'paypal' and payment.paypal_order_id:
                paypal_service = PayPalService()
                if paypal_service.capture_order(payment.paypal_order_id):
                    payment.status = 'completed'
                    payment.save()
                    return True
                    
            elif payment.payment_method == 'bank_transfer':
                # Manual approval for bank transfers
                payment.status = 'completed'
                payment.save()
                return True
                
            return False
            
        except Payment.DoesNotExist:
            return False