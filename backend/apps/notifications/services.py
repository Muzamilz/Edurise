from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from .models import Notification


class NotificationService:
    """Enhanced service for sending notifications through centralized API"""
    
    @staticmethod
    def create_notification(user, title, message, notification_type, tenant, 
                          related_object_id=None, related_object_type=None,
                          send_email=None, send_push=None):
        """Create and optionally send notification with user preferences"""
        
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
            related_object_type=related_object_type
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
        if hasattr(user, 'userprofile') and user.userprofile.notification_preferences:
            return user.userprofile.notification_preferences
        
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
        """Send course enrollment notification"""
        return NotificationService.create_notification(
            user=user,
            title=f"Enrolled in {course.title}",
            message=f"You have successfully enrolled in {course.title}. Start learning now!",
            notification_type='course_enrollment',
            tenant=tenant,
            related_object_id=course.id,
            related_object_type='course',
            send_email=True
        )
    
    @staticmethod
    def notify_class_reminder(user, live_class, tenant):
        """Send class reminder notification"""
        return NotificationService.create_notification(
            user=user,
            title=f"Class Reminder: {live_class.title}",
            message=f"Your class '{live_class.title}' starts in 30 minutes.",
            notification_type='class_reminder',
            tenant=tenant,
            related_object_id=live_class.id,
            related_object_type='live_class',
            send_email=True,
            send_push=True
        )
    
    @staticmethod
    def notify_teacher_approval(user, status, tenant):
        """Send teacher approval notification"""
        title = "Teacher Application Approved" if status == 'approved' else "Teacher Application Update"
        message = ("Congratulations! Your teacher application has been approved." 
                  if status == 'approved' 
                  else "Your teacher application status has been updated.")
        
        return NotificationService.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type='teacher_approval',
            tenant=tenant,
            send_email=True
        )


class EmailService:
    """Enhanced email notification service for centralized API with delivery tracking"""
    
    @staticmethod
    def send_notification_email(notification):
        """Send notification via email with template support and delivery tracking"""
        try:
            subject = f"[{notification.tenant.name if notification.tenant else 'Edurise'}] {notification.title}"
            
            # Try to render specific template for notification type
            template_name = f'emails/notifications/{notification.notification_type}.html'
            fallback_template = 'emails/notification.html'
            
            context = {
                'notification': notification,
                'user': notification.user,
                'tenant': notification.tenant,
                'site_url': settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:3000'
            }
            
            try:
                html_message = render_to_string(template_name, context)
            except Exception as template_error:
                print(f"Template {template_name} not found, using fallback: {str(template_error)}")
                # Fall back to generic template
                html_message = render_to_string(fallback_template, context)
            
            # Send email with delivery tracking
            send_mail(
                subject=subject,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            # Log successful email delivery
            EmailService.log_email_delivery(notification, 'sent', subject)
            return True
            
        except Exception as e:
            # Log failed email delivery
            EmailService.log_email_delivery(notification, 'failed', str(e))
            print(f"Failed to send email notification: {str(e)}")
            return False
    
    @staticmethod
    def log_email_delivery(notification, status, details):
        """Log email delivery status for monitoring"""
        try:
            from .models import EmailDeliveryLog
            EmailDeliveryLog.objects.create(
                notification=notification,
                recipient_email=notification.user.email,
                status=status,
                details=details,
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


class PushNotificationService:
    """Push notification service"""
    
    @staticmethod
    def send_push(notification):
        """Send push notification"""
        # Implementation would integrate with push notification service
        # like Firebase Cloud Messaging, OneSignal, etc.
        pass


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