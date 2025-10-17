from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import FileCategory, FileUpload, FileAccessLog, FileProcessingJob


@admin.register(FileCategory)
class FileCategoryAdmin(admin.ModelAdmin):
    """Admin interface for file categories"""
    
    list_display = ['name', 'display_name', 'max_file_size_mb', 'allowed_extensions_display']
    list_filter = ['max_file_size_mb']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['name']
    
    def allowed_extensions_display(self, obj):
        """Display allowed extensions as comma-separated string"""
        if obj.allowed_extensions:
            return ', '.join(obj.allowed_extensions)
        return 'All types allowed'
    allowed_extensions_display.short_description = 'Allowed Extensions'


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    """Admin interface for file uploads"""
    
    list_display = [
        'original_filename', 'title', 'category', 'uploaded_by_email',
        'file_size_display', 'access_level', 'status', 'download_count', 'created_at'
    ]
    list_filter = [
        'category', 'access_level', 'status', 'file_type', 'created_at'
    ]
    search_fields = [
        'original_filename', 'title', 'description', 'uploaded_by__email'
    ]
    readonly_fields = [
        'id', 'file_size', 'file_type', 'file_extension', 'download_count',
        'last_accessed', 'created_at', 'updated_at', 'file_preview'
    ]
    
    fieldsets = (
        ('File Information', {
            'fields': ('id', 'original_filename', 'file', 'file_preview', 'file_size', 
                      'file_type', 'file_extension')
        }),
        ('Metadata', {
            'fields': ('category', 'title', 'description', 'tags')
        }),
        ('Access Control', {
            'fields': ('uploaded_by', 'access_level', 'allowed_users', 'course')
        }),
        ('Status & Usage', {
            'fields': ('status', 'download_count', 'last_accessed', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    filter_horizontal = ['allowed_users']
    
    def uploaded_by_email(self, obj):
        """Display uploader email"""
        return obj.uploaded_by.email
    uploaded_by_email.short_description = 'Uploaded By'
    
    def file_size_display(self, obj):
        """Display file size in human readable format"""
        return f"{obj.file_size_mb} MB"
    file_size_display.short_description = 'File Size'
    
    def file_preview(self, obj):
        """Display file preview for images"""
        if obj.file and obj.is_image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.file.url
            )
        elif obj.file:
            return format_html(
                '<a href="{}" target="_blank">Download File</a>',
                obj.file.url
            )
        return 'No file'
    file_preview.short_description = 'Preview'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'category', 'uploaded_by', 'course'
        )


@admin.register(FileAccessLog)
class FileAccessLogAdmin(admin.ModelAdmin):
    """Admin interface for file access logs"""
    
    list_display = [
        'file_name', 'user_email', 'ip_address', 'accessed_at'
    ]
    list_filter = ['accessed_at', 'file__category']
    search_fields = [
        'file__original_filename', 'user__email', 'ip_address'
    ]
    readonly_fields = ['id', 'file', 'user', 'ip_address', 'user_agent', 'accessed_at']
    
    def file_name(self, obj):
        """Display file name with link"""
        if obj.file:
            url = reverse('admin:files_fileupload_change', args=[obj.file.pk])
            return format_html('<a href="{}">{}</a>', url, obj.file.original_filename)
        return 'N/A'
    file_name.short_description = 'File'
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email if obj.user else 'Anonymous'
    user_email.short_description = 'User'
    
    def has_add_permission(self, request):
        """Disable manual creation of access logs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make access logs read-only"""
        return False


@admin.register(FileProcessingJob)
class FileProcessingJobAdmin(admin.ModelAdmin):
    """Admin interface for file processing jobs"""
    
    list_display = [
        'file_name', 'job_type', 'status', 'duration_display', 'created_at'
    ]
    list_filter = ['job_type', 'status', 'created_at']
    search_fields = ['file__original_filename', 'job_type']
    readonly_fields = [
        'id', 'file', 'started_at', 'completed_at', 'created_at', 'duration_display'
    ]
    
    fieldsets = (
        ('Job Information', {
            'fields': ('id', 'file', 'job_type', 'status')
        }),
        ('Configuration', {
            'fields': ('parameters',)
        }),
        ('Results', {
            'fields': ('result_data', 'error_message')
        }),
        ('Timing', {
            'fields': ('created_at', 'started_at', 'completed_at', 'duration_display')
        })
    )
    
    def file_name(self, obj):
        """Display file name with link"""
        if obj.file:
            url = reverse('admin:files_fileupload_change', args=[obj.file.pk])
            return format_html('<a href="{}">{}</a>', url, obj.file.original_filename)
        return 'N/A'
    file_name.short_description = 'File'
    
    def duration_display(self, obj):
        """Display job duration"""
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return f"{duration.total_seconds():.2f} seconds"
        return 'N/A'
    duration_display.short_description = 'Duration'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('file')


# Customize admin site header
admin.site.site_header = "EduRise LMS File Management"
admin.site.site_title = "File Management Admin"
admin.site.index_title = "File Management Administration"