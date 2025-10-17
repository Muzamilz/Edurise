from django.contrib import admin
from .models import Course, LiveClass, CourseModule, CourseReview, CourseLicense, Wishlist, RecommendationInteraction


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'tenant', 'is_public', 'price', 'created_at')
    list_filter = ('is_public', 'tenant', 'created_at', 'category')
    search_fields = ('title', 'description', 'instructor__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'instructor', 'tenant')
        }),
        ('Course Details', {
            'fields': ('category', 'tags', 'thumbnail', 'price', 'is_public')
        }),
        ('Settings', {
            'fields': ('max_students', 'duration_weeks', 'difficulty_level')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'scheduled_at', 'status', 'duration_minutes')
    list_filter = ('status', 'scheduled_at', 'course__tenant')
    search_fields = ('title', 'course__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_published')
    list_filter = ('is_published', 'course__tenant')
    search_fields = ('title', 'course__title')
    ordering = ('course', 'order')


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('course__title', 'student__email', 'comment')
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"
    
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    reject_reviews.short_description = "Reject selected reviews"


@admin.register(CourseLicense)
class CourseLicenseAdmin(admin.ModelAdmin):
    list_display = ('course', 'license_type', 'is_active')
    list_filter = ('license_type', 'is_active')
    search_fields = ('course__title',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'priority', 'added_at', 'tenant')
    list_filter = ('priority', 'added_at', 'tenant', 'notify_price_change', 'notify_course_updates')
    search_fields = ('user__email', 'course__title', 'notes')
    readonly_fields = ('added_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'course', 'tenant', 'priority', 'notes')
        }),
        ('Notification Preferences', {
            'fields': ('notify_price_change', 'notify_course_updates', 'notify_enrollment_opening')
        }),
        ('Timestamps', {
            'fields': ('added_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Filter by tenant if user is not superuser"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filter by user's tenant if available
            if hasattr(request.user, 'tenant'):
                qs = qs.filter(tenant=request.user.tenant)
        return qs

@admin.register(RecommendationInteraction)
class RecommendationInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'interaction_type', 'algorithm_used', 'recommendation_score', 'created_at', 'tenant')
    list_filter = ('interaction_type', 'algorithm_used', 'created_at', 'tenant', 'page_context')
    search_fields = ('user__email', 'course__title')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'course', 'tenant', 'interaction_type')
        }),
        ('Recommendation Details', {
            'fields': ('algorithm_used', 'recommendation_score', 'recommendation_reason')
        }),
        ('Context Information', {
            'fields': ('session_id', 'page_context', 'position_in_list')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Filter by tenant if user is not superuser"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filter by user's tenant if available
            if hasattr(request.user, 'tenant'):
                qs = qs.filter(tenant=request.user.tenant)
        return qs