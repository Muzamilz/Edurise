from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
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


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile model"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return UserProfile.objects.filter(tenant=self.request.tenant, user=self.request.user)
        return UserProfile.objects.filter(user=self.request.user)


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
    permission_classes = [permissions.IsAdminUser]
    queryset = Organization.objects.all()
    
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