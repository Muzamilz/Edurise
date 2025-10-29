from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock
from apps.accounts.models import Organization, UserProfile
from apps.accounts.services import JWTAuthService

User = get_user_model()


class EnhancedAuthenticationTest(TestCase):
    """Test cases for enhanced authentication features"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
    
    def test_token_refresh_with_tenant_switching(self):
        """Test token refresh with tenant switching capability"""
        # Generate initial tokens
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        
        # Create another tenant
        new_tenant = Organization.objects.create(
            name='New University',
            subdomain='newuni',
            subscription_plan='basic'
        )
        
        # Add user to new tenant
        UserProfile.objects.create(user=self.user, tenant=new_tenant)
        
        # Test token refresh with tenant switch
        response = self.client.post(
            '/api/v1/accounts/auth/token/refresh/',
            {
                'refresh': tokens['refresh'],
                'tenant_id': str(new_tenant.id)
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertIn('tenant_info', data)
        self.assertEqual(data['tenant_info']['name'], 'New University')
    
    def test_token_refresh_invalid_tenant(self):
        """Test token refresh with invalid tenant"""
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        
        response = self.client.post(
            '/api/v1/accounts/auth/token/refresh/',
            {
                'refresh': tokens['refresh'],
                'tenant_id': '00000000-0000-0000-0000-000000000000'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_token_refresh_unauthorized_tenant(self):
        """Test token refresh with tenant user doesn't belong to"""
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        
        # Create tenant user doesn't belong to
        other_tenant = Organization.objects.create(
            name='Other University',
            subdomain='otheruni',
            subscription_plan='basic'
        )
        
        response = self.client.post(
            '/api/v1/accounts/auth/token/refresh/',
            {
                'refresh': tokens['refresh'],
                'tenant_id': str(other_tenant.id)
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserPreferencesTest(TestCase):
    """Test cases for user preferences management"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_get_user_preferences(self):
        """Test getting user preferences"""
        self.authenticate_user(self.user)
        
        response = self.client.get('/api/v1/users/preferences/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('notifications', data)
        self.assertIn('privacy', data)
        self.assertIn('display', data)
        self.assertIn('learning', data)
    
    def test_update_user_preferences(self):
        """Test updating user preferences"""
        self.authenticate_user(self.user)
        
        preferences = {
            'notifications': {
                'email_enabled': False,
                'push_enabled': True,
                'course_updates': True,
                'marketing': False
            },
            'privacy': {
                'profile_visibility': 'private',
                'show_online_status': False
            },
            'display': {
                'theme': 'dark',
                'language': 'en',
                'timezone': 'UTC'
            },
            'learning': {
                'auto_play_videos': True,
                'show_subtitles': True,
                'playback_speed': 1.25
            }
        }
        
        response = self.client.put(
            '/api/v1/users/preferences/',
            preferences,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify preferences were saved
        profile = UserProfile.objects.get(user=self.user, tenant=self.tenant)
        self.assertFalse(profile.preferences['notifications']['email_enabled'])
        self.assertEqual(profile.preferences['display']['theme'], 'dark')
    
    def test_partial_update_preferences(self):
        """Test partial update of user preferences"""
        self.authenticate_user(self.user)
        
        # First set some preferences
        profile = UserProfile.objects.get(user=self.user, tenant=self.tenant)
        profile.preferences = {
            'notifications': {'email_enabled': True},
            'display': {'theme': 'light'}
        }
        profile.save()
        
        # Partial update
        response = self.client.patch(
            '/api/v1/users/preferences/',
            {
                'notifications': {
                    'email_enabled': False,
                    'push_enabled': True
                }
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify partial update
        profile.refresh_from_db()
        self.assertFalse(profile.preferences['notifications']['email_enabled'])
        self.assertTrue(profile.preferences['notifications']['push_enabled'])
        self.assertEqual(profile.preferences['display']['theme'], 'light')  # Should remain unchanged


class TenantSwitchingTest(TestCase):
    """Test cases for multi-tenant switching"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant1 = Organization.objects.create(
            name='University A',
            subdomain='unia',
            subscription_plan='pro'
        )
        
        self.tenant2 = Organization.objects.create(
            name='University B',
            subdomain='unib',
            subscription_plan='basic'
        )
        
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        
        # User belongs to both tenants
        UserProfile.objects.create(user=self.user, tenant=self.tenant1)
        UserProfile.objects.create(user=self.user, tenant=self.tenant2)
    
    def authenticate_user(self, user, tenant):
        """Helper method to authenticate user with specific tenant"""
        tokens = JWTAuthService.generate_tokens(user, tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_switch_tenant_success(self):
        """Test successful tenant switching"""
        self.authenticate_user(self.user, self.tenant1)
        
        response = self.client.post(
            '/api/v1/users/switch_tenant/',
            {
                'tenant_id': str(self.tenant2.id)
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertIn('tenant_info', data)
        self.assertEqual(data['tenant_info']['name'], 'University B')
    
    def test_switch_to_unauthorized_tenant(self):
        """Test switching to tenant user doesn't belong to"""
        self.authenticate_user(self.user, self.tenant1)
        
        # Create tenant user doesn't belong to
        unauthorized_tenant = Organization.objects.create(
            name='Unauthorized Uni',
            subdomain='unauth',
            subscription_plan='basic'
        )
        
        response = self.client.post(
            '/api/v1/users/switch_tenant/',
            {
                'tenant_id': str(unauthorized_tenant.id)
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_switch_tenant_invalid_id(self):
        """Test switching with invalid tenant ID"""
        self.authenticate_user(self.user, self.tenant1)
        
        response = self.client.post(
            '/api/v1/users/switch_tenant/',
            {
                'tenant_id': '00000000-0000-0000-0000-000000000000'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_user_tenants(self):
        """Test getting list of user's tenants"""
        self.authenticate_user(self.user, self.tenant1)
        
        response = self.client.get('/api/v1/users/tenants/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(len(data), 2)
        tenant_names = [tenant['name'] for tenant in data]
        self.assertIn('University A', tenant_names)
        self.assertIn('University B', tenant_names)


class GDPRComplianceTest(TestCase):
    """Test cases for GDPR compliance features"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    @patch('apps.accounts.services.GDPRService.export_user_data')
    def test_export_user_data(self, mock_export_data):
        """Test GDPR data export"""
        mock_export_data.return_value = {
            'user_info': {
                'email': 'user@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'date_joined': '2024-01-01T00:00:00Z'
            },
            'profile_data': {
                'preferences': {},
                'tenant_memberships': ['Test University']
            },
            'activity_data': {
                'courses_enrolled': [],
                'files_uploaded': [],
                'payments_made': []
            }
        }
        
        self.authenticate_user(self.user)
        
        response = self.client.get('/api/v1/users/export-data/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('user_info', data)
        self.assertIn('profile_data', data)
        self.assertIn('activity_data', data)
        mock_export_data.assert_called_once_with(self.user)
    
    @patch('apps.accounts.services.AccountDeletionService.initiate_account_deletion')
    def test_delete_account_request(self, mock_delete_account):
        """Test account deletion request"""
        mock_delete_account.return_value = {
            'deletion_id': 'del_123456',
            'scheduled_date': '2024-02-01T00:00:00Z',
            'grace_period_days': 30
        }
        
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/users/delete-account/',
            {
                'reason': 'No longer needed',
                'confirm_deletion': True
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('deletion_id', data)
        self.assertIn('scheduled_date', data)
        self.assertIn('grace_period_days', data)
        mock_delete_account.assert_called_once()
    
    def test_delete_account_without_confirmation(self):
        """Test account deletion without confirmation"""
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/users/delete-account/',
            {
                'reason': 'No longer needed',
                'confirm_deletion': False
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SocialAuthenticationTest(TestCase):
    """Test cases for social authentication (Google OAuth)"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
    
    @patch('apps.accounts.services.GoogleOAuthService.verify_google_token')
    @patch('apps.accounts.services.SocialAuthService.create_or_update_user')
    def test_google_oauth_login_new_user(self, mock_create_user, mock_verify_token):
        """Test Google OAuth login for new user"""
        mock_verify_token.return_value = {
            'email': 'newuser@gmail.com',
            'first_name': 'New',
            'last_name': 'User',
            'picture': 'https://example.com/avatar.jpg',
            'email_verified': True
        }
        
        new_user = User.objects.create_user(
            email='newuser@gmail.com',
            first_name='New',
            last_name='User'
        )
        
        mock_create_user.return_value = (new_user, True)  # True indicates new user
        
        response = self.client.post(
            '/api/v1/accounts/auth/google/',
            {
                'access_token': 'google_access_token_123',
                'tenant_subdomain': 'testuni'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertIn('user', data)
        self.assertTrue(data['is_new_user'])
    
    @patch('apps.accounts.services.GoogleOAuthService.verify_google_token')
    @patch('apps.accounts.services.SocialAuthService.create_or_update_user')
    def test_google_oauth_login_existing_user(self, mock_create_user, mock_verify_token):
        """Test Google OAuth login for existing user"""
        existing_user = User.objects.create_user(
            email='existing@gmail.com',
            first_name='Existing',
            last_name='User'
        )
        
        UserProfile.objects.create(user=existing_user, tenant=self.tenant)
        
        mock_verify_token.return_value = {
            'email': 'existing@gmail.com',
            'first_name': 'Existing',
            'last_name': 'User',
            'picture': 'https://example.com/avatar.jpg',
            'email_verified': True
        }
        
        mock_create_user.return_value = (existing_user, False)  # False indicates existing user
        
        response = self.client.post(
            '/api/v1/accounts/auth/google/',
            {
                'access_token': 'google_access_token_123',
                'tenant_subdomain': 'testuni'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertIn('user', data)
        self.assertFalse(data['is_new_user'])
    
    @patch('apps.accounts.services.GoogleOAuthService.verify_google_token')
    def test_google_oauth_invalid_token(self, mock_verify_token):
        """Test Google OAuth with invalid token"""
        mock_verify_token.side_effect = Exception("Invalid token")
        
        response = self.client.post(
            '/api/v1/accounts/auth/google/',
            {
                'access_token': 'invalid_token',
                'tenant_subdomain': 'testuni'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_google_oauth_missing_token(self):
        """Test Google OAuth without access token"""
        response = self.client.post(
            '/api/v1/accounts/auth/google/',
            {
                'tenant_subdomain': 'testuni'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_google_oauth_invalid_tenant(self):
        """Test Google OAuth with invalid tenant"""
        response = self.client.post(
            '/api/v1/accounts/auth/google/',
            {
                'access_token': 'google_access_token_123',
                'tenant_subdomain': 'nonexistent'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)