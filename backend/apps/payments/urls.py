from django.urls import path
from .views import (
    StripeWebhookView, PayPalWebhookView,
    StripeAPIView, PayPalAPIView
)

# Note: Payment ViewSets are registered in the centralized API router (apps/api/urls.py)
# This file contains webhook endpoints and direct payment gateway API endpoints

urlpatterns = [
    # Webhook endpoints
    path('webhooks/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('webhooks/paypal/', PayPalWebhookView.as_view(), name='paypal-webhook'),
    
    # Stripe API endpoints
    path('stripe/create-payment-intent/', StripeAPIView.as_view(), {'action': 'create_payment_intent'}, name='stripe-create-payment-intent'),
    path('stripe/confirm-payment/', StripeAPIView.as_view(), {'action': 'confirm_payment'}, name='stripe-confirm-payment'),
    path('stripe/create-customer/', StripeAPIView.as_view(), {'action': 'create_customer'}, name='stripe-create-customer'),
    path('stripe/create-subscription/', StripeAPIView.as_view(), {'action': 'create_subscription'}, name='stripe-create-subscription'),
    path('stripe/cancel-subscription/', StripeAPIView.as_view(), {'action': 'cancel_subscription'}, name='stripe-cancel-subscription'),
    path('stripe/retrieve-payment/', StripeAPIView.as_view(), {'action': 'retrieve_payment'}, name='stripe-retrieve-payment'),
    
    # PayPal API endpoints
    path('paypal/create-order/', PayPalAPIView.as_view(), {'action': 'create_order'}, name='paypal-create-order'),
    path('paypal/capture-order/', PayPalAPIView.as_view(), {'action': 'capture_order'}, name='paypal-capture-order'),
    path('paypal/get-order/', PayPalAPIView.as_view(), {'action': 'get_order'}, name='paypal-get-order'),
    path('paypal/refund-payment/', PayPalAPIView.as_view(), {'action': 'refund_payment'}, name='paypal-refund-payment'),
]