from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()


class Testimonial(models.Model):
    """Model for storing user testimonials"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials')
    content = models.TextField(help_text="Testimonial content")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False, help_text="Show on homepage")
    position = models.CharField(max_length=100, blank=True, help_text="User's position/title")
    company = models.CharField(max_length=100, blank=True, help_text="User's company")
    course = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Publishing workflow
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='approved_testimonials'
    )
    
    # SEO and metadata
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'featured']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Testimonial by {self.user.get_full_name() or self.user.username}"


class TeamMember(models.Model):
    """Model for team member information"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('leadership', 'Leadership'),
        ('engineering', 'Engineering'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('support', 'Support'),
        ('education', 'Education'),
        ('operations', 'Operations'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, help_text="Job title or role")
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    bio = models.TextField(help_text="Brief biography")
    profile_image = models.ImageField(upload_to='team_members/', null=True, blank=True)
    
    # Contact information
    email = models.EmailField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    
    # Display settings
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    display_order = models.IntegerField(default=0, help_text="Order for display (lower numbers first)")
    featured = models.BooleanField(default=False, help_text="Show on main team page")
    
    # SEO and metadata
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['status', 'featured']),
            models.Index(fields=['department', 'display_order']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.role}"


class Announcement(models.Model):
    """Model for platform announcements"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('feature', 'New Feature'),
        ('maintenance', 'Maintenance'),
        ('event', 'Event'),
        ('promotion', 'Promotion'),
        ('update', 'Platform Update'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Publishing settings
    publish_at = models.DateTimeField(default=timezone.now)
    expire_at = models.DateTimeField(null=True, blank=True)
    
    # Display settings
    featured = models.BooleanField(default=False)
    show_on_homepage = models.BooleanField(default=False)
    send_notification = models.BooleanField(default=False)
    
    # Author information
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    
    # SEO and metadata
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=500, blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-publish_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'publish_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['featured', 'show_on_homepage']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_published(self):
        """Check if announcement is currently published"""
        now = timezone.now()
        return (
            self.status == 'published' and
            self.publish_at <= now and
            (self.expire_at is None or self.expire_at > now)
        )


class FAQ(models.Model):
    """Model for frequently asked questions"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('courses', 'Courses'),
        ('payments', 'Payments'),
        ('technical', 'Technical Support'),
        ('account', 'Account Management'),
        ('certificates', 'Certificates'),
        ('mobile', 'Mobile App'),
    ]
    
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Display settings
    display_order = models.IntegerField(default=0, help_text="Order for display (lower numbers first)")
    featured = models.BooleanField(default=False, help_text="Show in featured FAQs")
    
    # Usage tracking
    view_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)
    
    # Author information
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='faqs')
    
    # SEO and metadata
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=500, blank=True)
    keywords = models.CharField(max_length=500, blank=True, help_text="Comma-separated keywords")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'display_order', 'question']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['featured', 'status']),
            models.Index(fields=['category', 'display_order']),
        ]
    
    def __str__(self):
        return self.question
    
    @property
    def helpfulness_ratio(self):
        """Calculate helpfulness ratio"""
        total_votes = self.helpful_count + self.not_helpful_count
        if total_votes == 0:
            return 0
        return self.helpful_count / total_votes


class ContactInfo(models.Model):
    """Model for company contact information and social links"""
    # Company information
    company_name = models.CharField(max_length=200, default="EduRise")
    tagline = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    
    # Contact details
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Business hours
    business_hours = models.TextField(blank=True, help_text="Business hours information")
    
    # Social media links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    # Additional links
    blog_url = models.URLField(blank=True)
    support_url = models.URLField(blank=True)
    privacy_policy_url = models.URLField(blank=True)
    terms_of_service_url = models.URLField(blank=True)
    
    # Emergency contact
    emergency_contact = models.TextField(blank=True)
    
    # SEO and metadata
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=500, blank=True)
    
    # Version control
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=20, default="1.0")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"
        ordering = ['-is_active', '-created_at']
    
    def __str__(self):
        return f"{self.company_name} Contact Info (v{self.version})"
    
    def save(self, *args, **kwargs):
        # Ensure only one active contact info exists
        if self.is_active:
            ContactInfo.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active(cls):
        """Get the active contact information"""
        return cls.objects.filter(is_active=True).first()