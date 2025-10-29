"""
Management command to set up default notification preferences for existing users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up default notification preferences for existing users'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update preferences even if they already exist',
        )
    
    def handle(self, *args, **options):
        force_update = options['force']
        
        # Default notification preferences
        default_preferences = {
            'email_notifications': True,
            'push_notifications': True,
            'course_enrollment_notifications': True,
            'class_reminder_notifications': True,
            'assignment_due_notifications': True,
            'payment_notifications': True,
            'system_notifications': True,
        }
        
        # Get all user profiles
        profiles = UserProfile.objects.all()
        updated_count = 0
        
        for profile in profiles:
            # Check if preferences need to be set
            if not profile.notification_preferences or force_update:
                profile.notification_preferences = default_preferences
                profile.save()
                updated_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated notification preferences for {profile.user.email}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated notification preferences for {updated_count} users'
            )
        )
        
        # Also check for users without profiles
        users_without_profiles = User.objects.filter(profiles__isnull=True)
        if users_without_profiles.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Found {users_without_profiles.count()} users without profiles. '
                    'These users will get default preferences when they first access the system.'
                )
            )