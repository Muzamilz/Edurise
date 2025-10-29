# Payment Gateway Setup Guide

This guide explains how to configure Stripe and PayPal payment gateways for the Edurise platform.

## Environment Variables

### Required Payment Environment Variables

Copy the following variables to your `.env` file and replace with your actual API keys:

```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-stripe-webhook-secret

# PayPal Configuration
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
PAYPAL_MODE=sandbox  # or 'live' for production
PAYPAL_BASE_URL=https://api.sandbox.paypal.com  # or https://api.paypal.com for production

# Payment Gateway Settings
DEFAULT_CURRENCY=USD
PAYMENT_SUCCESS_URL=http://localhost:3000/payment/success
PAYMENT_CANCEL_URL=http://localhost:3000/payment/cancel

# Admin Configuration
ADMIN_EMAIL=admin@edurise.com
DEFAULT_FROM_EMAIL=noreply@edurise.com

# Frontend URL (for payment redirects and email links)
FRONTEND_URL=http://localhost:3000
```

## Stripe Setup

### 1. Create Stripe Account
1. Go to [https://stripe.com](https://stripe.com)
2. Sign up for a new account or log in
3. Complete account verification

### 2. Get API Keys
1. Go to **Developers** → **API keys**
2. Copy the **Publishable key** (starts with `pk_test_` for test mode)
3. Copy the **Secret key** (starts with `sk_test_` for test mode)
4. Add these to your `.env` file

### 3. Set Up Webhooks
1. Go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Set endpoint URL to: `https://yourdomain.com/api/v1/payments/webhooks/stripe/`
4. Select events to listen for:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.deleted`
5. Copy the **Signing secret** (starts with `whsec_`)
6. Add to your `.env` file as `STRIPE_WEBHOOK_SECRET`

### 4. Test Mode vs Live Mode
- **Test Mode**: Use `pk_test_` and `sk_test_` keys for development
- **Live Mode**: Use `pk_live_` and `sk_live_` keys for production

## PayPal Setup

### 1. Create PayPal Developer Account
1. Go to [https://developer.paypal.com](https://developer.paypal.com)
2. Sign up or log in with your PayPal account
3. Go to **My Apps & Credentials**

### 2. Create Application
1. Click **Create App**
2. Choose **Default Application** or create a new one
3. Select **Sandbox** for development or **Live** for production
4. Choose **Merchant** as the account type

### 3. Get API Credentials
1. Copy the **Client ID**
2. Copy the **Client Secret**
3. Add these to your `.env` file

### 4. Set Up Webhooks (Optional)
1. In your app settings, go to **Webhooks**
2. Add webhook URL: `https://yourdomain.com/api/v1/payments/webhooks/paypal/`
3. Select events:
   - `PAYMENT.CAPTURE.COMPLETED`
   - `PAYMENT.CAPTURE.DENIED`

### 5. Environment Configuration
- **Sandbox**: Set `PAYPAL_MODE=sandbox` and `PAYPAL_BASE_URL=https://api.sandbox.paypal.com`
- **Live**: Set `PAYPAL_MODE=live` and `PAYPAL_BASE_URL=https://api.paypal.com`

## Testing Payment Integration

### Test Stripe Integration

```bash
# Test creating a payment intent
curl -X POST http://localhost:8000/api/v1/payments/stripe/create-payment-intent/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 29.99,
    "currency": "usd",
    "metadata": {
      "course_id": "123"
    }
  }'
```

### Test PayPal Integration

```bash
# Test creating a PayPal order
curl -X POST http://localhost:8000/api/v1/payments/paypal/create-order/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 29.99,
    "currency": "USD",
    "description": "Course enrollment"
  }'
```

## Test Credit Cards (Stripe)

Use these test card numbers in Stripe test mode:

| Card Number | Brand | Description |
|-------------|-------|-------------|
| 4242424242424242 | Visa | Succeeds |
| 4000000000000002 | Visa | Declined |
| 4000000000009995 | Visa | Insufficient funds |
| 5555555555554444 | Mastercard | Succeeds |
| 2223003122003222 | Mastercard | Succeeds |

- Use any future expiry date (e.g., 12/34)
- Use any 3-digit CVC (e.g., 123)
- Use any ZIP code (e.g., 12345)

## PayPal Test Accounts

In PayPal sandbox, you can create test accounts:

1. Go to **Sandbox** → **Accounts**
2. Create **Personal** account for buyers
3. Create **Business** account for merchants
4. Use these accounts to test payments

### Sample Test Account Credentials
- **Buyer Email**: buyer@example.com
- **Buyer Password**: password123
- **Merchant Email**: merchant@example.com
- **Merchant Password**: password123

## Production Deployment

### Security Checklist

1. **Environment Variables**
   - ✅ Use production API keys
   - ✅ Set `DEBUG=False`
   - ✅ Use HTTPS for all endpoints
   - ✅ Set proper `ALLOWED_HOSTS`

2. **Webhook Security**
   - ✅ Verify webhook signatures
   - ✅ Use HTTPS webhook URLs
   - ✅ Implement rate limiting
   - ✅ Log all webhook events

3. **Payment Security**
   - ✅ Validate amounts server-side
   - ✅ Implement fraud detection
   - ✅ Use secure payment forms
   - ✅ Store minimal payment data

### Production Environment Variables

```bash
# Production Stripe
STRIPE_PUBLISHABLE_KEY=pk_live_your-live-publishable-key
STRIPE_SECRET_KEY=sk_live_your-live-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-live-webhook-secret

# Production PayPal
PAYPAL_CLIENT_ID=your-live-paypal-client-id
PAYPAL_CLIENT_SECRET=your-live-paypal-client-secret
PAYPAL_MODE=live
PAYPAL_BASE_URL=https://api.paypal.com

# Production URLs
FRONTEND_URL=https://yourdomain.com
PAYMENT_SUCCESS_URL=https://yourdomain.com/payment/success
PAYMENT_CANCEL_URL=https://yourdomain.com/payment/cancel
```

## Troubleshooting

### Common Issues

1. **"Invalid API Key" Error**
   - Check that you're using the correct key for your environment
   - Ensure no extra spaces in the environment variable

2. **Webhook Not Receiving Events**
   - Verify webhook URL is accessible from the internet
   - Check webhook endpoint configuration in Stripe/PayPal dashboard
   - Ensure webhook secret matches

3. **PayPal "Authentication Failed"**
   - Verify client ID and secret are correct
   - Check that you're using the right base URL for your environment

4. **CORS Errors**
   - Add your frontend domain to `CORS_ALLOWED_ORIGINS`
   - Ensure `CSRF_TRUSTED_ORIGINS` includes your domain

### Debug Mode

Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

This will log all payment API requests and responses for troubleshooting.

## Support

For payment gateway specific issues:
- **Stripe Support**: [https://support.stripe.com](https://support.stripe.com)
- **PayPal Developer Support**: [https://developer.paypal.com/support](https://developer.paypal.com/support)

For Edurise platform issues:
- Check the application logs
- Review the API documentation
- Contact the development team