from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Notification


class NotificationService:
    """Service for sending notifications"""
    
    @staticmethod
    def create_notification(user, title, message, notification_type, tenant, 
                          related_object_id=None, related_object_type=None,
                          send_email=True, send_push=False):
        """Create and optionally send notification"""
        
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            tenant=tenant,
            related_object_id=related_object_id,
            related_object_type=related_object_type
        )
        
        # Send email if requested
        if send_email:
            EmailService.send_notification_email(notification)
            notification.sent_email = True
            notification.save()
        
        # Send push notification if requested
        if send_push:
            PushNotificationService.send_push(notification)
            notification.sent_push = True
            notification.save()
        
        return notification
    
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
    """Email notification service"""
    
    @staticmethod
    def send_notification_email(notification):
        """Send notification via email"""
        try:
            subject = notification.title
            
            # Render email template
            html_message = render_to_string('emails/notification.html', {
                'notification': notification,
                'user': notification.user
            })
            
            send_mail(
                subject=subject,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                html_message=html_message,
                fail_silently=False
            )
            
        except Exception as e:
            # Log error but don't fail the notification creation
            print(f"Failed to send email notification: {str(e)}")


class PushNotificationService:
    """Push notification service"""
    
    @staticmethod
    def send_push(notification):
        """Send push notification"""
        # Implementation would integrate with push notification service
        # like Firebase Cloud Messaging, OneSignal, etc.
        pass


class WebSocketNotificationService:
    """Real-time WebSocket notifications"""
    
    @staticmethod
    def send_realtime_notification(user, notification_data):
        """Send real-time notification via WebSocket"""
        # Implementation would use Django Channels
        # to send real-time notifications to connected users
        pass