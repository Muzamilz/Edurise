from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Organization, UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with tenant association'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Superuser email')
        parser.add_argument('--password', required=True, help='Superuser password')
        parser.add_argument('--first-name', required=True, help='First name')
        parser.add_argument('--last-name', required=True, help='Last name')
        parser.add_argument('--tenant-name', help='Tenant name (optional)')
        parser.add_argument('--tenant-subdomain', help='Tenant subdomain (optional)')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        tenant_name = options.get('tenant_name')
        tenant_subdomain = options.get('tenant_subdomain')

        # Create superuser
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'User with email {email} already exists')
            )
            return

        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        self.stdout.write(
            self.style.SUCCESS(f'Superuser {email} created successfully')
        )

        # Create tenant if specified
        if tenant_name and tenant_subdomain:
            tenant, created = Organization.objects.get_or_create(
                subdomain=tenant_subdomain,
                defaults={
                    'name': tenant_name,
                    'subscription_plan': 'enterprise'
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Tenant {tenant_name} created successfully')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Tenant {tenant_name} already exists')
                )

            # Create user profile
            UserProfile.objects.get_or_create(
                user=user,
                tenant=tenant
            )

            self.stdout.write(
                self.style.SUCCESS(f'User associated with tenant {tenant_name}')
            )