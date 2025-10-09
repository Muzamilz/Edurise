from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import Organization, UserProfile
from apps.courses.models import Course, Enrollment, CourseModule, CourseReview
from apps.courses.services import CourseService, EnrollmentService
from apps.accounts.services import JWTAuthService

User = get_user_model()


class AdvancedCourseTest(TestCase):
    """Advanced course tests for new features"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test tenant
        self.tenant = Organization.objects.create(
            name="Advanced Test University",
            subdomain="advanced-test",
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
        
        UserProfile.objects.create(user=self.instructor, tenant=self.tenant)
        
        # Create students
        self.student1 = User.objects.create_user(
            email='student1@example.com',
            password='password123',
            first_name='Jane',
            last_name='Student'
        )
        
        self.student2 = User.objects.create_user(
            email='student2@example.com',
            password='password123',
            first_name='Bob',
            last_name='Learner'
        )
        
        UserProfile.objects.create(user=self.student1, tenant=self.tenant)
        UserProfile.objects.create(user=self.student2, tenant=self.tenant)
        
        # Create test courses
        self.course1 = Course.objects.create(
            title='Python Programming',
            description='Learn Python from scratch',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            difficulty_level='beginner',
            price=99.99,
            tags=['python', 'programming', 'beginner']
        )
        
        self.course2 = Course.objects.create(
            title='Advanced JavaScript',
            description='Master JavaScript concepts',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            difficulty_level='advanced',
            price=149.99,
            tags=['javascript', 'web', 'advanced']
        )
    
    def test_course_categories_endpoint(self):
        """Test course categories with counts"""
        # Login as student
        tokens = JWTAuthService.generate_tokens(self.student1, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get('/api/v1/courses/courses/categories/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should have technology category with 2 courses
        tech_category = next((cat for cat in data if cat['category'] == 'technology'), None)
        self.assertIsNotNone(tech_category)
        self.assertEqual(tech_category['count'], 2)
    
    def test_featured_courses_endpoint(self):
        """Test featured courses endpoint"""
        # Create enrollments to make courses popular
        Enrollment.objects.create(student=self.student1, course=self.course1, tenant=self.tenant)
        Enrollment.objects.create(student=self.student2, course=self.course1, tenant=self.tenant)
        
        # Create reviews to make courses highly rated
        CourseReview.objects.create(
            course=self.course1,
            student=self.student1,
            rating=5,
            comment='Excellent!',
            is_approved=True
        )
        
        # Make courses public
        self.course1.is_public = True
        self.course1.save()
        
        # Login as student
        tokens = JWTAuthService.generate_tokens(self.student1, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get('/api/v1/courses/courses/featured/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should include the highly rated course
        self.assertTrue(len(data) > 0)
    
    def test_my_courses_endpoint(self):
        """Test instructor's courses endpoint"""
        # Login as instructor
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get('/api/v1/courses/courses/my_courses/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should return instructor's courses
        self.assertEqual(len(data['results']), 2)
        course_titles = [course['title'] for course in data['results']]
        self.assertIn('Python Programming', course_titles)
        self.assertIn('Advanced JavaScript', course_titles)
    
    def test_enrolled_courses_endpoint(self):
        """Test student's enrolled courses endpoint"""
        # Create enrollment
        Enrollment.objects.create(student=self.student1, course=self.course1, tenant=self.tenant)
        
        # Login as student
        tokens = JWTAuthService.generate_tokens(self.student1, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get('/api/v1/courses/courses/enrolled_courses/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should return enrolled courses
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Python Programming')
    
    def test_course_duplication(self):
        """Test course duplication functionality"""
        # Login as instructor
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Create modules for the original course
        CourseModule.objects.create(
            course=self.course1,
            title='Introduction',
            description='Course introduction',
            content='Welcome to the course',
            order=1,
            is_published=True
        )
        
        response = self.client.post(f'/api/v1/courses/courses/{self.course1.id}/duplicate/')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        
        # Verify duplicate course was created
        self.assertEqual(data['title'], 'Python Programming (Copy)')
        self.assertEqual(data['instructor'], str(self.instructor.id))
        self.assertFalse(data['is_public'])  # Should start as private
        
        # Verify modules were duplicated
        duplicate_course = Course.objects.get(id=data['id'])
        self.assertEqual(duplicate_course.modules.count(), 1)
        self.assertFalse(duplicate_course.modules.first().is_published)  # Should start unpublished
    
    def test_course_statistics(self):
        """Test course statistics endpoint"""
        # Create enrollments and reviews
        enrollment1 = Enrollment.objects.create(
            student=self.student1, 
            course=self.course1, 
            tenant=self.tenant,
            progress_percentage=75
        )
        enrollment2 = Enrollment.objects.create(
            student=self.student2, 
            course=self.course1, 
            tenant=self.tenant,
            progress_percentage=100,
            status='completed'
        )
        
        CourseReview.objects.create(
            course=self.course1,
            student=self.student1,
            rating=4,
            is_approved=True
        )
        CourseReview.objects.create(
            course=self.course1,
            student=self.student2,
            rating=5,
            is_approved=True
        )
        
        # Login as instructor
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(f'/api/v1/courses/courses/{self.course1.id}/statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify statistics
        self.assertEqual(data['total_enrollments'], 2)
        self.assertEqual(data['active_enrollments'], 1)
        self.assertEqual(data['completed_enrollments'], 1)
        self.assertEqual(data['completion_rate'], 50.0)
        self.assertEqual(data['total_reviews'], 2)
        self.assertEqual(data['average_rating'], 4.5)
    
    def test_enrollment_analytics(self):
        """Test enrollment analytics for instructor"""
        # Create enrollments across multiple courses
        Enrollment.objects.create(student=self.student1, course=self.course1, tenant=self.tenant)
        Enrollment.objects.create(student=self.student2, course=self.course1, tenant=self.tenant)
        Enrollment.objects.create(student=self.student1, course=self.course2, tenant=self.tenant)
        
        # Login as instructor
        tokens = JWTAuthService.generate_tokens(self.instructor, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get('/api/v1/courses/enrollments/analytics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify analytics
        self.assertEqual(data['total_enrollments'], 3)
        self.assertEqual(data['active_enrollments'], 3)
        self.assertEqual(data['completed_enrollments'], 0)
    
    def test_student_dashboard(self):
        """Test student dashboard endpoint"""
        # Create enrollments with different progress
        enrollment1 = Enrollment.objects.create(
            student=self.student1, 
            course=self.course1, 
            tenant=self.tenant,
            progress_percentage=50
        )
        enrollment2 = Enrollment.objects.create(
            student=self.student1, 
            course=self.course2, 
            tenant=self.tenant,
            progress_percentage=100,
            status='completed'
        )
        
        # Login as student
        tokens = JWTAuthService.generate_tokens(self.student1, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get('/api/v1/courses/enrollments/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify dashboard data
        self.assertEqual(data['total_enrollments'], 2)
        self.assertEqual(data['active_courses'], 1)
        self.assertEqual(data['completed_courses'], 1)
        self.assertEqual(data['average_progress'], 75.0)
    
    def test_advanced_course_filtering(self):
        """Test advanced course filtering features"""
        # Create courses with different attributes
        Course.objects.create(
            title='Free Python Course',
            description='Free course',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            price=0,  # Free course
            tags=['python', 'free']
        )
        
        # Login as student
        tokens = JWTAuthService.generate_tokens(self.student1, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        # Test free courses filter
        response = self.client.get('/api/v1/courses/courses/?is_free=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], 'Free Python Course')
        
        # Test tags filter
        response = self.client.get('/api/v1/courses/courses/?tags=python,programming')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(len(data['results']) >= 2)  # Should include courses with python or programming tags
        
        # Test instructor name filter
        response = self.client.get('/api/v1/courses/courses/?instructor_name=John')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(len(data['results']) >= 3)  # All courses by John Instructor
    
    def test_course_service_methods(self):
        """Test CourseService methods directly"""
        # Create test data
        enrollment = Enrollment.objects.create(
            student=self.student1, 
            course=self.course1, 
            tenant=self.tenant,
            progress_percentage=75
        )
        
        # Test course statistics
        stats = CourseService.get_course_statistics(self.course1)
        self.assertEqual(stats['total_enrollments'], 1)
        self.assertEqual(stats['average_progress'], 75)
        
        # Test enrollment validation
        can_enroll, message = CourseService.can_enroll_in_course(self.student2, self.course1)
        self.assertTrue(can_enroll)
        
        # Test duplicate enrollment prevention
        can_enroll, message = CourseService.can_enroll_in_course(self.student1, self.course1)
        self.assertFalse(can_enroll)
        self.assertIn('Already enrolled', message)
    
    def test_enrollment_service_methods(self):
        """Test EnrollmentService methods directly"""
        # Test enrollment creation
        enrollment = EnrollmentService.enroll_student(
            student=self.student1,
            course=self.course1,
            tenant=self.tenant
        )
        
        self.assertEqual(enrollment.student, self.student1)
        self.assertEqual(enrollment.course, self.course1)
        self.assertEqual(enrollment.status, 'active')
        
        # Test progress update
        updated_enrollment = EnrollmentService.update_progress(enrollment, 100)
        self.assertEqual(updated_enrollment.progress_percentage, 100)
        self.assertEqual(updated_enrollment.status, 'completed')
        self.assertIsNotNone(updated_enrollment.completed_at)