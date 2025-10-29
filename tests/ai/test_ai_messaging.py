#!/usr/bin/env python3
"""
Test sending a message to AI conversation
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def get_auth_token():
    """Get authentication token"""
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
        return data.get('data', {}).get('access')
    return None

def create_conversation(token):
    """Create a new AI conversation"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Tenant-ID": "81cbaac8-7f8a-4fd1-b3da-c1ee97945ea3"
    }
    
    data = {
        "title": "Gemini API Test",
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
    
    if response.status_code in [200, 201]:
        result = response.json()
        return result.get('data', {}).get('id') or result.get('id')
    return None

def send_message(token, conversation_id):
    """Send a message to the AI"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Tenant-ID": "81cbaac8-7f8a-4fd1-b3da-c1ee97945ea3"
    }
    
    data = {
        "message": "Hello! Can you tell me what EduRise is?",
        "context": {
            "source": "api_test"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/ai-conversations/{conversation_id}/send_message/", 
        headers=headers, 
        json=data,
        timeout=60
    )
    
    return response

def main():
    print("🚀 Testing AI Message with Gemini API\n")
    
    # Get token
    token = get_auth_token()
    if not token:
        print("❌ Authentication failed")
        return
    print("✅ Authentication successful")
    
    # Create conversation
    conversation_id = create_conversation(token)
    if not conversation_id:
        print("❌ Failed to create conversation")
        return
    print(f"✅ Conversation created: {conversation_id}")
    
    # Send message
    print("📤 Sending message to AI...")
    response = send_message(token, conversation_id)
    
    print(f"📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"📋 Full Response: {json.dumps(result, indent=2)}")
        
        ai_response = result.get('ai_response', result.get('data', {}).get('ai_response', 'No response'))
        message_data = result.get('data', {}).get('message', {})
        
        print(f"🤖 AI Response: {ai_response}")
        if message_data:
            print(f"💬 Message Data: {message_data}")
        print("\n🎉 Gemini API is working!")
    else:
        print(f"❌ Error: {response.text}")
        if "quota" in response.text.lower():
            print("💡 This might be a quota issue - try again later")

if __name__ == "__main__":
    main()