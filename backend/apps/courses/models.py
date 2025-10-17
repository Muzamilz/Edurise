import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import TenantAwareModel

User = get_user_model()


class Course(TenantAwareModel):
    """Course model for both marketplace and institutional courses"""
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    CATEGORY_CHOICES = [
        ('technology', 'Technology'),
        ('business', 'Business'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
        ('language', 'Language'),
        ('science', 'Science'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    
    # Course metadata
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
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