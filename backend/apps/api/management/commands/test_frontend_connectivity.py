from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import Organization, UserProfile
import json
import requests
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    """
    Test frontend connectivity to the API endpoints.
    """
    
    help = 'Test API endpoints for frontend connectivity'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            type=str,
            default='http://localhost:8000',
            help='Backend host URL'
        )
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create test data for testing'
        )
    
    def handle(self, *args, **options):
        self.host = options['host']
        
        self.stdout.write(
            self.style.SUCCESS('🌐 Testing Frontend API Connectivity...')
        )
        
        if options['create_test_data']:
            self.create_test_data()
        
        # Test core endpoints
        self.test_health_check()
        self.test_api_documentation()
        self.test_authentication_flow()
        self.test_dashboard_endpoints()
        self.test_course_endpoints()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Frontend connectivity testing completed!')
        )
    
    def create_test_data(self):
        """Create test data for API testing"""
        self.stdout.write("Creating test data...")
        
        # Create test organization
        self.org, created = Organization.objects.get_or_create(
            subdomain='test-frontend',
            defaults={
                'name': 'Test Frontend Organization',
                'subscription_plan': 'pro'
            }
        )
        
        # Create test user
        self.test_user, created = User.objects.get_or_create(
            email='frontend-test@example.com',
            defaults={
                'first_name': 'Frontend',
                'last_name': 'Test',
                'is_teacher': True,
                'is_approved_teacher': True
            }
        )
        
        if created:
            self.test_user.set_password('testpassword123')
            self.test_user.save()
        
        # Create user profile
        UserProfile.objects.get_or_create(
            user=self.test_user,
            tenant=self.org,
            defaults={'role': 'teacher'}
        )
        
        self.stdout.write("✅ Test data created")
    
    def test_health_check(self):
        """Test API health check endpoint"""
        self.stdout.write("Testing health check endpoint...")
        
        try:
            response = requests.get(f'{self.host}/api/health/')
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.stdout.write("  ✅ Health check passed")
                    self.stdout.write(f"    Status: {data['data']['status']}")
                else:
                    self.stdout.write("  ❌ Health check failed - invalid response format")
            else:
                self.stdout.write(f"  ❌ Health check failed - status {response.status_code}")
                
        except Exception as e:
            self.stdout.write(f"  ❌ Health check failed - {str(e)}")
    
    def test_api_documentation(self):
        """Test API documentation endpoint"""
        self.stdout.write("Testing API documentation endpoint...")
        
        try:
            response = requests.get(f'{self.host}/api/docs/')
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'endpoints' in data.get('data', {}):
                    self.stdout.write("  ✅ API documentation accessible")
                    self.stdout.write(f"    API Version: {data['data'].get('api_version')}")
                    self.stdout.write(f"    Base URL: {data['data'].get('base_url')}")
                else:
                    self.stdout.write("  ❌ API documentation failed - invalid response format")
            else:
                self.stdout.write(f"  ❌ API documentation failed - status {response.status_code}")
                
        except Exception as e:
            self.stdout.write(f"  ❌ API documentation failed - {str(e)}")
    
    def test_authentication_flow(self):
        """Test authentication endpoints"""
        self.stdout.write("Testing authentication flow...")
        
        try:
            # Test login endpoint
            login_data = {
                'email': 'frontend-test@example.com',
                'password': 'testpassword123'
            }
            
            response = requests.post(
                f'{self.host}/api/v1/accounts/auth/login/',
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access' in data:
                    self.access_token = data['access']
                    self.stdout.write("  ✅ Authentication successful")
                    self.stdout.write("    Access token received")
                    return True
                else:
                    self.stdout.write("  ❌ Authentication failed - no access token")
            else:
                self.stdout.write(f"  ❌ Authentication failed - status {response.status_code}")
                if response.content:
                    self.stdout.write(f"    Response: {response.text}")
                
        except Exception as e:
            self.stdout.write(f"  ❌ Authentication failed - {str(e)}")
        
        return False
    
    def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        if not hasattr(self, 'access_token'):
            self.stdout.write("⏭️ Skipping dashboard tests - no access token")
            return
        
        self.stdout.write("Testing dashboard endpoints...")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Tenant': 'test-frontend',
            'Content-Type': 'application/json'
        }
        
        dashboard_endpoints = [
            ('Student Dashboard', '/api/v1/dashboard/student/'),
            ('Teacher Dashboard', '/api/v1/dashboard/teacher/'),
        ]
        
        for name, endpoint in dashboard_endpoints:
            try:
                response = requests.get(f'{self.host}{endpoint}', headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.stdout.write(f"  ✅ {name} accessible")
                    else:
                        self.stdout.write(f"  ❌ {name} failed - invalid response format")
                elif response.status_code == 403:
                    self.stdout.write(f"  ⚠️  {name} - permission denied (expected for some roles)")
                else:
                    self.stdout.write(f"  ❌ {name} failed - status {response.status_code}")
                    
            except Exception as e:
                self.stdout.write(f"  ❌ {name} failed - {str(e)}")
    
    def test_course_endpoints(self):
        """Test course-related endpoints"""
        if not hasattr(self, 'access_token'):
            self.stdout.write("⏭️ Skipping course tests - no access token")
            return
        
        self.stdout.write("Testing course endpoints...")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Tenant': 'test-frontend',
            'Content-Type': 'application/json'
        }
        
        course_endpoints = [
            ('Courses List', '/api/v1/courses/'),
            ('Course Dashboard Stats', '/api/v1/courses/dashboard_stats/'),
            ('Course Recommendations', '/api/v1/courses/recommendations/'),
            ('Marketplace Enhanced', '/api/v1/courses/marketplace_enhanced/'),
            ('Enrollments', '/api/v1/enrollments/'),
        ]
        
        for name, endpoint in course_endpoints:
            try:
                response = requests.get(f'{self.host}{endpoint}', headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.stdout.write(f"  ✅ {name} accessible")
                        # Show sample data structure
                        if 'data' in data and data['data']:
                            if isinstance(data['data'], dict):
                                keys = list(data['data'].keys())[:3]
                                self.stdout.write(f"    Sample keys: {keys}")
                            elif isinstance(data['data'], list) and data['data']:
                                if isinstance(data['data'][0], dict):
                                    keys = list(data['data'][0].keys())[:3]
                                    self.stdout.write(f"    Sample item keys: {keys}")
                    else:
                        self.stdout.write(f"  ❌ {name} failed - invalid response format")
                else:
                    self.stdout.write(f"  ❌ {name} failed - status {response.status_code}")
                    
            except Exception as e:
                self.stdout.write(f"  ❌ {name} failed - {str(e)}")
    
    def print_frontend_integration_guide(self):
        """Print integration guide for frontend developers"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("FRONTEND INTEGRATION GUIDE"))
        self.stdout.write("="*60)
        
        guide = f"""
🔗 Base API URL: {self.host}/api/v1/

📋 Required Headers:
- Authorization: Bearer <access_token>
- X-Tenant: <organization_subdomain>
- Content-Type: application/json

🔐 Authentication Flow:
1. POST {self.host}/api/v1/accounts/auth/login/
   Body: {{"email": "user@example.com", "password": "password"}}
   
2. Extract access_token from response
   
3. Include in subsequent requests:
   Headers: {{"Authorization": "Bearer <access_token>"}}

📊 Key Dashboard Endpoints:
- Student: GET {self.host}/api/v1/dashboard/student/
- Teacher: GET {self.host}/api/v1/dashboard/teacher/
- Admin: GET {self.host}/api/v1/dashboard/admin/

📚 Course Endpoints:
- List: GET {self.host}/api/v1/courses/
- Marketplace: GET {self.host}/api/v1/courses/marketplace_enhanced/
- Enroll: POST {self.host}/api/v1/courses/{{id}}/enroll/
- Stats: GET {self.host}/api/v1/courses/dashboard_stats/

📖 Full Documentation: {self.host}/api/docs/

✅ All responses follow standardized format:
{{
  "success": true/false,
  "data": {{...}},
  "message": "...",
  "timestamp": "...",
  "meta": {{...}}  // pagination, etc.
}}
"""
        
        self.stdout.write(guide)
        self.stdout.write("="*60)