"""
Standardized API response utilities for consistent response formatting
"""
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class StandardAPIResponse:
    """Standardized API response wrapper"""
    
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK, meta=None):
        """Create a standardized success response"""
        response_data = {
            'success': True,
            'message': message,
            'data': data,
            'timestamp': timezone.now().isoformat(),
        }
        
        if meta:
            response_data['meta'] = meta
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(message="An error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST, error_code=None):
        """Create a standardized error response"""
        response_data = {
            'success': False,
            'message': message,
            'timestamp': timezone.now().isoformat(),
        }
        
        if errors:
            response_data['errors'] = errors
            
        if error_code:
            response_data['error_code'] = error_code
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def paginated(data, page_info, message="Success", status_code=status.HTTP_200_OK):
        """Create a standardized paginated response"""
        response_data = {
            'success': True,
            'message': message,
            'data': data,
            'pagination': page_info,
            'timestamp': timezone.now().isoformat(),
        }
        
        return Response(response_data, status=status_code)


class APIResponseMixin:
    """Mixin to add standardized response methods to ViewSets"""
    
    def success_response(self, data=None, message="Success", status_code=status.HTTP_200_OK, meta=None):
        """Return a standardized success response"""
        return StandardAPIResponse.success(data, message, status_code, meta)
    
    def error_response(self, message="An error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST, error_code=None):
        """Return a standardized error response"""
        return StandardAPIResponse.error(message, errors, status_code, error_code)
    
    def paginated_response(self, data, page_info, message="Success", status_code=status.HTTP_200_OK):
        """Return a standardized paginated response"""
        return StandardAPIResponse.paginated(data, page_info, message, status_code)
    
    def validation_error_response(self, serializer_errors):
        """Return a standardized validation error response"""
        formatted_errors = {}
        for field, errors in serializer_errors.items():
            if isinstance(errors, list):
                formatted_errors[field] = errors
            else:
                formatted_errors[field] = [str(errors)]
        
        return self.error_response(
            message="Validation failed",
            errors=formatted_errors,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR"
        )


def format_validation_errors(serializer_errors):
    """Format Django REST framework serializer errors"""
    formatted_errors = {}
    for field, errors in serializer_errors.items():
        if isinstance(errors, list):
            formatted_errors[field] = [str(error) for error in errors]
        else:
            formatted_errors[field] = [str(errors)]
    return formatted_errors


def log_api_request(request, response_data=None, error=None):
    """Log API request and response for debugging"""
    log_data = {
        'method': request.method,
        'path': request.path,
        'user': str(request.user) if request.user.is_authenticated else 'Anonymous',
        'ip': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
        'timestamp': timezone.now().isoformat(),
    }
    
    if hasattr(request, 'tenant') and request.tenant:
        log_data['tenant'] = request.tenant.subdomain
    
    if error:
        log_data['error'] = str(error)
        logger.error(f"API Error: {log_data}")
    else:
        logger.info(f"API Request: {log_data}")