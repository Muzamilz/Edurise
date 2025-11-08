# Authentication & Role-Based Routing System Guide

## Overview

This guide explains the complete authentication and role-based routing system implemented in the EduRise platform. The system provides secure authentication with automatic role-based dashboard redirection.

## Architecture

### Backend (Django REST Framework)

#### User Roles Hierarchy
1. **Superuser** - Platform-wide administrator with full access
2. **Admin** - Organization administrator (staff)
3. **Teacher** - Approved teacher with course creation rights
4. **Teacher (Pending)** - Teacher awaiting approval
5. **Student** - Regular user with learning access

#### Key Backend Components

**Models** (`backend/apps/accounts/models.py`):
- `User` - Custom user model with email authentication
- `Organization` - Multi-tenant organization model
- `UserProfile` - User profile per organization with role
- `TeacherApproval` - Teacher approval workflow

**Services** (`backend/apps/accounts/services.py`):
- `AuthService` - Authentication operations
- `JWTAuthService` - JWT token generation with role information
- `TenantService` - Multi-tenant operations

**Serializers** (`backend/apps/accounts/serializers.py`):
- `UserSerializer` - Enhanced with role information
- `LoginSerializer` - Login validation
- `UserRegistrationSerializer` - Registration with role selection

**Views** (`backend/apps/accounts/views.py`):
- `LoginView` - Login with role-based token generation
- `RegisterView` - Registration with tenant assignment
- `UserViewSet` - User management with role filtering

#### JWT Token Structure

Tokens include comprehensive user and role information:

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "superuser|admin|teacher|student",
  "is_teacher": true,
  "is_approved_teacher": true,
  "is_staff": false,
  "is_superuser": false,
  "tenant_id": "uuid",
  "tenant_subdomain": "org-name",
  "tenant_name": "Organization Name",
  "tenant_role": "admin|teacher|student"
}
```

### Frontend (Vue 3 + TypeScript)

#### Key Frontend Components

**Auth Store** (`frontend/src/stores/auth.ts`):
- Manages authentication state
- Provides role-based computed properties
- Includes `userRole` and `dashboardRoute` getters

**Auth Middleware** (`frontend/src/middleware/auth.ts`):
- `authGuard` - Requires authentication
- `guestGuard` - Redirects authenticated users to their dashboard
- `teacherGuard` - Requires approved teacher role
- `adminGuard` - Requires admin role
- `superAdminGuard` - Requires superuser role

**Composables**:
- `useAuth` (`frontend/src/composables/useAuth.ts`) - Authentication operations with role-based redirects
- `useRoleBasedRouting` (`frontend/src/composables/useRoleBasedRouting.ts`) - Role-based navigation utilities

**Router** (`frontend/src/router/index.ts`):
- Role-based route protection
- Automatic dashboard redirection

## Role-Based Dashboard Routing

### Dashboard Routes by Role

| Role | Dashboard Route | Description |
|------|----------------|-------------|
| Superuser | `/super-admin/organizations` | Platform-wide organization management |
| Admin | `/admin/users` | Organization user management |
| Teacher (Approved) | `/teacher/courses` | Course management dashboard |
| Teacher (Pending) | `/teacher/application-status` | Application status page |
| Student | `/dashboard` | Student learning dashboard |

### How It Works

1. **Login Process**:
   ```typescript
   // User logs in
   await authStore.login({ email, password })
   
   // Backend generates JWT with role information
   // Frontend stores user data and tokens
   
   // Automatic redirect to role-specific dashboard
   router.push(authStore.dashboardRoute)
   ```

2. **Role Detection**:
   ```typescript
   // Priority: superuser > admin > teacher > student
   const userRole = computed(() => {
     if (user.is_superuser) return 'superuser'
     if (user.is_staff) return 'admin'
     if (user.is_approved_teacher) return 'teacher'
     if (user.is_teacher) return 'teacher-pending'
     return 'student'
   })
   ```

3. **Dashboard Route Selection**:
   ```typescript
   const dashboardRoute = computed(() => {
     switch (userRole.value) {
       case 'superuser': return '/super-admin/organizations'
       case 'admin': return '/admin/users'
       case 'teacher': return '/teacher/courses'
       case 'teacher-pending': return '/teacher/application-status'
       default: return '/dashboard'
     }
   })
   ```

## API Endpoints

### Authentication Endpoints

```
POST /api/accounts/auth/register/
POST /api/accounts/auth/login/
POST /api/accounts/auth/logout/
POST /api/accounts/auth/token/refresh/
POST /api/accounts/auth/password-reset/
POST /api/accounts/auth/password-reset-confirm/
POST /api/accounts/auth/google/
```

### User Management Endpoints

```
GET  /api/accounts/users/me/
PUT  /api/accounts/users/update_profile/
GET  /api/accounts/users/tenants/
POST /api/accounts/users/switch_tenant/
GET  /api/accounts/users/preferences/
```

## Usage Examples

### Backend: Creating a User with Role

```python
from apps.accounts.services import AuthService, TenantService

# Register a new teacher
user = AuthService.register_user(
    email='teacher@example.com',
    password='secure_password',
    first_name='Jane',
    last_name='Doe',
    is_teacher=True
)

# Add to organization with teacher role
tenant = Organization.objects.get(subdomain='my-org')
TenantService.add_user_to_tenant(user, tenant, role='teacher')
```

### Frontend: Login with Automatic Redirect

```vue
<script setup lang="ts">
import { useAuth } from '@/composables/useAuth'

const { login, isLoading, error } = useAuth()

const handleLogin = async () => {
  try {
    // Login automatically redirects to role-specific dashboard
    await login({
      email: 'user@example.com',
      password: 'password'
    })
    // User is now at their role-specific dashboard
  } catch (err) {
    console.error('Login failed:', err)
  }
}
</script>
```

### Frontend: Role-Based Navigation

```vue
<script setup lang="ts">
import { useRoleBasedRouting } from '@/composables/useRoleBasedRouting'

const { hasRole, getDashboardRoute, getNavigationItems } = useRoleBasedRouting()

// Check if user has specific role
if (hasRole('teacher')) {
  // Show teacher-specific content
}

// Get navigation items based on role
const navItems = getNavigationItems.value
// Returns only items accessible to current user role
</script>
```

### Frontend: Protected Routes

```typescript
// In router configuration
{
  path: '/teacher/courses',
  component: TeacherCoursesView,
  beforeEnter: teacherGuard, // Only approved teachers can access
  meta: { requiresAuth: true, requiresTeacher: true }
}
```

## Testing the System

### Test User Accounts

Create test users for each role:

```python
# In Django shell or management command
from django.contrib.auth import get_user_model
from apps.accounts.models import Organization, UserProfile

User = get_user_model()

# Create organization
org = Organization.objects.create(
    name='Test Organization',
    subdomain='test-org'
)

# Create superuser
superuser = User.objects.create_superuser(
    email='super@test.com',
    password='test123',
    first_name='Super',
    last_name='Admin'
)

# Create admin
admin = User.objects.create_user(
    email='admin@test.com',
    password='test123',
    first_name='Admin',
    last_name='User',
    is_staff=True
)
UserProfile.objects.create(user=admin, tenant=org, role='admin')

# Create approved teacher
teacher = User.objects.create_user(
    email='teacher@test.com',
    password='test123',
    first_name='Teacher',
    last_name='User'
)
UserProfile.objects.create(
    user=teacher,
    tenant=org,
    role='teacher',
    is_approved_teacher=True
)

# Create student
student = User.objects.create_user(
    email='student@test.com',
    password='test123',
    first_name='Student',
    last_name='User'
)
UserProfile.objects.create(user=student, tenant=org, role='student')
```

### Testing Login Flow

1. **Test Superuser Login**:
   - Login with `super@test.com`
   - Should redirect to `/super-admin/organizations`
   - Should see all organizations and platform-wide controls

2. **Test Admin Login**:
   - Login with `admin@test.com`
   - Should redirect to `/admin/users`
   - Should see organization management tools

3. **Test Teacher Login**:
   - Login with `teacher@test.com`
   - Should redirect to `/teacher/courses`
   - Should see course creation and management tools

4. **Test Student Login**:
   - Login with `student@test.com`
   - Should redirect to `/dashboard`
   - Should see student learning dashboard

## Security Considerations

1. **Token Security**:
   - JWT tokens include role information
   - Tokens are validated on every request
   - Refresh tokens can be blacklisted

2. **Role Validation**:
   - Backend validates roles on every endpoint
   - Frontend guards prevent unauthorized access
   - Role hierarchy is enforced (superuser > admin > teacher > student)

3. **Multi-Tenancy**:
   - Users can belong to multiple organizations
   - Role is organization-specific
   - Tenant context is included in JWT tokens

## Troubleshooting

### Issue: User not redirected after login

**Solution**: Check that:
1. JWT token includes role information
2. `authStore.dashboardRoute` is computed correctly
3. Router navigation is not blocked by guards

### Issue: User sees "Unauthorized" page

**Solution**: Verify:
1. User has correct role in database
2. Route guards match user permissions
3. Token is not expired

### Issue: Role not updating after approval

**Solution**:
1. Refresh JWT token after role change
2. Update UserProfile.is_approved_teacher
3. Clear frontend cache and re-login

## Best Practices

1. **Always use role-based routing**:
   ```typescript
   // Good
   router.push(authStore.dashboardRoute)
   
   // Avoid
   router.push('/dashboard')
   ```

2. **Check roles before showing UI elements**:
   ```vue
   <button v-if="hasRole('teacher')">Create Course</button>
   ```

3. **Validate roles on backend**:
   ```python
   if not request.user.is_superuser:
       return Response(status=403)
   ```

4. **Use composables for auth logic**:
   ```typescript
   const { hasRole, getDashboardRoute } = useRoleBasedRouting()
   ```

## Summary

The authentication system provides:
- ✅ Secure JWT-based authentication
- ✅ Role-based access control
- ✅ Automatic dashboard routing by role
- ✅ Multi-tenant support
- ✅ Teacher approval workflow
- ✅ Comprehensive role hierarchy
- ✅ Frontend and backend validation

Users are automatically redirected to their appropriate dashboard based on their role, providing a seamless and secure experience.
