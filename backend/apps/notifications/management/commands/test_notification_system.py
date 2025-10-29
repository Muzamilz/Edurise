"""
Management command to test the notification system
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Organization
from apps.notifications.services import NotificationService
from apps.notifications.i18n_service import NotificationI18nService

User = get_user_model()


class Command(BaseCommand):
    help = 'Test the notification system functionality'
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔔 Testing Django Notification System')
        )
        self.stdout.write('=' * 50)
        
        # Test 1: Multi-language support
        self.stdout.write('\n1️⃣ Multi-language Support')
        self.stdout.write('-' * 30)
        
        languages = NotificationI18nService.get_all_supported_languages()
        self.stdout.write(f'Supported languages: {list(languages.keys())}')
        
        # Test localized messages
        context = {'course_title': 'Python Programming'}
        
        for lang_code, lang_name in languages.items():
            message = NotificationI18nService.get_localized_message(
                'course_enrollment', lang_code, context
            )
            self.stdout.write(f'{lang_name} ({lang_code}): {message["title"]}')
            self.stdout.write(f'  RTL: {message["is_rtl"]}')
        
        # Test 2: Notification creation
        self.stdout.write('\n2️⃣ Notification Creation')
        self.stdout.write('-' * 25)
        
        user = User.objects.first()
        organization = Organization.objects.first()
        
        if user and organization:
            notification = NotificationService.create_notification(
                user=user,
                title="Test Notification",
                message="Test message",
                notification_type='course_enrollment',
                tenant=organization,
                context={'course_title': 'Advanced Python'},
                send_email=False  # Don't send email in test
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created notification: {notification.title}')
            )
            self.stdout.write(f'User: {notification.user.email}')
            self.stdout.write(f'Type: {notification.notification_type}')
            self.stdout.write(f'Tenant: {notification.tenant.name}')
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ No test data found')
            )
        
        # Test 3: User preferences
        self.stdout.write('\n3️⃣ User Preferences')
        self.stdout.write('-' * 20)
        
        if user:
            preferences = NotificationService.get_user_preferences(user)
            self.stdout.write('Current preferences:')
            for key, value in preferences.items():
                status = '✅' if value else '❌'
                self.stdout.write(f'  {key}: {status}')
        
        # Test 4: Statistics
        self.stdout.write('\n4️⃣ Statistics')
        self.stdout.write('-' * 15)
        
        from apps.notifications.models import Notification
        from django.db.models import Count
        
        if user:
            total = Notification.objects.filter(user=user).count()
            unread = Notification.objects.filter(user=user, is_read=False).count()
            
            self.stdout.write(f'Total notifications: {total}')
            self.stdout.write(f'Unread notifications: {unread}')
            
            # By type
            by_type = dict(
                Notification.objects.filter(user=user)
                .values('notification_type')
                .annotate(count=Count('id'))
                .values_list('notification_type', 'count')
            )
            
            if by_type:
                self.stdout.write('By type:')
                for notif_type, count in by_type.items():
                    self.stdout.write(f'  {notif_type}: {count}')
        
        self.stdout.write('\n🎉 Test completed successfully!')
        self.stdout.write('=' * 50)