#!/usr/bin/env python3
"""
Comprehensive AI Features Integration Test Runner
Executes both backend Django tests and frontend Playwright tests
Requirements: 6.1, 6.2, 6.3, 6.5
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, cwd=None, description=""):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"Directory: {cwd or os.getcwd()}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {description} - TIMEOUT (exceeded 5 minutes)")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {str(e)}")
        return False

def setup_test_environment():
    """Set up the test environment"""
    print("Setting up test environment...")
    
    # Set environment variables
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.test'
    os.environ['NODE_ENV'] = 'test'
    
    return True

def run_backend_tests():
    """Run Django backend integration tests"""
    print("\n🔧 Running Backend AI Integration Tests...")
    
    backend_dir = Path(__file__).parent / "backend"
    
    # Run Django tests
    commands = [
        {
            'cmd': 'python manage.py test tests.integration.test_ai_features --verbosity=2',
            'desc': 'Django AI Integration Tests',
            'cwd': backend_dir
        }
    ]
    
    results = []
    for cmd_info in commands:
        success = run_command(
            cmd_info['cmd'], 
            cwd=cmd_info['cwd'], 
            description=cmd_info['desc']
        )
        results.append(success)
    
    return all(results)

def run_frontend_tests():
    """Run Vitest frontend integration tests"""
    print("\n🌐 Running Frontend AI Integration Tests...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Install dependencies if needed
    if not (frontend_dir / "node_modules").exists():
        print("Installing frontend dependencies...")
        run_command(
            'npm install',
            cwd=frontend_dir,
            description="Install Frontend Dependencies"
        )
    
    # Run Vitest tests
    commands = [
        {
            'cmd': 'npm run test -- tests/integration/ai-features.test.ts --run',
            'desc': 'Vitest AI Integration Tests',
            'cwd': frontend_dir
        }
    ]
    
    results = []
    for cmd_info in commands:
        success = run_command(
            cmd_info['cmd'],
            cwd=cmd_info['cwd'],
            description=cmd_info['desc']
        )
        results.append(success)
    
    return all(results)

def generate_test_report(backend_success, frontend_success):
    """Generate a comprehensive test report"""
    print("\n" + "="*80)
    print("AI FEATURES INTEGRATION TEST REPORT")
    print("="*80)
    
    print(f"\n📊 Test Results Summary:")
    print(f"Backend Tests:  {'✅ PASSED' if backend_success else '❌ FAILED'}")
    print(f"Frontend Tests: {'✅ PASSED' if frontend_success else '❌ FAILED'}")
    
    overall_success = backend_success and frontend_success
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    print(f"\n📋 Requirements Coverage:")
    print(f"✓ 6.1 - AI tutor chat functionality and context retention")
    print(f"✓ 6.2 - Content summarization accuracy and display") 
    print(f"✓ 6.3 - Quiz generation and submission process")
    print(f"✓ 6.5 - Quota enforcement and rate limiting")
    
    if not overall_success:
        print(f"\n🔍 Troubleshooting:")
        if not backend_success:
            print(f"- Check Django test configuration and database setup")
            print(f"- Verify AI service mocks are properly configured")
            print(f"- Check backend/tests/integration/test_ai_features.py for errors")
        
        if not frontend_success:
            print(f"- Check frontend development server is running")
            print(f"- Verify Playwright configuration and browser installation")
            print(f"- Check frontend/tests/integration/ai-features.spec.ts for errors")
    
    print("="*80)
    
    return overall_success

def main():
    """Main test execution function"""
    print("🚀 Starting AI Features Integration Tests")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup
    if not setup_test_environment():
        print("❌ Failed to set up test environment")
        return False
    
    # Run tests
    backend_success = run_backend_tests()
    frontend_success = run_frontend_tests()
    
    # Generate report
    overall_success = generate_test_report(backend_success, frontend_success)
    
    return overall_success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)