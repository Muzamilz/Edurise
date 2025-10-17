from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Assignment, Submission, Certificate, CourseProgress
from .serializers import (
    AssignmentSerializer, AssignmentDetailSerializer, SubmissionSerializer,
    SubmissionCreateSerializer, SubmissionGradeSerializer, CertificateSerializer,
    CourseProgressSerializer, CourseCompletionAnalyticsSerializer
)
from .services import AssignmentService, SubmissionService, CertificateService, CourseProgressService
from apps.files.certificate_service import CertificateGenerationService
from apps.files.integration_service import FileIntegrationService
from .filters import AssignmentFilter, SubmissionFilter, CertificateFilter
from apps.api.responses import StandardAPIResponse
from apps.api.mixins import StandardViewSetMixin
from apps.courses.models import Course, Enrollment

User = get_user_model()


class AssignmentViewSet(StandardViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Assignment model with comprehensive assignment management"""
    
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AssignmentFilter
    search_fields = ['title', 'description', 'instructions']
    ordering_fields = ['created_at', 'due_date', 'title', 'max_score']
    ordering = ['due_date', '-created_at']
    
    # Query optimization fields
    select_related_fields = ['course', 'course__instructor', 'tenant']
    prefetch_related_fields = ['submissions', 'submissions__student']
    
    def get_queryset(self):
        """Filter assignments by tenant and user permissions"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Assignment.objects.filter(tenant=self.request.tenant)
            
            # Filter based on user role
            if not self.request.user.is_staff:
                if self.request.user.is_teacher:
                    # Teachers see assignments for their courses
                    queryset = queryset.filter(course__instructor=self.request.user)
                else:
                    # Students see assignments for courses they're enrolled in
                    enrolled_courses = Enrollment.objects.filter(
                        student=self.request.user,
                        tenant=self.request.tenant
                    ).values_list('course_id', flat=True)
                    queryset = queryset.filter(
                        course_id__in=enrolled_courses,
                        status='published'
                    )
            
            return queryset.select_related(*self.select_related_fields).prefetch_related(*self.prefetch_related_fields)
        
        return Assignment.objects.none()
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return AssignmentDetailSerializer
        return AssignmentSerializer
    
    def perform_create(self, serializer):
        """Set tenant when creating assignment and validate instructor permissions"""
        course = serializer.validated_data['course']
        
        # Check if user is instructor of the course or admin
        if course.instructor != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Only course instructors can create assignments")
        
        serializer.save(tenant=self.request.tenant)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish an assignment"""
        assignment = self.get_object()
        
        # Check permissions
        if assignment.course.instructor != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="Only course instructors can publish assignments"
            )
        
        assignment.publish()
        
        return StandardAPIResponse.success(
            data=self.get_serializer(assignment).data,
            message="Assignment published successfully"
        )
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close an assignment for submissions"""
        assignment = self.get_object()
        
        # Check permissions
        if assignment.course.instructor != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="Only course instructors can close assignments"
            )
        
        assignment.close()
        
        return StandardAPIResponse.success(
            data=self.get_serializer(assignment).data,
            message="Assignment closed successfully"
        )
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get detailed statistics for an assignment"""
        assignment = self.get_object()
        
        # Check permissions
        if assignment.course.instructor != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="Only course instructors and administrators can view assignment statistics"
            )
        
        stats = AssignmentService.get_assignment_statistics(assignment)
        
        return StandardAPIResponse.success(
            data=stats,
            message="Assignment statistics retrieved successfully"
        )
    
    @action(detail=True, methods=['post'])
    def bulk_grade(self, request, pk=None):
        """Bulk grade multiple submissions for an assignment"""
        assignment = self.get_object()
        
        # Check permissions
        if assignment.course.instructor != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="Only course instructors can grade assignments"
            )
        
        grades_data = request.data.get('grades', [])
        if not grades_data:
            return StandardAPIResponse.validation_error(
                errors={'grades': ['This field is required']},
                message="Grades data is required for bulk grading"
            )
        
        updated_submissions = AssignmentService.bulk_grade_submissions(
            assignment=assignment,
            grades_data=grades_data,
            graded_by=request.user
        )
        
        return StandardAPIResponse.success(
            data={'graded_count': len(updated_submissions)},
            message=f"Successfully graded {len(updated_submissions)} submissions"
        )
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming assignments for the current user"""
        now = timezone.now()
        
        if request.user.is_teacher:
            # Teachers see upcoming assignments for their courses
            assignments = self.get_queryset().filter(
                due_date__gt=now,
                status='published'
            ).order_by('due_date')[:10]
        else:
            # Students see upcoming assignments for enrolled courses
            enrolled_courses = Enrollment.objects.filter(
                student=request.user,
                tenant=getattr(request, 'tenant', None)
            ).values_list('course_id', flat=True)
            
            assignments = Assignment.objects.filter(
                course_id__in=enrolled_courses,
                due_date__gt=now,
                status='published',
                tenant=getattr(request, 'tenant', None)
            ).order_by('due_date')[:10]
        
        serializer = self.get_serializer(assignments, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Upcoming assignments retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue assignments for the current user"""
        now = timezone.now()
        
        if request.user.is_teacher:
            # Teachers see overdue assignments for their courses
            assignments = self.get_queryset().filter(
                due_date__lt=now,
                status='published'
            ).order_by('-due_date')[:10]
        else:
            # Students see overdue assignments they haven't submitted
            enrolled_courses = Enrollment.objects.filter(
                student=request.user,
                tenant=getattr(request, 'tenant', None)
            ).values_list('course_id', flat=True)
            
            # Get assignments where student hasn't submitted or submission is draft
            submitted_assignment_ids = Submission.objects.filter(
                student=request.user,
                status__in=['submitted', 'late', 'graded']
            ).values_list('assignment_id', flat=True)
            
            assignments = Assignment.objects.filter(
                course_id__in=enrolled_courses,
                due_date__lt=now,
                status='published',
                tenant=getattr(request, 'tenant', None)
            ).exclude(id__in=submitted_assignment_ids).order_by('-due_date')[:10]
        
        serializer = self.get_serializer(assignments, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Overdue assignments retrieved successfully"
        )


class SubmissionViewSet(StandardViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Submission model with grading functionality"""
    
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SubmissionFilter
    search_fields = ['assignment__title', 'student__email', 'text_content']
    ordering_fields = ['created_at', 'submitted_at', 'graded_at', 'score']
    ordering = ['-submitted_at', '-created_at']
    
    # Query optimization fields
    select_related_fields = ['assignment', 'assignment__course', 'student', 'graded_by', 'tenant']
    prefetch_related_fields = []
    
    def get_queryset(self):
        """Filter submissions by tenant and user permissions"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Submission.objects.filter(tenant=self.request.tenant)
            
            # Filter based on user role
            if not self.request.user.is_staff:
                if self.request.user.is_teacher:
                    # Teachers see submissions for their courses
                    queryset = queryset.filter(assignment__course__instructor=self.request.user)
                else:
                    # Students see only their own submissions
                    queryset = queryset.filter(student=self.request.user)
            
            return queryset.select_related(*self.select_related_fields).prefetch_related(*self.prefetch_related_fields)
        
        return Submission.objects.none()
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action"""
        if self.action in ['create', 'update', 'partial_update']:
            return SubmissionCreateSerializer
        elif self.action == 'grade':
            return SubmissionGradeSerializer
        return SubmissionSerializer
    
    def create(self, request, *args, **kwargs):
        """Create submission with centralized file upload integration"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Handle file upload through centralized system
        file_upload = None
        if 'file_upload' in request.FILES:
            file_service = FileIntegrationService()
            assignment = serializer.validated_data['assignment']
            
            file_upload = file_service.create_assignment_submission_upload(
                file=request.FILES['file_upload'],
                assignment=assignment,
                user=request.user,
                title=f"Submission - {assignment.title}",
                description=f"Assignment submission by {request.user.get_full_name() or request.user.email}"
            )
        
        # Save submission with file reference
        submission = serializer.save(
            student=request.user,
            tenant=request.tenant,
            uploaded_file=file_upload
        )
        
        response_serializer = SubmissionSerializer(submission, context={'request': request})
        return StandardAPIResponse.created(
            data=response_serializer.data,
            message="Submission created successfully"
        )
    
    def perform_create(self, serializer):
        """Set student and tenant when creating submission"""
        serializer.save(
            student=self.request.user,
            tenant=self.request.tenant
        )
    
    def perform_update(self, serializer):
        """Only allow students to update their own draft submissions"""
        submission = self.get_object()
        
        if submission.student != self.request.user:
            raise permissions.PermissionDenied("You can only update your own submissions")
        
        if submission.status != 'draft':
            raise permissions.PermissionDenied("You can only update draft submissions")
        
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit an assignment"""
        submission = self.get_object()
        
        # Check permissions
        if submission.student != request.user:
            return StandardAPIResponse.permission_denied(
                message="You can only submit your own assignments"
            )
        
        if submission.status not in ['draft']:
            return StandardAPIResponse.bad_request(
                message="Assignment has already been submitted"
            )
        
        # Submit the assignment
        SubmissionService.submit_assignment(submission)
        
        return StandardAPIResponse.success(
            data=self.get_serializer(submission).data,
            message="Assignment submitted successfully"
        )
    
    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        """Grade a submission"""
        submission = self.get_object()
        
        # Check permissions
        if submission.assignment.course.instructor != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="Only course instructors can grade submissions"
            )
        
        serializer = SubmissionGradeSerializer(submission, data=request.data, partial=True)
        if serializer.is_valid():
            score = serializer.validated_data.get('score')
            feedback = serializer.validated_data.get('feedback', '')
            
            submission.grade(score=score, feedback=feedback, graded_by=request.user)
            
            # Update course progress
            CourseProgressService.update_student_progress(
                student=submission.student,
                course=submission.assignment.course
            )
            
            return StandardAPIResponse.success(
                data=SubmissionSerializer(submission, context={'request': request}).data,
                message="Submission graded successfully"
            )
        
        return StandardAPIResponse.validation_error(
            errors=serializer.errors,
            message="Grading validation failed"
        )
    
    @action(detail=False, methods=['get'])
    def my_submissions(self, request):
        """Get current user's submissions"""
        submissions = self.get_queryset().filter(student=request.user)
        
        # Apply filters
        filtered_submissions = self.filter_queryset(submissions)
        
        page = self.paginate_queryset(filtered_submissions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(filtered_submissions, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Your submissions retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def pending_grading(self, request):
        """Get submissions pending grading for instructor"""
        if not request.user.is_teacher and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="Only teachers and administrators can access pending grading"
            )
        
        submissions = self.get_queryset().filter(
            is_graded=False,
            status__in=['submitted', 'late']
        )
        
        page = self.paginate_queryset(submissions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(submissions, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Pending submissions retrieved successfully"
        )
    
    @action(detail=True, methods=['get'])
    def download_file(self, request, pk=None):
        """Get secure download URL for submission file"""
        submission = self.get_object()
        
        # Check permissions - student or instructor can download
        if (submission.student != request.user and 
            submission.assignment.course.instructor != request.user and 
            not request.user.is_staff):
            return StandardAPIResponse.permission_denied(
                message="You don't have permission to download this file"
            )
        
        # Use centralized file if available, otherwise fall back to legacy file
        if submission.uploaded_file:
            file_service = FileIntegrationService()
            secure_url = file_service.get_file_access_url(submission.uploaded_file, request.user)
            
            if secure_url:
                return StandardAPIResponse.success(
                    data={
                        'download_url': secure_url,
                        'filename': submission.uploaded_file.original_filename,
                        'file_size': submission.uploaded_file.file_size_mb
                    },
                    message="Download URL generated successfully"
                )
        elif submission.file_upload:
            # Legacy file handling
            return StandardAPIResponse.success(
                data={
                    'download_url': submission.file_upload.url,
                    'filename': submission.file_upload.name.split('/')[-1],
                    'file_size': submission.file_upload.size / (1024 * 1024)  # Convert to MB
                },
                message="Download URL generated successfully"
            )
        
        return StandardAPIResponse.error(
            message="No file available for download",
            status_code=status.HTTP_404_NOT_FOUND
        )


class CertificateViewSet(StandardViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Certificate model with verification functionality"""
    
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CertificateFilter
    search_fields = ['certificate_number', 'student__email', 'course__title']
    ordering_fields = ['created_at', 'issued_at', 'completion_date']
    ordering = ['-issued_at', '-created_at']
    
    # Query optimization fields
    select_related_fields = ['student', 'course', 'course__instructor', 'tenant']
    prefetch_related_fields = []
    
    def get_queryset(self):
        """Filter certificates by tenant and user permissions"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Certificate.objects.filter(tenant=self.request.tenant)
            
            # Filter based on user role
            if not self.request.user.is_staff:
                if self.request.user.is_teacher:
                    # Teachers see certificates for their courses
                    queryset = queryset.filter(course__instructor=self.request.user)
                else:
                    # Students see only their own certificates
                    queryset = queryset.filter(student=self.request.user)
            
            return queryset.select_related(*self.select_related_fields).prefetch_related(*self.prefetch_related_fields)
        
        return Certificate.objects.none()
    
    def perform_create(self, serializer):
        """Set tenant when creating certificate"""
        serializer.save(tenant=self.request.tenant)
    
    @action(detail=True, methods=['post'])
    def issue(self, request, pk=None):
        """Issue a certificate"""
        certificate = self.get_object()
        
        # Check permissions
        if certificate.course.instructor != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="Only course instructors can issue certificates"
            )
        
        certificate.issue()
        
        return StandardAPIResponse.success(
            data=self.get_serializer(certificate).data,
            message="Certificate issued successfully"
        )
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a certificate"""
        certificate = self.get_object()
        
        # Check permissions
        if certificate.course.instructor != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="Only course instructors can revoke certificates"
            )
        
        certificate.revoke()
        
        return StandardAPIResponse.success(
            data=self.get_serializer(certificate).data,
            message="Certificate revoked successfully"
        )
    
    @action(detail=False, methods=['get'])
    def verify(self, request):
        """Verify a certificate by certificate number"""
        certificate_number = request.query_params.get('certificate_number')
        
        if not certificate_number:
            return StandardAPIResponse.validation_error(
                errors={'certificate_number': ['This parameter is required']},
                message="Certificate number is required for verification"
            )
        
        verification_result = CertificateService.verify_certificate(certificate_number)
        
        return StandardAPIResponse.success(
            data=verification_result,
            message="Certificate verification completed"
        )
    
    @action(detail=False, methods=['get'])
    def my_certificates(self, request):
        """Get current user's certificates"""
        certificates = self.get_queryset().filter(
            student=request.user,
            status='issued'
        )
        
        serializer = self.get_serializer(certificates, many=True)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Your certificates retrieved successfully"
        )
    
    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """Generate PDF certificate through centralized API"""
        from apps.files.certificate_service import CertificateGenerationService
        
        certificate = self.get_object()
        
        # Check permissions
        if certificate.student != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="You can only generate your own certificates"
            )
        
        # Use centralized certificate generation service
        cert_service = CertificateGenerationService()
        
        template_type = request.data.get('template_type', 'completion')
        file_upload = cert_service.generate_certificate_pdf(certificate, template_type)
        
        if file_upload:
            return StandardAPIResponse.success(
                data={
                    'certificate_file_id': str(file_upload.id),
                    'download_url': file_upload.get_secure_url(),
                    'file_size': file_upload.file_size_mb,
                    'filename': file_upload.original_filename
                },
                message="Certificate PDF generated successfully"
            )
        else:
            return StandardAPIResponse.error(
                message="Failed to generate certificate PDF",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        """Send certificate via email through centralized API"""
        certificate = self.get_object()
        
        # Check permissions
        if certificate.course.instructor != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="Only course instructors can send certificates"
            )
        
        # Use centralized certificate service
        cert_service = CertificateGenerationService()
        
        if cert_service.send_certificate_email(certificate):
            return StandardAPIResponse.success(
                message="Certificate sent via email successfully"
            )
        else:
            return StandardAPIResponse.error(
                message="Failed to send certificate email",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def generate_complete(self, request, pk=None):
        """Complete certificate generation process (PDF + QR + Email)"""
        certificate = self.get_object()
        
        # Check permissions
        if certificate.course.instructor != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="Only course instructors can generate certificates"
            )
        
        # Use centralized certificate service
        cert_service = CertificateGenerationService()
        results = cert_service.generate_certificate_complete(certificate)
        
        if results['success']:
            response_data = {
                'certificate_file_id': str(results['certificate_file'].id) if results['certificate_file'] else None,
                'qr_code_file_id': str(results['qr_code_file'].id) if results['qr_code_file'] else None,
                'email_sent': results['email_sent'],
                'certificate_number': certificate.certificate_number
            }
            
            return StandardAPIResponse.success(
                data=response_data,
                message="Certificate generation completed successfully"
            )
        else:
            return StandardAPIResponse.error(
                message="Certificate generation failed",
                errors=results['errors'],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Get secure download URL for certificate"""
        certificate = self.get_object()
        
        # Check permissions
        if certificate.student != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="You can only download your own certificates"
            )
        
        if certificate.certificate_file:
            # Use file integration service to get secure URL
            file_service = FileIntegrationService()
            secure_url = file_service.get_file_access_url(certificate.certificate_file, request.user)
            
            if secure_url:
                return StandardAPIResponse.success(
                    data={
                        'download_url': secure_url,
                        'filename': certificate.certificate_file.original_filename,
                        'file_size': certificate.certificate_file.file_size_mb
                    },
                    message="Download URL generated successfully"
                )
        
        return StandardAPIResponse.error(
            message="Certificate file not available",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'])
    def verify_centralized(self, request):
        """Verify certificate through centralized API"""
        certificate_number = request.query_params.get('certificate_number')
        
        if not certificate_number:
            return StandardAPIResponse.validation_error(
                errors={'certificate_number': ['This parameter is required']},
                message="Certificate number is required for verification"
            )
        
        # Use centralized certificate service
        cert_service = CertificateGenerationService()
        verification_data = cert_service.verify_certificate(certificate_number)
        
        if verification_data:
            return StandardAPIResponse.success(
                data=verification_data,
                message="Certificate verified successfully"
            )
        else:
            return StandardAPIResponse.error(
                message="Certificate not found or invalid",
                status_code=status.HTTP_404_NOT_FOUND
            )


class CourseProgressViewSet(StandardViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for CourseProgress model with analytics"""
    
    serializer_class = CourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['student__email', 'course__title']
    ordering_fields = ['created_at', 'updated_at', 'overall_progress_percentage']
    ordering = ['-updated_at']
    
    # Query optimization fields
    select_related_fields = ['student', 'course', 'course__instructor', 'tenant']
    prefetch_related_fields = []
    
    def get_queryset(self):
        """Filter course progress by tenant and user permissions"""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = CourseProgress.objects.filter(tenant=self.request.tenant)
            
            # Filter based on user role
            if not self.request.user.is_staff:
                if self.request.user.is_teacher:
                    # Teachers see progress for their courses
                    queryset = queryset.filter(course__instructor=self.request.user)
                else:
                    # Students see only their own progress
                    queryset = queryset.filter(student=self.request.user)
            
            return queryset.select_related(*self.select_related_fields).prefetch_related(*self.prefetch_related_fields)
        
        return CourseProgress.objects.none()
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Manually update student progress"""
        progress = self.get_object()
        
        # Check permissions
        if progress.course.instructor != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="Only course instructors can update student progress"
            )
        
        progress.calculate_progress()
        
        return StandardAPIResponse.success(
            data=self.get_serializer(progress).data,
            message="Progress updated successfully"
        )
    
    @action(detail=False, methods=['get'])
    def course_analytics(self, request):
        """Get completion analytics for a specific course"""
        course_id = request.query_params.get('course_id')
        
        if not course_id:
            return StandardAPIResponse.validation_error(
                errors={'course_id': ['This parameter is required']},
                message="Course ID is required for analytics"
            )
        
        try:
            course = Course.objects.get(id=course_id, tenant=request.tenant)
        except Course.DoesNotExist:
            return StandardAPIResponse.not_found(
                message="Course not found",
                resource_type="Course"
            )
        
        # Check permissions
        if course.instructor != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="Only course instructors can view course analytics"
            )
        
        analytics = CourseProgressService.get_course_completion_analytics(course)
        
        serializer = CourseCompletionAnalyticsSerializer(analytics)
        return StandardAPIResponse.success(
            data=serializer.data,
            message="Course completion analytics retrieved successfully"
        )
    
    @action(detail=False, methods=['get'])
    def student_dashboard(self, request):
        """Get dashboard data for current student"""
        dashboard_data = CourseProgressService.get_student_dashboard_data(
            student=request.user,
            tenant=getattr(request, 'tenant', None)
        )
        
        return StandardAPIResponse.success(
            data=dashboard_data,
            message="Student dashboard data retrieved successfully"
        )
    
    @action(detail=False, methods=['post'])
    def verify_by_qr(self, request):
        """Verify certificate by QR code data"""
        qr_data = request.data.get('qr_data')
        
        if not qr_data:
            return StandardAPIResponse.validation_error(
                errors={'qr_data': ['QR code data is required']},
                message="QR code data is required for verification"
            )
        
        # Extract certificate number from QR data (URL)
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(qr_data)
            certificate_number = parsed_url.path.split('/')[-2]  # Extract from URL path
            
            verification_result = CertificateService.verify_certificate(certificate_number)
            
            return StandardAPIResponse.success(
                data=verification_result,
                message="QR code verification completed"
            )
        except Exception as e:
            return StandardAPIResponse.validation_error(
                errors={'qr_data': ['Invalid QR code format']},
                message="Unable to parse QR code data"
            )
    
    @action(detail=True, methods=['post'])
    def generate_qr_code(self, request, pk=None):
        """Generate QR code for certificate verification"""
        from apps.files.certificate_service import CertificateGenerationService
        
        certificate = self.get_object()
        
        # Check permissions
        if certificate.student != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="You can only generate QR codes for your own certificates"
            )
        
        # Generate QR code through centralized service
        cert_service = CertificateGenerationService()
        qr_file = cert_service.generate_qr_code(certificate)
        
        if qr_file:
            return StandardAPIResponse.success(
                data={
                    'qr_code_file_id': str(qr_file.id),
                    'qr_code_url': qr_file.get_secure_url(),
                    'verification_url': certificate.verification_url
                },
                message="QR code generated successfully"
            )
        else:
            return StandardAPIResponse.error(
                message="Failed to generate QR code"
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download certificate PDF through centralized API"""
        certificate = self.get_object()
        
        # Check permissions
        if certificate.student != request.user and not request.user.is_staff:
            return StandardAPIResponse.permission_denied(
                message="You can only download your own certificates"
            )
        
        # Check if certificate file exists
        if not certificate.certificate_file:
            return StandardAPIResponse.not_found(
                message="Certificate PDF not found. Please generate it first."
            )
        
        # Return secure download URL
        return StandardAPIResponse.success(
            data={
                'download_url': certificate.certificate_file.get_secure_url(),
                'filename': certificate.certificate_file.original_filename,
                'file_size': certificate.certificate_file.file_size_mb
            },
            message="Certificate download URL generated"
        )