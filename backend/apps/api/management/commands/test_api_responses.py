from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import Organization, UserProfile
from apps.api.responses import StandardAPIResponse
from apps.api.dashboard_views import (
    StudentDashboardView, TeacherDashboardView, 
    AdminDashboardView, SuperAdminDashboardView
)
import json

User = get_user_model()


class Command(BaseCommand):
    """
    Test API responses to ensure they follow the standardized format.
    """
    
    help = 'Test API endpoints to verify standardized response format'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--endpoint',
            type=str,
            help='Specific endpoint to test (student, teacher, admin, superadmin, all)'
        )
        parser.add_argument(
            '--format',
            type=str,
            default='json',
            choices=['json', 'summary'],
            help='Output format'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🧪 Testing API Response Standardization...')
        )
        
        # Setup test data
        self.setup_test_data()
        
        # Test endpoints
        endpoint = options.get('endpoint', 'all')
        
        if endpoint in ['student', 'all']:
            self.test_student_dashboard()
        
        if endpoint in ['teacher', 'all']:
            self.test_teacher_dashboard()
        
        if endpoint in ['admin', 'all']:
            self.test_admin_dashboard()
        
        if endpoint in ['superadmin', 'all']:
            self.test_superadmin_dashboard()
        
        # Test standardized response utility
        self.test_response_utility()
        
        self.stdout.write(
            self.style.SUCCESS('✅ API response testing completed!')
        )
    
    def setup_test_data(self):
        """Setup test data for API testing"""
        # Create test organization
        self.org, created = Organization.objects.get_or_create(
            subdomain='test-api',
            defaults={
                'name': 'Test API Organization',
                'subscription_plan': 'pro'
            }
        )
        
        # Create test users
        self.student_user, created = User.objects.get_or_create(
            email='student@test-api.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'Student',
                'is_teacher': False
            }
        )
        
        self.teacher_user, created = User.objects.get_or_create(
            email='teacher@test-api.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'Teacher',
                'is_teacher': True,
                'is_approved_teacher': True
            }
        )
        
        self.admin_user, created = User.objects.get_or_create(
            email='admin@test-api.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'Admin',
                'is_staff': True
            }
        )
        
        self.superadmin_user, created = User.objects.get_or_create(
            email='superadmin@test-api.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'SuperAdmin',
                'is_superuser': True,
                'is_staff': True
            }
        )
        
        # Create user profiles
        for user in [self.student_user, self.teacher_user, self.admin_user]:
            UserProfile.objects.get_or_create(
                user=user,
                tenant=self.org,
                defaults={'role': 'student' if not user.is_staff else 'admin'}
            )
    
    def test_student_dashboard(self):
        """Test student dashboard endpoint"""
        self.stdout.write("Testing Student Dashboard...")
        
        client = APIClient()
        refresh = RefreshToken.for_user(self.student_user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        client.defaults['HTTP_X_TENANT'] = self.org.subdomain
        
        response = client.get('/api/v1/dashboard/student/')
        
        self.validate_response_format(response, 'Student Dashboard')
    
    def test_teacher_dashboard(self):
        """Test teacher dashboard endpoint"""
        self.stdout.write("Testing Teacher Dashboard...")
        
        client = APIClient()
        refresh = RefreshToken.for_user(self.teacher_user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        client.defaults['HTTP_X_TENANT'] = self.org.subdomain
        
        response = client.get('/api/v1/dashboard/teacher/')
        
        self.validate_response_format(response, 'Teacher Dashboard')
    
    def test_admin_dashboard(self):
        """Test admin dashboard endpoint"""
        self.stdout.write("Testing Admin Dashboard...")
        
        client = APIClient()
        refresh = RefreshToken.for_user(self.admin_user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        client.defaults['HTTP_X_TENANT'] = self.org.subdomain
        
        response = client.get('/api/v1/dashboard/admin/')
        
        self.validate_response_format(response, 'Admin Dashboard')
    
    def test_superadmin_dashboard(self):
        """Test superadmin dashboard endpoint"""
        self.stdout.write("Testing SuperAdmin Dashboard...")
        
        client = APIClient()
        refresh = RefreshToken.for_user(self.superadmin_user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = client.get('/api/v1/dashboard/superadmin/')
        
        self.validate_response_format(response, 'SuperAdmin Dashboard')
    
    def test_response_utility(self):
        """Test StandardAPIResponse utility methods"""
        self.stdout.write("Testing StandardAPIResponse utility...")
        
        # Test success response
        success_response = StandardAPIResponse.success(
            data={'test': 'data'},
            message='Test success message'
        )
        
        self.validate_response_structure(success_response.data, 'Success Response Utility')
        
        # Test error response
        error_response = StandardAPIResponse.error(
            message='Test error message',
            errors={'field': ['Test error']}
        )
        
        self.validate_response_structure(error_response.data, 'Error Response Utility')
        
        # Test validation error
        validation_response = StandardAPIResponse.validation_error(
            errors={'email': ['This field is required']}
        )
        
        self.validate_response_structure(validation_response.data, 'Validation Error Utility')
    
    def validate_response_format(self, response, endpoint_name):
        """Validate that response follows standardized format"""
        try:
            data = response.json() if hasattr(response, 'json') else response.data
            
            self.validate_response_structure(data, endpoint_name)
            
            # Check status code
            status_code = response.status_code if hasattr(response, 'status_code') else 200
            if 200 <= status_code < 300:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ {endpoint_name}: Response format valid")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠️  {endpoint_name}: Non-success status {status_code}")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ❌ {endpoint_name}: Validation failed - {str(e)}")
            )
    
    def validate_response_structure(self, data, endpoint_name):
        """Validate the structure of response data"""
        required_fields = ['success', 'timestamp']
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Check success field type
        if not isinstance(data['success'], bool):
            raise ValueError("'success' field must be boolean")
        
        # Check timestamp format
        if not isinstance(data['timestamp'], str):
            raise ValueError("'timestamp' field must be string")
        
        # For success responses, check data field
        if data['success']:
            if 'data' not in data:
                raise ValueError("Success responses must include 'data' field")
        else:
            # For error responses, check message field
            if 'message' not in data:
                raise ValueError("Error responses must include 'message' field")
        
        # Optional fields validation
        if 'message' in data and not isinstance(data['message'], str):
            raise ValueError("'message' field must be string")
        
        if 'meta' in data and not isinstance(data['meta'], dict):
            raise ValueError("'meta' field must be dictionary")
        
        if 'errors' in data and not isinstance(data['errors'], (dict, list)):
            raise ValueError("'errors' field must be dictionary or list")
        
        self.stdout.write(f"    📋 {endpoint_name}: Structure validation passed")
        
        # Print sample of response data for verification
        if self.verbosity >= 2:
            self.stdout.write(f"    📄 Sample data: {json.dumps(data, indent=2, default=str)[:200]}...")
    
    @property
    def verbosity(self):
        """Get verbosity level from options"""
        return getattr(self, '_verbosity', 1)
    
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--verbosity',
            type=int,
            default=1,
            help='Verbosity level'
        )
        
    def handle(self, *args, **options):
        self._verbosity = options.get('verbosity', 1)
        super().handle(*args, **options)