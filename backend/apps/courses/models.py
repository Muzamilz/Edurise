import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import TenantAwareModel

User = get_user_model()


class CourseCategory(models.Model):
    """Course categories with hierarchy support"""
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    # Visual customization
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class (e.g., 'fas fa-laptop-code')")
    color = models.CharField(max_length=7, blank=True, help_text="Hex color code (e.g., '#3B82F6')")
    
    # Hierarchy support
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories'
    )
    
    # Organization and display
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Optional: Tenant-specific categories (null = global category)
    tenant = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_categories'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_categories'
        verbose_name_plural = 'Course Categories'
        ordering = ['sort_order', 'name']
        unique_together = [
            ['slug', 'tenant'],  # Unique slug per tenant (or globally if tenant is null)
        ]
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def clean(self):
        """Validate category data"""
        from django.core.exceptions import ValidationError
        
        # Validate slug format
        import re
        if not re.match(r'^[a-z0-9-]+$', self.slug):
            raise ValidationError("Slug can only contain lowercase letters, numbers, and hyphens")
        
        # Validate parent relationship
        if self.parent:
            # Prevent circular references
            if self.parent == self:
                raise ValidationError("Category cannot be its own parent")
            
            # Check for circular reference in hierarchy
            current = self.parent
            while current:
                if current == self:
                    raise ValidationError("Circular reference detected in category hierarchy")
                current = current.parent
            
            # Validate tenant consistency
            if self.tenant and self.parent.tenant and self.tenant != self.parent.tenant:
                raise ValidationError("Child category must belong to the same tenant as parent")
        
        # Validate color format
        if self.color and not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
            raise ValidationError("Color must be a valid hex color code (e.g., #3B82F6)")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def full_path(self):
        """Get full category path"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return " > ".join(path)
    
    def get_descendants(self):
        """Get all descendant categories"""
        descendants = []
        for child in self.subcategories.filter(is_active=True):
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    @classmethod
    def get_root_categories(cls, tenant=None):
        """Get top-level categories for a tenant"""
        return cls.objects.filter(
            parent=None,
            is_active=True,
            tenant=tenant
        ).order_by('sort_order', 'name')
    
    def get_course_count(self):
        """Get number of courses in this category and its subcategories"""
        from django.db.models import Q
        
        # Get all descendant category IDs
        descendant_ids = [self.id]
        for descendant in self.get_descendants():
            descendant_ids.append(descendant.id)
        
        return Course.objects.filter(category_id__in=descendant_ids).count()
    
    def can_be_deleted(self):
        """Check if category can be safely deleted"""
        # Cannot delete if it has courses
        if self.courses.exists():
            return False, "Category has courses assigned to it"
        
        # Cannot delete if it has subcategories
        if self.subcategories.exists():
            return False, "Category has subcategories"
        
        return True, "Category can be deleted"
    
    def move_to_parent(self, new_parent):
        """Move category to a new parent with validation"""
        if new_parent:
            # Validate the move won't create circular reference
            current = new_parent
            while current:
                if current == self:
                    raise ValueError("Cannot move category: would create circular reference")
                current = current.parent
        
        self.parent = new_parent
        self.save()


class Course(TenantAwareModel):
    """Course model for both marketplace and institutional courses"""
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    

    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    
    # Course metadata
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.PROTECT,
        related_name='courses',
        help_text="Course category - cannot be deleted if courses exist"
    )
    tags = models.JSONField(default=list, blank=True)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    # New centralized file reference
    thumbnail_file = models.ForeignKey(
        'files.FileUpload',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='course_thumbnails'
    )
    
    # Pricing and access
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_public = models.BooleanField(default=False)  # Marketplace vs internal
    
    # Course settings
    max_students = models.PositiveIntegerField(null=True, blank=True)
    duration_weeks = models.PositiveIntegerField(default=4)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Validate category belongs to same tenant or is global
        if self.category and self.category.tenant and self.category.tenant != self.tenant:
            raise ValueError("Course category must belong to the same tenant or be global")
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate model data"""
        from django.core.exceptions import ValidationError
        
        # Validate price for public courses
        if self.is_public and self.price is None:
            raise ValidationError("Public courses must have a price set")
        
        # Validate max students
        if self.max_students is not None and self.max_students <= 0:
            raise ValidationError("Maximum students must be greater than 0")
        
        # Validate duration
        if self.duration_weeks <= 0:
            raise ValidationError("Duration must be greater than 0 weeks")
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating']
        return 0
    
    @property
    def total_enrollments(self):
        """Get total number of enrollments"""
        return self.enrollments.count()


class LiveClass(models.Model):
    """Live class sessions for courses"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='live_classes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Scheduling
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Zoom integration
    zoom_meeting_id = models.CharField(max_length=100, blank=True)
    join_url = models.URLField(blank=True)
    start_url = models.URLField(blank=True)
    password = models.CharField(max_length=50, blank=True)
    
    # Recording
    recording_url = models.URLField(blank=True)
    recording_password = models.CharField(max_length=50, blank=True)
    has_recording = models.BooleanField(default=False)
    recording_processed = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'live_classes'
        ordering = ['scheduled_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def is_accessible_to_user(self, user):
        """Check if user can access this live class"""
        if self.course.instructor == user or user.is_staff:
            return True
        
        # Check if user is enrolled in the course
        return Enrollment.objects.filter(
            student=user,
            course=self.course,
            status='active'
        ).exists()


class ClassRecording(models.Model):
    """Class recording files with access control"""
    
    RECORDING_TYPE_CHOICES = [
        ('zoom_cloud', 'Zoom Cloud Recording'),
        ('zoom_local', 'Zoom Local Recording'),
        ('manual_upload', 'Manual Upload'),
        ('processed', 'Processed Recording'),
    ]
    
    ACCESS_LEVEL_CHOICES = [
        ('enrolled', 'Enrolled Students Only'),
        ('public', 'Public Access'),
        ('instructor', 'Instructor Only'),
        ('premium', 'Premium Students Only'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='recordings')
    
    # Recording metadata
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    recording_type = models.CharField(max_length=20, choices=RECORDING_TYPE_CHOICES, default='zoom_cloud')
    
    # File information
    file_url = models.URLField()
    file_size_mb = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)
    file_format = models.CharField(max_length=10, default='mp4')
    
    # Access control
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES, default='enrolled')
    password_protected = models.BooleanField(default=False)
    access_password = models.CharField(max_length=100, blank=True)
    
    # Processing status
    is_processed = models.BooleanField(default=False)
    processing_status = models.CharField(max_length=50, default='pending')
    thumbnail_url = models.URLField(blank=True)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    recorded_at = models.DateTimeField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'class_recordings'
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.live_class.title} - {self.title}"
    
    def can_access(self, user):
        """Check if user can access this recording"""
        if self.access_level == 'instructor':
            return self.live_class.course.instructor == user or user.is_staff
        
        if self.access_level == 'public':
            return True
        
        if self.access_level == 'enrolled':
            return (
                self.live_class.course.instructor == user or
                user.is_staff or
                Enrollment.objects.filter(
                    student=user,
                    course=self.live_class.course,
                    status='active'
                ).exists()
            )
        
        if self.access_level == 'premium':
            # Check if user has premium access (implement based on your subscription logic)
            return (
                self.live_class.course.instructor == user or
                user.is_staff or
                Enrollment.objects.filter(
                    student=user,
                    course=self.live_class.course,
                    status='active'
                    # Add premium subscription check here
                ).exists()
            )
        
        return False
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_download_count(self):
        """Increment download count"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class CourseModule(models.Model):
    """Course modules/chapters"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    
    # Ordering and visibility
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    
    # Resources
    video_url = models.URLField(blank=True)
    materials = models.JSONField(default=list, blank=True)  # List of file URLs
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_modules'
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CourseReview(models.Model):
    """Course reviews and ratings"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_reviews'
        unique_together = ['course', 'student']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.student.email} ({self.rating}/5)"


class CourseLicense(models.Model):
    """Course licensing information"""
    
    LICENSE_CHOICES = [
        ('standard', 'Standard License'),
        ('extended', 'Extended License'),
        ('commercial', 'Commercial License'),
        ('educational', 'Educational License'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='license')
    license_type = models.CharField(max_length=20, choices=LICENSE_CHOICES, default='standard')
    terms = models.TextField()
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_licenses'
    
    def __str__(self):
        return f"{self.course.title} - {self.license_type}"


class Wishlist(TenantAwareModel):
    """Student wishlist for courses"""
    
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='wishlist_items')
    
    # Wishlist metadata
    priority = models.PositiveIntegerField(choices=PRIORITY_CHOICES, default=2)
    notes = models.TextField(blank=True, help_text="Personal notes about this course")
    
    # Notification preferences
    notify_price_change = models.BooleanField(default=True)
    notify_course_updates = models.BooleanField(default=True)
    notify_enrollment_opening = models.BooleanField(default=True)
    
    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wishlists'
        unique_together = ['user', 'course', 'tenant']
        ordering = ['-priority', '-added_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title}"
    
    @property
    def is_course_available(self):
        """Check if course is still available for enrollment"""
        if not self.course.is_public:
            return False
        
        if self.course.max_students:
            current_enrollments = self.course.enrollments.filter(status='active').count()
            return current_enrollments < self.course.max_students
        
        return True
    
    @property
    def price_at_addition(self):
        """Get the price when item was added to wishlist (for price change tracking)"""
        # This could be enhanced to track price history
        return self.course.price
    
    def is_enrolled(self):
        """Check if user is already enrolled in this course"""
        return Enrollment.objects.filter(
            student=self.user,
            course=self.course,
            tenant=self.tenant
        ).exists()


class RecommendationInteraction(TenantAwareModel):
    """Track user interactions with course recommendations"""
    
    INTERACTION_TYPES = [
        ('view', 'Viewed Recommendation'),
        ('click', 'Clicked on Course'),
        ('wishlist', 'Added to Wishlist'),
        ('enroll', 'Enrolled in Course'),
        ('dismiss', 'Dismissed Recommendation'),
    ]
    
    ALGORITHM_TYPES = [
        ('collaborative', 'Collaborative Filtering'),
        ('content_based', 'Content-Based Filtering'),
        ('popularity', 'Popularity-Based'),
        ('hybrid', 'Hybrid Algorithm'),
        ('wishlist_based', 'Wishlist-Based'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendation_interactions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='recommendation_interactions')
    
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    algorithm_used = models.CharField(max_length=20, choices=ALGORITHM_TYPES, null=True, blank=True)
    recommendation_score = models.FloatField(null=True, blank=True)
    recommendation_reason = models.TextField(blank=True)
    
    # Context information
    session_id = models.CharField(max_length=100, blank=True)
    page_context = models.CharField(max_length=100, blank=True)  # e.g., 'homepage', 'course_detail', 'wishlist'
    position_in_list = models.PositiveIntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recommendation_interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['course', 'interaction_type']),
            models.Index(fields=['algorithm_used', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.interaction_type} - {self.course.title}"


class Enrollment(TenantAwareModel):
    """Student enrollment in courses"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress_percentage = models.PositiveIntegerField(default=0)
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enrollments'
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.email} - {self.course.title}"