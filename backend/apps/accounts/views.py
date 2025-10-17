from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from django.utils import timezone
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from .models import UserProfile, TeacherApproval, Organization
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    UserProfileSerializer, TeacherApprovalSerializer, OrganizationSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer, GoogleOAuth2Serializer
)
from .services import AuthService, JWTAuthService, TenantService

User = get_user_model()


class RegisterView(APIView):
    """User registration view"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Get tenant from request if available
            tenant = getattr(request, 'tenant', None)
            if tenant:
                TenantService.add_user_to_tenant(user, tenant)
            
            # Generate tokens
            tokens = JWTAuthService.generate_tokens(user, tenant)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """Custom login view with tenant support"""
    
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tenant = getattr(request, 'tenant', None)
            
            # Generate tokens with tenant info
            tokens = JWTAuthService.generate_tokens(user, tenant)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': tokens
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """Password reset request view"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                AuthService.send_password_reset_email(user)
            except User.DoesNotExist:
                pass  # Don't reveal if email exists
            
            return Response({'message': 'Password reset email sent if account exists'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Password reset confirmation view"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            
            user = AuthService.reset_password(token, password)
            if user:
                return Response({'message': 'Password reset successful'})
            else:
                return Response(
                    {'error': 'Invalid or expired token'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Logout view that blacklists JWT tokens"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return User.objects.filter(profiles__tenant=self.request.tenant)
        return User.objects.all()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def tenants(self, request):
        """Get all tenants for current user"""
        tenants = TenantService.get_user_tenants(request.user)
        serializer = OrganizationSerializer(tenants, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def switch_tenant(self, request):
        """Switch to a different tenant context"""
        tenant_id = request.data.get('tenant_id')
        if not tenant_id:
            return Response({'error': 'tenant_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            tenant = Organization.objects.get(id=tenant_id, is_active=True)
            # Verify user has access to this tenant
            if not UserProfile.objects.filter(user=request.user, tenant=tenant).exists():
                return Response({'error': 'Access denied to this tenant'}, status=status.HTTP_403_FORBIDDEN)
            
            # Generate new tokens with the new tenant context
            tokens = JWTAuthService.generate_tokens(request.user, tenant)
            
            return Response({
                'message': 'Tenant switched successfully',
                'tenant': OrganizationSerializer(tenant).data,
                'tokens': tokens
            })
        except Organization.DoesNotExist:
            return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['patch'])
    def preferences(self, request):
        """Update user preferences"""
        preferences = request.data
        
        # Update user profile preferences
        if hasattr(request, 'tenant') and request.tenant:
            profile, created = UserProfile.objects.get_or_create(
                user=request.user,
                tenant=request.tenant,
                defaults={'role': 'teacher' if request.user.is_teacher else 'student'}
            )
            
            # Update profile fields if provided
            if 'language' in preferences:
                profile.language = preferences['language']
            if 'timezone' in preferences:
                profile.timezone = preferences['timezone']
            
            profile.save()
        
        # Store other preferences in user session or cache
        # For now, we'll just return success
        return Response({'message': 'Preferences updated successfully'})
    
    @action(detail=False, methods=['get'])
    def activity(self, request):
        """Get user activity log"""
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # For now, return mock data
        # In a real implementation, you would query an audit log table
        mock_activities = [
            {
                'id': '1',
                'action': 'Login',
                'timestamp': '2024-01-15T10:30:00Z',
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0...',
                'details': {'method': 'email'}
            },
            {
                'id': '2',
                'action': 'Profile Updated',
                'timestamp': '2024-01-14T15:45:00Z',
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0...',
                'details': {'fields': ['first_name', 'bio']}
            }
        ]
        
        return Response({
            'count': len(mock_activities),
            'next': None,
            'previous': None,
            'results': mock_activities
        })
    
    @action(detail=False, methods=['post'])
    def delete_account(self, request):
        """Delete user account (requires password confirmation)"""
        password = request.data.get('password')
        if not password:
            return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify password
        if not request.user.check_password(password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        
        # In a real implementation, you might want to:
        # 1. Anonymize the user data instead of deleting
        # 2. Send a confirmation email
        # 3. Add a grace period before actual deletion
        
        # For now, just return a success message
        return Response({'message': 'Account deletion request received'})
    
    @action(detail=False, methods=['get'])
    def export_data(self, request):
        """Export user data"""
        from django.http import JsonResponse
        import json
        
        # Collect user data
        user_data = {
            'user': UserSerializer(request.user).data,
            'profiles': UserProfileSerializer(
                UserProfile.objects.filter(user=request.user), 
                many=True
            ).data,
            'export_date': timezone.now().isoformat()
        }
        
        # Create JSON response
        response = JsonResponse(user_data, json_dumps_params={'indent': 2})
        response['Content-Disposition'] = f'attachment; filename="user-data-{request.user.id}.json"'
        return response


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile model"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return UserProfile.objects.filter(tenant=self.request.tenant, user=self.request.user)
        return UserProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def upload_avatar(self, request):
        """Upload user avatar"""
        if 'avatar' not in request.FILES:
            return Response({'error': 'No avatar file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        avatar_file = request.FILES['avatar']
        
        # Validate file type
        if not avatar_file.content_type.startswith('image/'):
            return Response({'error': 'File must be an image'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (5MB limit)
        if avatar_file.size > 5 * 1024 * 1024:
            return Response({'error': 'File size must be less than 5MB'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get or create user profile for current tenant
            profile, created = UserProfile.objects.get_or_create(
                user=request.user,
                tenant=getattr(request, 'tenant', None),
                defaults={'role': 'teacher' if request.user.is_teacher else 'student'}
            )
            
            # Save the avatar
            profile.avatar = avatar_file
            profile.save()
            
            return Response({
                'url': profile.avatar.url if profile.avatar else None,
                'filename': avatar_file.name,
                'size': avatar_file.size,
                'content_type': avatar_file.content_type
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TeacherApprovalViewSet(viewsets.ModelViewSet):
    """ViewSet for TeacherApproval model"""
    serializer_class = TeacherApprovalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return TeacherApproval.objects.all()
        return TeacherApproval.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """Approve teacher application"""
        approval = self.get_object()
        approval.approve(request.user)
        return Response({'message': 'Teacher application approved'})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        """Reject teacher application"""
        approval = self.get_object()
        notes = request.data.get('notes', '')
        approval.reject(request.user, notes)
        return Response({'message': 'Teacher application rejected'})


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for Organization model"""
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see organizations they belong to
        if self.request.user.is_superuser:
            return Organization.objects.all()
        return Organization.objects.filter(
            user_profiles__user=self.request.user,
            is_active=True
        ).distinct()
    
    def get_permissions(self):
        """Override permissions based on action"""
        if self.action == 'by_subdomain':
            return [permissions.AllowAny()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Create organization and add current user as admin"""
        organization = serializer.save()
        
        # Add current user as admin of the new organization
        TenantService.add_user_to_tenant(
            self.request.user, 
            organization, 
            role='admin'
        )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def by_subdomain(self, request):
        """Get organization by subdomain"""
        subdomain = request.query_params.get('subdomain')
        if not subdomain:
            return Response({'error': 'Subdomain parameter required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        tenant = TenantService.get_tenant_by_subdomain(subdomain)
        if tenant:
            serializer = self.get_serializer(tenant)
            return Response(serializer.data)
        
        return Response({'error': 'Organization not found'}, 
                       status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join an organization (with invitation code or admin approval)"""
        organization = self.get_object()
        invitation_code = request.data.get('invitation_code')
        
        # Check if user is already a member
        if UserProfile.objects.filter(user=request.user, tenant=organization).exists():
            return Response({'error': 'You are already a member of this organization'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # For now, allow anyone to join (in production, you'd want invitation codes or approval)
        TenantService.add_user_to_tenant(request.user, organization, role='student')
        
        return Response({
            'message': 'Successfully joined organization',
            'organization': self.get_serializer(organization).data
        })
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave an organization"""
        organization = self.get_object()
        
        try:
            profile = UserProfile.objects.get(user=request.user, tenant=organization)
            
            # Don't allow the last admin to leave
            admin_count = UserProfile.objects.filter(
                tenant=organization, 
                role='admin'
            ).count()
            
            if profile.role == 'admin' and admin_count <= 1:
                return Response({
                    'error': 'Cannot leave organization as the last admin. Please assign another admin first.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            profile.delete()
            
            return Response({'message': 'Successfully left organization'})
        except UserProfile.DoesNotExist:
            return Response({'error': 'You are not a member of this organization'}, 
                          status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshWithTenantView(TokenRefreshView):
    """Enhanced token refresh view that maintains tenant context"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Override to maintain tenant context in refreshed tokens"""
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get the refresh token from request
            refresh_token = request.data.get('refresh')
            if refresh_token:
                try:
                    # Decode the refresh token to get user and tenant info
                    token = RefreshToken(refresh_token)
                    user_id = token.get('user_id')
                    tenant_id = token.get('tenant_id')
                    
                    if user_id:
                        user = User.objects.get(id=user_id)
                        tenant = None
                        
                        if tenant_id:
                            try:
                                tenant = Organization.objects.get(id=tenant_id, is_active=True)
                            except Organization.DoesNotExist:
                                pass
                        
                        # Generate new tokens with tenant context
                        new_tokens = JWTAuthService.generate_tokens(user, tenant)
                        response.data.update(new_tokens)
                        
                except (TokenError, User.DoesNotExist, ValueError):
                    # If we can't decode or find user, return the original response
                    pass
        
        return response


class GoogleOAuth2LoginView(SocialLoginView):
    """Google OAuth2 login view with tenant support"""
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000/auth/google/callback"
    client_class = OAuth2Client
    serializer_class = GoogleOAuth2Serializer
    
    def get_response(self):
        """Override to add tenant information"""
        response = super().get_response()
        
        # Add tenant info if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            user = self.user
            TenantService.add_user_to_tenant(user, self.request.tenant)
            
            # Update tokens with tenant info
            tokens = JWTAuthService.generate_tokens(user, self.request.tenant)
            response.data.update(tokens)
        
        return response