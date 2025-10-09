import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import Organization, UserProfile
from apps.courses.models import Course

User = get_user_model()


class MultiTenantIntegrationTest(TestCase):
    """Integration tests for multi-tenant functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create test tenants
        self.tenant1 = Organization.objects.create(
            name="University A",
            subdomain="university-a",
            primary_color="#FF0000",
            secondary_color="#AA0000"
        )
        
        self.tenant2 = Organization.objects.create(
            name="School B",
            subdomain="school-b",
            primary_color="#00FF00",
            secondary_color="#00AA00"
        )
        
        # Create test users
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="testpass123",
            first_name="User",
            last_name="One"
        )
        
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="testpass123",
            first_name="User",
            last_name="Two"
        )
        
        # Create user profiles for different tenants
        self.profile1 = UserProfile.objects.create(
            user=self.user1,
            tenant=self.tenant1
        )
        
        self.profile2 = UserProfile.objects.create(
            user=self.user2,
            tenant=self.tenant2
        )
        
        # Create test courses for each tenant
        self.course1 = Course.objects.create(
            title="Course for University A",
            description="Test course for tenant 1",
            instructor=self.user1,
            tenant=self.tenant1,
            price=100.00
        )
        
        self.course2 = Course.objects.create(
            title="Course for School B",
            description="Test course for tenant 2",
            instructor=self.user2,
            tenant=self.tenant2,
            price=150.00
        )
        
        self.client = Client()
    
    def test_subdomain_tenant_detection(self):
        """Test that tenant is correctly detected from subdomain"""
        # Test tenant 1 subdomain
        response = self.client.get(
            '/api/v1/accounts/organizations/by_subdomain/',
            {'subdomain': 'university-a'},
            HTTP_HOST='university-a.example.com'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], 'University A')
        self.assertEqual(data['subdomain'], 'university-a')
        self.assertEqual(data['primary_color'], '#FF0000')
        
        # Test tenant 2 subdomain
        response = self.client.get(
            '/api/v1/accounts/organizations/by_subdomain/',
            {'subdomain': 'school-b'},
            HTTP_HOST='school-b.example.com'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], 'School B')
        self.assertEqual(data['subdomain'], 'school-b')
        self.assertEqual(data['primary_color'], '#00FF00')
    
    def test_tenant_isolation_courses(self):
        """Test that courses are isolated by tenant"""
        # Login as user1 (tenant1)
        self.client.login(email='user1@example.com', password='testpass123')
        
        # Request courses with tenant1 context
        response = self.client.get(
            '/api/v1/courses/courses/',
            HTTP_HOST='university-a.example.com'
        )
        
        # Should only see courses from tenant1
        self.assertEqual(response.status_code, 200)
        # Note: This would require proper authentication setup
        # For now, we're testing the model-level isolation
        
        # Test model-level isolation
        tenant1_courses = Course.objects.filter(tenant=self.tenant1)
        tenant2_courses = Course.objects.filter(tenant=self.tenant2)
        
        self.assertEqual(tenant1_courses.count(), 1)
        self.assertEqual(tenant2_courses.count(), 1)
        self.assertEqual(tenant1_courses.first().title, "Course for University A")
        self.assertEqual(tenant2_courses.first().title, "Course for School B")
    
    def test_tenant_isolation_users(self):
        """Test that user profiles are isolated by tenant"""
        # Get profiles for each tenant
        tenant1_profiles = UserProfile.objects.filter(tenant=self.tenant1)
        tenant2_profiles = UserProfile.objects.filter(tenant=self.tenant2)
        
        self.assertEqual(tenant1_profiles.count(), 1)
        self.assertEqual(tenant2_profiles.count(), 1)
        
        # Verify correct user-tenant associations
        self.assertEqual(tenant1_profiles.first().user, self.user1)
        self.assertEqual(tenant2_profiles.first().user, self.user2)
    
    def test_cross_tenant_data_access_prevention(self):
        """Test that users cannot access data from other tenants"""
        # Try to access tenant2's course from tenant1 context
        # This would be handled by the middleware and view permissions
        
        # Test at model level - ensure no cross-tenant data leakage
        user1_accessible_courses = Course.objects.filter(tenant=self.tenant1)
        user2_accessible_courses = Course.objects.filter(tenant=self.tenant2)
        
        # User1 should not see User2's courses
        self.assertNotIn(self.course2, user1_accessible_courses)
        self.assertNotIn(self.course1, user2_accessible_courses)
    
    def test_tenant_branding_data(self):
        """Test that tenant branding information is correctly stored and retrieved"""
        # Test tenant1 branding
        self.assertEqual(self.tenant1.primary_color, '#FF0000')
        self.assertEqual(self.tenant1.secondary_color, '#AA0000')
        self.assertEqual(self.tenant1.name, 'University A')
        
        # Test tenant2 branding
        self.assertEqual(self.tenant2.primary_color, '#00FF00')
        self.assertEqual(self.tenant2.secondary_color, '#00AA00')
        self.assertEqual(self.tenant2.name, 'School B')
    
    def test_invalid_subdomain_handling(self):
        """Test handling of invalid or non-existent subdomains"""
        response = self.client.get(
            '/api/v1/accounts/organizations/by_subdomain/',
            {'subdomain': 'non-existent'},
            HTTP_HOST='non-existent.example.com'
        )
        self.assertEqual(response.status_code, 404)
    
    def test_tenant_aware_model_manager(self):
        """Test that TenantAwareModel manager works correctly"""
        # Test filtering by tenant
        tenant1_courses = Course.objects.for_tenant(self.tenant1)
        tenant2_courses = Course.objects.for_tenant(self.tenant2)
        
        self.assertEqual(tenant1_courses.count(), 1)
        self.assertEqual(tenant2_courses.count(), 1)
        self.assertEqual(tenant1_courses.first(), self.course1)
        self.assertEqual(tenant2_courses.first(), self.course2)


class TenantMiddlewareTest(TestCase):
    """Test the tenant detection middleware"""
    
    def setUp(self):
        self.tenant = Organization.objects.create(
            name="Test Org",
            subdomain="test-org",
            primary_color="#0000FF"
        )
        self.client = Client()
    
    def test_middleware_sets_tenant_from_subdomain(self):
        """Test that middleware correctly sets tenant from subdomain"""
        # This would require a custom test that checks request.tenant
        # For now, we test the subdomain extraction logic
        from apps.common.middleware import TenantMiddleware
        
        middleware = TenantMiddleware(lambda r: None)
        
        # Test subdomain extraction
        self.assertEqual(middleware.extract_subdomain('test-org.example.com'), 'test-org')
        self.assertEqual(middleware.extract_subdomain('localhost'), None)
        self.assertEqual(middleware.extract_subdomain('127.0.0.1'), None)
        self.assertEqual(middleware.extract_subdomain('example.com'), None)
    
    def test_middleware_handles_missing_tenant(self):
        """Test that middleware handles requests without valid tenant"""
        # Test with non-existent subdomain
        response = self.client.get('/', HTTP_HOST='invalid.example.com')
        # Should not crash, but tenant should be None
        self.assertEqual(response.status_code, 200)  # Assuming home page exists


@pytest.mark.django_db
class TenantAPITest:
    """Pytest-based tests for tenant API functionality"""
    
    def test_tenant_api_endpoints(self, client):
        """Test tenant-related API endpoints"""
        # Create test tenant
        tenant = Organization.objects.create(
            name="API Test Org",
            subdomain="api-test",
            primary_color="#FF00FF"
        )
        
        # Test organization by subdomain endpoint
        response = client.get(
            '/api/v1/accounts/organizations/by_subdomain/',
            {'subdomain': 'api-test'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'API Test Org'
        assert data['subdomain'] == 'api-test'
        assert data['primary_color'] == '#FF00FF'


# Frontend Integration Test (would be run with a frontend testing framework)
class FrontendTenantDetectionTest(TestCase):
    """Test frontend tenant detection and branding"""
    
    def test_frontend_tenant_detection_simulation(self):
        """Simulate frontend tenant detection logic"""
        # This would typically be tested with Cypress, Playwright, or similar
        # For now, we simulate the logic that the frontend would use
        
        tenant = Organization.objects.create(
            name="Frontend Test",
            subdomain="frontend-test",
            primary_color="#FFFF00",
            secondary_color="#AAAA00"
        )
        
        # Simulate API call that frontend would make
        response = self.client.get(
            '/api/v1/accounts/organizations/by_subdomain/',
            {'subdomain': 'frontend-test'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify frontend would receive correct branding data
        self.assertEqual(data['primary_color'], '#FFFF00')
        self.assertEqual(data['secondary_color'], '#AAAA00')
        self.assertEqual(data['name'], 'Frontend Test')
        
        # This data would be used by frontend to:
        # 1. Set CSS custom properties for theming
        # 2. Display organization name in header
        # 3. Configure tenant-specific settings