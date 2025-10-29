#!/usr/bin/env python3
"""
Standalone notification system integration test runner
Tests the notification system without requiring full Django test framework
"""

import os
import sys
import django
import asyncio
import json
import time
from datetime import datetime

# Add the backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, backend_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# Now import Django modules
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async

from apps.accounts.models import Organization, UserProfile
from apps.notifications.models import Notification, EmailDeliveryLog, WebSocketConnection
from apps.notifications.services import NotificationService, EmailService, WebSocketNotificationService
from apps.notifications.consumers import NotificationConsumer
from apps.notifications.i18n_service import NotificationI18nService

User = get_user_model()

class NotificationSystemTester:
    """Standalone notification system tester"""
    
    def __init__(self):
        self.setup_test_data()
        self.test_results = []
    
    def setup_test_data(self):
        """Set up test data"""
        print("Setting up test data...")
        
        # Create or get test organization
        self.organization, created = Organization.objects.get_or_create(
            subdomain="test",
            defaults={
                'name': "Test Organization",
                'id': "81cbaac8-7f8a-4fd1-b3da-c1ee97945ea3"
            }
        )
        
        # Create test users with different languages
        self.user_en, created = User.objects.get_or_create(
            email="test_user_en@example.com",
            defaults={
                'first_name': "English",
                'last_name': "User"
            }
        )
        if created:
            self.user_en.set_password("testpass123")
            self.user_en.save()
        
        self.user_ar, created = User.objects.get_or_create(
            email="test_user_ar@example.com",
            defaults={
                'first_name': "Arabic", 
                'last_name': "User"
            }
        )
        if created:
            self.user_ar.set_password("testpass123")
            self.user_ar.save()
        
        # Create user profiles with different languages and preferences
        self.profile_en, created = UserProfile.objects.get_or_create(
            user=self.user_en,
            defaults={
                'tenant': self.organization,
                'language': 'en',
                'notification_preferences': {
                    'email_notifications': True,
                    'push_notifications': True,
                    'course_enrollment_notifications': True,
                    'class_reminder_notifications': True,
                    'assignment_due_notifications': True,
                    'payment_notifications': True,
                    'system_notifications': True,
                }
            }
        )
        
        self.profile_ar, created = UserProfile.objects.get_or_create(
            user=self.user_ar,
            defaults={
                'tenant': self.organization,
                'language': 'ar',
                'notification_preferences': {
                    'email_notifications': True,
                    'push_notifications': False,
                    'course_enrollment_notifications': True,
                    'class_reminder_notifications': False,
                    'assignment_due_notifications': True,
                    'payment_notifications': True,
                    'system_notifications': True,
                }
            }
        )
        
        print("✓ Test data setup complete")
    
    def test_email_notification_sending(self):
        """Test email notification sending"""
        print("\n[1] Testing Email Notification Sending")
        
        try:
            # Clear mail outbox
            mail.outbox = []
            
            # Create notification with email
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
            
            # Check that notification was created
            assert notification is not None, "Notification was not created"
            assert notification.user == self.user_en, "Notification user mismatch"
            assert 'Python Programming' in notification.title, "Localized content not applied"
            
            # Check that email was sent
            assert len(mail.outbox) >= 1, f"Expected at least 1 email, got {len(mail.outbox)}"
            
            sent_email = mail.outbox[0]
            assert self.user_en.email in sent_email.to, "Email recipient mismatch"
            assert 'Python Programming' in sent_email.body, "Email content missing course title"
            
            # Check email delivery log
            delivery_logs = EmailDeliveryLog.objects.filter(notification=notification)
            assert delivery_logs.count() >= 1, "Email delivery not logged"
            
            log = delivery_logs.first()
            assert log.status == 'sent', f"Expected status 'sent', got '{log.status}'"
            assert log.recipient_email == self.user_en.email, "Delivery log recipient mismatch"
            
            self.test_results.append(("Email Notification Sending", True, ""))
            print("✓ Email notifications working correctly")
            
        except Exception as e:
            self.test_results.append(("Email Notification Sending", False, str(e)))
            print(f"❌ Email notification test failed: {e}")
    
    def test_notification_preferences_filtering(self):
        """Test notification preferences and filtering"""
        print("\n[2] Testing Notification Preferences and Filtering")
        
        try:
            # Clear mail outbox
            mail.outbox = []
            
            # Test user with specific notification type disabled (user_ar has class_reminder_notifications=False)
            notification = NotificationService.create_notification(
                user=self.user_ar,
                title="Class Reminder Test",
                message="This should not send email due to type preference",
                notification_type='class_reminder',
                tenant=self.organization,
                context={'class_title': 'Math Class', 'minutes': 30}
            )
            
            # Notification should be created but email should not be sent
            assert notification is not None, "Notification was not created"
            assert not notification.sent_email, "Email was sent despite preferences"
            assert len(mail.outbox) == 0, f"Expected 0 emails, got {len(mail.outbox)}"
            
            # Test user with enabled preferences (user_en)
            notification2 = NotificationService.create_notification(
                user=self.user_en,
                title="Enabled Preference Test",
                message="This should send email",
                notification_type='assignment_due',
                tenant=self.organization
            )
            
            # Should send email because user_en has all notifications enabled
            assert notification2.sent_email, "Email was not sent despite enabled preferences"
            assert len(mail.outbox) >= 1, f"Expected at least 1 email, got {len(mail.outbox)}"
            
            # Test preference retrieval
            preferences_en = NotificationService.get_user_preferences(self.user_en)
            assert preferences_en['email_notifications'], "Email notifications should be enabled for user_en"
            assert preferences_en['course_enrollment_notifications'], "Course enrollment notifications should be enabled"
            
            preferences_ar = NotificationService.get_user_preferences(self.user_ar)
            assert preferences_ar['email_notifications'], "Email notifications should be enabled for user_ar"
            assert not preferences_ar['class_reminder_notifications'], "Class reminder notifications should be disabled for user_ar"
            
            self.test_results.append(("Notification Preferences Filtering", True, ""))
            print("✓ Notification preferences and filtering working correctly")
            
        except Exception as e:
            self.test_results.append(("Notification Preferences Filtering", False, str(e)))
            print(f"❌ Notification preferences test failed: {e}")
    
    def test_multi_language_support(self):
        """Test multi-language notification support"""
        print("\n[3] Testing Multi-Language Notification Support")
        
        try:
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
            assert 'Python Programming' in notification_en.title, "English localization not applied to title"
            assert 'Python Programming' in notification_en.message, "English localization not applied to message"
            
            # Check email was sent in English
            assert len(mail.outbox) >= 1, "English email was not sent"
            english_email = mail.outbox[0]
            assert 'Python Programming' in english_email.body, "English email content missing course title"
            
            # Test Arabic notification
            mail.outbox = []
            
            notification_ar = NotificationService.create_notification(
                user=self.user_ar,
                title="Will be localized",
                message="Will be localized",
                notification_type='course_enrollment', 
                tenant=self.organization,
                send_email=True,
                contex
t={'course_title': 'برمجة بايثون'}
            )
            
            # Check that Arabic localization was applied
            assert 'برمجة بايثون' in notification_ar.title, "Arabic localization not applied to title"
            assert 'برمجة بايثون' in notification_ar.message, "Arabic localization not applied to message"
            
            # Check email was sent in Arabic
            assert len(mail.outbox) >= 1, "Arabic email was not sent"
            arabic_email = mail.outbox[0]
            assert 'برمجة بايثون' in arabic_email.body, "Arabic email content missing course title"
            
            # Test i18n service directly
            en_message = NotificationI18nService.get_localized_message(
                'course_enrollment', 'en', {'course_title': 'Test Course'}
            )
            assert en_message['language'] == 'en', "English language not set correctly"
            assert not en_message['is_rtl'], "English should not be RTL"
            assert 'Test Course' in en_message['title'], "English message title missing course title"
            
            ar_message = NotificationI18nService.get_localized_message(
                'course_enrollment', 'ar', {'course_title': 'دورة تجريبية'}
            )
            assert ar_message['language'] == 'ar', "Arabic language not set correctly"
            assert ar_message['is_rtl'], "Arabic should be RTL"
            assert 'دورة تجريبية' in ar_message['title'], "Arabic message title missing course title"
            
            # Test supported languages
            languages = NotificationI18nService.get_all_supported_languages()
            assert 'en' in languages, "English not in supported languages"
            assert 'ar' in languages, "Arabic not in supported languages"
            assert 'so' in languages, "Somali not in supported languages"
            
            self.test_results.append(("Multi-Language Support", True, ""))
            print("✓ Multi-language notification support working correctly")
            
        except Exception as e:
            self.test_results.append(("Multi-Language Support", False, str(e)))
            print(f"❌ Multi-language support test failed: {e}")
    
    def test_websocket_real_time_delivery(self):
        """Test real-time notification delivery via WebSocket"""
        print("\n[4] Testing Real-Time WebSocket Delivery")
        
        async def test_websocket():
            try:
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
                if not connected:
                    return False, "WebSocket connection failed"
                
                # Receive connection confirmation
                response = await communicator.receive_json_from()
                if response['type'] != 'connection_established':
                    return False, f"Expected connection_established, got {response['type']}"
                
                # Receive initial unread count
                response = await communicator.receive_json_from()
                if response['type'] != 'unread_count':
                    return False, f"Expected unread_count, got {response['type']}"
                
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
                if response['type'] != 'notification':
                    return False, f"Expected notification, got {response['type']}"
                
                if response['notification']['title'] != "Test Real-Time Notification":
                    return False, "Notification title mismatch"
                
                # Test marking notification as read via WebSocket
                await communicator.send_json_to({
                    'type': 'mark_read',
                    'notification_id': str(notification.id)
                })
                
                # Should receive confirmation
                response = await communicator.receive_json_from()
                if response['type'] != 'mark_read_response':
                    return False, f"Expected mark_read_response, got {response['type']}"
                
                if not response['success']:
                    return False, "Mark as read failed"
                
                # Test ping/pong
                await communicator.send_json_to({
                    'type': 'ping'
                })
                
                response = await communicator.receive_json_from()
                if response['type'] != 'pong':
                    return False, f"Expected pong, got {response['type']}"
                
                # Disconnect
                await communicator.disconnect()
                
                return True, "WebSocket tests passed"
                
            except Exception as e:
                return False, f"WebSocket test error: {str(e)}"
        
        try:
            # Run the async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success, message = loop.run_until_complete(test_websocket())
                if success:
                    self.test_results.append(("Real-Time WebSocket Delivery", True, ""))
                    print("✓ Real-time WebSocket notifications working correctly")
                else:
                    self.test_results.append(("Real-Time WebSocket Delivery", False, message))
                    print(f"❌ WebSocket test failed: {message}")
            finally:
                loop.close()
                
        except Exception as e:
            self.test_results.append(("Real-Time WebSocket Delivery", False, str(e)))
            print(f"❌ WebSocket test failed: {e}")
    
    def test_bulk_operations(self):
        """Test bulk notification operations"""
        print("\n[5] Testing Bulk Notification Operations")
        
        try:
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
                }
            ]
            
            created_notifications = NotificationService.bulk_create_notifications(notifications_data)
            
            # Check that all notifications were created
            assert len(created_notifications) == 2, f"Expected 2 notifications, got {len(created_notifications)}"
            
            # Check that emails were sent based on user preferences
            # Both users have email enabled for system notifications
            assert len(mail.outbox) >= 2, f"Expected at least 2 emails, got {len(mail.outbox)}"
            
            # Test bulk WebSocket notifications (method should not crash)
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
            
            # This would normally send via WebSocket, just verify method doesn't crash
            result = WebSocketNotificationService.send_bulk_realtime_notifications(user_notification_pairs)
            # Result might be False if no channel layer is configured, but method should not crash
            
            self.test_results.append(("Bulk Operations", True, ""))
            print("✓ Bulk notification operations working correctly")
            
        except Exception as e:
            self.test_results.append(("Bulk Operations", False, str(e)))
            print(f"❌ Bulk operations test failed: {e}")
    
    def test_delivery_tracking(self):
        """Test notification delivery tracking"""
        print("\n[6] Testing Notification Delivery Tracking")
        
        try:
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
            
            assert stats['email_sent'], "Email delivery not tracked"
            assert stats['websocket_sent'], "WebSocket delivery not tracked"
            assert stats['total_attempts'] >= 1, "No delivery attempts tracked"
            assert stats['successful_deliveries'] >= 1, "No successful deliveries tracked"
            
            # Test email analytics
            from apps.notifications.services import EmailAutomationService
            
            analytics = EmailAutomationService.get_email_analytics()
            
            # Should have basic structure even if no data
            assert 'total_emails_sent' in analytics, "Missing total_emails_sent in analytics"
            assert 'successful_deliveries' in analytics, "Missing successful_deliveries in analytics"
            assert 'failed_deliveries' in analytics, "Missing failed_deliveries in analytics"
            assert 'delivery_rate' in analytics, "Missing delivery_rate in analytics"
            
            self.test_results.append(("Delivery Tracking", True, ""))
            print("✓ Notification delivery tracking working correctly")
            
        except Exception as e:
            self.test_results.append(("Delivery Tracking", False, str(e)))
            print(f"❌ Delivery tracking test failed: {e}")
    
    def run_all_tests(self):
        """Run all notification system tests"""
        print("==> EduRise Notification System - Integration Tests\n")
        
        # Run all tests
        self.test_email_notification_sending()
        self.test_notification_preferences_filtering()
        self.test_multi_language_support()
        self.test_websocket_real_time_delivery()
        self.test_bulk_operations()
        self.test_delivery_tracking()
        
        # Print results summary
        print("\n" + "="*60)
        print("NOTIFICATION SYSTEM TEST RESULTS:")
        print("="*60)
        
        passed = 0
        failed = 0
        
        for test_name, success, error in self.test_results:
            status = "✓ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
            if not success and error:
                print(f"    Error: {error}")
            
            if success:
                passed += 1
            else:
                failed += 1
        
        print("\n" + "="*60)
        if failed == 0:
            print("SUCCESS: ALL NOTIFICATION INTEGRATION TESTS PASSED!")
            print(f"- {passed} tests passed")
            print("- Real-time WebSocket notifications working")
            print("- Email notifications with i18n support working")
            print("- Notification preferences and filtering working")
            print("- Multi-language support working")
            print("- Bulk operations working")
            print("- Delivery tracking working")
            print("\n==> The EduRise notification system is fully operational!")
            return True
        else:
            print(f"FAILURE: {failed} test(s) failed, {passed} test(s) passed")
            print("Check the errors above for details.")
            return False


def main():
    """Main function to run notification system tests"""
    try:
        tester = NotificationSystemTester()
        success = tester.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)