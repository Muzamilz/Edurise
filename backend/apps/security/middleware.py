"""
Security middleware for audit logging and monitoring.
"""

import json
import logging
import re
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
from django.core.cache import cache
from .services import SecurityMonitoringService, AuditService
from .validators import SecurityValidator

User = get_user_model()
logger = logging.getLogger(__name__)


class AuditLoggingMiddleware(MiddlewareMixin):
    """Middleware to automatically log all API requests for audit purposes"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Store request start time and details"""
        request._audit_start_time = timezone.now()
        request._audit_data = {
            'method': request.method,
            'path': request.path,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': self._get_client_ip(request),
            'session_id': request.session.session_key if hasattr(request, 'session') else None
        }
    
    def process_response(self, request, response):
        """Log the request after processing"""
        
        # Skip logging for certain paths
        skip_paths = ['/health/', '/static/', '/media/', '/favicon.ico']
        if any(request.path.startswith(path) for path in skip_paths):
            return response
        
        # Skip logging for GET requests to reduce noise (optional)
        if request.method == 'GET' and not request.path.startswith('/api/'):
            return response
        
        try:
            user = getattr(request, 'user', None)
            if user and user.is_authenticated:
                
                # Determine action type based on method and response
                action = self._determine_action(request.method, response.status_code)
                
                # Get resource information from URL
                resource_info = self._extract_resource_info(request.path)
                
                # Log the audit entry
                AuditService.log_action(
                    user=user,
                    action=action,
                    resource_type=resource_info['type'],
                    resource_id=resource_info['id'],
                    description=f"{request.method} {request.path} - {response.status_code}",
                    ip_address=request._audit_data['ip_address'],
                    user_agent=request._audit_data['user_agent'],
                    endpoint=request.path,
                    method=request.method,
                    session_id=request._audit_data['session_id'],
                    tenant=getattr(request, 'tenant', None)
                )
        
        except Exception as e:
            logger.error(f"Error in audit logging middleware: {str(e)}")
        
        return response
    
    def _get_client_ip(self, request):
        """Get the client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _determine_action(self, method, status_code):
        """Determine audit action based on HTTP method and status"""
        if status_code >= 400:
            return 'error'
        
        action_map = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete'
        }
        
        return action_map.get(method, 'unknown')
    
    def _extract_resource_info(self, path):
        """Extract resource type and ID from URL path"""
        
        # Default values
        resource_type = 'unknown'
        resource_id = None
        
        try:
            # Parse API paths like /api/v1/courses/123/
            path_parts = [p for p in path.split('/') if p]
            
            if len(path_parts) >= 3 and path_parts[0] == 'api' and path_parts[1] == 'v1':
                resource_type = path_parts[2]
                
                # Try to extract ID if present
                if len(path_parts) >= 4:
                    potential_id = path_parts[3]
                    # Check if it looks like an ID (UUID or number)
                    if potential_id.isdigit() or len(potential_id) == 36:  # UUID length
                        resource_id = potential_id
        
        except Exception:
            pass
        
        return {
            'type': resource_type,
            'id': resource_id
        }


class SecurityMonitoringMiddleware(MiddlewareMixin):
    """Middleware for security monitoring and threat detection"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Monitor requests for security threats"""
        
        try:
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Check for suspicious patterns
            self._check_suspicious_patterns(request, ip_address, user_agent)
            
            # Rate limiting check (basic implementation)
            self._check_rate_limiting(request, ip_address)
        
        except Exception as e:
            logger.error(f"Error in security monitoring middleware: {str(e)}")
    
    def process_response(self, request, response):
        """Monitor responses for security events"""
        
        try:
            # Log failed authentication attempts
            if response.status_code == 401:
                self._log_failed_authentication(request)
            
            # Log permission denied events
            elif response.status_code == 403:
                self._log_permission_denied(request)
            
            # Log suspicious 404 patterns (potential scanning)
            elif response.status_code == 404:
                self._check_404_patterns(request)
        
        except Exception as e:
            logger.error(f"Error in security monitoring response: {str(e)}")
        
        return response
    
    def _get_client_ip(self, request):
        """Get the client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _check_suspicious_patterns(self, request, ip_address, user_agent):
        """Check for suspicious request patterns"""
        
        # Check for suspicious user agents
        suspicious_agents = ['sqlmap', 'nikto', 'nmap', 'masscan', 'nessus']
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            SecurityMonitoringService.log_security_event(
                event_type='suspicious_activity',
                severity='high',
                description=f'Suspicious user agent detected: {user_agent}',
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=request.path,
                method=request.method,
                tenant=getattr(request, 'tenant', None)
            )
        
        # Check for SQL injection patterns in query parameters
        sql_patterns = ['union', 'select', 'drop', 'insert', 'update', 'delete', '--', ';']
        query_string = request.META.get('QUERY_STRING', '').lower()
        
        if any(pattern in query_string for pattern in sql_patterns):
            SecurityMonitoringService.log_security_event(
                event_type='intrusion_attempt',
                severity='high',
                description=f'Potential SQL injection attempt in query: {query_string}',
                user=getattr(request, 'user', None) if hasattr(request, 'user') else None,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=request.path,
                method=request.method,
                tenant=getattr(request, 'tenant', None)
            )
    
    def _check_rate_limiting(self, request, ip_address):
        """Basic rate limiting check"""
        
        from django.core.cache import cache
        
        # Simple rate limiting: max 100 requests per minute per IP
        cache_key = f'rate_limit:{ip_address}'
        current_requests = cache.get(cache_key, 0)
        
        if current_requests > 100:
            SecurityMonitoringService.log_security_event(
                event_type='api_abuse',
                severity='medium',
                description=f'Rate limit exceeded: {current_requests} requests in 1 minute',
                user=getattr(request, 'user', None) if hasattr(request, 'user') else None,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                endpoint=request.path,
                method=request.method,
                tenant=getattr(request, 'tenant', None)
            )
        else:
            cache.set(cache_key, current_requests + 1, 60)  # 1 minute timeout
    
    def _log_failed_authentication(self, request):
        """Log failed authentication attempts"""
        
        ip_address = self._get_client_ip(request)
        
        SecurityMonitoringService.log_security_event(
            event_type='login_failed',
            severity='medium',
            description='Failed authentication attempt',
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            endpoint=request.path,
            method=request.method,
            tenant=getattr(request, 'tenant', None)
        )
    
    def _log_permission_denied(self, request):
        """Log permission denied events"""
        
        ip_address = self._get_client_ip(request)
        
        SecurityMonitoringService.log_security_event(
            event_type='permission_denied',
            severity='low',
            description='Access denied to protected resource',
            user=getattr(request, 'user', None) if hasattr(request, 'user') else None,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            endpoint=request.path,
            method=request.method,
            tenant=getattr(request, 'tenant', None)
        )
    
    def _check_404_patterns(self, request):
        """Check for suspicious 404 patterns that might indicate scanning"""
        
        from django.core.cache import cache
        
        ip_address = self._get_client_ip(request)
        
        # Track 404s per IP
        cache_key = f'404_count:{ip_address}'
        count_404 = cache.get(cache_key, 0)
        
        # If more than 20 404s in 5 minutes, it might be scanning
        if count_404 > 20:
            SecurityMonitoringService.log_security_event(
                event_type='suspicious_activity',
                severity='medium',
                description=f'Potential scanning detected: {count_404} 404 errors in 5 minutes',
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                endpoint=request.path,
                method=request.method,
                additional_data={'404_count': count_404},
                tenant=getattr(request, 'tenant', None)
            )
        else:
            cache.set(cache_key, count_404 + 1, 300)  # 5 minutes timeout


class InputValidationMiddleware(MiddlewareMixin):
    """Middleware for comprehensive input validation and sanitization"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'SECURITY_MONITORING_ENABLED', True)
        super().__init__(get_response)
    
    def process_request(self, request):
        """Validate and sanitize request data"""
        if not self.enabled:
            return None
        
        try:
            # Skip validation for certain paths
            skip_paths = ['/health/', '/static/', '/media/', '/admin/']
            if any(request.path.startswith(path) for path in skip_paths):
                return None
            
            # Validate query parameters
            if request.GET:
                validation_result = SecurityValidator.validate_request_data(dict(request.GET))
                if not validation_result['valid']:
                    self._log_security_violation(request, 'query_parameters', validation_result['security_issues'])
                    return self._security_response("Invalid query parameters")
            
            # Validate POST data
            if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'body'):
                try:
                    if request.content_type == 'application/json':
                        data = json.loads(request.body.decode('utf-8'))
                        validation_result = SecurityValidator.validate_request_data(data)
                        if not validation_result['valid']:
                            self._log_security_violation(request, 'json_body', validation_result['security_issues'])
                            return self._security_response("Invalid request data")
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass  # Let Django handle malformed JSON
            
            # Validate headers for injection attempts
            self._validate_headers(request)
        
        except Exception as e:
            logger.error(f"Error in input validation middleware: {str(e)}")
        
        return None
    
    def _validate_headers(self, request):
        """Validate HTTP headers for security threats"""
        dangerous_headers = ['User-Agent', 'Referer', 'X-Forwarded-For']
        
        for header in dangerous_headers:
            value = request.META.get(f'HTTP_{header.upper().replace("-", "_")}', '')
            if value:
                validation_result = SecurityValidator.validate_request_data(value)
                if not validation_result['valid']:
                    self._log_security_violation(request, f'header_{header}', validation_result['security_issues'])
    
    def _log_security_violation(self, request, violation_type: str, issues: list):
        """Log security violation"""
        ip_address = self._get_client_ip(request)
        
        SecurityMonitoringService.log_security_event(
            event_type='intrusion_attempt',
            severity='high',
            description=f'Input validation failed: {violation_type} - {", ".join(issues)}',
            user=getattr(request, 'user', None) if hasattr(request, 'user') else None,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            endpoint=request.path,
            method=request.method,
            additional_data={'violation_type': violation_type, 'issues': issues},
            tenant=getattr(request, 'tenant', None)
        )
    
    def _security_response(self, message: str):
        """Return security error response"""
        return JsonResponse({
            'error': 'Security validation failed',
            'message': message,
            'code': 'SECURITY_VIOLATION'
        }, status=400)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitingMiddleware(MiddlewareMixin):
    """Advanced rate limiting middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'RATE_LIMIT_ENABLE', True)
        self.per_minute = getattr(settings, 'RATE_LIMIT_PER_MINUTE', 100)
        self.per_hour = getattr(settings, 'RATE_LIMIT_PER_HOUR', 1000)
        self.per_day = getattr(settings, 'RATE_LIMIT_PER_DAY', 10000)
        super().__init__(get_response)
    
    def process_request(self, request):
        """Apply rate limiting"""
        if not self.enabled:
            return None
        
        try:
            ip_address = self._get_client_ip(request)
            user_id = getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else None
            
            # Create cache keys
            minute_key = f"rate_limit:minute:{ip_address}:{user_id}"
            hour_key = f"rate_limit:hour:{ip_address}:{user_id}"
            day_key = f"rate_limit:day:{ip_address}:{user_id}"
            
            # Check rate limits
            minute_count = cache.get(minute_key, 0)
            hour_count = cache.get(hour_key, 0)
            day_count = cache.get(day_key, 0)
            
            # Check if limits exceeded
            if minute_count >= self.per_minute:
                self._log_rate_limit_exceeded(request, 'minute', minute_count)
                return self._rate_limit_response('Too many requests per minute')
            
            if hour_count >= self.per_hour:
                self._log_rate_limit_exceeded(request, 'hour', hour_count)
                return self._rate_limit_response('Too many requests per hour')
            
            if day_count >= self.per_day:
                self._log_rate_limit_exceeded(request, 'day', day_count)
                return self._rate_limit_response('Too many requests per day')
            
            # Increment counters
            cache.set(minute_key, minute_count + 1, 60)  # 1 minute
            cache.set(hour_key, hour_count + 1, 3600)    # 1 hour
            cache.set(day_key, day_count + 1, 86400)     # 1 day
        
        except Exception as e:
            logger.error(f"Error in rate limiting middleware: {str(e)}")
        
        return None
    
    def _log_rate_limit_exceeded(self, request, period: str, count: int):
        """Log rate limit exceeded event"""
        ip_address = self._get_client_ip(request)
        
        SecurityMonitoringService.log_security_event(
            event_type='api_abuse',
            severity='medium',
            description=f'Rate limit exceeded: {count} requests per {period}',
            user=getattr(request, 'user', None) if hasattr(request, 'user') else None,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            endpoint=request.path,
            method=request.method,
            additional_data={'period': period, 'count': count},
            tenant=getattr(request, 'tenant', None)
        )
    
    def _rate_limit_response(self, message: str):
        """Return rate limit error response"""
        return JsonResponse({
            'error': 'Rate limit exceeded',
            'message': message,
            'code': 'RATE_LIMIT_EXCEEDED'
        }, status=429)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CSRFEnhancementMiddleware(MiddlewareMixin):
    """Enhanced CSRF protection middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Enhanced CSRF validation"""
        try:
            # Skip for safe methods
            if request.method in ['GET', 'HEAD', 'OPTIONS', 'TRACE']:
                return None
            
            # Additional CSRF checks for API endpoints
            if request.path.startswith('/api/'):
                # Check for double submit cookie pattern
                csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
                csrf_cookie = request.COOKIES.get('csrftoken')
                
                if csrf_token and csrf_cookie and csrf_token != csrf_cookie:
                    self._log_csrf_violation(request, 'token_mismatch')
                
                # Check referer for API calls
                referer = request.META.get('HTTP_REFERER', '')
                if referer and not self._is_same_origin(request, referer):
                    self._log_csrf_violation(request, 'cross_origin')
        
        except Exception as e:
            logger.error(f"Error in CSRF enhancement middleware: {str(e)}")
        
        return None
    
    def _is_same_origin(self, request, referer: str) -> bool:
        """Check if referer is from same origin"""
        try:
            from urllib.parse import urlparse
            
            request_origin = f"{request.scheme}://{request.get_host()}"
            referer_origin = f"{urlparse(referer).scheme}://{urlparse(referer).netloc}"
            
            return request_origin == referer_origin
        except Exception:
            return False
    
    def _log_csrf_violation(self, request, violation_type: str):
        """Log CSRF violation"""
        ip_address = self._get_client_ip(request)
        
        SecurityMonitoringService.log_security_event(
            event_type='intrusion_attempt',
            severity='high',
            description=f'CSRF violation: {violation_type}',
            user=getattr(request, 'user', None) if hasattr(request, 'user') else None,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            endpoint=request.path,
            method=request.method,
            additional_data={'violation_type': violation_type},
            tenant=getattr(request, 'tenant', None)
        )
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add comprehensive security headers"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_response(self, request, response):
        """Add security headers to response"""
        try:
            # Content Security Policy
            if not response.get('Content-Security-Policy'):
                csp_directives = [
                    "default-src 'self'",
                    "script-src 'self' 'unsafe-inline' https://apis.google.com",
                    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                    "font-src 'self' https://fonts.gstatic.com",
                    "img-src 'self' data: https:",
                    "connect-src 'self' https://api.zoom.us https://generativelanguage.googleapis.com",
                    "frame-ancestors 'none'",
                    "base-uri 'self'",
                    "form-action 'self'"
                ]
                response['Content-Security-Policy'] = '; '.join(csp_directives)
            
            # Additional security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
            
            # HSTS for HTTPS
            if request.is_secure():
                response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Remove server information
            if 'Server' in response:
                del response['Server']
            
            # Add custom security header
            response['X-Security-Scan'] = 'passed'
        
        except Exception as e:
            logger.error(f"Error adding security headers: {str(e)}")
        
        return response