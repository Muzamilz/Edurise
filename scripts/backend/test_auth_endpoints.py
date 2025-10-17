#!/usr/bin/env python
"""
Test script to verify all authentication endpoints are working correctly
"""
import os
import sys
import django
import requests
import json
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import Organization, UserProfile

User = get_user_model()

BASE_URL = 'http://localhost:8000/api/v1'

def test_auth_endpoints():
    """Test all authentication endpoints"""
    print("🔍 Testing Authentication Endpoints...")
    
    # Test data
    test_user_data = {
        'email': 'test@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    # 1. Test Registration
    print("\n1. Testing Registration...")
    try:
        response = requests.post(f'{BASE_URL}/accounts/auth/register/', json=test_user_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Registration successful")
            print(f"   User ID: {data.get('user', {}).get('id')}")
            access_token = data.get('tokens', {}).get('access')
            refresh_token = data.get('tokens', {}).get('refresh')
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return
    
    # 2. Test Login
    print("\n2. Testing Login...")
    try:
        login_data = {
            'email': test_user_data['email'],
            'password': test_user_data['password']
        }
        response = requests.post(f'{BASE_URL}/accounts/auth/login/', json=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login successful")
            access_token = data.get('tokens', {}).get('access')
            refresh_token = data.get('tokens', {}).get('refresh')
        else:
            print(f"   ❌ Login failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Login error: {e}")
    
    # 3. Test Token Refresh
    print("\n3. Testing Token Refresh...")
    try:
        refresh_data = {'refresh': refresh_token}
        response = requests.post(f'{BASE_URL}/accounts/auth/token/refresh/', json=refresh_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Token refresh successful")
            new_access_token = data.get('access')
            if new_access_token:
                access_token = new_access_token
        else:
            print(f"   ❌ Token refresh failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Token refresh error: {e}")
    
    # 4. Test Current User
    print("\n4. Testing Current User...")
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(f'{BASE_URL}/users/me/', headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Current user retrieved")
            print(f"   Email: {data.get('email')}")
        else:
            print(f"   ❌ Current user failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Current user error: {e}")
    
    # 5. Test User Tenants
    print("\n5. Testing User Tenants...")
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(f'{BASE_URL}/users/tenants/', headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ User tenants retrieved")
            print(f"   Tenants count: {len(data)}")
        else:
            print(f"   ❌ User tenants failed: {response.text}")
    except Exception as e:
        print(f"   ❌ User tenants error: {e}")
    
    # 6. Test Logout
    print("\n6. Testing Logout...")
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        logout_data = {'refresh_token': refresh_token}
        response = requests.post(f'{BASE_URL}/accounts/auth/logout/', json=logout_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Logout successful")
        else:
            print(f"   ❌ Logout failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Logout error: {e}")
    
    print("\n🎉 Authentication endpoint testing completed!")

if __name__ == '__main__':
    test_auth_endpoints()