import json
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from .responses import StandardAPIResponse

logger = logging.getLogger(__name__)


class APILoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests and responses for monitoring and debugging.
    """
    
    def process_request(self, request):
        """Log incoming API requests"""
        if request.path.startswith('/api/'):
            request._api_start_time = time.time()
            
            # Log request details (be careful with sensitive data)
            log_data = {
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'timestamp': timezone.now().isoformat()
            }
            
            # Add tenant info if available
            if hasattr(request, 'tenant'):
                log_data['tenant'] = request.tenant.subdomain if request.tenant else None
            
            logger.info(f"API Request: {json.dumps(log_data)}")
    
    def process_response(self, request, response):
        """Log API responses"""
        if request.path.startswith('/api/') and hasattr(request, '_api_start_time'):
            response_time = time.time() - request._api_start_time
            
            log_data = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'response_time_ms': round(response_time * 1000, 2),
                'timestamp': timezone.now().isoformat()
            }
            
            # Log level based on status code
            if response.status_code >= 500:
                logger.error(f"API Response: {json.dumps(log_data)}")
            elif response.status_code >= 400:
                logger.warning(f"API Response: {json.dumps(log_data)}")
            else:
                logger.info(f"API Response: {json.dumps(log_data)}")
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APIErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware to handle API errors consistently across all endpoints.
    """
    
    def process_exception(self, request, exception):
        """Handle unhandled exceptions in API requests"""
        if request.path.startswith('/api/'):
            # Log the exception
            logger.exception(f"Unhandled API exception: {str(exception)}")
            
            # Return standardized error response
            if settings.DEBUG:
                # In debug mode, include exception details
                error_details = {
                    'exception_type': type(exception).__name__,
                    'exception_message': str(exception),
                    'traceback': None  # Could include traceback if needed
                }
            else:
                error_details = None
            
            return StandardAPIResponse.server_error(
                message="An unexpected error occurred",
                error_id=f"err_{int(time.time())}"
            ).render()
        
        return None


class APIVersioningMiddleware(MiddlewareMixin):
    """
    Middleware to handle API versioning and deprecation warnings.
    """
    
    def process_request(self, request):
        """Add API version information to request"""
        if request.path.startswith('/api/'):
            # Extract version from URL path
            path_parts = request.path.strip('/').split('/')
            if len(path_parts) >= 2 and path_parts[1].startswith('v'):
                request.api_version = path_parts[1]
            else:
                request.api_version = 'v1'  # Default version
    
    def process_response(self, request, response):
        """Add API version headers to response"""
        if request.path.startswith('/api/'):
            response['X-API-Version'] = getattr(request, 'api_version', 'v1')
            response['X-API-Timestamp'] = timezone.now().isoformat()
            
            # Add deprecation warning for old versions if needed
            if getattr(request, 'api_version', 'v1') == 'v0':
                response['X-API-Deprecation-Warning'] = 'This API version is deprecated. Please upgrade to v1.'
        
        return response


class APIRateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware for API endpoints.
    Note: In production, consider using Redis-based rate limiting.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_counts = {}  # In-memory storage (not suitable for production)
        super().__init__(get_response)
    
    def process_request(self, request):
        """Check rate limits for API requests"""
        if not request.path.startswith('/api/'):
            return None
        
        # Skip rate limiting for health check
        if request.path.endswith('/health/'):
            return None
        
        client_ip = self.get_client_ip(request)
        current_time = int(time.time())
        window_start = current_time - 60  # 1-minute window
        
        # Clean old entries
        self.cleanup_old_entries(window_start)
        
        # Count requests in current window
        key = f"{client_ip}:{window_start // 60}"
        current_count = self.request_counts.get(key, 0)
        
        # Rate limit: 100 requests per minute per IP
        rate_limit = getattr(settings, 'API_RATE_LIMIT_PER_MINUTE', 100)
        
        if current_count >= rate_limit:
            return JsonResponse({
                'success': False,
                'message': 'Rate limit exceeded. Please try again later.',
                'error_code': 'RATE_LIMIT_EXCEEDED',
                'timestamp': timezone.now().isoformat()
            }, status=429)
        
        # Increment counter
        self.request_counts[key] = current_count + 1
        
        return None
    
    def cleanup_old_entries(self, window_start):
        """Remove old rate limit entries"""
        keys_to_remove = []
        for key in self.request_counts:
            if ':' in key:
                window = int(key.split(':')[1])
                if window < (window_start // 60):
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.request_counts[key]
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APICORSMiddleware(MiddlewareMixin):
    """
    Custom CORS middleware for API endpoints.
    Note: Consider using django-cors-headers for production.
    """
    
    def process_response(self, request, response):
        """Add CORS headers to API responses"""
        if request.path.startswith('/api/'):
            # Allow specific origins in production
            if settings.DEBUG:
                response['Access-Control-Allow-Origin'] = '*'
            else:
                # Configure allowed origins from settings
                allowed_origins = getattr(settings, 'API_ALLOWED_ORIGINS', [])
                origin = request.META.get('HTTP_ORIGIN')
                if origin in allowed_origins:
                    response['Access-Control-Allow-Origin'] = origin
            
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Tenant'
            response['Access-Control-Max-Age'] = '86400'  # 24 hours
        
        return response