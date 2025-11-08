#!/usr/bin/env python
"""
Complete Database Reset and Setup Script for EduRise Platform
This script will:
1. Delete existing database and migrations
2. Create fresh migrations
3. Apply migrations
4. Create superuser
5. Create sample organizations, users, and data
6. Set up test data for all apps
"""
import os
import sys
import django
import subprocess
from pathlib import Path
from django.utils import timezone
from datetime import timedelta, datetime
import random
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import transaction

# Import all models
from apps.accounts.models import Organization, UserProfile, TeacherApproval
from apps.content.models import Testimonial, TeamMember, Announcement, FAQ, ContactInfo
from apps.courses.models import Course, CourseCategory, Enrollment, CourseModule, CourseReview, LiveClass
from apps.assignments.models import Assignment, Submission, Certificate, CourseProgress
from apps.payments.models import SubscriptionPlan, Subscription, Payment, Invoice
from apps.notifications.models import Notification, EmailDeliveryLog, NotificationTemplate
from apps.classes.models import ClassAttendance, ClassRecording
from apps.files.models import FileCategory, FileUpload
from apps.ai.models import AIConversation, AIContentSummary, AIQuiz, AIUsage

User = get_user_model()

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def delete_migrations():
    """Delete all migration files except __init__.py"""
    print("\n🗑️ Deleting existing migrations...")
    apps_dir = Path("apps")
    
    for app_dir in apps_dir.iterdir():
        if app_dir.is_dir():
            migrations_dir = app_dir / "migrations"
            if migrations_dir.exists():
                for migration_file in migrations_dir.glob("*.py"):
                    if migration_file.name != "__init__.py":
                        migration_file.unlink()
                        print(f"   Deleted: {migration_file}")

def create_superuser():
    """Create superuser account"""
    print("\n👤 Creating superuser...")
    
    try:
        superuser = User.objects.create_superuser(
            email='admin@edurise.com',
            password='admin123',
            first_name='Super',
            last_name='Admin'
        )
        print(f"✅ Superuser created: {superuser.email}")
        return superuser
    except Exception as e:
        print(f"❌ Failed to create superuser: {e}")
        return None

def create_subscription_plans():
    """Create subscription plans"""
    print("\n💳 Creating subscription plans...")
    
    plans_data = [
        {
            'name': 'basic',
            'display_name': 'Basic Plan',
            'description': 'Perfect for small organizations getting started',
            'price_monthly': Decimal('29.99'),
            'price_yearly': Decimal('299.99'),
            'max_users': 50,
            'max_courses': 10,
            'max_storage_gb': 10,
            'ai_quota_monthly': 100,
            'has_analytics': False,
            'has_api_access': False,
            'has_white_labeling': False,
            'has_priority_support': False,
            'has_custom_integrations': False,
            'max_file_size_mb': 100,
            'monthly_download_limit': 1000,
            'recording_access': False,
            'premium_content_access': False,
            'is_popular': False,
            'sort_order': 1
        },
        {
            'name': 'pro',
            'display_name': 'Professional Plan',
            'description': 'Ideal for growing organizations with advanced needs',
            'price_monthly': Decimal('99.99'),
            'price_yearly': Decimal('999.99'),
            'max_users': 200,
            'max_courses': 50,
            'max_storage_gb': 100,
            'ai_quota_monthly': 500,
            'has_analytics': True,
            'has_api_access': True,
            'has_white_labeling': False,
            'has_priority_support': True,
            'has_custom_integrations': False,
            'max_file_size_mb': 500,
            'monthly_download_limit': 5000,
            'recording_access': True,
            'premium_content_access': True,
            'is_popular': True,
            'sort_order': 2
        },
        {
            'name': 'enterprise',
            'display_name': 'Enterprise Plan',
            'description': 'Complete solution for large organizations',
            'price_monthly': Decimal('299.99'),
            'price_yearly': Decimal('2999.99'),
            'max_users': -1,  # Unlimited
            'max_courses': -1,  # Unlimited
            'max_storage_gb': 1000,
            'ai_quota_monthly': 2000,
            'has_analytics': True,
            'has_api_access': True,
            'has_white_labeling': True,
            'has_priority_support': True,
            'has_custom_integrations': True,
            'max_file_size_mb': 2000,
            'monthly_download_limit': None,  # Unlimited
            'recording_access': True,
            'premium_content_access': True,
            'is_popular': False,
            'sort_order': 3
        }
    ]
    
    created_plans = []
    for plan_data in plans_data:
        plan, created = SubscriptionPlan.objects.get_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        if created:
            print(f"   Created plan: {plan.display_name}")
        created_plans.append(plan)
    
    return created_plans

def create_organizations_and_users(subscription_plans):
    """Create sample organizations and users"""
    print("\n🏢 Creating organizations and users...")
    
    # Create main organization
    main_org, created = Organization.objects.get_or_create(
        subdomain='edurise',
        defaults={
            'name': 'EduRise Main Campus',
            'primary_color': '#3B82F6',
            'secondary_color': '#1E40AF'
        }
    )
    if created:
        print(f"   Created organization: {main_org.name}")
    
    # Create subscription for main org
    pro_plan = next((p for p in subscription_plans if p.name == 'pro'), subscription_plans[1])
    subscription, created = Subscription.objects.get_or_create(
        organization=main_org,
        defaults={
            'plan': pro_plan,
            'billing_cycle': 'monthly',
            'status': 'active',
            'amount': pro_plan.price_monthly,
            'currency': 'USD',
            'current_period_start': timezone.now(),
            'current_period_end': timezone.now() + timedelta(days=30),
            'tenant': main_org
        }
    )
    
    # Create additional organizations
    orgs_data = [
        {
            'name': 'Tech University',
            'subdomain': 'techuni',
            'plan': 'enterprise'
        },
        {
            'name': 'Business Academy',
            'subdomain': 'bizacademy',
            'plan': 'basic'
        }
    ]
    
    organizations = [main_org]
    
    for org_data in orgs_data:
        org, created = Organization.objects.get_or_create(
            subdomain=org_data['subdomain'],
            defaults={
                'name': org_data['name'],
                'primary_color': '#3B82F6',
                'secondary_color': '#1E40AF'
            }
        )
        if created:
            print(f"   Created organization: {org.name}")
            
            # Create subscription
            plan = next((p for p in subscription_plans if p.name == org_data['plan']), subscription_plans[0])
            Subscription.objects.get_or_create(
                organization=org,
                defaults={
                    'plan': plan,
                    'billing_cycle': 'monthly',
                    'status': 'active',
                    'amount': plan.price_monthly,
                    'currency': 'USD',
                    'current_period_start': timezone.now(),
                    'current_period_end': timezone.now() + timedelta(days=30),
                    'tenant': org
                }
            )
        
        organizations.append(org)
    
    # Create sample users
    users_data = [
        {
            'email': 'teacher1@edurise.com',
            'first_name': 'John',
            'last_name': 'Teacher',
            'role': 'teacher',
            'is_approved': True
        },
        {
            'email': 'teacher2@edurise.com',
            'first_name': 'Jane',
            'last_name': 'Instructor',
            'role': 'teacher',
            'is_approved': True
        },
        {
            'email': 'student1@edurise.com',
            'first_name': 'Alice',
            'last_name': 'Student',
            'role': 'student',
            'is_approved': False
        },
        {
            'email': 'student2@edurise.com',
            'first_name': 'Bob',
            'last_name': 'Learner',
            'role': 'student',
            'is_approved': False
        },
        {
            'email': 'admin1@edurise.com',
            'first_name': 'Admin',
            'last_name': 'Manager',
            'role': 'admin',
            'is_approved': False
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_staff': user_data['role'] == 'admin'
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            print(f"   Created user: {user.email}")
        
        # Create user profiles for each organization
        for org in organizations:
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                tenant=org,
                defaults={
                    'role': user_data['role'],
                    'is_approved_teacher': user_data['is_approved'] and user_data['role'] == 'teacher',
                    'teacher_approval_status': 'approved' if user_data['is_approved'] and user_data['role'] == 'teacher' else 'not_applied'
                }
            )
            
            if profile_created:
                print(f"     Created profile for {user.email} in {org.name} as {user_data['role']}")
        
        created_users.append(user)
    
    return organizations, created_users

def create_course_categories():
    """Create course categories"""
    print("\n📚 Creating course categories...")
    
    categories_data = [
        {
            'name': 'Programming',
            'description': 'Learn programming languages and software development',
            'color': '#3B82F6'
        },
        {
            'name': 'Data Science',
            'description': 'Master data analysis, machine learning, and AI',
            'color': '#10B981'
        },
        {
            'name': 'Business',
            'description': 'Develop business and entrepreneurship skills',
            'color': '#F59E0B'
        },
        {
            'name': 'Design',
            'description': 'Creative design and user experience',
            'color': '#EF4444'
        },
        {
            'name': 'Marketing',
            'description': 'Digital marketing and growth strategies',
            'color': '#8B5CF6'
        }
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = CourseCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"   Created category: {category.name}")
        categories.append(category)
    
    return categories

def create_courses_and_content(organizations, users, categories):
    """Create sample courses and related content"""
    print("\n🎓 Creating courses and content...")
    
    teachers = [u for u in users if UserProfile.objects.filter(user=u, role='teacher').exists()]
    students = [u for u in users if UserProfile.objects.filter(user=u, role='student').exists()]
    
    courses_data = [
        {
            'title': 'Python Programming Fundamentals',
            'description': 'Learn Python programming from scratch with hands-on projects and real-world applications.',
            'category': 'Programming',
            'price': Decimal('99.99'),
            'duration_weeks': 8,
            'difficulty_level': 'beginner',
            'is_public': True
        },
        {
            'title': 'Data Science with Python',
            'description': 'Master data analysis, visualization, and machine learning using Python.',
            'category': 'Data Science',
            'price': Decimal('149.99'),
            'duration_weeks': 12,
            'difficulty_level': 'intermediate',
            'is_public': True
        },
        {
            'title': 'Digital Marketing Mastery',
            'description': 'Complete guide to digital marketing including SEO, social media, and paid advertising.',
            'category': 'Marketing',
            'price': Decimal('79.99'),
            'duration_weeks': 6,
            'difficulty_level': 'beginner',
            'is_public': True
        },
        {
            'title': 'UI/UX Design Principles',
            'description': 'Learn modern design principles and create stunning user interfaces.',
            'category': 'Design',
            'price': Decimal('129.99'),
            'duration_weeks': 10,
            'difficulty_level': 'intermediate',
            'is_public': True
        }
    ]
    
    created_courses = []
    
    for org in organizations:
        for i, course_data in enumerate(courses_data):
            teacher = teachers[i % len(teachers)]
            category = next((c for c in categories if c.name == course_data['category']), categories[0])
            
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                tenant=org,
                instructor=teacher,
                defaults={
                    **course_data,
                    'category': category,
                    'slug': course_data['title'].lower().replace(' ', '-'),
                    'learning_objectives': [
                        'Understand core concepts',
                        'Apply practical skills',
                        'Build real projects',
                        'Prepare for advanced topics'
                    ],
                    'prerequisites': ['Basic computer skills'],
                    'target_audience': ['Beginners', 'Students', 'Professionals'],
                    'what_you_will_learn': [
                        'Core fundamentals',
                        'Practical applications',
                        'Industry best practices',
                        'Real-world projects'
                    ]
                }
            )
            
            if created:
                print(f"   Created course: {course.title} in {org.name}")
                
                # Create course modules
                modules_data = [
                    {
                        'title': 'Introduction and Setup',
                        'description': 'Getting started with the course',
                        'order': 1,
                        'duration_minutes': 60
                    },
                    {
                        'title': 'Core Concepts',
                        'description': 'Understanding the fundamentals',
                        'order': 2,
                        'duration_minutes': 90
                    },
                    {
                        'title': 'Practical Applications',
                        'description': 'Hands-on practice and examples',
                        'order': 3,
                        'duration_minutes': 120
                    },
                    {
                        'title': 'Advanced Topics',
                        'description': 'Deep dive into advanced concepts',
                        'order': 4,
                        'duration_minutes': 90
                    },
                    {
                        'title': 'Final Project',
                        'description': 'Capstone project and assessment',
                        'order': 5,
                        'duration_minutes': 180
                    }
                ]
                
                for module_data in modules_data:
                    CourseModule.objects.create(
                        course=course,
                        **module_data
                    )
                
                # Create enrollments
                for student in students[:3]:  # Enroll first 3 students
                    enrollment, enroll_created = Enrollment.objects.get_or_create(
                        student=student,
                        course=course,
                        tenant=org,
                        defaults={
                            'status': random.choice(['active', 'completed']),
                            'progress_percentage': random.randint(10, 100),
                            'enrolled_at': timezone.now() - timedelta(days=random.randint(1, 30))
                        }
                    )
                    
                    if enroll_created:
                        # Create course progress
                        CourseProgress.objects.create(
                            student=student,
                            course=course,
                            tenant=org,
                            completion_percentage=enrollment.progress_percentage,
                            time_spent_minutes=random.randint(60, 500),
                            last_accessed=timezone.now() - timedelta(days=random.randint(0, 7))
                        )
                
                # Create course reviews
                for j in range(random.randint(2, 5)):
                    student = random.choice(students)
                    CourseReview.objects.get_or_create(
                        course=course,
                        student=student,
                        tenant=org,
                        defaults={
                            'rating': random.randint(4, 5),
                            'comment': f'Great course! Very informative and well-structured. Review {j+1}',
                            'is_approved': True
                        }
                    )
                
                # Create live classes
                for k in range(2):
                    LiveClass.objects.create(
                        course=course,
                        title=f'{course.title} - Live Session {k+1}',
                        description=f'Interactive live session for {course.title}',
                        scheduled_at=timezone.now() + timedelta(days=random.randint(1, 14)),
                        duration_minutes=90,
                        max_participants=50,
                        status='scheduled',
                        tenant=org
                    )
            
            created_courses.append(course)
    
    return created_courses

def create_payments_and_invoices(organizations, users, courses):
    """Create sample payments and invoices"""
    print("\n💰 Creating payments and invoices...")
    
    students = [u for u in users if UserProfile.objects.filter(user=u, role='student').exists()]
    
    for org in organizations:
        org_courses = [c for c in courses if c.tenant == org]
        
        for i in range(10):  # Create 10 sample payments per org
            student = random.choice(students)
            course = random.choice(org_courses)
            
            payment = Payment.objects.create(
                user=student,
                tenant=org,
                amount=course.price,
                currency='USD',
                payment_method='stripe',
                status=random.choice(['completed', 'pending', 'failed']),
                stripe_payment_intent_id=f'pi_test_{random.randint(100000, 999999)}',
                description=f'Payment for {course.title}',
                metadata={
                    'course_id': str(course.id),
                    'enrollment_type': 'individual'
                }
            )
            
            # Create invoice
            Invoice.objects.create(
                payment=payment,
                user=student,
                tenant=org,
                invoice_number=f'INV-{org.id}-{i+1:04d}',
                amount=payment.amount,
                currency=payment.currency,
                status='paid' if payment.status == 'completed' else 'pending',
                due_date=timezone.now() + timedelta(days=30),
                items=[
                    {
                        'description': f'Course: {course.title}',
                        'quantity': 1,
                        'unit_price': float(course.price),
                        'total': float(course.price)
                    }
                ]
            )

def create_notifications_and_templates(organizations, users):
    """Create sample notifications and templates"""
    print("\n🔔 Creating notifications and templates...")
    
    # Create notification templates
    templates_data = [
        {
            'name': 'welcome_email',
            'subject': 'Welcome to {{organization_name}}!',
            'content': 'Welcome {{user_name}} to our learning platform!',
            'template_type': 'email'
        },
        {
            'name': 'course_enrollment',
            'subject': 'Course Enrollment Confirmation',
            'content': 'You have successfully enrolled in {{course_title}}',
            'template_type': 'email'
        },
        {
            'name': 'assignment_due',
            'subject': 'Assignment Due Reminder',
            'content': 'Your assignment {{assignment_title}} is due soon',
            'template_type': 'push'
        }
    ]
    
    for template_data in templates_data:
        NotificationTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
    
    # Create sample notifications
    for org in organizations:
        org_users = [u for u in users if UserProfile.objects.filter(user=u, tenant=org).exists()]
        
        for user in org_users:
            for i in range(3):  # 3 notifications per user
                Notification.objects.create(
                    user=user,
                    tenant=org,
                    title=f'Sample Notification {i+1}',
                    message=f'This is a sample notification for {user.first_name}',
                    notification_type=random.choice(['info', 'success', 'warning']),
                    is_read=random.choice([True, False])
                )

def create_ai_data(organizations, users, courses):
    """Create sample AI-related data"""
    print("\n🤖 Creating AI data...")
    
    for org in organizations:
        org_users = [u for u in users if UserProfile.objects.filter(user=u, tenant=org).exists()]
        org_courses = [c for c in courses if c.tenant == org]
        
        # Create AI conversations
        for user in org_users[:2]:  # First 2 users
            AIConversation.objects.create(
                user=user,
                tenant=org,
                title='Course Recommendation Chat',
                messages=[
                    {'role': 'user', 'content': 'Can you recommend a good programming course?'},
                    {'role': 'assistant', 'content': 'I recommend starting with Python Programming Fundamentals.'}
                ],
                total_tokens=150,
                status='completed'
            )
        
        # Create AI content summaries
        for course in org_courses[:2]:  # First 2 courses
            AIContentSummary.objects.create(
                course=course,
                tenant=org,
                content_type='course_overview',
                original_content=course.description,
                summary=f'Summary of {course.title}: Key concepts and learning outcomes.',
                tokens_used=100
            )
        
        # Create AI usage records
        for user in org_users:
            AIUsage.objects.create(
                user=user,
                tenant=org,
                feature_type='chat',
                tokens_used=random.randint(50, 200),
                cost=Decimal(str(random.uniform(0.01, 0.10))),
                metadata={'session_id': f'session_{random.randint(1000, 9999)}'}
            )

def create_file_categories_and_uploads(organizations, users):
    """Create file categories and sample uploads"""
    print("\n📁 Creating file categories and uploads...")
    
    categories_data = [
        {'name': 'Course Materials', 'description': 'Course-related files and resources'},
        {'name': 'Assignments', 'description': 'Assignment files and submissions'},
        {'name': 'Media', 'description': 'Images, videos, and audio files'},
        {'name': 'Documents', 'description': 'PDF documents and presentations'}
    ]
    
    file_categories = []
    for cat_data in categories_data:
        category, created = FileCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"   Created file category: {category.name}")
        file_categories.append(category)
    
    # Create sample file uploads
    for org in organizations:
        org_users = [u for u in users if UserProfile.objects.filter(user=u, tenant=org).exists()]
        
        for user in org_users[:2]:  # First 2 users
            for i, category in enumerate(file_categories):
                FileUpload.objects.create(
                    uploaded_by=user,
                    tenant=org,
                    category=category,
                    original_filename=f'sample_file_{i+1}.pdf',
                    file_size=random.randint(1024, 10485760),  # 1KB to 10MB
                    mime_type='application/pdf',
                    file_hash=f'hash_{random.randint(100000, 999999)}',
                    is_public=random.choice([True, False]),
                    description=f'Sample {category.name.lower()} file'
                )

def create_content_data():
    """Create content management data"""
    print("\n📄 Creating content data...")
    
    # Create contact info
    ContactInfo.objects.get_or_create(
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
            'youtube_url': 'https://youtube.com/edurise'
        }
    )
    
    # Create team members
    team_data = [
        {
            'name': 'Dr. Sarah Johnson',
            'position': 'CEO & Founder',
            'bio': 'Educational technology expert with 15+ years of experience in online learning.',
            'image_url': 'https://via.placeholder.com/300x300',
            'linkedin_url': 'https://linkedin.com/in/sarahjohnson'
        },
        {
            'name': 'Michael Chen',
            'position': 'CTO',
            'bio': 'Full-stack developer and system architect passionate about scalable education platforms.',
            'image_url': 'https://via.placeholder.com/300x300',
            'linkedin_url': 'https://linkedin.com/in/michaelchen'
        },
        {
            'name': 'Emily Rodriguez',
            'position': 'Head of Curriculum',
            'bio': 'Curriculum designer with expertise in creating engaging and effective learning experiences.',
            'image_url': 'https://via.placeholder.com/300x300',
            'linkedin_url': 'https://linkedin.com/in/emilyrodriguez'
        }
    ]
    
    for member_data in team_data:
        TeamMember.objects.get_or_create(
            name=member_data['name'],
            defaults=member_data
        )
    
    # Create testimonials
    testimonials_data = [
        {
            'name': 'John Smith',
            'position': 'Software Developer',
            'company': 'Tech Corp',
            'content': 'EduRise transformed my career. The courses are well-structured and the instructors are top-notch.',
            'rating': 5,
            'image_url': 'https://via.placeholder.com/150x150'
        },
        {
            'name': 'Maria Garcia',
            'position': 'Data Scientist',
            'company': 'Analytics Inc',
            'content': 'The data science program gave me the skills I needed to transition into my dream job.',
            'rating': 5,
            'image_url': 'https://via.placeholder.com/150x150'
        },
        {
            'name': 'David Kim',
            'position': 'Marketing Manager',
            'company': 'Growth Agency',
            'content': 'Excellent platform with practical courses that directly apply to real-world scenarios.',
            'rating': 4,
            'image_url': 'https://via.placeholder.com/150x150'
        }
    ]
    
    for testimonial_data in testimonials_data:
        Testimonial.objects.get_or_create(
            name=testimonial_data['name'],
            defaults=testimonial_data
        )
    
    # Create FAQs
    faqs_data = [
        {
            'question': 'How do I enroll in a course?',
            'answer': 'Simply browse our course catalog, select a course, and click the "Enroll Now" button. You can pay securely online.',
            'category': 'enrollment',
            'order': 1
        },
        {
            'question': 'Can I access courses on mobile devices?',
            'answer': 'Yes! Our platform is fully responsive and works great on all devices including smartphones and tablets.',
            'category': 'technical',
            'order': 2
        },
        {
            'question': 'Do you offer certificates upon completion?',
            'answer': 'Yes, you will receive a certificate of completion for each course you successfully finish.',
            'category': 'certificates',
            'order': 3
        },
        {
            'question': 'What is your refund policy?',
            'answer': 'We offer a 30-day money-back guarantee if you are not satisfied with your course.',
            'category': 'billing',
            'order': 4
        }
    ]
    
    for faq_data in faqs_data:
        FAQ.objects.get_or_create(
            question=faq_data['question'],
            defaults=faq_data
        )
    
    # Create announcements
    announcements_data = [
        {
            'title': 'New Course: Advanced Machine Learning',
            'content': 'We are excited to announce our new Advanced Machine Learning course, starting next month!',
            'announcement_type': 'course_launch',
            'is_featured': True,
            'published_at': timezone.now() - timedelta(days=5)
        },
        {
            'title': 'Platform Maintenance Scheduled',
            'content': 'We will be performing scheduled maintenance on Sunday from 2 AM to 4 AM EST.',
            'announcement_type': 'maintenance',
            'is_featured': False,
            'published_at': timezone.now() - timedelta(days=2)
        },
        {
            'title': 'Student Success Story: Career Change at 40',
            'content': 'Read how one of our students successfully transitioned to a tech career after completing our programming bootcamp.',
            'announcement_type': 'success_story',
            'is_featured': True,
            'published_at': timezone.now() - timedelta(days=1)
        }
    ]
    
    for announcement_data in announcements_data:
        Announcement.objects.get_or_create(
            title=announcement_data['title'],
            defaults=announcement_data
        )

def main():
    """Main function to run the complete setup"""
    print("🚀 Starting complete database reset and setup...")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            # Step 1: Delete migrations
            delete_migrations()
            
            # Step 2: Create fresh migrations
            if not run_command("python manage.py makemigrations", "Creating fresh migrations"):
                return False
            
            # Step 3: Apply migrations
            if not run_command("python manage.py migrate", "Applying migrations"):
                return False
            
            # Step 4: Create superuser
            superuser = create_superuser()
            if not superuser:
                return False
            
            # Step 5: Create subscription plans
            subscription_plans = create_subscription_plans()
            
            # Step 6: Create organizations and users
            organizations, users = create_organizations_and_users(subscription_plans)
            
            # Step 7: Create course categories
            categories = create_course_categories()
            
            # Step 8: Create courses and content
            courses = create_courses_and_content(organizations, users, categories)
            
            # Step 9: Create payments and invoices
            create_payments_and_invoices(organizations, users, courses)
            
            # Step 10: Create notifications
            create_notifications_and_templates(organizations, users)
            
            # Step 11: Create AI data
            create_ai_data(organizations, users, courses)
            
            # Step 12: Create file categories and uploads
            create_file_categories_and_uploads(organizations, users)
            
            # Step 13: Create content data
            create_content_data()
            
            print("\n" + "=" * 60)
            print("🎉 Database setup completed successfully!")
            print("\n📋 Summary:")
            print(f"   • Organizations: {len(organizations)}")
            print(f"   • Users: {len(users) + 1} (including superuser)")
            print(f"   • Courses: {len(courses)}")
            print(f"   • Categories: {len(categories)}")
            print(f"   • Subscription Plans: {len(subscription_plans)}")
            
            print("\n🔑 Login Credentials:")
            print("   Superuser:")
            print("     Email: admin@edurise.com")
            print("     Password: admin123")
            print("\n   Sample Users:")
            print("     Teacher: teacher1@edurise.com / password123")
            print("     Student: student1@edurise.com / password123")
            print("     Admin: admin1@edurise.com / password123")
            
            print("\n🌐 Organizations:")
            for org in organizations:
                print(f"     • {org.name} (subdomain: {org.subdomain})")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)