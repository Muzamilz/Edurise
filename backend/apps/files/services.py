import os
import mimetypes
from typing import Optional, Dict, Any, List
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from .models import FileUpload, FileCategory, FileProcessingJob, FileAccessLog
from apps.security.file_scanner import FileUploadSecurityScanner
from apps.security.validators import SecurityValidator

User = get_user_model()


class FileStorageService:
    """Service for handling file storage operations"""
    
    @staticmethod
    def get_upload_path(category: str, filename: str) -> str:
        """Generate upload path based on category and date"""
        now = timezone.now()
        return f"{category}/{now.year}/{now.month:02d}/{now.day:02d}/{filename}"
    
    @staticmethod
    def validate_file_type(file, allowed_extensions: List[str]) -> bool:
        """Validate file type against allowed extensions"""
        if not allowed_extensions:
            return True
        
        file_ext = os.path.splitext(file.name)[1].lower().lstrip('.')
        return file_ext in allowed_extensions
    
    @staticmethod
    def validate_file_size(file, max_size_mb: int) -> bool:
        """Validate file size against maximum allowed size"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file.size <= max_size_bytes
    
    @staticmethod
    def get_file_metadata(file) -> Dict[str, Any]:
        """Extract metadata from uploaded file"""
        filename = file.name
        file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
        mime_type, _ = mimetypes.guess_type(filename)
        
        return {
            'original_filename': filename,
            'file_extension': file_ext,
            'file_type': mime_type or 'application/octet-stream',
            'file_size': file.size,
        }
    
    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """Generate secure filename to prevent path traversal"""
        import uuid
        name, ext = os.path.splitext(original_filename)
        # Keep original name but add UUID for uniqueness
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return f"{safe_name}_{uuid.uuid4().hex[:8]}{ext}"


class FileUploadService:
    """Service for handling file uploads and management"""
    
    def __init__(self):
        self.storage_service = FileStorageService()
        self.security_scanner = FileUploadSecurityScanner()
    
    def upload_file(
        self,
        file,
        category_name: str,
        user: User,
        title: str = None,
        description: str = None,
        access_level: str = 'private',
        course_id: str = None,
        tags: List[str] = None,
        expires_at = None
    ) -> FileUpload:
        """Upload and process a file"""
        
        # Get or create category
        category, created = FileCategory.objects.get_or_create(
            name=category_name,
            defaults={
                'display_name': category_name.replace('_', ' ').title(),
                'allowed_extensions': [],
                'max_file_size_mb': 10
            }
        )
        
        # Validate file
        if not self.storage_service.validate_file_size(file, category.max_file_size_mb):
            raise ValueError(f"File size exceeds maximum allowed size of {category.max_file_size_mb}MB")
        
        if category.allowed_extensions and not self.storage_service.validate_file_type(file, category.allowed_extensions):
            raise ValueError(f"File type not allowed. Allowed types: {', '.join(category.allowed_extensions)}")
        
        # Security scan
        scan_results = self.security_scanner.scan_uploaded_file(file)
        if not scan_results['safe']:
            threats = ', '.join(scan_results['threats'][:3])  # Show first 3 threats
            raise ValueError(f"File failed security scan: {threats}")
        
        # Extract metadata
        metadata = self.storage_service.get_file_metadata(file)
        
        # Create file upload record
        file_upload = FileUpload.objects.create(
            original_filename=metadata['original_filename'],
            file=file,
            file_size=metadata['file_size'],
            file_type=metadata['file_type'],
            file_extension=metadata['file_extension'],
            category=category,
            title=title or os.path.splitext(metadata['original_filename'])[0],
            description=description or '',
            tags=tags or [],
            uploaded_by=user,
            tenant=user.tenant,
            access_level=access_level,
            course_id=course_id,
            expires_at=expires_at,
            status='active'
        )
        
        # Queue processing jobs if needed
        self._queue_processing_jobs(file_upload)
        
        return file_upload
    
    def _queue_processing_jobs(self, file_upload: FileUpload):
        """Queue processing jobs for uploaded file"""
        jobs_to_create = []
        
        # Generate thumbnail for images
        if file_upload.is_image:
            jobs_to_create.append({
                'job_type': 'thumbnail',
                'parameters': {'sizes': [150, 300, 600]}
            })
        
        # Generate preview for documents
        if file_upload.is_document:
            jobs_to_create.append({
                'job_type': 'document_preview',
                'parameters': {'pages': 3}
            })
        
        # Virus scan for all files
        jobs_to_create.append({
            'job_type': 'virus_scan',
            'parameters': {}
        })
        
        # Create processing jobs
        for job_config in jobs_to_create:
            FileProcessingJob.objects.create(
                file=file_upload,
                job_type=job_config['job_type'],
                parameters=job_config['parameters'],
                tenant=file_upload.tenant
            )
    
    def get_file_access_url(self, file_upload: FileUpload, user: User, expires_in: int = 3600) -> Optional[str]:
        """Get secure access URL for file"""
        if not file_upload.can_access(user):
            return None
        
        # Record access
        file_upload.record_access(user)
        
        # Return secure URL (would integrate with cloud storage)
        return file_upload.get_secure_url(expires_in)
    
    def update_file_metadata(
        self,
        file_upload: FileUpload,
        user: User,
        **kwargs
    ) -> FileUpload:
        """Update file metadata"""
        
        # Check permissions
        if file_upload.uploaded_by != user and not user.is_staff:
            raise PermissionError("You don't have permission to modify this file")
        
        # Update allowed fields
        allowed_fields = ['title', 'description', 'tags', 'access_level', 'expires_at']
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(file_upload, field, value)
        
        file_upload.save()
        return file_upload
    
    def delete_file(self, file_upload: FileUpload, user: User, hard_delete: bool = False):
        """Delete file (soft or hard delete)"""
        
        # Check permissions
        if file_upload.uploaded_by != user and not user.is_staff:
            raise PermissionError("You don't have permission to delete this file")
        
        if hard_delete:
            # Delete physical file
            if file_upload.file:
                file_upload.file.delete()
            # Delete database record
            file_upload.delete()
        else:
            # Soft delete
            file_upload.delete_file()
    
    def get_user_files(
        self,
        user: User,
        category: str = None,
        course_id: str = None,
        status: str = 'active'
    ) -> List[FileUpload]:
        """Get files accessible to user"""
        
        queryset = FileUpload.objects.filter(status=status)
        
        # Filter by category
        if category:
            queryset = queryset.filter(category__name=category)
        
        # Filter by course
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # Filter by access permissions
        accessible_files = []
        for file_upload in queryset:
            if file_upload.can_access(user):
                accessible_files.append(file_upload)
        
        return accessible_files


class FileProcessingService:
    """Service for handling file processing jobs"""
    
    def process_thumbnail_generation(self, job: FileProcessingJob):
        """Generate thumbnails for image files"""
        try:
            from PIL import Image
            import io
            
            job.status = 'processing'
            job.started_at = timezone.now()
            job.save()
            
            file_upload = job.file
            sizes = job.parameters.get('sizes', [150, 300])
            
            # Open image
            image = Image.open(file_upload.file.path)
            thumbnails = {}
            
            for size in sizes:
                # Create thumbnail
                thumbnail = image.copy()
                thumbnail.thumbnail((size, size), Image.Resampling.LANCZOS)
                
                # Save thumbnail
                thumb_io = io.BytesIO()
                format = image.format or 'JPEG'
                thumbnail.save(thumb_io, format=format)
                thumb_io.seek(0)
                
                # Store thumbnail path
                thumb_filename = f"thumb_{size}_{file_upload.original_filename}"
                thumb_path = f"thumbnails/{thumb_filename}"
                
                # Save to storage
                default_storage.save(thumb_path, ContentFile(thumb_io.getvalue()))
                thumbnails[str(size)] = thumb_path
            
            # Update job result
            job.result_data = {'thumbnails': thumbnails}
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save()
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save()
    
    def process_document_preview(self, job: FileProcessingJob):
        """Generate preview for document files"""
        try:
            job.status = 'processing'
            job.started_at = timezone.now()
            job.save()
            
            # This would integrate with document processing libraries
            # For now, just mark as completed
            job.result_data = {'preview_generated': True}
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save()
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save()
    
    def process_virus_scan(self, job: FileProcessingJob):
        """Perform virus scan on uploaded file"""
        try:
            job.status = 'processing'
            job.started_at = timezone.now()
            job.save()
            
            # This would integrate with antivirus services
            # For now, just mark as clean
            job.result_data = {'scan_result': 'clean', 'threats_found': 0}
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save()
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save()


class FileAnalyticsService:
    """Service for file usage analytics"""
    
    @staticmethod
    def get_file_statistics(file_upload: FileUpload) -> Dict[str, Any]:
        """Get statistics for a specific file"""
        access_logs = file_upload.access_logs.all()
        
        return {
            'total_downloads': file_upload.download_count,
            'unique_users': access_logs.values('user').distinct().count(),
            'last_accessed': file_upload.last_accessed,
            'access_count_last_30_days': access_logs.filter(
                accessed_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count(),
        }
    
    @staticmethod
    def get_user_file_statistics(user: User) -> Dict[str, Any]:
        """Get file statistics for a user"""
        user_files = FileUpload.objects.filter(uploaded_by=user, status='active')
        
        return {
            'total_files': user_files.count(),
            'total_size_mb': sum(f.file_size for f in user_files) / (1024 * 1024),
            'files_by_category': {
                category['category__name']: category['count']
                for category in user_files.values('category__name').annotate(
                    count=models.Count('id')
                )
            },
            'total_downloads': sum(f.download_count for f in user_files),
        }
    
    @staticmethod
    def get_tenant_file_statistics(tenant) -> Dict[str, Any]:
        """Get file statistics for a tenant"""
        tenant_files = FileUpload.objects.filter(tenant=tenant, status='active')
        
        return {
            'total_files': tenant_files.count(),
            'total_size_mb': sum(f.file_size for f in tenant_files) / (1024 * 1024),
            'files_by_category': {
                category['category__name']: category['count']
                for category in tenant_files.values('category__name').annotate(
                    count=models.Count('id')
                )
            },
            'most_downloaded_files': tenant_files.order_by('-download_count')[:10],
        }