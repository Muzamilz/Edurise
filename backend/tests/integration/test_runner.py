#!/usr/bin/env python
"""
Test runner for AI features integration tests
Executes comprehensive tests for requirements 6.1, 6.2, 6.3, 6.5
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
django.setup()

def run_ai_integration_tests():
    """Run all AI integration tests"""
    from django.test.runner import DiscoverRunner
    
    test_runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=False)
    
    # Specific test modules for AI features
    test_modules = [
        'tests.integration.test_ai_features.AITutorChatIntegrationTest',
        'tests.integration.test_ai_features.AIContentSummarizationIntegrationTest', 
        'tests.integration.test_ai_features.AIQuizGenerationIntegrationTest',
        'tests.integration.test_ai_features.AIQuotaEnforcementIntegrationTest',
        'tests.integration.test_ai_features.AIServiceIntegrationTest'
    ]
    
    print("Running AI Features Integration Tests...")
    print("=" * 60)
    
    failures = test_runner.run_tests(test_modules)
    
    if failures:
        print(f"\n❌ {failures} test(s) failed")
        return False
    else:
        print("\n✅ All AI integration tests passed!")
        return True

if __name__ == '__main__':
    success = run_ai_integration_tests()
    sys.exit(0 if success else 1)