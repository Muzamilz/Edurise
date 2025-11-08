#!/usr/bin/env python
"""
Test script for authentication and role-based routing system
Run with: python manage.py shell < test_auth_roles.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import Organization, UserProfile
from apps.accounts.services import JWTAuthService
import json

User = get_user_model()

print("=" * 80)
print("AUTHENTICATION & ROLE-BASED ROUTING TEST")
print("=" * 80)

# Get or create test organization
org, created = Organization.objects.get_or_create(
    subdomain='test-org',
    defaults={
        'name': 'Test Organization',
        'is_active': True
    }
)
print(f"\n✓ Organization: {org.name} ({'created' if created else 'exists'})")

# Test users data
test_users = [
    {
        'email': 'superuser@test.com',
        'password': 'test123',
        'first_name': 'Super',
        'last_name': 'Admin',
        'is_superuser': True,
        'is_staff': True,
        'expected_role': 'superuser',
        'expected_dashboard': '/super-admin/organizations'
    },
    {
        'email': 'admin@test.com',
        'password': 'test123',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_staff': True,
        'profile_role': 'admin',
        'expected_role': 'admin',
        'expected_dashboard': '/admin/users'
    },
    {
        'email': 'teacher@test.com',
        'password': 'test123',
        'first_name': 'Teacher',
        'last_name': 'User',
        'profile_role': 'teacher',
        'is_approved_teacher': True,
        'expected_role': 'teacher',
        'expected_dashboard': '/teacher/courses'
    },
    {
        'email': 'teacher-pending@test.com',
        'password': 'test123',
        'first_name': 'Pending',
        'last_name': 'Teacher',
        'profile_role': 'teacher',
        'is_approved_teacher': False,
        'expected_role': 'teacher-pending',
        'expected_dashboard': '/teacher/application-status'
    },
    {
        'email': 'student@test.com',
        'password': 'test123',
        'first_name': 'Student',
        'last_name': 'User',
        'profile_role': 'student',
        'expected_role': 'student',
        'expected_dashboard': '/dashboard'
    }
]

print("\n" + "=" * 80)
print("CREATING TEST USERS")
print("=" * 80)

for user_data in test_users:
    email = user_data['email']
    
    # Delete existing user if exists
    User.objects.filter(email=email).delete()
    
    # Create user
    if user_data.get('is_superuser'):
        user = User.objects.create_superuser(
            email=email,
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
    else:
        user = User.objects.create_user(
            email=email,
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_staff=user_data.get('is_staff', False)
        )
    
    # Create profile if needed
    if 'profile_role' in user_data:
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            tenant=org,
            defaults={
                'role': user_data['profile_role'],
                'is_approved_teacher': user_data.get('is_approved_teacher', False)
            }
        )
    
    print(f"\n✓ Created: {user.email}")
    print(f"  - Name: {user.first_name} {user.last_name}")
    print(f"  - Superuser: {user.is_superuser}")
    print(f"  - Staff: {user.is_staff}")
    if hasattr(user, 'profiles'):
        profiles = user.profiles.all()
        if profiles:
            for p in profiles:
                print(f"  - Profile Role: {p.role} (Approved Teacher: {p.is_approved_teacher})")

print("\n" + "=" * 80)
print("TESTING JWT TOKEN GENERATION")
print("=" * 80)

for user_data in test_users:
    email = user_data['email']
    user = User.objects.get(email=email)
    
    # Generate tokens
    tokens = JWTAuthService.generate_tokens(user, org)
    
    print(f"\n{'=' * 80}")
    print(f"User: {email}")
    print(f"{'=' * 80}")
    
    # Display user info from token
    user_info = tokens['user']
    print(f"\nUser Information:")
    print(f"  - ID: {user_info['id']}")
    print(f"  - Email: {user_info['email']}")
    print(f"  - Name: {user_info['first_name']} {user_info['last_name']}")
    print(f"  - Role: {user_info['role']}")
    print(f"  - Is Teacher: {user_info['is_teacher']}")
    print(f"  - Is Approved Teacher: {user_info['is_approved_teacher']}")
    print(f"  - Is Staff: {user_info['is_staff']}")
    print(f"  - Is Superuser: {user_info['is_superuser']}")
    
    # Display tenant info
    if tokens['tenant']:
        tenant_info = tokens['tenant']
        print(f"\nTenant Information:")
        print(f"  - ID: {tenant_info['id']}")
        print(f"  - Name: {tenant_info['name']}")
        print(f"  - Subdomain: {tenant_info['subdomain']}")
        print(f"  - Role in Tenant: {tenant_info['role']}")
    
    # Verify expected role
    expected_role = user_data['expected_role']
    actual_role = user_info['role']
    
    print(f"\nRole Verification:")
    print(f"  - Expected: {expected_role}")
    print(f"  - Actual: {actual_role}")
    
    if actual_role == expected_role:
        print(f"  ✓ PASS: Role matches expected value")
    else:
        print(f"  ✗ FAIL: Role mismatch!")
    
    # Display expected dashboard
    print(f"\nExpected Dashboard Route:")
    print(f"  - {user_data['expected_dashboard']}")

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

print(f"\n✓ Created {len(test_users)} test users")
print(f"✓ Generated JWT tokens for all users")
print(f"✓ Verified role information in tokens")

print("\n" + "=" * 80)
print("LOGIN CREDENTIALS FOR TESTING")
print("=" * 80)

for user_data in test_users:
    print(f"\n{user_data['expected_role'].upper()}:")
    print(f"  Email: {user_data['email']}")
    print(f"  Password: {user_data['password']}")
    print(f"  Expected Dashboard: {user_data['expected_dashboard']}")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("""
1. Start the backend server:
   cd backend && python manage.py runserver

2. Start the frontend server:
   cd frontend && npm run dev

3. Test login with each user:
   - Login with each email/password combination
   - Verify automatic redirect to correct dashboard
   - Check that role-specific features are visible

4. Test role-based access:
   - Try accessing protected routes
   - Verify unauthorized access is blocked
   - Check that navigation items match user role
""")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
