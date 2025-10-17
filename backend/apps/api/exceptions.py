from rest_framework.views import exception_handler
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError
from .responses import StandardAPIResponse
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns standardized API responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If the default handler didn't handle the exception, handle it ourselves
    if response is None:
        return handle_unhandled_exception(exc, context)
    
    # Convert DRF responses to our standardized format
    return convert_to_standard_response(exc, response, context)


def handle_unhandled_exception(exc, context):
    """Handle exceptions not handled by DRF's default handler"""
    
    if isinstance(exc, Http404):
        return StandardAPIResponse.not_found(
            message="The requested resource was not found"
        )
    
    elif isinstance(exc, PermissionDenied):
        return StandardAPIResponse.permission_denied(
            message=str(exc) if str(exc) else "Permission denied"
        )
    
    elif isinstance(exc, ValidationError):
        return StandardAPIResponse.validation_error(
            errors={'validation_error': exc.messages if hasattr(exc, 'messages') else [str(exc)]},
            message="Validation failed"
        )
    
    else:
        # Log unexpected exceptions
        logger.exception(f"Unhandled exception in API: {type(exc).__name__}: {str(exc)}")
        
        return StandardAPIResponse.server_error(
            message="An unexpected error occurred",
            error_id=f"err_{int(__import__('time').time())}"
        )


def convert_to_standard_response(exc, response, context):
    """Convert DRF response to standardized format"""
    
    # Get the original response data
    original_data = response.data
    status_code = response.status_code
    
    # Determine error message and details
    if isinstance(original_data, dict):
        # Handle different types of DRF error responses
        if 'detail' in original_data:
            message = original_data['detail']
            errors = {k: v for k, v in original_data.items() if k != 'detail'} if len(original_data) > 1 else None
        elif 'non_field_errors' in original_data:
            message = "Validation failed"
            errors = original_data
        else:
            message = "Request failed"
            errors = original_data
    elif isinstance(original_data, list):
        message = "Request failed"
        errors = {'errors': original_data}
    else:
        message = str(original_data) if original_data else "Request failed"
        errors = None
    
    # Map status codes to appropriate response methods
    if status_code == status.HTTP_400_BAD_REQUEST:
        if errors and any(field in errors for field in ['non_field_errors', 'field_errors']):
            return StandardAPIResponse.validation_error(errors, message)
        else:
            return StandardAPIResponse.error(message, errors, status_code)
    
    elif status_code == status.HTTP_401_UNAUTHORIZED:
        return StandardAPIResponse.unauthorized(message)
    
    elif status_code == status.HTTP_403_FORBIDDEN:
        return StandardAPIResponse.permission_denied(message)
    
    elif status_code == status.HTTP_404_NOT_FOUND:
        return StandardAPIResponse.not_found(message)
    
    elif status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        return StandardAPIResponse.error(
            message="Method not allowed",
            errors={'allowed_methods': response.get('Allow', '').split(', ')} if response.get('Allow') else None,
            status_code=status_code
        )
    
    elif status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        return StandardAPIResponse.error(
            message="Rate limit exceeded",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status_code
        )
    
    elif status_code >= 500:
        return StandardAPIResponse.server_error(
            message=message if message != "Request failed" else "Internal server error"
        )
    
    else:
        # For any other status codes, use generic error response
        return StandardAPIResponse.error(message, errors, status_code)


class APIException(Exception):
    """Base exception class for API-specific exceptions"""
    default_message = "An API error occurred"
    default_code = "API_ERROR"
    status_code = status.HTTP_400_BAD_REQUEST
    
    def __init__(self, message=None, code=None, status_code=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class ValidationException(APIException):
    """Exception for validation errors"""
    default_message = "Validation failed"
    default_code = "VALIDATION_ERROR"
    status_code = status.HTTP_400_BAD_REQUEST
    
    def __init__(self, errors, message=None):
        self.errors = errors
        super().__init__(message)


class PermissionException(APIException):
    """Exception for permission errors"""
    default_message = "Permission denied"
    default_code = "PERMISSION_DENIED"
    status_code = status.HTTP_403_FORBIDDEN


class ResourceNotFoundException(APIException):
    """Exception for resource not found errors"""
    default_message = "Resource not found"
    default_code = "NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND
    
    def __init__(self, resource_type=None, message=None):
        self.resource_type = resource_type
        if resource_type and not message:
            message = f"{resource_type} not found"
        super().__init__(message)


class BusinessLogicException(APIException):
    """Exception for business logic violations"""
    default_message = "Business rule violation"
    default_code = "BUSINESS_LOGIC_ERROR"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class ExternalServiceException(APIException):
    """Exception for external service failures"""
    default_message = "External service unavailable"
    default_code = "EXTERNAL_SERVICE_ERROR"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    def __init__(self, service_name=None, message=None):
        self.service_name = service_name
        if service_name and not message:
            message = f"{service_name} service is currently unavailable"
        super().__init__(message)