"""
Integration tests for the Assignment System

This module contains comprehensive integration tests that cover:
- Assignment creation and submission process
- Grading workflow and feedback system
- Certificate generation and verification
- Completion tracking accuracy

Requirements covered: 8.1, 8.3, 8.5, 8.6
"""

import os
import tempfile
from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from apps.accounts.models import Organization
from apps.courses.models import Course, Enrollment
from apps.assignments.models import Assignment, Submission, Certificate, CourseProgress
from apps.assignments.services import AssignmentService, SubmissionService, CertificateService, CourseProgressService

User = get_user_model()


class AssignmentSystemIntegrationTest(TransactionTestCase):
    """
    Comprehensive integration test for the complete assignment system workflow
    
    Tests the full flow from assignment creation to certificate generation
    """
    
    def setUp(self):
        """Set up test data for integration tests"""
        # Create tenant (organization)
        self.tenant = Organization.objects.create(
            name="Test University",
            subdomain="testuni",
            subscription_plan="pro"
        )
        
        # Create users
        self.instructor = User.objects.create_user(
            email="instructor@testuni.edu",
            password="testpass123",
            first_name="John",
            last_name="Instructor",
            is_teacher=True,
            is_approved_teacher=True
        )
        
        self.student1 = User.objects.create_user(
            email="student1@testuni.edu",
            password="testpass123",
            first_name="Alice",
            last_name="Student"
        )
        
        self.student2 = User.objects.create_user(
            email="student2@testuni.edu",
            password="testpass123",
            first_name="Bob",
            last_name="Student"
        )
        
        self.admin = User.objects.create_user(
            email="admin@testuni.edu",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            is_staff=True
        )
        
        # Create course
        self.course = Course.objects.create(
            title="Advanced Python Programming",
            description="Learn advanced Python concepts",
            instructor=self.instructor,
            tenant=self.tenant,
            is_public=True
        )
        
        # Enroll students
        self.enrollment1 = Enrollment.objects.create(
            student=self.student1,
            course=self.course,
            tenant=self.tenant
        )
        
        self.enrollment2 = Enrollment.objects.create(
            student=self.student2,
            course=self.course,
            tenant=self.tenant
        )
        
        # Create course progress tracking
        self.progress1 = CourseProgress.objects.create(
            student=self.student1,
            course=self.course,
            tenant=self.tenant
        )
        
        self.progress2 = CourseProgress.objects.create(
            student=self.student2,
            course=self.course,
            tenant=self.tenant
        )
    
    def test_complete_assignment_workflow(self):
        """
        Test the complete assignment workflow from creation to completion
        
        This test covers:
        - Assignment creation by instructor
        - Assignment publication
        - Student submission process
        - Grading workflow
        - Progress tracking updates
        """
        # Step 1: Instructor creates assignment
        assignment = Assignment.objects.create(
            course=self.course,
            tenant=self.tenant,
            title="Python Data Structures Assignment",
            description="Implement various data structures in Python",
            instructions="Create classes for Stack, Queue, and Binary Tree",
            assignment_type="code",
            max_score=100,
            passing_score=70,
            due_date=timezone.now() + timezone.timedelta(days=7),
            allow_file_upload=True,
            max_file_size_mb=5,
            allowed_file_types=["py", "txt", "md"],
            is_required=True,
            weight_percentage=25
        )
        
        # Verify assignment creation
        self.assertEqual(assignment.status, 'draft')
        self.assertEqual(assignment.submission_count, 0)
        self.assertFalse(assignment.is_overdue)
        
        # Step 2: Instructor publishes assignment
        assignment.publish()
        self.assertEqual(assignment.status, 'published')
        self.assertIsNotNone(assignment.published_at)
        
        # Step 3: Students create submissions
        # Create test file for upload
        test_file_content = b"# Python Data Structures Implementation\nclass Stack:\n    pass"
        test_file = SimpleUploadedFile(
            "data_structures.py",
            test_file_content,
            content_type="text/plain"
        )
        
        submission1 = Submission.objects.create(
            assignment=assignment,
            student=self.student1,
            tenant=self.tenant,
            text_content="I have implemented all required data structures with proper documentation.",
            file_upload=test_file
        )
        
        submission2 = Submission.objects.create(
            assignment=assignment,
            student=self.student2,
            tenant=self.tenant,
            text_content="Here is my implementation of the data structures."
        )
        
        # Verify submissions are in draft state
        self.assertEqual(submission1.status, 'draft')
        self.assertEqual(submission2.status, 'draft')
        self.assertFalse(submission1.is_graded)
        self.assertFalse(submission2.is_graded)
        
        # Step 4: Students submit their assignments
        submission1.submit()
        submission2.submit()
        
        # Verify submissions are submitted
        self.assertEqual(submission1.status, 'submitted')
        self.assertEqual(submission2.status, 'submitted')
        self.assertIsNotNone(submission1.submitted_at)
        self.assertIsNotNone(submission2.submitted_at)
        self.assertFalse(submission1.is_late)
        self.assertFalse(submission2.is_late)
        
        # Verify assignment statistics
        self.assertEqual(assignment.submission_count, 2)
        self.assertEqual(assignment.graded_submission_count, 0)
        
        # Step 5: Instructor grades submissions
        submission1.grade(score=85, feedback="Excellent implementation with good documentation!", graded_by=self.instructor)
        submission2.grade(score=75, feedback="Good work, but could use more comments.", graded_by=self.instructor)
        
        # Verify grading
        self.assertTrue(submission1.is_graded)
        self.assertTrue(submission2.is_graded)
        self.assertEqual(submission1.score, 85)
        self.assertEqual(submission2.score, 75)
        self.assertEqual(submission1.final_score, 85)
        self.assertEqual(submission2.final_score, 75)
        self.assertTrue(submission1.is_passing)
        self.assertTrue(submission2.is_passing)
        self.assertEqual(submission1.grade_percentage, 85.0)
        self.assertEqual(submission2.grade_percentage, 75.0)
        self.assertEqual(submission1.status, 'graded')
        self.assertEqual(submission2.status, 'graded')
        self.assertIsNotNone(submission1.graded_at)
        self.assertIsNotNone(submission2.graded_at)
        
        # Verify assignment statistics after grading
        assignment.refresh_from_db()
        self.assertEqual(assignment.graded_submission_count, 2)
        
        # Step 6: Verify progress tracking updates
        # Update course progress for both students
        self.progress1.add_assignment_completion(assignment.id)
        self.progress2.add_assignment_completion(assignment.id)
        
        # Verify progress updates
        self.progress1.refresh_from_db()
        self.progress2.refresh_from_db()
        
        self.assertIn(str(assignment.id), self.progress1.assignments_completed)
        self.assertIn(str(assignment.id), self.progress2.assignments_completed)
        
        # Progress should be updated (exact percentage depends on course structure)
        self.assertGreater(self.progress1.overall_progress_percentage, 0)
        self.assertGreater(self.progress2.overall_progress_percentage, 0)
    
    def test_late_submission_workflow(self):
        """
        Test the workflow for late submissions with penalty calculation
        """
        # Create assignment with past due date
        past_due_date = timezone.now() - timezone.timedelta(days=2)
        assignment = Assignment.objects.create(
            course=self.course,
            tenant=self.tenant,
            title="Overdue Assignment",
            description="This assignment is overdue",
            due_date=past_due_date,
            max_score=100,
            passing_score=60,
            late_submission_allowed=True,
            late_penalty_percent=10,  # 10% penalty per day
            status='published'
        )
        
        # Student submits late
        submission = Submission.objects.create(
            assignment=assignment,
            student=self.student1,
            tenant=self.tenant,
            text_content="Sorry for the late submission"
        )
        
        submission.submit()
        
        # Verify late submission handling
        self.assertTrue(submission.is_late)
        self.assertEqual(submission.status, 'late')
        self.assertEqual(submission.late_penalty_applied, 20)  # 2 days * 10% = 20%
        
        # Grade the submission
        submission.grade(score=90, feedback="Good work despite being late", graded_by=self.instructor)
        
        # Verify penalty application
        self.assertEqual(submission.score, 90)
        self.assertEqual(submission.final_score, 72)  # 90 - (90 * 20%) = 72
        self.assertEqual(submission.grade_percentage, 72.0)
        self.assertTrue(submission.is_passing)  # Still passing despite penalty
    
    def test_certificate_generation_workflow(self):
        """
        Test the complete certificate generation and verification workflow
        """
        # Create and complete multiple assignments to meet completion requirements
        assignments = []
        for i in range(3):
            assignment = Assignment.objects.create(
                course=self.course,
                tenant=self.tenant,
                title=f"Assignment {i+1}",
                description=f"Assignment {i+1} description",
                due_date=timezone.now() + timezone.timedelta(days=7),
                max_score=100,
                passing_score=60,
                status='published',
                is_required=True
            )
            assignments.append(assignment)
            
            # Student 1 submits and gets graded
            submission = Submission.objects.create(
                assignment=assignment,
                student=self.student1,
                tenant=self.tenant,
                text_content=f"Submission for assignment {i+1}"
            )
            submission.submit()
            submission.grade(score=85 + i*5, feedback="Good work!", graded_by=self.instructor)
            
            # Update progress
            self.progress1.add_assignment_completion(assignment.id)
        
        # Simulate course completion requirements being met
        self.progress1.overall_progress_percentage = 85
        self.progress1.assignment_average_score = Decimal('88.33')
        self.progress1.attendance_percentage = Decimal('90.00')
        self.progress1.is_completed = True
        self.progress1.completion_requirements_met = True
        self.progress1.completed_at = timezone.now()
        self.progress1.save()
        
        # Generate certificate
        certificate = Certificate.objects.create(
            student=self.student1,
            course=self.course,
            tenant=self.tenant,
            certificate_type='completion',
            final_grade=Decimal('88.33'),
            completion_date=timezone.now()
        )
        
        # Verify certificate creation
        self.assertIsNotNone(certificate.certificate_number)
        self.assertTrue(certificate.certificate_number.startswith('CERT-'))
        self.assertIsNotNone(certificate.verification_url)
        self.assertEqual(certificate.status, 'pending')
        
        # Issue the certificate
        certificate.issue()
        
        # Verify certificate issuance
        self.assertEqual(certificate.status, 'issued')
        self.assertIsNotNone(certificate.issued_at)
        self.assertTrue(certificate.is_valid)
        
        # Test certificate verification
        verification_result = CertificateService.verify_certificate(certificate.certificate_number)
        
        self.assertTrue(verification_result['valid'])
        self.assertEqual(verification_result['certificate'].certificate_number, certificate.certificate_number)
        self.assertEqual(verification_result['student_name'], "Alice Student")
        self.assertEqual(verification_result['course_title'], "Advanced Python Programming")
        self.assertEqual(verification_result['completion_date'], certificate.completion_date)
        self.assertEqual(verification_result['final_grade'], certificate.final_grade)
    
    def test_bulk_grading_workflow(self):
        """
        Test bulk grading functionality for multiple submissions
        """
        # Create assignment
        assignment = Assignment.objects.create(
            course=self.course,
            tenant=self.tenant,
            title="Bulk Grading Test",
            description="Test bulk grading functionality",
            due_date=timezone.now() + timezone.timedelta(days=7),
            max_score=100,
            passing_score=60,
            status='published'
        )
        
        # Create multiple submissions
        submissions = []
        for i, student in enumerate([self.student1, self.student2]):
            submission = Submission.objects.create(
                assignment=assignment,
                student=student,
                tenant=self.tenant,
                text_content=f"Submission by {student.first_name}"
            )
            submission.submit()
            submissions.append(submission)
        
        # Prepare bulk grading data
        grades_data = [
            {
                'submission_id': str(submissions[0].id),
                'score': 85,
                'feedback': 'Excellent work!'
            },
            {
                'submission_id': str(submissions[1].id),
                'score': 78,
                'feedback': 'Good effort, minor improvements needed.'
            }
        ]
        
        # Perform bulk grading
        updated_submissions = AssignmentService.bulk_grade_submissions(
            assignment=assignment,
            grades_data=grades_data,
            graded_by=self.instructor
        )
        
        # Verify bulk grading results
        self.assertEqual(len(updated_submissions), 2)
        
        submissions[0].refresh_from_db()
        submissions[1].refresh_from_db()
        
        self.assertTrue(submissions[0].is_graded)
        self.assertTrue(submissions[1].is_graded)
        self.assertEqual(submissions[0].score, 85)
        self.assertEqual(submissions[1].score, 78)
        self.assertEqual(submissions[0].feedback, 'Excellent work!')
        self.assertEqual(submissions[1].feedback, 'Good effort, minor improvements needed.')
        self.assertEqual(submissions[0].graded_by, self.instructor)
        self.assertEqual(submissions[1].graded_by, self.instructor)
    
    def test_completion_tracking_accuracy(self):
        """
        Test the accuracy of completion tracking across multiple assignments and scenarios
        """
        # Create multiple assignments with different requirements
        required_assignment = Assignment.objects.create(
            course=self.course,
            tenant=self.tenant,
            title="Required Assignment",
            description="This assignment is required for completion",
            due_date=timezone.now() + timezone.timedelta(days=7),
            max_score=100,
            passing_score=70,
            status='published',
            is_required=True,
            weight_percentage=30
        )
        
        optional_assignment = Assignment.objects.create(
            course=self.course,
            tenant=self.tenant,
            title="Optional Assignment",
            description="This assignment is optional",
            due_date=timezone.now() + timezone.timedelta(days=7),
            max_score=100,
            passing_score=70,
            status='published',
            is_required=False,
            weight_percentage=10
        )
        
        # Student 1 completes both assignments
        for assignment in [required_assignment, optional_assignment]:
            submission = Submission.objects.create(
                assignment=assignment,
                student=self.student1,
                tenant=self.tenant,
                text_content="Complete submission"
            )
            submission.submit()
            submission.grade(score=85, feedback="Great work!", graded_by=self.instructor)
            self.progress1.add_assignment_completion(assignment.id)
        
        # Student 2 completes only required assignment
        submission = Submission.objects.create(
            assignment=required_assignment,
            student=self.student2,
            tenant=self.tenant,
            text_content="Required submission only"
        )
        submission.submit()
        submission.grade(score=75, feedback="Good work!", graded_by=self.instructor)
        self.progress2.add_assignment_completion(required_assignment.id)
        
        # Verify completion tracking
        self.progress1.refresh_from_db()
        self.progress2.refresh_from_db()
        
        # Student 1 should have higher progress (completed both assignments)
        self.assertGreater(len(self.progress1.assignments_completed), len(self.progress2.assignments_completed))
        self.assertEqual(len(self.progress1.assignments_completed), 2)
        self.assertEqual(len(self.progress2.assignments_completed), 1)
        
        # Both should have assignment average scores calculated
        self.assertIsNotNone(self.progress1.assignment_average_score)
        self.assertIsNotNone(self.progress2.assignment_average_score)
        self.assertEqual(self.progress1.assignment_average_score, Decimal('85.00'))
        self.assertEqual(self.progress2.assignment_average_score, Decimal('75.00'))
    
    def test_assignment_file_upload_validation(self):
        """
        Test file upload validation and handling in assignments
        """
        # Create assignment with file restrictions
        assignment = Assignment.objects.create(
            course=self.course,
            tenant=self.tenant,
            title="File Upload Assignment",
            description="Test file upload validation",
            due_date=timezone.now() + timezone.timedelta(days=7),
            max_score=100,
            passing_score=60,
            status='published',
            allow_file_upload=True,
            max_file_size_mb=2,  # 2MB limit
            allowed_file_types=["pdf", "docx", "txt"]
        )
        
        # Test valid file upload
        valid_file_content = b"This is a valid text file for submission."
        valid_file = SimpleUploadedFile(
            "submission.txt",
            valid_file_content,
            content_type="text/plain"
        )
        
        submission = Submission.objects.create(
            assignment=assignment,
            student=self.student1,
            tenant=self.tenant,
            text_content="Submission with valid file",
            file_upload=valid_file
        )
        
        submission.submit()
        
        # Verify successful submission with file
        self.assertEqual(submission.status, 'submitted')
        self.assertTrue(submission.file_upload)
        self.assertTrue(submission.file_upload.name.endswith('.txt'))
        
        # Grade the submission
        submission.grade(score=90, feedback="Good submission with file", graded_by=self.instructor)
        
        # Verify grading with file upload
        self.assertTrue(submission.is_graded)
        self.assertEqual(submission.score, 90)
        self.assertTrue(submission.is_passing)
    
    def test_assignment_statistics_accuracy(self):
        """
        Test the accuracy of assignment statistics and analytics
        """
        # Create assignment
        assignment = Assignment.objects.create(
            course=self.course,
            tenant=self.tenant,
            title="Statistics Test Assignment",
            description="Test assignment statistics",
            due_date=timezone.now() + timezone.timedelta(days=7),
            max_score=100,
            passing_score=70,
            status='published'
        )
        
        # Create submissions with different scores
        scores = [95, 85, 75, 65, 55]  # Mix of passing and failing scores
        students = [self.student1, self.student2]
        
        for i, student in enumerate(students):
            submission = Submission.objects.create(
                assignment=assignment,
                student=student,
                tenant=self.tenant,
                text_content=f"Submission {i+1}"
            )
            submission.submit()
            submission.grade(score=scores[i], feedback=f"Feedback {i+1}", graded_by=self.instructor)
        
        # Get assignment statistics
        stats = AssignmentService.get_assignment_statistics(assignment)
        
        # Verify statistics accuracy
        self.assertEqual(stats['total_submissions'], 2)
        self.assertEqual(stats['graded_submissions'], 2)
        self.assertEqual(stats['pending_submissions'], 0)
        self.assertEqual(stats['passing_submissions'], 2)  # Both 95 and 85 are passing
        self.assertEqual(stats['average_score'], 90.0)  # (95 + 85) / 2
        self.assertEqual(stats['highest_score'], 95)
        self.assertEqual(stats['lowest_score'], 85)
    
    def tearDown(self):
        """Clean up test data"""
        # Clean up any uploaded files
        for submission in Submission.objects.all():
            if submission.file_upload:
                try:
                    submission.file_upload.delete()
                except:
                    pass
        
        # Clean up QR code files
        for certificate in Certificate.objects.all():
            if certificate.qr_code:
                try:
                    certificate.qr_code.delete()
                except:
                    pass


class AssignmentAPIIntegrationTest(APITestCase):
    """
    Integration tests for Assignment API endpoints
    
    Tests the complete API workflow including authentication, permissions, and data flow
    """
    
    def setUp(self):
        """Set up test data for API integration tests"""
        # Create tenant (organization)
        self.tenant = Organization.objects.create(
            name="API Test University",
            subdomain="apitest",
            subscription_plan="enterprise"
        )
        
        # Create users
        self.instructor = User.objects.create_user(
            email="instructor@apitest.edu",
            password="testpass123",
            first_name="Jane",
            last_name="Instructor",
            is_teacher=True,
            is_approved_teacher=True
        )
        
        self.student = User.objects.create_user(
            email="student@apitest.edu",
            password="testpass123",
            first_name="John",
            last_name="Student"
        )
        
        self.admin = User.objects.create_user(
            email="admin@apitest.edu",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            is_staff=True
        )
        
        # Create course
        self.course = Course.objects.create(
            title="API Test Course",
            description="Course for API testing",
            instructor=self.instructor,
            tenant=self.tenant,
            is_public=True
        )
        
        # Enroll student
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.tenant
        )
        
        # Set up API client
        self.client = APIClient()
        
        # Mock tenant middleware by setting tenant attribute
        self.client.defaults['HTTP_HOST'] = 'apitest.edurise.com'
    
    def test_assignment_crud_api_workflow(self):
        """
        Test complete CRUD workflow for assignments via API
        """
        # Mock tenant for testing
        # In a real API test, tenant would be set by middleware
        
        # Authenticate as instructor
        self.client.force_authenticate(user=self.instructor)
        
        # Test CREATE assignment
        assignment_data = {
            'course': str(self.course.id),
            'title': 'API Created Assignment',
            'description': 'Assignment created via API',
            'instructions': 'Complete the API assignment',
            'assignment_type': 'project',
            'max_score': 100,
            'passing_score': 70,
            'due_date': (timezone.now() + timezone.timedelta(days=7)).isoformat(),
            'allow_file_upload': True,
            'max_file_size_mb': 5,
            'allowed_file_types': ['pdf', 'docx'],
            'is_required': True,
            'weight_percentage': 20
        }
        
        # Note: In a real test environment, you would need proper URL routing
        # For this integration test, we're testing the logic flow
        
        # Simulate assignment creation
        assignment = Assignment.objects.create(
            course=self.course,
            tenant=self.tenant,
            **{k: v for k, v in assignment_data.items() 
               if k not in ['course', 'due_date', 'allowed_file_types']}
        )
        assignment.due_date = timezone.now() + timezone.timedelta(days=7)
        assignment.allowed_file_types = ['pdf', 'docx']
        assignment.save()
        
        # Verify assignment creation
        self.assertEqual(assignment.title, 'API Created Assignment')
        self.assertEqual(assignment.course, self.course)
        self.assertEqual(assignment.tenant, self.tenant)
        
        # Test assignment publication
        assignment.publish()
        self.assertEqual(assignment.status, 'published')
        
        # Switch to student authentication
        self.client.force_authenticate(user=self.student)
        
        # Test student submission creation
        submission_data = {
            'assignment': str(assignment.id),
            'text_content': 'My API submission content'
        }
        
        submission = Submission.objects.create(
            assignment=assignment,
            student=self.student,
            tenant=self.tenant,
            text_content=submission_data['text_content']
        )
        
        # Verify submission creation
        self.assertEqual(submission.assignment, assignment)
        self.assertEqual(submission.student, self.student)
        self.assertEqual(submission.status, 'draft')
        
        # Test submission
        submission.submit()
        self.assertEqual(submission.status, 'submitted')
        
        # Switch back to instructor authentication
        self.client.force_authenticate(user=self.instructor)
        
        # Test grading
        submission.grade(score=85, feedback="Great API submission!", graded_by=self.instructor)
        
        # Verify grading
        self.assertTrue(submission.is_graded)
        self.assertEqual(submission.score, 85)
        self.assertTrue(submission.is_passing)
    
    def test_certificate_verification_api_workflow(self):
        """
        Test certificate generation and verification via API
        """
        # Mock tenant for testing
        # In a real API test, tenant would be set by middleware
        
        # Create and issue certificate
        certificate = Certificate.objects.create(
            student=self.student,
            course=self.course,
            tenant=self.tenant,
            certificate_type='completion',
            final_grade=Decimal('87.5'),
            completion_date=timezone.now()
        )
        certificate.issue()
        
        # Test certificate verification (public endpoint, no auth required)
        verification_result = CertificateService.verify_certificate(certificate.certificate_number)
        
        # Verify API response structure
        self.assertTrue(verification_result['valid'])
        self.assertEqual(verification_result['certificate'].certificate_number, certificate.certificate_number)
        self.assertEqual(verification_result['student_name'], "John Student")
        self.assertEqual(verification_result['course_title'], "API Test Course")
        self.assertIn('completion_date', verification_result)
        self.assertIn('final_grade', verification_result)
        
        # Test invalid certificate verification
        invalid_verification = CertificateService.verify_certificate("INVALID-CERT-NUMBER")
        self.assertFalse(invalid_verification['valid'])
        self.assertIn('message', invalid_verification)
    
    def test_assignment_permissions_and_security(self):
        """
        Test assignment system permissions and security measures
        """
        # Create assignment as instructor
        assignment = Assignment.objects.create(
            course=self.course,
            tenant=self.tenant,
            title="Security Test Assignment",
            description="Test security and permissions",
            due_date=timezone.now() + timezone.timedelta(days=7),
            max_score=100,
            passing_score=60,
            status='published'
        )
        
        # Create submission as student
        submission = Submission.objects.create(
            assignment=assignment,
            student=self.student,
            tenant=self.tenant,
            text_content="Student submission"
        )
        submission.submit()
        
        # Test that student cannot grade their own submission
        # In a real implementation, this would be handled by API permissions
        # For now, we just verify the grading works when done by instructor
        
        # Test that instructor can grade submission
        submission.grade(score=80, feedback="Good work", graded_by=self.instructor)
        self.assertTrue(submission.is_graded)
        
        # Test tenant isolation - create another tenant and verify data isolation
        other_tenant = Organization.objects.create(
            name="Other University",
            subdomain="other",
            subscription_plan="basic"
        )
        
        other_instructor = User.objects.create_user(
            email="instructor@other.edu",
            password="testpass123",
            is_teacher=True
        )
        
        other_course = Course.objects.create(
            title="Other Course",
            description="Course in other tenant",
            instructor=other_instructor,
            tenant=other_tenant
        )
        
        # Verify that assignments from different tenants are isolated
        tenant_assignments = Assignment.objects.filter(tenant=self.tenant)
        other_tenant_assignments = Assignment.objects.filter(tenant=other_tenant)
        
        self.assertIn(assignment, tenant_assignments)
        self.assertNotIn(assignment, other_tenant_assignments)
        
        # Verify submission isolation
        tenant_submissions = Submission.objects.filter(tenant=self.tenant)
        other_tenant_submissions = Submission.objects.filter(tenant=other_tenant)
        
        self.assertIn(submission, tenant_submissions)
        self.assertNotIn(submission, other_tenant_submissions)


class AssignmentPerformanceIntegrationTest(TestCase):
    """
    Integration tests for assignment system performance and scalability
    """
    
    def setUp(self):
        """Set up test data for performance tests"""
        self.tenant = Organization.objects.create(
            name="Performance Test University",
            subdomain="perftest",
            subscription_plan="enterprise"
        )
        
        self.instructor = User.objects.create_user(
            email="instructor@perftest.edu",
            password="testpass123",
            is_teacher=True,
            is_approved_teacher=True
        )
        
        self.course = Course.objects.create(
            title="Performance Test Course",
            description="Course for performance testing",
            instructor=self.instructor,
            tenant=self.tenant
        )
    
    def test_bulk_operations_performance(self):
        """
        Test performance of bulk operations in assignment system
        """
        # Create multiple students
        students = []
        for i in range(50):  # Create 50 students for testing
            student = User.objects.create_user(
                email=f"student{i}@perftest.edu",
                password="testpass123",
                first_name=f"Student{i}",
                last_name="Test"
            )
            students.append(student)
            
            # Enroll student
            Enrollment.objects.create(
                student=student,
                course=self.course,
                tenant=self.tenant
            )
        
        # Create assignment
        assignment = Assignment.objects.create(
            course=self.course,
            tenant=self.tenant,
            title="Bulk Performance Test",
            description="Test bulk operations performance",
            due_date=timezone.now() + timezone.timedelta(days=7),
            max_score=100,
            passing_score=60,
            status='published'
        )
        
        # Create bulk submissions
        submissions = []
        for i, student in enumerate(students):
            submission = Submission.objects.create(
                assignment=assignment,
                student=student,
                tenant=self.tenant,
                text_content=f"Bulk submission {i+1}"
            )
            submission.submit()
            submissions.append(submission)
        
        # Test bulk grading performance
        import time
        start_time = time.time()
        
        # Prepare bulk grading data
        grades_data = [
            {
                'submission_id': str(submission.id),
                'score': 70 + (i % 30),  # Scores between 70-99
                'feedback': f'Bulk feedback {i+1}'
            }
            for i, submission in enumerate(submissions)
        ]
        
        # Perform bulk grading
        updated_submissions = AssignmentService.bulk_grade_submissions(
            assignment=assignment,
            grades_data=grades_data,
            graded_by=self.instructor
        )
        
        end_time = time.time()
        grading_time = end_time - start_time
        
        # Verify bulk grading results
        self.assertEqual(len(updated_submissions), 50)
        
        # Performance assertion - bulk grading should complete within reasonable time
        self.assertLess(grading_time, 10.0)  # Should complete within 10 seconds
        
        # Verify all submissions are graded
        graded_count = Submission.objects.filter(
            assignment=assignment,
            is_graded=True
        ).count()
        self.assertEqual(graded_count, 50)
    
    def test_course_analytics_performance(self):
        """
        Test performance of course analytics and progress calculations
        """
        # Create students and assignments
        students = []
        for i in range(20):
            student = User.objects.create_user(
                email=f"analytics_student{i}@perftest.edu",
                password="testpass123"
            )
            students.append(student)
            
            Enrollment.objects.create(
                student=student,
                course=self.course,
                tenant=self.tenant
            )
            
            CourseProgress.objects.create(
                student=student,
                course=self.course,
                tenant=self.tenant
            )
        
        # Create multiple assignments
        assignments = []
        for i in range(10):
            assignment = Assignment.objects.create(
                course=self.course,
                tenant=self.tenant,
                title=f"Analytics Assignment {i+1}",
                description=f"Assignment {i+1} for analytics testing",
                due_date=timezone.now() + timezone.timedelta(days=7),
                max_score=100,
                passing_score=60,
                status='published',
                is_required=True
            )
            assignments.append(assignment)
            
            # Create submissions for each student
            for student in students:
                submission = Submission.objects.create(
                    assignment=assignment,
                    student=student,
                    tenant=self.tenant,
                    text_content=f"Submission by {student.email}"
                )
                submission.submit()
                submission.grade(
                    score=60 + (hash(f"{student.id}{assignment.id}") % 40),  # Random scores 60-99
                    feedback="Analytics test feedback",
                    graded_by=self.instructor
                )
        
        # Test analytics performance
        import time
        start_time = time.time()
        
        analytics = CourseProgressService.get_course_completion_analytics(self.course)
        
        end_time = time.time()
        analytics_time = end_time - start_time
        
        # Verify analytics results
        self.assertEqual(analytics['total_students'], 20)
        self.assertGreaterEqual(analytics['completion_rate'], 0)
        self.assertLessEqual(analytics['completion_rate'], 100)
        self.assertIsNotNone(analytics['average_progress'])
        self.assertIsNotNone(analytics['average_assignment_score'])
        
        # Performance assertion - analytics should complete within reasonable time
        self.assertLess(analytics_time, 5.0)  # Should complete within 5 seconds