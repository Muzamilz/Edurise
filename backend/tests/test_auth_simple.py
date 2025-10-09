from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import Organization, UserProfile
from apps.accounts.services import JWTAuthService

User = get_user_model()


class SimpleAuthenticationTest(TestCase):
    """Simple authentication tests to verify basic functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.tenant = Organization.objects.create(
            name="Test Org",
            subdomain="test-org",
            subscription_plan="basic"
        )
        
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_user_registration(self):
        """Test basic user registration"""
        response = self.client.post(
            '/api/v1/accounts/auth/register/',
            self.user_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify user was created
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
    
    def test_user_login(self):
        """Test basic user login"""
        # Create user first
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name']
        )
        
        # Login
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/login/',
            login_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('user', data)
        self.assertIn('tokens', data)
        self.assertIn('access', data['tokens'])
        self.assertIn('refresh', data['tokens'])
    
    def test_jwt_token_generation(self):
        """Test JWT token generation service"""
        user = User.objects.create_user(
            email='jwt@example.com',
            password='password123',
            first_name='JWT',
            last_name='User'
        )
        
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertIsInstance(tokens['access'], str)
        self.assertIsInstance(tokens['refresh'], str)
    
    def test_authenticated_request(self):
        """Test making authenticated requests"""
        # Create user and get tokens
        user = User.objects.create_user(
            email='auth@example.com',
            password='password123',
            first_name='Auth',
            last_name='User'
        )
        
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        
        # Make authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get('/api/v1/accounts/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['email'], user.email)
    
    def test_password_validation(self):
        """Test password validation during registration"""
        invalid_data = self.user_data.copy()
        invalid_data['password'] = 'weak'
        invalid_data['password_confirm'] = 'weak'
        
        response = self.client.post(
            '/api/v1/accounts/auth/register/',
            invalid_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_duplicate_email_registration(self):
        """Test that duplicate email registration is prevented"""
        # Register first user
        response = self.client.post(
            '/api/v1/accounts/auth/register/',
            self.user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Try to register with same email
        response = self.client.post(
            '/api/v1/accounts/auth/register/',
            self.user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_login_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(
            '/api/v1/accounts/auth/login/',
            login_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)