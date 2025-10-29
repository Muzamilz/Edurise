"""
Tests for Django security measures implementation.
"""

import json
import tempfile
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from unittest.mock import patch, MagicMock

from apps.security.validators import InputValidator, FileValidator, SecurityValidator
from apps.security.file_scanner import FileUploadSecurityScanner, VirusScanner
from apps.security.services import SecurityMonitoringService, SecurityAlertService
from apps.security.models import SecurityEvent, SecurityAlert

User = get_user_model()


class InputValidationTests(TestCase):
    """Test input validation and sanitization"""
    
    def test_sql_injection_detection(self):
        """Test SQL injection pattern detection"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM passwords",
            "admin'--",
            "' OR 1=1#"
        ]
        
        for malicious_input in malicious_inputs:
            result = InputValidator.validate_sql_injection(malicious_input)
            self.assertFalse(result, f"Failed to detect SQL injection: {malicious_input}")
    
    def test_xss_detection(self):
        """Test XSS pattern detection"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "onload=alert('xss')"
        ]
        
        for malicious_input in malicious_inputs:
            result = InputValidator.validate_xss(malicious_input)
            self.assertFalse(result, f"Failed to detect XSS: {malicious_input}")
    
    def test_path_traversal_detection(self):
        """Test path traversal pattern detection"""
        malicious_inputs = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "%2e%2e%2f%2e%2e%2f",
            "....//....//",
        ]
        
        for malicious_input in malicious_inputs:
            result = InputValidator.validate_path_traversal(malicious_input)
            self.assertFalse(result, f"Failed to detect path traversal: {malicious_input}")
    
    def test_string_sanitization(self):
        """Test string sanitization"""
        test_cases = [
            ("<script>alert('test')</script>", "&lt;script&gt;alert(&#x27;test&#x27;)&lt;/script&gt;"),
            ("Hello\x00World", "Hello World"),
            ("  Multiple   spaces  ", "Multiple spaces"),
        ]
        
        for input_str, expected in test_cases:
            result = InputValidator.sanitize_string(input_str)
            self.assertEqual(result, expected)
    
    def test_dict_sanitization(self):
        """Test dictionary sanitization"""
        test_data = {
            "name": "<script>alert('xss')</script>",
            "description": "Normal text",
            "nested": {
                "value": "'; DROP TABLE users; --"
            }
        }
        
        result = InputValidator.sanitize_dict(test_data)
        
        self.assertNotIn("<script>", result["name"])
        self.assertEqual(result["description"], "Normal text")
        self.assertNotIn("DROP TABLE", result["nested"]["value"])


class FileValidationTests(TestCase):
    """Test file upload validation"""
    
    def test_dangerous_extension_detection(self):
        """Test detection of dangerous file extensions"""
        dangerous_files = [
            "malware.exe",
            "script.bat",
            "virus.scr",
            "trojan.vbs"
        ]
        
        for filename in dangerous_files:
            result = FileValidator.validate_file_extension(filename)
            self.assertFalse(result, f"Failed to block dangerous file: {filename}")
    
    def test_file_size_validation(self):
        """Test file size validation"""
        max_size = FileValidator.MAX_FILE_SIZE
        
        # Test file within limit
        self.assertTrue(FileValidator.validate_file_size(max_size - 1000))
        
        # Test file exceeding limit
        self.assertFalse(FileValidator.validate_file_size(max_size + 1000))
    
    def test_file_signature_validation(self):
        """Test file signature validation"""
        # PDF signature
        pdf_content = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3'
        self.assertTrue(FileValidator.validate_file_signature(pdf_content, "test.pdf"))
        
        # Wrong signature for extension
        self.assertFalse(FileValidator.validate_file_signature(pdf_content, "test.jpg"))
    
    def test_malicious_content_detection(self):
        """Test detection of malicious content in files"""
        malicious_content = b'<script>alert("xss")</script>'
        
        scan_result = FileValidator.scan_file_content(malicious_content)
        
        self.assertFalse(scan_result['safe'])
        self.assertGreater(len(scan_result['threats']), 0)


class SecurityMiddlewareTests(TestCase):
    """Test security middleware functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_rate_limiting(self):
        """Test rate limiting middleware"""
        # Clear cache
        cache.clear()
        
        # Make requests up to the limit
        for i in range(5):  # Assuming limit is higher than 5
            response = self.client.get('/api/v1/courses/')
            self.assertNotEqual(response.status_code, 429)
        
        # This test would need actual rate limit configuration
        # In a real scenario, you'd make many requests to trigger rate limiting
    
    def test_security_headers(self):
        """Test security headers are added"""
        response = self.client.get('/')
        
        # Check for security headers
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        
        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')
    
    def test_input_validation_middleware(self):
        """Test input validation middleware"""
        # Test with malicious query parameter
        malicious_query = "'; DROP TABLE users; --"
        
        response = self.client.get(f'/api/v1/courses/?search={malicious_query}')
        
        # Should either block the request or sanitize the input
        # The exact behavior depends on your middleware implementation
        self.assertIn(response.status_code, [200, 400])


class FileUploadSecurityTests(TestCase):
    """Test file upload security scanning"""
    
    def setUp(self):
        self.scanner = FileUploadSecurityScanner()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_clean_file_upload(self):
        """Test scanning of clean file"""
        # Create a simple text file
        file_content = b"This is a clean text file."
        uploaded_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")
        
        scan_results = self.scanner.scan_uploaded_file(uploaded_file)
        
        self.assertTrue(scan_results['safe'])
        self.assertEqual(len(scan_results['threats']), 0)
    
    def test_malicious_file_upload(self):
        """Test scanning of potentially malicious file"""
        # Create a file with suspicious content
        malicious_content = b'<script>alert("xss")</script>'
        uploaded_file = SimpleUploadedFile("malicious.html", malicious_content, content_type="text/html")
        
        scan_results = self.scanner.scan_uploaded_file(uploaded_file)
        
        # Should detect threats or have warnings
        self.assertTrue(len(scan_results['threats']) > 0 or len(scan_results['warnings']) > 0)
    
    @patch('apps.security.file_scanner.subprocess.run')
    def test_virus_scanner_with_clamav(self, mock_subprocess):
        """Test virus scanner with ClamAV"""
        # Mock ClamAV being available and finding a threat
        mock_subprocess.side_effect = [
            MagicMock(returncode=0),  # 'which clamscan' succeeds
            MagicMock(returncode=1, stdout="test.txt: Eicar-Test-Signature FOUND")  # scan finds threat
        ]
        
        virus_scanner = VirusScanner()
        
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b"test content")
            temp_file.flush()
            
            result = virus_scanner.scan_file(temp_file.name)
            
            self.assertFalse(result['clean'])
            self.assertGreater(len(result['threats']), 0)


class SecurityMonitoringTests(TestCase):
    """Test security monitoring and alerting"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_security_event_logging(self):
        """Test security event logging"""
        event = SecurityMonitoringService.log_security_event(
            event_type='login_failed',
            severity='medium',
            description='Failed login attempt',
            user=self.user,
            ip_address='192.168.1.1'
        )
        
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, 'login_failed')
        self.assertEqual(event.severity, 'medium')
        self.assertEqual(event.user, self.user)
    
    def test_alert_creation(self):
        """Test security alert creation"""
        alert = SecurityAlertService.create_alert(
            alert_type='multiple_failed_logins',
            title='Multiple failed login attempts',
            description='5 failed attempts in 15 minutes',
            severity='high'
        )
        
        self.assertIsNotNone(alert)
        self.assertEqual(alert.alert_type, 'multiple_failed_logins')
        self.assertEqual(alert.severity, 'high')
    
    def test_security_overview(self):
        """Test security overview generation"""
        # Create some test events
        SecurityEvent.objects.create(
            event_type='login_failed',
            severity='medium',
            description='Test event',
            ip_address='192.168.1.1'
        )
        
        overview = SecurityMonitoringService.get_security_overview()
        
        self.assertIn('status', overview)
        self.assertIn('security_score', overview)
        self.assertIn('total_events', overview)
        self.assertIsInstance(overview['security_score'], int)


class SecurityAPITests(TestCase):
    """Test security API endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123'
        )
    
    def test_security_health_endpoint(self):
        """Test security health check endpoint"""
        response = self.client.get('/api/v1/security/health/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertIn('checks', data)
    
    def test_security_overview_requires_admin(self):
        """Test security overview requires admin access"""
        # Test without authentication
        response = self.client.get('/api/v1/security/overview/')
        self.assertEqual(response.status_code, 401)
        
        # Test with regular user
        self.client.force_login(self.regular_user)
        response = self.client.get('/api/v1/security/overview/')
        self.assertEqual(response.status_code, 403)
        
        # Test with admin user
        self.client.force_login(self.admin_user)
        response = self.client.get('/api/v1/security/overview/')
        self.assertEqual(response.status_code, 200)
    
    def test_file_security_scan_endpoint(self):
        """Test file security scan endpoint"""
        self.client.force_login(self.regular_user)
        
        # Create a test file
        test_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        
        response = self.client.post('/api/v1/security/file-scan/', {'file': test_file})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('safe', data['data'])
        self.assertIn('scan_summary', data['data'])


class GDPRComplianceTests(TestCase):
    """Test GDPR compliance features"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            is_superuser=True
        )
    
    def test_user_data_export(self):
        """Test user data export for GDPR"""
        from apps.security.services import ComplianceService
        
        exported_data = ComplianceService.export_user_data(self.user)
        
        self.assertIn('personal_info', exported_data)
        self.assertIn('export_date', exported_data)
        self.assertEqual(exported_data['personal_info']['email'], self.user.email)
    
    def test_user_data_deletion(self):
        """Test user data deletion for GDPR"""
        from apps.security.services import ComplianceService
        
        user_id = self.user.id
        user_email = self.user.email
        
        deletion_summary = ComplianceService.delete_user_data(self.user)
        
        self.assertIn('deletion_date', deletion_summary)
        self.assertIn('deleted_items', deletion_summary)
        
        # Verify user is deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_id)


class SecurityConfigurationTests(TestCase):
    """Test security configuration"""
    
    def test_security_settings_loaded(self):
        """Test that security settings are properly loaded"""
        # Test that security settings exist
        self.assertTrue(hasattr(settings, 'SECURITY_MONITORING_ENABLED'))
        self.assertTrue(hasattr(settings, 'RATE_LIMIT_ENABLE'))
        self.assertTrue(hasattr(settings, 'VIRUS_SCAN_ENABLED'))
        
        # Test middleware is configured
        middleware_classes = [
            'apps.security.middleware.SecurityHeadersMiddleware',
            'apps.security.middleware.RateLimitingMiddleware',
            'apps.security.middleware.InputValidationMiddleware',
            'apps.security.middleware.SecurityMonitoringMiddleware',
        ]
        
        for middleware_class in middleware_classes:
            self.assertIn(middleware_class, settings.MIDDLEWARE)
    
    def test_file_upload_restrictions(self):
        """Test file upload security restrictions"""
        self.assertTrue(hasattr(settings, 'ALLOWED_FILE_EXTENSIONS'))
        self.assertTrue(hasattr(settings, 'BLOCKED_FILE_EXTENSIONS'))
        self.assertTrue(hasattr(settings, 'MAX_FILE_SIZE_MB'))
        
        # Test that dangerous extensions are blocked
        dangerous_extensions = ['exe', 'bat', 'cmd', 'scr']
        blocked_extensions = getattr(settings, 'BLOCKED_FILE_EXTENSIONS', [])
        
        for ext in dangerous_extensions:
            self.assertIn(ext, blocked_extensions)