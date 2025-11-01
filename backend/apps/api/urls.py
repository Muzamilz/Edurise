from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import APIHealthCheckView, APIDocumentationView
from .dashboard_views import (
    StudentDashboardView, TeacherDashboardView, 
    AdminDashboardView, SuperAdminDashboardView
)
from .analytics_views import AnalyticsViewSet, ReportGenerationView, ScheduledReportViewSet, ReportDownloadView
from .security_views import SecurityOverviewView, PlatformAnalyticsView, GlobalFinancialView, SystemHealthView
from .additional_views import (
    PlatformAnalyticsView, TeacherAnalyticsView, TeacherEarningsView,
    WishlistViewSet, CourseRecommendationsView,
    GlobalFinancialAnalyticsView, OrganizationFinancialView, PaymentTransactionsView
)
# Import placeholder views for now
from apps.security.views import (
    SecurityOverviewView, SecurityAlertsView, SecurityEventsView, 
    SecuritySettingsView, SecurityPoliciesView
)
from apps.security.system_views import (
    SystemStatusView, SystemLogsView, SystemConfigView, SystemMaintenanceView
)

# Import ViewSets from other apps
from apps.accounts.views import UserViewSet, UserProfileViewSet, TeacherApprovalViewSet, OrganizationViewSet
from apps.courses.views import (
    CourseCategoryViewSet, CourseViewSet, LiveClassViewSet, CourseModuleViewSet, 
    CourseReviewViewSet, EnrollmentViewSet
)
from apps.classes.views import ClassAttendanceViewSet, ClassRecordingViewSet
from apps.payments.views import PaymentViewSet, SubscriptionViewSet, InvoiceViewSet, SubscriptionPlanViewSet
from apps.notifications.views import (
    NotificationViewSet, EmailDeliveryLogViewSet, NotificationTemplateViewSet,
    ChatMessageViewSet, WebSocketConnectionViewSet
)
from apps.admin_tools.views import AuditLogViewSet
from apps.ai.views import AIConversationViewSet, AIContentSummaryViewSet, AIQuizViewSet, AIUsageViewSet
from apps.assignments.views import AssignmentViewSet, SubmissionViewSet, CertificateViewSet, CourseProgressViewSet
from apps.files.views import (
    FileCategoryViewSet, FileUploadViewSet, FileAccessLogViewSet, FileProcessingJobViewSet,
    SecureFileDownloadView, FilePermissionsView
)

# Create API router
router = DefaultRouter()

# Register all ViewSets with consistent naming

# Analytics ViewSet
router.register(r'analytics', AnalyticsViewSet, basename='analytics')
router.register(r'scheduled-reports', ScheduledReportViewSet, basename='scheduledreport')

# Additional ViewSets
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

# Accounts app ViewSets
router.register(r'users', UserViewSet, basename='user')
router.register(r'user-profiles', UserProfileViewSet, basename='userprofile')
router.register(r'teacher-approvals', TeacherApprovalViewSet, basename='teacherapproval')
router.register(r'organizations', OrganizationViewSet, basename='organization')

# Courses app ViewSets
router.register(r'course-categories', CourseCategoryViewSet, basename='coursecategory')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'live-classes', LiveClassViewSet, basename='liveclass')
router.register(r'course-modules', CourseModuleViewSet, basename='coursemodule')
router.register(r'course-reviews', CourseReviewViewSet, basename='coursereview')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

# Classes app ViewSets
router.register(r'attendance', ClassAttendanceViewSet, basename='attendance')
router.register(r'class-recordings', ClassRecordingViewSet, basename='classrecording')

# Payments app ViewSets
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscriptionplan')
router.register(r'invoices', InvoiceViewSet, basename='invoice')

# Notifications app ViewSets
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'email-delivery-logs', EmailDeliveryLogViewSet, basename='emaildeliverylog')
router.register(r'notification-templates', NotificationTemplateViewSet, basename='notificationtemplate')
router.register(r'chat-messages', ChatMessageViewSet, basename='chatmessage')
router.register(r'websocket-connections', WebSocketConnectionViewSet, basename='websocketconnection')

# Admin tools app ViewSets
router.register(r'audit-logs', AuditLogViewSet, basename='auditlog')

# AI app ViewSets
router.register(r'ai-conversations', AIConversationViewSet, basename='aiconversation')
router.register(r'ai-content-summaries', AIContentSummaryViewSet, basename='aicontentsummary')
router.register(r'ai-quizzes', AIQuizViewSet, basename='aiquiz')
router.register(r'ai-usage', AIUsageViewSet, basename='aiusage')

# Assignments app ViewSets
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'certificates', CertificateViewSet, basename='certificate')
router.register(r'course-progress', CourseProgressViewSet, basename='courseprogress')

# Files app ViewSets
router.register(r'file-categories', FileCategoryViewSet, basename='filecategory')
router.register(r'file-uploads', FileUploadViewSet, basename='fileupload')
router.register(r'file-access-logs', FileAccessLogViewSet, basename='fileaccesslog')
router.register(r'file-processing-jobs', FileProcessingJobViewSet, basename='fileprocessingjob')

urlpatterns = [
    # API health check and documentation
    path('health/', APIHealthCheckView.as_view(), name='api-health'),
    path('docs/', APIDocumentationView.as_view(), name='api-docs'),
    
    # API v1 routes - All ViewSets registered through router
    path('v1/', include(router.urls)),
    
    # Dashboard endpoints
    path('v1/dashboard/student/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('v1/dashboard/teacher/', TeacherDashboardView.as_view(), name='teacher-dashboard'),
    path('v1/dashboard/admin/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('v1/dashboard/superadmin/', SuperAdminDashboardView.as_view(), name='superadmin-dashboard'),
    
    # Analytics and reporting endpoints
    path('v1/reports/generate/', ReportGenerationView.as_view(), name='generate-report'),
    path('v1/reports/download/<str:report_id>/', ReportDownloadView.as_view(), name='download-report'),
    
    # Additional analytics endpoints
    path('v1/analytics/platform-overview/', PlatformAnalyticsView.as_view(), name='platform-analytics'),
    path('v1/analytics/teacher/', TeacherAnalyticsView.as_view(), name='teacher-analytics'),
    
    # Teacher-specific endpoints
    path('v1/teacher/earnings/', TeacherEarningsView.as_view(), name='teacher-earnings'),
    
    # Super Admin specific endpoints
    path('v1/security/', SecurityOverviewView.as_view(), name='security-overview'),
    path('v1/analytics/platform/', PlatformAnalyticsView.as_view(), name='platform-analytics-new'),
    path('v1/financial/global/', GlobalFinancialView.as_view(), name='global-financial'),
    path('v1/system/health/', SystemHealthView.as_view(), name='system-health'),
    path('v1/security/events/', SecurityEventsView.as_view(), name='security-events'),
    path('v1/security/settings/', SecuritySettingsView.as_view(), name='security-settings'),
    path('v1/security/policies/', SecurityPoliciesView.as_view(), name='security-policies'),
    
    # System endpoints
    path('v1/system/status/', SystemStatusView.as_view(), name='system-status'),
    path('v1/system/logs/', SystemLogsView.as_view(), name='system-logs'),
    path('v1/system/config/', SystemConfigView.as_view(), name='system-config'),
    path('v1/system/maintenance/<str:action>/', SystemMaintenanceView.as_view(), name='system-maintenance'),
    
    # Course recommendations
    path('v1/courses/recommendations/', CourseRecommendationsView.as_view(), name='course-recommendations'),
    
    # Financial analytics endpoints
    path('v1/analytics/financial/global/', GlobalFinancialAnalyticsView.as_view(), name='global-financial-analytics'),
    path('v1/organizations/financial/', OrganizationFinancialView.as_view(), name='organization-financial'),
    path('v1/payments/transactions/', PaymentTransactionsView.as_view(), name='payment-transactions'),
    
    # App-specific endpoints with additional functionality
    
    # Authentication endpoints (includes auth views + ViewSets)
    path('v1/accounts/', include('apps.accounts.urls')),
    
    # AI endpoints (includes AI ViewSets + additional endpoints)
    path('v1/ai/', include('apps.ai.urls')),
    
    # Payment webhooks and additional endpoints
    path('v1/payments/', include('apps.payments.urls')),
    
    # Security and compliance endpoints
    path('v1/security/', include('apps.security.urls')),
    
    # Class management with Zoom integration
    path('v1/classes/', include('apps.classes.urls')),
    
    # Notifications
    path('v1/notifications/', include('apps.notifications.urls')),
    
    # Admin tools
    path('v1/admin-tools/', include('apps.admin_tools.urls')),
    
    # File management
    path('v1/files/', include('apps.files.urls')),
    
    # Content management
    path('v1/content/', include('apps.content.urls')),
]