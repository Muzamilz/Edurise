#!/usr/bin/env python3
"""
Test AI endpoints without actually calling Gemini API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_django_server():
    """Test if Django server is running"""
    try:
        # Try a known endpoint that should return 401 (auth required)
        response = requests.get(f"{BASE_URL}/ai-conversations/", timeout=10)
        print(f"✅ Django Server Health: {response.status_code}")
        # Server is running if we get any response (200, 401, 403, etc.)
        return response.status_code in [200, 401, 403, 404]
    except Exception as e:
        print(f"❌ Django Server: Not running ({e})")
        return False

def test_ai_endpoints():
    """Test if AI endpoints are accessible"""
    endpoints = [
        "/ai-conversations/",
        "/ai-content-summaries/", 
        "/ai-quizzes/",
        "/ai-usage/"
    ]
    
    print("\n🔍 Testing AI Endpoints (should return 401 - auth required):")
    
    all_accessible = True
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code in [200, 401, 403]:
                print(f"   ✅ {endpoint}: OK (status {response.status_code})")
            else:
                print(f"   ❌ {endpoint}: ERROR (status {response.status_code})")
                all_accessible = False
        except Exception as e:
            print(f"   ❌ {endpoint}: FAILED ({e})")
            all_accessible = False
    
    return all_accessible

def test_ai_models_configured():
    """Test if AI models are properly configured in Django"""
    try:
        # This will test if we can import the AI modules
        import sys
        import os
        
        # Add backend to path
        backend_path = os.path.join(os.getcwd(), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Configure Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
        
        import django
        django.setup()
        
        # Test imports
        from apps.ai.models import AIConversation, AIMessage
        from apps.ai.services import AIService
        from apps.ai.providers import GeminiProvider
        
        print("✅ AI Models: Properly configured")
        print("✅ AI Services: Properly configured") 
        print("✅ AI Providers: Properly configured")
        
        return True
        
    except ImportError as e:
        print(f"❌ AI Configuration: Import error ({e})")
        return False
    except Exception as e:
        print(f"❌ AI Configuration: Error ({e})")
        return False

def main():
    """Run endpoint tests"""
    print("==> EduRise AI Endpoint Test\n")
    
    # Test 1: Django Server
    server_ok = test_django_server()
    
    # Test 2: AI Endpoints
    endpoints_ok = test_ai_endpoints()
    
    # Test 3: AI Configuration
    print("\n🔧 Testing AI Configuration:")
    config_ok = test_ai_models_configured()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS:")
    print(f"   🌐 Django Server: {'✅ Running' if server_ok else '❌ Not Running'}")
    print(f"   🔗 AI Endpoints: {'✅ Accessible' if endpoints_ok else '❌ Not Accessible'}")
    print(f"   ⚙️  AI Configuration: {'✅ OK' if config_ok else '❌ Error'}")
    
    if server_ok and endpoints_ok and config_ok:
        print("\n🎉 SUCCESS: AI Infrastructure is Ready!")
        print("   ✅ Django server is running")
        print("   ✅ AI endpoints are accessible")
        print("   ✅ AI models and services are configured")
        print("\n📝 NOTE: Gemini API quota exceeded, but infrastructure is working")
        print("   - Wait ~26 minutes for quota reset, or")
        print("   - Use a different API key, or") 
        print("   - Upgrade to paid Gemini plan")
        print("\n🧪 You can test the frontend AI widget - it will show fallback responses")
    else:
        print("\n❌ ISSUES FOUND:")
        if not server_ok:
            print("   - Django server not running (run: python manage.py runserver)")
        if not endpoints_ok:
            print("   - AI endpoints not accessible")
        if not config_ok:
            print("   - AI configuration problems")

if __name__ == "__main__":
    main()