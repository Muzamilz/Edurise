# 📸 Visual Step-by-Step API Keys Setup Guide

This guide provides detailed visual instructions for getting API keys from Stripe and PayPal.

---

## 🔵 **Stripe Visual Setup Guide**

### **Step 1: Create Stripe Account**

#### **1.1 Visit Stripe Homepage**
```
🌐 Go to: https://stripe.com
👀 Look for: "Start now" or "Sign up" button (usually top-right)
🖱️ Click: The signup button
```

#### **1.2 Registration Form**
```
📧 Email: Enter your business email
🔒 Password: Create a strong password (8+ characters)
🏢 Business name: Enter your company/project name
🌍 Country: Select your country
📋 Business type: Choose appropriate type (Individual/Company)
```

#### **1.3 Email Verification**
```
📨 Check your email for verification link
🖱️ Click the verification link
✅ Account is now created
```

### **Step 2: Access Dashboard**

#### **2.1 Login to Dashboard**
```
🌐 Go to: https://dashboard.stripe.com
🔑 Login with your credentials
👀 You'll see: Main dashboard with payment overview
```

#### **2.2 Dashboard Layout**
```
📊 Left Sidebar: Navigation menu
🔄 Top Right: "Test mode" toggle (should be ON for development)
📈 Center: Payment statistics and recent activity
```

### **Step 3: Get API Keys**

#### **3.1 Navigate to API Keys**
```
📍 Location: Left sidebar → "Developers" → "API keys"
👀 You'll see: Two sections - "Standard keys" and "Restricted keys"
```

#### **3.2 Test Mode Keys**
```
🔄 Ensure: "Test mode" toggle is ON (top-right corner)
👀 You'll see two keys:

📤 Publishable key:
   - Starts with: pk_test_
   - Example: pk_test_51H7x2xKj9...
   - 🟢 Safe to use in frontend code
   
🔐 Secret key:
   - Starts with: sk_test_
   - Example: sk_test_51H7x2xKj9...
   - 🔴 Keep secret! Backend only!
   - 🖱️ Click "Reveal live key token" to see full key
```

#### **3.3 Copy Keys**
```
📋 Copy Publishable Key:
   - Click the copy icon next to publishable key
   - Paste in .env as: STRIPE_PUBLISHABLE_KEY=pk_test_...

📋 Copy Secret Key:
   - Click "Reveal live key token"
   - Click copy icon
   - Paste in .env as: STRIPE_SECRET_KEY=sk_test_...
```

### **Step 4: Setup Webhooks**

#### **4.1 Navigate to Webhooks**
```
📍 Location: Left sidebar → "Developers" → "Webhooks"
🖱️ Click: "Add endpoint" button
```

#### **4.2 Configure Webhook**
```
🌐 Endpoint URL: https://yourdomain.com/api/v1/payments/webhooks/stripe/
   (For local testing: use ngrok tunnel URL)

📋 Description: "Edurise Payment Webhooks" (optional)

🎯 Events to send:
   ✅ payment_intent.succeeded
   ✅ payment_intent.payment_failed  
   ✅ invoice.payment_succeeded
   ✅ invoice.payment_failed
   ✅ customer.subscription.deleted
```

#### **4.3 Get Webhook Secret**
```
✅ After creating webhook, click on it
👀 Look for: "Signing secret" section
🖱️ Click: "Reveal" button
📋 Copy: The webhook secret (starts with whsec_)
📝 Add to .env: STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## 🟡 **PayPal Visual Setup Guide**

### **Step 1: Access PayPal Developer Portal**

#### **1.1 Visit Developer Portal**
```
🌐 Go to: https://developer.paypal.com
👀 Look for: "Log into Dashboard" button (top-right)
🖱️ Click: "Log into Dashboard"
```

#### **1.2 Login Process**
```
🔑 Use existing PayPal account OR create new one
📧 Enter: PayPal email and password
✅ Complete: Any 2FA if enabled
```

### **Step 2: Developer Dashboard**

#### **2.1 Dashboard Overview**
```
👀 You'll see: Developer dashboard homepage
📍 Main sections:
   - My Apps & Credentials
   - Sandbox
   - Live
   - Documentation
```

#### **2.2 Navigate to Apps**
```
🖱️ Click: "My Apps & Credentials" (main navigation)
👀 You'll see: List of your applications (empty if first time)
```

### **Step 3: Create Application**

#### **3.1 Create New App**
```
🖱️ Click: "Create App" button (blue button)
📋 Fill in form:
   - App Name: "Edurise Payment System"
   - Merchant: Select your PayPal account from dropdown
```

#### **3.2 Choose Environment**
```
🧪 For Development:
   ✅ Select: "Sandbox" tab
   
🚀 For Production:
   ✅ Select: "Live" tab (requires business verification)
```

#### **3.3 Select Features**
```
📦 Product/Features:
   ✅ Check: "Express Checkout" or "PayPal Checkout"
   ✅ Check: "Subscriptions" (if you need recurring payments)
   
🖱️ Click: "Create App" button
```

### **Step 4: Get API Credentials**

#### **4.1 App Details Page**
```
✅ After creating app, you'll see app details page
👀 Look for: "SANDBOX APP CREDENTIALS" or "LIVE APP CREDENTIALS"
```

#### **4.2 Copy Credentials**
```
📋 Client ID:
   - Long string starting with letters/numbers
   - Example: AeA1QIZXiflr1_-K9UcmQzpQjbm...
   - 🖱️ Click copy icon
   - 📝 Add to .env: PAYPAL_CLIENT_ID=...

🔐 Client Secret:
   - 🖱️ Click "Show" to reveal
   - 🖱️ Click copy icon  
   - 📝 Add to .env: PAYPAL_CLIENT_SECRET=...
```

### **Step 5: Create Test Accounts (Sandbox Only)**

#### **5.1 Navigate to Sandbox Accounts**
```
📍 Location: Main navigation → "Sandbox" → "Accounts"
👀 You'll see: List of sandbox test accounts
```

#### **5.2 Create Personal Account (Buyer)**
```
🖱️ Click: "Create Account" button
📋 Fill form:
   - Account Type: "Personal"
   - Country: Select your country
   - Email: Auto-generated (e.g., sb-buyer123@personal.example.com)
   - Password: Set a test password
   - PayPal Balance: $1000 (or desired amount)
   
🖱️ Click: "Create Account"
```

#### **5.3 Create Business Account (Merchant)**
```
🖱️ Click: "Create Account" button again
📋 Fill form:
   - Account Type: "Business"  
   - Country: Select your country
   - Email: Auto-generated (e.g., sb-merchant456@business.example.com)
   - Password: Set a test password
   - PayPal Balance: $0 (merchants receive money)
   
🖱️ Click: "Create Account"
```

---

## 🔧 **Environment Configuration Visual Guide**

### **Step 1: Locate .env File**
```
📁 Navigate to: your-project/backend/
👀 Look for: .env.development or .env.example
📝 Edit with: VS Code, Notepad++, or any text editor
```

### **Step 2: Add Stripe Configuration**
```
# Add these lines to your .env file:
STRIPE_PUBLISHABLE_KEY=pk_test_[paste_your_key_here]
STRIPE_SECRET_KEY=sk_test_[paste_your_key_here]  
STRIPE_WEBHOOK_SECRET=whsec_[paste_your_webhook_secret_here]
```

### **Step 3: Add PayPal Configuration**
```
# Add these lines to your .env file:
PAYPAL_CLIENT_ID=[paste_your_client_id_here]
PAYPAL_CLIENT_SECRET=[paste_your_client_secret_here]
PAYPAL_MODE=sandbox
PAYPAL_BASE_URL=https://api.sandbox.paypal.com
```

### **Step 4: Complete Configuration**
```
# Add remaining payment settings:
DEFAULT_CURRENCY=USD
PAYMENT_SUCCESS_URL=http://localhost:3000/payment/success
PAYMENT_CANCEL_URL=http://localhost:3000/payment/cancel
ADMIN_EMAIL=admin@yourdomain.com
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
FRONTEND_URL=http://localhost:3000
```

---

## ✅ **Verification Steps**

### **Step 1: Visual Verification**
```
👀 Check your .env file looks like this:

# Stripe (Test Mode)
STRIPE_PUBLISHABLE_KEY=pk_test_51H7x2xKj9...
STRIPE_SECRET_KEY=sk_test_51H7x2xKj9...
STRIPE_WEBHOOK_SECRET=whsec_1234567890...

# PayPal (Sandbox Mode)  
PAYPAL_CLIENT_ID=AeA1QIZXiflr1_-K9UcmQzpQjbm...
PAYPAL_CLIENT_SECRET=EGnHDxD_qRPdaLdHgGYQwNEb...
PAYPAL_MODE=sandbox
PAYPAL_BASE_URL=https://api.sandbox.paypal.com
```

### **Step 2: Run Validation Script**
```
💻 Open terminal in backend folder
⌨️ Type: python validate_payment_config.py
👀 Look for: Green checkmarks ✅ for all configurations
```

### **Step 3: Test Server**
```
⌨️ Type: python manage.py runserver
👀 Look for: Server starting without errors
🌐 Visit: http://localhost:8000/api/v1/payments/
```

---

## 🚨 **Common Visual Indicators of Issues**

### **Stripe Dashboard Issues**
```
❌ Red "Test mode" indicator: Switch to test mode for development
❌ "Account not verified": Complete verification for live mode
❌ Empty API keys section: Refresh page or check account status
```

### **PayPal Dashboard Issues**
```
❌ "App not found": Make sure you're in correct environment (Sandbox/Live)
❌ "Credentials not showing": Click "Show" button for client secret
❌ "Create App disabled": Complete PayPal account verification
```

### **Environment File Issues**
```
❌ Keys not working: Check for extra spaces or missing characters
❌ Server errors: Ensure all required variables are set
❌ Validation failing: Run validation script to identify specific issues
```

---

## 🎯 **Success Indicators**

### **You'll know it's working when:**
```
✅ Stripe dashboard shows your test payments
✅ PayPal sandbox shows successful transactions  
✅ Validation script shows all green checkmarks
✅ Django server starts without payment-related errors
✅ API endpoints respond with proper JSON (not error messages)
```

### **Final Test**
```
🧪 Create a test payment:
   1. Use Stripe test card: 4242424242424242
   2. Use PayPal sandbox account credentials
   3. Check both dashboards for successful transactions
   4. Verify webhook events are received
```

**🎉 Congratulations! Your payment system is now configured and ready to use!**