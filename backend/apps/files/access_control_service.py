"""
Enhanced file access control service with role-based permissions,
subscription plan restrictions, and secure URL generation.
"""

import hashlib
import hmac
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache

from .models import FileUpload, FileAccessLog
from apps.accounts.models import Organization

User = get_user_model()


class FileAccessControlService:
    """Enhanced file access control service with subscription-based restrictions"""
    
    def __init__(self):
        self.secret_key = getattr(settings, 'SECRET_KEY', 'default-secret')
        self.default_expires_in = 3600  # 1 hour
        self.max_expires_in = 86400  # 24 hours
    
    def check_file_access(self, file_upload: FileUpload, user: User, request_ip: str = None) -> Dict[str, Any]:
        """
        Comprehensive file access check with subscription plan restrictions
        
        Returns:
            Dict with 'allowed', 'reason', 'restrictions', 'subscription_required', etc.
        """
        result = {
            'allowed': False,
            'reason': 'Access denied',
            'restrictions': [],
            'subscription_required': False,
            'upgrade_url': None
        }
        
        # Basic file status checks
        if file_upload.status == 'deleted':
            result['reason'] = 'File has been deleted'
            return result
        
        if file_upload.is_expired:
            result['reason'] = 'File has expired'
            return result
        
        # Owner always has access
        if file_upload.uploaded_by == user:
            result['allowed'] = True
            result['reason'] = 'File owner'
            return result
        
        # Staff/admin access
        if user.is_staff or user.is_superuser:
            result['allowed'] = True
            result['reason'] = 'Administrative access'
            return result
        
        # Check subscription plan restrictions
        subscription_check = self._check_subscription_restrictions(file_upload, user)
        if not subscription_check['allowed']:
            result.update(subscription_check)
            return result
        
        # Check access level permissions
        access_level_check = self._check_access_level_permissions(file_upload, user)
        if not access_level_check['allowed']:
            result.update(access_level_check)
            return result
        
        # Check IP restrictions if configured
        ip_check = self._check_ip_restrictions(file_upload, request_ip)
        if not ip_check['allowed']:
            result.update(ip_check)
            return result
        
        # Check time-based restrictions
        time_check = self._check_time_restrictions(file_upload, user)
        if not time_check['allowed']:
            result.update(time_check)
            return result
        
        # All checks passed
        result['allowed'] = True
        result['reason'] = 'Access granted'
        return result
    
    def _check_subscription_restrictions(self, file_upload: FileUpload, user: User) -> Dict[str, Any]:
        """Check if user's subscription plan allows access to this file"""
        result = {'allowed': True, 'reason': 'Subscription check passed'}
        
        try:
            # Get user's organization/tenant
            user_org = getattr(user, 'tenant', None)
            if not user_org:
                # Try to get from user profiles
                profile = user.profiles.first()
                if profile:
                    user_org = profile.tenant
            
            if not user_org:
                result['allowed'] = False
                result['reason'] = 'No organization found'
                return result
            
            # Check subscription plan restrictions
            subscription_plan = user_org.subscription_plan
            
            # Define file access restrictions by subscription plan
            plan_restrictions = {
                'basic': {
                    'max_file_size_mb': 10,
                    'allowed_file_types': ['image', 'document'],
                    'max_downloads_per_day': 50
                },
                'pro': {
                    'max_file_size_mb': 100,
                    'allowed_file_types': ['image', 'document', 'video', 'audio'],
                    'max_downloads_per_day': 500
                },
                'enterprise': {
                    'max_file_size_mb': 1000,
                    'allowed_file_types': ['*'],  # All types allowed
                    'max_downloads_per_day': -1  # Unlimited
                }
            }
            
            restrictions = plan_restrictions.get(subscription_plan, plan_restrictions['basic'])
            
            # Check file size restriction
            if file_upload.file_size_mb > restrictions['max_file_size_mb']:
                result['allowed'] = False
                result['reason'] = f'File size exceeds {restrictions["max_file_size_mb"]}MB limit for {subscription_plan} plan'
                result['subscription_required'] = True
                result['restrictions'].append(f'max_file_size: {restrictions["max_file_size_mb"]}MB')
                return result
            
            # Check file type restriction
            allowed_types = restrictions['allowed_file_types']
            if '*' not in allowed_types:
                file_category = self._get_file_category(file_upload)
                if file_category not in allowed_types:
                    result['allowed'] = False
                    result['reason'] = f'{file_category} files not allowed in {subscription_plan} plan'
                    result['subscription_required'] = True
                    result['restrictions'].append(f'allowed_types: {", ".join(allowed_types)}')
                    return result
            
            # Check daily download limit
            max_downloads = restrictions['max_downloads_per_day']
            if max_downloads > 0:
                today_downloads = self._get_user_daily_downloads(user)
                if today_downloads >= max_downloads:
                    result['allowed'] = False
                    result['reason'] = f'Daily download limit of {max_downloads} exceeded'
                    result['subscription_required'] = True
                    result['restrictions'].append(f'daily_limit: {max_downloads}')
                    return result
            
        except Exception as e:
            result['allowed'] = False
            result['reason'] = f'Subscription check failed: {str(e)}'
        
        return result
    
    def _check_access_level_permissions(self, file_upload: FileUpload, user: User) -> Dict[str, Any]:
        """Check access level permissions"""
        result = {'allowed': False, 'reason': 'Access level check failed'}
        
        access_level = file_upload.access_level
        
        if access_level == 'public':
            result['allowed'] = True
            result['reason'] = 'Public file'
        
        elif access_level == 'tenant':
            if hasattr(user, 'tenant') and user.tenant == file_upload.tenant:
                result['allowed'] = True
                result['reason'] = 'Tenant access'
            else:
                result['reason'] = 'Not in same tenant'
        
        elif access_level == 'enrolled' and file_upload.course:
            if file_upload.course.enrollments.filter(student=user).exists():
                result['allowed'] = True
                result['reason'] = 'Enrolled student access'
            else:
                result['reason'] = 'Not enrolled in course'
        
        elif access_level == 'instructor' and file_upload.course:
            if file_upload.course.instructor == user:
                result['allowed'] = True
                result['reason'] = 'Course instructor access'
            else:
                result['reason'] = 'Not course instructor'
        
        elif access_level == 'private':
            if file_upload.allowed_users.filter(id=user.id).exists():
                result['allowed'] = True
                result['reason'] = 'Explicitly allowed user'
            else:
                result['reason'] = 'Not in allowed users list'
        
        return result
    
    def _check_ip_restrictions(self, file_upload: FileUpload, request_ip: str) -> Dict[str, Any]:
        """Check IP-based restrictions (if configured)"""
        result = {'allowed': True, 'reason': 'No IP restrictions'}
        
        # This could be extended to check IP whitelist/blacklist
        # For now, we'll just log the IP for security purposes
        
        return result
    
    def _check_time_restrictions(self, file_upload: FileUpload, user: User) -> Dict[str, Any]:
        """Check time-based access restrictions"""
        result = {'allowed': True, 'reason': 'No time restrictions'}
        
        # Check if file has expired
        if file_upload.expires_at and timezone.now() > file_upload.expires_at:
            result['allowed'] = False
            result['reason'] = 'File access has expired'
        
        # Could add business hours restrictions, etc.
        
        return result
    
    def _get_file_category(self, file_upload: FileUpload) -> str:
        """Get file category for subscription restrictions"""
        if file_upload.is_image:
            return 'image'
        elif file_upload.is_video:
            return 'video'
        elif file_upload.is_document:
            return 'document'
        elif file_upload.file_type.startswith('audio/'):
            return 'audio'
        else:
            return 'other'
    
    def _get_user_daily_downloads(self, user: User) -> int:
        """Get user's download count for today"""
        today = timezone.now().date()
        cache_key = f"user_downloads_{user.id}_{today}"
        
        downloads = cache.get(cache_key)
        if downloads is None:
            downloads = FileAccessLog.objects.filter(
                user=user,
                accessed_at__date=today
            ).count()
            cache.set(cache_key, downloads, 3600)  # Cache for 1 hour
        
        return downloads
    
    def generate_secure_url(self, file_upload: FileUpload, user: User, expires_in: int = None, request_ip: str = None) -> Optional[str]:
        """
        Generate secure URL for file access with token-based authentication
        
        Args:
            file_upload: FileUpload instance
            user: User requesting access
            expires_in: Expiration time in seconds
            request_ip: Client IP address for additional security
            
        Returns:
            Secure URL string or None if access denied
        """
        # Check if user can access the file
        access_result = self.check_file_access(file_upload, user, request_ip)
        if not access_result['allowed']:
            return None
        
        # Set expiration
        if expires_in is None:
            expires_in = self.default_expires_in
        elif expires_in > self.max_expires_in:
            expires_in = self.max_expires_in
        
        expires_at = int(time.time()) + expires_in
        
        # Generate secure token
        token_data = {
            'file_id': str(file_upload.id),
            'user_id': str(user.id),
            'expires': expires_at,
            'ip': request_ip or 'unknown'
        }
        
        token = self._generate_secure_token(token_data)
        
        # Build secure URL
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        secure_url = f"{base_url}/api/v1/files/secure-download/{file_upload.id}/"
        
        params = {
            'token': token,
            'expires': expires_at
        }
        
        return f"{secure_url}?{urlencode(params)}"
    
    def _generate_secure_token(self, token_data: Dict) -> str:
        """Generate HMAC-based secure token"""
        # Create message from token data
        message = f"{token_data['file_id']}:{token_data['user_id']}:{token_data['expires']}:{token_data['ip']}"
        
        # Generate HMAC signature
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_secure_token(self, file_id: str, token: str, expires: str, user: User, request_ip: str = None) -> Dict[str, Any]:
        """
        Verify secure token for file access
        
        Returns:
            Dict with 'valid', 'reason', etc.
        """
        result = {'valid': False, 'reason': 'Invalid token'}
        
        try:
            # Check expiration
            expires_timestamp = int(expires)
            if time.time() > expires_timestamp:
                result['reason'] = 'Token expired'
                return result
            
            # Regenerate token with same data
            token_data = {
                'file_id': file_id,
                'user_id': str(user.id),
                'expires': expires_timestamp,
                'ip': request_ip or 'unknown'
            }
            
            expected_token = self._generate_secure_token(token_data)
            
            # Compare tokens (constant time comparison)
            if hmac.compare_digest(token, expected_token):
                result['valid'] = True
                result['reason'] = 'Token valid'
            else:
                result['reason'] = 'Token signature invalid'
        
        except (ValueError, TypeError) as e:
            result['reason'] = f'Token format error: {str(e)}'
        
        return result
    
    def get_user_file_permissions(self, user: User, file_upload: FileUpload) -> Dict[str, Any]:
        """Get detailed permissions for user on specific file"""
        access_result = self.check_file_access(file_upload, user)
        
        permissions = {
            'can_view': access_result['allowed'],
            'can_download': access_result['allowed'],
            'can_edit': False,
            'can_delete': False,
            'can_share': False,
            'access_reason': access_result['reason'],
            'restrictions': access_result.get('restrictions', [])
        }
        
        # Check edit/delete permissions
        if file_upload.uploaded_by == user or user.is_staff:
            permissions['can_edit'] = True
            permissions['can_delete'] = True
        
        # Check sharing permissions
        if access_result['allowed'] and (file_upload.uploaded_by == user or user.is_staff):
            permissions['can_share'] = True
        
        return permissions
    
    def bulk_check_access(self, file_uploads: List[FileUpload], user: User) -> Dict[str, Dict]:
        """Bulk check access for multiple files"""
        results = {}
        
        for file_upload in file_uploads:
            access_result = self.check_file_access(file_upload, user)
            permissions = self.get_user_file_permissions(user, file_upload)
            
            results[str(file_upload.id)] = {
                'access_allowed': access_result['allowed'],
                'access_reason': access_result['reason'],
                'permissions': permissions,
                'file_info': {
                    'filename': file_upload.original_filename,
                    'size_mb': file_upload.file_size_mb,
                    'type': file_upload.file_type,
                    'access_level': file_upload.access_level
                }
            }
        
        return results
    
    def log_file_access(self, file_upload: FileUpload, user: User, request_ip: str = None, 
                       user_agent: str = None, access_granted: bool = True):
        """Log file access attempt with enhanced details"""
        try:
            # Create access log
            access_log = FileAccessLog.objects.create(
                file=file_upload,
                user=user,
                tenant=file_upload.tenant,
                ip_address=request_ip,
                user_agent=user_agent or ''
            )
            
            # Update file statistics
            if access_granted:
                file_upload.record_access(user)
            
            # Cache user's daily download count
            if access_granted:
                today = timezone.now().date()
                cache_key = f"user_downloads_{user.id}_{today}"
                current_count = cache.get(cache_key, 0)
                cache.set(cache_key, current_count + 1, 3600)
            
        except Exception as e:
            # Log error but don't fail the request
            print(f"Error logging file access: {e}")
    
    def get_subscription_upgrade_url(self, user: User, required_plan: str = 'pro') -> str:
        """Get URL for subscription upgrade"""
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        return f"{base_url}/subscription/upgrade?plan={required_plan}"
    
    def check_file_sharing_permissions(self, file_upload: FileUpload, user: User, target_users: List[User]) -> Dict[str, Any]:
        """Check if user can share file with target users"""
        result = {
            'can_share': False,
            'reason': 'Sharing not allowed',
            'allowed_users': [],
            'denied_users': []
        }
        
        # Check if user can share this file
        if file_upload.uploaded_by != user and not user.is_staff:
            result['reason'] = 'Only file owner can share'
            return result
        
        # Check subscription plan sharing limits
        user_org = getattr(user, 'tenant', None)
        if user_org and user_org.subscription_plan == 'basic':
            result['reason'] = 'File sharing requires Pro or Enterprise plan'
            result['upgrade_url'] = self.get_subscription_upgrade_url(user)
            return result
        
        # Check each target user
        for target_user in target_users:
            if target_user.tenant == file_upload.tenant:
                result['allowed_users'].append({
                    'user_id': str(target_user.id),
                    'email': target_user.email,
                    'name': target_user.get_full_name()
                })
            else:
                result['denied_users'].append({
                    'user_id': str(target_user.id),
                    'email': target_user.email,
                    'reason': 'Different tenant'
                })
        
        result['can_share'] = len(result['allowed_users']) > 0
        if result['can_share']:
            result['reason'] = 'Sharing allowed'
        
        return result