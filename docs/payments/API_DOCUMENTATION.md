# Payment Gateway API Documentation

This document describes the direct Stripe and PayPal API integration endpoints.

## Base URL
All endpoints are prefixed with: `/api/v1/payments/`

## Authentication
All endpoints require authentication. Include the Authorization header:
```
Authorization: Bearer <your_token>
```

## Stripe API Endpoints

### 1. Create Payment Intent
**POST** `/api/v1/payments/stripe/create-payment-intent/`

Create a new Stripe payment intent for processing payments.

**Request Body:**
```json
{
    "amount": 29.99,
    "currency": "usd",
    "metadata": {
        "course_id": "123",
        "description": "Course enrollment"
    }
}
```

**Response:**
```json
{
    "payment_intent_id": "pi_1234567890",
    "client_secret": "pi_1234567890_secret_abc123",
    "status": "requires_payment_method",
    "amount": 2999,
    "currency": "usd"
}
```

### 2. Confirm Payment
**POST** `/api/v1/payments/stripe/confirm-payment/`

Confirm a Stripe payment intent.

**Request Body:**
```json
{
    "payment_intent_id": "pi_1234567890"
}
```

**Response:**
```json
{
    "confirmed": true,
    "payment_intent_id": "pi_1234567890"
}
```

### 3. Create Customer
**POST** `/api/v1/payments/stripe/create-customer/`

Create a new Stripe customer for subscriptions.

**Request Body:**
```json
{
    "email": "user@example.com",
    "name": "John Doe",
    "metadata": {
        "organization_id": "org_123"
    }
}
```

**Response:**
```json
{
    "customer_id": "cus_1234567890",
    "email": "user@example.com",
    "name": "John Doe"
}
```

### 4. Create Subscription
**POST** `/api/v1/payments/stripe/create-subscription/`

Create a new Stripe subscription.

**Request Body:**
```json
{
    "customer_id": "cus_1234567890",
    "price_id": "price_1234567890",
    "metadata": {
        "plan": "pro",
        "billing_cycle": "monthly"
    }
}
```

**Response:**
```json
{
    "subscription_id": "sub_1234567890",
    "status": "active",
    "current_period_start": 1640995200,
    "current_period_end": 1643673600,
    "latest_invoice": "in_1234567890"
}
```

### 5. Cancel Subscription
**POST** `/api/v1/payments/stripe/cancel-subscription/`

Cancel a Stripe subscription.

**Request Body:**
```json
{
    "subscription_id": "sub_1234567890"
}
```

**Response:**
```json
{
    "subscription_id": "sub_1234567890",
    "status": "canceled",
    "canceled_at": 1640995200
}
```

### 6. Retrieve Payment
**POST** `/api/v1/payments/stripe/retrieve-payment/`

Retrieve details of a Stripe payment intent.

**Request Body:**
```json
{
    "payment_intent_id": "pi_1234567890"
}
```

**Response:**
```json
{
    "payment_intent_id": "pi_1234567890",
    "status": "succeeded",
    "amount": 2999,
    "currency": "usd",
    "created": 1640995200,
    "metadata": {
        "course_id": "123"
    }
}
```

## PayPal API Endpoints

### 1. Create Order
**POST** `/api/v1/payments/paypal/create-order/`

Create a new PayPal order.

**Request Body:**
```json
{
    "amount": 29.99,
    "currency": "USD",
    "description": "Course enrollment",
    "custom_id": "payment_123"
}
```

**Response:**
```json
{
    "order_id": "5O190127TN364715T",
    "status": "CREATED",
    "approval_url": "https://www.paypal.com/checkoutnow?token=5O190127TN364715T",
    "links": [
        {
            "href": "https://api.paypal.com/v2/checkout/orders/5O190127TN364715T",
            "rel": "self",
            "method": "GET"
        }
    ]
}
```

### 2. Capture Order
**POST** `/api/v1/payments/paypal/capture-order/`

Capture a PayPal order after user approval.

**Request Body:**
```json
{
    "order_id": "5O190127TN364715T"
}
```

**Response:**
```json
{
    "order_id": "5O190127TN364715T",
    "captured": true
}
```

### 3. Get Order Details
**POST** `/api/v1/payments/paypal/get-order/`

Retrieve PayPal order details.

**Request Body:**
```json
{
    "order_id": "5O190127TN364715T"
}
```

**Response:**
```json
{
    "order_id": "5O190127TN364715T",
    "status": "COMPLETED",
    "intent": "CAPTURE",
    "purchase_units": [
        {
            "amount": {
                "currency_code": "USD",
                "value": "29.99"
            }
        }
    ],
    "create_time": "2023-01-01T12:00:00Z",
    "update_time": "2023-01-01T12:05:00Z"
}
```

### 4. Refund Payment
**POST** `/api/v1/payments/paypal/refund-payment/`

Process a PayPal refund.

**Request Body:**
```json
{
    "capture_id": "8MC585209K746392H",
    "amount": 29.99,
    "currency": "USD",
    "note_to_payer": "Refund for course cancellation"
}
```

**Response:**
```json
{
    "refund_id": "1JU08902781691411",
    "status": "COMPLETED",
    "amount": {
        "currency_code": "USD",
        "value": "29.99"
    },
    "create_time": "2023-01-01T12:10:00Z"
}
```

## Error Responses

All endpoints return error responses in the following format:

```json
{
    "error": "Error description"
}
```

Common HTTP status codes:
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Integration Examples

### Frontend JavaScript (Stripe)
```javascript
// Create payment intent
const response = await fetch('/api/v1/payments/stripe/create-payment-intent/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
        amount: 29.99,
        currency: 'usd',
        metadata: {
            course_id: '123'
        }
    })
});

const { client_secret } = await response.json();

// Use client_secret with Stripe.js to complete payment
```

### Frontend JavaScript (PayPal)
```javascript
// Create PayPal order
const response = await fetch('/api/v1/payments/paypal/create-order/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
        amount: 29.99,
        currency: 'USD',
        description: 'Course enrollment'
    })
});

const { approval_url } = await response.json();

// Redirect user to approval_url for PayPal payment
window.location.href = approval_url;
```

## Security Notes

1. **Never expose API keys** in frontend code
2. **Always validate** payment amounts on the server
3. **Use HTTPS** for all payment-related requests
4. **Implement rate limiting** to prevent abuse
5. **Log all payment activities** for audit purposes
6. **Verify webhook signatures** for security

## Webhook Endpoints

The system also provides webhook endpoints for payment gateway notifications:

- **Stripe Webhook:** `POST /api/v1/payments/webhooks/stripe/`
- **PayPal Webhook:** `POST /api/v1/payments/webhooks/paypal/`

These endpoints handle automatic payment status updates and should be configured in your Stripe and PayPal dashboard settings.