from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, LiveClassViewSet, CourseModuleViewSet,
    CourseReviewViewSet, EnrollmentViewSet, WishlistViewSet, RecommendationViewSet,
    OrganizationViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'live-classes', LiveClassViewSet, basename='liveclass')
router.register(r'modules', CourseModuleViewSet, basename='coursemodule')
router.register(r'reviews', CourseReviewViewSet, basename='coursereview')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')
router.register(r'organizations', OrganizationViewSet, basename='organization')

urlpatterns = [
    path('', include(router.urls)),
]