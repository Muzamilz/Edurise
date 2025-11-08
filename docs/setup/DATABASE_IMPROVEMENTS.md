# Database Architecture Improvements

## Overview
This document outlines the key improvements made to the EduRise LMS database architecture to enhance flexibility, maintainability, and scalability.

## Key Improvements

### 1. Subscription Plans Normalization

**Before:**
```python
class Organization(models.Model):
    subscription_plan = models.CharField(
        choices=[('basic', 'Basic'), ('pro', 'Pro'), ('enterprise', 'Enterprise')]
    )
```

**After:**
```python
class Subscription(TenantAwareModel):
    organization = models.OneToOneField(Organization, ...)
    plan = models.ForeignKey(SubscriptionPlan, ...)  # Proper FK relationship
```

**Benefits:**
- ✅ **Dynamic plan management**: Add/modify plans without code changes
- ✅ **Rich plan metadata**: Store pricing, features, limits in dedicated model
- ✅ **Plan history**: Track subscription changes over time
- ✅ **Custom plans**: Create organization-specific plans
- ✅ **Better data integrity**: FK constraints prevent orphaned references

### 2. Multi-Tenant Teacher Permissions

**Before:**
```python
class User(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_approved_teacher = models.BooleanField(default=False)
```

**After:**
```python
class UserProfile(models.Model):
    user = models.ForeignKey(User, ...)
    tenant = models.ForeignKey(Organization, ...)
    role = models.CharField(...)
    is_approved_teacher = models.BooleanField(default=False)  # Per tenant
    teacher_approval_status = models.CharField(...)
```

**Benefits:**
- ✅ **Tenant-specific roles**: User can be teacher in one org, student in another
- ✅ **Granular permissions**: Different approval status per organization
- ✅ **Audit trail**: Track who approved teachers and when
- ✅ **Flexible roles**: Easy to add new roles (TA, moderator, etc.)

### 3. Dynamic Course Categories

**Before:**
```python
class Course(TenantAwareModel):
    category = models.CharField(
        choices=[('technology', 'Technology'), ('business', 'Business'), ...]
    )
```

**After:**
```python
class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', ...)  # Hierarchy support
    tenant = models.ForeignKey(Organization, ...)  # Custom categories

class Course(TenantAwareModel):
    category = models.ForeignKey(CourseCategory, ...)
```

**Benefits:**
- ✅ **Dynamic categories**: Add categories without code deployment
- ✅ **Hierarchical structure**: Support subcategories (Technology > Web Development)
- ✅ **Tenant customization**: Organizations can create custom categories
- ✅ **Rich metadata**: Icons, colors, descriptions for better UX
- ✅ **Localization ready**: Easy to add multi-language support

## Migration Strategy

### 1. Data Migration for Subscription Plans
```python
# Create default subscription plans
python manage.py seed_subscription_plans

# Migrate existing organizations to use new Subscription model
# (Custom migration script needed)
```

### 2. Data Migration for Categories
```python
# Create default course categories
python manage.py seed_categories

# Migrate existing courses to use CourseCategory FK
# (Custom migration script needed)
```

### 3. User Profile Migration
```python
# Create UserProfile records for existing users
# Migrate is_teacher flags to UserProfile.role
# (Custom migration script needed)
```

## New Management Commands

### Seed Categories
```bash
python manage.py seed_categories
```
Creates hierarchical course categories with icons and colors.

### Seed Subscription Plans
```bash
python manage.py seed_subscription_plans
```
Creates Basic, Pro, and Enterprise subscription plans with feature limits.

## API Impact

### Course Categories API
```python
# New endpoints needed:
GET /api/categories/                    # List categories
GET /api/categories/{id}/subcategories/ # Get subcategories
POST /api/categories/                   # Create custom category (admin)
```

### Subscription Management API
```python
# Enhanced endpoints:
GET /api/subscriptions/plans/           # List available plans
POST /api/subscriptions/upgrade/        # Upgrade subscription
GET /api/subscriptions/usage/           # Current usage vs limits
```

### User Management API
```python
# Updated endpoints:
GET /api/users/profile/{tenant_id}/     # Get user profile for specific tenant
POST /api/users/apply-teacher/          # Apply to be teacher in tenant
POST /api/admin/approve-teacher/        # Approve teacher application
```

## Database Schema Changes

### New Tables
- `course_categories` - Hierarchical course categories
- Enhanced `user_profiles` - Per-tenant user roles and permissions

### Modified Tables
- `organizations` - Removed `subscription_plan` field
- `subscriptions` - Changed `plan` from CharField to ForeignKey
- `courses` - Changed `category` from CharField to ForeignKey
- `users` - Removed `is_teacher` and `is_approved_teacher` fields

### Indexes Added
```sql
-- Performance indexes for new relationships
CREATE INDEX idx_course_category ON courses(category_id);
CREATE INDEX idx_subscription_plan ON subscriptions(plan_id);
CREATE INDEX idx_user_profile_tenant_role ON user_profiles(tenant_id, role);
CREATE INDEX idx_category_parent ON course_categories(parent_id);
```

## Benefits Summary

1. **Flexibility**: Easy to modify plans, categories, and permissions without code changes
2. **Scalability**: Proper normalization reduces data redundancy
3. **Multi-tenancy**: Better support for organization-specific customizations
4. **Maintainability**: Cleaner separation of concerns
5. **User Experience**: Richer metadata enables better UI/UX
6. **Business Agility**: Marketing can create new plans without engineering involvement

## Next Steps

1. Create and run database migrations
2. Update API endpoints to use new models
3. Update frontend to consume new API structure
4. Create admin interface for managing categories and plans
5. Add data validation and business logic
6. Update documentation and API specs
## Fronten
d Updates Completed ✅

### 1. **Updated Type Definitions**
- Removed `is_teacher` and `is_approved_teacher` from User interface
- Added `current_profile` with role-based permissions  
- Updated Organization interface to use subscription relationship
- Added new CourseCategory, SubscriptionPlan, and Subscription interfaces

### 2. **Updated API Integration**
- Updated all serializers to work with new model structure
- Added CourseCategory ViewSet with hierarchy support
- Updated API documentation to include new endpoints
- Fixed subscription plan references in payment serializers

### 3. **Updated Frontend Components**
- CourseForm now uses dynamic categories from API
- Updated tenant composable to use new subscription structure
- Updated teacher role checks to use profile-based roles
- Added category service and composable for category management

### 4. **New API Endpoints Added**
```
GET /api/v1/course-categories/                    # List all categories
GET /api/v1/course-categories/root_categories/    # Get root categories  
GET /api/v1/course-categories/hierarchy/          # Get full hierarchy
GET /api/v1/course-categories/{id}/subcategories/ # Get subcategories
POST /api/v1/course-categories/                   # Create category (admin)
```

### 5. **Migration Commands Created**
```bash
# Seed default categories
python manage.py seed_categories

# Seed subscription plans
python manage.py seed_subscription_plans
```

## What's Been Fixed

✅ **Subscription Plans**: Now properly normalized with FK relationships  
✅ **User Teacher Status**: Moved to per-tenant UserProfile model  
✅ **Course Categories**: Dynamic, hierarchical categories with rich metadata  
✅ **API Endpoints**: Updated to support new model structure  
✅ **Frontend Integration**: Components updated to use new APIs  
✅ **Type Safety**: All TypeScript interfaces updated  

The centralized API app has been fully updated to reflect the new database architecture. The system is now much more flexible and follows proper database design principles!
#
# Admin Interface & Business Logic Completed ✅

### 1. **Admin Category Management Interface**
- **CategoryManagementView**: Full category CRUD with tree hierarchy
- **CategoryTreeNode**: Interactive tree component with expand/collapse
- **CategoryModal**: Rich form with validation, preview, and visual settings
- **Business Logic**: Category validation, hierarchy checks, course count tracking

### 2. **Super Admin Global Management**
- **GlobalCategoryManagementView**: Platform-wide category management
- **GlobalSubscriptionPlanManagementView**: Global plan management with analytics
- **Enhanced Navigation**: Added to both admin and super admin dashboards
- **Multi-tenant Support**: Global vs tenant-specific category management

### 3. **Subscription Plan Management**
- **SubscriptionPlanManagementView**: Complete plan CRUD interface
- **SubscriptionPlanModal**: Tabbed interface (Basic, Pricing, Limits, Features, Preview)
- **Plan Analytics**: Usage statistics, revenue tracking, conversion metrics
- **Business Validation**: Price validation, feature consistency checks

### 4. **Enhanced Business Logic & Validation**

#### **Course Model Enhancements**
```python
def clean(self):
    # Validate price for public courses
    if self.is_public and self.price is None:
        raise ValidationError("Public courses must have a price set")
    
    # Validate category tenant consistency
    if self.category and self.category.tenant and self.category.tenant != self.tenant:
        raise ValueError("Course category must belong to the same tenant or be global")
```

#### **SubscriptionPlan Model Enhancements**
```python
def clean(self):
    # Validate yearly price is less than 12 months of monthly price
    if self.price_yearly >= (self.price_monthly * 12):
        raise ValidationError("Yearly price should be less than 12 months of monthly price")

def calculate_savings_percentage(self):
    """Calculate percentage savings for yearly vs monthly billing"""
    monthly_total = self.price_monthly * 12
    if monthly_total > 0:
        savings = ((monthly_total - self.price_yearly) / monthly_total) * 100
        return max(0, round(savings, 1))
    return 0
```

#### **CourseCategory Model Enhancements**
```python
def clean(self):
    # Prevent circular references
    if self.parent:
        current = self.parent
        while current:
            if current == self:
                raise ValidationError("Circular reference detected in category hierarchy")
            current = current.parent

def can_be_deleted(self):
    """Check if category can be safely deleted"""
    if self.courses.exists():
        return False, "Category has courses assigned to it"
    if self.subcategories.exists():
        return False, "Category has subcategories"
    return True, "Category can be deleted"
```

### 5. **Updated Routes & Navigation**

#### **Admin Routes Added**
```typescript
{
  path: 'categories',
  name: 'admin-categories',
  component: () => import('../views/admin/CategoryManagementView.vue')
},
{
  path: 'subscription-plans', 
  name: 'admin-subscription-plans',
  component: () => import('../views/admin/SubscriptionPlanManagementView.vue')
}
```

#### **Super Admin Routes Added**
```typescript
{
  path: 'categories',
  name: 'super-admin-categories', 
  component: () => import('../views/super-admin/GlobalCategoryManagementView.vue')
},
{
  path: 'subscription-plans',
  name: 'super-admin-subscription-plans',
  component: () => import('../views/super-admin/GlobalSubscriptionPlanManagementView.vue')
}
```

### 6. **Dashboard Integration**
- **AdminDashboard**: Added "Category Management" and "Subscription Plans" quick actions
- **SuperAdminDashboard**: Added "Global Categories" and "Subscription Plans" quick actions
- **Navigation Icons**: Consistent iconography (📂 for categories, 💳 for plans)

### 7. **Services & Composables**
- **CategoryService**: Complete API integration for category CRUD
- **SubscriptionService**: Full subscription and plan management API
- **useCategories**: Global state management for categories with caching
- **Validation**: Client-side form validation with real-time feedback

### 8. **Key Features Implemented**

#### **Category Management**
- ✅ Hierarchical tree structure with drag-and-drop (ready)
- ✅ Visual customization (icons, colors)
- ✅ Global vs tenant-specific categories
- ✅ Usage analytics and course counting
- ✅ Bulk operations and export functionality
- ✅ Real-time validation and error handling

#### **Subscription Plan Management**
- ✅ Rich plan configuration (limits, features, pricing)
- ✅ Visual plan preview and comparison
- ✅ Usage analytics and revenue tracking
- ✅ Plan upgrade/downgrade workflows
- ✅ Feature flag management
- ✅ Billing cycle optimization (yearly savings calculation)

#### **Business Logic & Validation**
- ✅ Comprehensive model validation
- ✅ Circular reference prevention
- ✅ Tenant consistency checks
- ✅ Price validation and business rules
- ✅ Safe deletion checks
- ✅ Automatic slug generation

## Summary

The admin interface for managing categories and subscription plans is now complete with:

🎯 **Full CRUD Operations** for both categories and subscription plans
🎯 **Rich UI Components** with modals, trees, and tabbed interfaces  
🎯 **Business Logic Validation** preventing data inconsistencies
🎯 **Multi-tenant Support** with global and tenant-specific management
🎯 **Dashboard Integration** with quick access navigation
🎯 **API Documentation** updated with new endpoints
🎯 **Type Safety** with comprehensive TypeScript interfaces

The system now provides enterprise-grade admin tools for managing the core platform configuration while maintaining data integrity and user experience excellence.