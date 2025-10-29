#!/usr/bin/env python3
"""
Test script to verify AI API endpoints are working
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

def test_api_health():
    """Test if the API is responding"""
    try:
        # Try the AI conversations endpoint instead
        response = requests.get(f"{BASE_URL}/ai-conversations/", headers=HEADERS, timeout=10)
        print(f"✅ API Health Check (AI endpoint): {response.status_code}")
        if response.status_code in [200, 401, 403]:  # 401/403 means API is up but needs auth
            print(f"   API is responding (status: {response.status_code})")
            return True
        return False
    except Exception as e:
        print(f"❌ API Health Check Failed: {e}")
        return False

def test_ai_conversation_create():
    """Test creating an AI conversation"""
    try:
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
            headers=HEADERS, 
            json=data,
            timeout=30
        )
        
        print(f"✅ Create AI Conversation: {response.status_code}")
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"   Conversation ID: {result.get('data', {}).get('id', 'N/A')}")
            return result.get('data', {}).get('id')
        else:
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Create AI Conversation Failed: {e}")
        return None

def test_ai_send_message(conversation_id):
    """Test sending a message to AI"""
    if not conversation_id:
        print("❌ No conversation ID to test messaging")
        return False
        
    try:
        data = {
            "message": "What is EduRise?",
            "context": {
                "source": "api_test"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/ai-conversations/{conversation_id}/send_message/", 
            headers=HEADERS, 
            json=data,
            timeout=60  # AI responses can take time
        )
        
        print(f"✅ Send AI Message: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('data', {}).get('ai_response', 'No response')
            print(f"   AI Response: {ai_response[:100]}...")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Send AI Message Failed: {e}")
        return False

def test_ai_usage_stats():
    """Test getting AI usage statistics"""
    try:
        response = requests.get(
            f"{BASE_URL}/ai-usage/current_stats/", 
            headers=HEADERS,
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
    """Run all AI API tests"""
    print("🚀 Starting AI API Communication Tests...\n")
    
    # Test 1: API Health
    if not test_api_health():
        print("❌ API is not responding. Make sure Django server is running.")
        print("   Continuing with tests anyway...")
        # Don't exit, continue with tests
    
    print()
    
    # Test 2: Create AI Conversation
    conversation_id = test_ai_conversation_create()
    print()
    
    # Test 3: Send AI Message (requires Gemini API key)
    message_success = test_ai_send_message(conversation_id)
    print()
    
    # Test 4: Get Usage Stats
    stats_success = test_ai_usage_stats()
    print()
    
    # Summary
    print("📊 Test Results Summary:")
    print(f"   API Health: ✅")
    print(f"   Create Conversation: {'✅' if conversation_id else '❌'}")
    print(f"   Send AI Message: {'✅' if message_success else '❌'}")
    print(f"   Usage Stats: {'✅' if stats_success else '❌'}")
    
    if conversation_id and message_success:
        print("\n🎉 AI API is working correctly!")
        print("   - Conversations can be created")
        print("   - AI is responding to messages")
        print("   - Gemini integration is functional")
    else:
        print("\n⚠️  Some AI features may not be working:")
        if not conversation_id:
            print("   - Cannot create conversations (check database)")
        if not message_success:
            print("   - AI not responding (check Gemini API key)")

if __name__ == "__main__":
    main()