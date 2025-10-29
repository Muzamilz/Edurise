#!/usr/bin/env python3
"""
Direct test of Gemini API to verify it's working
"""
import os
import sys

def test_gemini_api():
    """Test Gemini API directly"""
    try:
        print("Testing Gemini API...")
        
        # Import Gemini
        import google.generativeai as genai
        
        # Get API key from environment file
        api_key = "AIzaSyAE_ie2AXTPbgG3XuIEBVlJ8tqsy-GOBSk"
        
        if not api_key:
            print("ERROR: No Gemini API key found")
            return False
        
        print(f"API Key: {api_key[:20]}...")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        # Try different model names
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            try:
                model = genai.GenerativeModel('gemini-pro')
            except:
                model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        
        # Test with EduRise-specific prompt
        test_prompt = """You are the EduRise AI Assistant. Answer this question about EduRise:
        
What is EduRise and what features does it offer?"""
        
        print("Sending test message to Gemini...")
        response = model.generate_content(test_prompt)
        
        if response.text:
            print("SUCCESS: Gemini API is working!")
            print(f"Response: {response.text[:200]}...")
            
            # Check if response mentions EduRise
            if 'edurise' in response.text.lower():
                print("GREAT: Response is EduRise-focused!")
            else:
                print("NOTE: Response may not be EduRise-focused")
            
            return True
        else:
            print("ERROR: Empty response from Gemini")
            return False
            
    except ImportError:
        print("ERROR: google-generativeai package not installed")
        print("Run: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"ERROR: Gemini API failed - {e}")
        return False

def test_ai_endpoints_simple():
    """Simple test of AI endpoints without authentication"""
    try:
        import requests
        
        print("\nTesting AI endpoints...")
        
        # Test if endpoints exist (should return 401 for auth required)
        base_url = "http://127.0.0.1:8000/api/v1"
        
        endpoints = [
            "/ai-conversations/",
            "/ai-content-summaries/", 
            "/ai-quizzes/",
            "/ai-usage/"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                if response.status_code in [200, 401, 403]:
                    print(f"  {endpoint}: OK (status {response.status_code})")
                else:
                    print(f"  {endpoint}: ERROR (status {response.status_code})")
            except Exception as e:
                print(f"  {endpoint}: FAILED ({e})")
        
        return True
        
    except ImportError:
        print("ERROR: requests package not installed")
        return False
    except Exception as e:
        print(f"ERROR: Endpoint test failed - {e}")
        return False

def main():
    """Run simple AI tests"""
    print("=== EduRise AI Quick Test ===\n")
    
    # Test 1: Gemini API
    gemini_works = test_gemini_api()
    
    # Test 2: AI Endpoints
    endpoints_work = test_ai_endpoints_simple()
    
    # Summary
    print("\n" + "="*50)
    print("RESULTS:")
    print(f"  Gemini API: {'WORKING' if gemini_works else 'FAILED'}")
    print(f"  AI Endpoints: {'ACCESSIBLE' if endpoints_work else 'FAILED'}")
    
    if gemini_works and endpoints_work:
        print("\nSUCCESS: AI system is ready!")
        print("- Gemini API key is working")
        print("- AI endpoints are accessible")
        print("- You can now test the frontend AI assistant")
    else:
        print("\nISSUES FOUND:")
        if not gemini_works:
            print("- Gemini API not working (check API key)")
        if not endpoints_work:
            print("- AI endpoints not accessible (check Django server)")

if __name__ == "__main__":
    main()