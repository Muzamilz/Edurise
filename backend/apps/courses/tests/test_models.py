from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from decimal import Decimal
from apps.accounts.models import Organization, UserProfile
from apps.courses.models import (
    Course, CourseModule, Enrollment, CourseReview, 
    Assignment, Submission, Certificate, Wishlist
)

User = get_user_model()


class CourseModelTest(TestCase):
    """Test cases for the Course model"""
    
    def setUp(self):
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
        
        UserProfile.objects.create(
            user=self.instructor,
            tenant=self.tenant
        )
        
        self.course_data = {
            'title': 'Introduction to Python',
            'description': 'Learn Python programming from scratch',
            'instructor': self.instructor,
            'tenant': self.tenant,
            'category': 'technology',
            'difficulty_level': 'beginner',
            'price': Decimal('99.99'),
            'duration_weeks': 8,
            'max_students': 50
        }
    
    def test_create_course(self):
        """Test creating a course"""
        course = Course.objects.create(**self.course_data)
        
        self.assertEqual(course.title, 'Introduction to Python')
        self.assertEqual(course.instructor, self.instructor)
        self.assertEqual(course.tenant, self.tenant)
        self.assertEqual(course.category, 'technology')
        self.assertEqual(course.difficulty_level, 'beginner')
        self.assertEqual(course.price, Decimal('99.99'))
        self.assertEqual(course.duration_weeks, 8)
        self.assertEqual(course.max_students, 50)
        self.assertTrue(course.is_active)
        self.assertFalse(course.is_public)
    
    def test_course_string_representation(self):
        """Test the string representation of Course"""
        course = Course.objects.create(**self.course_data)
        self.assertEqual(str(course), 'Introduction to Python')
    
    def test_course_slug_generation(self):
        """Test that course slug is generated automatically"""
        course = Course.objects.create(**self.course_data)
        self.assertEqual(course.slug, 'introduction-to-python')
    
    def test_course_enrollment_count(self):
        """Test course enrollment count calculation"""
        course = Course.objects.create(**self.course_data)
        
        # Initially no enrollments
        self.assertEqual(course.enrollment_count, 0)
        
        # Create students and enrollments
        student1 = User.objects.create_user(
            email='student1@example.com',
            password='testpass123'
        )
        student2 = User.objects.create_user(
            email='student2@example.com',
            password='testpass123'
        )
        
        Enrollment.objects.create(
            student=student1,
            course=course,
            tenant=self.tenant
        )
        Enrollment.objects.create(
            student=student2,
            course=course,
            tenant=self.tenant
        )
        
        # Refresh course and check count
        course.refresh_from_db()
        self.assertEqual(course.enrollment_count, 2)
    
    def test_course_average_rating(self):
        """Test course average rating calculation"""
        course = Course.objects.create(**self.course_data)
        
        # Initially no rating
        self.assertEqual(course.average_rating, 0)
        
        # Create students and reviews
        student1 = User.objects.create_user(
            email='student1@example.com',
            password='testpass123'
        )
        student2 = User.objects.create_user(
            email='student2@example.com',
            password='testpass123'
        )
        
        # Create enrollments first
        Enrollment.objects.create(
            student=student1,
            course=course,
            tenant=self.tenant
        )
        Enrollment.objects.create(
            student=student2,
            course=course,
            tenant=self.tenant
        )
        
        # Create reviews
        CourseReview.objects.create(
            student=student1,
            course=course,
            tenant=self.tenant,
            rating=4,
            comment='Good course'
        )
        CourseReview.objects.create(
            student=student2,
            course=course,
            tenant=self.tenant,
            rating=5,
            comment='Excellent course'
        )
        
        # Check average rating
        course.refresh_from_db()
        self.assertEqual(course.average_rating, 4.5)


class CourseModuleModelTest(TestCase):
    """Test cases for the CourseModule model"""
    
    def setUp(self):
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
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology'
        )
    
    def test_create_course_module(self):
        """Test creating a course module"""
        module = CourseModule.objects.create(
            course=self.course,
            title='Introduction Module',
            description='First module of the course',
            content='This is the module content',
            order=1,
            is_published=True,
            tenant=self.tenant
        )
        
        self.assertEqual(module.course, self.course)
        self.assertEqual(module.title, 'Introduction Module')
        self.assertEqual(module.order, 1)
        self.assertTrue(module.is_published)
        self.assertEqual(module.tenant, self.tenant)
    
    def test_module_ordering(self):
        """Test module ordering"""
        module1 = CourseModule.objects.create(
            course=self.course,
            title='Module 1',
            order=1,
            tenant=self.tenant
        )
        module2 = CourseModule.objects.create(
            course=self.course,
            title='Module 2',
            order=2,
            tenant=self.tenant
        )
        
        modules = CourseModule.objects.filter(course=self.course).order_by('order')
        self.assertEqual(list(modules), [module1, module2])
    
    def test_module_string_representation(self):
        """Test the string representation of CourseModule"""
        module = CourseModule.objects.create(
            course=self.course,
            title='Test Module',
            order=1,
            tenant=self.tenant
        )
        expected = f"{self.course.title} - Test Module"
        self.assertEqual(str(module), expected)


class EnrollmentModelTest(TestCase):
    """Test cases for the Enrollment model"""
    
    def setUp(self):
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
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology'
        )
    
    def test_create_enrollment(self):
        """Test creating an enrollment"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.tenant
        )
        
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertEqual(enrollment.status, 'active')
        self.assertEqual(enrollment.progress_percentage, 0)
        self.assertIsNone(enrollment.completed_at)
    
    def test_enrollment_completion(self):
        """Test enrollment completion"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.tenant
        )
        
        # Update progress to 100%
        enrollment.progress_percentage = 100
        enrollment.save()
        
        # Check that status is updated to completed
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, 'completed')
        self.assertIsNotNone(enrollment.completed_at)
    
    def test_unique_enrollment_constraint(self):
        """Test that student can only enroll once per course"""
        Enrollment.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.tenant
        )
        
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(
                student=self.student,
                course=self.course,
                tenant=self.tenant
            )
    
    def test_enrollment_string_representation(self):
        """Test the string representation of Enrollment"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.tenant
        )
        expected = f"{self.student.email} - {self.course.title}"
        self.assertEqual(str(enrollment), expected)


class CourseReviewModelTest(TestCase):
    """Test cases for the CourseReview model"""
    
    def setUp(self):
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
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology'
        )
        
        # Create enrollment first
        Enrollment.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.tenant
        )
    
    def test_create_course_review(self):
        """Test creating a course review"""
        review = CourseReview.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.tenant,
            rating=5,
            comment='Excellent course! Highly recommended.'
        )
        
        self.assertEqual(review.student, self.student)
        self.assertEqual(review.course, self.course)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excellent course! Highly recommended.')
    
    def test_rating_validation(self):
        """Test rating validation (should be between 1 and 5)"""
        # Valid rating
        review = CourseReview.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.tenant,
            rating=3,
            comment='Average course'
        )
        self.assertEqual(review.rating, 3)
    
    def test_unique_review_constraint(self):
        """Test that student can only review a course once"""
        CourseReview.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.tenant,
            rating=5,
            comment='Great course'
        )
        
        with self.assertRaises(IntegrityError):
            CourseReview.objects.create(
                student=self.student,
                course=self.course,
                tenant=self.tenant,
                rating=4,
                comment='Another review'
            )
    
    def test_review_string_representation(self):
        """Test the string representation of CourseReview"""
        review = CourseReview.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.tenant,
            rating=5,
            comment='Great course'
        )
        expected = f"{self.student.email} - {self.course.title} (5/5)"
        self.assertEqual(str(review), expected)


class WishlistModelTest(TestCase):
    """Test cases for the Wishlist model"""
    
    def setUp(self):
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
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.instructor,
            tenant=self.tenant,
            category='technology',
            price=Decimal('99.99')
        )
    
    def test_create_wishlist_item(self):
        """Test creating a wishlist item"""
        wishlist_item = Wishlist.objects.create(
            user=self.student,
            course=self.course,
            tenant=self.tenant
        )
        
        self.assertEqual(wishlist_item.user, self.student)
        self.assertEqual(wishlist_item.course, self.course)
        self.assertEqual(wishlist_item.tenant, self.tenant)
    
    def test_unique_wishlist_constraint(self):
        """Test that user can only add a course to wishlist once"""
        Wishlist.objects.create(
            user=self.student,
            course=self.course,
            tenant=self.tenant
        )
        
        with self.assertRaises(IntegrityError):
            Wishlist.objects.create(
                user=self.student,
                course=self.course,
                tenant=self.tenant
            )
    
    def test_wishlist_string_representation(self):
        """Test the string representation of Wishlist"""
        wishlist_item = Wishlist.objects.create(
            user=self.student,
            course=self.course,
            tenant=self.tenant
        )
        expected = f"{self.student.email} - {self.course.title}"
        self.assertEqual(str(wishlist_item), expected)