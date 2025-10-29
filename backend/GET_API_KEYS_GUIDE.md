# 🔑 How to Get API Keys from Stripe and PayPal

This guide walks you through getting API keys from both Stripe and PayPal payment gateways.

---

## 🔵 **Getting Stripe API Keys**

### **Step 1: Create Stripe Account**

1. **Go to Stripe Website**
   - Visit [https://stripe.com](https://stripe.com)
   - Click **"Start now"** or **"Sign up"**

2. **Sign Up Process**
   - Enter your email address
   - Create a strong password
   - Verify your email address
   - Complete the account setup form:
     - Business name
     - Country
     - Business type
     - Website (optional for testing)

3. **Account Verification**
   - For test mode: No verification needed
   - For live mode: Complete identity verification (bank details, tax info, etc.)

### **Step 2: Access the Dashboard**

1. **Login to Stripe Dashboard**
   - Go to [https://dashboard.stripe.com](https://dashboard.stripe.com)
   - Login with your credentials

2. **Dashboard Overview**
   - You'll see the main dashboard with payment overview
   - Notice the **"Test mode"** toggle in the top-right corner

### **Step 3: Get Your API Keys**

1. **Navigate to API Keys**
   - In the left sidebar, click **"Developers"**
   - Click **"API keys"**

2. **Test Mode Keys (for development)**
   - Ensure **"Test mode"** is ON (toggle in top-right)
   - You'll see two keys:
     - **Publishable key**: `pk_test_...` (safe to use in frontend)
     - **Secret key**: `sk_test_...` (keep secret, backend only)

3. **Copy Your Keys**
   ```bash
   # Test mode keys (for development)
   STRIPE_PUBLISHABLE_KEY=pk_test_51234567890abcdef...
   STRIPE_SECRET_KEY=sk_test_51234567890abcdef...
   ```

4. **Live Mode Keys (for production)**
   - Toggle **"Test mode"** to OFF
   - Complete account verification first
   - Copy the live keys:
   ```bash
   # Live mode keys (for production)
   STRIPE_PUBLISHABLE_KEY=pk_live_51234567890abcdef...
   STRIPE_SECRET_KEY=sk_live_51234567890abcdef...
   ```

### **Step 4: Set Up Webhooks**

1. **Navigate to Webhooks**
   - In **"Developers"** section, click **"Webhooks"**
   - Click **"Add endpoint"**

2. **Configure Webhook**
   - **Endpoint URL**: `https://yourdomain.com/api/v1/payments/webhooks/stripe/`
   - For local testing: Use ngrok or similar tool
   - **Events to send**:
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`
     - `customer.subscription.deleted`

3. **Get Webhook Secret**
   - After creating the webhook, click on it
   - In the **"Signing secret"** section, click **"Reveal"**
   - Copy the webhook secret: `whsec_...`
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_1234567890abcdef...
   ```

### **Step 5: Test Your Integration**

1. **Use Test Card Numbers**
   ```
   Success: 4242424242424242
   Declined: 4000000000000002
   Insufficient funds: 4000000000009995
   ```

2. **Test in Dashboard**
   - Go to **"Payments"** in dashboard
   - You should see test payments appear here

---

## 🟡 **Getting PayPal API Keys**

### **Step 1: Create PayPal Developer Account**

1. **Go to PayPal Developer Portal**
   - Visit [https://developer.paypal.com](https://developer.paypal.com)
   - Click **"Log into Dashboard"**

2. **Sign Up/Login**
   - Use your existing PayPal account OR
   - Create a new PayPal account
   - Complete the developer account setup

### **Step 2: Access Developer Dashboard**

1. **Navigate to Dashboard**
   - After login, you'll be in the PayPal Developer Dashboard
   - You'll see **"My Apps & Credentials"** section

### **Step 3: Create an Application**

1. **Create New App**
   - Click **"Create App"** button
   - Fill in the application details:
     - **App Name**: "Edurise Payment System" (or your choice)
     - **Merchant**: Select your PayPal account
     - **Platform**: Choose **"Merchant"**
     - **Product**: Select **"Express Checkout"** or **"PayPal Checkout"**

2. **Choose Environment**
   - **Sandbox**: For development and testing
   - **Live**: For production (requires business verification)

### **Step 4: Get Your API Credentials**

1. **Sandbox Credentials (for development)**
   - In **"My Apps & Credentials"**, select **"Sandbox"**
   - Click on your app name
   - You'll see:
     - **Client ID**: Your public identifier
     - **Client Secret**: Your private key (click "Show" to reveal)

   ```bash
   # Sandbox credentials (for development)
   PAYPAL_CLIENT_ID=AeA1QIZXiflr1_-K9UcmQzpQjbm...
   PAYPAL_CLIENT_SECRET=EGnHDxD_qRPdaLdHgGYQwNEb...
   PAYPAL_MODE=sandbox
   PAYPAL_BASE_URL=https://api.sandbox.paypal.com
   ```

2. **Live Credentials (for production)**
   - Switch to **"Live"** tab
   - Complete business verification first
   - Get your live credentials:
   ```bash
   # Live credentials (for production)
   PAYPAL_CLIENT_ID=AeA1QIZXiflr1_-K9UcmQzpQjbm...
   PAYPAL_CLIENT_SECRET=EGnHDxD_qRPdaLdHgGYQwNEb...
   PAYPAL_MODE=live
   PAYPAL_BASE_URL=https://api.paypal.com
   ```

### **Step 5: Create Test Accounts (Sandbox Only)**

1. **Navigate to Sandbox Accounts**
   - In the developer dashboard, click **"Sandbox"**
   - Click **"Accounts"**

2. **Create Test Accounts**
   - **Personal Account** (for buyers):
     - Click **"Create Account"**
     - Account Type: **"Personal"**
     - Country: Select your country
     - Email: Will be auto-generated (e.g., `buyer_test@example.com`)
     - Password: Set a password
     - PayPal Balance: Add test money (e.g., $1000)

   - **Business Account** (for merchants):
     - Account Type: **"Business"**
     - Similar setup process

3. **Test Account Credentials**
   ```bash
   # Example test accounts
   Buyer Email: sb-buyer123@personal.example.com
   Buyer Password: testpassword123
   
   Merchant Email: sb-merchant456@business.example.com  
   Merchant Password: testpassword456
   ```

### **Step 6: Set Up Webhooks (Optional)**

1. **Configure Webhooks**
   - In your app settings, go to **"Webhooks"**
   - Add webhook URL: `https://yourdomain.com/api/v1/payments/webhooks/paypal/`
   - Select events:
     - `PAYMENT.CAPTURE.COMPLETED`
     - `PAYMENT.CAPTURE.DENIED`

---

## 🔧 **Setting Up Your Environment**

### **Complete .env Configuration**

Create or update your `.env` file with all the keys:

```bash
# Django Configuration
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Stripe Configuration (Test Mode)
STRIPE_PUBLISHABLE_KEY=pk_test_51234567890abcdef...
STRIPE_SECRET_KEY=sk_test_51234567890abcdef...
STRIPE_WEBHOOK_SECRET=whsec_1234567890abcdef...

# PayPal Configuration (Sandbox Mode)
PAYPAL_CLIENT_ID=AeA1QIZXiflr1_-K9UcmQzpQjbm...
PAYPAL_CLIENT_SECRET=EGnHDxD_qRPdaLdHgGYQwNEb...
PAYPAL_MODE=sandbox
PAYPAL_BASE_URL=https://api.sandbox.paypal.com

# Payment Settings
DEFAULT_CURRENCY=USD
PAYMENT_SUCCESS_URL=http://localhost:3000/payment/success
PAYMENT_CANCEL_URL=http://localhost:3000/payment/cancel

# Admin Configuration
ADMIN_EMAIL=admin@yourdomain.com
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
FRONTEND_URL=http://localhost:3000
```

---

## 🧪 **Testing Your Setup**

### **1. Validate Configuration**
```bash
cd backend
python validate_payment_config.py
```

### **2. Test Stripe Integration**
```bash
# Test creating a payment intent
curl -X POST http://localhost:8000/api/v1/payments/stripe/create-payment-intent/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 10.00,
    "currency": "usd"
  }'
```

### **3. Test PayPal Integration**
```bash
# Test creating a PayPal order
curl -X POST http://localhost:8000/api/v1/payments/paypal/create-order/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 10.00,
    "currency": "USD",
    "description": "Test payment"
  }'
```

---

## 🚨 **Security Best Practices**

### **1. Key Management**
- ✅ **Never commit API keys to version control**
- ✅ **Use environment variables for all keys**
- ✅ **Use test keys for development**
- ✅ **Rotate keys regularly in production**

### **2. Environment Separation**
```bash
# Development
STRIPE_SECRET_KEY=sk_test_...
PAYPAL_MODE=sandbox

# Production  
STRIPE_SECRET_KEY=sk_live_...
PAYPAL_MODE=live
```

### **3. Access Control**
- ✅ **Limit API key permissions in dashboards**
- ✅ **Use webhook secrets for verification**
- ✅ **Implement rate limiting**
- ✅ **Monitor API usage**

---

## 🔍 **Troubleshooting Common Issues**

### **Stripe Issues**

1. **"Invalid API Key" Error**
   ```
   Problem: Wrong key format or environment mismatch
   Solution: Check key starts with sk_test_ or sk_live_
   ```

2. **"Test mode keys cannot be used in live mode"**
   ```
   Problem: Using test keys in production
   Solution: Switch to live keys after account verification
   ```

### **PayPal Issues**

1. **"Authentication Failed"**
   ```
   Problem: Wrong client ID/secret combination
   Solution: Verify credentials in PayPal dashboard
   ```

2. **"Invalid environment"**
   ```
   Problem: Sandbox credentials used with live URL
   Solution: Match PAYPAL_MODE with PAYPAL_BASE_URL
   ```

### **General Issues**

1. **Webhook not receiving events**
   ```
   Problem: Webhook URL not accessible
   Solution: Use ngrok for local testing, ensure HTTPS in production
   ```

2. **CORS errors**
   ```
   Problem: Frontend domain not allowed
   Solution: Add domain to CORS_ALLOWED_ORIGINS
   ```

---

## 📞 **Getting Help**

### **Stripe Support**
- **Documentation**: [https://stripe.com/docs](https://stripe.com/docs)
- **Support**: [https://support.stripe.com](https://support.stripe.com)
- **Community**: [https://github.com/stripe](https://github.com/stripe)

### **PayPal Support**
- **Documentation**: [https://developer.paypal.com/docs](https://developer.paypal.com/docs)
- **Support**: [https://developer.paypal.com/support](https://developer.paypal.com/support)
- **Community**: [https://github.com/paypal](https://github.com/paypal)

---

## ✅ **Quick Checklist**

Before going live, ensure you have:

- [ ] Stripe account verified
- [ ] PayPal business account verified  
- [ ] Test payments working in sandbox/test mode
- [ ] Webhooks configured and tested
- [ ] Live API keys obtained
- [ ] Environment variables properly set
- [ ] SSL certificate installed (HTTPS)
- [ ] Payment flows tested end-to-end
- [ ] Error handling implemented
- [ ] Monitoring and logging set up

**You're now ready to accept payments! 🎉**