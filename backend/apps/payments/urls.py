from django.urls import path
from .views import StripeWebhookView, PayPalWebhookView

# Note: Payment ViewSets are registered in the centralized API router (apps/api/urls.py)
# This file only contains webhook endpoints and other non-ViewSet payment functionality

urlpatterns = [
    path('webhooks/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('webhooks/paypal/', PayPalWebhookView.as_view(), name='paypal-webhook'),
]