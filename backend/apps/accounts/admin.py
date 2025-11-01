from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, TeacherApproval, Organization


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    # Remove the teacher status fieldset since it's now per-tenant in UserProfile


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'subdomain', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'subdomain')
    prepopulated_fields = {'subdomain': ('name',)}


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant', 'role', 'is_approved_teacher', 'created_at')
    list_filter = ('tenant', 'role', 'is_approved_teacher', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


@admin.register(TeacherApproval)
class TeacherApprovalAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'applied_at', 'reviewed_at', 'reviewed_by')
    list_filter = ('status', 'applied_at', 'reviewed_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    actions = ['approve_teachers', 'reject_teachers']
    
    def approve_teachers(self, request, queryset):
        queryset.update(status='approved', reviewed_by=request.user)
    approve_teachers.short_description = "Approve selected teacher applications"
    
    def reject_teachers(self, request, queryset):
        queryset.update(status='rejected', reviewed_by=request.user)
    reject_teachers.short_description = "Reject selected teacher applications"