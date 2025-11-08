# Payment System Implementation

This document describes the comprehensive payment processing system implemented for the Edurise LMS platform.

## Overview

The payment system supports multiple payment methods, subscription billing, invoice generation, and comprehensive transaction tracking with full multi-tenant isolation.

## Features Implemented

### 1. Payment Model for Transaction Tracking
- **Payment Model**: Comprehensive payment tracking with support for course payments and subscriptions
- **Status Management**: Pending, processing, completed, failed, cancelled, refunded states
- **Multi-tenant Isolation**: All payments are tenant-aware
- **Metadata Support**: JSON field for storing additional payment information

### 2. Stripe Integration for Card Payments
- **StripeService**: Complete Stripe API integration
- **Payment Intents**: Support for one-time payments
- **Subscriptions**: Recurring billing for institutional plans
- **Webhooks**: Automatic payment status updates via Stripe webhooks
- **Customer Management**: Stripe customer creation and management

### 3. PayPal Integration for Alternative Payments
- **PayPalService**: PayPal REST API integration
- **Order Management**: Create and capture PayPal orders
- **Webhooks**: PayPal webhook handling for payment confirmations
- **OAuth Integration**: Secure PayPal API authentication

### 4. Bank Transfer Handling with Manual Approval
- **BankTransferService**: Manual bank transfer processing
- **Reference Generation**: Unique bank transfer reference codes
- **Admin Approval**: Staff can approve/reject bank transfers
- **Notification System**: Email notifications for status changes

### 5. Subscription Billing for Institutional Plans
- **Subscription Model**: Complete subscription management
- **Billing Cycles**: Monthly and yearly billing support
- **Plan Management**: Basic, Pro, and Enterprise tiers
- **Automatic Renewal**: Celery-based subscription renewal
- **Stripe Integration**: Stripe subscription management

### 6. Invoice Generation and Notification System
- **Invoice Model**: Comprehensive invoice tracking
- **PDF Generation**: ReportLab-based PDF invoice creation
- **Email Templates**: HTML and text email templates
- **Line Items**: Detailed invoice line item tracking
- **Automatic Numbering**: Sequential invoice number generation

## API Endpoints

### Payment Endpoints
- `GET /api/v1/payments/payments/` - List payments
- `POST /api/v1/payments/payments/create_course_payment/` - Create course payment
- `POST /api/v1/payments/payments/{id}/confirm_payment/` - Confirm payment
- `POST /api/v1/payments/payments/{id}/approve_bank_transfer/` - Approve bank transfer
- `POST /api/v1/payments/payments/{id}/reject_bank_transfer/` - Reject bank transfer

### Subscription Endpoints
- `GET /api/v1/payments/subscriptions/` - List subscriptions
- `POST /api/v1/payments/subscriptions/create_subscription/` - Create subscription
- `POST /api/v1/payments/subscriptions/{id}/cancel_subscription/` - Cancel subscription
- `POST /api/v1/payments/subscriptions/{id}/renew_subscription/` - Renew subscription

### Invoice Endpoints
- `GET /api/v1/payments/invoices/` - List invoices
- `POST /api/v1/payments/invoices/{id}/send_invoice/` - Send invoice
- `POST /api/v1/payments/invoices/{id}/mark_paid/` - Mark invoice as paid
- `GET /api/v1/payments/invoices/overdue_invoices/` - Get overdue invoices

### Webhook Endpoints
- `POST /api/v1/payments/webhooks/stripe/` - Stripe webhook handler
- `POST /api/v1/payments/webhooks/paypal/` - PayPal webhook handler

## Services Architecture

### Core Services
1. **PaymentService**: Main payment processing orchestrator
2. **StripeService**: Stripe API integration
3. **PayPalService**: PayPal API integration
4. **BankTransferService**: Manual bank transfer handling
5. **SubscriptionService**: Subscription management
6. **InvoiceService**: Invoice generation and management
7. **PDFInvoiceService**: PDF generation for invoices

## Background Tasks (Celery)

### Automated Tasks
- `process_overdue_invoices`: Mark overdue invoices and send reminders
- `process_subscription_renewals`: Handle subscription renewals
- `generate_monthly_invoices`: Generate monthly subscription invoices
- `cleanup_failed_payments`: Clean up old failed payments
- `send_payment_confirmation`: Send payment confirmation emails
- `send_overdue_reminder`: Send overdue invoice reminders

## Management Commands

### Available Commands
- `python manage.py process_payments --all`: Run all payment processing tasks
- `python manage.py process_payments --overdue-invoices`: Process overdue invoices
- `python manage.py process_payments --subscription-renewals`: Process renewals
- `python manage.py process_payments --cleanup-failed`: Clean up failed payments
- `python manage.py test_payment_services --all`: Test all payment integrations
- `python manage.py test_payment_services --stripe`: Test Stripe integration
- `python manage.py test_payment_services --paypal`: Test PayPal integration

## Configuration

### Environment Variables
```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-stripe-webhook-secret

# PayPal Configuration
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
PAYPAL_BASE_URL=https://api.sandbox.paypal.com  # or https://api.paypal.com for production

# Frontend URL for redirects
FRONTEND_URL=http://localhost:3000
```

### Subscription Pricing
- **Basic**: $29/month, $290/year
- **Pro**: $99/month, $990/year
- **Enterprise**: $299/month, $2990/year

## Security Features

### Implemented Security Measures
- **Webhook Verification**: Stripe and PayPal webhook signature verification
- **CSRF Protection**: CSRF exemption for webhook endpoints only
- **Tenant Isolation**: All payments are tenant-aware
- **Input Validation**: Comprehensive input validation and sanitization
- **Audit Logging**: Payment status changes are logged
- **Secure Storage**: Sensitive payment data is properly handled

## Testing

### Test Coverage
- **Model Tests**: Payment, Invoice, Subscription model functionality
- **Service Tests**: Payment processing service tests with mocking
- **API Tests**: REST API endpoint testing
- **Integration Tests**: End-to-end payment flow testing

### Running Tests
```bash
# Run all payment tests
python manage.py test apps.payments

# Run specific test classes
python manage.py test apps.payments.tests.PaymentModelTest
python manage.py test apps.payments.tests.PaymentServiceTest
```

## Email Templates

### Available Templates
- `backend/templates/emails/invoice.html` - HTML invoice email
- `backend/templates/emails/invoice.txt` - Plain text invoice email

## Database Schema

### Key Models
- **Payment**: Transaction tracking with payment method support
- **Subscription**: Institutional subscription management
- **Invoice**: Invoice generation and tracking
- **InvoiceLineItem**: Detailed invoice line items

### Indexes
- Tenant and status indexes for efficient querying
- User and payment type indexes
- Created date indexes for time-based queries
- Invoice number and due date indexes

## Requirements Satisfied

This implementation satisfies all requirements from the specification:

✅ **7.1**: Support for Stripe, PayPal, and bank transfer payment methods
✅ **7.2**: One-time payments for marketplace courses
✅ **7.3**: Recurring billing for institutional subscriptions
✅ **7.4**: Invoice generation and notification system
✅ **7.5**: Payment security and error handling
✅ **7.6**: Payment retry mechanisms and reconciliation

## Future Enhancements

### Potential Improvements
- **Refund Processing**: Automated refund handling
- **Payment Analytics**: Advanced payment reporting and analytics
- **Multi-Currency**: Support for multiple currencies
- **Payment Plans**: Installment payment options
- **Fraud Detection**: Advanced fraud detection integration
- **Mobile Payments**: Apple Pay and Google Pay integration

## Troubleshooting

### Common Issues
1. **Webhook Failures**: Check webhook endpoint URLs and signatures
2. **Payment Failures**: Review payment method configurations
3. **Invoice Generation**: Ensure ReportLab is installed for PDF generation
4. **Email Delivery**: Verify email backend configuration

### Debugging
- Enable Django logging for payment-related operations
- Use management commands to test payment service integrations
- Check Celery logs for background task execution
- Monitor webhook delivery in Stripe/PayPal dashboards