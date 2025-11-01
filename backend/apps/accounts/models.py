import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with email as username field"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email


class Organization(models.Model):
    """Organization/Tenant model for multi-tenancy"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    subdomain = models.SlugField(unique=True, max_length=50)
    logo = models.ImageField(upload_to='tenant_logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    secondary_color = models.CharField(max_length=7, default='#1E40AF')
    
    # Subscription relationship moved to Subscription model
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
    
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extended user profile with tenant relationship - allows users to belong to multiple tenants"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    tenant = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='user_profiles')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    
    # Role within this tenant
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    # Teacher-specific fields (per tenant)
    is_approved_teacher = models.BooleanField(default=False)
    teacher_approval_status = models.CharField(
        max_length=20,
        choices=[
            ('not_applied', 'Not Applied'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='not_applied'
    )
    teacher_approved_at = models.DateTimeField(null=True, blank=True)
    teacher_approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_teachers'
    )
    
    # Notification preferences
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    # User presence tracking
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        unique_together = ['user', 'tenant']
    
    def __str__(self):
        return f"{self.user.email} - {self.tenant.name}"


class TeacherApproval(models.Model):
    """Teacher approval requests for marketplace access"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_approval')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Application details
    teaching_experience = models.TextField()
    qualifications = models.TextField()
    subject_expertise = models.TextField()
    portfolio_url = models.URLField(blank=True)
    
    # Review details
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_teacher_applications'
    )
    review_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'teacher_approvals'
    
    def __str__(self):
        return f"{self.user.email} - {self.status}"
    
    def approve(self, reviewer, tenant=None):
        """Approve teacher application"""
        self.status = 'approved'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()
        
        # Update user profile teacher status for specific tenant
        if tenant:
            profile, created = UserProfile.objects.get_or_create(
                user=self.user,
                tenant=tenant,
                defaults={'role': 'teacher'}
            )
            profile.is_approved_teacher = True
            profile.teacher_approval_status = 'approved'
            profile.teacher_approved_at = timezone.now()
            profile.teacher_approved_by = reviewer
            profile.save()
    
    def reject(self, reviewer, notes=""):
        """Reject teacher application"""
        self.status = 'rejected'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()