from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from .models import Notification
from .i18n_service import NotificationI18nService, NotificationTemplateI18nService


class NotificationService:
    """Enhanced service for sending notifications through centralized API"""
    
    @staticmethod
    def create_notification(user, title, message, notification_type, tenant, 
                          related_object_id=None, related_object_type=None,
                          send_email=None, send_push=None, context=None):
        """Create and optionally send notification with user preferences and i18n support"""
        
        # Get user's preferred language
        user_language = NotificationI18nService.get_user_language(user)
        
        # Get localized message if context is provided
        if context:
            localized_content = NotificationI18nService.get_localized_message(
                notification_type, user_language, context
            )
            title = localized_content['title']
            message = localized_content['message']
        
        # Check user preferences if not explicitly specified
        if send_email is None or send_push is None:
            preferences = NotificationService.get_user_preferences(user)
            
            if send_email is None:
                send_email = preferences.get('email_notifications', True)
                # Check specific type preferences
                type_key = f"{notification_type}_notifications"
                if type_key in preferences:
                    send_email = send_email and preferences[type_key]
            
            if send_push is None:
                send_push = preferences.get('push_notifications', True)
                # Check specific type preferences
                type_key = f"{notification_type}_notifications"
                if type_key in preferences:
                    send_push = send_push and preferences[type_key]
        
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            tenant=tenant,
            related_object_id=related_object_id,
            related_object_type=related_object_type or ''
        )
        
        # Send email if requested and user allows it
        if send_email:
            try:
                EmailService.send_notification_email(notification)
                notification.sent_email = True
                notification.save()
            except Exception as e:
                print(f"Failed to send email notification: {str(e)}")
        
        # Send push notification if requested and user allows it
        if send_push:
            try:
                PushNotificationService.send_push(notification)
                notification.sent_push = True
                notification.save()
            except Exception as e:
                print(f"Failed to send push notification: {str(e)}")
        
        # Send real-time WebSocket notification
        try:
            WebSocketNotificationService.send_realtime_notification(user, {
                'id': str(notification.id),
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.isoformat(),
            })
        except Exception as e:
            print(f"Failed to send WebSocket notification: {str(e)}")
        
        return notification
    
    @staticmethod
    def get_user_preferences(user):
        """Get user notification preferences"""
        # Try to get preferences from user profile
        if hasattr(user, 'profiles'):
            profiles = user.profiles.all()
            if profiles.exists():
                profile = profiles.first()
                if profile.notification_preferences:
                    return profile.notification_preferences
        
        # Return default preferences
        return {
            'email_notifications': True,
            'push_notifications': True,
            'course_enrollment_notifications': True,
            'class_reminder_notifications': True,
            'assignment_due_notifications': True,
            'payment_notifications': True,
            'system_notifications': True,
        }
    
    @staticmethod
    def bulk_create_notifications(notifications_data):
        """Create multiple notifications efficiently"""
        notifications = []
        for data in notifications_data:
            notification = Notification(
                user=data['user'],
                title=data['title'],
                message=data['message'],
                notification_type=data['notification_type'],
                tenant=data['tenant'],
                related_object_id=data.get('related_object_id'),
                related_object_type=data.get('related_object_type')
            )
            notifications.append(notification)
        
        created_notifications = Notification.objects.bulk_create(notifications)
        
        # Send emails and push notifications for bulk created notifications
        for notification in created_notifications:
            preferences = NotificationService.get_user_preferences(notification.user)
            
            if preferences.get('email_notifications', True):
                EmailService.send_notification_email(notification)
            
            if preferences.get('push_notifications', True):
                PushNotificationService.send_push(notification)
        
        return created_notifications
    
    @staticmethod
    def notify_course_enrollment(user, course, tenant):
        """Send course enrollment notification with i18n support"""
        return NotificationService.create_notification(
            user=user,
            title="Course Enrollment",  # Will be localized
            message="Course enrollment notification",  # Will be localized
            notification_type='course_enrollment',
            tenant=tenant,
            related_object_id=course.id,
            related_object_type='course',
            send_email=True,
            context={'course_title': course.title}
        )
    
    @staticmethod
    def notify_class_reminder(user, live_class, tenant, minutes_before=30):
        """Send class reminder notification with i18n support"""
        return NotificationService.create_notification(
            user=user,
            title="Class Reminder",  # Will be localized
            message="Class reminder notification",  # Will be localized
            notification_type='class_reminder',
            tenant=tenant,
            related_object_id=live_class.id,
            related_object_type='live_class',
            send_email=True,
            send_push=True,
            context={
                'class_title': live_class.title,
                'minutes': minutes_before
            }
        )
    
    @staticmethod
    def notify_teacher_approval(user, status, tenant, additional_info=""):
        """Send teacher approval notification with i18n support"""
        return NotificationService.create_notification(
            user=user,
            title="Teacher Application",  # Will be localized
            message="Teacher application notification",  # Will be localized
            notification_type='teacher_approval',
            tenant=tenant,
            send_email=True,
            context={
                'status': status,
                'additional_info': additional_info
            }
        )


class EmailService:
    """Enhanced email notification service for centralized API with delivery tracking"""
    
    @staticmethod
    def send_notification_email(notification):
        """Send notification via email with template support, i18n, and delivery tracking"""
        try:
            # Get user's preferred language
            user_language = NotificationI18nService.get_user_language(notification.user)
            
            # Get localized subject prefix
            subject_prefix = NotificationI18nService.get_email_subject_prefix(
                user_language, 
                notification.tenant.name if notification.tenant else None
            )
            subject = f"{subject_prefix} {notification.title}"
            
            # Get language-specific template
            template_name = NotificationTemplateI18nService.get_email_template_path(
                notification.notification_type, user_language
            )
            fallback_template = 'emails/notification.html'
            
            # Get template context with i18n support
            context = NotificationTemplateI18nService.get_template_context(
                notification, user_language
            )
            
            try:
                html_message = render_to_string(template_name, context)
                template_used = template_name
            except Exception as template_error:
                print(f"Template {template_name} not found, using fallback: {str(template_error)}")
                # Fall back to generic template
                html_message = render_to_string(fallback_template, context)
                template_used = fallback_template
            
            # Send email with delivery tracking
            send_mail(
                subject=subject,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            # Log successful email delivery with template info
            EmailService.log_email_delivery(notification, 'sent', subject, template_used)
            return True
            
        except Exception as e:
            # Log failed email delivery
            EmailService.log_email_delivery(notification, 'failed', str(e))
            print(f"Failed to send email notification: {str(e)}")
            return False
    
    @staticmethod
    def log_email_delivery(notification, status, details, template_used=None):
        """Log email delivery status for monitoring"""
        try:
            from .models import EmailDeliveryLog
            EmailDeliveryLog.objects.create(
                notification=notification,
                recipient_email=notification.user.email,
                status=status,
                details=details,
                subject=details if status == 'sent' else '',
                template_used=template_used or '',
                tenant=notification.tenant
            )
        except Exception as e:
            print(f"Failed to log email delivery: {str(e)}")
    
    @staticmethod
    def get_available_templates():
        """Get list of available email templates"""
        import os
        from django.conf import settings
        
        template_dir = os.path.join(settings.BASE_DIR, 'templates', 'emails', 'notifications')
        templates = []
        
        if os.path.exists(template_dir):
            for filename in os.listdir(template_dir):
                if filename.endswith('.html'):
                    template_name = filename.replace('.html', '')
                    templates.append(template_name)
        
        return templates
    
    @staticmethod
    def validate_template(template_name):
        """Validate if email template exists"""
        try:
            template_path = f'emails/notifications/{template_name}.html'
            render_to_string(template_path, {})
            return True
        except:
            return False
    
    @staticmethod
    def send_bulk_emails(notifications):
        """Send multiple email notifications efficiently"""
        from django.core.mail import EmailMultiAlternatives
        from django.core.mail import get_connection
        
        try:
            connection = get_connection()
            messages = []
            
            for notification in notifications:
                subject = f"[{notification.tenant.name if notification.tenant else 'Edurise'}] {notification.title}"
                
                context = {
                    'notification': notification,
                    'user': notification.user,
                    'tenant': notification.tenant,
                    'site_url': settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:3000'
                }
                
                try:
                    template_name = f'emails/notifications/{notification.notification_type}.html'
                    html_message = render_to_string(template_name, context)
                except:
                    html_message = render_to_string('emails/notification.html', context)
                
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=notification.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[notification.user.email],
                    connection=connection
                )
                msg.attach_alternative(html_message, "text/html")
                messages.append(msg)
            
            connection.send_messages(messages)
            return True
            
        except Exception as e:
            print(f"Failed to send bulk email notifications: {str(e)}")
            return False


class EmailAutomationService:
    """Service for automated email notifications based on events"""
    
    @staticmethod
    def setup_automated_notifications():
        """Set up automated email notifications for key events"""
        # This would typically be called during app initialization
        # or through a management command
        
        automation_rules = [
            {
                'event': 'user_registered',
                'delay_minutes': 0,
                'template': 'welcome_email',
                'enabled': True
            },
            {
                'event': 'course_enrolled',
                'delay_minutes': 5,
                'template': 'course_enrollment',
                'enabled': True
            },
            {
                'event': 'assignment_due_soon',
                'delay_minutes': 0,
                'template': 'assignment_due',
                'enabled': True,
                'trigger_hours_before': 24
            },
            {
                'event': 'class_reminder',
                'delay_minutes': 0,
                'template': 'class_reminder',
                'enabled': True,
                'trigger_minutes_before': 30
            },
            {
                'event': 'payment_failed',
                'delay_minutes': 15,
                'template': 'payment_failed',
                'enabled': True,
                'retry_attempts': 3
            },
            {
                'event': 'subscription_expiring',
                'delay_minutes': 0,
                'template': 'subscription_renewal_reminder',
                'enabled': True,
                'trigger_days_before': 7
            }
        ]
        
        return automation_rules
    
    @staticmethod
    def trigger_event_notification(event_type, user, context_data=None):
        """Trigger automated notification based on event"""
        try:
            automation_rules = EmailAutomationService.setup_automated_notifications()
            
            # Find matching rule
            rule = next((r for r in automation_rules if r['event'] == event_type and r['enabled']), None)
            
            if not rule:
                return False
            
            # Create notification based on event type
            notification_data = EmailAutomationService.get_notification_data(event_type, user, context_data)
            
            if notification_data:
                # Create notification
                from .models import Notification
                notification = Notification.objects.create(
                    user=user,
                    title=notification_data['title'],
                    message=notification_data['message'],
                    notification_type=notification_data['type'],
                    tenant=context_data.get('tenant') if context_data else None
                )
                
                # Send email immediately or schedule for later
                if rule['delay_minutes'] == 0:
                    EmailService.send_notification_email(notification)
                else:
                    # Schedule for later (would use Celery in production)
                    EmailAutomationService.schedule_email(notification, rule['delay_minutes'])
                
                return True
                
        except Exception as e:
            print(f"Failed to trigger event notification: {str(e)}")
            return False
    
    @staticmethod
    def get_notification_data(event_type, user, context_data):
        """Get notification data based on event type"""
        notification_map = {
            'user_registered': {
                'title': 'Welcome to EduRise!',
                'message': f'Welcome {user.first_name or user.email}! Your account has been created successfully.',
                'type': 'system'
            },
            'course_enrolled': {
                'title': f'Enrolled in {context_data.get("course_title", "Course")}',
                'message': f'You have successfully enrolled in {context_data.get("course_title", "the course")}. Start learning now!',
                'type': 'course_enrollment'
            },
            'assignment_due_soon': {
                'title': f'Assignment Due: {context_data.get("assignment_title", "Assignment")}',
                'message': f'Your assignment "{context_data.get("assignment_title", "Assignment")}" is due in 24 hours.',
                'type': 'assignment_due'
            },
            'class_reminder': {
                'title': f'Class Starting Soon: {context_data.get("class_title", "Class")}',
                'message': f'Your class "{context_data.get("class_title", "Class")}" starts in 30 minutes.',
                'type': 'class_reminder'
            },
            'payment_failed': {
                'title': 'Payment Failed',
                'message': f'We were unable to process your payment for {context_data.get("item_name", "your purchase")}. Please update your payment method.',
                'type': 'payment_failed'
            },
            'subscription_expiring': {
                'title': 'Subscription Expiring Soon',
                'message': 'Your subscription will expire in 7 days. Renew now to continue accessing all features.',
                'type': 'system'
            }
        }
        
        return notification_map.get(event_type)
    
    @staticmethod
    def get_email_analytics():
        """Get email automation analytics"""
        try:
            from .models import EmailDeliveryLog, Notification
            from django.db.models import Count, Q
            from datetime import datetime, timedelta
            
            # Get stats for the last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            analytics = {
                'total_emails_sent': EmailDeliveryLog.objects.filter(
                    sent_at__gte=thirty_days_ago
                ).count(),
                'successful_deliveries': EmailDeliveryLog.objects.filter(
                    sent_at__gte=thirty_days_ago,
                    status__in=['sent', 'delivered']
                ).count(),
                'failed_deliveries': EmailDeliveryLog.objects.filter(
                    sent_at__gte=thirty_days_ago,
                    status='failed'
                ).count(),
                'emails_by_type': dict(
                    Notification.objects.filter(
                        created_at__gte=thirty_days_ago,
                        sent_email=True
                    ).values('notification_type').annotate(
                        count=Count('id')
                    ).values_list('notification_type', 'count')
                )
            }
            
            # Calculate delivery rate
            if analytics['total_emails_sent'] > 0:
                analytics['delivery_rate'] = round(
                    (analytics['successful_deliveries'] / analytics['total_emails_sent']) * 100, 2
                )
            else:
                analytics['delivery_rate'] = 0
            
            return analytics
            
        except Exception as e:
            print(f"Failed to get email analytics: {str(e)}")
            return {}


class PushNotificationService:
    """Push notification service"""
    
    @staticmethod
    def send_push(notification):
        """Send push notification"""
        # Implementation would integrate with push notification service
        # like Firebase Cloud Messaging, OneSignal, etc.
        pass


class NotificationDeliveryTracker:
    """Service for tracking notification delivery across all channels"""
    
    @staticmethod
    def track_delivery_attempt(notification, channel, status, details=None):
        """Track notification delivery attempt"""
        try:
            from .models import EmailDeliveryLog
            from django.utils import timezone
            
            # For now, we'll use EmailDeliveryLog for all delivery tracking
            # In a more complex system, we'd have separate models for each channel
            if channel == 'email':
                EmailDeliveryLog.objects.create(
                    notification=notification,
                    recipient_email=notification.user.email,
                    status=status,
                    details=details or '',
                    tenant=notification.tenant
                )
            elif channel == 'websocket':
                # Track WebSocket delivery success/failure
                # Could be extended to have a separate WebSocketDeliveryLog model
                pass
            elif channel == 'push':
                # Track push notification delivery
                # Could be extended to have a PushDeliveryLog model
                pass
                
        except Exception as e:
            print(f"Failed to track delivery for {channel}: {str(e)}")
    
    @staticmethod
    def get_delivery_stats(notification):
        """Get delivery statistics for a notification"""
        try:
            from .models import EmailDeliveryLog
            
            stats = {
                'email_sent': False,
                'websocket_sent': False,
                'push_sent': False,
                'total_attempts': 0,
                'successful_deliveries': 0
            }
            
            # Check email delivery
            email_logs = EmailDeliveryLog.objects.filter(notification=notification)
            if email_logs.exists():
                stats['email_sent'] = email_logs.filter(status='sent').exists()
                stats['total_attempts'] += email_logs.count()
                stats['successful_deliveries'] += email_logs.filter(status__in=['sent', 'delivered']).count()
            
            # Check notification flags
            if notification.sent_email:
                stats['email_sent'] = True
            if notification.sent_push:
                stats['push_sent'] = True
            
            # WebSocket is considered sent if notification was created successfully
            stats['websocket_sent'] = True
            
            return stats
            
        except Exception as e:
            print(f"Failed to get delivery stats: {str(e)}")
            return {}
    
    @staticmethod
    def retry_failed_deliveries():
        """Retry failed notification deliveries"""
        try:
            from .models import Notification, EmailDeliveryLog
            from django.utils import timezone
            from datetime import timedelta
            
            # Find notifications with failed email deliveries in the last hour
            one_hour_ago = timezone.now() - timedelta(hours=1)
            
            failed_emails = EmailDeliveryLog.objects.filter(
                status='failed',
                sent_at__gte=one_hour_ago
            ).select_related('notification')
            
            retry_count = 0
            for log in failed_emails:
                # Only retry up to 3 times
                retry_attempts = EmailDeliveryLog.objects.filter(
                    notification=log.notification,
                    status='failed'
                ).count()
                
                if retry_attempts < 3:
                    success = EmailService.send_notification_email(log.notification)
                    if success:
                        retry_count += 1
            
            return retry_count
            
        except Exception as e:
            print(f"Failed to retry deliveries: {str(e)}")
            return 0


class WebSocketNotificationService:
    """Enhanced real-time WebSocket notifications for centralized API"""
    
    @staticmethod
    def send_realtime_notification(user, notification_data):
        """Send real-time notification via WebSocket"""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                group_name = f"notifications_{user.id}"
                
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'notification_message',
                        'notification': notification_data
                    }
                )
                return True
        except Exception as e:
            print(f"Failed to send WebSocket notification: {str(e)}")
            return False
    
    @staticmethod
    def send_bulk_realtime_notifications(user_notification_pairs):
        """Send multiple real-time notifications efficiently"""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        try:
            channel_layer = get_channel_layer()
            if not channel_layer:
                return False
            
            for user, notification_data in user_notification_pairs:
                group_name = f"notifications_{user.id}"
                
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'notification_message',
                        'notification': notification_data
                    }
                )
            
            return True
            
        except Exception as e:
            print(f"Failed to send bulk WebSocket notifications: {str(e)}")
            return False
    
    @staticmethod
    def send_system_broadcast(notification_data, tenant=None):
        """Send system-wide notification broadcast"""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        from django.contrib.auth import get_user_model
        
        try:
            channel_layer = get_channel_layer()
            if not channel_layer:
                return False
            
            User = get_user_model()
            users = User.objects.all()
            
            if tenant:
                users = users.filter(userprofile__tenant=tenant)
            
            for user in users:
                group_name = f"notifications_{user.id}"
                
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'notification_message',
                        'notification': notification_data
                    }
                )
            
            return True
            
        except Exception as e:
            print(f"Failed to send system broadcast: {str(e)}")
            return False