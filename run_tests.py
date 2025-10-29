#!/usr/bin/env python3
"""
EduRise Test Runner
Runs various test suites for the EduRise platform
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Main test runner"""
    print("==> EduRise Test Suite Runner")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("tests"):
        print("❌ Tests directory not found. Please run from the project root.")
        sys.exit(1)
    
    # Available test suites
    test_suites = {
        "quick": [
            ("python tests/ai/test_ai_endpoints.py", "AI Endpoints Health Check"),
            ("python tests/integration/test_ai_system_complete.py", "Complete AI System Test")
        ],
        "ai": [
            ("python tests/ai/test_ai_endpoints.py", "AI Endpoints Test"),
            ("python tests/ai/test_ai_authentication.py", "AI Authentication Test"),
            ("python tests/ai/test_ai_messaging.py", "AI Messaging Test"),
            ("python tests/ai/test_gemini_direct.py", "Gemini Direct Test"),
        ],
        "integration": [
            ("python tests/integration/test_ai_system_complete.py", "Complete AI System Test")
        ],
        "all": [
            ("python tests/ai/test_ai_endpoints.py", "AI Endpoints Test"),
            ("python tests/ai/test_ai_authentication.py", "AI Authentication Test"),
            ("python tests/ai/test_ai_messaging.py", "AI Messaging Test"),
            ("python tests/ai/test_gemini_direct.py", "Gemini Direct Test"),
            ("python tests/ai/test_gemini_models.py", "Gemini Models Test"),
            ("python tests/integration/test_ai_system_complete.py", "Complete AI System Test")
        ]
    }
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [quick|ai|integration|all]")
        print("\nAvailable test suites:")
        print("  quick       - Quick health check (endpoints + complete system)")
        print("  ai          - All AI system tests")
        print("  integration - Integration tests only")
        print("  all         - All available tests")
        sys.exit(1)
    
    suite_name = sys.argv[1].lower()
    
    if suite_name not in test_suites:
        print(f"❌ Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(test_suites.keys())}")
        sys.exit(1)
    
    # Run selected test suite
    tests = test_suites[suite_name]
    passed = 0
    failed = 0
    
    print(f"Running test suite: {suite_name.upper()}")
    print(f"Total tests: {len(tests)}")
    
    for command, description in tests:
        if run_command(command, description):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total:  {passed + failed}")
    
    if failed == 0:
        print(f"\n🎉 All tests passed! EduRise is ready to go!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()