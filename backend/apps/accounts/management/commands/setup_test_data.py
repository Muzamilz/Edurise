from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Organization, UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up test data for authentication testing'

    def handle(self, *args, **options):
        self.stdout.write('Setting up test data...')
        
        # Create test organization
        org, created = Organization.objects.get_or_create(
            subdomain='test-uni',
            defaults={
                'name': 'Test University',
                'primary_color': '#3B82F6',
                'secondary_color': '#1E40AF',
                'subscription_plan': 'pro'
            }
        )
        
        if created:
            self.stdout.write(f'✓ Created organization: {org.name}')
        else:
            self.stdout.write(f'✓ Organization already exists: {org.name}')
        
        # Create test users
        test_users = [
            {
                'email': 'student@test.com',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'Student',
                'is_teacher': False
            },
            {
                'email': 'teacher@test.com',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'Teacher',
                'is_teacher': True
            }
        ]
        
        for user_data in test_users:
            try:
                user = User.objects.get(email=user_data['email'])
                self.stdout.write(f'✓ User already exists: {user.email}')
            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_teacher=user_data['is_teacher']
                )
                self.stdout.write(f'✓ Created user: {user.email}')
            
            # Create user profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                tenant=org
            )
            
            if created:
                self.stdout.write(f'✓ Created profile for: {user.email}')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Test data setup complete!')
        self.stdout.write('='*50)
        self.stdout.write('\nTest credentials:')
        self.stdout.write('Student: student@test.com / testpass123')
        self.stdout.write('Teacher: teacher@test.com / testpass123')
        self.stdout.write('Admin: admin@edurise.com / admin123')
        self.stdout.write('\nTest organization: test-uni.localhost:3000')
        self.stdout.write('='*50)