"""
Certificate generation service integrated with centralized file management.
Handles PDF generation, QR codes, and delivery through the centralized API.
"""

import os
import qrcode
from io import BytesIO
from typing import Optional, Dict, Any
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, gold
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from .models import FileUpload, FileCategory
from .services import FileUploadService

User = get_user_model()


class CertificateGenerationService:
    """Service for generating certificates through centralized file management"""
    
    def __init__(self):
        self.upload_service = FileUploadService()
    
    def generate_certificate_pdf(
        self,
        certificate,
        template_type: str = 'completion'
    ) -> Optional[FileUpload]:
        """Generate PDF certificate and store in centralized system"""
        
        try:
            # Create PDF in memory
            buffer = BytesIO()
            
            if template_type == 'completion':
                self._generate_completion_certificate(buffer, certificate)
            elif template_type == 'achievement':
                self._generate_achievement_certificate(buffer, certificate)
            else:
                self._generate_completion_certificate(buffer, certificate)
            
            buffer.seek(0)
            
            # Create file upload through centralized system
            filename = f"certificate_{certificate.certificate_number}.pdf"
            
            file_upload = self.upload_service.upload_file(
                file=ContentFile(buffer.getvalue(), name=filename),
                category_name='certificate',
                user=certificate.student,
                title=f"Certificate - {certificate.course.title}",
                description=f"Certificate of {certificate.certificate_type} for {certificate.course.title}",
                access_level='private',  # Only student can access
                course_id=str(certificate.course.id),
                tags=['certificate', certificate.certificate_type, certificate.course.category]
            )
            
            # Update certificate model
            certificate.certificate_file = file_upload
            certificate.save()
            
            return file_upload
            
        except Exception as e:
            print(f"Error generating certificate PDF: {e}")
            return None
    
    def _generate_completion_certificate(self, buffer: BytesIO, certificate):
        """Generate completion certificate PDF"""
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=blue
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        content_style = ParagraphStyle(
            'CustomContent',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        # Certificate content
        story.append(Spacer(1, 50))
        
        # Title
        story.append(Paragraph("CERTIFICATE OF COMPLETION", title_style))
        story.append(Spacer(1, 30))
        
        # Subtitle
        story.append(Paragraph("This is to certify that", subtitle_style))
        story.append(Spacer(1, 20))
        
        # Student name
        student_name = certificate.student.get_full_name() or certificate.student.email
        name_style = ParagraphStyle(
            'StudentName',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=gold
        )
        story.append(Paragraph(f"<b>{student_name}</b>", name_style))
        story.append(Spacer(1, 30))
        
        # Course completion text
        story.append(Paragraph("has successfully completed the course", content_style))
        story.append(Spacer(1, 15))
        
        # Course title
        course_style = ParagraphStyle(
            'CourseTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=blue
        )
        story.append(Paragraph(f"<b>{certificate.course.title}</b>", course_style))
        story.append(Spacer(1, 30))
        
        # Completion details
        if certificate.final_grade:
            story.append(Paragraph(f"Final Grade: {certificate.final_grade}%", content_style))
        
        completion_date = certificate.completion_date.strftime("%B %d, %Y")
        story.append(Paragraph(f"Completed on: {completion_date}", content_style))
        story.append(Spacer(1, 40))
        
        # Certificate number and verification
        cert_info_style = ParagraphStyle(
            'CertInfo',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"Certificate Number: {certificate.certificate_number}", cert_info_style))
        story.append(Paragraph(f"Verify at: {settings.FRONTEND_URL}{certificate.verification_url}", cert_info_style))
        
        # Build PDF
        doc.build(story)
    
    def _generate_achievement_certificate(self, buffer: BytesIO, certificate):
        """Generate achievement certificate PDF with enhanced design"""
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles for achievement certificate
        title_style = ParagraphStyle(
            'AchievementTitle',
            parent=styles['Heading1'],
            fontSize=26,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=gold
        )
        
        # Certificate content
        story.append(Spacer(1, 40))
        
        # Title
        story.append(Paragraph("CERTIFICATE OF ACHIEVEMENT", title_style))
        story.append(Spacer(1, 40))
        
        # Achievement content (similar structure but different styling)
        student_name = certificate.student.get_full_name() or certificate.student.email
        story.append(Paragraph(f"<b>{student_name}</b>", title_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("has demonstrated exceptional performance in", styles['Normal']))
        story.append(Paragraph(f"<b>{certificate.course.title}</b>", styles['Heading2']))
        
        if certificate.final_grade and certificate.final_grade >= 90:
            story.append(Paragraph("with distinction", styles['Normal']))
        
        # Build PDF
        doc.build(story)
    
    def generate_qr_code(self, certificate) -> Optional[FileUpload]:
        """Generate QR code for certificate verification"""
        
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Full verification URL
            verification_url = f"{settings.FRONTEND_URL}{certificate.verification_url}"
            qr.add_data(verification_url)
            qr.make(fit=True)
            
            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Save to BytesIO
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Upload through centralized system
            filename = f"qr_code_{certificate.certificate_number}.png"
            
            file_upload = self.upload_service.upload_file(
                file=ContentFile(buffer.getvalue(), name=filename),
                category_name='image',
                user=certificate.student,
                title=f"QR Code - Certificate {certificate.certificate_number}",
                description=f"QR code for certificate verification",
                access_level='public',  # QR codes can be public
                course_id=str(certificate.course.id),
                tags=['qr-code', 'certificate-verification']
            )
            
            return file_upload
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None
    
    def get_certificate_data(self, certificate) -> Dict[str, Any]:
        """Get comprehensive certificate data from centralized API"""
        
        # Get user data from centralized API
        user_data = {
            'id': str(certificate.student.id),
            'name': certificate.student.get_full_name(),
            'email': certificate.student.email,
            'profile': {
                'organization': getattr(certificate.student, 'organization', None),
                'title': getattr(certificate.student, 'title', None)
            }
        }
        
        # Get course data from centralized API
        course_data = {
            'id': str(certificate.course.id),
            'title': certificate.course.title,
            'description': certificate.course.description,
            'category': certificate.course.category,
            'instructor': {
                'name': certificate.course.instructor.get_full_name(),
                'email': certificate.course.instructor.email
            },
            'duration_weeks': certificate.course.duration_weeks,
            'total_modules': certificate.course.modules.count(),
            'total_assignments': certificate.course.assignments.count()
        }
        
        # Get completion data
        completion_data = {
            'certificate_number': certificate.certificate_number,
            'certificate_type': certificate.certificate_type,
            'final_grade': certificate.final_grade,
            'completion_date': certificate.completion_date,
            'issued_at': certificate.issued_at,
            'verification_url': certificate.verification_url
        }
        
        return {
            'user': user_data,
            'course': course_data,
            'completion': completion_data,
            'certificate_file_url': certificate.certificate_file.get_secure_url() if certificate.certificate_file else None,
            'qr_code_url': certificate.qr_code.url if certificate.qr_code else None
        }
    
    def send_certificate_email(self, certificate) -> bool:
        """Send certificate via email through centralized API"""
        
        try:
            from django.core.mail import EmailMessage
            from django.template.loader import render_to_string
            
            # Get certificate data
            cert_data = self.get_certificate_data(certificate)
            
            # Render email template
            subject = f"Your Certificate for {certificate.course.title}"
            
            html_content = render_to_string('emails/certificate_delivery.html', {
                'certificate': certificate,
                'student': certificate.student,
                'course': certificate.course,
                'cert_data': cert_data
            })
            
            text_content = f"""
            Congratulations {certificate.student.get_full_name()}!
            
            You have successfully completed {certificate.course.title}.
            
            Certificate Number: {certificate.certificate_number}
            Completion Date: {certificate.completion_date.strftime('%B %d, %Y')}
            Final Grade: {certificate.final_grade}%
            
            You can download your certificate and verify it at:
            {settings.FRONTEND_URL}{certificate.verification_url}
            
            Best regards,
            EduRise LMS Team
            """
            
            # Create email
            email = EmailMessage(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[certificate.student.email]
            )
            
            # Attach certificate PDF if available
            if certificate.certificate_file and certificate.certificate_file.file:
                email.attach_file(certificate.certificate_file.file.path)
            
            # Send email
            email.send()
            
            return True
            
        except Exception as e:
            print(f"Error sending certificate email: {e}")
            return False
    
    def verify_certificate(self, certificate_number: str) -> Optional[Dict[str, Any]]:
        """Verify certificate through centralized API"""
        
        try:
            from apps.assignments.models import Certificate
            
            certificate = Certificate.objects.get(
                certificate_number=certificate_number,
                status='issued'
            )
            
            return self.get_certificate_data(certificate)
            
        except Certificate.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error verifying certificate: {e}")
            return None
    
    def generate_certificate_complete(self, certificate) -> Dict[str, Any]:
        """Complete certificate generation process"""
        
        results = {
            'success': False,
            'certificate_file': None,
            'qr_code_file': None,
            'email_sent': False,
            'errors': []
        }
        
        try:
            # Generate PDF certificate
            cert_file = self.generate_certificate_pdf(certificate)
            if cert_file:
                results['certificate_file'] = cert_file
            else:
                results['errors'].append("Failed to generate certificate PDF")
            
            # Generate QR code
            qr_file = self.generate_qr_code(certificate)
            if qr_file:
                results['qr_code_file'] = qr_file
            else:
                results['errors'].append("Failed to generate QR code")
            
            # Send email
            if self.send_certificate_email(certificate):
                results['email_sent'] = True
            else:
                results['errors'].append("Failed to send certificate email")
            
            # Mark certificate as issued
            certificate.issue()
            
            results['success'] = len(results['errors']) == 0
            
        except Exception as e:
            results['errors'].append(f"Certificate generation failed: {e}")
        
        return results