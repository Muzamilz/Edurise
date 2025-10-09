from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView,
    UserViewSet, UserProfileViewSet, TeacherApprovalViewSet, OrganizationViewSet,
    GoogleOAuth2LoginView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='userprofile')
router.register(r'teacher-approvals', TeacherApprovalViewSet, basename='teacherapproval')
router.register(r'organizations', OrganizationViewSet, basename='organization')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/google/', GoogleOAuth2LoginView.as_view(), name='google_oauth2_login'),
    
    # dj-rest-auth endpoints
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/social/', include('allauth.socialaccount.urls')),
    
    # Include router URLs
    path('', include(router.urls)),
]