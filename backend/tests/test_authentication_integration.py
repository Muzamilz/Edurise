import pytest
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.accounts.models import Organization, UserProfile, TeacherApproval
from apps.accounts.services import JWTAuthService
from unittest.mock import patch

User = get_user_model()


class AuthenticationIntegrationTest(APITestCase):
    """Comprehensive integration tests for authentication flow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test tenant
        self.tenant = Organization.objects.create(
            name="Test University",
            subdomain="test-uni",
            primary_color="#3B82F6",
            secondary_color="#1E40AF",
            subscription_plan="pro"
        )
        
        # Test user data
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'is_teacher': False
        }
        
        self.teacher_data = {
            'email': 'teacher@example.com',
            'password': 'TeacherPass123!',
            'password_confirm': 'TeacherPass123!',
            'first_name': 'Test',
            'last_name': 'Teacher',
            'is_teacher': True
        }
    
    def test_complete_user_registration_flow(self):
        """Test complete user registration process"""
        # Step 1: Register new user
        response = self.client.post(
            '/api/v1/accounts/auth/register/',
            self.user_data,
            format='json',
            HTTP_HOST='test-uni.example.com'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        
        # Verify response structure
        self.assertIn('user', data)
        self.assertIn('tokens', data)
        
        user_data = data['user']
        tokens = data['tokens']
        
        # Verify user data
        self.assertEqual(user_data['email'], self.user_data['email'])
        self.assertEqual(user_data['first_name'], self.user_data['first_name'])
        self.assertEqual(user_data['last_name'], self.user_data['last_name'])
        self.assertEqual(user_data['is_teacher'], False)
        self.assertEqual(user_data['is_approved_teacher'], False)
        
        # Verify tokens are present
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        
        # Step 2: Verify user was created in database
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
        self.assertFalse(user.is_teacher)
        
        # Step 3: Verify user profile was created with tenant
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.tenant, self.tenant)
        
        return user, tokens
    
    def test_complete_teacher_registration_flow(self):
        """Test teacher registration and approval process"""
        # Step 1: Register as teacher
        response = self.client.post(
            '/api/v1/accounts/auth/register/',
            self.teacher_data,
            format='json',
            HTTP_HOST='test-uni.example.com'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        
        # Verify teacher flag is set
        user_data = data['user']
        self.assertEqual(user_data['is_teacher'], True)
        self.assertEqual(user_data['is_approved_teacher'], False)
        
        # Step 2: Verify teacher can apply for approval
        user = User.objects.get(email=self.teacher_data['email'])
        tokens = data['tokens']
        
        # Set authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Submit teacher approval application
        approval_data = {
            'teaching_experience': 'I have 5 years of teaching experience in computer science.',
            'qualifications': 'PhD in Computer Science, Master in Education',
            'subject_expertise': 'Python, Django, Web Development, Machine Learning',
            'portfolio_url': 'https://example.com/portfolio'
        }
        
        response = self.client.post(
            '/api/v1/accounts/teacher-approvals/',
            approval_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 3: Verify approval record was created
        approval = TeacherApproval.objects.get(user=user)
        self.assertEqual(approval.status, 'pending')
        self.assertEqual(approval.teaching_experience, approval_data['teaching_experience'])
        
        return user, tokens, approval
    
    def test_login_flow_with_jwt_tokens(self):
        """Test complete login flow with JWT token generation"""
        # Step 1: Create user first
        user, _ = self.test_complete_user_registration_flow()
        
        # Step 2: Login with credentials
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/login/',
            login_data,
            format='json',
            HTTP_HOST='test-uni.example.com'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify response structure
        self.assertIn('user', data)
        self.assertIn('tokens', data)
        
        tokens = data['tokens']
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        
        # Step 3: Test authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get('/api/v1/accounts/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user_data = response.json()
        self.assertEqual(user_data['email'], self.user_data['email'])
        
        return tokens
    
    def test_jwt_token_refresh_flow(self):
        """Test JWT token refresh mechanism"""
        # Step 1: Get initial tokens
        tokens = self.test_login_flow_with_jwt_tokens()
        
        # Step 2: Use refresh token to get new access token
        refresh_data = {
            'refresh': tokens['refresh']
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/token/refresh/',
            refresh_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify new access token is provided
        self.assertIn('access', data)
        new_access_token = data['access']
        self.assertNotEqual(new_access_token, tokens['access'])
        
        # Step 3: Test new access token works
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        
        response = self.client.get('/api/v1/accounts/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_tenant_aware_authentication(self):
        """Test that authentication is tenant-aware"""
        # Step 1: Create user in tenant1
        user, tokens = self.test_complete_user_registration_flow()
        
        # Step 2: Create another tenant
        tenant2 = Organization.objects.create(
            name="Another University",
            subdomain="another-uni",
            primary_color="#EF4444",
            subscription_plan="basic"
        )
        
        # Step 3: Test that user can access tenant1 resources
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(
            '/api/v1/accounts/users/me/',
            HTTP_HOST='test-uni.example.com'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 4: Verify user profile is associated with correct tenant
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.tenant, self.tenant)
        self.assertNotEqual(profile.tenant, tenant2)
    
    def test_password_reset_flow(self):
        """Test complete password reset process"""
        # Step 1: Create user
        user, _ = self.test_complete_user_registration_flow()
        
        # Step 2: Request password reset
        reset_request_data = {
            'email': self.user_data['email']
        }
        
        with patch('apps.accounts.services.AuthService.send_password_reset_email') as mock_send_email:
            response = self.client.post(
                '/api/v1/accounts/auth/password-reset/',
                reset_request_data,
                format='json'
            )
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_send_email.assert_called_once_with(user)
        
        # Step 3: Generate reset token (simulate email link)
        from apps.accounts.services import JWTAuthService
        reset_token = JWTAuthService.generate_password_reset_token(user)
        
        # Step 4: Confirm password reset
        new_password = 'NewPassword123!'
        reset_confirm_data = {
            'token': reset_token,
            'password': new_password,
            'password_confirm': new_password
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/password-reset-confirm/',
            reset_confirm_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 5: Verify new password works
        login_data = {
            'email': self.user_data['email'],
            'password': new_password
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/login/',
            login_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_google_oauth_integration_flow(self):
        """Test Google OAuth integration (mocked)"""
        # Mock Google OAuth response
        mock_google_data = {
            'access_token': 'mock_access_token',
            'id_token': 'mock_id_token'
        }
        
        with patch('allauth.socialaccount.providers.google.views.GoogleOAuth2Adapter') as mock_adapter:
            # Mock successful Google authentication
            mock_adapter.return_value.complete_login.return_value = True
            
            response = self.client.post(
                '/api/v1/accounts/auth/google/',
                mock_google_data,
                format='json',
                HTTP_HOST='test-uni.example.com'
            )
            
            # Note: This would require proper Google OAuth setup
            # For now, we test that the endpoint exists and handles the request
            # The actual implementation would depend on django-allauth configuration
    
    def test_authentication_error_handling(self):
        """Test various authentication error scenarios"""
        # Test 1: Invalid login credentials
        invalid_login = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/login/',
            invalid_login,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test 2: Registration with mismatched passwords
        invalid_registration = self.user_data.copy()
        invalid_registration['password_confirm'] = 'different_password'
        
        response = self.client.post(
            '/api/v1/accounts/auth/register/',
            invalid_registration,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test 3: Duplicate email registration
        self.test_complete_user_registration_flow()  # Create first user
        
        response = self.client.post(
            '/api/v1/accounts/auth/register/',
            self.user_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test 4: Invalid JWT token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        
        response = self.client.get('/api/v1/accounts/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_profile_management(self):
        """Test user profile creation and updates"""
        # Step 1: Create user and get tokens
        user, tokens = self.test_complete_user_registration_flow()
        
        # Step 2: Update user profile
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        profile_update = {
            'bio': 'I am a passionate learner interested in technology.',
            'phone_number': '+1234567890',
            'timezone': 'America/New_York',
            'language': 'en'
        }
        
        # Get user profile
        profile = UserProfile.objects.get(user=user)
        
        response = self.client.patch(
            f'/api/v1/accounts/profiles/{profile.id}/',
            profile_update,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify profile was updated
        profile.refresh_from_db()
        self.assertEqual(profile.bio, profile_update['bio'])
        self.assertEqual(profile.phone_number, profile_update['phone_number'])
        self.assertEqual(profile.timezone, profile_update['timezone'])
    
    def test_teacher_approval_workflow(self):
        """Test complete teacher approval workflow"""
        # Step 1: Register teacher and submit approval
        user, tokens, approval = self.test_complete_teacher_registration_flow()
        
        # Step 2: Create admin user to approve teacher
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User'
        )
        
        # Login as admin
        admin_login = {
            'email': 'admin@example.com',
            'password': 'AdminPass123!'
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/login/',
            admin_login,
            format='json'
        )
        
        admin_tokens = response.json()['tokens']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_tokens["access"]}')
        
        # Step 3: Approve teacher application
        response = self.client.post(
            f'/api/v1/accounts/teacher-approvals/{approval.id}/approve/',
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 4: Verify teacher is now approved
        user.refresh_from_db()
        approval.refresh_from_db()
        
        self.assertTrue(user.is_approved_teacher)
        self.assertEqual(approval.status, 'approved')
        self.assertEqual(approval.reviewed_by, admin_user)
        self.assertIsNotNone(approval.reviewed_at)


class TenantAwareAuthenticationTest(APITestCase):
    """Test tenant-aware authentication features"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create multiple tenants
        self.tenant1 = Organization.objects.create(
            name="University One",
            subdomain="uni-one",
            subscription_plan="pro"
        )
        
        self.tenant2 = Organization.objects.create(
            name="University Two", 
            subdomain="uni-two",
            subscription_plan="basic"
        )
    
    def test_user_isolation_between_tenants(self):
        """Test that users are properly isolated between tenants"""
        # Create user in tenant1
        user1_data = {
            'email': 'user1@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'first_name': 'User',
            'last_name': 'One'
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/register/',
            user1_data,
            format='json',
            HTTP_HOST='uni-one.example.com'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user1_tokens = response.json()['tokens']
        
        # Create user in tenant2
        user2_data = {
            'email': 'user2@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'first_name': 'User',
            'last_name': 'Two'
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/register/',
            user2_data,
            format='json',
            HTTP_HOST='uni-two.example.com'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify users are in different tenants
        user1 = User.objects.get(email='user1@example.com')
        user2 = User.objects.get(email='user2@example.com')
        
        profile1 = UserProfile.objects.get(user=user1)
        profile2 = UserProfile.objects.get(user=user2)
        
        self.assertEqual(profile1.tenant, self.tenant1)
        self.assertEqual(profile2.tenant, self.tenant2)
        self.assertNotEqual(profile1.tenant, profile2.tenant)
    
    def test_jwt_token_contains_tenant_info(self):
        """Test that JWT tokens contain tenant information"""
        # Create user
        user_data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/register/',
            user_data,
            format='json',
            HTTP_HOST='uni-one.example.com'
        )
        
        tokens = response.json()['tokens']
        
        # Decode JWT token to verify tenant info
        import jwt
        from django.conf import settings
        
        decoded_token = jwt.decode(
            tokens['access'], 
            settings.SECRET_KEY, 
            algorithms=['HS256'],
            options={"verify_signature": False}
        )
        
        # Verify tenant information is in token
        self.assertIn('tenant_id', decoded_token)
        self.assertIn('tenant_subdomain', decoded_token)
        self.assertEqual(decoded_token['tenant_subdomain'], 'uni-one')


@pytest.mark.django_db
class AuthenticationPerformanceTest:
    """Performance tests for authentication system"""
    
    def test_bulk_user_registration_performance(self):
        """Test performance with multiple user registrations"""
        import time
        
        tenant = Organization.objects.create(
            name="Performance Test Org",
            subdomain="perf-test"
        )
        
        client = APIClient()
        
        start_time = time.time()
        
        # Register 10 users
        for i in range(10):
            user_data = {
                'email': f'user{i}@example.com',
                'password': 'Password123!',
                'password_confirm': 'Password123!',
                'first_name': f'User{i}',
                'last_name': 'Test'
            }
            
            response = client.post(
                '/api/v1/accounts/auth/register/',
                user_data,
                format='json',
                HTTP_HOST='perf-test.example.com'
            )
            
            assert response.status_code == 201
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert total_time < 5.0, f"Registration took too long: {total_time}s"
        
        # Verify all users were created
        assert User.objects.count() == 10
        assert UserProfile.objects.filter(tenant=tenant).count() == 10