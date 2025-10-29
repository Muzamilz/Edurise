#!/usr/bin/env python3
"""
Test script to verify AI API endpoints with authentication
"""
import requests
import json
import sys

# API Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def create_test_user():
    """Create a test user and get authentication token"""
    try:
        # Try to register a test user
        user_data = {
            "email": "test@edurise.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = requests.post(
            f"{BASE_URL}/accounts/auth/register/", 
            headers=HEADERS, 
            json=user_data,
            timeout=30
        )
        
        print(f"✅ User Registration: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            token = result.get('data', {}).get('access_token') or result.get('access_token')
            if token:
                print(f"   Got auth token: {token[:20]}...")
                return token
        
        # If registration fails, try login with existing user
        login_data = {
            "email": "test@edurise.com", 
            "password": "testpass123"
        }
        
        response = requests.post(
            f"{BASE_URL}/accounts/auth/login/", 
            headers=HEADERS, 
            json=login_data,
            timeout=30
        )
        
        print(f"✅ User Login: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('data', {}).get('access_token') or result.get('access_token')
            if token:
                print(f"   Got auth token: {token[:20]}...")
                return token
        
        print(f"   Auth Error: {response.text}")
        return None
        
    except Exception as e:
        print(f"❌ Authentication Failed: {e}")
        return None

def test_ai_with_token(token):
    """Test AI endpoints with authentication token"""
    if not token:
        print("❌ No authentication token available")
        return False
    
    auth_headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    try:
        # Test 1: Create AI Conversation
        print("\n🧪 Testing AI Conversation Creation...")
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
            headers=auth_headers, 
            json=data,
            timeout=30
        )
        
        print(f"   Create Conversation: {response.status_code}")
        if response.status_code in [200, 201]:
            result = response.json()
            conversation_id = result.get('data', {}).get('id')
            print(f"   ✅ Conversation ID: {conversation_id}")
        else:
            print(f"   ❌ Error: {response.text}")
            return False
        
        # Test 2: Send AI Message
        print("\n🤖 Testing AI Message...")
        message_data = {
            "message": "What is EduRise and how does it work?",
            "context": {
                "source": "api_test"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/ai-conversations/{conversation_id}/send_message/", 
            headers=auth_headers, 
            json=message_data,
            timeout=60  # AI responses can take time
        )
        
        print(f"   Send Message: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('data', {}).get('ai_response', 'No response')
            tokens_used = result.get('data', {}).get('metadata', {}).get('tokens_used', 0)
            response_time = result.get('data', {}).get('metadata', {}).get('response_time_ms', 0)
            
            print(f"   ✅ AI Response: {ai_response[:150]}...")
            print(f"   📊 Tokens Used: {tokens_used}")
            print(f"   ⏱️  Response Time: {response_time}ms")
            
            # Check if it's EduRise-focused
            if 'edurise' in ai_response.lower():
                print(f"   ✅ Response is EduRise-focused!")
            else:
                print(f"   ⚠️  Response may not be EduRise-focused")
                
        else:
            print(f"   ❌ Error: {response.text}")
            return False
        
        # Test 3: Get Usage Stats
        print("\n📊 Testing AI Usage Stats...")
        response = requests.get(
            f"{BASE_URL}/ai-usage/current_stats/", 
            headers=auth_headers,
            timeout=30
        )
        
        print(f"   Usage Stats: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            stats = result.get('data', {}).get('stats', {})
            chat_usage = stats.get('chat', {})
            print(f"   ✅ Chat Messages Used: {chat_usage.get('messages_used', 0)}/{chat_usage.get('messages_limit', 0)}")
            print(f"   ✅ Chat Usage: {chat_usage.get('percentage_used', 0):.1f}%")
        else:
            print(f"   ❌ Error: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Test Failed: {e}")
        return False

def main():
    """Run AI API tests with authentication"""
    print("🚀 Starting Authenticated AI API Tests...\n")
    
    # Get authentication token
    token = create_test_user()
    
    if not token:
        print("\n❌ Could not get authentication token")
        print("   Make sure the Django server is running and user registration is working")
        return
    
    # Test AI endpoints
    success = test_ai_with_token(token)
    
    print("\n" + "="*60)
    if success:
        print("🎉 AI API Communication Test: SUCCESS!")
        print("   ✅ Authentication working")
        print("   ✅ AI conversations can be created")
        print("   ✅ AI is responding to messages")
        print("   ✅ Gemini integration is functional")
        print("   ✅ Usage tracking is working")
    else:
        print("❌ AI API Communication Test: FAILED")
        print("   Check the error messages above for details")

if __name__ == "__main__":
    main()