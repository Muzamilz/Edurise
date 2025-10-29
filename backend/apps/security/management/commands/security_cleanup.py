"""
Django management command for security data cleanup.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.security.models import SecurityEvent, SecurityAlert, AuditLog


class Command(BaseCommand):
    help = 'Clean up old security data (events, alerts, audit logs)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete data older than this many days (default: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['events', 'alerts', 'audit', 'all'],
            default='all',
            help='Type of data to clean up (default: all)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cleanup_type = options['type']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f"Cleaning up security data older than {days} days ({cutoff_date})")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No data will be deleted"))
        
        total_deleted = 0
        
        # Clean up security events
        if cleanup_type in ['events', 'all']:
            events_count = SecurityEvent.objects.filter(
                created_at__lt=cutoff_date,
                is_resolved=True  # Only delete resolved events
            ).count()
            
            if dry_run:
                self.stdout.write(f"Would delete {events_count} resolved security events")
            else:
                deleted_events = SecurityEvent.objects.filter(
                    created_at__lt=cutoff_date,
                    is_resolved=True
                ).delete()[0]
                self.stdout.write(f"Deleted {deleted_events} resolved security events")
                total_deleted += deleted_events
        
        # Clean up resolved security alerts
        if cleanup_type in ['alerts', 'all']:
            alerts_count = SecurityAlert.objects.filter(
                created_at__lt=cutoff_date,
                status__in=['resolved', 'false_positive']
            ).count()
            
            if dry_run:
                self.stdout.write(f"Would delete {alerts_count} resolved security alerts")
            else:
                deleted_alerts = SecurityAlert.objects.filter(
                    created_at__lt=cutoff_date,
                    status__in=['resolved', 'false_positive']
                ).delete()[0]
                self.stdout.write(f"Deleted {deleted_alerts} resolved security alerts")
                total_deleted += deleted_alerts
        
        # Clean up old audit logs
        if cleanup_type in ['audit', 'all']:
            audit_count = AuditLog.objects.filter(
                created_at__lt=cutoff_date
            ).count()
            
            if dry_run:
                self.stdout.write(f"Would delete {audit_count} audit log entries")
            else:
                deleted_audit = AuditLog.objects.filter(
                    created_at__lt=cutoff_date
                ).delete()[0]
                self.stdout.write(f"Deleted {deleted_audit} audit log entries")
                total_deleted += deleted_audit
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"Cleanup completed. Total items deleted: {total_deleted}")
            )
        else:
            self.stdout.write("Dry run completed. Use without --dry-run to actually delete data.")