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
from django.db.models import Q, Avg
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
            
            # Get subscription plan name
            subscription_plan_name = 'basic'
            try:
                if hasattr(tenant, 'subscription') and tenant.subscription:
                    subscription_plan_name = tenant.subscription.plan.name
            except:
                subscription_plan_name = 'basic'
            
            response_data = {
                'tenant': {
                    'id': str(tenant.id),
                    'name': tenant.name,
                    'subdomain': tenant.subdomain,
                    'role': profile.role,
                    'subscription_plan': subscription_plan_name,
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

    @action(detail=False, methods=['get'])
    def all_with_roles(self, request):
        """Get all users with their roles (superuser only)"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can view all users"
            )
        
        # Get all users with their profiles
        users = User.objects.all().prefetch_related('profiles__tenant')
        
        users_data = []
        for user in users:
            # Get primary profile (first one or main organization)
            primary_profile = user.profiles.first()
            
            user_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.email,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
                'role': 'superuser' if user.is_superuser else ('admin' if user.is_staff else (primary_profile.role if primary_profile else 'student')),
                'organization_name': primary_profile.tenant.name if primary_profile else 'No Organization',
                'organization_id': primary_profile.tenant.id if primary_profile else None,
                'profiles_count': user.profiles.count(),
            }
            users_data.append(user_data)
        
        return StandardAPIResponse.success(
            data=users_data,
            message="All users retrieved successfully"
        )


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
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get organization statistics"""
        organization = self.get_object()
        
        # Get organization statistics
        from apps.courses.models import Course, Enrollment
        from apps.payments.models import Payment
        from django.db.models import Count, Sum
        
        # User statistics
        user_profiles = UserProfile.objects.filter(tenant=organization)
        user_stats = user_profiles.aggregate(
            total_users=Count('id'),
            total_students=Count('id', filter=Q(role='student')),
            total_teachers=Count('id', filter=Q(role='teacher')),
            total_admins=Count('id', filter=Q(role='admin'))
        )
        
        # Course statistics
        courses = Course.objects.filter(tenant=organization)
        course_stats = courses.aggregate(
            total_courses=Count('id'),
            published_courses=Count('id', filter=Q(is_public=True)),
            avg_price=Avg('price')
        )
        
        # Enrollment statistics
        enrollments = Enrollment.objects.filter(tenant=organization)
        enrollment_stats = enrollments.aggregate(
            total_enrollments=Count('id'),
            active_enrollments=Count('id', filter=Q(status='active')),
            completed_enrollments=Count('id', filter=Q(status='completed'))
        )
        
        # Revenue statistics
        payments = Payment.objects.filter(tenant=organization, status='completed')
        revenue_stats = payments.aggregate(
            total_revenue=Sum('amount'),
            total_payments=Count('id')
        )
        
        stats_data = {
            'user_stats': user_stats,
            'course_stats': course_stats,
            'enrollment_stats': enrollment_stats,
            'revenue_stats': {
                'total_revenue': float(revenue_stats['total_revenue'] or 0),
                'total_payments': revenue_stats['total_payments']
            }
        }
        
        return StandardAPIResponse.success(
            data=stats_data,
            message="Organization statistics retrieved successfully"
        )

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

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get users for this organization"""
        organization = self.get_object()
        
        # Only superusers can view organization users
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can view organization users"
            )
        
        # Get user profiles for this organization
        profiles = UserProfile.objects.filter(tenant=organization).select_related('user')
        
        users_data = []
        for profile in profiles:
            user_data = {
                'id': profile.user.id,
                'email': profile.user.email,
                'first_name': profile.user.first_name,
                'last_name': profile.user.last_name,
                'full_name': f"{profile.user.first_name} {profile.user.last_name}".strip() or profile.user.email,
                'is_active': profile.user.is_active,
                'role': profile.role,
                'is_approved_teacher': profile.is_approved_teacher,
                'avatar': profile.avatar.url if profile.avatar else None,
                'last_seen': profile.last_seen,
                'created_at': profile.created_at,
                'updated_at': profile.updated_at,
            }
            users_data.append(user_data)
        
        return StandardAPIResponse.success(
            data=users_data,
            message="Organization users retrieved successfully"
        )

    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        """Get courses for this organization"""
        organization = self.get_object()
        
        # Only superusers can view organization courses
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can view organization courses"
            )
        
        # Get courses for this organization
        from apps.courses.models import Course
        courses = Course.objects.filter(tenant=organization).select_related(
            'instructor', 'category'
        ).prefetch_related('enrollments')
        
        courses_data = []
        for course in courses:
            course_data = {
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'thumbnail': course.thumbnail.url if course.thumbnail else None,
                'price': float(course.price) if course.price else 0,
                'is_public': course.is_public,
                'instructor_name': course.instructor.get_full_name() if course.instructor else 'Unknown',
                'category_name': course.category.name if course.category else 'Uncategorized',
                'category': course.category.id if course.category else None,
                'enrollment_count': course.enrollments.count(),
                'created_at': course.created_at,
                'updated_at': course.updated_at,
            }
            courses_data.append(course_data)
        
        return StandardAPIResponse.success(
            data=courses_data,
            message="Organization courses retrieved successfully"
        )

    @action(detail=True, methods=['post'])
    def change_subscription_plan(self, request, pk=None):
        """Change organization subscription plan (super admin only)"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can change organization subscription plans"
            )
        
        organization = self.get_object()
        new_plan_id = request.data.get('plan_id')
        
        if not new_plan_id:
            return StandardAPIResponse.validation_error(
                message="plan_id is required",
                errors={'plan_id': ['This field is required']}
            )
        
        try:
            from apps.payments.models import SubscriptionPlan, Subscription
            
            # Get the new plan
            try:
                new_plan = SubscriptionPlan.objects.get(id=new_plan_id, is_active=True)
            except SubscriptionPlan.DoesNotExist:
                return StandardAPIResponse.validation_error(
                    message="Invalid or inactive subscription plan",
                    errors={'plan_id': ['Invalid subscription plan']}
                )
            
            # Get or create subscription for organization
            subscription, created = Subscription.objects.get_or_create(
                organization=organization,
                defaults={
                    'plan': new_plan,
                    'billing_cycle': 'monthly',
                    'amount': new_plan.price_monthly,
                    'current_period_start': timezone.now(),
                    'current_period_end': timezone.now() + timezone.timedelta(days=30),
                    'tenant': organization
                }
            )
            
            if not created:
                # Update existing subscription
                old_plan = subscription.plan
                subscription.plan = new_plan
                subscription.amount = new_plan.price_monthly
                subscription.save()
                
                # Log the change (simple logging for now)
                import logging
                logger = logging.getLogger('apps.accounts')
                logger.info(f"Subscription plan changed for organization {organization.name} "
                           f"from {old_plan.name} to {new_plan.name} by {request.user.email}")
            
            return StandardAPIResponse.success(
                data={
                    'organization_id': str(organization.id),
                    'organization_name': organization.name,
                    'old_plan': subscription.plan.name if not created else None,
                    'new_plan': new_plan.name,
                    'plan_details': {
                        'id': str(new_plan.id),
                        'name': new_plan.name,
                        'display_name': new_plan.display_name,
                        'price_monthly': float(new_plan.price_monthly),
                        'price_yearly': float(new_plan.price_yearly),
                        'max_users': new_plan.max_users,
                        'max_courses': new_plan.max_courses,
                        'max_storage_gb': new_plan.max_storage_gb,
                        'ai_quota_monthly': new_plan.ai_quota_monthly,
                    }
                },
                message=f"Subscription plan changed to {new_plan.display_name} successfully"
            )
            
        except Exception as e:
            return StandardAPIResponse.error(
                message="Failed to change subscription plan",
                error_code="SUBSCRIPTION_CHANGE_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def subscription_info(self, request, pk=None):
        """Get organization subscription information (super admin only)"""
        if not request.user.is_superuser:
            return StandardAPIResponse.permission_denied(
                message="Only super administrators can view organization subscription information"
            )
        
        organization = self.get_object()
        
        try:
            from apps.payments.models import Subscription, SubscriptionPlan
            
            # Get current subscription
            try:
                subscription = Subscription.objects.get(organization=organization)
                current_plan = subscription.plan
                
                subscription_data = {
                    'has_subscription': True,
                    'subscription_id': str(subscription.id),
                    'current_plan': {
                        'id': str(current_plan.id),
                        'name': current_plan.name,
                        'display_name': current_plan.display_name,
                        'price_monthly': float(current_plan.price_monthly),
                        'price_yearly': float(current_plan.price_yearly),
                        'max_users': current_plan.max_users,
                        'max_courses': current_plan.max_courses,
                        'max_storage_gb': current_plan.max_storage_gb,
                        'ai_quota_monthly': current_plan.ai_quota_monthly,
                    },
                    'billing_cycle': subscription.billing_cycle,
                    'status': subscription.status,
                    'current_period_start': subscription.current_period_start,
                    'current_period_end': subscription.current_period_end,
                    'amount': float(subscription.amount),
                }
            except Subscription.DoesNotExist:
                subscription_data = {
                    'has_subscription': False,
                    'current_plan': None,
                }
            
            # Get all available plans
            available_plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
            plans_data = []
            
            for plan in available_plans:
                plans_data.append({
                    'id': str(plan.id),
                    'name': plan.name,
                    'display_name': plan.display_name,
                    'description': plan.description,
                    'price_monthly': float(plan.price_monthly),
                    'price_yearly': float(plan.price_yearly),
                    'max_users': plan.max_users,
                    'max_courses': plan.max_courses,
                    'max_storage_gb': plan.max_storage_gb,
                    'ai_quota_monthly': plan.ai_quota_monthly,
                    'has_analytics': plan.has_analytics,
                    'has_api_access': plan.has_api_access,
                    'has_white_labeling': plan.has_white_labeling,
                    'has_priority_support': plan.has_priority_support,
                    'has_custom_integrations': plan.has_custom_integrations,
                    'is_popular': plan.is_popular,
                })
            
            subscription_data['available_plans'] = plans_data
            
            return StandardAPIResponse.success(
                data=subscription_data,
                message="Organization subscription information retrieved successfully"
            )
            
        except Exception as e:
            return StandardAPIResponse.error(
                message="Failed to retrieve subscription information",
                error_code="SUBSCRIPTION_INFO_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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