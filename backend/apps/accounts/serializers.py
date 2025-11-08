from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile, TeacherApproval, Organization


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with enhanced role information"""
    organization_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    current_profile = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'is_staff', 'is_superuser', 'is_teacher', 'is_approved_teacher',
            'date_joined', 'last_login', 'organization_name', 'current_profile', 'role'
        ]
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'date_joined', 'last_login']
    
    def get_organization_name(self, obj):
        """Get the user's primary organization name"""
        try:
            profile = obj.profiles.first()
            return profile.tenant.name if profile and profile.tenant else 'No Organization'
        except:
            return 'No Organization'
    
    def get_full_name(self, obj):
        """Get the user's full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email
    
    def get_role(self, obj):
        """Get the user's primary role"""
        if obj.is_superuser:
            return 'superuser'
        if obj.is_staff:
            return 'admin'
        
        request = self.context.get('request')
        if request and hasattr(request, 'tenant'):
            try:
                profile = obj.profiles.get(tenant=request.tenant)
                return profile.role
            except UserProfile.DoesNotExist:
                pass
        
        # Fallback to first profile role
        try:
            profile = obj.profiles.first()
            return profile.role if profile else 'student'
        except:
            return 'student'
    
    def get_current_profile(self, obj):
        """Get the user's profile for the current tenant"""
        request = self.context.get('request')
        if request and hasattr(request, 'tenant'):
            try:
                profile = obj.profiles.get(tenant=request.tenant)
                return {
                    'id': str(profile.id),
                    'role': profile.role,
                    'is_approved_teacher': profile.is_approved_teacher,
                    'teacher_approval_status': profile.teacher_approval_status,
                    'is_online': profile.is_online,
                    'last_seen': profile.last_seen
                }
            except UserProfile.DoesNotExist:
                return None
        return None


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=[('student', 'Student'), ('teacher', 'Teacher')],
        default='student',
        write_only=True
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm', 'role']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        role = validated_data.pop('role', 'student')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user profile for the current tenant if available
        request = self.context.get('request')
        if request and hasattr(request, 'tenant'):
            UserProfile.objects.create(
                user=user,
                tenant=request.tenant,
                role=role
            )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = UserSerializer(read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    teacher_approved_by_name = serializers.CharField(source='teacher_approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'tenant', 'tenant_name', 'avatar', 'bio', 
            'phone_number', 'date_of_birth', 'timezone', 'language',
            'role', 'is_approved_teacher', 'teacher_approval_status',
            'teacher_approved_at', 'teacher_approved_by', 'teacher_approved_by_name',
            'notification_preferences', 'is_online', 'last_seen',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'tenant', 'is_approved_teacher', 'teacher_approval_status',
            'teacher_approved_at', 'teacher_approved_by', 'created_at', 'updated_at'
        ]


class TeacherApprovalSerializer(serializers.ModelSerializer):
    """Serializer for TeacherApproval model"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    organization_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherApproval
        fields = [
            'id', 'user', 'user_email', 'user_name', 'user_first_name', 'user_last_name',
            'organization_name', 'status', 'teaching_experience', 'qualifications', 
            'subject_expertise', 'portfolio_url', 'applied_at', 'reviewed_at', 'review_notes'
        ]
        read_only_fields = ['id', 'user', 'status', 'applied_at', 'reviewed_at']
    
    def get_organization_name(self, obj):
        """Get the organization name for the user"""
        try:
            # Get the user's first profile (assuming users typically belong to one org)
            profile = obj.user.profiles.first()
            return profile.tenant.name if profile and profile.tenant else 'No Organization'
        except:
            return 'No Organization'


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model"""
    subscription = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'subdomain', 'logo', 'primary_color', 
            'secondary_color', 'is_active', 'subscription',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_subscription(self, obj):
        """Get the organization's subscription details"""
        try:
            from apps.payments.models import Subscription
            subscription = Subscription.objects.select_related('plan').get(organization=obj)
            return {
                'id': subscription.id,
                'plan_name': subscription.plan.name,
                'plan_display_name': subscription.plan.display_name,
                'status': subscription.status,
                'billing_cycle': subscription.billing_cycle,
                'current_period_end': subscription.current_period_end,
                'is_active': subscription.is_active()
            }
        except Subscription.DoesNotExist:
            return None


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)
    password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class GoogleOAuth2Serializer(serializers.Serializer):
    """Serializer for Google OAuth2 authentication"""
    access_token = serializers.CharField()
    code = serializers.CharField(required=False)
    id_token = serializers.CharField(required=False)


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout request"""
    refresh_token = serializers.CharField()


class TenantSwitchSerializer(serializers.Serializer):
    """Serializer for tenant switching"""
    tenant_id = serializers.UUIDField()