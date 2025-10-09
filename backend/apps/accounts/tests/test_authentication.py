from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken
from apps.accounts.models import Organization, UserProfile
from apps.accounts.authentication import TenantAwareJWTAuthentication
from apps.accounts.services import JWTAuthService

User = get_user_model()


class TenantAwareJWTAuthenticationTest(TestCase):
    """Test cases for TenantAwareJWTAuthentication"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.auth = TenantAwareJWTAuthentication()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
    
    def test_authenticate_with_valid_token(self):
        """Test authentication with valid JWT token"""
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {tokens["access"]}'
        
        result = self.auth.authenticate(request)
        
        self.assertIsNotNone(result)
        user, token = result
        self.assertEqual(user, self.user)
        self.assertEqual(request.tenant, self.tenant)
    
    def test_authenticate_with_invalid_token(self):
        """Test authentication with invalid JWT token"""
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid.token.here'
        
        with self.assertRaises(InvalidToken):
            self.auth.authenticate(request)
    
    def test_authenticate_without_token(self):
        """Test authentication without token"""
        request = self.factory.get('/')
        
        result = self.auth.authenticate(request)
        
        self.assertIsNone(result)
    
    def test_authenticate_with_token_without_tenant(self):
        """Test authentication with token that doesn't have tenant info"""
        tokens = JWTAuthService.generate_tokens(self.user)  # No tenant
        
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {tokens["access"]}'
        
        result = self.auth.authenticate(request)
        
        self.assertIsNotNone(result)
        user, token = result
        self.assertEqual(user, self.user)
        # No tenant should be set on request
        self.assertFalse(hasattr(request, 'tenant'))
    
    def test_authenticate_with_inactive_user(self):
        """Test authentication with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {tokens["access"]}'
        
        with self.assertRaises(InvalidToken):
            self.auth.authenticate(request)
    
    def test_authenticate_with_nonexistent_user(self):
        """Test authentication with token for nonexistent user"""
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        
        # Delete user after token generation
        self.user.delete()
        
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {tokens["access"]}'
        
        with self.assertRaises(InvalidToken):
            self.auth.authenticate(request)
    
    def test_authenticate_with_invalid_tenant_in_token(self):
        """Test authentication with token containing invalid tenant"""
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        
        # Delete tenant after token generation
        self.tenant.delete()
        
        request = self.factory.get('/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {tokens["access"]}'
        
        result = self.auth.authenticate(request)
        
        # Should still authenticate user, but no tenant set
        self.assertIsNotNone(result)
        user, token = result
        self.assertEqual(user, self.user)
        self.assertFalse(hasattr(request, 'tenant'))