"""
Comprehensive tests for the notification system
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from unittest.mock import patch, MagicMock
import json

from apps.accounts.models import Organization, UserProfile
from .models import Notification, EmailDeliveryLog, NotificationTemplate, ChatMessage, WebSocketConnection
from .services import NotificationService, EmailService, WebSocketNotificationService
from .i18n_service import NotificationI18nService

User = get_user_model()


class NotificationModelTests(TestCase):
    """Test notification models"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            subdomain="test"
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            tenant=self.organization,
            language='en'
        )
    
    def test_notification_creation(self):
        """Test notification model creation"""
        notification = Notification.objects.create(
            user=self.user,
            tenant=self.organization,
            title="Test Notification",
            message="This is a test notification",
            notification_type="system"
        )
        
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.tenant, self.organization)
        self.assertEqual(notification.title, "Test Notification")
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.created_at)
    
    def test_notification_mark_as_read(self):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            user=self.user,
            tenant=self.organization,
            title="Test Notification",
            message="This is a test notification",
            notification_type="system"
        )
        
        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)
        
        notification.mark_as_read()
        
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)


class NotificationI18nServiceTests(TestCase):
    """Test internationalization service"""
    
    def test_get_localized_message_english(self):
        """Test getting localized message in English"""
        context = {'course_title': 'Python Programming'}
        message = NotificationI18nService.get_localized_message(
            'course_enrollment', 'en', context
        )
        
        self.assertEqual(message['language'], 'en')
        self.assertIn('Python Programming', message['title'])
        self.assertIn('Python Programming', message['message'])
        self.assertFalse(message['is_rtl'])
    
    def test_get_localized_message_arabic(self):
        """Test getting localized message in Arabic"""
        context = {'course_title': 'برمجة بايثون'}
        message = NotificationI18nService.get_localized_message(
            'course_enrollment', 'ar', context
        )
        
        self.assertEqual(message['language'], 'ar')
        self.assertIn('برمجة بايثون', message['title'])
        self.assertIn('برمجة بايثون', message['message'])
        self.assertTrue(message['is_rtl'])
    
    def test_supported_languages(self):
        """Test getting supported languages"""
        languages = NotificationI18nService.get_all_supported_languages()
        
        self.assertIn('en', languages)
        self.assertIn('ar', languages)
        self.assertIn('so', languages)
        self.assertEqual(languages['en'], 'English')
        self.assertEqual(languages['ar'], 'Arabic')
        self.assertEqual(languages['so'], 'Somali')


class NotificationServiceTests(TestCase):
    """Test notification service"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            subdomain="test"
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            tenant=self.organization,
            language='en',
            notification_preferences={
                'email_notifications': True,
                'push_notifications': True,
                'course_enrollment_notifications': True,
                'class_reminder_notifications': True,
                'assignment_due_notifications': True,
                'payment_notifications': True,
                'system_notifications': True,
            }
        )
    
    def test_get_user_preferences(self):
        """Test getting user notification preferences"""
        preferences = NotificationService.get_user_preferences(self.user)
        
        self.assertTrue(preferences['email_notifications'])
        self.assertTrue(preferences['course_enrollment_notifications'])
        self.assertTrue(preferences['system_notifications'])
    
    @patch('apps.notifications.services.EmailService.send_notification_email')
    @patch('apps.notifications.services.WebSocketNotificationService.send_realtime_notification')
    def test_create_notification_with_i18n(self, mock_websocket, mock_email):
        """Test creating notification with i18n support"""
        mock_email.return_value = True
        mock_websocket.return_value = True
        
        # Create notification with context for localization
        notification = NotificationService.create_notification(
            user=self.user,
            title="Test Title",  # Will be overridden by i18n
            message="Test Message",  # Will be overridden by i18n
            notification_type='course_enrollment',
            tenant=self.organization,
            context={'course_title': 'Python Programming'}
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.tenant, self.organization)
        self.assertEqual(notification.notification_type, 'course_enrollment')
        
        # Check that localized content was used
        self.assertIn('Python Programming', notification.title)
        self.assertIn('Python Programming', notification.message)


class EmailServiceTests(TestCase):
    """Test email service"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            subdomain="test"
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            tenant=self.organization,
            language='en'
        )
    
    def test_send_notification_email(self):
        """Test sending notification email"""
        notification = Notification.objects.create(
            user=self.user,
            tenant=self.organization,
            title="Test Notification",
            message="This is a test notification",
            notification_type="system"
        )
        
        # Clear any existing emails
        mail.outbox = []
        
        result = EmailService.send_notification_email(notification)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        sent_email = mail.outbox[0]
        self.assertIn("Test Notification", sent_email.subject)
        self.assertEqual(sent_email.to, [self.user.email])


class WebSocketNotificationServiceTests(TestCase):
    """Test WebSocket notification service"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            subdomain="test"
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
    
    @patch('channels.layers.get_channel_layer')
    def test_send_realtime_notification(self, mock_get_channel_layer):
        """Test sending real-time notification"""
        mock_channel_layer = MagicMock()
        mock_get_channel_layer.return_value = mock_channel_layer
        
        notification_data = {
            'id': 'test-id',
            'title': 'Test Notification',
            'message': 'Test message',
            'type': 'system'
        }
        
        result = WebSocketNotificationService.send_realtime_notification(
            self.user, notification_data
        )
        
        self.assertTrue(result)
        mock_channel_layer.group_send.assert_called_once()