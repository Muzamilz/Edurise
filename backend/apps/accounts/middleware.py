"""
Middleware for standardized API response handling and logging
"""
import json
import logging
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from .response_utils import log_api_request

logger = logging.getLogger(__name__)


class StandardAPIResponseMiddleware:
    """Middleware to standardize API responses and handle errors"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log incoming request
        if request.path.startswith('/api/'):
            log_api_request(request)
        
        response = self.get_response(request)
        
        # Only process API responses
        if not request.path.startswith('/api/'):
            return response
        
        # Handle different response types
        if hasattr(response, 'data') and isinstance(response, Response):
            # DRF Response - check if it needs standardization
            if not self._is_standardized_response(response.data):
                response.data = self._standardize_response_data(response.data, response.status_code)
        elif isinstance(response, JsonResponse):
            # JsonResponse - check if it needs standardization
            try:
                data = json.loads(response.content.decode('utf-8'))
                if not self._is_standardized_response(data):
                    standardized_data = self._standardize_response_data(data, response.status_code)
                    response = JsonResponse(standardized_data, status=response.status_code)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        
        return response
    
    def _is_standardized_response(self, data):
        """Check if response data is already standardized"""
        if not isinstance(data, dict):
            return False
        return 'success' in data and 'timestamp' in data
    
    def _standardize_response_data(self, data, status_code):
        """Standardize response data format"""
        is_success = 200 <= status_code < 300
        
        standardized = {
            'success': is_success,
            'timestamp': timezone.now().isoformat(),
        }
        
        if is_success:
            standardized['message'] = 'Success'
            standardized['data'] = data
        else:
            standardized['message'] = 'Error'
            if isinstance(data, dict) and 'detail' in data:
                standardized['message'] = data['detail']
                if len(data) > 1:
                    standardized['errors'] = {k: v for k, v in data.items() if k != 'detail'}
            else:
                standardized['errors'] = data
        
        return standardized
    
    def process_exception(self, request, exception):
        """Handle unhandled exceptions for API requests"""
        if not request.path.startswith('/api/'):
            return None
        
        # Log the exception
        log_api_request(request, error=exception)
        
        # Return standardized error response
        error_data = {
            'success': False,
            'message': 'Internal server error',
            'timestamp': timezone.now().isoformat(),
            'error_code': 'INTERNAL_ERROR'
        }
        
        # In debug mode, include exception details
        from django.conf import settings
        if settings.DEBUG:
            error_data['debug_info'] = {
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
            }
        
        return JsonResponse(error_data, status=500)


class RequestLoggingMiddleware:
    """Middleware for detailed request/response logging"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip non-API requests
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Log request details
        request_data = {
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
            'ip': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
            'timestamp': timezone.now().isoformat(),
        }
        
        if hasattr(request, 'tenant') and request.tenant:
            request_data['tenant'] = request.tenant.subdomain
        
        # Log request body for POST/PUT/PATCH (excluding sensitive data)
        if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'data'):
            try:
                # Create a copy and remove sensitive fields
                body_data = dict(request.data) if hasattr(request, 'data') else {}
                sensitive_fields = ['password', 'password_confirm', 'token', 'refresh_token']
                for field in sensitive_fields:
                    if field in body_data:
                        body_data[field] = '[REDACTED]'
                request_data['body'] = body_data
            except:
                request_data['body'] = '[COULD_NOT_PARSE]'
        
        logger.info(f"API Request: {json.dumps(request_data, default=str)}")
        
        # Process request
        response = self.get_response(request)
        
        # Log response details
        response_data = {
            'status_code': response.status_code,
            'path': request.path,
            'method': request.method,
            'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous',
            'response_time': timezone.now().isoformat(),
        }
        
        # Log response body for errors or in debug mode
        from django.conf import settings
        if response.status_code >= 400 or settings.DEBUG:
            try:
                if hasattr(response, 'data'):
                    response_data['response_body'] = response.data
                elif hasattr(response, 'content'):
                    content = response.content.decode('utf-8')
                    if content:
                        response_data['response_body'] = json.loads(content)
            except:
                response_data['response_body'] = '[COULD_NOT_PARSE]'
        
        if response.status_code >= 400:
            logger.warning(f"API Error Response: {json.dumps(response_data, default=str)}")
        else:
            logger.info(f"API Response: {json.dumps(response_data, default=str)}")
        
        return response
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip