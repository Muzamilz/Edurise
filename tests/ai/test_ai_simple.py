#!/usr/bin/env python3
"""
Simple test to check if AI endpoints are accessible and Gemini is working
"""
import requests
import json
import sys
import subprocess
import time

# API Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"

def create_superuser():
    """Create a superuser using Django management command"""
    try:
        print("🔧 Creating test superuser...")
        
        # Create superuser using Django management command
        result = subprocess.run([
            "python", "manage.py", "shell", "-c",
            """
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@edurise.com').exists():
    user = User.objects.create_superuser(
        email='admin@edurise.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print(f'Created superuser: {user.email}')
else:
    print('Superuser already exists')
            """
        ], cwd="backend", capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Superuser created/exists")
            return True
        else:
            print(f"❌ Failed to create superuser: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return False

def get_auth_token():
    """Get authentication token for the superuser"""
    try:
        login_data = {
            "email": "admin@edurise.com",
            "password": "admin123"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.post(
            f"{BASE_URL}/accounts/auth/login/", 
            headers=headers, 
            json=login_data,
            timeout=30
        )
        
        print(f"🔑 Login attempt: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            # Try different possible token field names
            token = (result.get('data', {}).get('access_token') or 
                    result.get('access_token') or 
                    result.get('data', {}).get('access') or
                    result.get('access'))
            
            if token:
                print(f"✅ Got auth token: {token[:20]}...")
                return token
        
        print(f"❌ Login failed: {response.text}")
        return None
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_gemini_connection():
    """Test if Gemini API key is working by making a direct test"""
    try:
        print("\n🤖 Testing Gemini API Connection...")
        
        # Import and test Gemini directly
        result = subprocess.run([
            "python", "-c",
            """
import os
import google.generativeai as genai

# Load environment
import sys
sys.path.append('backend')
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.conf import settings

if settings.GEMINI_API_KEY:
    print(f'Gemini API Key found: {settings.GEMINI_API_KEY[:20]}...')
    
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        response = model.generate_content('What is EduRise?')
        if response.text:
            print(f'✅ Gemini Response: {response.text[:100]}...')
        else:
            print('❌ Empty response from Gemini')
    except Exception as e:
        print(f'❌ Gemini API Error: {e}')
else:
    print('❌ No Gemini API key found')
            """
        ], capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
            
        return "✅ Gemini Response:" in result.stdout
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

def test_ai_endpoints(token):
    """Test AI endpoints with authentication"""
    if not token:
        print("❌ No authentication token")
        return False
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        print("\n🧪 Testing AI Endpoints...")
        
        # Test 1: List AI conversations
        response = requests.get(f"{BASE_URL}/ai-conversations/", headers=headers, timeout=30)
        print(f"   List Conversations: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return False
        
        # Test 2: Create conversation
        conv_data = {
            "title": "Test Conversation",
            "conversation_type": "general",
            "context": {"test": True}
        }
        
        response = requests.post(f"{BASE_URL}/ai-conversations/", headers=headers, json=conv_data, timeout=30)
        print(f"   Create Conversation: {response.status_code}")
        
        if response.status_code not in [200, 201]:
            print(f"   Error: {response.text}")
            return False
        
        conversation_id = response.json().get('data', {}).get('id')
        if not conversation_id:
            print("   ❌ No conversation ID returned")
            return False
        
        print(f"   ✅ Created conversation: {conversation_id}")
        
        # Test 3: Send message to AI
        message_data = {
            "message": "What is EduRise?",
            "context": {"test": True}
        }
        
        print("   🤖 Sending message to AI...")
        response = requests.post(
            f"{BASE_URL}/ai-conversations/{conversation_id}/send_message/", 
            headers=headers, 
            json=message_data, 
            timeout=60
        )
        
        print(f"   Send Message: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('data', {}).get('ai_response', '')
            metadata = result.get('data', {}).get('metadata', {})
            
            print(f"   ✅ AI Response: {ai_response[:100]}...")
            print(f"   📊 Tokens: {metadata.get('tokens_used', 0)}")
            print(f"   ⏱️  Time: {metadata.get('response_time_ms', 0)}ms")
            
            # Check if response is EduRise-focused
            if 'edurise' in ai_response.lower():
                print(f"   ✅ Response is EduRise-focused!")
                return True
            else:
                print(f"   ⚠️  Response may not be EduRise-focused")
                return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AI endpoint test failed: {e}")
        return False

def main():
    """Run comprehensive AI test"""
    print("🚀 EduRise AI Communication Test\n")
    
    # Step 1: Create superuser
    if not create_superuser():
        print("❌ Cannot create test user")
        return
    
    # Step 2: Test Gemini directly
    gemini_works = test_gemini_connection()
    
    # Step 3: Get auth token
    token = get_auth_token()
    
    # Step 4: Test AI endpoints
    if token:
        endpoints_work = test_ai_endpoints(token)
    else:
        endpoints_work = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS:")
    print(f"   🔑 Authentication: {'✅' if token else '❌'}")
    print(f"   🤖 Gemini API: {'✅' if gemini_works else '❌'}")
    print(f"   🌐 AI Endpoints: {'✅' if endpoints_work else '❌'}")
    
    if token and gemini_works and endpoints_work:
        print("\n🎉 SUCCESS: AI is fully working!")
        print("   - Authentication is working")
        print("   - Gemini API is responding")
        print("   - AI endpoints are functional")
        print("   - EduRise AI assistant is ready!")
    else:
        print("\n❌ ISSUES FOUND:")
        if not token:
            print("   - Authentication problems")
        if not gemini_works:
            print("   - Gemini API not working (check API key)")
        if not endpoints_work:
            print("   - AI endpoints not responding")

if __name__ == "__main__":
    main()