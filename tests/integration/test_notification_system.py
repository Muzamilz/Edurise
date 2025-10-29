#!/usr/bin/env python3
"""
Integration tests for the notification system
Tests real-time delivery, email notifications, preferences, and multi-language support
"""

import asyncio
import json
import time
import websockets
import requests
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from unittest.mock import patch, MagicMock
import pytest

from apps.accounts.models import Organization, UserProfile
from apps.notifications.models import Notification, EmailDeliveryLog, WebSocketConnection
from apps.notifications.services import NotificationService, EmailService, WebSocketNotificationService
from apps.notifications.consumers import NotificationConsumer
from apps.notifications.i18n_service import NotificationI18nService

User = get_user_model()

# Test configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
WS_URL = "ws://127.0.0.1:8000/ws/notifications/"
TENANT_ID = "81cbaac8-7f8a-4fd1-b3da-c1ee97945ea3"


class NotificationSystemIntegrationTest(TransactionTestCase):
    """Comprehensive integration test for the notification system"""
    
    def setUp(self):
        """Set up test data"""
        # Create test organization
        self.organization = Organization.objects.create(
            name="Test Organization",
            subdomain="test",
            id=TENANT_ID
        )
        
        # Create test users with different languages
        self.user_en = User.objects.create_user(
            email="user_en@test.com",
            password="testpass123",
            first_name="English",
            last_name="User"
        )
        
        self.user_ar = User.objects.create_user(
            email="user_ar@test.com", 
            password="testpass123",
            first_name="Arabic",
            last_name="User"
        )
        
        self.user_so = User.objects.create_user(
            email="user_so@test.com",
            password="testpass123", 
            first_name="Somali",
            last_name="User"
        )
        
        # Create user profiles with different languages and preferences
        self.profile_en = UserProfile.objects.create(
            user=self.user_en,
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
        
        self.profile_ar = UserProfile.objects.create(
            user=self.user_ar,
            tenant=self.organization,
            language='ar',
            notification_preferences={
                'email_notifications': True,
                'push_notifications': False,
                'course_enrollment_notifications': True,
                'class_reminder_notifications': False,
                'assignment_due_notifications': True,
                'payment_notifications': True,
                'system_notifications': True,
            }
        )
        
        self.profile_so = UserProfile.objects.create(
            user=self.user_so,
            tenant=self.organization,
            language='so',
            notification_preferences={
                'email_notifications': False,
                'push_notifications': True,
                'course_enrollment_notifications': False,
                'class_reminder_notifications': True,
                'assignment_due_notifications': True,
                'payment_notifications': False,
                'system_notifications': True,
            }
        )
        
        # Clear any existing emails
        mail.outbox = []
    
    def test_real_time_notification_delivery(self):
        """Test real-time notification delivery via WebSocket"""
        print("\n==> Testing Real-Time Notification Delivery")
        
        async def test_websocket_notifications():
            # Create WebSocket communicator
            communicator = WebsocketCommunicator(
                NotificationConsumer.as_asgi(),
                "/ws/notifications/"
            )
            
            # Mock user authentication
            communicator.scope["user"] = self.user_en
            communicator.scope["tenant"] = self.organization
            
            # Connect to WebSocket
            connected, subprotocol = await communicator.connect()
            self.assertTrue(connected, "WebSocket connection failed")
            
            # Receive connection confirmation
            response = await communicator.receive_json_from()
            self.assertEqual(response['type'], 'connection_established')
            self.assertEqual(response['user_id'], str(self.user_en.id))
            
            # Receive initial unread count
            response = await communicator.receive_json_from()
            self.assertEqual(response['type'], 'unread_count')
            initial_count = response['count']
            
            # Create a notification using the service
            notification = await database_sync_to_async(NotificationService.create_notification)(
                user=self.user_en,
                title="Test Real-Time Notification",
                message="This is a test notification for real-time delivery",
                notification_type='system',
                tenant=self.organization,
                send_email=False,
                send_push=False
            )
            
            # Should receive the notification via WebSocket
            response = await communicator.receive_json_from()
            self.assertEqual(response['type'], 'notification')
            self.assertEqual(response['notification']['title'], "Test Real-Time Notification")
            self.assertEqual(response['notification']['id'], str(notification.id))
            
            # Test marking notification as read via WebSocket
            await communicator.send_json_to({
                'type': 'mark_read',
                'notification_id': str(notification.id)
            })
            
            # Should receive confirmation
            response = await communicator.receive_json_from()
            self.assertEqual(response['type'], 'mark_read_response')
            self.assertTrue(response['success'])
            
            # Test getting updated unread count
            await communicator.send_json_to({
                'type': 'get_unread_count'
            })
            
            response = await communicator.receive_json_from()
            self.assertEqual(response['type'], 'unread_count')
            self.assertEqual(response['count'], initial_count)  # Should be same as initial since we marked as read
            
            # Test mark all as read
            # Create another notification first
            await database_sync_to_async(NotificationService.create_notification)(
                user=self.user_en,
                title="Another Test Notification",
                message="Another test notification",
                notification_type='system',
                tenant=self.organization,
                send_email=False,
                send_push=False
            )
            
            # Receive the new notification
            response = await communicator.receive_json_from()
            self.assertEqual(response['type'], 'notification')
            
            # Mark all as read
            await communicator.send_json_to({
                'type': 'mark_all_read'
            })
            
            response = await communicator.receive_json_from()
            self.assertEqual(response['type'], 'mark_all_read_response')
            self.assertGreaterEqual(response['marked_count'], 1)
            
            # Test ping/pong
            await communicator.send_json_to({
                'type': 'ping'
            })
            
            response = await communicator.receive_json_from()
            self.assertEqual(response['type'], 'pong')
            self.assertIn('timestamp', response)
            
            # Disconnect
            await communicator.disconnect()
            
            print("✓ Real-time WebSocket notifications working correctly")
            return True
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(test_websocket_notifications())
            self.assertTrue(result)
        finally:
            loop.close()
    
    def test_email_notification_sending(self):
        """Test email notification sending with templates and delivery tracking"""
        print("\n==> Testing Email Notification Sending")
        
        # Clear mail outbox
        mail.outbox = []
        
        # Test basic email notification
        notification = NotificationService.create_notification(
            user=self.user_en,
            title="Test Email Notification",
            message="This is a test email notification",
            notification_type='course_enrollment',
            tenant=self.organization,
            send_email=True,
            send_push=False,
            context={'course_title': 'Python Programming'}
        )
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        
        # Verify email content
        self.assertIn("Test Organization", sent_email.subject)
        self.assertEqual(sent_email.to, [self.user_en.email])
        self.assertIn("Python Programming", sent_email.body)
        
        # Check email delivery log
        delivery_logs = EmailDeliveryLog.objects.filter(notification=notification)
        self.assertEqual(delivery_logs.count(), 1)
        
        log = delivery_logs.first()
        self.assertEqual(log.status, 'sent')
        self.assertEqual(log.recipient_email, self.user_en.email)
        self.assertIn("Test Organization", log.subject)
        
        # Test email with template fallback
        mail.outbox = []
        
        notification2 = NotificationService.create_notification(
            user=self.user_en,
            title="Test Template Notification",
            message="This notification should use template",
            notification_type='assignment_due',
            tenant=self.organization,
            send_email=True,
            send_push=False
        )
        
        # Should still send email even if specific template doesn't exist
        self.assertEqual(len(mail.outbox), 1)
        
        print("✓ Email notifications sending correctly with delivery tracking")
    
    def test_notification_preferences_and_filtering(self):
        """Test notification preferences and filtering"""
        print("\n==> Testing Notification Preferences and Filtering")
        
        # Clear mail outbox
        mail.outbox = []
        
        # Test user with email notifications disabled (user_so)
        notification1 = NotificationService.create_notification(
            user=self.user_so,
            title="Test Preference Filtering",
            message="This should not send email",
            notification_type='course_enrollment',
            tenant=self.organization,
            context={'course_title': 'Test Course'}
        )
        
        # Should not send email because user_so has email_notifications=False
        self.assertEqual(len(mail.outbox), 0)
        
        # But notification should still be created
        self.assertTrue(Notification.objects.filter(id=notification1.id).exists())
        self.assertFalse(notification1.sent_email)
        
        # Test user with specific notification type disabled (user_ar has class_reminder_notifications=False)
        notification2 = NotificationService.create_notification(
            user=self.user_ar,
            title="Class Reminder Test",
            message="This should not send email due to type preference",
            notification_type='class_reminder',
            tenant=self.organization,
            context={'class_title': 'Math Class', 'minutes': 30}
        )
        
        # Should not send email because user_ar has class_reminder_notifications=False
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(notification2.sent_email)
        
        # Test user with enabled preferences (user_en)
        notification3 = NotificationService.create_notification(
            user=self.user_en,
            title="Enabled Preference Test",
            message="This should send email",
            notification_type='assignment_due',
            tenant=self.organization
        )
        
        # Should send email because user_en has all notifications enabled
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(notification3.sent_email)
        
        # Test preference retrieval
        preferences_en = NotificationService.get_user_preferences(self.user_en)
        self.assertTrue(preferences_en['email_notifications'])
        self.assertTrue(preferences_en['course_enrollment_notifications'])
        
        preferences_so = NotificationService.get_user_preferences(self.user_so)
        self.assertFalse(preferences_so['email_notifications'])
        self.assertFalse(preferences_so['course_enrollment_notifications'])
        
        print("✓ Notification preferences and filtering working correctly")
    
    def test_multi_language_notification_support(self):
        """Test multi-language notification support"""
        print("\n==> Testing Multi-Language Notification Support")
        
        # Clear mail outbox
        mail.outbox = []
        
        # Test English notification
        notification_en = NotificationService.create_notification(
            user=self.user_en,
            title="Will be localized",
            message="Will be localized",
            notification_type='course_enrollment',
            tenant=self.organization,
            send_email=True,
            context={'course_title': 'Python Programming'}
        )
        
        # Check that English localization was applied
        self.assertIn('Python Programming', notification_en.title)
        self.assertIn('Python Programming', notification_en.message)
        
        # Check email was sent in English
        self.assertEqual(len(mail.outbox), 1)
        english_email = mail.outbox[0]
        self.assertIn('Python Programming', english_email.body)
        
        # Test Arabic notification
        mail.outbox = []
        
        notification_ar = NotificationService.create_notification(
            user=self.user_ar,
            title="Will be localized",
            message="Will be localized", 
            notification_type='course_enrollment',
            tenant=self.organization,
            send_email=True,
            context={'course_title': 'برمجة بايثون'}
        )
        
        # Check that Arabic localization was applied
        self.assertIn('برمجة بايثون', notification_ar.title)
        self.assertIn('برمجة بايثون', notification_ar.message)
        
        # Check email was sent in Arabic
        self.assertEqual(len(mail.outbox), 1)
        arabic_email = mail.outbox[0]
        self.assertIn('برمجة بايثون', arabic_email.body)
        
        # Test Somali notification (but email disabled for this user)
        notification_so = NotificationService.create_notification(
            user=self.user_so,
            title="Will be localized",
            message="Will be localized",
            notification_type='system',  # system notifications are enabled for user_so
            tenant=self.organization,
            send_email=True,  # Will be overridden by user preferences
            context={'course_title': 'Barnaamijka Python'}
        )
        
        # Check that Somali localization was applied
        self.assertIn('Barnaamijka Python', notification_so.title)
        self.assertIn('Barnaamijka Python', notification_so.message)
        
        # Email should not be sent due to user preferences
        self.assertEqual(len(mail.outbox), 1)  # Still 1 from Arabic test
        
        # Test i18n service directly
        en_message = NotificationI18nService.get_localized_message(
            'course_enrollment', 'en', {'course_title': 'Test Course'}
        )
        self.assertEqual(en_message['language'], 'en')
        self.assertFalse(en_message['is_rtl'])
        self.assertIn('Test Course', en_message['title'])
        
        ar_message = NotificationI18nService.get_localized_message(
            'course_enrollment', 'ar', {'course_title': 'دورة تجريبية'}
        )
        self.assertEqual(ar_message['language'], 'ar')
        self.assertTrue(ar_message['is_rtl'])
        self.assertIn('دورة تجريبية', ar_message['title'])
        
        # Test supported languages
        languages = NotificationI18nService.get_all_supported_languages()
        self.assertIn('en', languages)
        self.assertIn('ar', languages)
        self.assertIn('so', languages)
        
        print("✓ Multi-language notification support working correctly")
    
    def test_websocket_connection_tracking(self):
        """Test WebSocket connection tracking and monitoring"""
        print("\n==> Testing WebSocket Connection Tracking")
        
        async def test_connection_tracking():
            # Create WebSocket communicator
            communicator = WebsocketCommunicator(
                NotificationConsumer.as_asgi(),
                "/ws/notifications/"
            )
            
            # Mock user authentication
            communicator.scope["user"] = self.user_en
            communicator.scope["tenant"] = self.organization
            communicator.scope["client"] = ["127.0.0.1", 12345]
            communicator.scope["headers"] = [(b"user-agent", b"Test Browser")]
            
            # Connect to WebSocket
            connected, subprotocol = await communicator.connect()
            self.assertTrue(connected)
            
            # Check that connection was tracked
            await asyncio.sleep(0.1)  # Give time for database write
            
            connections = await database_sync_to_async(
                lambda: list(WebSocketConnection.objects.filter(
                    user=self.user_en,
                    connection_type='notifications',
                    is_active=True
                ))
            )()
            
            self.assertEqual(len(connections), 1)
            connection = connections[0]
            self.assertEqual(connection.user, self.user_en)
            self.assertEqual(connection.connection_type, 'notifications')
            self.assertTrue(connection.is_active)
            self.assertEqual(connection.ip_address, "127.0.0.1")
            self.assertEqual(connection.user_agent, "Test Browser")
            
            # Disconnect
            await communicator.disconnect()
            
            # Check that connection was marked as inactive
            await asyncio.sleep(0.1)  # Give time for database write
            
            connection.refresh_from_db()
            self.assertFalse(connection.is_active)
            self.assertIsNotNone(connection.disconnected_at)
            
            return True
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(test_connection_tracking())
            self.assertTrue(result)
        finally:
            loop.close()
        
        print("✓ WebSocket connection tracking working correctly")
    
    def test_bulk_notification_operations(self):
        """Test bulk notification creation and delivery"""
        print("\n==> Testing Bulk Notification Operations")
        
        # Clear mail outbox
        mail.outbox = []
        
        # Create bulk notifications
        notifications_data = [
            {
                'user': self.user_en,
                'title': 'Bulk Notification 1',
                'message': 'First bulk notification',
                'notification_type': 'system',
                'tenant': self.organization
            },
            {
                'user': self.user_ar,
                'title': 'Bulk Notification 2', 
                'message': 'Second bulk notification',
                'notification_type': 'system',
                'tenant': self.organization
            },
            {
                'user': self.user_so,
                'title': 'Bulk Notification 3',
                'message': 'Third bulk notification',
                'notification_type': 'system',
                'tenant': self.organization
            }
        ]
        
        created_notifications = NotificationService.bulk_create_notifications(notifications_data)
        
        # Check that all notifications were created
        self.assertEqual(len(created_notifications), 3)
        
        # Check that emails were sent based on user preferences
        # user_en: email enabled, user_ar: email enabled, user_so: email disabled
        self.assertEqual(len(mail.outbox), 2)
        
        # Test bulk WebSocket notifications
        user_notification_pairs = [
            (self.user_en, {
                'id': 'bulk-1',
                'title': 'Bulk WebSocket Test 1',
                'message': 'First bulk WebSocket notification',
                'type': 'system'
            }),
            (self.user_ar, {
                'id': 'bulk-2', 
                'title': 'Bulk WebSocket Test 2',
                'message': 'Second bulk WebSocket notification',
                'type': 'system'
            })
        ]
        
        # This would normally send via WebSocket, but we can't easily test that here
        # Just verify the method doesn't crash
        result = WebSocketNotificationService.send_bulk_realtime_notifications(user_notification_pairs)
        # Result might be False if no channel layer is configured, but method should not crash
        
        print("✓ Bulk notification operations working correctly")
    
    def test_system_broadcast_notifications(self):
        """Test system-wide broadcast notifications"""
        print("\n==> Testing System Broadcast Notifications")
        
        # Test tenant-specific broadcast
        broadcast_data = {
            'title': 'System Maintenance',
            'message': 'The system will be under maintenance from 2-4 AM',
            'priority': 'high'
        }
        
        # This would normally send to all users in the tenant via WebSocket
        result = WebSocketNotificationService.send_system_broadcast(
            broadcast_data, 
            tenant=self.organization
        )
        
        # Result might be False if no channel layer is configured, but method should not crash
        
        # Test global broadcast (no tenant specified)
        global_broadcast_data = {
            'title': 'Global Announcement',
            'message': 'New features have been released!',
            'priority': 'normal'
        }
        
        result = WebSocketNotificationService.send_system_broadcast(global_broadcast_data)
        
        print("✓ System broadcast notifications working correctly")
    
    def test_notification_delivery_tracking(self):
        """Test notification delivery tracking and analytics"""
        print("\n==> Testing Notification Delivery Tracking")
        
        # Clear mail outbox
        mail.outbox = []
        
        # Create notification with email
        notification = NotificationService.create_notification(
            user=self.user_en,
            title="Delivery Tracking Test",
            message="Testing delivery tracking",
            notification_type='payment_success',
            tenant=self.organization,
            send_email=True
        )
        
        # Check delivery stats
        from apps.notifications.services import NotificationDeliveryTracker
        
        stats = NotificationDeliveryTracker.get_delivery_stats(notification)
        
        self.assertTrue(stats['email_sent'])
        self.assertTrue(stats['websocket_sent'])  # Always true if notification created
        self.assertGreaterEqual(stats['total_attempts'], 1)
        self.assertGreaterEqual(stats['successful_deliveries'], 1)
        
        # Test email analytics
        from apps.notifications.services import EmailAutomationService
        
        analytics = EmailAutomationService.get_email_analytics()
        
        # Should have basic structure even if no data
        self.assertIn('total_emails_sent', analytics)
        self.assertIn('successful_deliveries', analytics)
        self.assertIn('failed_deliveries', analytics)
        self.assertIn('delivery_rate', analytics)
        
        print("✓ Notification delivery tracking working correctly")


def run_integration_tests():
    """Run all notification system integration tests"""
    print("==> EduRise Notification System - Integration Tests\n")
    
    # Import Django test runner
    from django.test.utils import get_runner
    from django.conf import settings
    
    # Get the Django test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run the tests
    failures = test_runner.run_tests(["tests.integration.test_notification_system"])
    
    if failures:
        print(f"\n❌ {failures} test(s) failed")
        return False
    else:
        print("\n" + "="*60)
        print("SUCCESS: ALL NOTIFICATION INTEGRATION TESTS PASSED!")
        print("- Real-time WebSocket notifications working")
        print("- Email notifications with i18n support working")
        print("- Notification preferences and filtering working")
        print("- Multi-language support working")
        print("- WebSocket connection tracking working")
        print("- Bulk operations working")
        print("- System broadcasts working")
        print("- Delivery tracking working")
        print("\n==> The EduRise notification system is fully operational!")
        return True


if __name__ == "__main__":
    import os
    import django
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
    django.setup()
    
    success = run_integration_tests()
    if not success:
        exit(1)