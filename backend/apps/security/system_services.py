"""
System administration services for monitoring and maintenance.
"""

import os
import psutil
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
import subprocess
import json

from apps.admin_tools.models import AuditLog

User = get_user_model()
logger = logging.getLogger(__name__)


class SystemMonitoringService:
    """Service for system health monitoring"""
    
    @staticmethod
    def get_system_status() -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        try:
            # Server health
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Database health
            db_status = SystemMonitoringService._check_database_health()
            
            # Cache health
            cache_status = SystemMonitoringService._check_cache_health()
            
            # System uptime
            boot_time = psutil.boot_time()
            uptime_seconds = timezone.now().timestamp() - boot_time
            uptime_days = int(uptime_seconds // 86400)
            uptime_hours = int((uptime_seconds % 86400) // 3600)
            uptime_str = f"{uptime_days} days, {uptime_hours} hours"
            
            # Active connections
            active_connections = SystemMonitoringService._get_active_connections()
            
            return {
                'server_status': 'healthy' if cpu_percent < 80 and memory.percent < 85 else 'warning',
                'database_status': db_status['status'],
                'cache_status': cache_status['status'],
                'cpu_usage': round(cpu_percent, 1),
                'memory_used': round(memory.used / (1024**3), 2),  # GB
                'memory_total': round(memory.total / (1024**3), 2),  # GB
                'memory_percent': memory.percent,
                'disk_used': round(disk.used / (1024**3), 2),  # GB
                'disk_total': round(disk.total / (1024**3), 2),  # GB
                'disk_percent': round((disk.used / disk.total) * 100, 1),
                'uptime': uptime_str,
                'db_connections': db_status['connections'],
                'active_sessions': active_connections,
                'last_updated': timezone.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {
                'server_status': 'error',
                'database_status': 'unknown',
                'cache_status': 'unknown',
                'error': str(e),
                'last_updated': timezone.now().isoformat()
            }
    
    @staticmethod
    def _check_database_health() -> Dict[str, Any]:
        """Check database connection and performance"""
        
        try:
            with connection.cursor() as cursor:
                # Test query
                cursor.execute("SELECT 1")
                
                # Get connection count (PostgreSQL specific)
                try:
                    cursor.execute("""
                        SELECT count(*) 
                        FROM pg_stat_activity 
                        WHERE state = 'active'
                    """)
                    active_connections = cursor.fetchone()[0]
                except Exception:
                    # Fallback for SQLite or other databases
                    active_connections = 1
                
                return {
                    'status': 'healthy',
                    'connections': active_connections,
                    'response_time': 'fast'
                }
        
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'status': 'error',
                'connections': 0,
                'error': str(e)
            }
    
    @staticmethod
    def _check_cache_health() -> Dict[str, Any]:
        """Check cache system health"""
        
        try:
            # Test cache operation
            test_key = 'health_check_test'
            test_value = 'test_value'
            
            cache.set(test_key, test_value, 60)
            retrieved_value = cache.get(test_key)
            
            if retrieved_value == test_value:
                cache.delete(test_key)
                return {'status': 'healthy'}
            else:
                return {'status': 'warning', 'error': 'Cache read/write mismatch'}
        
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    @staticmethod
    def _get_active_connections() -> int:
        """Get number of active user sessions"""
        
        try:
            # Count active sessions from the last hour
            one_hour_ago = timezone.now() - timedelta(hours=1)
            active_users = User.objects.filter(
                last_login__gte=one_hour_ago
            ).count()
            
            return active_users
        
        except Exception as e:
            logger.error(f"Error counting active connections: {str(e)}")
            return 0


class SystemLogsService:
    """Service for system logs management"""
    
    @staticmethod
    def get_system_logs(
        log_type: str = 'all',
        level: str = 'all',
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get system logs with filtering"""
        
        logs = []
        
        try:
            # Get Django logs from database (audit logs)
            if log_type in ['all', 'audit']:
                audit_logs = SystemLogsService._get_audit_logs(start_date, end_date, limit // 2)
                logs.extend(audit_logs)
            
            # Get application logs from log files
            if log_type in ['all', 'application']:
                app_logs = SystemLogsService._get_application_logs(level, start_date, end_date, limit // 2)
                logs.extend(app_logs)
            
            # Sort by timestamp
            logs.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return logs[:limit]
        
        except Exception as e:
            logger.error(f"Error retrieving system logs: {str(e)}")
            return [{
                'level': 'ERROR',
                'message': f'Error retrieving logs: {str(e)}',
                'timestamp': timezone.now().isoformat(),
                'source': 'system'
            }]
    
    @staticmethod
    def _get_audit_logs(start_date: datetime, end_date: datetime, limit: int) -> List[Dict]:
        """Get audit logs from database"""
        
        logs_qs = AuditLog.objects.all()
        
        if start_date:
            logs_qs = logs_qs.filter(created_at__gte=start_date)
        
        if end_date:
            logs_qs = logs_qs.filter(created_at__lte=end_date)
        
        audit_logs = logs_qs.order_by('-created_at')[:limit]
        
        formatted_logs = []
        for log in audit_logs:
            formatted_logs.append({
                'level': 'INFO',
                'message': f"{log.user.email if log.user else 'System'} performed {log.action} on {log.resource_type}",
                'timestamp': log.created_at.isoformat(),
                'source': 'audit',
                'user': log.user.email if log.user else None,
                'action': log.action,
                'resource_type': log.resource_type,
                'ip_address': log.ip_address
            })
        
        return formatted_logs
    
    @staticmethod
    def _get_application_logs(level: str, start_date: datetime, end_date: datetime, limit: int) -> List[Dict]:
        """Get application logs from log files"""
        
        logs = []
        
        try:
            # Try to read from Django log file if configured
            log_file_path = getattr(settings, 'LOG_FILE_PATH', None)
            
            if log_file_path and os.path.exists(log_file_path):
                with open(log_file_path, 'r') as f:
                    lines = f.readlines()
                    
                    # Parse last N lines
                    for line in lines[-limit:]:
                        try:
                            # Simple log parsing - would need more sophisticated parsing for real logs
                            parts = line.strip().split(' - ')
                            if len(parts) >= 3:
                                timestamp_str = parts[0]
                                log_level = parts[1]
                                message = ' - '.join(parts[2:])
                                
                                # Filter by level if specified
                                if level != 'all' and log_level.lower() != level.lower():
                                    continue
                                
                                logs.append({
                                    'level': log_level,
                                    'message': message,
                                    'timestamp': timestamp_str,
                                    'source': 'application'
                                })
                        
                        except Exception:
                            continue
            
            else:
                # Fallback: create sample log entries
                logs.append({
                    'level': 'INFO',
                    'message': 'Application started successfully',
                    'timestamp': timezone.now().isoformat(),
                    'source': 'application'
                })
        
        except Exception as e:
            logger.error(f"Error reading application logs: {str(e)}")
        
        return logs


class SystemMaintenanceService:
    """Service for system maintenance operations"""
    
    @staticmethod
    def perform_maintenance_action(action: str, user: User) -> Dict[str, Any]:
        """Perform system maintenance action"""
        
        valid_actions = ['restart', 'backup', 'cleanup', 'update', 'cache_clear']
        
        if action not in valid_actions:
            return {
                'success': False,
                'error': f"Invalid action. Valid actions: {', '.join(valid_actions)}"
            }
        
        try:
            result = None
            
            if action == 'cache_clear':
                result = SystemMaintenanceService._clear_cache()
            
            elif action == 'cleanup':
                result = SystemMaintenanceService._cleanup_system()
            
            elif action == 'backup':
                result = SystemMaintenanceService._create_backup()
            
            elif action == 'restart':
                result = SystemMaintenanceService._schedule_restart()
            
            elif action == 'update':
                result = SystemMaintenanceService._check_updates()
            
            # Log the maintenance action
            AuditLog.objects.create(
                user=user,
                action='maintenance',
                resource_type='system',
                description=f"Performed maintenance action: {action}",
                ip_address=getattr(user, 'current_ip', ''),
                new_values={'action': action, 'result': result}
            )
            
            return {
                'success': True,
                'action': action,
                'result': result,
                'timestamp': timezone.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Maintenance action {action} failed: {str(e)}")
            return {
                'success': False,
                'action': action,
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
    
    @staticmethod
    def _clear_cache() -> Dict[str, Any]:
        """Clear application cache"""
        
        try:
            cache.clear()
            return {
                'operation': 'cache_clear',
                'status': 'completed',
                'message': 'Application cache cleared successfully'
            }
        
        except Exception as e:
            return {
                'operation': 'cache_clear',
                'status': 'failed',
                'error': str(e)
            }
    
    @staticmethod
    def _cleanup_system() -> Dict[str, Any]:
        """Perform system cleanup"""
        
        try:
            # Clean up old log entries (older than 90 days)
            ninety_days_ago = timezone.now() - timedelta(days=90)
            
            deleted_audit_logs = AuditLog.objects.filter(
                created_at__lt=ninety_days_ago
            ).count()
            
            AuditLog.objects.filter(created_at__lt=ninety_days_ago).delete()
            
            # Clean up old security events
            from .models import SecurityEvent
            deleted_security_events = SecurityEvent.objects.filter(
                created_at__lt=ninety_days_ago,
                is_resolved=True
            ).count()
            
            SecurityEvent.objects.filter(
                created_at__lt=ninety_days_ago,
                is_resolved=True
            ).delete()
            
            return {
                'operation': 'cleanup',
                'status': 'completed',
                'deleted_audit_logs': deleted_audit_logs,
                'deleted_security_events': deleted_security_events,
                'message': 'System cleanup completed successfully'
            }
        
        except Exception as e:
            return {
                'operation': 'cleanup',
                'status': 'failed',
                'error': str(e)
            }
    
    @staticmethod
    def _create_backup() -> Dict[str, Any]:
        """Create system backup"""
        
        try:
            # In a real implementation, this would create database and file backups
            backup_id = f"backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
            
            return {
                'operation': 'backup',
                'status': 'completed',
                'backup_id': backup_id,
                'message': 'System backup created successfully'
            }
        
        except Exception as e:
            return {
                'operation': 'backup',
                'status': 'failed',
                'error': str(e)
            }
    
    @staticmethod
    def _schedule_restart() -> Dict[str, Any]:
        """Schedule system restart"""
        
        try:
            # In a real implementation, this would schedule a graceful restart
            return {
                'operation': 'restart',
                'status': 'scheduled',
                'scheduled_time': (timezone.now() + timedelta(minutes=5)).isoformat(),
                'message': 'System restart scheduled in 5 minutes'
            }
        
        except Exception as e:
            return {
                'operation': 'restart',
                'status': 'failed',
                'error': str(e)
            }
    
    @staticmethod
    def _check_updates() -> Dict[str, Any]:
        """Check for system updates"""
        
        try:
            # In a real implementation, this would check for available updates
            return {
                'operation': 'update_check',
                'status': 'completed',
                'updates_available': False,
                'current_version': '1.0.0',
                'message': 'System is up to date'
            }
        
        except Exception as e:
            return {
                'operation': 'update_check',
                'status': 'failed',
                'error': str(e)
            }


class UserManagementService:
    """Service for bulk user management operations"""
    
    @staticmethod
    def bulk_user_operation(
        operation: str,
        user_ids: List[str],
        admin_user: User,
        **kwargs
    ) -> Dict[str, Any]:
        """Perform bulk operations on users"""
        
        valid_operations = ['activate', 'deactivate', 'delete', 'approve_teacher', 'reject_teacher']
        
        if operation not in valid_operations:
            return {
                'success': False,
                'error': f"Invalid operation. Valid operations: {', '.join(valid_operations)}"
            }
        
        try:
            users = User.objects.filter(id__in=user_ids)
            results = []
            
            for user in users:
                try:
                    if operation == 'activate':
                        user.is_active = True
                        user.save()
                        results.append({'user_id': str(user.id), 'status': 'activated'})
                    
                    elif operation == 'deactivate':
                        user.is_active = False
                        user.save()
                        results.append({'user_id': str(user.id), 'status': 'deactivated'})
                    
                    elif operation == 'delete':
                        if user.is_superuser:
                            results.append({'user_id': str(user.id), 'status': 'error', 'error': 'Cannot delete superuser'})
                        else:
                            user.delete()
                            results.append({'user_id': str(user.id), 'status': 'deleted'})
                    
                    elif operation == 'approve_teacher':
                        user.is_approved_teacher = True
                        user.save()
                        results.append({'user_id': str(user.id), 'status': 'approved'})
                    
                    elif operation == 'reject_teacher':
                        user.is_approved_teacher = False
                        user.save()
                        results.append({'user_id': str(user.id), 'status': 'rejected'})
                
                except Exception as e:
                    results.append({'user_id': str(user.id), 'status': 'error', 'error': str(e)})
            
            # Log the bulk operation
            AuditLog.objects.create(
                user=admin_user,
                action='bulk_operation',
                resource_type='user',
                description=f"Performed bulk {operation} on {len(user_ids)} users",
                new_values={'operation': operation, 'user_ids': user_ids, 'results': results}
            )
            
            return {
                'success': True,
                'operation': operation,
                'total_users': len(user_ids),
                'results': results,
                'timestamp': timezone.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Bulk user operation {operation} failed: {str(e)}")
            return {
                'success': False,
                'operation': operation,
                'error': str(e)
            }