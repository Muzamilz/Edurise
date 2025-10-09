from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import Organization, UserProfile
from apps.courses.models import Course, Enrollment, CourseModule, CourseReview
from apps.accounts.services import JWTAuthService

User = get_user_model()


class SimpleCourseIntegrationTest(TestCase):
    """Simplified integration tests for course management system"""
    
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
            email='instructor@test.com',
            password='testpass123',
            first_name='John',
            last_name='Instructor',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        UserProfile.objects.create(user=self.instructor, tenant=self.tenant)
        
        # Create student
        self.student = User.objects.create_user(
            email='student@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Student'
        )
        
        UserProfile.objects.create(user=self.student, tenant=self.tenant)
    
    def test_course_creation_and_enrollment_workflow(self):
        """Test complete course creation and student enrollment workflow"""
        # Step 1: Instructor creates course
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        course_data = {
            'title': 'Python Programming',
            'description': 'Learn Python basics',
            'category': 'technology',
            'difficulty_level': 'beginner',
            'price': 99.99,
            'duration_weeks': 8,
            'tags': ['python', 'programming'],
            'is_public': True
        }
        
        response = self.client.post('/api/v1/courses/courses/', course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        course_id = response.data['id']
        
        # Verify course was created
        course = Course.objects.get(id=course_id)
        self.assertEqual(course.title, 'Python Programming')
        self.assertEqual(course.instructor, self.instructor)
        
        # Step 2: Add course modules
        module_data = {
            'course': course_id,
            'title': 'Introduction',
            'description': 'Course introduction',
            'content': 'Welcome to Python',
            'order': 1,
            'is_published': True
        }
        
        response = self.client.post('/api/v1/courses/modules/', module_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 3: Student enrolls in course
        tokens = JWTAuthService.generate_tokens(self.student, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.post(f'/api/v1/courses/courses/{course_id}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify enrollment was created
        enrollment = Enrollment.objects.get(student=self.student, course=course)
        self.assertEqual(enrollment.status, 'active')
        self.assertEqual(enrollment.progress_percentage, 0)
        
        # Step 4: Student updates progress
        response = self.client.patch(
            f'/api/v1/courses/enrollments/{enrollment.id}/update_progress/',
            {'progress_percentage': 50},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.progress_percentage, 50)
        
        # Step 5: Student completes course
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
        
        # Step 6: Student leaves review
        review_data = {
            'course': course_id,
            'rating': 5,
            'comment': 'Great course!'
        }
        
        response = self.client.post('/api/v1/courses/reviews/', review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify review was created
        review = CourseReview.objects.get(course=course, student=self.student)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great course!')
    
    def test_course_search_and_filtering(self):
        """Test course search and filtering functionality"""
        # Create test courses
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        courses_data = [
            {
                'title': 'Python Basics',
                'description': 'Learn Python',
                'category': 'technology',
                'difficulty_level': 'beginner',
                'price': 50.00,
                'duration_weeks': 4,
                'is_public': True
            },
            {
                'title': 'JavaScript Advanced',
                'description': 'Advanced JS',
                'category': 'technology',
                'difficulty_level': 'advanced',
                'price': 100.00,
                'duration_weeks': 8,
                'is_public': True
            },
            {
                'title': 'Business Strategy',
                'description': 'Learn business',
                'category': 'business',
                'difficulty_level': 'intermediate',
                'price': 75.00,
                'duration_weeks': 6,
                'is_public': True
            }
        ]
        
        for course_data in courses_data:
            response = self.client.post('/api/v1/courses/courses/', course_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Switch to student to test filtering
        tokens = JWTAuthService.generate_tokens(self.student, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Test category filter
        response = self.client.get('/api/v1/courses/courses/?category=technology')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tech_courses = response.data['results']
        self.assertEqual(len(tech_courses), 2)
        
        # Test difficulty filter
        response = self.client.get('/api/v1/courses/courses/?difficulty_level=beginner')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        beginner_courses = response.data['results']
        self.assertEqual(len(beginner_courses), 1)
        
        # Test search
        response = self.client.get('/api/v1/courses/courses/?search=Python')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        python_courses = response.data['results']
        self.assertEqual(len(python_courses), 1)
    
    def test_instructor_course_management(self):
        """Test instructor course management features"""
        # Create course
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        course_data = {
            'title': 'Test Course',
            'description': 'Test Description',
            'category': 'technology',
            'difficulty_level': 'beginner',
            'is_public': True
        }
        
        response = self.client.post('/api/v1/courses/courses/', course_data, format='json')
        course_id = response.data['id']
        
        # Test getting instructor's courses
        response = self.client.get('/api/v1/courses/courses/my_courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        my_courses = response.data['results']
        self.assertTrue(len(my_courses) > 0)
        
        # Test course update
        update_data = {'title': 'Updated Course Title'}
        response = self.client.patch(f'/api/v1/courses/courses/{course_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify update
        course = Course.objects.get(id=course_id)
        self.assertEqual(course.title, 'Updated Course Title')
        
        # Test course duplication
        response = self.client.post(f'/api/v1/courses/courses/{course_id}/duplicate/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        duplicated_course = response.data
        self.assertEqual(duplicated_course['title'], 'Updated Course Title (Copy)')
        self.assertFalse(duplicated_course['is_public'])
    
    def test_tenant_isolation(self):
        """Test that courses are properly isolated by tenant"""
        # Create course in tenant1
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        course_data = {
            'title': 'Tenant 1 Course',
            'description': 'Course in tenant 1',
            'category': 'technology',
            'difficulty_level': 'beginner',
            'is_public': True
        }
        
        response = self.client.post('/api/v1/courses/courses/', course_data, format='json')
        course_id = response.data['id']
        
        # Create another tenant
        tenant2 = Organization.objects.create(
            name="Another University",
            subdomain="another-uni",
            subscription_plan="basic"
        )
        
        instructor2 = User.objects.create_user(
            email='instructor2@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Teacher',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        UserProfile.objects.create(user=instructor2, tenant=tenant2)
        
        # Login as instructor2 (different tenant)
        tokens = JWTAuthService.generate_tokens(instructor2, tenant2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Should not see courses from tenant1
        response = self.client.get('/api/v1/courses/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        courses = response.data['results']
        self.assertEqual(len(courses), 0)
        
        # Should not be able to access course from tenant1
        response = self.client.get(f'/api/v1/courses/courses/{course_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_enrollment_analytics(self):
        """Test enrollment analytics functionality"""
        # Create course and enrollment
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        course_data = {
            'title': 'Analytics Test Course',
            'description': 'Test course for analytics',
            'category': 'technology',
            'difficulty_level': 'beginner',
            'is_public': True
        }
        
        response = self.client.post('/api/v1/courses/courses/', course_data, format='json')
        course_id = response.data['id']
        
        # Student enrolls
        tokens = JWTAuthService.generate_tokens(self.student, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.post(f'/api/v1/courses/courses/{course_id}/enroll/')
        enrollment_id = response.data['id']
        
        # Update progress to completion
        response = self.client.patch(
            f'/api/v1/courses/enrollments/{enrollment_id}/update_progress/',
            {'progress_percentage': 100},
            format='json'
        )
        
        # Test student dashboard
        response = self.client.get('/api/v1/courses/enrollments/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        dashboard = response.data
        self.assertEqual(dashboard['total_enrollments'], 1)
        self.assertEqual(dashboard['completed_courses'], 1)
        
        # Test instructor analytics
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get('/api/v1/courses/enrollments/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        analytics = response.data
        self.assertEqual(analytics['total_enrollments'], 1)
        self.assertEqual(analytics['completed_enrollments'], 1)
        self.assertEqual(analytics['completion_rate'], 100.0)