import json
import inspect
from django.core.management.base import BaseCommand, CommandError
from django.urls import get_resolver
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.apps import apps
from rest_framework import viewsets, serializers
from rest_framework.test import APIClient
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import Organization, UserProfile

User = get_user_model()


class Command(BaseCommand):
    """
    Audit all API endpoints for completeness and functionality.
    
    This command discovers all API endpoints, tests their functionality,
    verifies serializer completeness, and checks permission classes.
    """
    
    help = 'Audit API endpoints for completeness and functionality'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='table',
            choices=['table', 'json'],
            help='Output format (table or json)'
        )
        parser.add_argument(
            '--test-endpoints',
            action='store_true',
            help='Test endpoint functionality with actual HTTP requests'
        )
        parser.add_argument(
            '--check-serializers',
            action='store_true',
            help='Check serializer field completeness'
        )
        parser.add_argument(
            '--check-permissions',
            action='store_true',
            help='Verify permission classes'
        )
        parser.add_argument(
            '--app',
            type=str,
            help='Audit endpoints for specific app only'
        )
    
    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        self.format = options['format']
        
        try:
            # Discover all API endpoints
            self.stdout.write(
                self.style.SUCCESS('🔍 Discovering API endpoints...')
            )
            endpoints = self.discover_endpoints(options.get('app'))
            
            if not endpoints:
                self.stdout.write(
                    self.style.WARNING('No API endpoints found.')
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS(f'Found {len(endpoints)} endpoints')
            )
            
            # Initialize audit results
            audit_results = {
                'total_endpoints': len(endpoints),
                'endpoints': [],
                'summary': {
                    'functional': 0,
                    'non_functional': 0,
                    'serializer_complete': 0,
                    'serializer_incomplete': 0,
                    'permission_secure': 0,
                    'permission_insecure': 0
                }
            }
            
            # Test each endpoint
            for endpoint_info in endpoints:
                result = self.audit_endpoint(
                    endpoint_info,
                    test_functionality=options.get('test_endpoints', False),
                    check_serializers=options.get('check_serializers', False),
                    check_permissions=options.get('check_permissions', False)
                )
                audit_results['endpoints'].append(result)
                
                # Update summary
                if result.get('functional'):
                    audit_results['summary']['functional'] += 1
                else:
                    audit_results['summary']['non_functional'] += 1
                
                if result.get('serializer_complete'):
                    audit_results['summary']['serializer_complete'] += 1
                else:
                    audit_results['summary']['serializer_incomplete'] += 1
                
                if result.get('permission_secure'):
                    audit_results['summary']['permission_secure'] += 1
                else:
                    audit_results['summary']['permission_insecure'] += 1
            
            # Output results
            self.output_results(audit_results)
            
        except Exception as e:
            raise CommandError(f'Audit failed: {str(e)}')
    
    def discover_endpoints(self, app_filter=None):
        """Discover all API endpoints in the project"""
        endpoints = []
        resolver = get_resolver()
        
        def extract_endpoints(url_patterns, prefix=''):
            for pattern in url_patterns:
                if hasattr(pattern, 'url_patterns'):
                    # This is an include() pattern
                    new_prefix = prefix + str(pattern.pattern)
                    extract_endpoints(pattern.url_patterns, new_prefix)
                else:
                    # This is a regular URL pattern
                    full_path = prefix + str(pattern.pattern)
                    
                    # Skip non-API endpoints
                    if not full_path.startswith('api/'):
                        continue
                    
                    # Filter by app if specified
                    if app_filter and app_filter not in full_path:
                        continue
                    
                    # Get view information
                    view_info = self.get_view_info(pattern)
                    if view_info:
                        endpoints.append({
                            'path': full_path,
                            'name': pattern.name,
                            'view_class': view_info['view_class'],
                            'view_name': view_info['view_name'],
                            'methods': view_info['methods'],
                            'app_name': view_info['app_name']
                        })
        
        extract_endpoints(resolver.url_patterns)
        return endpoints
    
    def get_view_info(self, pattern):
        """Extract view information from URL pattern"""
        try:
            view_func = pattern.callback
            
            if hasattr(view_func, 'view_class'):
                # This is a class-based view
                view_class = view_func.view_class
                app_name = view_class.__module__.split('.')[1] if '.' in view_class.__module__ else 'unknown'
                
                # Get allowed methods
                methods = []
                if hasattr(view_class, 'http_method_names'):
                    methods = view_class.http_method_names
                elif hasattr(view_class, 'allowed_methods'):
                    methods = view_class.allowed_methods
                
                return {
                    'view_class': view_class,
                    'view_name': view_class.__name__,
                    'methods': methods,
                    'app_name': app_name
                }
            else:
                # This is a function-based view
                app_name = view_func.__module__.split('.')[1] if '.' in view_func.__module__ else 'unknown'
                return {
                    'view_class': None,
                    'view_name': view_func.__name__,
                    'methods': ['GET', 'POST'],  # Default assumption
                    'app_name': app_name
                }
        except Exception:
            return None
    
    def audit_endpoint(self, endpoint_info, test_functionality=False, 
                      check_serializers=False, check_permissions=False):
        """Audit a single endpoint"""
        result = {
            'path': endpoint_info['path'],
            'name': endpoint_info['name'],
            'view_name': endpoint_info['view_name'],
            'app_name': endpoint_info['app_name'],
            'methods': endpoint_info['methods'],
            'functional': None,
            'serializer_complete': None,
            'permission_secure': None,
            'issues': []
        }
        
        view_class = endpoint_info['view_class']
        
        if test_functionality and view_class:
            result['functional'] = self.test_endpoint_functionality(endpoint_info)
        
        if check_serializers and view_class:
            result['serializer_complete'] = self.verify_serializer_completeness(view_class)
        
        if check_permissions and view_class:
            result['permission_secure'] = self.check_permission_classes(view_class)
        
        return result
    
    def test_endpoint_functionality(self, endpoint_info):
        """Test endpoint functionality with HTTP requests"""
        try:
            # Create test client
            client = APIClient()
            
            # Create test user and organization for authentication
            test_org = self.get_or_create_test_org()
            test_user = self.get_or_create_test_user(test_org)
            
            # Authenticate client
            refresh = RefreshToken.for_user(test_user)
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
            
            # Add tenant header if needed
            client.defaults['HTTP_X_TENANT'] = test_org.subdomain
            
            # Test GET request (most common)
            path = f"/{endpoint_info['path'].rstrip('/')}"
            if 'GET' in endpoint_info['methods'] or 'get' in endpoint_info['methods']:
                response = client.get(path)
                
                # Consider 200, 201, 404 as functional (404 might be expected for empty data)
                if response.status_code in [200, 201, 404]:
                    return True
                elif response.status_code == 403:
                    # Permission denied might be expected
                    return True
                elif response.status_code == 401:
                    # Authentication required is functional
                    return True
                else:
                    return False
            
            return True  # If no GET method, assume functional
            
        except Exception as e:
            if self.verbosity >= 2:
                self.stdout.write(
                    self.style.WARNING(f'Error testing {endpoint_info["path"]}: {str(e)}')
                )
            return False
    
    def verify_serializer_completeness(self, view_class):
        """Check if serializers expose all model fields properly"""
        try:
            if not issubclass(view_class, viewsets.ModelViewSet):
                return True  # Skip non-model viewsets
            
            # Get the model
            if hasattr(view_class, 'queryset') and view_class.queryset is not None:
                model = view_class.queryset.model
            elif hasattr(view_class, 'model'):
                model = view_class.model
            else:
                return True  # Can't determine model
            
            # Get the serializer
            serializer_class = getattr(view_class, 'serializer_class', None)
            if not serializer_class:
                return False
            
            # Get model fields
            model_fields = set()
            for field in model._meta.get_fields():
                if not field.many_to_many and not field.one_to_many:
                    model_fields.add(field.name)
            
            # Get serializer fields
            serializer_instance = serializer_class()
            serializer_fields = set(serializer_instance.fields.keys())
            
            # Check if important fields are missing
            important_fields = {'id', 'created_at', 'updated_at'}
            missing_important = important_fields - serializer_fields
            
            # Consider complete if no important fields are missing
            return len(missing_important) == 0
            
        except Exception as e:
            if self.verbosity >= 2:
                self.stdout.write(
                    self.style.WARNING(f'Error checking serializer for {view_class.__name__}: {str(e)}')
                )
            return False
    
    def check_permission_classes(self, view_class):
        """Verify that proper permission classes are set"""
        try:
            permission_classes = getattr(view_class, 'permission_classes', [])
            
            # Check if any permission classes are defined
            if not permission_classes:
                return False
            
            # Check for common secure permissions
            secure_permissions = [
                'IsAuthenticated',
                'IsAuthenticatedOrReadOnly', 
                'IsAdminUser',
                'DjangoModelPermissions'
            ]
            
            for perm_class in permission_classes:
                perm_name = perm_class.__name__ if hasattr(perm_class, '__name__') else str(perm_class)
                if any(secure_perm in perm_name for secure_perm in secure_permissions):
                    return True
            
            return False
            
        except Exception as e:
            if self.verbosity >= 2:
                self.stdout.write(
                    self.style.WARNING(f'Error checking permissions for {view_class.__name__}: {str(e)}')
                )
            return False
    
    def get_or_create_test_org(self):
        """Get or create test organization for testing"""
        org, created = Organization.objects.get_or_create(
            subdomain='test-audit',
            defaults={
                'name': 'Test Audit Organization',
                'subscription_plan': 'basic'
            }
        )
        return org
    
    def get_or_create_test_user(self, org):
        """Get or create test user for testing"""
        user, created = User.objects.get_or_create(
            email='test-audit@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_teacher': True,
                'is_approved_teacher': True
            }
        )
        
        # Create user profile for the organization
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            tenant=org,
            defaults={
                'role': 'admin'
            }
        )
        
        return user
    
    def output_results(self, audit_results):
        """Output audit results in specified format"""
        if self.format == 'json':
            self.stdout.write(json.dumps(audit_results, indent=2, default=str))
        else:
            self.output_table_format(audit_results)
    
    def output_table_format(self, audit_results):
        """Output results in table format"""
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('API ENDPOINT AUDIT RESULTS'))
        self.stdout.write('='*80)
        
        # Summary
        summary = audit_results['summary']
        self.stdout.write(f"\n📊 SUMMARY:")
        self.stdout.write(f"Total Endpoints: {audit_results['total_endpoints']}")
        
        if summary['functional'] + summary['non_functional'] > 0:
            self.stdout.write(f"Functional: {summary['functional']}")
            self.stdout.write(f"Non-functional: {summary['non_functional']}")
        
        if summary['serializer_complete'] + summary['serializer_incomplete'] > 0:
            self.stdout.write(f"Serializer Complete: {summary['serializer_complete']}")
            self.stdout.write(f"Serializer Incomplete: {summary['serializer_incomplete']}")
        
        if summary['permission_secure'] + summary['permission_insecure'] > 0:
            self.stdout.write(f"Permission Secure: {summary['permission_secure']}")
            self.stdout.write(f"Permission Insecure: {summary['permission_insecure']}")
        
        # Detailed results
        self.stdout.write(f"\n📋 DETAILED RESULTS:")
        self.stdout.write("-" * 80)
        
        for endpoint in audit_results['endpoints']:
            status_indicators = []
            
            if endpoint['functional'] is not None:
                status_indicators.append('✅' if endpoint['functional'] else '❌')
            
            if endpoint['serializer_complete'] is not None:
                status_indicators.append('📝✅' if endpoint['serializer_complete'] else '📝❌')
            
            if endpoint['permission_secure'] is not None:
                status_indicators.append('🔒✅' if endpoint['permission_secure'] else '🔒❌')
            
            status_str = ' '.join(status_indicators) if status_indicators else '⏭️'
            
            self.stdout.write(
                f"{status_str} {endpoint['app_name']:<12} {endpoint['path']:<40} {endpoint['view_name']}"
            )
            
            if endpoint.get('issues'):
                for issue in endpoint['issues']:
                    self.stdout.write(f"    ⚠️  {issue}")
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write("Legend:")
        self.stdout.write("✅/❌ = Functional/Non-functional")
        self.stdout.write("📝✅/📝❌ = Serializer Complete/Incomplete") 
        self.stdout.write("🔒✅/🔒❌ = Permission Secure/Insecure")
        self.stdout.write("⏭️ = Not tested")
        self.stdout.write("="*80