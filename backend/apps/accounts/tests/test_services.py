from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import Organization, UserProfile
from apps.accounts.services import AuthService, JWTAuthService, TenantService
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from django.conf import settings

User = get_user_model()


class AuthServiceTest(TestCase):
    """Test cases for AuthService"""
    
    def setUp(self):
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
    
    def test_register_user(self):
        """Test user registration"""
        user = AuthService.register_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            is_teacher=True,
            tenant=self.tenant
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_teacher)
        self.assertTrue(user.check_password('testpass123'))
        
        # Check that profile was created
        profile = UserProfile.objects.get(user=user, tenant=self.tenant)
        self.assertEqual(profile.role, 'teacher')
    
    def test_register_user_without_tenant(self):
        """Test user registration without tenant"""
        user = AuthService.register_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_teacher)
        
        # Check that no profile was created
        self.assertEqual(UserProfile.objects.filter(user=user).count(), 0)
    
    def test_authenticate_user(self):
        """Test user authentication"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Test successful authentication
        auth_user = AuthService.authenticate_user('test@example.com', 'testpass123')
        self.assertEqual(auth_user, user)
        
        # Test failed authentication
        auth_user = AuthService.authenticate_user('test@example.com', 'wrongpass')
        self.assertIsNone(auth_user)


class JWTAuthServiceTest(TestCase):
    """Test cases for JWTAuthService"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            is_teacher=True
        )
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
    
    def test_generate_tokens_without_tenant(self):
        """Test JWT token generation without tenant"""
        tokens = JWTAuthService.generate_tokens(self.user)
        
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        
        # Verify token content
        payload = jwt.decode(tokens['access'], settings.SECRET_KEY, algorithms=['HS256'])
        self.assertEqual(payload['email'], self.user.email)
        self.assertEqual(payload['user_id'], str(self.user.id))
        self.assertTrue(payload['is_teacher'])
        self.assertFalse(payload['is_approved_teacher'])
    
    def test_generate_tokens_with_tenant(self):
        """Test JWT token generation with tenant"""
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        
        # Verify token content includes tenant info
        payload = jwt.decode(tokens['access'], settings.SECRET_KEY, algorithms=['HS256'])
        self.assertEqual(payload['tenant_id'], str(self.tenant.id))
        self.assertEqual(payload['tenant_subdomain'], self.tenant.subdomain)
        self.assertEqual(payload['tenant_name'], self.tenant.name)
    
    def test_verify_token(self):
        """Test JWT token verification"""
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        
        # Test valid token
        payload = JWTAuthService.verify_token(tokens['access'])
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], str(self.user.id))
        
        # Test invalid token
        payload = JWTAuthService.verify_token('invalid.token.here')
        self.assertIsNone(payload)
    
    def test_generate_password_reset_token(self):
        """Test password reset token generation"""
        token = JWTAuthService.generate_password_reset_token(self.user)
        
        # Verify token content
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        self.assertEqual(payload['user_id'], str(self.user.id))
        self.assertEqual(payload['type'], 'password_reset')
    
    def test_blacklist_token(self):
        """Test token blacklisting"""
        tokens = JWTAuthService.generate_tokens(self.user)
        
        # Test successful blacklisting
        result = JWTAuthService.blacklist_token(tokens['refresh'])
        self.assertTrue(result)
        
        # Test blacklisting invalid token
        result = JWTAuthService.blacklist_token('invalid.token.here')
        self.assertFalse(result)


class TenantServiceTest(TestCase):
    """Test cases for TenantService"""
    
    def setUp(self):
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
    
    def test_get_tenant_by_subdomain(self):
        """Test getting tenant by subdomain"""
        # Test existing tenant
        tenant = TenantService.get_tenant_by_subdomain('testuni')
        self.assertEqual(tenant, self.tenant)
        
        # Test non-existing tenant
        tenant = TenantService.get_tenant_by_subdomain('nonexistent')
        self.assertIsNone(tenant)
        
        # Test inactive tenant
        self.tenant.is_active = False
        self.tenant.save()
        
        tenant = TenantService.get_tenant_by_subdomain('testuni')
        self.assertIsNone(tenant)
    
    def test_create_tenant(self):
        """Test tenant creation"""
        tenant = TenantService.create_tenant(
            name='Demo Corp',
            subdomain='democorp',
            subscription_plan='enterprise'
        )
        
        self.assertEqual(tenant.name, 'Demo Corp')
        self.assertEqual(tenant.subdomain, 'democorp')
        self.assertEqual(tenant.subscription_plan, 'enterprise')
        self.assertTrue(tenant.is_active)
    
    def test_get_user_tenants(self):
        """Test getting user tenants"""
        # Initially no tenants
        tenants = TenantService.get_user_tenants(self.user)
        self.assertEqual(tenants.count(), 0)
        
        # Add user to tenant
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
        
        tenants = TenantService.get_user_tenants(self.user)
        self.assertEqual(tenants.count(), 1)
        self.assertIn(self.tenant, tenants)
        
        # Add user to another tenant
        tenant2 = Organization.objects.create(
            name='Demo Corp',
            subdomain='democorp',
            subscription_plan='enterprise'
        )
        UserProfile.objects.create(user=self.user, tenant=tenant2)
        
        tenants = TenantService.get_user_tenants(self.user)
        self.assertEqual(tenants.count(), 2)
        self.assertIn(self.tenant, tenants)
        self.assertIn(tenant2, tenants)
    
    def test_add_user_to_tenant(self):
        """Test adding user to tenant"""
        profile = TenantService.add_user_to_tenant(self.user, self.tenant, role='teacher')
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.tenant, self.tenant)
        self.assertEqual(profile.role, 'teacher')
        
        # Test adding same user to same tenant (should return existing)
        profile2 = TenantService.add_user_to_tenant(self.user, self.tenant, role='admin')
        self.assertEqual(profile, profile2)
        # Role should not change for existing profile
        self.assertEqual(profile2.role, 'teacher')
    
    def test_add_user_to_tenant_default_role(self):
        """Test adding user to tenant with default role"""
        profile = TenantService.add_user_to_tenant(self.user, self.tenant)
        
        self.assertEqual(profile.role, 'student')