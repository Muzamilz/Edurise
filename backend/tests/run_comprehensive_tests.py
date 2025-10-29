#!/usr/bin/env python
"""
Comprehensive test runner for EduRise platform.
Runs all test suites including unit tests, integration tests, performance tests, and end-to-end tests.
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


class ComprehensiveTestRunner:
    """Comprehensive test runner for all test suites"""
    
    def __init__(self):
        self.test_suites = {
            'unit': {
                'description': 'Unit Tests - Test individual components and functions',
                'patterns': [
                    'apps.*.tests.test_models',
                    'apps.*.tests.test_views', 
                    'apps.*.tests.test_serializers',
                    'apps.*.tests.test_services',
                    'apps.accounts.tests.test_enhanced_views',
                    'apps.payments.tests.test_views',
                    'apps.payments.tests.test_models',
                    'apps.courses.tests.test_views',
                    'apps.courses.tests.test_models',
                    'apps.files.tests.test_views',
                    'apps.ai.tests.test_views'
                ]
            },
            'integration': {
                'description': 'Integration Tests - Test component interactions and workflows',
                'patterns': [
                    'tests.test_complete_user_workflows',
                    'tests.test_external_service_integrations',
                    'tests.test_centralized_api_integration',
                    'tests.test_course_management_integration',
                    'tests.test_live_class_integration'
                ]
            },
            'performance': {
                'description': 'Performance Tests - Test system performance and scalability',
                'patterns': [
                    'tests.test_performance'
                ]
            },
            'e2e': {
                'description': 'End-to-End Tests - Test complete user journeys',
                'patterns': [
                    'tests.test_end_to_end'
                ]
            }
        }
        
        self.results = {}
    
    def run_test_suite(self, suite_name, verbose=False, failfast=False):
        """Run a specific test suite"""
        if suite_name not in self.test_suites:
            print(f"Unknown test suite: {suite_name}")
            return False
        
        suite = self.test_suites[suite_name]
        print(f"\n{'='*60}")
        print(f"Running {suite_name.upper()} TESTS")
        print(f"Description: {suite['description']}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # Build test command
        cmd = ['python', 'manage.py', 'test']
        
        if verbose:
            cmd.append('--verbosity=2')
        else:
            cmd.append('--verbosity=1')
        
        if failfast:
            cmd.append('--failfast')
        
        # Add test patterns
        for pattern in suite['patterns']:
            cmd.append(pattern)
        
        # Run tests
        try:
            result = subprocess.run(
                cmd,
                cwd=backend_dir,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            
            self.results[suite_name] = {
                'success': success,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
            print(f"\n{suite_name.upper()} Tests completed in {duration:.2f} seconds")
            
            if success:
                print(f"✅ {suite_name.upper()} TESTS PASSED")
            else:
                print(f"❌ {suite_name.upper()} TESTS FAILED")
                if verbose:
                    print("STDOUT:", result.stdout)
                    print("STDERR:", result.stderr)
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"❌ {suite_name.upper()} TESTS TIMED OUT")
            self.results[suite_name] = {
                'success': False,
                'duration': 1800,
                'error': 'Timeout'
            }
            return False
        
        except Exception as e:
            print(f"❌ {suite_name.upper()} TESTS ERROR: {str(e)}")
            self.results[suite_name] = {
                'success': False,
                'duration': 0,
                'error': str(e)
            }
            return False
    
    def run_all_tests(self, verbose=False, failfast=False, skip_suites=None):
        """Run all test suites"""
        skip_suites = skip_suites or []
        
        print("🚀 Starting Comprehensive Test Suite")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        overall_start = time.time()
        all_passed = True
        
        for suite_name in self.test_suites.keys():
            if suite_name in skip_suites:
                print(f"\n⏭️  Skipping {suite_name.upper()} tests")
                continue
            
            success = self.run_test_suite(suite_name, verbose, failfast)
            if not success:
                all_passed = False
                if failfast:
                    print(f"\n🛑 Stopping due to {suite_name} test failures (--failfast enabled)")
                    break
        
        overall_end = time.time()
        total_duration = overall_end - overall_start
        
        self.print_summary(total_duration, all_passed)
        
        return all_passed
    
    def print_summary(self, total_duration, all_passed):
        """Print test results summary"""
        print(f"\n{'='*60}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*60}")
        
        for suite_name, result in self.results.items():
            status = "✅ PASSED" if result['success'] else "❌ FAILED"
            duration = result.get('duration', 0)
            print(f"{suite_name.upper():15} {status:10} ({duration:.2f}s)")
        
        print(f"\nTotal Duration: {total_duration:.2f} seconds")
        
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("💥 SOME TESTS FAILED!")
            
        # Print failure details
        failed_suites = [name for name, result in self.results.items() if not result['success']]
        if failed_suites:
            print(f"\nFailed Suites: {', '.join(failed_suites)}")
    
    def run_specific_tests(self, test_patterns, verbose=False):
        """Run specific test patterns"""
        print(f"\n{'='*60}")
        print("Running Specific Tests")
        print(f"Patterns: {', '.join(test_patterns)}")
        print(f"{'='*60}")
        
        cmd = ['python', 'manage.py', 'test']
        
        if verbose:
            cmd.append('--verbosity=2')
        
        cmd.extend(test_patterns)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=backend_dir,
                timeout=1800
            )
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Tests timed out")
            return False
        except Exception as e:
            print(f"❌ Error running tests: {str(e)}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run comprehensive tests for EduRise platform')
    
    parser.add_argument(
        '--suite',
        choices=['unit', 'integration', 'performance', 'e2e', 'all'],
        default='all',
        help='Test suite to run (default: all)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--failfast',
        action='store_true',
        help='Stop on first failure'
    )
    
    parser.add_argument(
        '--skip',
        nargs='*',
        choices=['unit', 'integration', 'performance', 'e2e'],
        help='Test suites to skip'
    )
    
    parser.add_argument(
        '--pattern',
        nargs='*',
        help='Specific test patterns to run'
    )
    
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Run with coverage analysis'
    )
    
    args = parser.parse_args()
    
    runner = ComprehensiveTestRunner()
    
    # Handle coverage
    if args.coverage:
        print("📊 Running tests with coverage analysis...")
        # Install coverage if not available
        try:
            import coverage
        except ImportError:
            print("Installing coverage...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'])
    
    # Run specific patterns
    if args.pattern:
        success = runner.run_specific_tests(args.pattern, args.verbose)
        sys.exit(0 if success else 1)
    
    # Run test suites
    if args.suite == 'all':
        success = runner.run_all_tests(
            verbose=args.verbose,
            failfast=args.failfast,
            skip_suites=args.skip or []
        )
    else:
        success = runner.run_test_suite(
            args.suite,
            verbose=args.verbose,
            failfast=args.failfast
        )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()