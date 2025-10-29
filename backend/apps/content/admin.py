from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Testimonial, TeamMember, Announcement, FAQ, ContactInfo


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'status', 'featured', 'course', 'submitted_at']
    list_filter = ['status', 'rating', 'featured', 'course', 'submitted_at']
    search_fields = ['user__username', 'user__email', 'content', 'position', 'company']
    readonly_fields = ['submitted_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'content', 'rating', 'course')
        }),
        ('User Details', {
            'fields': ('position', 'company')
        }),
        ('Publishing', {
            'fields': ('status', 'featured', 'approved_by', 'approved_at')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['approve_testimonials', 'reject_testimonials', 'feature_testimonials']
    
    def approve_testimonials(self, request, queryset):
        updated = queryset.update(
            status='published',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} testimonials approved.')
    approve_testimonials.short_description = "Approve selected testimonials"
    
    def reject_testimonials(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} testimonials rejected.')
    reject_testimonials.short_description = "Reject selected testimonials"
    
    def feature_testimonials(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} testimonials featured.')
    feature_testimonials.short_description = "Feature selected testimonials"


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'department', 'status', 'featured', 'display_order']
    list_filter = ['department', 'status', 'featured']
    search_fields = ['name', 'role', 'bio', 'email']
    list_editable = ['display_order', 'featured', 'status']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'role', 'department', 'bio')
        }),
        ('Profile', {
            'fields': ('profile_image', 'email', 'linkedin_url', 'twitter_url')
        }),
        ('Display Settings', {
            'fields': ('status', 'display_order', 'featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'priority', 'status', 'featured', 'publish_at', 'author']
    list_filter = ['category', 'priority', 'status', 'featured', 'publish_at']
    search_fields = ['title', 'content', 'tags']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'publish_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'author')
        }),
        ('Categorization', {
            'fields': ('category', 'priority', 'tags')
        }),
        ('Publishing', {
            'fields': ('status', 'publish_at', 'expire_at')
        }),
        ('Display Settings', {
            'fields': ('featured', 'show_on_homepage', 'send_notification')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['publish_announcements', 'feature_announcements']
    
    def publish_announcements(self, request, queryset):
        updated = queryset.update(status='published', publish_at=timezone.now())
        self.message_user(request, f'{updated} announcements published.')
    publish_announcements.short_description = "Publish selected announcements"
    
    def feature_announcements(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} announcements featured.')
    feature_announcements.short_description = "Feature selected announcements"


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'status', 'featured', 'display_order', 'view_count']
    list_filter = ['category', 'status', 'featured']
    search_fields = ['question', 'answer', 'keywords']
    list_editable = ['display_order', 'featured', 'status']
    readonly_fields = ['view_count', 'helpful_count', 'not_helpful_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('question', 'answer', 'author')
        }),
        ('Categorization', {
            'fields': ('category', 'keywords')
        }),
        ('Display Settings', {
            'fields': ('status', 'display_order', 'featured')
        }),
        ('Analytics', {
            'fields': ('view_count', 'helpful_count', 'not_helpful_count'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['publish_faqs', 'feature_faqs']
    
    def publish_faqs(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} FAQs published.')
    publish_faqs.short_description = "Publish selected FAQs"
    
    def feature_faqs(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} FAQs featured.')
    feature_faqs.short_description = "Feature selected FAQs"


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'version', 'is_active', 'email', 'phone', 'updated_at']
    list_filter = ['is_active', 'updated_at']
    search_fields = ['company_name', 'email', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'tagline', 'description')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'address', 'business_hours')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url', 'youtube_url')
        }),
        ('Additional Links', {
            'fields': ('blog_url', 'support_url', 'privacy_policy_url', 'terms_of_service_url')
        }),
        ('Emergency', {
            'fields': ('emergency_contact',)
        }),
        ('Version Control', {
            'fields': ('is_active', 'version')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of contact info
        return False