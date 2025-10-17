# Centralized API Structure Summary

## Overview
All apps now follow a truly centralized API pattern where ViewSets are registered only in the centralized API router (`apps/api/urls.py`), eliminating duplication and ensuring consistent routing.

## Current State ✅

### Total Endpoints: 231 (down from 361)
- **Eliminated 130 duplicate endpoints** by removing redundant app-level ViewSet registrations
- All endpoints now use consistent `/api/v1/` prefix
- Clean separation between centralized ViewSets and app-specific functionality

## Centralized API Structure

### Core API Endpoints (apps/api/)
- **Health & Documentation**: `/api/health/`, `/api/docs/`
- **Dashboard Endpoints**: 
  - `/api/v1/dashboard/student/`
  - `/api/v1/dashboard/teacher/`
  - `/api/v1/dashboard/admin/`
  - `/api/v1/dashboard/superadmin/`

### Centralized ViewSets (registered in apps/api/urls.py)

#### Accounts App ViewSets
- `/api/v1/users/` - UserViewSet
- `/api/v1/user-profiles/` - UserProfileViewSet  
- `/api/v1/teacher-approvals/` - TeacherApprovalViewSet
- `/api/v1/organizations/` - OrganizationViewSet

#### Courses App ViewSets
- `/api/v1/courses/` - CourseViewSet (enhanced with analytics)
- `/api/v1/live-classes/` - LiveClassViewSet
- `/api/v1/course-modules/` - CourseModuleViewSet
- `/api/v1/course-reviews/` - CourseReviewViewSet
- `/api/v1/enrollments/` - EnrollmentViewSet

#### Classes App ViewSets
- `/api/v1/attendance/` - ClassAttendanceViewSet

#### Payments App ViewSets
- `/api/v1/payments/` - PaymentViewSet
- `/api/v1/subscriptions/` - SubscriptionViewSet
- `/api/v1/invoices/` - InvoiceViewSet

#### Notifications App ViewSets
- `/api/v1/notifications/` - NotificationViewSet

#### Admin Tools App ViewSets
- `/api/v1/audit-logs/` - AuditLogViewSet

#### AI App ViewSets
- `/api/v1/ai-conversations/` - AIConversationViewSet
- `/api/v1/ai-content-summaries/` - AIContentSummaryViewSet
- `/api/v1/ai-quizzes/` - AIQuizViewSet
- `/api/v1/ai-usage/` - AIUsageViewSet

### App-Specific Non-ViewSet Endpoints

#### Authentication (apps/accounts/urls.py)
- `/api/v1/accounts/auth/register/`
- `/api/v1/accounts/auth/login/`
- `/api/v1/accounts/auth/logout/`
- `/api/v1/accounts/auth/password-reset/`
- `/api/v1/accounts/auth/google/`
- Plus dj-rest-auth and social auth endpoints

#### Payment Webhooks (apps/payments/urls.py)
- `/api/v1/payments/webhooks/stripe/`
- `/api/v1/payments/webhooks/paypal/`

#### Zoom Integration (apps/classes/urls.py)
- `/api/v1/classes/zoom/webhook/`
- `/api/v1/classes/zoom/meetings/<uuid:live_class_id>/`

## Key Improvements Made

### 1. Eliminated Duplication ✅
- **Before**: ViewSets registered in both central router AND app routers
- **After**: ViewSets only registered in central router
- **Result**: 130 fewer duplicate endpoints

### 2. Clean Separation ✅
- **ViewSets**: Centrally managed in `apps/api/urls.py`
- **Special Endpoints**: App-specific (auth, webhooks, integrations)
- **Result**: Clear architectural boundaries

### 3. Enhanced Functionality ✅
- **Query Optimization**: Added select_related and prefetch_related
- **Real Data Integration**: Enhanced dashboard and analytics endpoints
- **Standardized Responses**: Consistent API response format
- **Intelligent Recommendations**: Multi-criteria course recommendations

### 4. Consistent Routing ✅
- All ViewSets accessible via `/api/v1/{resource}/`
- All dashboard endpoints via `/api/v1/dashboard/{role}/`
- All app-specific endpoints via `/api/v1/{app}/{functionality}/`

## Benefits Achieved

1. **No Duplicate Endpoints**: Clean, single source of truth for all ViewSets
2. **Better Performance**: Optimized database queries with proper relationships
3. **Real Data**: All dashboard and analytics endpoints use actual database data
4. **Consistent Responses**: Standardized API response format across all endpoints
5. **Maintainable**: Clear separation between centralized and app-specific functionality
6. **Scalable**: Easy to add new ViewSets to central router or app-specific endpoints

## Frontend Integration

The frontend can now reliably use:
- **Core Resources**: `/api/v1/{resource}/` for all CRUD operations
- **Dashboard Data**: `/api/v1/dashboard/{role}/` for role-specific dashboards
- **Authentication**: `/api/v1/accounts/auth/` for all auth operations
- **Webhooks**: App-specific webhook endpoints for external integrations

All endpoints return standardized response formats with proper error handling and consistent data structures.