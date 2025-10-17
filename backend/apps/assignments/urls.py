from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AssignmentViewSet, SubmissionViewSet, CertificateViewSet, CourseProgressViewSet
)

# Create router for assignment ViewSets
router = DefaultRouter()
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'certificates', CertificateViewSet, basename='certificate')
router.register(r'course-progress', CourseProgressViewSet, basename='courseprogress')

urlpatterns = [
    # Include all ViewSet routes
    path('', include(router.urls)),
    
    # Additional custom endpoints can be added here if needed
    # For example:
    # path('bulk-operations/', BulkOperationsView.as_view(), name='bulk-operations'),
]