import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from .models import User, UserProfile, Organization


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def register_user(email, password, first_name, last_name, is_teacher=False, tenant=None):
        """Register a new user"""
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_teacher=is_teacher
        )
        
        # Create user profile if tenant is provided
        if tenant:
            role = 'teacher' if is_teacher else 'student'
            UserProfile.objects.create(user=user, tenant=tenant, role=role)
        
        return user
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password"""
        return authenticate(username=email, password=password)
    
    @staticmethod
    def send_password_reset_email(user):
        """Send password reset email"""
        token = JWTAuthService.generate_password_reset_token(user)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        subject = 'Password Reset - Edurise'
        html_message = render_to_string('emails/password_reset.html', {
            'user': user,
            'reset_url': reset_url
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message
        )
    
    @staticmethod
    def reset_password(token, new_password):
        """Reset user password with token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            user.set_password(new_password)
            user.save()
            return user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return None


class JWTAuthService:
    """Service for JWT token operations"""
    
    @staticmethod
    def generate_tokens(user, tenant=None):
        """Generate JWT access and refresh tokens with enhanced tenant support"""
        refresh = RefreshToken.for_user(user)
        
        # Add tenant information to token if available
        if tenant:
            refresh['tenant_id'] = str(tenant.id)
            refresh['tenant_subdomain'] = tenant.subdomain
            refresh['tenant_name'] = tenant.name
            
            # Add user role within this tenant
            try:
                profile = UserProfile.objects.get(user=user, tenant=tenant)
                refresh['tenant_role'] = profile.role
            except UserProfile.DoesNotExist:
                refresh['tenant_role'] = 'student'
        else:
            refresh['tenant_id'] = None
            refresh['tenant_subdomain'] = None
            refresh['tenant_name'] = None
            refresh['tenant_role'] = None
        
        # Add user information
        refresh['user_id'] = str(user.id)
        refresh['email'] = user.email
        refresh['first_name'] = user.first_name
        refresh['last_name'] = user.last_name
        refresh['is_teacher'] = user.is_teacher
        refresh['is_approved_teacher'] = user.is_approved_teacher
        refresh['is_staff'] = user.is_staff
        refresh['is_superuser'] = user.is_superuser
        
        # Add access token with same claims
        access_token = refresh.access_token
        if tenant:
            access_token['tenant_id'] = str(tenant.id)
            access_token['tenant_subdomain'] = tenant.subdomain
            access_token['tenant_name'] = tenant.name
            access_token['tenant_role'] = refresh['tenant_role']
        
        access_token['email'] = user.email
        access_token['first_name'] = user.first_name
        access_token['last_name'] = user.last_name
        access_token['is_teacher'] = user.is_teacher
        access_token['is_approved_teacher'] = user.is_approved_teacher
        access_token['is_staff'] = user.is_staff
        access_token['is_superuser'] = user.is_superuser
        
        return {
            'refresh': str(refresh),
            'access': str(access_token),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_teacher': user.is_teacher,
                'is_approved_teacher': user.is_approved_teacher,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            },
            'tenant': {
                'id': str(tenant.id) if tenant else None,
                'name': tenant.name if tenant else None,
                'subdomain': tenant.subdomain if tenant else None,
                'role': refresh['tenant_role'] if tenant else None,
            } if tenant else None
        }
    
    @staticmethod
    def generate_password_reset_token(user):
        """Generate password reset token"""
        payload = {
            'user_id': str(user.id),
            'exp': datetime.utcnow() + timedelta(hours=1),  # 1 hour expiry
            'type': 'password_reset'
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def blacklist_token(refresh_token):
        """Blacklist a refresh token"""
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except Exception:
            return False
    
    @staticmethod
    def is_token_blacklisted(token_jti):
        """Check if a token is blacklisted"""
        try:
            return BlacklistedToken.objects.filter(token__jti=token_jti).exists()
        except Exception:
            return False


class TenantService:
    """Service for tenant operations"""
    
    @staticmethod
    def get_tenant_by_subdomain(subdomain):
        """Get tenant by subdomain"""
        try:
            return Organization.objects.get(subdomain=subdomain, is_active=True)
        except Organization.DoesNotExist:
            return None
    
    @staticmethod
    def create_tenant(name, subdomain, **kwargs):
        """Create a new tenant"""
        return Organization.objects.create(
            name=name,
            subdomain=subdomain,
            **kwargs
        )
    
    @staticmethod
    def get_user_tenants(user):
        """Get all tenants for a user"""
        return Organization.objects.filter(
            user_profiles__user=user,
            is_active=True
        ).distinct()
    
    @staticmethod
    def add_user_to_tenant(user, tenant, role='student'):
        """Add user to tenant"""
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            tenant=tenant,
            defaults={'role': role}
        )
        return profile