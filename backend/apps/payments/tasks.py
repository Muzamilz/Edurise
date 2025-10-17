from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment, Invoice, Subscription
from .services import InvoiceService, SubscriptionService


@shared_task
def process_overdue_invoices():
    """Mark overdue invoices and send reminders"""
    from datetime import date
    
    # Get invoices that are past due
    overdue_invoices = Invoice.objects.filter(
        status='sent',
        due_date__lt=date.today()
    )
    
    for invoice in overdue_invoices:
        invoice.mark_overdue()
        
        # Send overdue reminder email
        send_overdue_reminder.delay(invoice.id)
    
    return f"Processed {overdue_invoices.count()} overdue invoices"


@shared_task
def send_overdue_reminder(invoice_id):
    """Send overdue invoice reminder email"""
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        
        subject = f"Overdue Invoice Reminder - {invoice.invoice_number}"
        message = f"""
        Dear {invoice.billing_name},
        
        This is a reminder that your invoice {invoice.invoice_number} 
        for ${invoice.total_amount} is now overdue.
        
        Original due date: {invoice.due_date}
        
        Please make payment as soon as possible to avoid any service interruption.
        
        You can view and pay your invoice at: {settings.FRONTEND_URL}/invoice/{invoice.id}
        
        If you have any questions, please contact us at support@edurise.com
        
        Thank you,
        Edurise Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invoice.billing_email],
            fail_silently=False
        )
        
        return f"Overdue reminder sent for invoice {invoice.invoice_number}"
        
    except Invoice.DoesNotExist:
        return f"Invoice {invoice_id} not found"


@shared_task
def process_subscription_renewals():
    """Process subscription renewals for subscriptions ending soon"""
    from datetime import date, timedelta
    
    # Get subscriptions ending in the next 3 days
    upcoming_renewals = Subscription.objects.filter(
        status='active',
        current_period_end__lte=timezone.now() + timedelta(days=3),
        current_period_end__gt=timezone.now()
    )
    
    renewed_count = 0
    
    for subscription in upcoming_renewals:
        try:
            # Attempt to renew subscription
            SubscriptionService.renew_subscription(subscription)
            renewed_count += 1
            
        except Exception as e:
            # Log error and send notification to admin
            send_renewal_failure_notification.delay(subscription.id, str(e))
    
    return f"Processed {renewed_count} subscription renewals"


@shared_task
def send_renewal_failure_notification(subscription_id, error_message):
    """Send notification when subscription renewal fails"""
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        
        subject = f"Subscription Renewal Failed - {subscription.organization.name}"
        message = f"""
        Subscription renewal failed for organization: {subscription.organization.name}
        Subscription ID: {subscription.id}
        Plan: {subscription.plan}
        Error: {error_message}
        
        Please investigate and take appropriate action.
        """
        
        # Send to admin email
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@edurise.com')
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False
        )
        
        return f"Renewal failure notification sent for subscription {subscription_id}"
        
    except Subscription.DoesNotExist:
        return f"Subscription {subscription_id} not found"


@shared_task
def generate_monthly_invoices():
    """Generate monthly invoices for active subscriptions"""
    from datetime import date
    
    # Get subscriptions that need monthly invoicing
    monthly_subscriptions = Subscription.objects.filter(
        status='active',
        billing_cycle='monthly',
        current_period_start__date=date.today()
    )
    
    generated_count = 0
    
    for subscription in monthly_subscriptions:
        try:
            # Create payment for this billing period
            payment_result = SubscriptionService.process_subscription_payment(subscription)
            
            # The payment service will automatically create and send invoice
            generated_count += 1
            
        except Exception as e:
            # Log error
            print(f"Failed to generate invoice for subscription {subscription.id}: {e}")
    
    return f"Generated {generated_count} monthly invoices"


@shared_task
def cleanup_failed_payments():
    """Clean up old failed payments"""
    from datetime import timedelta
    
    # Delete failed payments older than 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    
    old_failed_payments = Payment.objects.filter(
        status='failed',
        failed_at__lt=cutoff_date
    )
    
    count = old_failed_payments.count()
    old_failed_payments.delete()
    
    return f"Cleaned up {count} old failed payments"


@shared_task
def send_payment_confirmation(payment_id):
    """Send payment confirmation email"""
    try:
        payment = Payment.objects.get(id=payment_id)
        
        if payment.course:
            subject = f"Payment Confirmation - {payment.course.title}"
            message = f"""
            Dear {payment.user.get_full_name() or payment.user.email},
            
            Your payment of ${payment.amount} for the course "{payment.course.title}" 
            has been successfully processed.
            
            Payment ID: {payment.id}
            Payment Method: {payment.get_payment_method_display()}
            Date: {payment.completed_at.strftime('%B %d, %Y at %I:%M %p')}
            
            You can now access your course at: {settings.FRONTEND_URL}/courses/{payment.course.id}
            
            Thank you for choosing Edurise!
            
            Best regards,
            Edurise Team
            """
        else:
            subject = "Payment Confirmation"
            message = f"""
            Dear {payment.user.get_full_name() or payment.user.email},
            
            Your payment of ${payment.amount} has been successfully processed.
            
            Payment ID: {payment.id}
            Payment Method: {payment.get_payment_method_display()}
            Date: {payment.completed_at.strftime('%B %d, %Y at %I:%M %p')}
            
            Thank you for choosing Edurise!
            
            Best regards,
            Edurise Team
            """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[payment.user.email],
            fail_silently=False
        )
        
        return f"Payment confirmation sent for payment {payment_id}"
        
    except Payment.DoesNotExist:
        return f"Payment {payment_id} not found"