"""
Service for integrating existing file uploads with the centralized file management system.
This service helps migrate and connect existing file fields to the new centralized system.
"""

import os
from typing import Optional, Dict, Any
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import FileUpload, FileCategory
from .services import FileUploadService

User = get_user_model()


class FileIntegrationService:
    """Service for integrating existing files with centralized system"""
    
    def __init__(self):
        self.upload_service = FileUploadService()
    
    def migrate_assignment_submission(self, submission, user: User) -> Optional[FileUpload]:
        """Migrate assignment submission file to centralized system"""
        if not submission.file_upload or submission.uploaded_file:
            return submission.uploaded_file
        
        try:
            # Get or create category
            category, _ = FileCategory.objects.get_or_create(
                name='assignment_submission',
                defaults={
                    'display_name': 'Assignment Submission',
                    'allowed_extensions': ['pdf', 'doc', 'docx', 'txt', 'py', 'js', 'java', 'cpp', 'zip'],
                    'max_file_size_mb': 25
                }
            )
            
            # Create centralized file upload
            file_upload = FileUpload.objects.create(
                original_filename=os.path.basename(submission.file_upload.name),
                file=submission.file_upload,
                file_size=submission.file_upload.size,
                file_type=getattr(submission.file_upload.file, 'content_type', 'application/octet-stream'),
                file_extension=os.path.splitext(submission.file_upload.name)[1].lower().lstrip('.'),
                category=category,
                title=f"Assignment Submission - {submission.assignment.title}",
                description=f"Submission by {user.get_full_name() or user.email}",
                uploaded_by=user,
                tenant=user.tenant,
                access_level='instructor',  # Only instructor can access
                course=submission.assignment.course,
                status='active'
            )
            
            # Update submission to reference centralized file
            submission.uploaded_file = file_upload
            submission.save()
            
            return file_upload
            
        except Exception as e:
            print(f"Error migrating assignment submission file: {e}")
            return None
    
    def migrate_certificate_file(self, certificate, user: User) -> Optional[FileUpload]:
        """Migrate certificate PDF to centralized system"""
        if not certificate.pdf_file or certificate.certificate_file:
            return certificate.certificate_file
        
        try:
            # Get or create category
            category, _ = FileCategory.objects.get_or_create(
                name='certificate',
                defaults={
                    'display_name': 'Certificate',
                    'allowed_extensions': ['pdf'],
                    'max_file_size_mb': 5
                }
            )
            
            # Create centralized file upload
            file_upload = FileUpload.objects.create(
                original_filename=os.path.basename(certificate.pdf_file.name),
                file=certificate.pdf_file,
                file_size=certificate.pdf_file.size,
                file_type='application/pdf',
                file_extension='pdf',
                category=category,
                title=f"Certificate - {certificate.course.title}",
                description=f"Certificate for {user.get_full_name() or user.email}",
                uploaded_by=user,  # System user or certificate owner
                tenant=user.tenant,
                access_level='private',  # Only certificate owner can access
                course=certificate.course,
                status='active'
            )
            
            # Update certificate to reference centralized file
            certificate.certificate_file = file_upload
            certificate.save()
            
            return file_upload
            
        except Exception as e:
            print(f"Error migrating certificate file: {e}")
            return None
    
    def migrate_course_thumbnail(self, course, user: User) -> Optional[FileUpload]:
        """Migrate course thumbnail to centralized system"""
        if not course.thumbnail or course.thumbnail_file:
            return course.thumbnail_file
        
        try:
            # Get or create category
            category, _ = FileCategory.objects.get_or_create(
                name='course_thumbnail',
                defaults={
                    'display_name': 'Course Thumbnail',
                    'allowed_extensions': ['jpg', 'jpeg', 'png'],
                    'max_file_size_mb': 5
                }
            )
            
            # Create centralized file upload
            file_upload = FileUpload.objects.create(
                original_filename=os.path.basename(course.thumbnail.name),
                file=course.thumbnail,
                file_size=course.thumbnail.size,
                file_type=getattr(course.thumbnail.file, 'content_type', 'image/jpeg'),
                file_extension=os.path.splitext(course.thumbnail.name)[1].lower().lstrip('.'),
                category=category,
                title=f"Thumbnail - {course.title}",
                description=f"Course thumbnail for {course.title}",
                uploaded_by=user,  # Course instructor
                tenant=user.tenant,
                access_level='public',  # Public access for thumbnails
                course=course,
                status='active'
            )
            
            # Update course to reference centralized file
            course.thumbnail_file = file_upload
            course.save()
            
            return file_upload
            
        except Exception as e:
            print(f"Error migrating course thumbnail: {e}")
            return None
    
    def create_course_material_upload(
        self, 
        file, 
        course, 
        user: User, 
        title: str = None,
        description: str = None
    ) -> Optional[FileUpload]:
        """Create a new course material upload through centralized system"""
        try:
            return self.upload_service.upload_file(
                file=file,
                category_name='course_material',
                user=user,
                title=title or f"Course Material - {course.title}",
                description=description or f"Material for {course.title}",
                access_level='enrolled',  # Only enrolled students can access
                course_id=str(course.id),
                tags=['course-material', course.category]
            )
        except Exception as e:
            print(f"Error creating course material upload: {e}")
            return None
    
    def create_assignment_submission_upload(
        self,
        file,
        assignment,
        user: User,
        title: str = None,
        description: str = None
    ) -> Optional[FileUpload]:
        """Create a new assignment submission through centralized system"""
        try:
            return self.upload_service.upload_file(
                file=file,
                category_name='assignment_submission',
                user=user,
                title=title or f"Submission - {assignment.title}",
                description=description or f"Assignment submission for {assignment.title}",
                access_level='instructor',  # Only instructor can access
                course_id=str(assignment.course.id),
                tags=['assignment-submission', assignment.assignment_type]
            )
        except Exception as e:
            print(f"Error creating assignment submission upload: {e}")
            return None
    
    def get_file_access_url(self, file_upload: FileUpload, user: User) -> Optional[str]:
        """Get secure access URL for file through centralized system"""
        return self.upload_service.get_file_access_url(file_upload, user)
    
    def get_course_files(self, course, user: User, category: str = None) -> list:
        """Get all files for a course that user can access"""
        return self.upload_service.get_user_files(
            user=user,
            category=category,
            course_id=str(course.id)
        )
    
    def migrate_existing_files_batch(self, batch_size: int = 100):
        """Migrate existing files in batches"""
        from apps.assignments.models import Submission, Certificate
        from apps.courses.models import Course
        
        results = {
            'submissions_migrated': 0,
            'certificates_migrated': 0,
            'thumbnails_migrated': 0,
            'errors': []
        }
        
        # Migrate assignment submissions
        submissions = Submission.objects.filter(
            file_upload__isnull=False,
            uploaded_file__isnull=True
        )[:batch_size]
        
        for submission in submissions:
            try:
                if self.migrate_assignment_submission(submission, submission.student):
                    results['submissions_migrated'] += 1
            except Exception as e:
                results['errors'].append(f"Submission {submission.id}: {e}")
        
        # Migrate certificates
        certificates = Certificate.objects.filter(
            pdf_file__isnull=False,
            certificate_file__isnull=True
        )[:batch_size]
        
        for certificate in certificates:
            try:
                if self.migrate_certificate_file(certificate, certificate.student):
                    results['certificates_migrated'] += 1
            except Exception as e:
                results['errors'].append(f"Certificate {certificate.id}: {e}")
        
        # Migrate course thumbnails
        courses = Course.objects.filter(
            thumbnail__isnull=False,
            thumbnail_file__isnull=True
        )[:batch_size]
        
        for course in courses:
            try:
                if self.migrate_course_thumbnail(course, course.instructor):
                    results['thumbnails_migrated'] += 1
            except Exception as e:
                results['errors'].append(f"Course {course.id}: {e}")
        
        return results