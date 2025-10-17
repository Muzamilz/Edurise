import os
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Avg, Count, Q
from django.utils import timezone
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from .models import Assignment, Submission, Certificate, CourseProgress


class AssignmentService:
    """Service class for assignment-related operations"""
    
    @staticmethod
    def create_assignment(course, instructor, **assignment_data):
        """Create a new assignment for a course"""
        assignment = Assignment.objects.create(
            course=course,
            tenant=course.tenant,
            **assignment_data
        )
        return assignment
    
    @staticmethod
    def get_assignment_statistics(assignment):
        """Get comprehensive statistics for an assignment"""
        submissions = assignment.submissions.all()
        
        stats = {
            'total_submissions': submissions.count(),
            'graded_submissions': submissions.filter(is_graded=True).count(),
            'pending_submissions': submissions.filter(is_graded=False, status__in=['submitted', 'late']).count(),
            'late_submissions': submissions.filter(is_late=True).count(),
            'draft_submissions': submissions.filter(status='draft').count(),
        }
        
        # Grade statistics
        graded_submissions = submissions.filter(is_graded=True, score__isnull=False)
        if graded_submissions.exists():
            scores = graded_submissions.values_list('score', flat=True)
            stats.update({
                'average_score': sum(scores) / len(scores),
                'highest_score': max(scores),
                'lowest_score': min(scores),
                'passing_submissions': graded_submissions.filter(
                    score__gte=assignment.passing_score
                ).count(),
            })
            
            # Grade distribution
            stats['grade_distribution'] = {
                'A (90-100)': graded_submissions.filter(score__gte=90).count(),
                'B (80-89)': graded_submissions.filter(score__gte=80, score__lt=90).count(),
                'C (70-79)': graded_submissions.filter(score__gte=70, score__lt=80).count(),
                'D (60-69)': graded_submissions.filter(score__gte=60, score__lt=70).count(),
                'F (0-59)': graded_submissions.filter(score__lt=60).count(),
            }
        else:
            stats.update({
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0,
                'passing_submissions': 0,
                'grade_distribution': {}
            })
        
        return stats
    
    @staticmethod
    def bulk_grade_submissions(assignment, grades_data, graded_by):
        """Bulk grade multiple submissions"""
        updated_submissions = []
        
        for grade_data in grades_data:
            submission_id = grade_data.get('submission_id')
            score = grade_data.get('score')
            feedback = grade_data.get('feedback', '')
            
            try:
                submission = assignment.submissions.get(id=submission_id)
                submission.grade(score=score, feedback=feedback, graded_by=graded_by)
                updated_submissions.append(submission)
            except Submission.DoesNotExist:
                continue
        
        return updated_submissions


class SubmissionService:
    """Service class for submission-related operations"""
    
    @staticmethod
    def create_or_update_submission(assignment, student, **submission_data):
        """Create or update a student's submission"""
        submission, created = Submission.objects.get_or_create(
            assignment=assignment,
            student=student,
            tenant=assignment.tenant,
            defaults=submission_data
        )
        
        if not created:
            # Update existing submission if not yet submitted
            if submission.status == 'draft':
                for key, value in submission_data.items():
                    setattr(submission, key, value)
                submission.save()
        
        return submission, created
    
    @staticmethod
    def submit_assignment(submission):
        """Submit an assignment and handle late submission logic"""
        submission.submit()
        
        # Update course progress
        progress, created = CourseProgress.objects.get_or_create(
            student=submission.student,
            course=submission.assignment.course,
            tenant=submission.tenant
        )
        
        if submission.is_graded and submission.is_passing:
            progress.add_assignment_completion(submission.assignment.id)
        
        return submission
    
    @staticmethod
    def get_student_submissions_summary(student, course=None, tenant=None):
        """Get summary of student's submissions"""
        submissions = Submission.objects.filter(student=student)
        
        if course:
            submissions = submissions.filter(assignment__course=course)
        
        if tenant:
            submissions = submissions.filter(tenant=tenant)
        
        summary = submissions.aggregate(
            total_submissions=Count('id'),
            graded_submissions=Count('id', filter=Q(is_graded=True)),
            passing_submissions=Count('id', filter=Q(is_graded=True, score__gte=F('assignment__passing_score'))),
            average_score=Avg('score', filter=Q(is_graded=True)),
            late_submissions=Count('id', filter=Q(is_late=True))
        )
        
        return summary


class CertificateService:
    """Service class for certificate generation and management through centralized API"""
    
    @staticmethod
    def generate_certificate(student, course, certificate_type='completion', final_grade=None):
        """Generate a certificate for course completion using centralized API data"""
        from apps.files.certificate_service import CertificateGenerationService
        
        # Check if certificate already exists
        existing_cert = Certificate.objects.filter(
            student=student,
            course=course
        ).first()
        
        if existing_cert:
            return existing_cert
        
        # Get real data from centralized API models
        real_final_grade = final_grade
        if not real_final_grade:
            # Calculate final grade from actual enrollments and assignments
            from apps.courses.models import Enrollment
            enrollment = Enrollment.objects.filter(
                student=student,
                course=course
            ).first()
            
            if enrollment and enrollment.progress_percentage == 100:
                # Get average assignment score from submissions
                from apps.assignments.models import Submission
                submissions = Submission.objects.filter(
                    student=student,
                    assignment__course=course,
                    is_graded=True
                )
                if submissions.exists():
                    real_final_grade = submissions.aggregate(
                        avg_score=models.Avg('final_score')
                    )['avg_score']
        
        # Create certificate with real data
        certificate = Certificate.objects.create(
            student=student,
            course=course,
            tenant=course.tenant,
            certificate_type=certificate_type,
            final_grade=real_final_grade,
            completion_date=timezone.now()
        )
        
        # Use centralized certificate generation service
        cert_service = CertificateGenerationService()
        generation_result = cert_service.generate_certificate_complete(certificate)
        
        if generation_result['success']:
            return certificate
        else:
            # Log errors but still return certificate
            print(f"Certificate generation warnings: {generation_result['errors']}")
            return certificate
    
    @staticmethod
    def generate_certificate_pdf(certificate):
        """Generate PDF certificate using ReportLab"""
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        # Build certificate content
        story = []
        
        # Header
        story.append(Paragraph("CERTIFICATE OF COMPLETION", title_style))
        story.append(Spacer(1, 20))
        
        # Student name
        story.append(Paragraph(
            f"This is to certify that",
            body_style
        ))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph(
            f"<b>{certificate.student.first_name} {certificate.student.last_name}</b>",
            subtitle_style
        ))
        story.append(Spacer(1, 20))
        
        # Course completion
        story.append(Paragraph(
            f"has successfully completed the course",
            body_style
        ))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph(
            f"<b>{certificate.course.title}</b>",
            subtitle_style
        ))
        story.append(Spacer(1, 20))
        
        # Instructor
        story.append(Paragraph(
            f"Instructed by {certificate.course.instructor.first_name} {certificate.course.instructor.last_name}",
            body_style
        ))
        story.append(Spacer(1, 20))
        
        # Grade (if available)
        if certificate.final_grade:
            story.append(Paragraph(
                f"Final Grade: {certificate.final_grade}%",
                body_style
            ))
            story.append(Spacer(1, 20))
        
        # Completion date
        story.append(Paragraph(
            f"Completed on {certificate.completion_date.strftime('%B %d, %Y')}",
            body_style
        ))
        story.append(Spacer(1, 30))
        
        # Certificate details
        details_data = [
            ['Certificate Number:', certificate.certificate_number],
            ['Issue Date:', certificate.completion_date.strftime('%B %d, %Y')],
            ['Verification URL:', certificate.verification_url]
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 30))
        
        # QR Code (if available)
        if certificate.qr_code:
            try:
                qr_image = Image(certificate.qr_code.path, width=1*inch, height=1*inch)
                qr_image.hAlign = 'CENTER'
                story.append(qr_image)
            except:
                pass  # Skip if QR code file not found
        
        # Build PDF
        doc.build(story)
        
        # Save PDF to certificate
        buffer.seek(0)
        filename = f"certificate_{certificate.certificate_number}.pdf"
        certificate.pdf_file.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=True
        )
        
        buffer.close()
        
        return certificate
    
    @staticmethod
    def verify_certificate(certificate_number):
        """Verify a certificate by its number using centralized API data"""
        from apps.files.certificate_service import CertificateGenerationService
        
        try:
            certificate = Certificate.objects.select_related(
                'student', 'course', 'course__instructor', 'tenant'
            ).get(
                certificate_number=certificate_number,
                status='issued'
            )
            
            # Get comprehensive data through centralized API
            cert_service = CertificateGenerationService()
            cert_data = cert_service.get_certificate_data(certificate)
            
            return {
                'valid': True,
                'certificate': certificate,
                'student_name': cert_data['user']['name'],
                'student_email': cert_data['user']['email'],
                'course_title': cert_data['course']['title'],
                'course_category': cert_data['course']['category'],
                'instructor_name': cert_data['course']['instructor']['name'],
                'completion_date': certificate.completion_date,
                'final_grade': certificate.final_grade,
                'certificate_type': certificate.certificate_type,
                'verification_url': certificate.verification_url,
                'qr_code_url': cert_data['qr_code_url'],
                'certificate_file_url': cert_data['certificate_file_url'],
                'issued_at': certificate.issued_at
            }
        except Certificate.DoesNotExist:
            return {
                'valid': False,
                'message': 'Certificate not found or invalid'
            }


class CourseProgressService:
    """Service class for course progress tracking and analytics"""
    
    @staticmethod
    def update_student_progress(student, course):
        """Update student's progress in a course"""
        progress, created = CourseProgress.objects.get_or_create(
            student=student,
            course=course,
            tenant=course.tenant
        )
        
        progress.calculate_progress()
        
        # Check if student is eligible for certificate
        if progress.completion_requirements_met and not hasattr(student, 'certificates'):
            CertificateService.generate_certificate(
                student=student,
                course=course,
                final_grade=progress.assignment_average_score
            )
        
        return progress
    
    @staticmethod
    def get_course_completion_analytics(course):
        """Get comprehensive completion analytics for a course"""
        progress_records = CourseProgress.objects.filter(course=course)
        
        if not progress_records.exists():
            return {
                'total_students': 0,
                'completed_students': 0,
                'completion_rate': 0,
                'average_progress': 0,
                'average_assignment_score': 0,
                'average_attendance': 0,
                'progress_distribution': {},
                'top_performers': [],
                'students_at_risk': []
            }
        
        # Basic statistics
        total_students = progress_records.count()
        completed_students = progress_records.filter(is_completed=True).count()
        completion_rate = (completed_students / total_students) * 100 if total_students > 0 else 0
        
        # Averages
        averages = progress_records.aggregate(
            avg_progress=Avg('overall_progress_percentage'),
            avg_assignment_score=Avg('assignment_average_score'),
            avg_attendance=Avg('attendance_percentage')
        )
        
        # Progress distribution
        progress_distribution = {
            '0-25%': progress_records.filter(overall_progress_percentage__lt=25).count(),
            '25-50%': progress_records.filter(
                overall_progress_percentage__gte=25,
                overall_progress_percentage__lt=50
            ).count(),
            '50-75%': progress_records.filter(
                overall_progress_percentage__gte=50,
                overall_progress_percentage__lt=75
            ).count(),
            '75-100%': progress_records.filter(overall_progress_percentage__gte=75).count(),
        }
        
        # Top performers (top 10% or minimum 5)
        top_count = max(5, int(total_students * 0.1))
        top_performers = progress_records.order_by(
            '-overall_progress_percentage',
            '-assignment_average_score'
        )[:top_count]
        
        # Students at risk (bottom 20% or those with <50% progress)
        at_risk_count = max(5, int(total_students * 0.2))
        students_at_risk = progress_records.filter(
            Q(overall_progress_percentage__lt=50) |
            Q(assignment_average_score__lt=60)
        ).order_by('overall_progress_percentage')[:at_risk_count]
        
        return {
            'total_students': total_students,
            'completed_students': completed_students,
            'completion_rate': round(completion_rate, 2),
            'average_progress': round(averages['avg_progress'] or 0, 2),
            'average_assignment_score': round(averages['avg_assignment_score'] or 0, 2),
            'average_attendance': round(averages['avg_attendance'] or 0, 2),
            'progress_distribution': progress_distribution,
            'top_performers': top_performers,
            'students_at_risk': students_at_risk
        }
    
    @staticmethod
    def get_student_dashboard_data(student, tenant=None):
        """Get dashboard data for a student"""
        progress_records = CourseProgress.objects.filter(student=student)
        
        if tenant:
            progress_records = progress_records.filter(tenant=tenant)
        
        # Get active courses
        active_courses = progress_records.filter(is_completed=False)
        completed_courses = progress_records.filter(is_completed=True)
        
        # Upcoming assignments
        from django.utils import timezone
        upcoming_assignments = Assignment.objects.filter(
            course__in=[p.course for p in active_courses],
            due_date__gt=timezone.now(),
            status='published'
        ).order_by('due_date')[:5]
        
        # Recent submissions
        recent_submissions = Submission.objects.filter(
            student=student,
            assignment__course__in=[p.course for p in active_courses]
        ).order_by('-submitted_at')[:5]
        
        return {
            'active_courses_count': active_courses.count(),
            'completed_courses_count': completed_courses.count(),
            'overall_average_progress': active_courses.aggregate(
                avg=Avg('overall_progress_percentage')
            )['avg'] or 0,
            'upcoming_assignments': upcoming_assignments,
            'recent_submissions': recent_submissions,
            'certificates_earned': Certificate.objects.filter(
                student=student,
                status='issued'
            ).count()
        }