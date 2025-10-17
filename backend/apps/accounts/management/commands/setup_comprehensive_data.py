import random
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.models import Organization, UserProfile, TeacherApproval
from apps.courses.models import Course, CourseModule, LiveClass, Enrollment
from apps.payments.models import Subscription

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up comprehensive test data for the Edurise LMS platform'

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true', help='Clean existing data')
        parser.add_argument('--organizations', type=int, default=5, help='Number of organizations')

    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write('Cleaning existing data...')
            self.clean_data()

        self.stdout.write('Creating comprehensive test data...')
        
        # Create organizations
        organizations = self.create_organizations(options['organizations'])
        
        # Create users for each organization
        all_users = []
        for org in organizations:
            users = self.create_users_for_organization(org)
            all_users.extend(users)
        
        # Create courses
        self.create_courses(all_users)
        
        self.stdout.write(self.style.SUCCESS('✅ Comprehensive test data created successfully!'))
        self.print_summary()

    def clean_data(self):
        """Clean all existing data"""
        models = [Enrollment, CourseModule, LiveClass, Course, TeacherApproval, 
                 UserProfile, User, Subscription, Organization]
        
        for model in models:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f'Deleted {count} {model.__name__} records')

    def create_organizations(self, count):
        """Create organizations"""
        organizations = []
        
        org_data = [
            {'name': 'Edurise Platform', 'subdomain': 'main', 'subscription_plan': 'enterprise'},
            {'name': 'Tech University', 'subdomain': 'techuni', 'subscription_plan': 'pro'},
            {'name': 'Business Academy', 'subdomain': 'bizacademy', 'subscription_plan': 'pro'},
            {'name': 'Creative Institute', 'subdomain': 'creative', 'subscription_plan': 'basic'},
            {'name': 'Medical College', 'subdomain': 'medcollege', 'subscription_plan': 'enterprise'}
        ]
        
        for i in range(count):
            if i < len(org_data):
                data = org_data[i]
            else:
                data = {
                    'name': f'Organization {i+1}',
                    'subdomain': f'org{i+1}',
                    'subscription_plan': random.choice(['basic', 'pro', 'enterprise'])
                }
            
            org = Organization.objects.create(**data)
            organizations.append(org)
            
            # Create subscription
            self.create_subscription(org)
            
            self.stdout.write(f'Created organization: {org.name}')
        
        return organizations

    def create_subscription(self, org):
        """Create subscription for organization"""
        plan_pricing = {
            'basic': 29.99,
            'pro': 99.99,
            'enterprise': 299.99
        }
        
        start_date = timezone.now() - timedelta(days=random.randint(1, 365))
        end_date = start_date + timedelta(days=30)
        
        Subscription.objects.create(
            organization=org,
            plan=org.subscription_plan,
            billing_cycle='monthly',
            status='active',
            amount=Decimal(str(plan_pricing[org.subscription_plan])),
            current_period_start=start_date,
            current_period_end=end_date,
            tenant=org
        )

    def create_users_for_organization(self, org):
        """Create users for an organization"""
        users = []
        
        # Create super admin (only for main platform)
        if org.subdomain == 'main':
            super_admin = User.objects.create_user(
                email='admin@edurise.com',
                password='admin123456',
                first_name='Super',
                last_name='Admin',
                is_staff=True,
                is_superuser=True
            )
            UserProfile.objects.create(user=super_admin, tenant=org, role='admin')
            users.append(super_admin)
        
        # Create organization admin
        org_admin = User.objects.create_user(
            email=f'admin@{org.subdomain}.com',
            password='admin123456',
            first_name='Organization',
            last_name='Admin',
            is_staff=True,
            is_superuser=False
        )
        UserProfile.objects.create(user=org_admin, tenant=org, role='admin')
        users.append(org_admin)
        
        # Create teachers
        for i in range(5):
            is_approved = random.choice([True, True, False])  # 66% approved
            
            teacher = User.objects.create_user(
                email=f'teacher{i+1}@{org.subdomain}.com',
                password='teacher123456',
                first_name=f'Teacher{i+1}',
                last_name='User',
                is_teacher=True,
                is_approved_teacher=is_approved
            )
            
            UserProfile.objects.create(user=teacher, tenant=org, role='teacher')
            
            # Create teacher approval if not approved
            if not is_approved:
                TeacherApproval.objects.create(
                    user=teacher,
                    status='pending',
                    teaching_experience='5 years of teaching experience',
                    qualifications='Masters degree',
                    subject_expertise='Web Development, Programming'
                )
            
            users.append(teacher)
        
        # Create students
        for i in range(15):
            student = User.objects.create_user(
                email=f'student{i+1}@{org.subdomain}.com',
                password='student123456',
                first_name=f'Student{i+1}',
                last_name='User'
            )
            
            UserProfile.objects.create(user=student, tenant=org, role='student')
            users.append(student)
        
        self.stdout.write(f'Created {len(users)} users for {org.name}')
        return users

    def create_courses(self, all_users):
        """Create courses with content"""
        teachers = [user for user in all_users if user.is_approved_teacher]
        students = [user for user in all_users if not user.is_teacher and not user.is_staff]
        
        course_templates = [
            {
                'title': 'JavaScript Fundamentals',
                'description': 'Learn JavaScript from basics to advanced concepts.',
                'category': 'technology',
                'price': Decimal('99.99')
            },
            {
                'title': 'React Development',
                'description': 'Build modern web applications with React.',
                'category': 'technology',
                'price': Decimal('149.99')
            },
            {
                'title': 'Business Management',
                'description': 'Essential business management skills.',
                'category': 'business',
                'price': None
            }
        ]
        
        for teacher in teachers:
            teacher_profile = teacher.profiles.first()
            if not teacher_profile:
                continue
            
            for i, template in enumerate(course_templates):
                if i >= 2:  # Limit to 2 courses per teacher
                    break
                
                is_public = teacher_profile.tenant.subdomain == 'main'
                
                course = Course.objects.create(
                    title=f"{template['title']} - {teacher.first_name}'s Edition",
                    description=template['description'],
                    instructor=teacher,
                    tenant=teacher_profile.tenant,
                    category=template['category'],
                    price=template['price'] if is_public else None,
                    is_public=is_public,
                    duration_weeks=8
                )
                
                # Create course modules
                for j in range(4):
                    CourseModule.objects.create(
                        course=course,
                        title=f'Module {j+1}',
                        description=f'Module {j+1} content',
                        order=j+1,
                        is_published=True
                    )
                
                # Create live classes
                for j in range(3):
                    LiveClass.objects.create(
                        course=course,
                        title=f'Live Session {j+1}',
                        scheduled_at=timezone.now() + timedelta(days=j*7),
                        duration_minutes=90,
                        status='scheduled'
                    )
                
                # Create enrollments
                enrolled_students = random.sample(students, min(10, len(students)))
                for student in enrolled_students:
                    student_profile = student.profiles.first()
                    if student_profile and (is_public or student_profile.tenant == course.tenant):
                        Enrollment.objects.create(
                            student=student,
                            course=course,
                            tenant=course.tenant,
                            status='active',
                            progress_percentage=random.randint(10, 90)
                        )
        
        self.stdout.write(f'Created {Course.objects.count()} courses')

    def print_summary(self):
        """Print summary of created data"""
        self.stdout.write('\n📊 DATA SUMMARY')
        self.stdout.write('=' * 30)
        self.stdout.write(f'Organizations: {Organization.objects.count()}')
        self.stdout.write(f'Users: {User.objects.count()}')
        self.stdout.write(f'Courses: {Course.objects.count()}')
        self.stdout.write(f'Enrollments: {Enrollment.objects.count()}')
        
        self.stdout.write('\n🔑 TEST ACCOUNTS:')
        self.stdout.write('Super Admin: admin@edurise.com / admin123456')
        
        orgs = Organization.objects.all()
        for org in orgs:
            self.stdout.write(f'Org Admin ({org.name}): admin@{org.subdomain}.com / admin123456')
            self.stdout.write(f'Teachers: teacher1-5@{org.subdomain}.com / teacher123456')
            self.stdout.write(f'Students: student1-15@{org.subdomain}.com / student123456')