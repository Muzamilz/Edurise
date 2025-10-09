from django.contrib import admin
from .models import Course, LiveClass, CourseModule, CourseReview, CourseLicense


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