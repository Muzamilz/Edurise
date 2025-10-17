from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.utils import timezone
from typing import Any, Dict, Optional, Union


class StandardAPIResponse:
    """
    Standardized API response format for consistent responses across all endpoints.
    
    This utility class provides methods to create consistent response formats
    with success indicators, timestamps, and proper error handling.
    """
    
    @staticmethod
    def success(
        data: Any = None, 
        message: Optional[str] = None, 
        status_code: int = status.HTTP_200_OK,
        meta: Optional[Dict] = None
    ) -> Response:
        """
        Create a standardized success response.
        
        Args:
            data: The response data
            message: Optional success message
            status_code: HTTP status code (default: 200)
            meta: Optional metadata dictionary
            
        Returns:
            Response object with standardized format
        """
        response_data = {
            'success': True,
            'data': data,
            'timestamp': timezone.now().isoformat()
        }
        
        if message:
            response_data['message'] = message
            
        if meta:
            response_data['meta'] = meta
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(
        message: str,
        errors: Optional[Union[Dict, list]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None
    ) -> Response:
        """
        Create a standardized error response.
        
        Args:
            message: Error message
            errors: Detailed error information
            status_code: HTTP status code (default: 400)
            error_code: Optional error code for client handling
            
        Returns:
            Response object with standardized error format
        """
        response_data = {
            'success': False,
            'message': message,
            'timestamp': timezone.now().isoformat()
        }
        
        if errors:
            response_data['errors'] = errors
            
        if error_code:
            response_data['error_code'] = error_code
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def validation_error(
        errors: Dict,
        message: str = "Validation failed",
        status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> Response:
        """
        Create a standardized validation error response.
        
        Args:
            errors: Dictionary of field validation errors
            message: Error message
            status_code: HTTP status code (default: 400)
            
        Returns:
            Response object with validation error format
        """
        return StandardAPIResponse.error(
            message=message,
            errors=errors,
            status_code=status_code,
            error_code='VALIDATION_ERROR'
        )
    
    @staticmethod
    def not_found(
        message: str = "Resource not found",
        resource_type: Optional[str] = None
    ) -> Response:
        """
        Create a standardized 404 not found response.
        
        Args:
            message: Error message
            resource_type: Type of resource that was not found
            
        Returns:
            Response object with 404 error format
        """
        error_data = {
            'message': message,
            'status_code': status.HTTP_404_NOT_FOUND,
            'error_code': 'NOT_FOUND'
        }
        
        if resource_type:
            error_data['resource_type'] = resource_type
            
        return StandardAPIResponse.error(**error_data)
    
    @staticmethod
    def permission_denied(
        message: str = "Permission denied",
        required_permission: Optional[str] = None
    ) -> Response:
        """
        Create a standardized 403 permission denied response.
        
        Args:
            message: Error message
            required_permission: The permission that was required
            
        Returns:
            Response object with 403 error format
        """
        error_data = {
            'message': message,
            'status_code': status.HTTP_403_FORBIDDEN,
            'error_code': 'PERMISSION_DENIED'
        }
        
        if required_permission:
            error_data['errors'] = {'required_permission': required_permission}
            
        return StandardAPIResponse.error(**error_data)
    
    @staticmethod
    def unauthorized(
        message: str = "Authentication required"
    ) -> Response:
        """
        Create a standardized 401 unauthorized response.
        
        Args:
            message: Error message
            
        Returns:
            Response object with 401 error format
        """
        return StandardAPIResponse.error(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code='UNAUTHORIZED'
        )
    
    @staticmethod
    def server_error(
        message: str = "Internal server error",
        error_id: Optional[str] = None
    ) -> Response:
        """
        Create a standardized 500 server error response.
        
        Args:
            message: Error message
            error_id: Optional error ID for tracking
            
        Returns:
            Response object with 500 error format
        """
        error_data = {
            'message': message,
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'error_code': 'SERVER_ERROR'
        }
        
        if error_id:
            error_data['errors'] = {'error_id': error_id}
            
        return StandardAPIResponse.error(**error_data)
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "Resource created successfully"
    ) -> Response:
        """
        Create a standardized 201 created response.
        
        Args:
            data: The created resource data
            message: Success message
            
        Returns:
            Response object with 201 status
        """
        return StandardAPIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def updated(
        data: Any = None,
        message: str = "Resource updated successfully"
    ) -> Response:
        """
        Create a standardized 200 updated response.
        
        Args:
            data: The updated resource data
            message: Success message
            
        Returns:
            Response object with 200 status
        """
        return StandardAPIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_200_OK
        )
    
    @staticmethod
    def deleted(
        message: str = "Resource deleted successfully"
    ) -> Response:
        """
        Create a standardized 204 deleted response.
        
        Args:
            message: Success message
            
        Returns:
            Response object with 204 status
        """
        return StandardAPIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    @staticmethod
    def bad_request(
        message: str = "Bad request",
        errors: Optional[Union[Dict, list]] = None
    ) -> Response:
        """
        Create a standardized 400 bad request response.
        
        Args:
            message: Error message
            errors: Detailed error information
            
        Returns:
            Response object with 400 error format
        """
        return StandardAPIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code='BAD_REQUEST'
        )
    
    @staticmethod
    def conflict(
        message: str = "Resource conflict",
        errors: Optional[Union[Dict, list]] = None
    ) -> Response:
        """
        Create a standardized 409 conflict response.
        
        Args:
            message: Error message
            errors: Detailed error information
            
        Returns:
            Response object with 409 error format
        """
        return StandardAPIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_409_CONFLICT,
            error_code='CONFLICT'
        )


class StandardPagination(PageNumberPagination):
    """
    Standardized pagination class with consistent response format.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Return a paginated response with standardized format.
        """
        return StandardAPIResponse.success(
            data=data,
            meta={
                'pagination': {
                    'current_page': self.page.number,
                    'total_pages': self.page.paginator.num_pages,
                    'page_size': self.get_page_size(self.request),
                    'total_count': self.page.paginator.count,
                    'has_next': self.page.has_next(),
                    'has_previous': self.page.has_previous(),
                    'next_page': self.page.next_page_number() if self.page.has_next() else None,
                    'previous_page': self.page.previous_page_number() if self.page.has_previous() else None,
                }
            }
        )


class APIResponseMixin:
    """
    Mixin to add standardized response methods to ViewSets.
    """
    
    def success_response(self, data=None, message=None, status_code=status.HTTP_200_OK):
        """Create a success response using StandardAPIResponse"""
        return StandardAPIResponse.success(data, message, status_code)
    
    def error_response(self, message, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Create an error response using StandardAPIResponse"""
        return StandardAPIResponse.error(message, errors, status_code)
    
    def validation_error_response(self, errors, message="Validation failed"):
        """Create a validation error response"""
        return StandardAPIResponse.validation_error(errors, message)
    
    def not_found_response(self, message="Resource not found", resource_type=None):
        """Create a not found response"""
        return StandardAPIResponse.not_found(message, resource_type)
    
    def permission_denied_response(self, message="Permission denied", required_permission=None):
        """Create a permission denied response"""
        return StandardAPIResponse.permission_denied(message, required_permission)
    
    def created_response(self, data=None, message="Resource created successfully"):
        """Create a created response using StandardAPIResponse"""
        return StandardAPIResponse.created(data, message)
    
    def updated_response(self, data=None, message="Resource updated successfully"):
        """Create an updated response using StandardAPIResponse"""
        return StandardAPIResponse.updated(data, message)
    
    def deleted_response(self, message="Resource deleted successfully"):
        """Create a deleted response using StandardAPIResponse"""
        return StandardAPIResponse.deleted(message)
    
    def bad_request_response(self, message="Bad request", errors=None):
        """Create a bad request response using StandardAPIResponse"""
        return StandardAPIResponse.bad_request(message, errors)
    
    def conflict_response(self, message="Resource conflict", errors=None):
        """Create a conflict response using StandardAPIResponse"""
        return StandardAPIResponse.conflict(message, errors)