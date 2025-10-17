from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView,
    GoogleOAuth2LoginView, TokenRefreshWithTenantView
)

# Note: ViewSets are registered in the centralized API router (apps/api/urls.py)
# This file only contains non-ViewSet endpoints like authentication views

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/google/', GoogleOAuth2LoginView.as_view(), name='google_oauth2_login'),
    
    # JWT Token endpoints
    path('auth/token/refresh/', TokenRefreshWithTenantView.as_view(), name='token_refresh'),
    
    # dj-rest-auth endpoints
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/social/', include('allauth.socialaccount.urls')),
]