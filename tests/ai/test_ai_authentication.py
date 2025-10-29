#!/usr/bin/env python3
"""
Test AI API endpoints with proper authentication
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def get_auth_token():
    """Get authentication token for testing"""
    try:
        # Try to login with existing admin user
        login_data = {
            "email": "admin@edurise.com",
            "password": "admin123456"
        }
        
        response = requests.post(
            f"{BASE_URL}/accounts/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Authentication: Success")
            print(f"   Response data: {data}")
            
            # Try different possible token field names
            token = (data.get('access_token') or 
                    data.get('access') or 
                    data.get('token') or
                    data.get('data', {}).get('access_token') or
                    data.get('data', {}).get('access') or
                    data.get('data', {}).get('token'))
            
            if token:
                print(f"   Token found: {token[:20]}...")
                return token
            else:
                print(f"   No token found in response")
                return None
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_ai_conversation_with_auth(token):
    """Test creating an AI conversation with authentication"""
    if not token:
        print("❌ No auth token available")
        return None
        
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Tenant-ID": "81cbaac8-7f8a-4fd1-b3da-c1ee97945ea3"  # Main organization
        }
        
        data = {
            "title": "Test AI Conversation",
            "conversation_type": "general",
            "context": {
                "source": "api_test",
                "test": True
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/ai-conversations/", 
            headers=headers, 
            json=data,
            timeout=30
        )
        
        print(f"✅ Create AI Conversation: {response.status_code}")
        if response.status_code in [200, 201]:
            result = response.json()
            conversation_id = result.get('data', {}).get('id') or result.get('id')
            print(f"   Conversation ID: {conversation_id}")
            return conversation_id
        else:
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Create AI Conversation Failed: {e}")
        return None

def test_ai_usage_with_auth(token):
    """Test getting AI usage stats with authentication"""
    if not token:
        print("❌ No auth token available")
        return False
        
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Tenant-ID": "81cbaac8-7f8a-4fd1-b3da-c1ee97945ea3"  # Main organization
        }
        
        response = requests.get(
            f"{BASE_URL}/ai-usage/current_stats/", 
            headers=headers,
            timeout=30
        )
        
        print(f"✅ AI Usage Stats: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            stats = result.get('data', {}).get('stats', {})
            print(f"   Chat Usage: {stats.get('chat', {}).get('percentage_used', 0)}%")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AI Usage Stats Failed: {e}")
        return False

def main():
    """Run authenticated AI API tests"""
    print("🚀 EduRise AI API Test (With Authentication)\n")
    
    # Step 1: Get authentication token
    token = get_auth_token()
    print()
    
    if not token:
        print("❌ Cannot proceed without authentication token")
        print("   Make sure the admin user exists with correct password")
        return
    
    # Step 2: Test AI conversation creation
    conversation_id = test_ai_conversation_with_auth(token)
    print()
    
    # Step 3: Test AI usage stats
    usage_success = test_ai_usage_with_auth(token)
    print()
    
    # Summary
    print("📊 Test Results:")
    print(f"   🔐 Authentication: {'✅' if token else '❌'}")
    print(f"   💬 Create Conversation: {'✅' if conversation_id else '❌'}")
    print(f"   📊 Usage Stats: {'✅' if usage_success else '❌'}")
    
    if token and conversation_id:
        print("\n🎉 AI API is working with authentication!")
        print("   - Can authenticate successfully")
        print("   - Can create AI conversations")
        print("   - API endpoints are accessible")
    else:
        print("\n⚠️  Some issues found:")
        if not token:
            print("   - Authentication failed")
        if not conversation_id:
            print("   - Cannot create conversations")

if __name__ == "__main__":
    main()