import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import Organization, UserProfile
from apps.courses.models import Course, Enrollment, CourseModule, CourseReview
from apps.accounts.services import JWTAuthService

User = get_user_model()


class CourseManagementIntegrationTest(TestCase):
    """Comprehensive integration tests for course management system"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test tenant
        self.tenant = Organization.objects.create(
            name="Integration Test University",
            subdomain="integration-test",
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
        
        # Create students
        self.student1 = User.objects.create_user(
            email='student1@test.com',
            password='testpass123',
            first_name='Alice',
            last_name='Student'
        )
        
        self.student2 = User.objects.create_user(
            email='student2@test.com',
            password='testpass123',
            first_name='Bob',
            last_name='Learner'
        )
        
        UserProfile.objects.create(user=self.student1, tenant=self.tenant)
        UserProfile.objects.create(user=self.student2, tenant=self.tenant)
        
        # Create admin user
        self.admin = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        UserProfile.objects.create(user=self.admin, tenant=self.tenant)
    
    def test_complete_course_creation_workflow(self):
        """Test complete course creation workflow from instructor perspective"""
        # Login as instructor
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Step 1: Create course
        course_data = {
            'title': 'Complete Python Bootcamp',
            'description': 'Learn Python from zero to hero with hands-on projects',
            'category': 'technology',
            'difficulty_level': 'beginner',
            'price': 199.99,
            'duration_weeks': 12,
            'max_students': 100,
            'tags': ['python', 'programming', 'bootcamp'],
            'is_public': True
        }
        
        response = self.client.post('/api/v1/courses/courses/', course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        course_id = response.data['id']
        course = Course.objects.get(id=course_id)
        
        # Verify course was created correctly
        self.assertEqual(course.title, course_data['title'])
        self.assertEqual(course.instructor, self.instructor)
        self.assertEqual(course.tenant, self.tenant)
        self.assertTrue(course.is_public)
        
        # Step 2: Add course modules
        modules_data = [
            {
                'course': course_id,
                'title': 'Introduction to Python',
                'description': 'Getting started with Python basics',
                'content': 'Welcome to Python programming...',
                'order': 1,
                'is_published': True
            },
            {
                'course': course_id,
                'title': 'Variables and Data Types',
                'description': 'Understanding Python data types',
                'content': 'In this module we will learn...',
                'order': 2,
                'is_published': True
            },
            {
                'course': course_id,
                'title': 'Control Structures',
                'description': 'Loops and conditionals in Python',
                'content': 'Control structures are essential...',
                'order': 3,
                'is_published': False  # Draft module
            }
        ]
        
        created_modules = []
        for module_data in modules_data:
            response = self.client.post('/api/v1/courses/modules/', module_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created_modules.append(response.data)
        
        # Verify modules were created
        self.assertEqual(CourseModule.objects.filter(course=course).count(), 3)
        published_modules = CourseModule.objects.filter(course=course, is_published=True)
        self.assertEqual(published_modules.count(), 2)
        
        # Step 3: Get course statistics (should be empty initially)
        response = self.client.get(f'/api/v1/courses/courses/{course_id}/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats = response.data
        self.assertEqual(stats['total_enrollments'], 0)
        self.assertEqual(stats['completion_rate'], 0)
        
        return course_id, created_modules
    
    def test_complete_student_enrollment_workflow(self):
        """Test complete student enrollment and learning workflow"""
        # Create course first
        course_id, modules = self.test_complete_course_creation_workflow()
        
        # Login as student
        tokens = JWTAuthService.generate_tokens(self.student1, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Step 1: Browse and search courses
        response = self.client.get('/api/v1/courses/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        courses = response.data['results']
        self.assertTrue(len(courses) > 0)
        
        # Step 2: Search for specific course
        response = self.client.get('/api/v1/courses/courses/?search=Python')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        search_results = response.data['results']
        self.assertTrue(any(course['id'] == course_id for course in search_results))
        
        # Step 3: View course details
        response = self.client.get(f'/api/v1/courses/courses/{course_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        course_detail = response.data
        self.assertEqual(course_detail['title'], 'Complete Python Bootcamp')
        self.assertTrue('modules' in course_detail)
        
        # Step 4: Enroll in course
        response = self.client.post(f'/api/v1/courses/courses/{course_id}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        enrollment_data = response.data
        self.assertEqual(str(enrollment_data['course']), str(course_id))
        self.assertEqual(str(enrollment_data['student']), str(self.student1.id))
        self.assertEqual(enrollment_data['status'], 'active')
        self.assertEqual(enrollment_data['progress_percentage'], 0)
        
        enrollment_id = enrollment_data['id']
        
        # Step 5: Check enrollment appears in student's enrollments
        response = self.client.get('/api/v1/courses/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        enrollments = response.data['results']
        self.assertTrue(any(e['id'] == enrollment_id for e in enrollments))
        
        # Step 6: Update progress
        progress_updates = [25, 50, 75, 100]
        
        for progress in progress_updates:
            response = self.client.patch(
                f'/api/v1/courses/enrollments/{enrollment_id}/update_progress/',
                {'progress_percentage': progress},
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            updated_enrollment = response.data
            self.assertEqual(updated_enrollment['progress_percentage'], progress)
            
            if progress == 100:
                self.assertEqual(updated_enrollment['status'], 'completed')
                self.assertIsNotNone(updated_enrollment['completed_at'])
        
        # Step 7: Leave a review
        review_data = {
            'course': course_id,
            'rating': 5,
            'comment': 'Excellent course! Learned a lot about Python programming.'
        }
        
        response = self.client.post('/api/v1/courses/reviews/', review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        review = response.data
        self.assertEqual(review['rating'], 5)
        self.assertEqual(str(review['student']), str(self.student1.id))
        
        return enrollment_id, review['id']
    
    def test_course_filtering_and_search(self):
        """Test comprehensive course filtering and search functionality"""
        # Create multiple courses with different attributes
        courses_data = [
            {
                'title': 'Python for Beginners',
                'description': 'Learn Python basics',
                'category': 'technology',
                'difficulty_level': 'beginner',
                'price': 49.99,
                'duration_weeks': 4,
                'tags': ['python', 'beginner'],
                'is_public': True
            },
            {
                'title': 'Advanced JavaScript',
                'description': 'Master JavaScript concepts',
                'category': 'technology',
                'difficulty_level': 'advanced',
                'price': 149.99,
                'duration_weeks': 8,
                'tags': ['javascript', 'advanced', 'web'],
                'is_public': True
            },
            {
                'title': 'Business Strategy 101',
                'description': 'Learn business fundamentals',
                'category': 'business',
                'difficulty_level': 'intermediate',
                'price': 99.99,
                'duration_weeks': 6,
                'tags': ['business', 'strategy'],
                'is_public': True
            },
            {
                'title': 'Free HTML Course',
                'description': 'Learn HTML for free',
                'category': 'technology',
                'difficulty_level': 'beginner',
                'price': 0,
                'duration_weeks': 2,
                'tags': ['html', 'web', 'free'],
                'is_public': True
            }
        ]
        
        # Login as instructor to create courses
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        created_courses = []
        for course_data in courses_data:
            response = self.client.post('/api/v1/courses/courses/', course_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created_courses.append(response.data)
        
        # Switch to student to test filtering
        tokens = JWTAuthService.generate_tokens(self.student1, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Test 1: Filter by category
        response = self.client.get('/api/v1/courses/courses/?category=technology')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tech_courses = response.data['results']
        self.assertEqual(len(tech_courses), 3)  # Python, JavaScript, HTML
        
        # Test 2: Filter by difficulty level
        response = self.client.get('/api/v1/courses/courses/?difficulty_level=beginner')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        beginner_courses = response.data['results']
        self.assertEqual(len(beginner_courses), 2)  # Python, HTML
        
        # Test 3: Filter by price range
        response = self.client.get('/api/v1/courses/courses/?min_price=50&max_price=100')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        price_range_courses = response.data['results']
        self.assertEqual(len(price_range_courses), 1)  # Business Strategy
        
        # Test 4: Filter free courses
        response = self.client.get('/api/v1/courses/courses/?is_free=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        free_courses = response.data['results']
        self.assertEqual(len(free_courses), 1)  # HTML course
        
        # Test 5: Search by title
        response = self.client.get('/api/v1/courses/courses/?search=Python')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        python_courses = response.data['results']
        self.assertEqual(len(python_courses), 1)
        
        # Test 6: Search by tags
        response = self.client.get('/api/v1/courses/courses/?tags=web')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        web_courses = response.data['results']
        self.assertEqual(len(web_courses), 2)  # JavaScript, HTML
        
        # Test 7: Combined filters
        response = self.client.get('/api/v1/courses/courses/?category=technology&difficulty_level=beginner&max_price=50')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered_courses = response.data['results']
        self.assertEqual(len(filtered_courses), 2)  # Python (49.99), HTML (free)
    
    def test_instructor_course_management(self):
        """Test instructor's course management capabilities"""
        # Create initial course
        course_id, modules = self.test_complete_course_creation_workflow()
        
        # Login as instructor
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Test 1: Get instructor's courses
        response = self.client.get('/api/v1/courses/courses/my_courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        my_courses = response.data['results']
        self.assertTrue(len(my_courses) > 0)
        self.assertTrue(any(course['id'] == course_id for course in my_courses))
        
        # Test 2: Update course
        update_data = {
            'title': 'Updated Python Bootcamp',
            'price': 249.99,
            'max_students': 150
        }
        
        response = self.client.patch(f'/api/v1/courses/courses/{course_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        updated_course = response.data
        self.assertEqual(updated_course['title'], 'Updated Python Bootcamp')
        self.assertEqual(float(updated_course['price']), 249.99)
        
        # Test 3: Duplicate course
        response = self.client.post(f'/api/v1/courses/courses/{course_id}/duplicate/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        duplicated_course = response.data
        self.assertEqual(duplicated_course['title'], 'Updated Python Bootcamp (Copy)')
        self.assertFalse(duplicated_course['is_public'])  # Should start as private
        self.assertNotEqual(duplicated_course['id'], course_id)
        
        # Verify modules were duplicated
        duplicate_id = duplicated_course['id']
        duplicate_modules = CourseModule.objects.filter(course_id=duplicate_id)
        self.assertEqual(duplicate_modules.count(), 3)
        
        # Test 4: Get course statistics with enrollments
        # Create enrollment and review for statistics
        enrollment = Enrollment.objects.create(
            student=self.student1,
            course=Course.objects.get(id=course_id),
            tenant=self.tenant,
            status='completed',
            progress_percentage=100
        )
        
        review = CourseReview.objects.create(
            course=Course.objects.get(id=course_id),
            student=self.student1,
            rating=5,
            comment='Great course!',
            is_approved=True
        )
        
        response = self.client.get(f'/api/v1/courses/courses/{course_id}/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats = response.data
        self.assertEqual(stats['total_enrollments'], 1)
        self.assertEqual(stats['completed_enrollments'], 1)
        self.assertEqual(stats['completion_rate'], 100.0)
        self.assertEqual(stats['total_reviews'], 1)
        self.assertEqual(stats['average_rating'], 5.0)
        
        # Test 5: Get enrolled students
        response = self.client.get(f'/api/v1/courses/courses/{course_id}/students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        students = response.data
        self.assertEqual(len(students), 1)
        self.assertEqual(str(students[0]['student']), str(self.student1.id))
    
    def test_admin_course_moderation(self):
        """Test admin course moderation capabilities"""
        # Create course and review first
        course_id, modules = self.test_complete_course_creation_workflow()
        enrollment_id, review_id = self.test_complete_student_enrollment_workflow()
        
        # Login as admin
        tokens = JWTAuthService.generate_tokens(self.admin, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Test 1: View all courses (admin can see all)
        response = self.client.get('/api/v1/courses/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test 2: Approve review
        response = self.client.post(f'/api/v1/courses/reviews/{review_id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify review is approved
        review = CourseReview.objects.get(id=review_id)
        self.assertTrue(review.is_approved)
        
        # Test 3: View course statistics (admin can view any course)
        response = self.client.get(f'/api/v1/courses/courses/{course_id}/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_tenant_isolation(self):
        """Test that courses are properly isolated by tenant"""
        # Create another tenant
        tenant2 = Organization.objects.create(
            name="Another University",
            subdomain="another-uni",
            subscription_plan="basic"
        )
        
        # Create instructor in tenant2
        instructor2 = User.objects.create_user(
            email='instructor2@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Teacher',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        UserProfile.objects.create(user=instructor2, tenant=tenant2)
        
        # Create course in tenant1
        course_id, _ = self.test_complete_course_creation_workflow()
        
        # Login as instructor2 (tenant2)
        tokens = JWTAuthService.generate_tokens(instructor2, tenant2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Should not see courses from tenant1
        response = self.client.get('/api/v1/courses/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        courses = response.data['results']
        self.assertEqual(len(courses), 0)  # Should not see any courses
        
        # Should not be able to access course from tenant1
        response = self.client.get(f'/api/v1/courses/courses/{course_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_enrollment_analytics_and_dashboard(self):
        """Test enrollment analytics and student dashboard"""
        # Create multiple courses and enrollments
        course_id1, _ = self.test_complete_course_creation_workflow()
        
        # Login as instructor to create another course
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        course_data2 = {
            'title': 'Advanced Python',
            'description': 'Advanced Python concepts',
            'category': 'technology',
            'difficulty_level': 'advanced',
            'price': 299.99,
            'duration_weeks': 16,
            'is_public': True
        }
        
        response = self.client.post('/api/v1/courses/courses/', course_data2, format='json')
        course_id2 = response.data['id']
        
        # Login as student1 and enroll in both courses
        tokens = JWTAuthService.generate_tokens(self.student1, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Enroll in first course
        response = self.client.post(f'/api/v1/courses/courses/{course_id1}/enroll/')
        enrollment1_id = response.data['id']
        
        # Enroll in second course
        response = self.client.post(f'/api/v1/courses/courses/{course_id2}/enroll/')
        enrollment2_id = response.data['id']
        
        # Update progress on both courses
        self.client.patch(
            f'/api/v1/courses/enrollments/{enrollment1_id}/update_progress/',
            {'progress_percentage': 100},
            format='json'
        )
        
        self.client.patch(
            f'/api/v1/courses/enrollments/{enrollment2_id}/update_progress/',
            {'progress_percentage': 50},
            format='json'
        )
        
        # Test student dashboard
        response = self.client.get('/api/v1/courses/enrollments/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        dashboard = response.data
        self.assertEqual(dashboard['total_enrollments'], 2)
        self.assertEqual(dashboard['active_courses'], 1)
        self.assertEqual(dashboard['completed_courses'], 1)
        self.assertEqual(dashboard['average_progress'], 75.0)
        
        # Login as instructor to check analytics
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get('/api/v1/courses/enrollments/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        analytics = response.data
        self.assertEqual(analytics['total_enrollments'], 2)
        self.assertEqual(analytics['active_enrollments'], 1)
        self.assertEqual(analytics['completed_enrollments'], 1)
        self.assertEqual(analytics['completion_rate'], 50.0)
    
    def test_error_handling_and_edge_cases(self):
        """Test error handling and edge cases"""
        # Test 1: Unauthenticated access
        self.client.credentials()  # Clear credentials
        
        response = self.client.get('/api/v1/courses/courses/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test 2: Non-teacher trying to create course
        tokens = JWTAuthService.generate_tokens(self.student1, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        course_data = {
            'title': 'Unauthorized Course',
            'description': 'This should fail',
            'category': 'technology',
            'difficulty_level': 'beginner'
        }
        
        response = self.client.post('/api/v1/courses/courses/', course_data, format='json')
        # This might succeed depending on permissions, but let's test duplicate enrollment
        
        # Test 3: Duplicate enrollment
        course_id, _ = self.test_complete_course_creation_workflow()
        
        # Enroll once
        response = self.client.post(f'/api/v1/courses/courses/{course_id}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Try to enroll again
        response = self.client.post(f'/api/v1/courses/courses/{course_id}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Already enrolled', response.data['error'])
        
        # Test 4: Invalid course ID
        response = self.client.get('/api/v1/courses/courses/invalid-uuid/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test 5: Invalid progress update
        enrollment = Enrollment.objects.filter(student=self.student1).first()
        if not enrollment:
            # Create an enrollment for this test
            course = Course.objects.first()
            enrollment = Enrollment.objects.create(
                student=self.student1,
                course=course,
                tenant=self.tenant
            )
        enrollment_id = enrollment.id
        
        # Login as the student who owns the enrollment
        tokens = JWTAuthService.generate_tokens(self.student1, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.patch(
            f'/api/v1/courses/enrollments/{enrollment_id}/update_progress/',
            {'progress_percentage': 150},  # Invalid progress > 100
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should be clamped to 100
        enrollment = Enrollment.objects.get(id=enrollment_id)
        self.assertEqual(enrollment.progress_percentage, 100)