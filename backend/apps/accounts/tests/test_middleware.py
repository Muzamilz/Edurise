from django.test import TestCase, RequestFactory, override_settings
from django.http import HttpResponse
from apps.accounts.models import Organization
from apps.common.middleware import TenantMiddleware


@override_settings(ALLOWED_HOSTS=['*'])
class TenantMiddlewareTest(TestCase):
    """Test cases for TenantMiddleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantMiddleware(self.get_response)
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
    
    def get_response(self, request):
        """Mock response function"""
        return HttpResponse('OK')
    
    def test_extract_subdomain_valid(self):
        """Test extracting valid subdomain"""
        subdomain = self.middleware.extract_subdomain('testuni.edurise.com')
        self.assertEqual(subdomain, 'testuni')
    
    def test_extract_subdomain_localhost(self):
        """Test extracting subdomain from localhost"""
        subdomain = self.middleware.extract_subdomain('localhost')
        self.assertIsNone(subdomain)
        
        subdomain = self.middleware.extract_subdomain('127.0.0.1')
        self.assertIsNone(subdomain)
    
    def test_extract_subdomain_no_subdomain(self):
        """Test extracting subdomain when none exists"""
        subdomain = self.middleware.extract_subdomain('edurise.com')
        self.assertIsNone(subdomain)
    
    def test_middleware_with_valid_tenant(self):
        """Test middleware with valid tenant"""
        request = self.factory.get('/', HTTP_HOST='testuni.edurise.com')
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.tenant, self.tenant)
    
    def test_middleware_with_invalid_tenant(self):
        """Test middleware with invalid tenant"""
        request = self.factory.get('/', HTTP_HOST='nonexistent.edurise.com')
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(request.tenant)
    
    def test_middleware_with_localhost(self):
        """Test middleware with localhost"""
        request = self.factory.get('/', HTTP_HOST='localhost:8000')
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(request.tenant)
    
    def test_middleware_with_inactive_tenant(self):
        """Test middleware with inactive tenant"""
        self.tenant.is_active = False
        self.tenant.save()
        
        request = self.factory.get('/', HTTP_HOST='testuni.edurise.com')
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(request.tenant)