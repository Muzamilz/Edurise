#!/usr/bin/env python
"""
Simple test to check token refresh endpoint
"""
import requests
import json

BASE_URL = 'http://localhost:8000/api/v1'

def test_token_refresh():
    print("🔍 Testing Token Refresh Endpoint...")
    
    # First, let's register a user to get tokens
    test_user_data = {
        'email': 'testrefresh@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123',
        'first_name': 'Test',
        'last_name': 'Refresh'
    }
    
    print("\n1. Registering user...")
    try:
        response = requests.post(f'{BASE_URL}/accounts/auth/register/', json=test_user_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            refresh_token = data.get('tokens', {}).get('refresh')
            print(f"   ✅ Got refresh token: {refresh_token[:50]}...")
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return
    
    # Test different possible token refresh endpoints
    endpoints_to_test = [
        '/accounts/auth/token/refresh/',
        '/accounts/auth/refresh/',
        '/accounts/token/refresh/',
        '/auth/token/refresh/',
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n2. Testing endpoint: {endpoint}")
        try:
            refresh_data = {'refresh': refresh_token}
            response = requests.post(f'{BASE_URL}{endpoint}', json=refresh_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Token refresh successful!")
                print(f"   New access token: {data.get('access', 'N/A')[:50]}...")
                return
            else:
                print(f"   ❌ Failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n❌ No working token refresh endpoint found!")

if __name__ == '__main__':
    test_token_refresh()