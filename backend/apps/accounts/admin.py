from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, TeacherApproval


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_teacher', 'is_approved_teacher', 'is_staff')
    list_filter = ('is_teacher', 'is_approved_teacher', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Teacher Status', {'fields': ('is_teacher', 'is_approved_teacher')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant', 'created_at')
    list_filter = ('tenant', 'created_at')
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