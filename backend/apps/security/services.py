"""
Security services for monitoring, alerting, and threat detection.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.core.mail import send_mail
from django.conf import settings

from .models import SecurityEvent, SecurityAlert, SecurityPolicy, ThreatIntelligence
from apps.admin_tools.models import AuditLog

User = get_user_model()
logger = logging.getLogger(__name__)


class SecurityMonitoringService:
    """Service for security monitoring and event detection"""
    
    @staticmethod
    def get_security_overview(tenant=None):
        """Get security overview metrics"""
        
        try:
            # Get recent security events (last 30 days)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            
            events_qs = SecurityEvent.objects.filter(created_at__gte=thirty_days_ago)
            alerts_qs = SecurityAlert.objects.filter(created_at__gte=thirty_days_ago)
            
            if tenant:
                events_qs = events_qs.filter(tenant=tenant)
                alerts_qs = alerts_qs.filter(tenant=tenant)
            
            # Count events by severity
            event_counts = events_qs.values('severity').annotate(count=Count('id'))
            severity_counts = {item['severity']: item['count'] for item in event_counts}
            
            # Count unresolved events
            unresolved_events = events_qs.filter(is_resolved=False).count()
            
            # Count active alerts
            active_alerts = alerts_qs.filter(status='active').count()
            
            # Calculate security score (simplified algorithm)
            total_events = events_qs.count()
            critical_events = severity_counts.get('critical', 0)
            high_events = severity_counts.get('high', 0)
            
            # Base score of 100, deduct points for events
            security_score = 100
            security_score -= (critical_events * 10)  # -10 per critical event
            security_score -= (high_events * 5)       # -5 per high event
            security_score -= (unresolved_events * 2) # -2 per unresolved event
            security_score = max(0, min(100, security_score))  # Keep between 0-100
            
            # Determine overall status
            if security_score >= 90:
                status = 'excellent'
            elif security_score >= 75:
                status = 'good'
            elif security_score >= 50:
                status = 'warning'
            else:
                status = 'critical'
            
            return {
                'status': status,
                'security_score': security_score,
                'total_events': total_events,
                'unresolved_events': unresolved_events,
                'active_alerts': active_alerts,
                'severity_breakdown': severity_counts,
                'last_updated': timezone.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting security overview: {str(e)}")
            return {
                'status': 'error',
                'security_score': 0,
                'error': str(e),
                'last_updated': timezone.now().isoformat()
            }
    
    @staticmethod
    def log_security_event(
        event_type: str,
        severity: str = 'low',
        description: str = '',
        user: User = None,
        ip_address: str = '',
        user_agent: str = '',
        endpoint: str = '',
        method: str = '',
        additional_data: dict = None,
        tenant=None
    ) -> SecurityEvent:
        """Log a security event"""
        
        try:
            event = SecurityEvent.objects.create(
                event_type=event_type,
                severity=severity,
                description=description,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                method=method,
                additional_data=additional_data or {},
                tenant=tenant
            )
            
            # Check if this event should trigger an alert
            SecurityMonitoringService._check_alert_triggers(event)
            
            return event
        
        except Exception as e:
            logger.error(f"Error logging security event: {str(e)}")
            raise
    
    @staticmethod
    def _check_alert_triggers(event: SecurityEvent):
        """Check if a security event should trigger an alert"""
        
        try:
            # Multiple failed logins from same IP
            if event.event_type == 'login_failed':
                recent_failures = SecurityEvent.objects.filter(
                    event_type='login_failed',
                    ip_address=event.ip_address,
                    created_at__gte=timezone.now() - timedelta(minutes=15)
                ).count()
                
                if recent_failures >= 5:
                    SecurityAlertService.create_alert(
                        alert_type='multiple_failed_logins',
                        title=f'Multiple failed logins from {event.ip_address}',
                        description=f'{recent_failures} failed login attempts in 15 minutes',
                        severity='high',
                        tenant=event.tenant
                    )
            
            # Suspicious activity patterns
            elif event.event_type == 'suspicious_activity':
                SecurityAlertService.create_alert(
                    alert_type='suspicious_ip',
                    title=f'Suspicious activity detected',
                    description=event.description,
                    severity=event.severity,
                    tenant=event.tenant
                )
        
        except Exception as e:
            logger.error(f"Error checking alert triggers: {str(e)}")


class SecurityAlertService:
    """Service for managing security alerts"""
    
    @staticmethod
    def get_active_alerts(tenant=None):
        """Get all active security alerts"""
        
        try:
            alerts_qs = SecurityAlert.objects.filter(status='active')
            
            if tenant:
                alerts_qs = alerts_qs.filter(tenant=tenant)
            
            alerts = alerts_qs.order_by('-created_at')
            
            alert_data = []
            for alert in alerts:
                alert_data.append({
                    'id': str(alert.id),
                    'alert_type': alert.alert_type,
                    'title': alert.title,
                    'description': alert.description,
                    'severity': alert.severity,
                    'status': alert.status,
                    'created_at': alert.created_at.isoformat(),
                    'assigned_to': alert.assigned_to.email if alert.assigned_to else None
                })
            
            return alert_data
        
        except Exception as e:
            logger.error(f"Error getting active alerts: {str(e)}")
            return []
    
    @staticmethod
    def create_alert(
        alert_type: str,
        title: str,
        description: str,
        severity: str = 'medium',
        tenant=None
    ) -> SecurityAlert:
        """Create a new security alert"""
        
        try:
            # Check if similar alert already exists
            existing_alert = SecurityAlert.objects.filter(
                alert_type=alert_type,
                status='active',
                tenant=tenant,
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).first()
            
            if existing_alert:
                # Update existing alert instead of creating duplicate
                existing_alert.description += f"\n\nAdditional occurrence: {description}"
                existing_alert.save()
                return existing_alert
            
            alert = SecurityAlert.objects.create(
                alert_type=alert_type,
                title=title,
                description=description,
                severity=severity,
                tenant=tenant
            )
            
            # Send notification to administrators
            SecurityAlertService._notify_administrators(alert)
            
            return alert
        
        except Exception as e:
            logger.error(f"Error creating security alert: {str(e)}")
            raise
    
    @staticmethod
    def _notify_administrators(alert: SecurityAlert):
        """Send notification to administrators about new alert"""
        
        try:
            # Get admin users
            admin_users = User.objects.filter(
                Q(is_staff=True) | Q(is_superuser=True),
                is_active=True
            )
            
            if alert.tenant:
                # Filter by tenant if applicable
                admin_users = admin_users.filter(profile__organization=alert.tenant)
            
            admin_emails = list(admin_users.values_list('email', flat=True))
            
            if admin_emails and hasattr(settings, 'EMAIL_HOST'):
                subject = f'Security Alert: {alert.title}'
                message = f"""
A new security alert has been generated:

Alert Type: {alert.get_alert_type_display()}
Severity: {alert.severity.upper()}
Description: {alert.description}

Please review this alert in the admin dashboard.

Time: {alert.created_at}
                """
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@edurise.com'),
                    recipient_list=admin_emails,
                    fail_silently=True
                )
        
        except Exception as e:
            logger.error(f"Error notifying administrators: {str(e)}")


class AuditService:
    """Service for comprehensive audit logging"""
    
    @staticmethod
    def log_action(
        user: User,
        action: str,
        resource_type: str,
        resource_id: str = None,
        description: str = '',
        ip_address: str = '',
        user_agent: str = '',
        endpoint: str = '',
        method: str = '',
        session_id: str = '',
        old_values: dict = None,
        new_values: dict = None,
        tenant=None
    ) -> AuditLog:
        """Log an audit action"""
        
        try:
            # Prepare changes data
            changes = {}
            if old_values:
                changes['old_values'] = old_values
            if new_values:
                changes['new_values'] = new_values
            
            # Add request metadata
            changes['metadata'] = {
                'ip_address': ip_address,
                'user_agent': user_agent,
                'endpoint': endpoint,
                'method': method,
                'session_id': session_id
            }
            
            audit_log = AuditLog.objects.create(
                user=user,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=description,
                old_values=old_values or {},
                new_values=new_values or {},
                ip_address=ip_address,
                user_agent=user_agent,
                tenant=tenant
            )
            
            return audit_log
        
        except Exception as e:
            logger.error(f"Error logging audit action: {str(e)}")
            raise
    
    @staticmethod
    def get_audit_logs(
        tenant=None,
        user_id: str = None,
        action: str = None,
        resource_type: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get filtered audit logs"""
        
        try:
            logs_qs = AuditLog.objects.all()
            
            if tenant:
                logs_qs = logs_qs.filter(tenant=tenant)
            
            if user_id:
                logs_qs = logs_qs.filter(user_id=user_id)
            
            if action:
                logs_qs = logs_qs.filter(action=action)
            
            if resource_type:
                logs_qs = logs_qs.filter(resource_type=resource_type)
            
            if start_date:
                logs_qs = logs_qs.filter(timestamp__gte=start_date)
            
            if end_date:
                logs_qs = logs_qs.filter(created_at__lte=end_date)
            
            logs = logs_qs.order_by('-created_at')[:limit]
            
            log_data = []
            for log in logs:
                log_data.append({
                    'id': str(log.id),
                    'user': log.user.email if log.user else None,
                    'action': log.action,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'description': log.description,
                    'ip_address': log.ip_address,
                    'timestamp': log.created_at.isoformat(),
                    'old_values': log.old_values,
                    'new_values': log.new_values
                })
            
            return log_data
        
        except Exception as e:
            logger.error(f"Error getting audit logs: {str(e)}")
            return []


class ComplianceService:
    """Service for compliance and data protection"""
    
    @staticmethod
    def export_user_data(user: User) -> Dict[str, Any]:
        """Export all user data for GDPR compliance"""
        
        try:
            # Personal information
            personal_info = {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_active': user.is_active
            }
            
            # Profile information
            profile_data = {}
            if hasattr(user, 'profile'):
                profile = user.profile
                profile_data = {
                    'bio': profile.bio,
                    'phone_number': profile.phone_number,
                    'date_of_birth': profile.date_of_birth.isoformat() if profile.date_of_birth else None,
                    'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
                    'organization': profile.organization.name if profile.organization else None
                }
            
            # Course data
            courses_data = []
            if hasattr(user, 'enrollments'):
                for enrollment in user.enrollments.all():
                    courses_data.append({
                        'course_title': enrollment.course.title,
                        'enrollment_date': enrollment.created_at.isoformat(),
                        'completion_status': enrollment.completion_status,
                        'progress_percentage': enrollment.progress_percentage
                    })
            
            # Payment data
            payments_data = []
            if hasattr(user, 'payments'):
                for payment in user.payments.all():
                    payments_data.append({
                        'amount': str(payment.amount),
                        'currency': payment.currency,
                        'status': payment.status,
                        'payment_date': payment.created_at.isoformat(),
                        'course': payment.course.title if payment.course else None
                    })
            
            # Audit logs (limited to user's own actions)
            audit_logs = []
            for log in AuditLog.objects.filter(user=user).order_by('-created_at')[:50]:
                audit_logs.append({
                    'action': log.action,
                    'resource_type': log.resource_type,
                    'timestamp': log.created_at.isoformat(),
                    'description': log.description
                })
            
            # Security events
            security_events = []
            for event in SecurityEvent.objects.filter(user=user).order_by('-created_at')[:20]:
                security_events.append({
                    'event_type': event.event_type,
                    'severity': event.severity,
                    'description': event.description,
                    'timestamp': event.created_at.isoformat(),
                    'ip_address': event.ip_address
                })
            
            return {
                'export_date': timezone.now().isoformat(),
                'user_id': str(user.id),
                'personal_info': personal_info,
                'profile': profile_data,
                'courses': courses_data,
                'payments': payments_data,
                'audit_logs': audit_logs,
                'security_events': security_events,
                'data_retention_policy': 'Data is retained according to our privacy policy',
                'export_format': 'JSON',
                'compliance_frameworks': ['GDPR', 'CCPA']
            }
        
        except Exception as e:
            logger.error(f"Error exporting user data: {str(e)}")
            raise
    
    @staticmethod
    def delete_user_data(user: User) -> Dict[str, Any]:
        """Delete user data for GDPR compliance"""
        
        try:
            deletion_summary = {
                'user_id': str(user.id),
                'user_email': user.email,
                'deletion_date': timezone.now().isoformat(),
                'deleted_items': {}
            }
            
            # Delete or anonymize audit logs
            audit_logs_count = AuditLog.objects.filter(user=user).count()
            AuditLog.objects.filter(user=user).update(user=None)  # Anonymize instead of delete
            deletion_summary['deleted_items']['audit_logs_anonymized'] = audit_logs_count
            
            # Delete security events
            security_events_count = SecurityEvent.objects.filter(user=user).count()
            SecurityEvent.objects.filter(user=user).delete()
            deletion_summary['deleted_items']['security_events'] = security_events_count
            
            # Delete user profile
            if hasattr(user, 'profile'):
                user.profile.delete()
                deletion_summary['deleted_items']['profile'] = 1
            
            # Handle enrollments (mark as deleted user)
            if hasattr(user, 'enrollments'):
                enrollments_count = user.enrollments.count()
                user.enrollments.all().delete()
                deletion_summary['deleted_items']['enrollments'] = enrollments_count
            
            # Handle payments (keep for legal/tax reasons but anonymize)
            if hasattr(user, 'payments'):
                payments_count = user.payments.count()
                user.payments.update(user=None)  # Anonymize
                deletion_summary['deleted_items']['payments_anonymized'] = payments_count
            
            # Delete the user account
            user.delete()
            deletion_summary['deleted_items']['user_account'] = 1
            
            # Log the deletion
            AuditLog.objects.create(
                user=None,
                action='delete',
                resource_type='user_data',
                description=f'GDPR deletion for user {user.email}',
                new_values={'deletion_summary': deletion_summary}
            )
            
            return deletion_summary
        
        except Exception as e:
            logger.error(f"Error deleting user data: {str(e)}")
            raise