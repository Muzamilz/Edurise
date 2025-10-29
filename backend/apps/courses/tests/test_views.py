from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from apps.accounts.models import Organization, UserProfile
from apps.courses.models import Course, Enrollment, CourseReview, Wishlist
from apps.accounts.services import JWTAuthService

User = get_user_model()


class CourseViewSetTest(TestCase):
    """Test cases for CourseViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
        
        self.instructor = User.objects.create_user(
            email='instructor@example.com',
            password='testpass123',
            first_name='John',
            last_name='Instructor',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        self.student = User.objects.create_user(
            email='student@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Student'
        )
        
        # Create profiles
        UserProfile.objects.create(user=self.instructor, tenant=self.tenant)
        UserProfile.objects.create(user=self.student, tenant=self.tenant)
        
        self.course_data = {
            'title': 'Introduction to Python',
            'description': 'Learn Python programming from scratch',
            'category': 'technology',
            'difficulty_level': 'beginner',
            'price': '99.99',
            'duration_weeks': 8,
            'max_students': 50,
            'tags': ['python', 'programming', 'beginner']
        }
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_create_course_as_instructor(self):
        """Test course creation by instructor"""
        self.authenticate_user(self.instructor)
        
        response = self.client.post(
            '/api/v1/courses/courses/',
            self.course_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify course was created
        course = Course.objects.get(title=self.course_data['title'])
        self.assertEqual(course.instructor, self.instructor)
        self.assertEqual(course.tenant, self.tenant)
    
    def test_create_course_as_student_fails(self):
        """Test that students cannot create courses"""
        self.authenticate_user(self.student)
        
        response = self.client.post(
            '/api/v1/courses/courses/',
            self.course_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_courses(self):
        """Test course listing"""
        # Create test courses
        Course.objects.create(
            title='Python Basics',
            description='Learn Python',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            price=Decimal('50.00'),
            is_public=True
        )
        
        Course.objects.create(
            title='Advanced JavaScript',
            description='Advanced JS',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            price=Decimal('100.00'),
            is_public=True
        )
        
        self.authenticate_user(self.student)
        
        response = self.client.get('/api/v1/courses/courses/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 2)
    
    def test_course_search(self):
        """Test course search functionality"""
        Course.objects.create(
            title='Python Basics',
            description='Learn Python programming',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            is_public=True
        )
        
        Course.objects.create(
            title='JavaScript Advanced',
            description='Advanced JavaScript concepts',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            is_public=True
        )
        
        self.authenticate_user(self.student)
        
        # Search by title
        response = self.client.get('/api/v1/courses/courses/?search=Python')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], 'Python Basics')
    
    def test_course_filtering(self):
        """Test course filtering by category and difficulty"""
        Course.objects.create(
            title='Python Basics',
            description='Learn Python',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            difficulty_level='beginner',
            is_public=True
        )
        
        Course.objects.create(
            title='Business Strategy',
            description='Learn business',
            instructor=self.instructor,
            tenant=self.tenant,
            category='business',
            difficulty_level='intermediate',
            is_public=True
        )
        
        self.authenticate_user(self.student)
        
        # Filter by category
        response = self.client.get('/api/v1/courses/courses/?category=technology')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        
        # Filter by difficulty
        response = self.client.get('/api/v1/courses/courses/?difficulty_level=beginner')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
    
    def test_course_enrollment(self):
        """Test course enrollment"""
        course = Course.objects.create(
            title='Enrollment Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            price=Decimal('75.00')
        )
        
        self.authenticate_user(self.student)
        
        response = self.client.post(f'/api/v1/courses/courses/{course.id}/enroll/')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify enrollment was created
        enrollment = Enrollment.objects.get(student=self.student, course=course)
        self.assertEqual(enrollment.status, 'active')
    
    def test_duplicate_enrollment_prevention(self):
        """Test that duplicate enrollments are prevented"""
        course = Course.objects.create(
            title='Duplicate Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology'
        )
        
        # Create initial enrollment
        Enrollment.objects.create(
            student=self.student,
            course=course,
            tenant=self.tenant
        )
        
        self.authenticate_user(self.student)
        
        response = self.client.post(f'/api/v1/courses/courses/{course.id}/enroll/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_course_duplicate_action(self):
        """Test course duplication action"""
        course = Course.objects.create(
            title='Original Course',
            description='Original Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            price=Decimal('99.99')
        )
        
        self.authenticate_user(self.instructor)
        
        response = self.client.post(f'/api/v1/courses/courses/{course.id}/duplicate/')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify duplicate was created
        duplicated_course = Course.objects.get(title='Original Course (Copy)')
        self.assertEqual(duplicated_course.instructor, self.instructor)
        self.assertEqual(duplicated_course.description, 'Original Description')
    
    def test_course_statistics_action(self):
        """Test course statistics action"""
        course = Course.objects.create(
            title='Statistics Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology'
        )
        
        # Create some enrollments
        student2 = User.objects.create_user(
            email='student2@example.com',
            password='testpass123'
        )
        
        Enrollment.objects.create(
            student=self.student,
            course=course,
            tenant=self.tenant,
            progress_percentage=75
        )
        Enrollment.objects.create(
            student=student2,
            course=course,
            tenant=self.tenant,
            progress_percentage=100,
            status='completed'
        )
        
        self.authenticate_user(self.instructor)
        
        response = self.client.get(f'/api/v1/courses/courses/{course.id}/statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['total_enrollments'], 2)
        self.assertEqual(data['completed_enrollments'], 1)
        self.assertEqual(data['average_progress'], 87.5)
    
    def test_course_students_action(self):
        """Test course students action"""
        course = Course.objects.create(
            title='Students Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology'
        )
        
        # Create enrollments
        Enrollment.objects.create(
            student=self.student,
            course=course,
            tenant=self.tenant
        )
        
        self.authenticate_user(self.instructor)
        
        response = self.client.get(f'/api/v1/courses/courses/{course.id}/students/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['student']['email'], self.student.email)


class EnrollmentViewSetTest(TestCase):
    """Test cases for EnrollmentViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
        
        self.instructor = User.objects.create_user(
            email='instructor@example.com',
            password='testpass123',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        self.student = User.objects.create_user(
            email='student@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.instructor, tenant=self.tenant)
        UserProfile.objects.create(user=self.student, tenant=self.tenant)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology'
        )
        
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.tenant
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_update_enrollment_progress(self):
        """Test updating enrollment progress"""
        self.authenticate_user(self.student)
        
        response = self.client.patch(
            f'/api/v1/courses/enrollments/{self.enrollment.id}/update_progress/',
            {'progress_percentage': 75},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify progress was updated
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 75)
    
    def test_complete_enrollment(self):
        """Test completing enrollment (100% progress)"""
        self.authenticate_user(self.student)
        
        response = self.client.patch(
            f'/api/v1/courses/enrollments/{self.enrollment.id}/update_progress/',
            {'progress_percentage': 100},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify enrollment is completed
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 100)
        self.assertEqual(self.enrollment.status, 'completed')
        self.assertIsNotNone(self.enrollment.completed_at)


class WishlistViewSetTest(TestCase):
    """Test cases for WishlistViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
        
        self.instructor = User.objects.create_user(
            email='instructor@example.com',
            password='testpass123',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        self.student = User.objects.create_user(
            email='student@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.instructor, tenant=self.tenant)
        UserProfile.objects.create(user=self.student, tenant=self.tenant)
        
        self.course = Course.objects.create(
            title='Wishlist Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            price=Decimal('99.99')
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_add_course_to_wishlist(self):
        """Test adding course to wishlist"""
        self.authenticate_user(self.student)
        
        response = self.client.post(
            '/api/v1/courses/wishlist/add_course/',
            {'course_id': str(self.course.id)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify wishlist item was created
        wishlist_item = Wishlist.objects.get(user=self.student, course=self.course)
        self.assertEqual(wishlist_item.tenant, self.tenant)
    
    def test_remove_course_from_wishlist(self):
        """Test removing course from wishlist"""
        # Add course to wishlist first
        Wishlist.objects.create(
            user=self.student,
            course=self.course,
            tenant=self.tenant
        )
        
        self.authenticate_user(self.student)
        
        response = self.client.delete(
            '/api/v1/courses/wishlist/remove_course/',
            {'course_id': str(self.course.id)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify wishlist item was removed
        self.assertFalse(
            Wishlist.objects.filter(user=self.student, course=self.course).exists()
        )
    
    def test_list_wishlist_items(self):
        """Test listing wishlist items"""
        # Add course to wishlist
        Wishlist.objects.create(
            user=self.student,
            course=self.course,
            tenant=self.tenant
        )
        
        self.authenticate_user(self.student)
        
        response = self.client.get('/api/v1/courses/wishlist/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['course']['title'], self.course.title)