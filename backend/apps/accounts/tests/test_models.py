from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from apps.accounts.models import Organization, UserProfile, TeacherApproval

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the custom User model"""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertFalse(user.is_teacher)
        self.assertFalse(user.is_approved_teacher)
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_teacher_user(self):
        """Test creating a teacher user"""
        self.user_data['is_teacher'] = True
        user = User.objects.create_user(**self.user_data)
        
        self.assertTrue(user.is_teacher)
        self.assertFalse(user.is_approved_teacher)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(**self.user_data)
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_email_unique_constraint(self):
        """Test that email must be unique"""
        User.objects.create_user(**self.user_data)
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)
    
    def test_user_string_representation(self):
        """Test the string representation of User"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'test@example.com')


class OrganizationModelTest(TestCase):
    """Test cases for the Organization model"""
    
    def setUp(self):
        self.org_data = {
            'name': 'Test University',
            'subdomain': 'testuni',
            'subscription_plan': 'pro'
        }
    
    def test_create_organization(self):
        """Test creating an organization"""
        org = Organization.objects.create(**self.org_data)
        
        self.assertEqual(org.name, 'Test University')
        self.assertEqual(org.subdomain, 'testuni')
        self.assertEqual(org.subscription_plan, 'pro')
        self.assertTrue(org.is_active)
        self.assertEqual(org.primary_color, '#3B82F6')
        self.assertEqual(org.secondary_color, '#1E40AF')
    
    def test_subdomain_unique_constraint(self):
        """Test that subdomain must be unique"""
        Organization.objects.create(**self.org_data)
        
        with self.assertRaises(IntegrityError):
            Organization.objects.create(**self.org_data)
    
    def test_organization_string_representation(self):
        """Test the string representation of Organization"""
        org = Organization.objects.create(**self.org_data)
        self.assertEqual(str(org), 'Test University')


class UserProfileModelTest(TestCase):
    """Test cases for the UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.organization = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
    
    def test_create_user_profile(self):
        """Test creating a user profile"""
        profile = UserProfile.objects.create(
            user=self.user,
            tenant=self.organization,
            bio='Test bio',
            role='student'
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.tenant, self.organization)
        self.assertEqual(profile.bio, 'Test bio')
        self.assertEqual(profile.role, 'student')
        self.assertEqual(profile.timezone, 'UTC')
        self.assertEqual(profile.language, 'en')
    
    def test_user_tenant_unique_constraint(self):
        """Test that user-tenant combination must be unique"""
        UserProfile.objects.create(
            user=self.user,
            tenant=self.organization
        )
        
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(
                user=self.user,
                tenant=self.organization
            )
    
    def test_multiple_tenants_for_user(self):
        """Test that a user can belong to multiple tenants"""
        org2 = Organization.objects.create(
            name='Demo Corp',
            subdomain='democorp',
            subscription_plan='enterprise'
        )
        
        profile1 = UserProfile.objects.create(
            user=self.user,
            tenant=self.organization
        )
        profile2 = UserProfile.objects.create(
            user=self.user,
            tenant=org2
        )
        
        self.assertEqual(self.user.profiles.count(), 2)
        self.assertIn(profile1, self.user.profiles.all())
        self.assertIn(profile2, self.user.profiles.all())
    
    def test_user_profile_string_representation(self):
        """Test the string representation of UserProfile"""
        profile = UserProfile.objects.create(
            user=self.user,
            tenant=self.organization
        )
        expected = f"{self.user.email} - {self.organization.name}"
        self.assertEqual(str(profile), expected)


class TeacherApprovalModelTest(TestCase):
    """Test cases for the TeacherApproval model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
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
        """Test creating a teacher approval request"""
        approval = TeacherApproval.objects.create(
            user=self.user,
            teaching_experience='5 years',
            qualifications='PhD in Computer Science',
            subject_expertise='Python, Django'
        )
        
        self.assertEqual(approval.user, self.user)
        self.assertEqual(approval.status, 'pending')
        self.assertEqual(approval.teaching_experience, '5 years')
        self.assertIsNone(approval.reviewed_at)
        self.assertIsNone(approval.reviewed_by)
    
    def test_approve_teacher(self):
        """Test approving a teacher application"""
        approval = TeacherApproval.objects.create(
            user=self.user,
            teaching_experience='5 years',
            qualifications='PhD in Computer Science',
            subject_expertise='Python, Django'
        )
        
        approval.approve(self.admin_user)
        
        self.assertEqual(approval.status, 'approved')
        self.assertEqual(approval.reviewed_by, self.admin_user)
        self.assertIsNotNone(approval.reviewed_at)
        
        # Check that user is now approved teacher
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_approved_teacher)
    
    def test_reject_teacher(self):
        """Test rejecting a teacher application"""
        approval = TeacherApproval.objects.create(
            user=self.user,
            teaching_experience='2 years',
            qualifications='Bachelor degree',
            subject_expertise='Basic programming'
        )
        
        approval.reject(self.admin_user, 'Insufficient experience')
        
        self.assertEqual(approval.status, 'rejected')
        self.assertEqual(approval.reviewed_by, self.admin_user)
        self.assertEqual(approval.review_notes, 'Insufficient experience')
        self.assertIsNotNone(approval.reviewed_at)
        
        # Check that user is still not approved teacher
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_approved_teacher)
    
    def test_teacher_approval_string_representation(self):
        """Test the string representation of TeacherApproval"""
        approval = TeacherApproval.objects.create(
            user=self.user,
            teaching_experience='5 years',
            qualifications='PhD in Computer Science',
            subject_expertise='Python, Django'
        )
        expected = f"{self.user.email} - pending"
        self.assertEqual(str(approval), expected)