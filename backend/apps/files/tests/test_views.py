from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock
from apps.accounts.models import Organization, UserProfile
from apps.courses.models import Course
from apps.files.models import FileCategory, FileUpload, FileAccessLog
from apps.accounts.services import JWTAuthService

User = get_user_model()


class FileCategoryViewSetTest(TestCase):
    """Test cases for FileCategoryViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
        
        # Create test categories
        FileCategory.objects.create(
            name='documents',
            display_name='Documents',
            allowed_extensions=['pdf', 'doc', 'docx'],
            max_file_size_mb=10
        )
        
        FileCategory.objects.create(
            name='images',
            display_name='Images',
            allowed_extensions=['jpg', 'jpeg', 'png', 'gif'],
            max_file_size_mb=5
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_list_file_categories(self):
        """Test listing file categories"""
        self.authenticate_user(self.user)
        
        response = self.client.get('/api/v1/files/file-categories/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(len(data['data']), 2)
        category_names = [cat['name'] for cat in data['data']]
        self.assertIn('documents', category_names)
        self.assertIn('images', category_names)


class FileUploadViewSetTest(TestCase):
    """Test cases for FileUploadViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
        UserProfile.objects.create(user=self.other_user, tenant=self.tenant)
        UserProfile.objects.create(user=self.admin_user, tenant=self.tenant)
        
        self.category = FileCategory.objects.create(
            name='documents',
            display_name='Documents',
            allowed_extensions=['pdf', 'txt'],
            max_file_size_mb=10
        )
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            instructor=self.user,
            tenant=self.tenant,
            category='technology'
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    @patch('apps.files.services.FileUploadService.upload_file')
    def test_upload_file(self, mock_upload_file):
        """Test file upload"""
        # Create mock file upload
        mock_file_upload = Mock()
        mock_file_upload.id = 'test-file-id'
        mock_file_upload.original_filename = 'test.pdf'
        mock_file_upload.file_size = 1024
        mock_upload_file.return_value = mock_file_upload
        
        # Create test file
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/files/file-uploads/',
            {
                'file': test_file,
                'category': self.category.id,
                'title': 'Test Document',
                'description': 'A test document',
                'access_level': 'private'
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_upload_file.assert_called_once()
    
    def test_upload_file_missing_data(self):
        """Test file upload with missing required data"""
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/files/file-uploads/',
            {
                'title': 'Test Document'
                # Missing file and category
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_files(self):
        """Test listing files"""
        # Create test file
        file_upload = FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='test.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.get('/api/v1/files/file-uploads/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(len(data['data']['results']), 1)
        self.assertEqual(data['data']['results'][0]['original_filename'], 'test.pdf')
    
    def test_retrieve_file_details(self):
        """Test retrieving file details"""
        file_upload = FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='test.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.get(f'/api/v1/files/file-uploads/{file_upload.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['data']['original_filename'], 'test.pdf')
        self.assertEqual(data['data']['access_level'], 'private')
    
    def test_retrieve_file_permission_denied(self):
        """Test retrieving file without permission"""
        file_upload = FileUpload.objects.create(
            uploaded_by=self.other_user,
            tenant=self.tenant,
            category=self.category,
            original_filename='private.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.get(f'/api/v1/files/file-uploads/{file_upload.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_file_metadata(self):
        """Test updating file metadata"""
        file_upload = FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='test.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private',
            title='Original Title'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.patch(
            f'/api/v1/files/file-uploads/{file_upload.id}/',
            {
                'title': 'Updated Title',
                'description': 'Updated description'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify update
        file_upload.refresh_from_db()
        self.assertEqual(file_upload.title, 'Updated Title')
    
    def test_update_file_permission_denied(self):
        """Test updating file without permission"""
        file_upload = FileUpload.objects.create(
            uploaded_by=self.other_user,
            tenant=self.tenant,
            category=self.category,
            original_filename='test.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.patch(
            f'/api/v1/files/file-uploads/{file_upload.id}/',
            {
                'title': 'Hacked Title'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('apps.files.services.FileUploadService.delete_file')
    def test_delete_file(self, mock_delete_file):
        """Test file deletion"""
        file_upload = FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='test.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.delete(f'/api/v1/files/file-uploads/{file_upload.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_delete_file.assert_called_once_with(file_upload, self.user, hard_delete=False)
    
    @patch('apps.files.access_control_service.FileAccessControlService.generate_secure_url')
    def test_secure_url_generation(self, mock_generate_url):
        """Test secure URL generation"""
        mock_generate_url.return_value = 'https://example.com/secure/download/token123'
        
        file_upload = FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='test.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.get(f'/api/v1/files/file-uploads/{file_upload.id}/secure_url/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('secure_url', data['data'])
        self.assertIn('expires_in', data['data'])
    
    @patch('apps.files.access_control_service.FileAccessControlService.generate_secure_url')
    @patch('apps.files.access_control_service.FileAccessControlService.check_file_access')
    def test_secure_url_access_denied(self, mock_check_access, mock_generate_url):
        """Test secure URL generation when access is denied"""
        mock_generate_url.return_value = None
        mock_check_access.return_value = {
            'reason': 'Subscription required',
            'restrictions': ['premium_feature'],
            'subscription_required': True,
            'upgrade_url': 'https://example.com/upgrade'
        }
        
        file_upload = FileUpload.objects.create(
            uploaded_by=self.other_user,
            tenant=self.tenant,
            category=self.category,
            original_filename='premium.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='premium'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.get(f'/api/v1/files/file-uploads/{file_upload.id}/secure_url/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        data = response.json()
        
        self.assertIn('errors', data)
        self.assertEqual(data['errors']['subscription_required'], True)
    
    def test_my_files(self):
        """Test getting user's own files"""
        # Create files for different users
        user_file = FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='my_file.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        FileUpload.objects.create(
            uploaded_by=self.other_user,
            tenant=self.tenant,
            category=self.category,
            original_filename='other_file.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.get('/api/v1/files/file-uploads/my_files/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should only return user's own files
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['original_filename'], 'my_file.pdf')
    
    def test_course_files(self):
        """Test getting files for a specific course"""
        course_file = FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            course=self.course,
            original_filename='course_material.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='course'
        )
        
        # File not associated with course
        FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='other_file.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.get(
            f'/api/v1/files/file-uploads/course_files/?course_id={self.course.id}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should only return course files
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['original_filename'], 'course_material.pdf')
    
    def test_course_files_missing_course_id(self):
        """Test getting course files without course_id parameter"""
        self.authenticate_user(self.user)
        
        response = self.client.get('/api/v1/files/file-uploads/course_files/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_bulk_delete_files(self):
        """Test bulk deleting files"""
        file1 = FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='file1.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        file2 = FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='file2.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        # File owned by other user (should not be deleted)
        other_file = FileUpload.objects.create(
            uploaded_by=self.other_user,
            tenant=self.tenant,
            category=self.category,
            original_filename='other.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.post(
            '/api/v1/files/file-uploads/bulk_delete/',
            {
                'file_ids': [str(file1.id), str(file2.id), str(other_file.id)]
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should only delete user's own files
        self.assertEqual(data['data']['deleted_count'], 2)
    
    def test_file_analytics(self):
        """Test getting file analytics"""
        # Create test files
        FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='doc1.pdf',
            file_size=1024 * 1024,  # 1MB
            file_type='application/pdf',
            access_level='private',
            download_count=5
        )
        
        FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='doc2.pdf',
            file_size=2 * 1024 * 1024,  # 2MB
            file_type='application/pdf',
            access_level='private',
            download_count=10
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.get('/api/v1/files/file-uploads/analytics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('summary', data['data'])
        self.assertEqual(data['data']['summary']['total_files'], 2)
        self.assertEqual(data['data']['summary']['total_downloads'], 15)
        self.assertIn('by_category', data['data'])
        self.assertIn('popular_files', data['data'])
    
    def test_file_search(self):
        """Test file search functionality"""
        # Create test files
        FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='python_tutorial.pdf',
            title='Python Programming Tutorial',
            description='Learn Python basics',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='javascript_guide.pdf',
            title='JavaScript Guide',
            description='Advanced JavaScript concepts',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        self.authenticate_user(self.user)
        
        # Search by filename
        response = self.client.get('/api/v1/files/file-uploads/search/?q=python')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['original_filename'], 'python_tutorial.pdf')
    
    @patch('apps.files.access_control_service.FileAccessControlService.check_file_sharing_permissions')
    def test_share_file(self, mock_check_sharing):
        """Test sharing file with other users"""
        mock_check_sharing.return_value = {
            'can_share': True,
            'allowed_users': [{'user_id': str(self.other_user.id), 'email': self.other_user.email}],
            'denied_users': []
        }
        
        file_upload = FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='shared.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
        
        self.authenticate_user(self.user)
        
        response = self.client.post(
            f'/api/v1/files/file-uploads/{file_upload.id}/share/',
            {
                'user_emails': [self.other_user.email]
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('shared_with', data['data'])
        self.assertEqual(len(data['data']['shared_with']), 1)


class SecureFileDownloadViewTest(TestCase):
    """Test cases for SecureFileDownloadView"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.tenant = Organization.objects.create(
            name='Test University',
            subdomain='testuni',
            subscription_plan='pro'
        )
        
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        
        UserProfile.objects.create(user=self.user, tenant=self.tenant)
        
        self.category = FileCategory.objects.create(
            name='documents',
            display_name='Documents',
            allowed_extensions=['pdf'],
            max_file_size_mb=10
        )
        
        self.file_upload = FileUpload.objects.create(
            uploaded_by=self.user,
            tenant=self.tenant,
            category=self.category,
            original_filename='test.pdf',
            file_size=1024,
            file_type='application/pdf',
            access_level='private'
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate user"""
        tokens = JWTAuthService.generate_tokens(user, self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_secure_download_missing_token(self):
        """Test secure download without token"""
        self.authenticate_user(self.user)
        
        response = self.client.get(f'/api/v1/files/secure-download/{self.file_upload.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('apps.files.access_control_service.FileAccessControlService.verify_secure_token')
    @patch('apps.files.access_control_service.FileAccessControlService.check_file_access')
    @patch('apps.files.access_control_service.FileAccessControlService.log_file_access')
    def test_secure_download_invalid_token(self, mock_log_access, mock_check_access, mock_verify_token):
        """Test secure download with invalid token"""
        mock_verify_token.return_value = {'valid': False, 'reason': 'Token expired'}
        
        self.authenticate_user(self.user)
        
        response = self.client.get(
            f'/api/v1/files/secure-download/{self.file_upload.id}/?token=invalid&expires=123456789'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_log_access.assert_called_once()
    
    @patch('apps.files.access_control_service.FileAccessControlService.verify_secure_token')
    @patch('apps.files.access_control_service.FileAccessControlService.check_file_access')
    @patch('apps.files.access_control_service.FileAccessControlService.log_file_access')
    def test_secure_download_success(self, mock_log_access, mock_check_access, mock_verify_token):
        """Test successful secure download"""
        mock_verify_token.return_value = {'valid': True}
        mock_check_access.return_value = {'allowed': True}
        
        # Mock file content
        with patch.object(self.file_upload, 'file') as mock_file:
            mock_file.read.return_value = b'test file content'
            mock_file.name = 'test.pdf'
            
            self.authenticate_user(self.user)
            
            response = self.client.get(
                f'/api/v1/files/secure-download/{self.file_upload.id}/?token=valid&expires=123456789'
            )
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response['Content-Type'], 'application/pdf')
            mock_log_access.assert_called_once()