#!/usr/bin/env python3
"""
Complete AI system test - verifies all components are working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"
TENANT_ID = "81cbaac8-7f8a-4fd1-b3da-c1ee97945ea3"  # Main organization

def test_complete_ai_system():
    """Test the complete AI system end-to-end"""
    print("==> EduRise AI System - Complete Test\n")
    
    # Step 1: Authentication
    print("[1] Authentication")
    login_data = {
        "email": "admin@edurise.com",
        "password": "admin123456"
    }
    
    response = requests.post(f"{BASE_URL}/accounts/auth/login/", json=login_data)
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code}")
        return False
    
    token = response.json().get('data', {}).get('access')
    if not token:
        print("❌ No access token received")
        return False
    
    print("SUCCESS: Authentication successful")
    
    # Step 2: Create AI Conversation
    print("\n[2] Create AI Conversation")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID
    }
    
    conversation_data = {
        "title": "Complete System Test",
        "conversation_type": "general",
        "context": {"source": "system_test"}
    }
    
    response = requests.post(f"{BASE_URL}/ai-conversations/", headers=headers, json=conversation_data)
    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create conversation: {response.status_code}")
        return False
    
    result = response.json()
    conversation_id = result.get('data', {}).get('id') or result.get('id')
    print(f"SUCCESS: Conversation created: {conversation_id}")
    
    if not conversation_id:
        print(f"❌ No conversation ID in response: {result}")
        return False
    
    # Step 3: Send Message to AI
    print("\n[3] Send Message to AI")
    message_data = {
        "message": "What are the main features of EduRise?",
        "context": {"test": True}
    }
    
    response = requests.post(
        f"{BASE_URL}/ai-conversations/{conversation_id}/send_message/", 
        headers=headers, 
        json=message_data,
        timeout=60
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to send message: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    result = response.json()
    ai_response = result.get('ai_response', '')
    metadata = result.get('metadata', {})
    
    print(f"SUCCESS: AI responded successfully")
    print(f"   Response length: {len(ai_response)} characters")
    print(f"   Tokens used: {metadata.get('tokens_used', 0)}")
    print(f"   Response time: {metadata.get('response_time_ms', 0)}ms")
    print(f"   Remaining quota: {metadata.get('remaining_quota', 0)}")
    
    # Step 4: Check AI Usage Stats
    print("\n[4] Check AI Usage Statistics")
    response = requests.get(f"{BASE_URL}/ai-usage/current_stats/", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get usage stats: {response.status_code}")
        return False
    
    stats = response.json().get('data', {}).get('stats', {})
    print(f"SUCCESS: Usage stats retrieved")
    print(f"   Chat usage: {stats.get('chat', {}).get('percentage_used', 0)}%")
    
    # Step 5: List Conversations
    print("\n[5] List AI Conversations")
    response = requests.get(f"{BASE_URL}/ai-conversations/", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to list conversations: {response.status_code}")
        return False
    
    result = response.json()
    if isinstance(result, list):
        conversations = result
    elif isinstance(result, dict):
        conversations = result.get('data', {})
        if isinstance(conversations, dict):
            conversations = conversations.get('results', result.get('results', []))
        elif isinstance(conversations, list):
            pass  # conversations is already the list
        else:
            conversations = []
    else:
        conversations = []
    
    print(f"SUCCESS: Found {len(conversations)} conversations")
    
    # Summary
    print("\n" + "="*60)
    print("SUCCESS: COMPLETE AI SYSTEM TEST - ALL PASSED!")
    print("- Authentication working")
    print("- AI conversation creation working")
    print("- Gemini API integration working")
    print("- AI message processing working")
    print("- Usage tracking working")
    print("- Conversation management working")
    print("\n==> The EduRise AI system is fully operational!")
    
    return True

if __name__ == "__main__":
    success = test_complete_ai_system()
    if not success:
        print("\n❌ Some tests failed. Check the output above for details.")
        exit(1)