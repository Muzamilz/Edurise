import random
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.models import Organization, UserProfile, TeacherApproval
from apps.courses.models import Course, CourseModule, LiveClass, Enrollment, CourseCategory
from apps.payments.models import Subscription, SubscriptionPlan

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
        
        # Create payments
        self.create_payments()
        
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
            {'name': 'Edurise Platform', 'subdomain': 'main', 'plan_name': 'enterprise'},
            {'name': 'Tech University', 'subdomain': 'techuni', 'plan_name': 'pro'},
            {'name': 'Business Academy', 'subdomain': 'bizacademy', 'plan_name': 'pro'},
            {'name': 'Creative Institute', 'subdomain': 'creative', 'plan_name': 'basic'},
            {'name': 'Medical College', 'subdomain': 'medcollege', 'plan_name': 'enterprise'}
        ]
        
        for i in range(count):
            if i < len(org_data):
                data = org_data[i]
                plan_name = data.pop('plan_name')  # Remove plan_name from org data
            else:
                data = {
                    'name': f'Organization {i+1}',
                    'subdomain': f'org{i+1}',
                }
                plan_name = random.choice(['basic', 'pro', 'enterprise'])
            
            org, created = Organization.objects.get_or_create(
                subdomain=data['subdomain'],
                defaults=data
            )
            organizations.append(org)
            
            if created:
                # Create subscription
                self.create_subscription(org, plan_name)
                self.stdout.write(f'Created organization: {org.name}')
            else:
                self.stdout.write(f'Organization already exists: {org.name}')
        
        return organizations

    def create_subscription(self, org, plan_name):
        """Create subscription for organization"""
        from apps.payments.models import SubscriptionPlan
        
        # Get the subscription plan
        try:
            plan = SubscriptionPlan.objects.get(name=plan_name)
        except SubscriptionPlan.DoesNotExist:
            plan = SubscriptionPlan.objects.get(name='basic')  # Fallback to basic
        
        start_date = timezone.now() - timedelta(days=random.randint(1, 365))
        end_date = start_date + timedelta(days=30)
        
        Subscription.objects.create(
            organization=org,
            plan=plan,
            billing_cycle='monthly',
            status='active',
            amount=plan.price_monthly,
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
                last_name='User'
            )
            
            UserProfile.objects.create(
                user=teacher, 
                tenant=org, 
                role='teacher',
                is_approved_teacher=is_approved,
                teacher_approval_status='approved' if is_approved else 'pending'
            )
            
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
        # Get approved teachers by checking their profiles
        teachers = []
        students = []
        
        for user in all_users:
            for profile in user.profiles.all():
                if profile.role == 'teacher' and profile.is_approved_teacher:
                    teachers.append(user)
                    break
                elif profile.role == 'student':
                    students.append(user)
                    break
        
        # Get some categories
        tech_category = CourseCategory.objects.filter(name='Technology').first()
        business_category = CourseCategory.objects.filter(name='Business').first()
        design_category = CourseCategory.objects.filter(name='Design').first()
        
        # Use first available category as fallback
        fallback_category = CourseCategory.objects.first()
        
        course_templates = [
            {
                'title': 'JavaScript Fundamentals',
                'description': 'Learn JavaScript from basics to advanced concepts.',
                'category': tech_category or fallback_category,
                'price': Decimal('99.99'),
                'tags': ['javascript', 'programming', 'web-development']
            },
            {
                'title': 'React Development',
                'description': 'Build modern web applications with React.',
                'category': tech_category or fallback_category,
                'price': Decimal('149.99'),
                'tags': ['react', 'javascript', 'frontend']
            },
            {
                'title': 'Business Management',
                'description': 'Essential business management skills.',
                'category': business_category or fallback_category,
                'price': None,
                'tags': ['business', 'management', 'leadership']
            },
            {
                'title': 'UI/UX Design Basics',
                'description': 'Learn user interface and user experience design.',
                'category': design_category or fallback_category,
                'price': Decimal('79.99'),
                'tags': ['design', 'ui', 'ux', 'figma']
            }
        ]
        
        if not fallback_category:
            self.stdout.write(self.style.WARNING('No categories found. Skipping course creation.'))
            return
        
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
                    tags=template['tags'],
                    price=template['price'] if is_public else None,
                    is_public=is_public,
                    duration_weeks=random.randint(4, 12),
                    difficulty_level=random.choice(['beginner', 'intermediate', 'advanced']),
                    max_students=random.randint(20, 100)
                )
                
                # Create course modules
                for j in range(4):
                    CourseModule.objects.create(
                        course=course,
                        title=f'Module {j+1}: {template["title"]} Part {j+1}',
                        description=f'Module {j+1} content for {template["title"]}',
                        order=j+1,
                        is_published=True
                    )
                
                # Create live classes
                for j in range(3):
                    LiveClass.objects.create(
                        course=course,
                        title=f'Live Session {j+1}: {template["title"]}',
                        scheduled_at=timezone.now() + timedelta(days=j*7),
                        duration_minutes=random.choice([60, 90, 120]),
                        status='scheduled'
                    )
                
                # Create enrollments
                if students:
                    enrolled_students = random.sample(students, min(random.randint(5, 15), len(students)))
                    for student in enrolled_students:
                        student_profile = student.profiles.first()
                        if student_profile and (is_public or student_profile.tenant == course.tenant):
                            Enrollment.objects.create(
                                student=student,
                                course=course,
                                tenant=course.tenant,
                                status=random.choice(['active', 'completed']),
                                progress_percentage=random.randint(10, 100)
                            )
        
        self.stdout.write(f'Created {Course.objects.count()} courses')

    def create_payments(self):
        """Create sample payment data"""
        from apps.payments.models import Payment, SubscriptionPlan
        from decimal import Decimal
        import random
        from datetime import datetime, timedelta
        
        self.stdout.write('Creating payment data...')
        
        # Get all enrollments to create payments for
        enrollments = Enrollment.objects.all()
        
        # Create payments for about 60% of enrollments
        payment_enrollments = random.sample(list(enrollments), int(len(enrollments) * 0.6))
        
        for enrollment in payment_enrollments:
            # Create payment for course enrollment
            payment_amount = enrollment.course.price or Decimal('99.99')
            
            Payment.objects.create(
                user=enrollment.student,
                tenant=enrollment.tenant,
                amount=payment_amount,
                currency='USD',
                payment_method='stripe',
                status='completed',
                stripe_payment_intent_id=f'pi_test_{random.randint(100000, 999999)}',
                description=f'Payment for course: {enrollment.course.title}',
                created_at=enrollment.enrolled_at + timedelta(minutes=random.randint(1, 30))
            )
        
        # Create some subscription payments
        organizations = Organization.objects.all()
        for org in organizations:
            try:
                subscription = org.subscription
                if subscription and subscription.plan:
                    # Create monthly payments for the last 6 months
                    for i in range(6):
                        payment_date = timezone.now() - timedelta(days=30 * i)
                        
                        Payment.objects.create(
                            user=None,  # Organization payment
                            tenant=org,
                            amount=subscription.plan.monthly_price,
                            currency='USD',
                            payment_method='stripe',
                            status='completed',
                            stripe_payment_intent_id=f'pi_sub_{random.randint(100000, 999999)}',
                            description=f'Monthly subscription - {subscription.plan.display_name}',
                            created_at=payment_date
                        )
            except:
                continue
        
        self.stdout.write(f'Created {Payment.objects.count()} payments')

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