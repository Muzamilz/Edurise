#!/usr/bin/env python
"""
Sample data creation script for EduRise platform
"""
import os
import sys
import django
from django.utils import timezone
from datetime import timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.content.models import Testimonial, TeamMember, Announcement, FAQ, ContactInfo
from apps.courses.models import Course, Enrollment, CourseModule, CourseReview, LiveClass
from apps.assignments.models import Assignment, Submission, Certificate, CourseProgress
from apps.accounts.models import Organization, UserProfile

User = get_user_model()

def create_sample_content():
    """Create sample content data"""
    print("Creating sample content data...")
    
    # Create default organization
    organization, created = Organization.objects.get_or_create(
        subdomain='default',
        defaults={
            'name': 'EduRise Default Organization',
            'subscription_plan': 'pro'
        }
    )
    if created:
        print(f"Created organization: {organization.name}")
    
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        email='admin@edurise.com',
        defaults={
            'username': 'admin@edurise.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"Created admin user: {admin_user.email}")
    
    # Create sample users
    sample_users = []
    for i in range(5):
        email = f'user{i+1}@example.com'
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': f'User{i+1}',
                'last_name': 'Test'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            
            # Create user profile with appropriate role
            role = 'teacher' if i < 2 else 'student'  # First 2 users are teachers
            is_approved_teacher = i < 2  # First 2 users are approved teachers
            
            UserProfile.objects.create(
                user=user,
                tenant=organization,
                role=role,
                is_approved_teacher=is_approved_teacher
            )
            
        sample_users.append(user)
    
    # Create contact info
    contact_info, created = ContactInfo.objects.get_or_create(
        is_active=True,
        defaults={
            'company_name': 'EduRise Learning Platform',
            'tagline': 'Empowering Education Through Technology',
            'description': 'EduRise is a comprehensive learning management system designed to provide high-quality education through innovative technology solutions.',
            'email': 'contact@edurise.com',
            'phone': '+1 (555) 123-4567',
            'address': '123 Education Street, Learning City, LC 12345',
            'business_hours': 'Monday - Friday: 9:00 AM - 6:00 PM\nSaturday: 10:00 AM - 4:00 PM\nSunday: Closed',
            'facebook_url': 'https://facebook.com/edurise',
            'twitter_url': 'https://twitter.com/edurise',
            'linkedin_url': 'https://linkedin.com/company/edurise',
            'instagram_url': 'https://instagram.com/edurise',
            'youtube_url': 'https://youtube.com/edurise',
            'blog_url': 'https://blog.edurise.com',
            'support_url': 'https://support.edurise.com',
            'privacy_policy_url': 'https://edurise.com/privacy',
            'terms_of_service_url': 'https://edurise.com/terms'
        }
    )
    
    # Create team members
    team_data = [
        {
            'name': 'Sarah Johnson',
            'role': 'CEO & Founder',
            'department': 'leadership',
            'bio': 'Sarah has over 15 years of experience in educational technology and is passionate about making quality education accessible to everyone.',
            'email': 'sarah@edurise.com',
            'linkedin_url': 'https://linkedin.com/in/sarahjohnson',
            'status': 'published',
            'featured': True,
            'display_order': 1
        },
        {
            'name': 'Michael Chen',
            'role': 'CTO',
            'department': 'engineering',
            'bio': 'Michael leads our technical team with expertise in scalable web applications and educational software development.',
            'email': 'michael@edurise.com',
            'linkedin_url': 'https://linkedin.com/in/michaelchen',
            'status': 'published',
            'featured': True,
            'display_order': 2
        },
        {
            'name': 'Emily Rodriguez',
            'role': 'Head of Education',
            'department': 'education',
            'bio': 'Emily brings 12 years of teaching experience and curriculum development expertise to ensure our courses meet the highest educational standards.',
            'email': 'emily@edurise.com',
            'status': 'published',
            'featured': True,
            'display_order': 3
        },
        {
            'name': 'David Kim',
            'role': 'Lead Developer',
            'department': 'engineering',
            'bio': 'David specializes in full-stack development and is responsible for building robust, user-friendly learning experiences.',
            'email': 'david@edurise.com',
            'status': 'published',
            'display_order': 4
        },
        {
            'name': 'Lisa Thompson',
            'role': 'UX Designer',
            'department': 'design',
            'bio': 'Lisa focuses on creating intuitive and engaging user interfaces that enhance the learning experience for students and educators.',
            'email': 'lisa@edurise.com',
            'status': 'published',
            'display_order': 5
        }
    ]
    
    for data in team_data:
        TeamMember.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
    
    # Create testimonials
    testimonial_data = [
        {
            'user': sample_users[0],
            'content': 'EduRise has completely transformed my learning experience. The interactive courses and expert instructors make complex topics easy to understand.',
            'rating': 5,
            'status': 'published',
            'featured': True,
            'position': 'Software Developer',
            'company': 'Tech Solutions Inc.'
        },
        {
            'user': sample_users[1],
            'content': 'The live classes and recorded sessions provide flexibility that fits perfectly with my busy schedule. Highly recommended!',
            'rating': 5,
            'status': 'published',
            'featured': True,
            'position': 'Marketing Manager',
            'company': 'Digital Marketing Pro'
        },
        {
            'user': sample_users[2],
            'content': 'Outstanding platform with comprehensive courses. The certificate I earned helped me advance in my career.',
            'rating': 4,
            'status': 'published',
            'featured': True,
            'position': 'Data Analyst',
            'company': 'Analytics Corp'
        },
        {
            'user': sample_users[3],
            'content': 'Great community of learners and supportive instructors. The assignments are challenging but rewarding.',
            'rating': 5,
            'status': 'published',
            'position': 'Student',
            'company': 'University of Technology'
        },
        {
            'user': sample_users[4],
            'content': 'The course materials are well-structured and the platform is very user-friendly. Excellent value for money.',
            'rating': 4,
            'status': 'published',
            'position': 'Freelance Designer',
            'company': 'Creative Studio'
        }
    ]
    
    for data in testimonial_data:
        Testimonial.objects.get_or_create(
            user=data['user'],
            content=data['content'],
            defaults=data
        )
    
    # Create announcements
    announcement_data = [
        {
            'title': 'Welcome to EduRise 2.0!',
            'content': 'We are excited to announce the launch of EduRise 2.0 with enhanced features, improved user interface, and new course offerings. Explore our updated platform and discover new learning opportunities.',
            'category': 'general',
            'priority': 'high',
            'status': 'published',
            'featured': True,
            'show_on_homepage': True,
            'author': admin_user,
            'tags': 'platform, update, features'
        },
        {
            'title': 'New AI and Machine Learning Course Available',
            'content': 'Join our comprehensive AI and Machine Learning course designed for beginners and intermediate learners. Learn from industry experts and work on real-world projects.',
            'category': 'feature',
            'priority': 'normal',
            'status': 'published',
            'featured': True,
            'show_on_homepage': True,
            'author': admin_user,
            'tags': 'ai, machine learning, course'
        },
        {
            'title': 'Scheduled Maintenance - October 25th',
            'content': 'We will be performing scheduled maintenance on October 25th from 2:00 AM to 4:00 AM UTC. During this time, the platform may be temporarily unavailable.',
            'category': 'maintenance',
            'priority': 'normal',
            'status': 'published',
            'author': admin_user,
            'expire_at': timezone.now() + timedelta(days=7),
            'tags': 'maintenance, downtime'
        }
    ]
    
    for data in announcement_data:
        Announcement.objects.get_or_create(
            title=data['title'],
            defaults=data
        )
    
    # Create FAQs
    faq_data = [
        {
            'question': 'How do I enroll in a course?',
            'answer': 'To enroll in a course, simply browse our course catalog, select the course you want, and click the "Enroll Now" button. You can pay using various payment methods including credit card, PayPal, or bank transfer.',
            'category': 'courses',
            'status': 'published',
            'featured': True,
            'display_order': 1,
            'author': admin_user,
            'view_count': 150,
            'helpful_count': 45,
            'not_helpful_count': 3
        },
        {
            'question': 'Can I access courses on mobile devices?',
            'answer': 'Yes! EduRise is fully responsive and works on all devices including smartphones, tablets, and desktop computers. You can also download our mobile app for the best mobile experience.',
            'category': 'technical',
            'status': 'published',
            'featured': True,
            'display_order': 2,
            'author': admin_user,
            'view_count': 120,
            'helpful_count': 38,
            'not_helpful_count': 2
        },
        {
            'question': 'What payment methods do you accept?',
            'answer': 'We accept major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers. All payments are processed securely through our encrypted payment system.',
            'category': 'payments',
            'status': 'published',
            'featured': True,
            'display_order': 3,
            'author': admin_user,
            'view_count': 95,
            'helpful_count': 32,
            'not_helpful_count': 1
        },
        {
            'question': 'Do I get a certificate after completing a course?',
            'answer': 'Yes, you will receive a digital certificate upon successful completion of any course. Certificates include your name, course title, completion date, and a unique verification code.',
            'category': 'certificates',
            'status': 'published',
            'featured': True,
            'display_order': 4,
            'author': admin_user,
            'view_count': 180,
            'helpful_count': 55,
            'not_helpful_count': 2
        },
        {
            'question': 'Can I get a refund if I am not satisfied?',
            'answer': 'We offer a 30-day money-back guarantee for all courses. If you are not satisfied with your purchase, you can request a full refund within 30 days of enrollment.',
            'category': 'payments',
            'status': 'published',
            'display_order': 5,
            'author': admin_user,
            'view_count': 75,
            'helpful_count': 28,
            'not_helpful_count': 4
        }
    ]
    
    for data in faq_data:
        FAQ.objects.get_or_create(
            question=data['question'],
            defaults=data
        )
    
    print("Sample content data created successfully!")

def create_sample_courses():
    """Create sample course data"""
    print("Creating sample course data...")
    
    # Get default organization
    organization = Organization.objects.get(subdomain='default')
    
    # Get teachers
    teachers = User.objects.filter(is_teacher=True)
    if not teachers.exists():
        print("No teachers found, skipping course creation")
        return
    
    # Sample course data
    course_data = [
        {
            'title': 'Introduction to Python Programming',
            'description': 'Learn Python programming from scratch. This comprehensive course covers variables, data types, control structures, functions, and object-oriented programming.',
            'category': 'technology',
            'tags': ['python', 'programming', 'beginner'],
            'price': 99.99,
            'is_public': True,
            'max_students': 100,
            'duration_weeks': 8,
            'difficulty_level': 'beginner'
        },
        {
            'title': 'Web Development with React',
            'description': 'Master modern web development with React. Build interactive user interfaces and single-page applications using React, JSX, and modern JavaScript.',
            'category': 'technology',
            'tags': ['react', 'javascript', 'web development'],
            'price': 149.99,
            'is_public': True,
            'max_students': 80,
            'duration_weeks': 10,
            'difficulty_level': 'intermediate'
        },
        {
            'title': 'Digital Marketing Fundamentals',
            'description': 'Learn the essentials of digital marketing including SEO, social media marketing, email marketing, and analytics.',
            'category': 'marketing',
            'tags': ['digital marketing', 'seo', 'social media'],
            'price': 79.99,
            'is_public': True,
            'max_students': 150,
            'duration_weeks': 6,
            'difficulty_level': 'beginner'
        },
        {
            'title': 'Data Science with Python',
            'description': 'Dive into data science using Python. Learn data analysis, visualization, machine learning, and statistical modeling.',
            'category': 'technology',
            'tags': ['data science', 'python', 'machine learning'],
            'price': 199.99,
            'is_public': True,
            'max_students': 60,
            'duration_weeks': 12,
            'difficulty_level': 'advanced'
        },
        {
            'title': 'UI/UX Design Principles',
            'description': 'Master the principles of user interface and user experience design. Learn design thinking, prototyping, and usability testing.',
            'category': 'design',
            'tags': ['ui design', 'ux design', 'prototyping'],
            'price': 129.99,
            'is_public': True,
            'max_students': 70,
            'duration_weeks': 8,
            'difficulty_level': 'intermediate'
        }
    ]
    
    created_courses = []
    for i, data in enumerate(course_data):
        instructor = teachers[i % len(teachers)]
        course, created = Course.objects.get_or_create(
            title=data['title'],
            defaults={**data, 'instructor': instructor, 'tenant': organization}
        )
        if created:
            created_courses.append(course)
    
    # Create course modules for each course
    for course in created_courses:
        module_data = [
            {
                'title': f'Introduction to {course.title.split()[-1]}',
                'description': f'Get started with the basics of {course.title.lower()}',
                'content': 'This module introduces you to the fundamental concepts and provides an overview of what you will learn in this course.',
                'order': 1,
                'is_published': True
            },
            {
                'title': 'Core Concepts',
                'description': 'Learn the essential concepts and terminology',
                'content': 'In this module, we dive deeper into the core concepts that form the foundation of this subject.',
                'order': 2,
                'is_published': True
            },
            {
                'title': 'Practical Applications',
                'description': 'Apply what you have learned through hands-on exercises',
                'content': 'Put your knowledge into practice with real-world examples and exercises.',
                'order': 3,
                'is_published': True
            },
            {
                'title': 'Advanced Topics',
                'description': 'Explore advanced concepts and techniques',
                'content': 'Take your skills to the next level with advanced topics and best practices.',
                'order': 4,
                'is_published': True
            }
        ]
        
        for module_info in module_data:
            CourseModule.objects.get_or_create(
                course=course,
                title=module_info['title'],
                defaults=module_info
            )
    
    print(f"Created {len(created_courses)} courses with modules!")

def create_sample_assignments():
    """Create sample assignments"""
    print("Creating sample assignments...")
    
    # Get default organization
    organization = Organization.objects.get(subdomain='default')
    courses = Course.objects.all()[:3]  # Get first 3 courses
    
    for course in courses:
        assignment_data = [
            {
                'title': f'{course.title} - Assignment 1',
                'description': f'Complete the first assignment for {course.title}. This assignment tests your understanding of the basic concepts.',
                'instructions': 'Please read the course materials and complete all exercises. Submit your work as a PDF or Word document.',
                'assignment_type': 'essay',
                'max_score': 100,
                'passing_score': 70,
                'due_date': timezone.now() + timedelta(days=14),
                'status': 'published',
                'is_required': True,
                'weight_percentage': 25
            },
            {
                'title': f'{course.title} - Project Assignment',
                'description': f'Final project for {course.title}. Apply all concepts learned in the course.',
                'instructions': 'Create a comprehensive project that demonstrates your mastery of the course material. Include documentation and source code if applicable.',
                'assignment_type': 'project',
                'max_score': 100,
                'passing_score': 75,
                'due_date': timezone.now() + timedelta(days=30),
                'status': 'published',
                'is_required': True,
                'weight_percentage': 40
            }
        ]
        
        for data in assignment_data:
            Assignment.objects.get_or_create(
                course=course,
                title=data['title'],
                defaults={**data, 'tenant': organization}
            )
    
    print("Sample assignments created!")

def create_sample_enrollments():
    """Create sample enrollments and progress"""
    print("Creating sample enrollments...")
    
    # Get default organization
    organization = Organization.objects.get(subdomain='default')
    courses = Course.objects.all()
    students = User.objects.filter(is_teacher=False)
    
    for student in students:
        # Enroll each student in 2-3 random courses
        enrolled_courses = random.sample(list(courses), min(3, len(courses)))
        
        for course in enrolled_courses:
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                defaults={
                    'status': 'active',
                    'progress_percentage': random.randint(10, 95),
                    'tenant': organization
                }
            )
            
            if created:
                # Create course progress
                CourseProgress.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={
                        'overall_progress_percentage': enrollment.progress_percentage,
                        'modules_completed': [str(i) for i in range(1, random.randint(1, 4))],
                        'assignments_completed': [],
                        'live_classes_attended': [],
                        'tenant': organization
                    }
                )
    
    print("Sample enrollments created!")

if __name__ == '__main__':
    print("Starting sample data creation...")
    
    try:
        create_sample_content()
        create_sample_courses()
        create_sample_assignments()
        create_sample_enrollments()
        
        print("\n✅ All sample data created successfully!")
        print("\nSummary:")
        print(f"- Users: {User.objects.count()}")
        print(f"- Courses: {Course.objects.count()}")
        print(f"- Enrollments: {Enrollment.objects.count()}")
        print(f"- Assignments: {Assignment.objects.count()}")
        print(f"- Testimonials: {Testimonial.objects.count()}")
        print(f"- Team Members: {TeamMember.objects.count()}")
        print(f"- Announcements: {Announcement.objects.count()}")
        print(f"- FAQs: {FAQ.objects.count()}")
        print(f"- Contact Info: {ContactInfo.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        sys.exit(1)