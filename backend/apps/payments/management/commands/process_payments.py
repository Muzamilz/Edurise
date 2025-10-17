from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.payments.models import Payment, Invoice, Subscription
from apps.payments.services import InvoiceService, SubscriptionService


class Command(BaseCommand):
    help = 'Process payment-related tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overdue-invoices',
            action='store_true',
            help='Process overdue invoices',
        )
        parser.add_argument(
            '--subscription-renewals',
            action='store_true',
            help='Process subscription renewals',
        )
        parser.add_argument(
            '--cleanup-failed',
            action='store_true',
            help='Clean up old failed payments',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all payment processing tasks',
        )

    def handle(self, *args, **options):
        if options['overdue_invoices'] or options['all']:
            self.process_overdue_invoices()
        
        if options['subscription_renewals'] or options['all']:
            self.process_subscription_renewals()
        
        if options['cleanup_failed'] or options['all']:
            self.cleanup_failed_payments()

    def process_overdue_invoices(self):
        """Mark overdue invoices and send reminders"""
        self.stdout.write("Processing overdue invoices...")
        
        overdue_invoices = Invoice.objects.filter(
            status='sent',
            due_date__lt=timezone.now().date()
        )
        
        count = 0
        for invoice in overdue_invoices:
            invoice.mark_overdue()
            count += 1
            
            # Send reminder email
            try:
                from apps.payments.tasks import send_overdue_reminder
                send_overdue_reminder.delay(invoice.id)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Failed to send reminder for {invoice.invoice_number}: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"Processed {count} overdue invoices")
        )

    def process_subscription_renewals(self):
        """Process subscription renewals"""
        self.stdout.write("Processing subscription renewals...")
        
        # Get subscriptions ending in the next 3 days
        upcoming_renewals = Subscription.objects.filter(
            status='active',
            current_period_end__lte=timezone.now() + timedelta(days=3),
            current_period_end__gt=timezone.now()
        )
        
        renewed_count = 0
        failed_count = 0
        
        for subscription in upcoming_renewals:
            try:
                SubscriptionService.renew_subscription(subscription)
                renewed_count += 1
                self.stdout.write(f"Renewed subscription for {subscription.organization.name}")
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Failed to renew subscription for {subscription.organization.name}: {e}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"Renewed {renewed_count} subscriptions, {failed_count} failed")
        )

    def cleanup_failed_payments(self):
        """Clean up old failed payments"""
        self.stdout.write("Cleaning up old failed payments...")
        
        # Delete failed payments older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        
        old_failed_payments = Payment.objects.filter(
            status='failed',
            failed_at__lt=cutoff_date
        )
        
        count = old_failed_payments.count()
        old_failed_payments.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f"Cleaned up {count} old failed payments")
        )