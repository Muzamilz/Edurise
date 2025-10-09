from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.accounts.models import Organization, UserProfile, TeacherApproval
from apps.accounts.services import JWTAuthService
import json

User = get_user_model()


class AuthenticationAPITest(APITestCase):
    """Test cases for authentication API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'is_teacher': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        
        # Verify user was created
        user = User.objects.get(email='test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.is_teacher)
    
    def test_user_registration_password_mismatch(self):
        """Test user registration with password mismatch"""
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_user_login(self):
        """Test user login endpoint"""
        # Create user
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
    
    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials"""
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_logout(self):
        """Test user logout endpoint"""
        # Create user and get tokens
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        tokens = JWTAuthService.generate_tokens(user)
        
        url = reverse('logout')
        data = {'refresh_token': tokens['refresh']}
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_user_logout_invalid_token(self):
        """Test user logout with invalid token"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        tokens = JWTAuthService.generate_tokens(user)
        
        url = reverse('logout')
        data = {'refresh_token': 'invalid.token.here'}
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAPITest(APITestCase):
    """Test cases for user API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
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
        
        # Authenticate user
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_get_current_user(self):
        """Test getting current user profile"""
        url = reverse('user-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'Test')
    
    def test_get_user_tenants(self):
        """Test getting user tenants"""
        url = reverse('user-tenants')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test University')
    
    def test_switch_tenant(self):
        """Test tenant switching"""
        # Create another tenant and add user to it
        tenant2 = Organization.objects.create(
            name='Demo Corp',
            subdomain='democorp',
            subscription_plan='enterprise'
        )
        UserProfile.objects.create(user=self.user, tenant=tenant2)
        
        url = reverse('user-switch-tenant')
        data = {'tenant_id': str(tenant2.id)}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('tenant', response.data)
        self.assertEqual(response.data['tenant']['name'], 'Demo Corp')
    
    def test_switch_tenant_unauthorized(self):
        """Test switching to unauthorized tenant"""
        # Create tenant user doesn't belong to
        tenant2 = Organization.objects.create(
            name='Demo Corp',
            subdomain='democorp',
            subscription_plan='enterprise'
        )
        
        url = reverse('user-switch-tenant')
        data = {'tenant_id': str(tenant2.id)}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TeacherApprovalAPITest(APITestCase):
    """Test cases for teacher approval API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com',
            password='testpass123',
            first_name='Teacher',
            last_name='User',
            is_teacher=True
        )
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
    
    def test_create_teacher_approval(self):
        """Test creating teacher approval request"""
        tokens = JWTAuthService.generate_tokens(self.teacher_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('teacherapproval-list')
        data = {
            'teaching_experience': '5 years of experience',
            'qualifications': 'PhD in Computer Science',
            'subject_expertise': 'Python, Django, Web Development',
            'portfolio_url': 'https://example.com/portfolio'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        
        # Verify approval was created
        approval = TeacherApproval.objects.get(user=self.teacher_user)
        self.assertEqual(approval.teaching_experience, '5 years of experience')
    
    def test_approve_teacher_application(self):
        """Test approving teacher application"""
        # Create approval request
        approval = TeacherApproval.objects.create(
            user=self.teacher_user,
            teaching_experience='5 years',
            qualifications='PhD in Computer Science',
            subject_expertise='Python, Django'
        )
        
        # Authenticate as admin
        tokens = JWTAuthService.generate_tokens(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('teacherapproval-approve', kwargs={'pk': approval.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify approval status changed
        approval.refresh_from_db()
        self.assertEqual(approval.status, 'approved')
        
        # Verify user is now approved teacher
        self.teacher_user.refresh_from_db()
        self.assertTrue(self.teacher_user.is_approved_teacher)
    
    def test_reject_teacher_application(self):
        """Test rejecting teacher application"""
        # Create approval request
        approval = TeacherApproval.objects.create(
            user=self.teacher_user,
            teaching_experience='1 year',
            qualifications='Bachelor degree',
            subject_expertise='Basic programming'
        )
        
        # Authenticate as admin
        tokens = JWTAuthService.generate_tokens(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        url = reverse('teacherapproval-reject', kwargs={'pk': approval.id})
        data = {'notes': 'Insufficient experience'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify approval status changed
        approval.refresh_from_db()
        self.assertEqual(approval.status, 'rejected')
        self.assertEqual(approval.review_notes, 'Insufficient experience')


class OrganizationAPITest(APITestCase):
    """Test cases for organization API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
    
    def test_get_organization_by_subdomain(self):
        """Test getting organization by subdomain"""
        url = reverse('organization-by-subdomain')
        response = self.client.get(url, {'subdomain': 'testuni'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test University')
        self.assertEqual(response.data['subdomain'], 'testuni')
    
    def test_get_organization_by_invalid_subdomain(self):
        """Test getting organization by invalid subdomain"""
        url = reverse('organization-by-subdomain')
        response = self.client.get(url, {'subdomain': 'nonexistent'})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_organization_without_subdomain(self):
        """Test getting organization without subdomain parameter"""
        url = reverse('organization-by-subdomain')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)