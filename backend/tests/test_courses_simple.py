from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import Organization, UserProfile
from apps.courses.models import Course, Enrollment, CourseModule, CourseReview
from apps.accounts.services import JWTAuthService

User = get_user_model()


class SimpleCourseTest(TestCase):
    """Simple course tests to verify basic functionality"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test tenant
        self.tenant = Organization.objects.create(
            name="Test University",
            subdomain="test-uni",
            subscription_plan="pro"
        )
        
        # Create instructor
        self.instructor = User.objects.create_user(
            email='instructor@example.com',
            password='password123',
            first_name='John',
            last_name='Instructor',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        # Create instructor profile
        UserProfile.objects.create(
            user=self.instructor,
            tenant=self.tenant
        )
        
        # Create student
        self.student = User.objects.create_user(
            email='student@example.com',
            password='password123',
            first_name='Jane',
            last_name='Student'
        )
        
        # Create student profile
        UserProfile.objects.create(
            user=self.student,
            tenant=self.tenant
        )
        
        # Course data
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
    
    def test_course_creation(self):
        """Test course creation by instructor"""
        # Login as instructor
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
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
        self.assertEqual(course.category, 'technology')
    
    def test_course_listing(self):
        """Test course listing with tenant filtering"""
        # Create course
        course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            price=50.00
        )
        
        # Login as student
        tokens = JWTAuthService.generate_tokens(self.student, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get('/api/v1/courses/courses/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], 'Test Course')
    
    def test_course_enrollment(self):
        """Test student enrollment in course"""
        # Create course
        course = Course.objects.create(
            title='Enrollment Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            price=75.00
        )
        
        # Login as student
        tokens = JWTAuthService.generate_tokens(self.student, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Enroll in course
        response = self.client.post(f'/api/v1/courses/courses/{course.id}/enroll/')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify enrollment was created
        enrollment = Enrollment.objects.get(student=self.student, course=course)
        self.assertEqual(enrollment.status, 'active')
        self.assertEqual(enrollment.progress_percentage, 0)
    
    def test_duplicate_enrollment_prevention(self):
        """Test that duplicate enrollments are prevented"""
        # Create course and enrollment
        course = Course.objects.create(
            title='Duplicate Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology'
        )
        
        Enrollment.objects.create(
            student=self.student,
            course=course,
            tenant=self.tenant
        )
        
        # Login as student
        tokens = JWTAuthService.generate_tokens(self.student, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Try to enroll again
        response = self.client.post(f'/api/v1/courses/courses/{course.id}/enroll/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Already enrolled', response.json()['error'])
    
    def test_course_modules(self):
        """Test course module creation and listing"""
        # Create course
        course = Course.objects.create(
            title='Module Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology'
        )
        
        # Login as instructor
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Create module
        module_data = {
            'course': str(course.id),
            'title': 'Introduction Module',
            'description': 'First module of the course',
            'content': 'This is the module content',
            'order': 1,
            'is_published': True
        }
        
        response = self.client.post(
            '/api/v1/courses/modules/',
            module_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify module was created
        module = CourseModule.objects.get(title='Introduction Module')
        self.assertEqual(module.course, course)
        self.assertEqual(module.order, 1)
    
    def test_course_reviews(self):
        """Test course review creation"""
        # Create course and enrollment
        course = Course.objects.create(
            title='Review Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology'
        )
        
        Enrollment.objects.create(
            student=self.student,
            course=course,
            tenant=self.tenant
        )
        
        # Login as student
        tokens = JWTAuthService.generate_tokens(self.student, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Create review
        review_data = {
            'course': str(course.id),
            'rating': 5,
            'comment': 'Excellent course! Highly recommended.'
        }
        
        response = self.client.post(
            '/api/v1/courses/reviews/',
            review_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify review was created
        review = CourseReview.objects.get(course=course, student=self.student)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excellent course! Highly recommended.')
    
    def test_course_search_and_filtering(self):
        """Test course search and filtering functionality"""
        # Create multiple courses
        Course.objects.create(
            title='Python Basics',
            description='Learn Python programming',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            difficulty_level='beginner',
            price=50.00
        )
        
        Course.objects.create(
            title='Advanced JavaScript',
            description='Advanced JS concepts',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            difficulty_level='advanced',
            price=100.00
        )
        
        Course.objects.create(
            title='Business Strategy',
            description='Learn business strategy',
            instructor=self.instructor,
            tenant=self.tenant,
            category='business',
            difficulty_level='intermediate',
            price=75.00
        )
        
        # Login as student
        tokens = JWTAuthService.generate_tokens(self.student, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Test search by title
        response = self.client.get('/api/v1/courses/courses/?search=Python')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], 'Python Basics')
        
        # Test filter by category
        response = self.client.get('/api/v1/courses/courses/?category=technology')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 2)
        
        # Test filter by difficulty
        response = self.client.get('/api/v1/courses/courses/?difficulty_level=beginner')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        
        # Test price range filter
        response = self.client.get('/api/v1/courses/courses/?min_price=60&max_price=80')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], 'Business Strategy')
    
    def test_enrollment_progress_update(self):
        """Test updating enrollment progress"""
        # Create course and enrollment
        course = Course.objects.create(
            title='Progress Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology'
        )
        
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=course,
            tenant=self.tenant
        )
        
        # Login as student
        tokens = JWTAuthService.generate_tokens(self.student, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Update progress
        response = self.client.patch(
            f'/api/v1/courses/enrollments/{enrollment.id}/update_progress/',
            {'progress_percentage': 75},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify progress was updated
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.progress_percentage, 75)
        self.assertEqual(enrollment.status, 'active')
        
        # Test completion (100% progress)
        response = self.client.patch(
            f'/api/v1/courses/enrollments/{enrollment.id}/update_progress/',
            {'progress_percentage': 100},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.progress_percentage, 100)
        self.assertEqual(enrollment.status, 'completed')
        self.assertIsNotNone(enrollment.completed_at)