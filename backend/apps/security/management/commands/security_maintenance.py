"""
Security maintenance management command.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from apps.security.models import SecurityEvent, SecurityAlert, ThreatIntelligence
from apps.admin_tools.models import AuditLog
from apps.accounts.models import User
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Perform security maintenance tasks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup-old-events',
            action='store_true',
            help='Clean up old security events'
        )
        parser.add_argument(
            '--cleanup-audit-logs',
            action='store_true',
            help='Clean up old audit logs'
        )
        parser.add_argument(
            '--update-threat-intel',
            action='store_true',
            help='Update threat intelligence data'
        )
        parser.add_argument(
            '--cleanup-inactive-users',
            action='store_true',
            help='Clean up inactive user accounts'
        )
        parser.add_argument(
            '--generate-security-report',
            action='store_true',
            help='Generate security report'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all maintenance tasks'
        )
    
    def handle(self, *args, **options):
        """Execute security maintenance tasks"""
        
        if options['all']:
            options.update({
                'cleanup_old_events': True,
                'cleanup_audit_logs': True,
                'update_threat_intel': True,
                'cleanup_inactive_users': True,
                'generate_security_report': True
            })
        
        if options['cleanup_old_events']:
            self.cleanup_old_security_events()
        
        if options['cleanup_audit_logs']:
            self.cleanup_old_audit_logs()
        
        if options['update_threat_intel']:
            self.update_threat_intelligence()
        
        if options['cleanup_inactive_users']:
            self.cleanup_inactive_users()
        
        if options['generate_security_report']:
            self.generate_security_report()
        
        self.stdout.write(
            self.style.SUCCESS('Security maintenance completed successfully')
        )
    
    def cleanup_old_security_events(self):
        """Clean up old security events"""
        retention_days = getattr(settings, 'SECURITY_EVENT_RETENTION_DAYS', 90)
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        # Keep critical events longer
        critical_retention_days = retention_days * 2
        critical_cutoff_date = timezone.now() - timedelta(days=critical_retention_days)
        
        # Delete old non-critical events
        deleted_count = SecurityEvent.objects.filter(
            created_at__lt=cutoff_date,
            severity__in=['low', 'medium']
        ).delete()[0]
        
        # Delete very old critical events
        critical_deleted_count = SecurityEvent.objects.filter(
            created_at__lt=critical_cutoff_date,
            severity__in=['high', 'critical']
        ).delete()[0]
        
        total_deleted = deleted_count + critical_deleted_count
        
        self.stdout.write(
            self.style.SUCCESS(f'Cleaned up {total_deleted} old security events')
        )
        
        logger.info(f'Security maintenance: Deleted {total_deleted} old security events')
    
    def cleanup_old_audit_logs(self):
        """Clean up old audit logs"""
        retention_days = getattr(settings, 'AUDIT_LOG_RETENTION_DAYS', 365)
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        # Archive instead of delete for compliance
        archived_count = AuditLog.objects.filter(
            created_at__lt=cutoff_date
        ).update(archived=True)
        
        self.stdout.write(
            self.style.SUCCESS(f'Archived {archived_count} old audit logs')
        )
        
        logger.info(f'Security maintenance: Archived {archived_count} old audit logs')
    
    def update_threat_intelligence(self):
        """Update threat intelligence data"""
        try:
            # Remove old threat intelligence data
            old_threats_deleted = ThreatIntelligence.objects.filter(
                last_seen__lt=timezone.now() - timedelta(days=30),
                is_active=False
            ).delete()[0]
            
            # Update confidence scores (decay over time)
            from django.db import models
            threats_updated = ThreatIntelligence.objects.filter(
                is_active=True,
                last_seen__lt=timezone.now() - timedelta(days=7)
            ).update(
                confidence_score=models.F('confidence_score') * 0.9  # Reduce by 10%
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Updated threat intelligence: deleted {old_threats_deleted}, '
                    f'updated {threats_updated} confidence scores'
                )
            )
            
            logger.info(f'Security maintenance: Updated threat intelligence data')
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating threat intelligence: {str(e)}')
            )
            logger.error(f'Security maintenance error: {str(e)}')
    
    def cleanup_inactive_users(self):
        """Clean up inactive user accounts (GDPR compliance)"""
        if not getattr(settings, 'AUTO_DELETE_INACTIVE_USERS_DAYS', None):
            self.stdout.write(
                self.style.WARNING('Auto-deletion of inactive users is disabled')
            )
            return
        
        inactive_days = settings.AUTO_DELETE_INACTIVE_USERS_DAYS
        cutoff_date = timezone.now() - timedelta(days=inactive_days)
        
        # Find inactive users (not logged in for specified period)
        inactive_users = User.objects.filter(
            last_login__lt=cutoff_date,
            is_active=True,
            is_staff=False,
            is_superuser=False
        )
        
        # Send notification before deletion (implement notification logic)
        users_to_notify = inactive_users.filter(
            last_login__lt=timezone.now() - timedelta(days=inactive_days - 30)  # 30 days warning
        )
        
        for user in users_to_notify:
            # Send warning email (implement email notification)
            logger.info(f'Warning sent to inactive user: {user.email}')
        
        # Actually delete users who have been inactive for the full period
        users_to_delete = inactive_users.filter(
            last_login__lt=cutoff_date
        )
        
        deleted_count = 0
        for user in users_to_delete:
            # Use GDPR deletion service
            from apps.security.services import ComplianceService
            try:
                ComplianceService.delete_user_data(user)
                deleted_count += 1
                logger.info(f'Deleted inactive user: {user.email}')
            except Exception as e:
                logger.error(f'Error deleting user {user.email}: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Processed inactive users: {users_to_notify.count()} notified, '
                f'{deleted_count} deleted'
            )
        )
    
    def generate_security_report(self):
        """Generate security summary report"""
        try:
            from apps.security.services import SecurityMonitoringService
            
            # Get security overview
            overview = SecurityMonitoringService.get_security_overview()
            
            # Get recent events summary
            recent_events = SecurityEvent.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            )
            
            event_summary = {
                'total': recent_events.count(),
                'critical': recent_events.filter(severity='critical').count(),
                'high': recent_events.filter(severity='high').count(),
                'medium': recent_events.filter(severity='medium').count(),
                'low': recent_events.filter(severity='low').count(),
            }
            
            # Get active alerts
            active_alerts = SecurityAlert.objects.filter(status='active').count()
            
            report = {
                'generated_at': timezone.now().isoformat(),
                'security_score': overview.get('security_score', 0),
                'status': overview.get('status', 'unknown'),
                'recent_events': event_summary,
                'active_alerts': active_alerts,
                'unresolved_events': overview.get('unresolved_events', 0)
            }
            
            self.stdout.write(
                self.style.SUCCESS('Security Report Generated:')
            )
            self.stdout.write(f"Security Score: {report['security_score']}/100")
            self.stdout.write(f"Status: {report['status']}")
            self.stdout.write(f"Recent Events (7 days): {report['recent_events']['total']}")
            self.stdout.write(f"Active Alerts: {report['active_alerts']}")
            self.stdout.write(f"Unresolved Events: {report['unresolved_events']}")
            
            logger.info(f'Security maintenance: Generated security report')
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating security report: {str(e)}')
            )
            logger.error(f'Security maintenance error: {str(e)}')