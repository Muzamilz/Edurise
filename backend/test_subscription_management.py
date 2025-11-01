#!/usr/bin/env python3
"""
Test script for organization subscription management functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import Organization, UserProfile
from apps.payments.models import SubscriptionPlan, Subscription
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def create_test_data():
    """Create test data for subscription management"""
    print("Creating test data...")
    
    # Create superuser
    superuser, created = User.objects.get_or_create(
        email='superadmin@test.com',
        defaults={
            'first_name': 'Super',
            'last_name': 'Admin',
            'is_superuser': True,
            'is_staff': True
        }
    )
    if created:
        superuser.set_password('password123')
        superuser.save()
        print(f"✅ Created superuser: {superuser.email}")
    else:
        print(f"✅ Superuser already exists: {superuser.email}")
    
    # Create test organization
    org, created = Organization.objects.get_or_create(
        subdomain='testorg',
        defaults={
            'name': 'Test Organization',
            'is_active': True
        }
    )
    if created:
        print(f"✅ Created organization: {org.name}")
    else:
        print(f"✅ Organization already exists: {org.name}")
    
    # Create subscription plans
    plans_data = [
        {
            'name': 'basic',
            'display_name': 'Basic Plan',
            'description': 'Perfect for small teams getting started',
            'price_monthly': 29.99,
            'price_yearly': 299.99,
            'max_users': 10,
            'max_courses': 5,
            'max_storage_gb': 10,
            'ai_quota_monthly': 100,
        },
        {
            'name': 'pro',
            'display_name': 'Pro Plan',
            'description': 'Great for growing organizations',
            'price_monthly': 79.99,
            'price_yearly': 799.99,
            'max_users': 50,
            'max_courses': 25,
            'max_storage_gb': 100,
            'ai_quota_monthly': 500,
            'has_analytics': True,
            'has_api_access': True,
            'is_popular': True,
        },
        {
            'name': 'enterprise',
            'display_name': 'Enterprise Plan',
            'description': 'For large organizations with advanced needs',
            'price_monthly': 199.99,
            'price_yearly': 1999.99,
            'max_users': 500,
            'max_courses': 100,
            'max_storage_gb': 1000,
            'ai_quota_monthly': 2000,
            'has_analytics': True,
            'has_api_access': True,
            'has_white_labeling': True,
            'has_priority_support': True,
            'has_custom_integrations': True,
        }
    ]
    
    for plan_data in plans_data:
        plan, created = SubscriptionPlan.objects.get_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        if created:
            print(f"✅ Created subscription plan: {plan.display_name}")
        else:
            print(f"✅ Subscription plan already exists: {plan.display_name}")
    
    # Create initial subscription for organization (basic plan)
    basic_plan = SubscriptionPlan.objects.get(name='basic')
    subscription, created = Subscription.objects.get_or_create(
        organization=org,
        defaults={
            'plan': basic_plan,
            'billing_cycle': 'monthly',
            'amount': basic_plan.price_monthly,
            'current_period_start': timezone.now(),
            'current_period_end': timezone.now() + timedelta(days=30),
            'tenant': org
        }
    )
    if created:
        print(f"✅ Created subscription: {org.name} -> {basic_plan.display_name}")
    else:
        print(f"✅ Subscription already exists: {org.name} -> {subscription.plan.display_name}")
    
    print("\n🎉 Test data created successfully!")
    print(f"Superuser: {superuser.email} (password: password123)")
    print(f"Organization: {org.name} ({org.subdomain})")
    print(f"Current Plan: {subscription.plan.display_name}")
    print(f"Available Plans: {', '.join([p.display_name for p in SubscriptionPlan.objects.all()])}")

def test_api_endpoints():
    """Test the API endpoints"""
    print("\n🧪 Testing API endpoints...")
    
    from django.test import Client
    from django.contrib.auth import authenticate
    
    client = Client()
    
    # Login as superuser
    superuser = User.objects.get(email='superadmin@test.com')
    client.force_login(superuser)
    
    org = Organization.objects.get(subdomain='testorg')
    
    # Test subscription info endpoint
    print("Testing subscription info endpoint...")
    response = client.get(f'/api/v1/organizations/{org.id}/subscription-info/')
    if response.status_code == 200:
        print("✅ Subscription info endpoint works")
        data = response.json()
        print(f"   Current plan: {data.get('data', {}).get('current_plan', {}).get('display_name', 'None')}")
        print(f"   Available plans: {len(data.get('data', {}).get('available_plans', []))}")
    else:
        print(f"❌ Subscription info endpoint failed: {response.status_code}")
        print(f"   Response: {response.content.decode()}")
    
    # Test plan change endpoint
    print("Testing plan change endpoint...")
    pro_plan = SubscriptionPlan.objects.get(name='pro')
    response = client.post(f'/api/v1/organizations/{org.id}/change-subscription-plan/', {
        'plan_id': str(pro_plan.id)
    }, content_type='application/json')
    
    if response.status_code == 200:
        print("✅ Plan change endpoint works")
        data = response.json()
        print(f"   Changed to: {data.get('data', {}).get('new_plan', 'Unknown')}")
    else:
        print(f"❌ Plan change endpoint failed: {response.status_code}")
        print(f"   Response: {response.content.decode()}")

if __name__ == '__main__':
    print("🚀 Testing Organization Subscription Management")
    print("=" * 50)
    
    try:
        create_test_data()
        test_api_endpoints()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)