#!/usr/bin/env python
"""
Payment Configuration Validation Script

This script validates that all required payment environment variables are properly configured.
Run this script to check your payment gateway setup before deploying.

Usage:
    python validate_payment_config.py
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

try:
    import django
    django.setup()
    from django.conf import settings
except ImportError as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)


def validate_stripe_config():
    """Validate Stripe configuration"""
    print("\n🔵 Validating Stripe Configuration...")
    
    issues = []
    
    # Check required Stripe settings
    if not settings.STRIPE_PUBLISHABLE_KEY:
        issues.append("STRIPE_PUBLISHABLE_KEY is not set")
    elif not settings.STRIPE_PUBLISHABLE_KEY.startswith(('pk_test_', 'pk_live_')):
        issues.append("STRIPE_PUBLISHABLE_KEY format is invalid")
    
    if not settings.STRIPE_SECRET_KEY:
        issues.append("STRIPE_SECRET_KEY is not set")
    elif not settings.STRIPE_SECRET_KEY.startswith(('sk_test_', 'sk_live_')):
        issues.append("STRIPE_SECRET_KEY format is invalid")
    
    if not settings.STRIPE_WEBHOOK_SECRET:
        issues.append("STRIPE_WEBHOOK_SECRET is not set (optional but recommended)")
    elif not settings.STRIPE_WEBHOOK_SECRET.startswith('whsec_'):
        issues.append("STRIPE_WEBHOOK_SECRET format is invalid")
    
    # Check key consistency (test vs live)
    if settings.STRIPE_PUBLISHABLE_KEY and settings.STRIPE_SECRET_KEY:
        pub_is_test = settings.STRIPE_PUBLISHABLE_KEY.startswith('pk_test_')
        secret_is_test = settings.STRIPE_SECRET_KEY.startswith('sk_test_')
        
        if pub_is_test != secret_is_test:
            issues.append("Stripe publishable and secret keys are from different environments (test/live)")
    
    if issues:
        print("❌ Stripe configuration issues:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        env_type = "Test" if settings.STRIPE_PUBLISHABLE_KEY.startswith('pk_test_') else "Live"
        print(f"✅ Stripe configuration is valid ({env_type} mode)")
        return True


def validate_paypal_config():
    """Validate PayPal configuration"""
    print("\n🟡 Validating PayPal Configuration...")
    
    issues = []
    
    # Check required PayPal settings
    if not settings.PAYPAL_CLIENT_ID:
        issues.append("PAYPAL_CLIENT_ID is not set")
    
    if not settings.PAYPAL_CLIENT_SECRET:
        issues.append("PAYPAL_CLIENT_SECRET is not set")
    
    if not settings.PAYPAL_BASE_URL:
        issues.append("PAYPAL_BASE_URL is not set")
    elif settings.PAYPAL_BASE_URL not in ['https://api.sandbox.paypal.com', 'https://api.paypal.com']:
        issues.append("PAYPAL_BASE_URL should be either sandbox or live PayPal API URL")
    
    if not hasattr(settings, 'PAYPAL_MODE') or settings.PAYPAL_MODE not in ['sandbox', 'live']:
        issues.append("PAYPAL_MODE should be either 'sandbox' or 'live'")
    
    # Check consistency between mode and base URL
    if hasattr(settings, 'PAYPAL_MODE') and settings.PAYPAL_BASE_URL:
        if settings.PAYPAL_MODE == 'sandbox' and 'sandbox' not in settings.PAYPAL_BASE_URL:
            issues.append("PAYPAL_MODE is 'sandbox' but PAYPAL_BASE_URL is not sandbox URL")
        elif settings.PAYPAL_MODE == 'live' and 'sandbox' in settings.PAYPAL_BASE_URL:
            issues.append("PAYPAL_MODE is 'live' but PAYPAL_BASE_URL is sandbox URL")
    
    if issues:
        print("❌ PayPal configuration issues:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        mode = getattr(settings, 'PAYPAL_MODE', 'unknown')
        print(f"✅ PayPal configuration is valid ({mode} mode)")
        return True


def validate_general_config():
    """Validate general payment configuration"""
    print("\n⚙️  Validating General Payment Configuration...")
    
    issues = []
    warnings = []
    
    # Check currency
    if not hasattr(settings, 'DEFAULT_CURRENCY') or not settings.DEFAULT_CURRENCY:
        warnings.append("DEFAULT_CURRENCY is not set, defaulting to USD")
    
    # Check URLs
    if not settings.FRONTEND_URL:
        issues.append("FRONTEND_URL is not set")
    
    if not hasattr(settings, 'PAYMENT_SUCCESS_URL') or not settings.PAYMENT_SUCCESS_URL:
        warnings.append("PAYMENT_SUCCESS_URL is not set")
    
    if not hasattr(settings, 'PAYMENT_CANCEL_URL') or not settings.PAYMENT_CANCEL_URL:
        warnings.append("PAYMENT_CANCEL_URL is not set")
    
    # Check admin email
    if not hasattr(settings, 'ADMIN_EMAIL') or not settings.ADMIN_EMAIL:
        warnings.append("ADMIN_EMAIL is not set")
    
    if not settings.DEFAULT_FROM_EMAIL:
        warnings.append("DEFAULT_FROM_EMAIL is not set")
    
    if issues:
        print("❌ General configuration issues:")
        for issue in issues:
            print(f"   • {issue}")
    
    if warnings:
        print("⚠️  General configuration warnings:")
        for warning in warnings:
            print(f"   • {warning}")
    
    if not issues:
        print("✅ General payment configuration is valid")
    
    return len(issues) == 0


def test_stripe_connection():
    """Test Stripe API connection"""
    print("\n🔵 Testing Stripe API Connection...")
    
    if not settings.STRIPE_SECRET_KEY:
        print("❌ Cannot test Stripe connection: STRIPE_SECRET_KEY not set")
        return False
    
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Test API connection by retrieving account info
        account = stripe.Account.retrieve()
        print(f"✅ Stripe connection successful")
        print(f"   Account ID: {account.id}")
        print(f"   Country: {account.country}")
        print(f"   Currency: {account.default_currency}")
        return True
        
    except stripe.error.AuthenticationError:
        print("❌ Stripe authentication failed: Invalid API key")
        return False
    except stripe.error.StripeError as e:
        print(f"❌ Stripe API error: {e}")
        return False
    except ImportError:
        print("❌ Stripe library not installed: pip install stripe")
        return False
    except Exception as e:
        print(f"❌ Unexpected error testing Stripe: {e}")
        return False


def test_paypal_connection():
    """Test PayPal API connection"""
    print("\n🟡 Testing PayPal API Connection...")
    
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        print("❌ Cannot test PayPal connection: Client credentials not set")
        return False
    
    try:
        import requests
        import base64
        
        # Test PayPal authentication
        credentials = f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = 'grant_type=client_credentials'
        url = f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token"
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ PayPal connection successful")
            print(f"   Token type: {token_data.get('token_type')}")
            print(f"   Expires in: {token_data.get('expires_in')} seconds")
            return True
        else:
            print(f"❌ PayPal authentication failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ PayPal connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error testing PayPal: {e}")
        return False


def main():
    """Main validation function"""
    print("🚀 Payment Gateway Configuration Validator")
    print("=" * 50)
    
    # Validate configurations
    stripe_valid = validate_stripe_config()
    paypal_valid = validate_paypal_config()
    general_valid = validate_general_config()
    
    # Test connections if configurations are valid
    stripe_connected = False
    paypal_connected = False
    
    if stripe_valid:
        stripe_connected = test_stripe_connection()
    
    if paypal_valid:
        paypal_connected = test_paypal_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Validation Summary:")
    print(f"   Stripe Config: {'✅' if stripe_valid else '❌'}")
    print(f"   Stripe Connection: {'✅' if stripe_connected else '❌'}")
    print(f"   PayPal Config: {'✅' if paypal_valid else '❌'}")
    print(f"   PayPal Connection: {'✅' if paypal_connected else '❌'}")
    print(f"   General Config: {'✅' if general_valid else '❌'}")
    
    all_valid = stripe_valid and paypal_valid and general_valid
    all_connected = stripe_connected and paypal_connected
    
    if all_valid and all_connected:
        print("\n🎉 All payment configurations are valid and connections successful!")
        print("   Your payment system is ready for use.")
        return 0
    elif all_valid:
        print("\n⚠️  Configurations are valid but some connections failed.")
        print("   Check your internet connection and API credentials.")
        return 1
    else:
        print("\n❌ Some configurations are invalid.")
        print("   Please fix the issues above before proceeding.")
        return 2


if __name__ == '__main__':
    sys.exit(main())