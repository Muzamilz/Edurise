"""
Demonstration script for the Django notification system
Shows all implemented features including multi-language support
"""

from django.contrib.auth import get_user_model
from apps.accounts.models import Organization, UserProfile
from .services import NotificationService
from .i18n_service import NotificationI18nService

User = get_user_model()


def demo_notification_system():
    """Demonstrate the notification system features"""
    
    print("🔔 Django Notification System Demo")
    print("=" * 50)
    
    # Get test data
    user = User.objects.first()
    organization = Organization.objects.first()
    
    if not user or not organization:
        print("❌ No test data found. Please run the sample data creation first.")
        return
    
    print(f"👤 Using user: {user.email}")
    print(f"🏢 Using organization: {organization.name}")
    print()
    
    # Demo 1: Multi-language support
    print("1️⃣ Multi-language Support Demo")
    print("-" * 30)
    
    languages = NotificationI18nService.get_all_supported_languages()
    print(f"Supported languages: {languages}")
    
    # Test localized messages
    context = {'course_title': 'Advanced Python Programming'}
    
    for lang_code, lang_name in languages.items():
        message = NotificationI18nService.get_localized_message(
            'course_enrollment', lang_code, context
        )
        print(f"{lang_name} ({lang_code}): {message['title']}")
        print(f"  RTL: {message['is_rtl']}")
    
    print()
    
    # Demo 2: Notification creation with i18n
    print("2️⃣ Notification Creation with I18n")
    print("-" * 35)
    
    notification = NotificationService.create_notification(
        user=user,
        title="Demo Notification",
        message="Demo message",
        notification_type='course_enrollment',
        tenant=organization,
        context={'course_title': 'Advanced Python Programming'}
    )
    
    print(f"✅ Created notification: {notification.title}")
    print(f"📧 Email sent: {notification.sent_email}")
    print(f"📱 Push sent: {notification.sent_push}")
    print()
    
    # Demo 3: User preferences
    print("3️⃣ User Notification Preferences")
    print("-" * 32)
    
    preferences = NotificationService.get_user_preferences(user)
    print("Current preferences:")
    for key, value in preferences.items():
        print(f"  {key}: {'✅' if value else '❌'}")
    
    print()
    
    # Demo 4: Different notification types
    print("4️⃣ Different Notification Types")
    print("-" * 31)
    
    notification_types = [
        ('class_reminder', {'class_title': 'Python Basics', 'minutes': 30}),
        ('payment_success', {'amount': '$99.99', 'item_name': 'Python Course'}),
        ('system', {'message': 'System maintenance scheduled'})
    ]
    
    for notif_type, context in notification_types:
        notification = NotificationService.create_notification(
            user=user,
            title="Demo",
            message="Demo",
            notification_type=notif_type,
            tenant=organization,
            context=context,
            send_email=False  # Don't spam emails in demo
        )
        print(f"✅ {notif_type}: {notification.title}")
    
    print()
    
    # Demo 5: Notification statistics
    print("5️⃣ Notification Statistics")
    print("-" * 25)
    
    from .models import Notification
    
    total_notifications = Notification.objects.filter(user=user).count()
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
    
    print(f"Total notifications: {total_notifications}")
    print(f"Unread notifications: {unread_notifications}")
    
    # Get notifications by type
    from django.db.models import Count
    notifications_by_type = dict(
        Notification.objects.filter(user=user)
        .values('notification_type')
        .annotate(count=Count('id'))
        .values_list('notification_type', 'count')
    )
    
    print("Notifications by type:")
    for notif_type, count in notifications_by_type.items():
        print(f"  {notif_type}: {count}")
    
    print()
    print("🎉 Demo completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    demo_notification_system()