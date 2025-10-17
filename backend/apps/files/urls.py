from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FileCategoryViewSet, FileUploadViewSet, 
    FileAccessLogViewSet, FileProcessingJobViewSet,
    SecureFileDownloadView, FilePermissionsView
)

# Create router for file management endpoints
router = DefaultRouter()
router.register(r'categories', FileCategoryViewSet, basename='filecategory')
router.register(r'uploads', FileUploadViewSet, basename='fileupload')
router.register(r'access-logs', FileAccessLogViewSet, basename='fileaccesslog')
router.register(r'processing-jobs', FileProcessingJobViewSet, basename='fileprocessingjob')

urlpatterns = [
    # File management API endpoints
    path('', include(router.urls)),
    
    # Secure file access endpoints
    path('secure-download/<uuid:file_id>/', SecureFileDownloadView.as_view(), name='secure-file-download'),
    path('permissions/<uuid:file_id>/', FilePermissionsView.as_view(), name='file-permissions'),
    path('permissions/bulk/', FilePermissionsView.as_view(), name='bulk-file-permissions'),
]