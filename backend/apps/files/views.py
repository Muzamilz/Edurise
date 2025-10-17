from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.api.responses import StandardAPIResponse
# Tenant filtering is handled in get_queryset methods
from .models import FileCategory, FileUpload, FileAccessLog, FileProcessingJob
from .serializers import (
    FileCategorySerializer, FileUploadSerializer, FileUploadCreateSerializer,
    FileUploadListSerializer, FileUploadUpdateSerializer, FileAccessLogSerializer,
    FileProcessingJobSerializer
)
from .services import FileUploadService, FileAnalyticsService


class FileCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for file categories"""
    
    queryset = FileCategory.objects.all()
    serializer_class = FileCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """List all file categories"""
        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)
        
        return StandardAPIResponse.success(
            data=serializer.data,
            message="File categories retrieved successfully"
        )


class FileUploadViewSet(viewsets.ModelViewSet):
    """ViewSet for file uploads with comprehensive file management"""
    
    queryset = FileUpload.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category__name', 'access_level', 'status', 'course']
    search_fields = ['original_filename', 'title', 'description']
    ordering_fields = ['created_at', 'file_size', 'download_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return FileUploadCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FileUploadUpdateSerializer
        elif self.action == 'list':
            return FileUploadListSerializer
        return FileUploadSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        queryset = FileUpload.objects.filter(tenant=user.tenant)
        
        # Filter by access permissions
        if not user.is_staff:
            # Users can see their own files and files they have access to
            accessible_files = []
            for file_upload in queryset:
                if file_upload.can_access(user):
                    accessible_files.append(file_upload.id)
            
            queryset = queryset.filter(id__in=accessible_files)
        
        return queryset
    
    def create(self, request):
        """Upload a new file"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Use service to handle file upload
            file_service = FileUploadService()
            file_upload = file_service.upload_file(
                file=serializer.validated_data['file'],
                category_name=serializer.validated_data['category'].name,
                user=request.user,
                title=serializer.validated_data.get('title'),
                description=serializer.validated_data.get('description'),
                access_level=serializer.validated_data.get('access_level', 'private'),
                course_id=serializer.validated_data.get('course_id'),
                tags=serializer.validated_data.get('tags', []),
                expires_at=serializer.validated_data.get('expires_at')
            )
            
            # Return detailed response
            response_serializer = FileUploadSerializer(file_upload, context={'request': request})
            
            return StandardAPIResponse.success(
                data=response_serializer.data,
                message="File uploaded successfully",
                status_code=status.HTTP_201_CREATED
            )
            
        except ValueError as e:
            return StandardAPIResponse.error(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return StandardAPIResponse.error(
                message="File upload failed",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list(self, request):
        """List files with filtering and pagination"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Files retrieved successfully"
        )
    
    def retrieve(self, request, pk=None):
        """Get file details"""
        file_upload = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check access permissions
        if not file_upload.can_access(request.user):
            raise PermissionDenied("You don't have permission to access this file")
        
        serializer = self.get_serializer(file_upload)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="File details retrieved successfully"
        )
    
    def update(self, request, pk=None):
        """Update file metadata"""
        file_upload = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check permissions
        if file_upload.uploaded_by != request.user and not request.user.is_staff:
            raise PermissionDenied("You don't have permission to modify this file")
        
        serializer = self.get_serializer(file_upload, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return StandardAPIResponse.success(
            data=serializer.data,
            message="File updated successfully"
        )
    
    def destroy(self, request, pk=None):
        """Delete file (soft delete)"""
        file_upload = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check permissions
        if file_upload.uploaded_by != request.user and not request.user.is_staff:
            raise PermissionDenied("You don't have permission to delete this file")
        
        # Use service for deletion
        file_service = FileUploadService()
        file_service.delete_file(file_upload, request.user, hard_delete=False)
        
        return StandardAPIResponse.success(
            message="File deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download file with access control"""
        file_upload = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check access permissions
        if not file_upload.can_access(request.user):
            raise PermissionDenied("You don't have permission to access this file")
        
        # Check if file exists and is not deleted
        if file_upload.status == 'deleted' or not file_upload.file:
            raise Http404("File not found")
        
        # Record access
        file_upload.record_access(request.user)
        
        # Return file response
        try:
            response = HttpResponse(
                file_upload.file.read(),
                content_type=file_upload.file_type
            )
            response['Content-Disposition'] = f'attachment; filename="{file_upload.original_filename}"'
            response['Content-Length'] = file_upload.file_size
            return response
        except Exception:
            raise Http404("File not found")
    
    @action(detail=True, methods=['get'])
    def secure_url(self, request, pk=None):
        """Get secure URL for file access with enhanced access control"""
        from .access_control_service import FileAccessControlService
        
        file_upload = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Use enhanced access control service
        access_service = FileAccessControlService()
        expires_in = int(request.query_params.get('expires_in', 3600))
        
        # Get client IP for additional security
        client_ip = self.get_client_ip(request)
        
        secure_url = access_service.generate_secure_url(
            file_upload=file_upload,
            user=request.user,
            expires_in=expires_in,
            request_ip=client_ip
        )
        
        if not secure_url:
            # Get detailed access result for better error message
            access_result = access_service.check_file_access(file_upload, request.user, client_ip)
            
            error_data = {
                'reason': access_result.get('reason', 'Access denied'),
                'restrictions': access_result.get('restrictions', []),
                'subscription_required': access_result.get('subscription_required', False)
            }
            
            if access_result.get('upgrade_url'):
                error_data['upgrade_url'] = access_result['upgrade_url']
            
            return StandardAPIResponse.error(
                message="Access denied",
                errors=error_data,
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        return StandardAPIResponse.success(
            data={'secure_url': secure_url, 'expires_in': expires_in},
            message="Secure URL generated successfully"
        )
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get file usage statistics"""
        file_upload = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check permissions (owner or staff)
        if file_upload.uploaded_by != request.user and not request.user.is_staff:
            raise PermissionDenied("You don't have permission to view file statistics")
        
        stats = FileAnalyticsService.get_file_statistics(file_upload)
        
        return StandardAPIResponse.success(
            data=stats,
            message="File statistics retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def my_files(self, request):
        """Get current user's uploaded files"""
        user_files = FileUpload.objects.filter(
            uploaded_by=request.user,
            tenant=request.user.tenant,
            status='active'
        ).order_by('-created_at')
        
        # Apply filters
        category = request.query_params.get('category')
        if category:
            user_files = user_files.filter(category__name=category)
        
        page = self.paginate_queryset(user_files)
        if page is not None:
            serializer = FileUploadListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = FileUploadListSerializer(user_files, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Your files retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def course_files(self, request):
        """Get files for a specific course"""
        course_id = request.query_params.get('course_id')
        if not course_id:
            return StandardAPIResponse.error(
                message="course_id parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Get files for the course that user can access
        course_files = []
        queryset = FileUpload.objects.filter(
            course_id=course_id,
            tenant=request.user.tenant,
            status='active'
        )
        
        for file_upload in queryset:
            if file_upload.can_access(request.user):
                course_files.append(file_upload)
        
        serializer = FileUploadListSerializer(course_files, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Course files retrieved successfully"
        )
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share file with specific users"""
        from .access_control_service import FileAccessControlService
        
        file_upload = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Get target users from request
        user_emails = request.data.get('user_emails', [])
        if not user_emails:
            return StandardAPIResponse.validation_error(
                errors={'user_emails': ['This field is required']},
                message="User emails are required for sharing"
            )
        
        try:
            # Get target users
            target_users = User.objects.filter(email__in=user_emails)
            
            # Check sharing permissions
            access_service = FileAccessControlService()
            sharing_result = access_service.check_file_sharing_permissions(
                file_upload, request.user, list(target_users)
            )
            
            if not sharing_result['can_share']:
                error_data = {
                    'reason': sharing_result['reason'],
                    'denied_users': sharing_result['denied_users']
                }
                
                if sharing_result.get('upgrade_url'):
                    error_data['upgrade_url'] = sharing_result['upgrade_url']
                
                return StandardAPIResponse.error(
                    message="File sharing not allowed",
                    errors=error_data,
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Add users to allowed_users
            for user_data in sharing_result['allowed_users']:
                user = User.objects.get(id=user_data['user_id'])
                file_upload.allowed_users.add(user)
            
            return StandardAPIResponse.success(
                data={
                    'shared_with': sharing_result['allowed_users'],
                    'denied_users': sharing_result['denied_users']
                },
                message="File shared successfully"
            )
        
        except Exception as e:
            return StandardAPIResponse.error(
                message="File sharing failed",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def unshare(self, request, pk=None):
        """Remove file sharing for specific users"""
        file_upload = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check permissions
        if file_upload.uploaded_by != request.user and not request.user.is_staff:
            raise PermissionDenied("You don't have permission to modify file sharing")
        
        user_emails = request.data.get('user_emails', [])
        if not user_emails:
            return StandardAPIResponse.validation_error(
                errors={'user_emails': ['This field is required']},
                message="User emails are required"
            )
        
        try:
            # Remove users from allowed_users
            users_to_remove = User.objects.filter(email__in=user_emails)
            for user in users_to_remove:
                file_upload.allowed_users.remove(user)
            
            return StandardAPIResponse.success(
                message="File sharing removed successfully"
            )
        
        except Exception as e:
            return StandardAPIResponse.error(
                message="Failed to remove file sharing",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def shared_users(self, request, pk=None):
        """Get list of users file is shared with"""
        file_upload = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check permissions
        if file_upload.uploaded_by != request.user and not request.user.is_staff:
            raise PermissionDenied("You don't have permission to view file sharing details")
        
        shared_users = file_upload.allowed_users.all()
        user_data = [
            {
                'id': str(user.id),
                'email': user.email,
                'name': user.get_full_name() or user.email,
                'shared_at': file_upload.created_at  # This could be enhanced with actual sharing timestamp
            }
            for user in shared_users
        ]
        
        return StandardAPIResponse.success(
            data=user_data,
            message="Shared users retrieved successfully"
        )
    
    @action(detail=True, methods=['post'])
    def set_access_level(self, request, pk=None):
        """Update file access level with subscription plan validation"""
        from .access_control_service import FileAccessControlService
        
        file_upload = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Check permissions
        if file_upload.uploaded_by != request.user and not request.user.is_staff:
            raise PermissionDenied("You don't have permission to modify file access level")
        
        new_access_level = request.data.get('access_level')
        if not new_access_level:
            return StandardAPIResponse.validation_error(
                errors={'access_level': ['This field is required']},
                message="Access level is required"
            )
        
        # Validate access level
        valid_levels = [choice[0] for choice in FileUpload.ACCESS_LEVEL_CHOICES]
        if new_access_level not in valid_levels:
            return StandardAPIResponse.validation_error(
                errors={'access_level': [f'Invalid access level. Must be one of: {", ".join(valid_levels)}']},
                message="Invalid access level"
            )
        
        # Check subscription plan restrictions
        access_service = FileAccessControlService()
        user_org = getattr(request.user, 'tenant', None)
        
        if user_org and user_org.subscription_plan == 'basic':
            # Basic plan restrictions
            if new_access_level in ['public', 'tenant']:
                return StandardAPIResponse.error(
                    message="Public and tenant-wide sharing requires Pro or Enterprise plan",
                    errors={
                        'subscription_required': True,
                        'upgrade_url': access_service.get_subscription_upgrade_url(request.user)
                    },
                    status_code=status.HTTP_403_FORBIDDEN
                )
        
        # Update access level
        file_upload.access_level = new_access_level
        file_upload.save()
        
        serializer = self.get_serializer(file_upload)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="File access level updated successfully"
        )


class FileAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for file access logs"""
    
    queryset = FileAccessLog.objects.all()
    serializer_class = FileAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['file', 'user']
    ordering = ['-accessed_at']
    
    def get_queryset(self):
        """Filter access logs based on user permissions"""
        user = self.request.user
        queryset = FileAccessLog.objects.filter(tenant=user.tenant)
        
        # Non-staff users can only see logs for their own files
        if not user.is_staff:
            queryset = queryset.filter(file__uploaded_by=user)
        
        return queryset
    
    def list(self, request):
        """List file access logs"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Access logs retrieved successfully"
        )


class FileProcessingJobViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for file processing jobs"""
    
    queryset = FileProcessingJob.objects.all()
    serializer_class = FileProcessingJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['file', 'job_type', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter processing jobs based on user permissions"""
        user = self.request.user
        queryset = FileProcessingJob.objects.filter(tenant=user.tenant)
        
        # Non-staff users can only see jobs for their own files
        if not user.is_staff:
            queryset = queryset.filter(file__uploaded_by=user)
        
        return queryset
    
    def list(self, request):
        """List file processing jobs"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Processing jobs retrieved successfully"
        )


class SecureFileDownloadView(APIView):
    """Secure file download with access control and token verification"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, file_id):
        """Handle secure file download with token verification"""
        from .access_control_service import FileAccessControlService
        
        try:
            file_upload = get_object_or_404(FileUpload, id=file_id)
            
            # Get token and expiry from query params
            token = request.query_params.get('token')
            expires = request.query_params.get('expires')
            
            if not token or not expires:
                return StandardAPIResponse.error(
                    message="Missing security token or expiry",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Initialize access control service
            access_service = FileAccessControlService()
            
            # Get client IP
            client_ip = self.get_client_ip(request)
            
            # Verify token
            token_result = access_service.verify_secure_token(
                file_id=file_id,
                token=token,
                expires=expires,
                user=request.user,
                request_ip=client_ip
            )
            
            if not token_result['valid']:
                access_service.log_file_access(
                    file_upload=file_upload,
                    user=request.user,
                    request_ip=client_ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    access_granted=False
                )
                
                return StandardAPIResponse.error(
                    message=f"Invalid token: {token_result['reason']}",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Double-check file access permissions
            access_result = access_service.check_file_access(file_upload, request.user, client_ip)
            
            if not access_result['allowed']:
                access_service.log_file_access(
                    file_upload=file_upload,
                    user=request.user,
                    request_ip=client_ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    access_granted=False
                )
                
                return StandardAPIResponse.error(
                    message=f"Access denied: {access_result['reason']}",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Log successful access
            access_service.log_file_access(
                file_upload=file_upload,
                user=request.user,
                request_ip=client_ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                access_granted=True
            )
            
            # Serve file
            try:
                response = HttpResponse(
                    file_upload.file.read(),
                    content_type=file_upload.file_type
                )
                response['Content-Disposition'] = f'attachment; filename="{file_upload.original_filename}"'
                response['Content-Length'] = file_upload.file_size
                response['X-Accel-Redirect'] = f'/protected/{file_upload.file.name}'  # For nginx
                return response
                
            except Exception as e:
                return StandardAPIResponse.error(
                    message="File not found or corrupted",
                    status_code=status.HTTP_404_NOT_FOUND
                )
        
        except FileUpload.DoesNotExist:
            return StandardAPIResponse.error(
                message="File not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return StandardAPIResponse.error(
                message="Download failed",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class FilePermissionsView(APIView):
    """View for checking file permissions"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, file_id):
        """Get file permissions for current user"""
        from .access_control_service import FileAccessControlService
        
        try:
            file_upload = get_object_or_404(FileUpload, id=file_id)
            
            access_service = FileAccessControlService()
            permissions = access_service.get_user_file_permissions(request.user, file_upload)
            
            return StandardAPIResponse.success(
                data=permissions,
                message="File permissions retrieved successfully"
            )
        
        except FileUpload.DoesNotExist:
            return StandardAPIResponse.error(
                message="File not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    def post(self, request):
        """Bulk check permissions for multiple files"""
        from .access_control_service import FileAccessControlService
        
        file_ids = request.data.get('file_ids', [])
        
        if not file_ids:
            return StandardAPIResponse.validation_error(
                errors={'file_ids': ['This field is required']},
                message="File IDs are required"
            )
        
        try:
            file_uploads = FileUpload.objects.filter(id__in=file_ids)
            
            access_service = FileAccessControlService()
            results = access_service.bulk_check_access(list(file_uploads), request.user)
            
            return StandardAPIResponse.success(
                data=results,
                message="Bulk permissions check completed"
            )
        
        except Exception as e:
            return StandardAPIResponse.error(
                message="Permissions check failed",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )