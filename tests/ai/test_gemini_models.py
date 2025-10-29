#!/usr/bin/env python3
"""
Test to check available Gemini models and test the API
"""
import google.generativeai as genai

def test_gemini_models():
    """Test Gemini API and list available models"""
    try:
        # Configure API
        api_key = "AIzaSyAE_ie2AXTPbgG3XuIEBVlJ8tqsy-GOBSk"
        genai.configure(api_key=api_key)
        
        print("🔍 Listing available Gemini models...")
        
        # List available models
        models = genai.list_models()
        available_models = []
        
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
                print(f"   ✅ {model.name}")
        
        if not available_models:
            print("   ❌ No models found that support generateContent")
            return False
        
        # Test with the first available model
        model_name = available_models[0]
        print(f"\n🧪 Testing with model: {model_name}")
        
        model = genai.GenerativeModel(model_name)
        
        # Test with EduRise prompt
        prompt = """You are the EduRise AI Assistant. Answer this question about EduRise:

What is EduRise and what features does it offer for online learning?"""
        
        print("📤 Sending test message...")
        response = model.generate_content(prompt)
        
        if response.text:
            print("✅ SUCCESS: Gemini API is working!")
            print(f"📝 Response: {response.text[:200]}...")
            
            # Check if response mentions EduRise
            if 'edurise' in response.text.lower():
                print("🎯 GREAT: Response is EduRise-focused!")
            else:
                print("⚠️  NOTE: Response may not be EduRise-focused")
            
            return True
        else:
            print("❌ ERROR: Empty response from Gemini")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🚀 EduRise Gemini API Test\n")
    
    success = test_gemini_models()
    
    print("\n" + "="*50)
    if success:
        print("🎉 SUCCESS: Gemini API is working correctly!")
        print("   - API key is valid")
        print("   - Model is responding")
        print("   - Ready for EduRise integration")
    else:
        print("❌ FAILED: Gemini API is not working")
        print("   - Check API key")
        print("   - Check internet connection")
        print("   - Check model availability")