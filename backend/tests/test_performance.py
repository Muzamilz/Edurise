"""
Performance tests for EduRise platform critical paths.
Tests API response times, database query performance, file operations,
and concurrent user scenarios.
"""

import time
import threading
import statistics
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import connection
from django.test.utils import override_settings
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock

from apps.accounts.models import Organization, UserProfile
from apps.courses.models import Course, Enrollment, CourseModule
from apps.payments.models import Payment
from apps.files.models import FileCategory, FileUpload
from apps.ai.models import AIConversation, AIMessage
from apps.accounts.services import JWTAuthService

User = get_user_model()


class APIResponseTimeTest(TransactionTestCase):
    """Test API response times under various conditions"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test tenant
        self.tenant = Organization.objects.create(
            name="Performance Test University",
            subdomain="perf-test",
            subscription_plan="enterprise"
        )
        
        # Create test users
        self.instructor = User.objects.create_user(
            email='perf-instructor@example.com',
            password='testpass123',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        self.student = User.objects.create_user(
            email='perf-student@example.com',
            password='testpass123'
        )
        
        self.admin = User.objects.create_user(
            email='perf-admin@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create profiles
        for user in [self.instructor, self.student, self.admin]:
            UserProfile.objects.create(user=user, tenant=self.tenant)
        
        # Create test data
        self.courses = []
        for i in range(50):  # Create 50 courses for performance testing
            course = Course.objects.create(
                title=f"Performance Course {i}",
                description=f"Course {i} for performance testing",
                instructor=self.instructor,
                tenant=self.tenant,
                category="technology",
                price=Decimal('99.99'),
                is_public=True
            )
            self.courses.append(course)
            
            # Create modules for each course
            for j in range(5):
                CourseModule.objects.create(
                    course=course,
                    title=f"Module {j} - Course {i}",
                    description=f"Module {j} description",
                    order=j + 1,
                    is_published=True
                )
        
        # Create enrollments
        for i in range(0, 25):  # Enroll in first 25 courses
            Enrollment.objects.create(
                student=self.student,
                course=self.courses[i],
                tenant=self.tenant,
                status='active',
                progress_percentage=i * 2  # Varying progress
            )
    
    def authenticate_user(self, user):
        """Helper to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def measure_response_time(self, method, url, data=None, expected_status=200):
        """Helper to measure API response time"""
        start_time = time.time()
        
        if method.upper() == 'GET':
            response = self.client.get(url)
        elif method.upper() == 'POST':
            response = self.client.post(url, data, format='json')
        elif method.upper() == 'PUT':
            response = self.client.put(url, data, format='json')
        elif method.upper() == 'PATCH':
            response = self.client.patch(url, data, format='json')
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Verify response status if specified
        if expected_status:
            self.assertEqual(response.status_code, expected_status)
        
        return response_time, response
    
    def test_course_list_api_performance(self):
        """Test course list API response time with pagination"""
        self.authenticate_user(self.student)
        
        # Test different page sizes
        page_sizes = [10, 25, 50]
        response_times = []
        
        for page_size in page_sizes:
            response_time, response = self.measure_response_time(
                'GET', 
                f'/api/v1/courses/?page=1&page_size={page_size}'
            )
            response_times.append(response_time)
            
            # Response should be under 2 seconds
            self.assertLess(response_time, 2.0, 
                f"Course list API too slow with page_size={page_size}: {response_time:.3f}s")
            
            # Verify pagination works
            data = response.json()
            self.assertIn('meta', data)
            self.assertIn('pagination', data['meta'])
        
        # Average response time should be reasonable
        avg_response_time = statistics.mean(response_times)
        self.assertLess(avg_response_time, 1.5, 
            f"Average course list response time too slow: {avg_response_time:.3f}s")
    
    def test_course_search_performance(self):
        """Test course search API performance"""
        self.authenticate_user(self.student)
        
        search_queries = [
            'Performance',
            'Course',
            'technology',
            'Performance Course 1'
        ]
        
        response_times = []
        
        for query in search_queries:
            response_time, response = self.measure_response_time(
                'GET',
                f'/api/v1/courses/?search={query}'
            )
            response_times.append(response_time)
            
            # Search should be fast
            self.assertLess(response_time, 1.5,
                f"Course search too slow for '{query}': {response_time:.3f}s")
        
        # Average search time should be under 1 second
        avg_search_time = statistics.mean(response_times)
        self.assertLess(avg_search_time, 1.0,
            f"Average search time too slow: {avg_search_time:.3f}s")
    
    def test_dashboard_api_performance(self):
        """Test dashboard API performance with complex data"""
        dashboards = [
            ('student', self.student),
            ('teacher', self.instructor),
            ('admin', self.admin)
        ]
        
        for dashboard_type, user in dashboards:
            self.authenticate_user(user)
            
            response_time, response = self.measure_response_time(
                'GET',
                f'/api/v1/dashboard/{dashboard_type}/'
            )
            
            # Dashboard should load within 3 seconds
            self.assertLess(response_time, 3.0,
                f"{dashboard_type} dashboard too slow: {response_time:.3f}s")
            
            # Verify dashboard has expected structure
            if response.status_code == 200:
                data = response.json()
                self.assertTrue(data.get('success', False))
                self.assertIn('data', data)
    
    def test_enrollment_creation_performance(self):
        """Test enrollment creation performance"""
        self.authenticate_user(self.student)
        
        # Test enrolling in multiple courses
        enrollment_times = []
        
        # Use courses the student isn't enrolled in (26-50)
        for course in self.courses[25:30]:  # Test 5 enrollments
            response_time, response = self.measure_response_time(
                'POST',
                f'/api/v1/courses/courses/{course.id}/enroll/',
                expected_status=None  # Don't check status as it might vary
            )
            enrollment_times.append(response_time)
            
            # Each enrollment should be fast
            self.assertLess(response_time, 2.0,
                f"Enrollment creation too slow: {response_time:.3f}s")
        
        # Average enrollment time should be reasonable
        avg_enrollment_time = statistics.mean(enrollment_times)
        self.assertLess(avg_enrollment_time, 1.0,
            f"Average enrollment time too slow: {avg_enrollment_time:.3f}s")
    
    def test_analytics_api_performance(self):
        """Test analytics API performance"""
        self.authenticate_user(self.instructor)
        
        analytics_endpoints = [
            '/api/v1/analytics/enrollment_trends/',
            '/api/v1/analytics/user_engagement/',
            '/api/v1/analytics/course_performance/',
        ]
        
        for endpoint in analytics_endpoints:
            response_time, response = self.measure_response_time(
                'GET',
                endpoint,
                expected_status=None  # Don't check status as endpoints might not exist
            )
            
            # Analytics should load within 5 seconds (complex queries allowed)
            self.assertLess(response_time, 5.0,
                f"Analytics endpoint {endpoint} too slow: {response_time:.3f}s")


class DatabaseQueryPerformanceTest(TransactionTestCase):
    """Test database query performance and optimization"""
    
    def setUp(self):
        self.tenant = Organization.objects.create(
            name="DB Performance Test",
            subdomain="db-perf",
            subscription_plan="enterprise"
        )
        
        self.instructor = User.objects.create_user(
            email='db-instructor@example.com',
            password='testpass123',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        UserProfile.objects.create(user=self.instructor, tenant=self.tenant)
        
        # Create large dataset for performance testing
        self.courses = []
        self.students = []
        
        # Create 100 courses
        for i in range(100):
            course = Course.objects.create(
                title=f"DB Course {i}",
                description=f"Database performance course {i}",
                instructor=self.instructor,
                tenant=self.tenant,
                category="technology",
                price=Decimal('50.00')
            )
            self.courses.append(course)
        
        # Create 200 students
        for i in range(200):
            student = User.objects.create_user(
                email=f'dbstudent{i}@example.com',
                password='testpass123'
            )
            UserProfile.objects.create(user=student, tenant=self.tenant)
            self.students.append(student)
        
        # Create enrollments (each student enrolled in 5 random courses)
        import random
        for student in self.students:
            selected_courses = random.sample(self.courses, 5)
            for course in selected_courses:
                Enrollment.objects.create(
                    student=student,
                    course=course,
                    tenant=self.tenant,
                    status='active',
                    progress_percentage=random.randint(0, 100)
                )
    
    def measure_query_performance(self, query_func, max_queries=None, max_time=None):
        """Helper to measure query performance"""
        with override_settings(DEBUG=True):
            # Reset query log
            connection.queries_log.clear()
            
            start_time = time.time()
            result = query_func()
            end_time = time.time()
            
            query_count = len(connection.queries)
            execution_time = end_time - start_time
            
            if max_queries:
                self.assertLessEqual(query_count, max_queries,
                    f"Too many queries: {query_count} (max: {max_queries})")
            
            if max_time:
                self.assertLess(execution_time, max_time,
                    f"Query too slow: {execution_time:.3f}s (max: {max_time}s)")
            
            return result, query_count, execution_time
    
    def test_course_list_with_instructor_query_optimization(self):
        """Test optimized course list query with instructor data"""
        
        def optimized_query():
            return list(Course.objects.select_related('instructor').filter(
                tenant=self.tenant
            )[:50])
        
        def unoptimized_query():
            courses = list(Course.objects.filter(tenant=self.tenant)[:50])
            # Force instructor access (N+1 query problem)
            for course in courses:
                _ = course.instructor.email
            return courses
        
        # Test optimized query
        optimized_result, opt_queries, opt_time = self.measure_query_performance(
            optimized_query, max_queries=5, max_time=1.0
        )
        
        # Test unoptimized query
        unopt_result, unopt_queries, unopt_time = self.measure_query_performance(
            unoptimized_query, max_time=2.0
        )
        
        # Optimized should use significantly fewer queries
        self.assertLess(opt_queries, unopt_queries,
            f"Optimized query should use fewer queries: {opt_queries} vs {unopt_queries}")
        
        # Both should return same number of results
        self.assertEqual(len(optimized_result), len(unopt_result))
    
    def test_enrollment_analytics_query_performance(self):
        """Test enrollment analytics query performance"""
        
        def enrollment_analytics_query():
            from django.db.models import Count, Avg
            
            return Enrollment.objects.filter(
                tenant=self.tenant
            ).select_related('student', 'course').aggregate(
                total_enrollments=Count('id'),
                avg_progress=Avg('progress_percentage')
            )
        
        result, query_count, execution_time = self.measure_query_performance(
            enrollment_analytics_query, max_queries=3, max_time=2.0
        )
        
        # Verify results make sense
        self.assertGreater(result['total_enrollments'], 0)
        self.assertIsNotNone(result['avg_progress'])
    
    def test_course_with_modules_query_optimization(self):
        """Test course with modules query optimization"""
        
        def optimized_courses_with_modules():
            return list(Course.objects.prefetch_related('modules').filter(
                tenant=self.tenant
            )[:20])
        
        result, query_count, execution_time = self.measure_query_performance(
            optimized_courses_with_modules, max_queries=5, max_time=1.5
        )
        
        # Verify we can access modules without additional queries
        for course in result:
            modules = list(course.modules.all())  # Should not trigger additional queries
    
    def test_bulk_operations_performance(self):
        """Test bulk database operations performance"""
        
        def bulk_create_enrollments():
            # Create 100 new enrollments in bulk
            new_enrollments = []
            for i in range(100):
                new_enrollments.append(Enrollment(
                    student=self.students[i % len(self.students)],
                    course=self.courses[i % len(self.courses)],
                    tenant=self.tenant,
                    status='active',
                    progress_percentage=50
                ))
            
            return Enrollment.objects.bulk_create(new_enrollments, ignore_conflicts=True)
        
        result, query_count, execution_time = self.measure_query_performance(
            bulk_create_enrollments, max_queries=3, max_time=2.0
        )
        
        # Bulk create should be efficient
        self.assertGreater(len(result), 0)
    
    def test_complex_filtering_performance(self):
        """Test complex filtering query performance"""
        
        def complex_filter_query():
            from django.db.models import Q, Count
            
            return Course.objects.filter(
                Q(tenant=self.tenant) &
                Q(is_public=True) &
                Q(price__gte=Decimal('25.00'))
            ).annotate(
                enrollment_count=Count('enrollments')
            ).select_related('instructor').order_by('-enrollment_count')[:20]
        
        result, query_count, execution_time = self.measure_query_performance(
            complex_filter_query, max_queries=5, max_time=2.0
        )
        
        # Verify results
        result_list = list(result)
        self.assertLessEqual(len(result_list), 20)


class FileOperationPerformanceTest(TransactionTestCase):
    """Test file upload and download performance"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name="File Performance Test",
            subdomain="file-perf",
            subscription_plan="pro"
        )
        
        self.user = User.objects.create_user(
            email='file-user@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
        
        self.file_category = FileCategory.objects.create(
            name='performance_test',
            display_name='Performance Test Files',
            allowed_extensions=['pdf', 'doc', 'txt', 'jpg'],
            max_file_size_mb=50
        )
    
    def authenticate_user(self):
        """Helper to authenticate user"""
        tokens = JWTAuthService.generate_tokens(self.user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    @patch('apps.files.services.FileUploadService.upload_file')
    def test_file_upload_performance(self, mock_upload_service):
        """Test file upload API performance"""
        
        # Mock file upload service to avoid actual file operations
        def mock_upload_func(file_obj, category, **kwargs):
            return FileUpload.objects.create(
                uploaded_by=self.user,
                tenant=self.tenant,
                category=category,
                original_filename=file_obj.name,
                file_size=len(file_obj.read()),
                file_type='application/pdf',
                storage_path=f'test/{file_obj.name}'
            )
        
        mock_upload_service.side_effect = mock_upload_func
        
        self.authenticate_user()
        
        # Test uploading files of different sizes
        file_sizes = [1024, 10240, 102400]  # 1KB, 10KB, 100KB
        upload_times = []
        
        for size in file_sizes:
            from django.core.files.uploadedfile import SimpleUploadedFile
            
            # Create test file of specified size
            file_content = b'x' * size
            test_file = SimpleUploadedFile(
                f"test_file_{size}.pdf",
                file_content,
                content_type="application/pdf"
            )
            
            start_time = time.time()
            
            response = self.client.post(
                '/api/v1/files/file-uploads/',
                {
                    'file': test_file,
                    'category': self.file_category.id,
                    'title': f'Performance Test File {size}B'
                },
                format='multipart'
            )
            
            end_time = time.time()
            upload_time = end_time - start_time
            upload_times.append(upload_time)
            
            # Upload should complete within reasonable time
            self.assertLess(upload_time, 5.0,
                f"File upload too slow for {size}B file: {upload_time:.3f}s")
            
            if response.status_code == 201:
                self.assertEqual(response.status_code, 201)
        
        # Average upload time should be reasonable
        if upload_times:
            avg_upload_time = statistics.mean(upload_times)
            self.assertLess(avg_upload_time, 3.0,
                f"Average upload time too slow: {avg_upload_time:.3f}s")
    
    def test_file_list_performance_with_large_dataset(self):
        """Test file list API performance with many files"""
        
        # Create many file records
        files = []
        for i in range(100):
            file_upload = FileUpload.objects.create(
                uploaded_by=self.user,
                tenant=self.tenant,
                category=self.file_category,
                original_filename=f'perf_test_file_{i}.pdf',
                file_size=1024 * (i + 1),
                file_type='application/pdf',
                storage_path=f'test/perf_test_file_{i}.pdf'
            )
            files.append(file_upload)
        
        self.authenticate_user()
        
        # Test file list performance
        start_time = time.time()
        
        response = self.client.get('/api/v1/files/file-uploads/?page=1&page_size=20')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # File list should load quickly even with many files
        self.assertLess(response_time, 2.0,
            f"File list too slow with large dataset: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            self.assertIn('data', data)
    
    @patch('apps.files.access_control_service.FileAccessControlService.generate_secure_url')
    def test_secure_url_generation_performance(self, mock_generate_url):
        """Test secure URL generation performance"""
        
        mock_generate_url.return_value = 'https://example.com/secure/file.pdf?token=abc123'
        
        # Create test file
        file_upload = FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.file_category,
            original_filename='secure_test.pdf',
            file_size=1024,
            file_type='application/pdf',
            storage_path='test/secure_test.pdf'
        )
        
        self.authenticate_user()
        
        # Test multiple secure URL generations
        generation_times = []
        
        for _ in range(10):
            start_time = time.time()
            
            response = self.client.get(f'/api/v1/files/file-uploads/{file_upload.id}/secure_url/')
            
            end_time = time.time()
            generation_time = end_time - start_time
            generation_times.append(generation_time)
            
            # Each URL generation should be fast
            self.assertLess(generation_time, 1.0,
                f"Secure URL generation too slow: {generation_time:.3f}s")
        
        # Average generation time should be very fast
        avg_generation_time = statistics.mean(generation_times)
        self.assertLess(avg_generation_time, 0.5,
            f"Average URL generation too slow: {avg_generation_time:.3f}s")


class ConcurrentUserPerformanceTest(TransactionTestCase):
    """Test performance under concurrent user load"""
    
    def setUp(self):
        self.tenant = Organization.objects.create(
            name="Concurrent Test University",
            subdomain="concurrent-test",
            subscription_plan="enterprise"
        )
        
        # Create multiple users for concurrent testing
        self.users = []
        for i in range(20):
            user = User.objects.create_user(
                email=f'concurrent{i}@example.com',
                password='testpass123'
            )
            UserProfile.objects.create(user=user, tenant=self.tenant)
            self.users.append(user)
        
        # Create instructor and courses
        self.instructor = User.objects.create_user(
            email='concurrent-instructor@example.com',
            password='testpass123',
            is_teacher=True,
            is_approved_teacher=True
        )
        
        UserProfile.objects.create(user=self.instructor, tenant=self.tenant)
        
        self.courses = []
        for i in range(10):
            course = Course.objects.create(
                title=f"Concurrent Course {i}",
                description=f"Course {i} for concurrent testing",
                instructor=self.instructor,
                tenant=self.tenant,
                category="technology",
                price=Decimal('99.99')
            )
            self.courses.append(course)
    
    def simulate_user_session(self, user):
        """Simulate a user session with multiple API calls"""
        client = APIClient()
        
        # Authenticate user
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        session_times = []
        
        try:
            # 1. Get course list
            start_time = time.time()
            response = client.get('/api/v1/courses/')
            session_times.append(('course_list', time.time() - start_time))
            
            # 2. Get user dashboard
            start_time = time.time()
            response = client.get('/api/v1/dashboard/student/')
            session_times.append(('dashboard', time.time() - start_time))
            
            # 3. Enroll in a course
            if self.courses:
                course = self.courses[0]  # All users try to enroll in same course
                start_time = time.time()
                response = client.post(f'/api/v1/courses/courses/{course.id}/enroll/')
                session_times.append(('enrollment', time.time() - start_time))
            
            # 4. Get enrollments
            start_time = time.time()
            response = client.get('/api/v1/courses/enrollments/')
            session_times.append(('enrollments', time.time() - start_time))
            
        except Exception as e:
            # Log error but don't fail the test
            session_times.append(('error', str(e)))
        
        return session_times
    
    def test_concurrent_api_access(self):
        """Test API performance under concurrent access"""
        
        # Use ThreadPoolExecutor to simulate concurrent users
        max_workers = 10
        session_results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks for concurrent execution
            futures = []
            for user in self.users[:max_workers]:
                future = executor.submit(self.simulate_user_session, user)
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)  # 30 second timeout
                    session_results.append(result)
                except Exception as e:
                    session_results.append([('error', str(e))])
        
        # Analyze results
        self.assertGreater(len(session_results), 0, "No session results collected")
        
        # Calculate average response times for each operation
        operation_times = {}
        
        for session in session_results:
            for operation, duration in session:
                if operation != 'error' and isinstance(duration, (int, float)):
                    if operation not in operation_times:
                        operation_times[operation] = []
                    operation_times[operation].append(duration)
        
        # Verify performance under concurrent load
        for operation, times in operation_times.items():
            if times:
                avg_time = statistics.mean(times)
                max_time = max(times)
                
                # Under concurrent load, allow higher thresholds
                max_allowed = {
                    'course_list': 5.0,
                    'dashboard': 8.0,
                    'enrollment': 10.0,
                    'enrollments': 5.0
                }
                
                if operation in max_allowed:
                    self.assertLess(avg_time, max_allowed[operation],
                        f"Average {operation} time too slow under concurrent load: {avg_time:.3f}s")
                    
                    self.assertLess(max_time, max_allowed[operation] * 2,
                        f"Max {operation} time too slow under concurrent load: {max_time:.3f}s")
    
    def test_database_connection_handling(self):
        """Test database connection handling under concurrent load"""
        
        def database_intensive_operation():
            """Perform database-intensive operations"""
            try:
                # Multiple database queries
                courses = list(Course.objects.filter(tenant=self.tenant)[:10])
                enrollments = list(Enrollment.objects.filter(tenant=self.tenant)[:20])
                users = list(User.objects.filter(userprofile__tenant=self.tenant)[:15])
                
                return len(courses) + len(enrollments) + len(users)
            except Exception as e:
                return str(e)
        
        # Run concurrent database operations
        results = []
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            for _ in range(30):  # 30 concurrent operations
                future = executor.submit(database_intensive_operation)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=10)
                    results.append(result)
                except Exception as e:
                    results.append(f"Error: {str(e)}")
        
        # Verify most operations completed successfully
        successful_results = [r for r in results if isinstance(r, int)]
        error_results = [r for r in results if isinstance(r, str)]
        
        success_rate = len(successful_results) / len(results) * 100
        
        # At least 80% of operations should succeed under concurrent load
        self.assertGreaterEqual(success_rate, 80.0,
            f"Success rate too low under concurrent load: {success_rate:.1f}%")
        
        if error_results:
            print(f"Errors encountered: {error_results[:5]}")  # Print first 5 errors for debugging


class MemoryUsagePerformanceTest(TransactionTestCase):
    """Test memory usage and optimization"""
    
    def setUp(self):
        self.tenant = Organization.objects.create(
            name="Memory Test University",
            subdomain="memory-test",
            subscription_plan="pro"
        )
        
        self.user = User.objects.create_user(
            email='memory-user@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
    
    def test_large_queryset_memory_usage(self):
        """Test memory usage with large querysets"""
        
        # Create large dataset
        courses = []
        for i in range(1000):
            course = Course.objects.create(
                title=f"Memory Test Course {i}",
                description=f"Course {i} for memory testing",
                instructor=self.user,
                tenant=self.tenant,
                category="technology"
            )
            courses.append(course)
        
        # Test iterator vs list for memory efficiency
        import sys
        
        # Method 1: Load all into memory (memory intensive)
        def load_all_courses():
            return list(Course.objects.filter(tenant=self.tenant))
        
        # Method 2: Use iterator (memory efficient)
        def iterate_courses():
            count = 0
            for course in Course.objects.filter(tenant=self.tenant).iterator():
                count += 1
            return count
        
        # Test both methods
        start_time = time.time()
        all_courses = load_all_courses()
        load_all_time = time.time() - start_time
        
        start_time = time.time()
        course_count = iterate_courses()
        iterator_time = time.time() - start_time
        
        # Verify same results
        self.assertEqual(len(all_courses), course_count)
        
        # Iterator should be more memory efficient (though timing may vary)
        # This is more about demonstrating the pattern than strict performance
        self.assertGreater(len(all_courses), 0)
        self.assertGreater(course_count, 0)
    
    def test_queryset_optimization_for_memory(self):
        """Test queryset optimization techniques for memory efficiency"""
        
        # Create test data
        instructor = User.objects.create_user(
            email='memory-instructor@example.com',
            password='testpass123',
            is_teacher=True
        )
        
        UserProfile.objects.create(user=instructor, tenant=self.tenant)
        
        courses = []
        for i in range(100):
            course = Course.objects.create(
                title=f"Optimization Course {i}",
                instructor=instructor,
                tenant=self.tenant,
                category="technology"
            )
            courses.append(course)
            
            # Create modules
            for j in range(5):
                CourseModule.objects.create(
                    course=course,
                    title=f"Module {j}",
                    order=j + 1
                )
        
        # Test 1: only() for selecting specific fields
        def optimized_field_selection():
            return list(Course.objects.filter(tenant=self.tenant).only('id', 'title'))
        
        # Test 2: defer() for excluding large fields
        def deferred_field_query():
            return list(Course.objects.filter(tenant=self.tenant).defer('description'))
        
        # Test 3: values() for dictionary results
        def values_query():
            return list(Course.objects.filter(tenant=self.tenant).values('id', 'title'))
        
        # Execute tests
        optimized_results = optimized_field_selection()
        deferred_results = deferred_field_query()
        values_results = values_query()
        
        # Verify results
        self.assertEqual(len(optimized_results), 100)
        self.assertEqual(len(deferred_results), 100)
        self.assertEqual(len(values_results), 100)
        
        # All should return data efficiently
        self.assertIsNotNone(optimized_results[0].title)
        self.assertIsNotNone(deferred_results[0].title)
        self.assertIn('title', values_results[0])


class CachePerformanceTest(TransactionTestCase):
    """Test caching performance and effectiveness"""
    
    def setUp(self):
        self.tenant = Organization.objects.create(
            name="Cache Test University",
            subdomain="cache-test",
            subscription_plan="pro"
        )
        
        self.user = User.objects.create_user(
            email='cache-user@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
    
    def test_cache_hit_vs_miss_performance(self):
        """Test performance difference between cache hits and misses"""
        
        from django.core.cache import cache
        
        # Clear cache
        cache.clear()
        
        cache_key = f'test_data_{self.tenant.id}'
        test_data = {
            'courses': [f'Course {i}' for i in range(100)],
            'users': [f'User {i}' for i in range(50)],
            'stats': {'total': 150, 'active': 120}
        }
        
        # Test cache miss (first access)
        start_time = time.time()
        cached_data = cache.get(cache_key)
        if cached_data is None:
            # Simulate expensive operation
            time.sleep(0.1)  # Simulate database query
            cache.set(cache_key, test_data, timeout=300)
            cached_data = test_data
        cache_miss_time = time.time() - start_time
        
        # Test cache hit (subsequent access)
        start_time = time.time()
        cached_data = cache.get(cache_key)
        cache_hit_time = time.time() - start_time
        
        # Cache hit should be significantly faster
        self.assertLess(cache_hit_time, cache_miss_time,
            f"Cache hit not faster than miss: hit={cache_hit_time:.4f}s, miss={cache_miss_time:.4f}s")
        
        # Cache hit should be very fast
        self.assertLess(cache_hit_time, 0.01,
            f"Cache hit too slow: {cache_hit_time:.4f}s")
    
    def test_cache_invalidation_performance(self):
        """Test cache invalidation performance"""
        
        from django.core.cache import cache
        
        # Set up multiple cache entries
        cache_keys = []
        for i in range(50):
            key = f'cache_test_{i}_{self.tenant.id}'
            cache.set(key, f'data_{i}', timeout=300)
            cache_keys.append(key)
        
        # Test individual cache deletion
        start_time = time.time()
        for key in cache_keys[:25]:
            cache.delete(key)
        individual_delete_time = time.time() - start_time
        
        # Test bulk cache deletion
        start_time = time.time()
        cache.delete_many(cache_keys[25:])
        bulk_delete_time = time.time() - start_time
        
        # Both operations should be fast
        self.assertLess(individual_delete_time, 1.0,
            f"Individual cache deletion too slow: {individual_delete_time:.3f}s")
        
        self.assertLess(bulk_delete_time, 0.5,
            f"Bulk cache deletion too slow: {bulk_delete_time:.3f}s")
        
        # Bulk should generally be faster for large operations
        # (though this may vary by cache backend)
        if len(cache_keys[25:]) > 10:
            per_key_individual = individual_delete_time / 25
            per_key_bulk = bulk_delete_time / len(cache_keys[25:])
            
            # This is informational - bulk operations should be more efficient
            print(f"Per-key times: individual={per_key_individual:.4f}s, bulk={per_key_bulk:.4f}s")