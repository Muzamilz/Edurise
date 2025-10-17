"""
Standardized API response utilities for consistent response formatting.
"""
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone


class StandardAPIResponse:
    """
    Utility class for creating standardized API responses.
    """
    
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        """
        Create a successful API response.
        
        Args:
            data: The response data
            message: Success message
            status_code: HTTP status code
            
        Returns:
            Response: DRF Response object
        """
        response_data = {
            'success': True,
            'message': message,
            'data': data,
            'timestamp': timezone.now().isoformat()
        }
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(message="An error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        """
        Create an error API response.
        
        Args:
            message: Error message
            errors: Detailed error information
            status_code: HTTP status code
            
        Returns:
            Response: DRF Response object
        """
        response_data = {
            'success': False,
            'message': message,
            'errors': errors,
            'timestamp': timezone.now().isoformat()
        }
        return Response(response_data, status=status_code)
    
    @staticmethod
    def created(data=None, message="Created successfully"):
        """
        Create a successful creation response.
        
        Args:
            data: The created resource data
            message: Success message
            
        Returns:
            Response: DRF Response object
        """
        return StandardAPIResponse.success(
            data=data, 
            message=message, 
            status_code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def not_found(message="Resource not found"):
        """
        Create a not found response.
        
        Args:
            message: Not found message
            
        Returns:
            Response: DRF Response object
        """
        return StandardAPIResponse.error(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def unauthorized(message="Unauthorized access"):
        """
        Create an unauthorized response.
        
        Args:
            message: Unauthorized message
            
        Returns:
            Response: DRF Response object
        """
        return StandardAPIResponse.error(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(message="Access forbidden"):
        """
        Create a forbidden response.
        
        Args:
            message: Forbidden message
            
        Returns:
            Response: DRF Response object
        """
        return StandardAPIResponse.error(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def validation_error(errors, message="Validation failed"):
        """
        Create a validation error response.
        
        Args:
            errors: Validation error details
            message: Error message
            
        Returns:
            Response: DRF Response object
        """
        return StandardAPIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )