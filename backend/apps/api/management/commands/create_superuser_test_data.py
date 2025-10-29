from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from apps.accounts.models import Organization, UserProfile, TeacherApproval
from apps.courses.models import Course, Enrollment
from apps.payments.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test data for super admin views'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data for super admin views...')
        
        # Create a superuser if it doesn't exist
        superuser_email = 'superadmin@edurise.com'
        if not User.objects.filter(email=superuser_email).exists():
            superuser = User.objects.create_superuser(
                email=superuser_email,
                password='superadmin123',
                first_name='Super',
                last_name='Admin'
            )
            self.stdout.write(f'Created superuser: {superuser_email}')
        else:
            superuser = User.objects.get(email=superuser_email)
            self.stdout.write(f'Superuser already exists: {superuser_email}')
        
        # Ensure we have some organizations
        if Organization.objects.count() < 3:
            orgs = [
                {'name': 'Tech University', 'subdomain': 'techuni'},
                {'name': 'Business School', 'subdomain': 'bizschool'},
                {'name': 'Art Institute', 'subdomain': 'artinst'},
            ]
            
            for org_data in orgs:
                org, created = Organization.objects.get_or_create(
                    subdomain=org_data['subdomain'],
                    defaults={
                        'name': org_data['name'],
                        'subscription_plan': random.choice(['basic', 'pro', 'enterprise']),
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f'Created organization: {org.name}')
        
        # Ensure we have some users across organizations
        organizations = Organization.objects.all()
        
        for i, org in enumerate(organizations):
            # Create some teachers
            for j in range(2):
                teacher_email = f'teacher{i+1}_{j+1}@{org.subdomain}.com'
                if not User.objects.filter(email=teacher_email).exists():
                    teacher = User.objects.create_user(
                        email=teacher_email,
                        password='teacher123',
                        first_name=f'Teacher{i+1}_{j+1}',
                        last_name='User',
                        is_teacher=True,
                        is_approved_teacher=j == 0  # Approve first teacher
                    )
                    
                    # Create profile
                    UserProfile.objects.create(
                        user=teacher,
                        tenant=org
                    )
                    
                    # Create teacher approval for unapproved teachers
                    if not teacher.is_approved_teacher:
                        TeacherApproval.objects.create(
                            user=teacher,
                            status='pending',
                            teaching_experience='5 years of teaching experience',
                            qualifications='Masters degree in subject area',
                            subject_expertise='Programming, Web Development'
                        )
                    
                    self.stdout.write(f'Created teacher: {teacher_email}')
            
            # Create some students
            for j in range(5):
                student_email = f'student{i+1}_{j+1}@{org.subdomain}.com'
                if not User.objects.filter(email=student_email).exists():
                    student = User.objects.create_user(
                        email=student_email,
                        password='student123',
                        first_name=f'Student{i+1}_{j+1}',
                        last_name='User'
                    )
                    
                    # Create profile
                    UserProfile.objects.create(
                        user=student,
                        tenant=org
                    )
                    
                    self.stdout.write(f'Created student: {student_email}')
        
        # Create some courses with categories
        teachers = User.objects.filter(is_teacher=True, is_approved_teacher=True)
        
        course_templates = [
            {
                'title': 'Complete Web Development Bootcamp',
                'category': 'technology',
                'description': 'Learn HTML, CSS, JavaScript, React, Node.js and build real-world projects',
                'tags': ['html', 'css', 'javascript', 'react', 'nodejs']
            },
            {
                'title': 'Python for Data Science',
                'category': 'technology', 
                'description': 'Master Python programming for data analysis, visualization, and machine learning',
                'tags': ['python', 'data-science', 'pandas', 'numpy', 'matplotlib']
            },
            {
                'title': 'UI/UX Design Fundamentals',
                'category': 'design',
                'description': 'Learn user interface and user experience design principles and tools',
                'tags': ['ui', 'ux', 'figma', 'design-thinking', 'prototyping']
            },
            {
                'title': 'Digital Marketing Mastery',
                'category': 'marketing',
                'description': 'Complete guide to digital marketing, SEO, social media, and analytics',
                'tags': ['seo', 'social-media', 'google-ads', 'analytics', 'content-marketing']
            },
            {
                'title': 'Business Strategy & Leadership',
                'category': 'business',
                'description': 'Develop strategic thinking and leadership skills for business success',
                'tags': ['strategy', 'leadership', 'management', 'entrepreneurship']
            },
            {
                'title': 'Machine Learning with Python',
                'category': 'technology',
                'description': 'Build intelligent systems using machine learning algorithms and Python',
                'tags': ['machine-learning', 'python', 'ai', 'tensorflow', 'scikit-learn']
            },
            {
                'title': 'Graphic Design Essentials',
                'category': 'design',
                'description': 'Master Adobe Creative Suite and design principles for visual communication',
                'tags': ['photoshop', 'illustrator', 'graphic-design', 'branding']
            },
            {
                'title': 'Financial Planning & Investment',
                'category': 'business',
                'description': 'Learn personal finance, investment strategies, and wealth building',
                'tags': ['finance', 'investing', 'stocks', 'retirement-planning']
            }
        ]
        
        for i, teacher in enumerate(teachers):
            org = teacher.profiles.first().tenant
            template = course_templates[i % len(course_templates)]
            course_title = f"{template['title']} - {teacher.first_name}"
            
            if not Course.objects.filter(title=course_title).exists():
                course = Course.objects.create(
                    title=course_title,
                    description=template['description'],
                    category=template['category'],
                    tags=template['tags'],
                    instructor=teacher,
                    tenant=org,
                    price=random.choice([0, 29, 49, 99, 149, 199, 299]),  # Include some free courses
                    is_public=True,
                    max_students=random.randint(20, 100),
                    duration_weeks=random.randint(4, 12),
                    difficulty_level=random.choice(['beginner', 'intermediate', 'advanced'])
                )
                
                # Create some enrollments
                students = User.objects.filter(
                    profiles__tenant=org,
                    is_teacher=False
                )[:random.randint(3, 8)]
                
                for student in students:
                    Enrollment.objects.create(
                        student=student,
                        course=course,
                        tenant=org,
                        status=random.choice(['active', 'completed']),
                        progress_percentage=random.randint(10, 100),
                        enrolled_at=timezone.now() - timedelta(days=random.randint(1, 60))
                    )
                
                # Create some course reviews
                from apps.courses.models import CourseReview
                review_students = User.objects.filter(
                    profiles__tenant=org,
                    is_teacher=False
                )[:random.randint(2, 5)]
                
                for review_student in review_students:
                    CourseReview.objects.create(
                        course=course,
                        student=review_student,
                        rating=random.randint(3, 5),
                        comment=random.choice([
                            'Great course! Learned a lot.',
                            'Excellent instructor and content.',
                            'Very practical and well-structured.',
                            'Highly recommend this course.',
                            'Good value for money.'
                        ]),
                        is_approved=True
                    )
                
                self.stdout.write(f'Created course: {course_title}')
        
        # Create some payments
        enrollments = Enrollment.objects.all()
        
        for enrollment in enrollments[:10]:  # Create payments for first 10 enrollments
            if enrollment.course.price > 0:
                Payment.objects.create(
                    user=enrollment.student,
                    tenant=enrollment.tenant,
                    amount=enrollment.course.price,
                    status='completed',
                    payment_method='stripe',
                    created_at=enrollment.enrolled_at
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully created test data for super admin views!'))
        self.stdout.write(f'Superuser login: {superuser_email} / superadmin123')