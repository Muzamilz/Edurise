from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile, TeacherApproval, Organization


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'is_teacher', 'is_approved_teacher', 'is_staff', 'is_superuser',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'is_approved_teacher', 'is_staff', 'is_superuser', 'date_joined', 'last_login']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm', 'is_teacher']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
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
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'tenant', 'tenant_name', 'avatar', 'bio', 
            'phone_number', 'date_of_birth', 'timezone', 'language'
        ]
        read_only_fields = ['id', 'user', 'tenant']


class TeacherApprovalSerializer(serializers.ModelSerializer):
    """Serializer for TeacherApproval model"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = TeacherApproval
        fields = [
            'id', 'user', 'user_email', 'user_name', 'status',
            'teaching_experience', 'qualifications', 'subject_expertise',
            'portfolio_url', 'applied_at', 'reviewed_at', 'review_notes'
        ]
        read_only_fields = ['id', 'user', 'status', 'applied_at', 'reviewed_at']


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model"""
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'subdomain', 'logo', 'primary_color', 
            'secondary_color', 'subscription_plan', 'is_active'
        ]
        read_only_fields = ['id']


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