from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
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
from .response_utils import APIResponseMixin, StandardAPIResponse, log_api_request

User = get_user_model()


class RegisterView(APIView, APIResponseMixin):
    """User registration view"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        log_api_request(request)
        
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                
                # Get tenant from request if available
                tenant = getattr(request, 'tenant', None)
                if tenant:
                    TenantService.add_user_to_tenant(user, tenant)
                
                # Generate tokens
                tokens = JWTAuthService.generate_tokens(user, tenant)
                
                response_data = {
                    'user': UserSerializer(user).data,
                    **tokens
                }
                
                return self.success_response(
                    data=response_data,
                    message="User registered successfully",
                    status_code=status.HTTP_201_CREATED
                )
            except Exception as e:
                log_api_request(request, error=e)
                return self.error_response(
                    message="Registration failed",
                    error_code="REGISTRATION_ERROR",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return self.validation_error_response(serializer.errors)


class LoginView(TokenObtainPairView, APIResponseMixin):
    """Custom login view with tenant support"""
    
    def post(self, request, *args, **kwargs):
        log_api_request(request)
        
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.validated_data['user']
                tenant = getattr(request, 'tenant', None)
                
                # Generate tokens with tenant info
                tokens = JWTAuthService.generate_tokens(user, tenant)
                
                response_data = {
                    'user': UserSerializer(user).data,
                    **tokens
                }
                
                return self.success_response(
                    data=response_data,
                    message="Login successful"
                )
            except Exception as e:
                log_api_request(request, error=e)
                return self.error_response(
                    message="Login failed",
                    error_code="LOGIN_ERROR",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return self.validation_error_response(serializer.errors)


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


class UserViewSet(viewsets.ModelViewSet, APIResponseMixin):
    """ViewSet for User model"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Superusers can see all users across all tenants
        if self.request.user.is_superuser:
            return User.objects.all().select_related().prefetch_related('profiles__tenant')
        
        # Filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return User.objects.filter(profiles__tenant=self.request.tenant)
        return User.objects.all()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        try:
            serializer = self.get_serializer(request.user)
            return self.success_response(
                data=serializer.data,
                message="User profile retrieved successfully"
            )
        except Exception as e:
            log_api_request(request, error=e)
            return self.error_response(
                message="Failed to retrieve user profile",
                error_code="PROFILE_ERROR"
            )
    
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
            return self.error_response(
                message="tenant_id is required",
                error_code="MISSING_TENANT_ID"
            )
        
        try:
            tenant = Organization.objects.get(id=tenant_id, is_active=True)
            
            # Verify user has access to this tenant
            try:
                profile = UserProfile.objects.get(user=request.user, tenant=tenant)
            except UserProfile.DoesNotExist:
                return self.error_response(
                    message="Access denied to this tenant",
                    error_code="TENANT_ACCESS_DENIED",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Generate new tokens with the new tenant context
            tokens = JWTAuthService.generate_tokens(request.user, tenant)
            
            response_data = {
                'tenant': {
                    'id': str(tenant.id),
                    'name': tenant.name,
                    'subdomain': tenant.subdomain,
                    'role': profile.role,
                    'subscription_plan': tenant.subscription_plan,
                },
                **tokens
            }
            
            return self.success_response(
                data=response_data,
                message="Tenant switched successfully"
            )
        except Organization.DoesNotExist:
            return self.error_response(
                message="Tenant not found",
                error_code="TENANT_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def preferences(self, request):
        """Get user preferences"""
        try:
            preferences = {}
            
            # Get user profile preferences for current tenant
            if hasattr(request, 'tenant') and request.tenant:
                try:
                    profile = UserProfile.objects.get(user=request.user, tenant=request.tenant)
                    preferences.update({
                        'language': profile.language,
                        'timezone': profile.timezone,
                        'role': profile.role,
                        'tenant_id': str(profile.tenant.id),
                        'tenant_name': profile.tenant.name,
                    })
                except UserProfile.DoesNotExist:
                    # Return default preferences
                    preferences.update({
                        'language': 'en',
                        'timezone': 'UTC',
                        'role': 'student',
                        'tenant_id': None,
                        'tenant_name': None,
                    })
            else:
                # Return user-level preferences
                preferences.update({
                    'language': 'en',  # Could be stored in user model
                    'timezone': 'UTC',  # Could be stored in user model
                    'role': 'teacher' if request.user.is_teacher else 'student',
                    'tenant_id': None,
                    'tenant_name': None,
                })
            
            # Add user information
            preferences.update({
                'email_notifications': True,  # Could be stored in user model
                'push_notifications': True,   # Could be stored in user model
                'marketing_emails': False,    # Could be stored in user model
            })
            
            return self.success_response(
                data=preferences,
                message="User preferences retrieved successfully"
            )
        except Exception as e:
            log_api_request(request, error=e)
            return self.error_response(
                message="Failed to retrieve user preferences",
                error_code="PREFERENCES_ERROR"
            )
    
    @action(detail=False, methods=['patch'])
    def update_preferences(self, request):
        """Update user preferences"""
        preferences = request.data
        
        # Update user profile preferences for current tenant
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
        
        # Update user-level preferences (could be stored in user model in future)
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
        confirmation = request.data.get('confirmation')
        
        if not password:
            return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if confirmation != 'DELETE':
            return Response({
                'error': 'Please type "DELETE" to confirm account deletion'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify password
        if not request.user.check_password(password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is the last admin of any organization
        admin_profiles = UserProfile.objects.filter(user=request.user, role='admin')
        for profile in admin_profiles:
            admin_count = UserProfile.objects.filter(
                tenant=profile.tenant, 
                role='admin'
            ).count()
            if admin_count <= 1:
                return Response({
                    'error': f'Cannot delete account. You are the last admin of "{profile.tenant.name}". Please assign another admin first.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # In a real implementation, you might want to:
            # 1. Anonymize the user data instead of deleting
            # 2. Send a confirmation email
            # 3. Add a grace period before actual deletion
            # 4. Archive related data instead of deleting
            
            # For now, we'll mark the user as inactive and anonymize
            user = request.user
            user.is_active = False
            user.email = f"deleted_user_{user.id}@deleted.local"
            user.first_name = "Deleted"
            user.last_name = "User"
            user.save()
            
            # Remove user from all organizations
            UserProfile.objects.filter(user=user).delete()
            
            return Response({
                'message': 'Account deletion completed successfully'
            })
        except Exception as e:
            return Response({
                'error': 'Account deletion failed. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def export_data(self, request):
        """Export user data for GDPR compliance"""
        try:
            from django.http import JsonResponse
            import json
            
            # Collect comprehensive user data
            user_data = {
                'personal_information': {
                    'id': str(request.user.id),
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'is_teacher': request.user.is_teacher,
                    'is_approved_teacher': request.user.is_approved_teacher,
                    'date_joined': request.user.date_joined.isoformat(),
                    'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
                },
                'organization_profiles': [],
                'export_metadata': {
                    'export_date': timezone.now().isoformat(),
                    'export_format': 'JSON',
                    'data_controller': 'EduRise Platform',
                }
            }
            
            # Add organization profiles
            profiles = UserProfile.objects.filter(user=request.user).select_related('tenant')
            for profile in profiles:
                user_data['organization_profiles'].append({
                    'organization_name': profile.tenant.name,
                    'organization_subdomain': profile.tenant.subdomain,
                    'role': profile.role,
                    'bio': profile.bio,
                    'phone_number': profile.phone_number,
                    'date_of_birth': profile.date_of_birth.isoformat() if profile.date_of_birth else None,
                    'timezone': profile.timezone,
                    'language': profile.language,
                    'joined_date': profile.created_at.isoformat(),
                    'last_updated': profile.updated_at.isoformat(),
                })
            
            # Add teacher approval data if exists
            try:
                teacher_approval = request.user.teacher_approval
                user_data['teacher_approval'] = {
                    'status': teacher_approval.status,
                    'teaching_experience': teacher_approval.teaching_experience,
                    'qualifications': teacher_approval.qualifications,
                    'subject_expertise': teacher_approval.subject_expertise,
                    'portfolio_url': teacher_approval.portfolio_url,
                    'applied_date': teacher_approval.applied_at.isoformat(),
                    'reviewed_date': teacher_approval.reviewed_at.isoformat() if teacher_approval.reviewed_at else None,
                }
            except:
                pass
            
            # Create JSON response
            response = JsonResponse(user_data, json_dumps_params={'indent': 2})
            response['Content-Disposition'] = f'attachment; filename="edurise-user-data-{request.user.id}.json"'
            response['Content-Type'] = 'application/json'
            
            return response
            
        except Exception as e:
            return Response({
                'error': 'Data export failed. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile model"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filter by tenant if available
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return UserProfile.objects.filter(tenant=self.request.tenant, user=self.request.user)
        return UserProfile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create user profile with current user and tenant"""
        tenant = getattr(self.request, 'tenant', None)
        if not tenant:
            raise ValidationError("Tenant is required to create a user profile")
        
        # Set default role based on user type
        role = 'teacher' if self.request.user.is_teacher else 'student'
        
        serializer.save(
            user=self.request.user,
            tenant=tenant,
            role=role
        )
    
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
    """Enhanced token refresh view that maintains tenant context and supports tenant switching"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Override to maintain tenant context in refreshed tokens and support tenant switching"""
        refresh_token = request.data.get('refresh')
        tenant_switch_id = request.data.get('tenant_id')  # Optional tenant switch
        
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Decode the refresh token to get user and current tenant info
            token = RefreshToken(refresh_token)
            user_id = token.get('user_id')
            current_tenant_id = token.get('tenant_id')
            
            if not user_id:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.get(id=user_id)
            tenant = None
            
            # Handle tenant switching if requested
            if tenant_switch_id:
                try:
                    new_tenant = Organization.objects.get(id=tenant_switch_id, is_active=True)
                    # Verify user has access to this tenant
                    if UserProfile.objects.filter(user=user, tenant=new_tenant).exists():
                        tenant = new_tenant
                    else:
                        return Response({
                            'error': 'Access denied to the requested tenant'
                        }, status=status.HTTP_403_FORBIDDEN)
                except Organization.DoesNotExist:
                    return Response({
                        'error': 'Requested tenant not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                # Use current tenant from token
                if current_tenant_id:
                    try:
                        tenant = Organization.objects.get(id=current_tenant_id, is_active=True)
                    except Organization.DoesNotExist:
                        # Tenant no longer exists or is inactive, continue without tenant
                        pass
            
            # Blacklist the old refresh token
            token.blacklist()
            
            # Generate new tokens with (possibly new) tenant context
            new_tokens = JWTAuthService.generate_tokens(user, tenant)
            
            response_data = {
                'message': 'Token refreshed successfully',
                **new_tokens
            }
            
            if tenant_switch_id:
                response_data['message'] = 'Token refreshed and tenant switched successfully'
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except TokenError as e:
            return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Token refresh failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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