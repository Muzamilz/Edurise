# 🔐 Authentication & Role-Based Routing System

## Overview

A complete authentication system with automatic role-based dashboard routing for the EduRise learning management platform. Users are automatically redirected to their appropriate dashboard based on their role after login.

## 🎯 Key Features

- ✅ **Automatic Role Detection** - System determines user role from JWT token
- ✅ **Smart Dashboard Routing** - Each role redirects to specific dashboard
- ✅ **Role Hierarchy** - Superuser > Admin > Teacher > Student
- ✅ **Multi-Tenant Support** - Users can belong to multiple organizations
- ✅ **Teacher Approval Workflow** - Pending teachers have limited access
- ✅ **Secure JWT Authentication** - Tokens include comprehensive role information
- ✅ **Route Protection** - Guards prevent unauthorized access
- ✅ **Type-Safe** - Full TypeScript support

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[AUTH_SYSTEM_GUIDE.md](AUTH_SYSTEM_GUIDE.md)** | Complete system architecture and usage guide |
| **[AUTH_SYSTEM_IMPLEMENTATION_SUMMARY.md](AUTH_SYSTEM_IMPLEMENTATION_SUMMARY.md)** | Summary of changes and implementation details |
| **[QUICK_AUTH_REFERENCE.md](QUICK_AUTH_REFERENCE.md)** | Quick reference for common tasks |
| **[AUTH_FLOW_DIAGRAM.md](AUTH_FLOW_DIAGRAM.md)** | Visual flow diagrams |
| **[AUTH_TESTING_CHECKLIST.md](AUTH_TESTING_CHECKLIST.md)** | Comprehensive testing checklist |

## 🚀 Quick Start

### 1. Create Test Users

```bash
cd backend
python manage.py shell < test_auth_roles.py
```

This creates 5 test users with different roles.

### 2. Start Servers

```bash
# Terminal 1 - Backend
cd backend
python manage.py runserver

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 3. Test Login

Navigate to `http://localhost:5173/auth/login` and login with any test credential:

| Role | Email | Password | Expected Dashboard |
|------|-------|----------|-------------------|
| Superuser | superuser@test.com | test123 | /super-admin/organizations |
| Admin | admin@test.com | test123 | /admin/users |
| Teacher | teacher@test.com | test123 | /teacher/courses |
| Pending | teacher-pending@test.com | test123 | /teacher/application-status |
| Student | student@test.com | test123 | /dashboard |

## 🎭 Role-Based Dashboards

```
🔴 Superuser → /super-admin/organizations
   Platform-wide administrator with full access

🟠 Admin → /admin/users
   Organization administrator managing users and content

🟢 Teacher → /teacher/courses
   Approved teacher creating and managing courses

🟡 Teacher (Pending) → /teacher/application-status
   Teacher awaiting approval with limited access

🔵 Student → /dashboard
   Learner accessing courses and content
```

## 💻 Usage Examples

### Frontend: Check User Role

```typescript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Get user role
const role = authStore.userRole // 'superuser', 'admin', 'teacher', 'student'

// Get dashboard route
const dashboard = authStore.dashboardRoute // Role-specific route
```

### Frontend: Navigate to Dashboard

```typescript
import { useRoleBasedRouting } from '@/composables/useRoleBasedRouting'

const { goToDashboard } = useRoleBasedRouting()

// Navigate to user's role-specific dashboard
await goToDashboard()
```

### Frontend: Role-Based UI

```vue
<template>
  <div>
    <button v-if="hasRole('teacher')">Create Course</button>
    <button v-if="hasRole('admin')">Manage Users</button>
    <button v-if="hasRole('superuser')">Manage Platform</button>
  </div>
</template>

<script setup lang="ts">
import { useRoleBasedRouting } from '@/composables/useRoleBasedRouting'

const { hasRole } = useRoleBasedRouting()
</script>
```

### Backend: Generate Tokens with Role

```python
from apps.accounts.services import JWTAuthService

# Generate tokens with role information
tokens = JWTAuthService.generate_tokens(user, tenant)

# Token includes:
# - role: 'superuser', 'admin', 'teacher', or 'student'
# - is_teacher, is_approved_teacher, is_staff, is_superuser
# - tenant information
```

## 🔐 JWT Token Structure

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

## 🛡️ Route Guards

```typescript
// Require authentication
beforeEnter: authGuard

// Require teacher role
beforeEnter: teacherGuard

// Require admin role
beforeEnter: adminGuard

// Require superuser role
beforeEnter: superAdminGuard

// Guest only (redirect if authenticated)
beforeEnter: guestGuard
```

## 📋 API Endpoints

### Authentication
```
POST /api/accounts/auth/register/
POST /api/accounts/auth/login/
POST /api/accounts/auth/logout/
POST /api/accounts/auth/token/refresh/
POST /api/accounts/auth/password-reset/
POST /api/accounts/auth/password-reset-confirm/
POST /api/accounts/auth/google/
```

### User Management
```
GET  /api/accounts/users/me/
PUT  /api/accounts/users/update_profile/
GET  /api/accounts/users/tenants/
POST /api/accounts/users/switch_tenant/
GET  /api/accounts/users/preferences/
```

## 🔄 Login Flow

```
User Login
    ↓
Backend Authenticates
    ↓
Generate JWT (with role)
    ↓
Frontend Stores Token
    ↓
Compute User Role
    ↓
Redirect to Dashboard
    ↓
Show Role-Specific UI
```

## 🎓 Role Hierarchy

```
Superuser (Highest)
    ↓
  Admin
    ↓
 Teacher
    ↓
 Student (Lowest)
```

Higher roles inherit lower role permissions.

## 🧪 Testing

Follow the comprehensive testing checklist in [AUTH_TESTING_CHECKLIST.md](AUTH_TESTING_CHECKLIST.md).

### Quick Test

1. Create test users: `python manage.py shell < test_auth_roles.py`
2. Start servers (backend & frontend)
3. Login with each test user
4. Verify automatic redirect to correct dashboard

## 🐛 Troubleshooting

### Not redirected after login?
- Check `authStore.dashboardRoute` in browser console
- Verify JWT token includes `role` field
- Check router navigation logs

### See "Unauthorized" page?
- Verify user role in database
- Check route guard requirements
- Ensure token not expired

### Wrong dashboard shown?
- Check `authStore.userRole` value
- Verify role hierarchy logic
- Clear localStorage and re-login

## 📦 Files Modified

### Backend
- `backend/apps/accounts/serializers.py` - Enhanced UserSerializer with role
- `backend/apps/accounts/services.py` - Enhanced JWT token generation
- `backend/test_auth_roles.py` - Test script for creating users

### Frontend
- `frontend/src/stores/auth.ts` - Added userRole and dashboardRoute
- `frontend/src/middleware/auth.ts` - Updated guestGuard
- `frontend/src/composables/useAuth.ts` - Role-based redirects
- `frontend/src/composables/useRoleBasedRouting.ts` - New composable

### Documentation
- `AUTH_SYSTEM_GUIDE.md` - Complete guide
- `AUTH_SYSTEM_IMPLEMENTATION_SUMMARY.md` - Implementation summary
- `QUICK_AUTH_REFERENCE.md` - Quick reference
- `AUTH_FLOW_DIAGRAM.md` - Visual diagrams
- `AUTH_TESTING_CHECKLIST.md` - Testing checklist
- `README_AUTH_SYSTEM.md` - This file

## 🎯 Benefits

1. **Clear User Experience** - Users always land on the right dashboard
2. **Reduced Confusion** - No need to navigate after login
3. **Better Security** - Role-based access from the start
4. **Maintainable Code** - Centralized role logic
5. **Scalable** - Easy to add new roles
6. **Type-Safe** - TypeScript ensures correct usage

## 🔮 Future Enhancements

- [ ] Add more granular permissions within roles
- [ ] Implement role-based feature flags
- [ ] Add audit logging for role changes
- [ ] Create admin UI for role management
- [ ] Add role-based email notifications
- [ ] Implement temporary role elevation

## 📞 Support

For questions or issues:
1. Check the comprehensive guide: [AUTH_SYSTEM_GUIDE.md](AUTH_SYSTEM_GUIDE.md)
2. Review test script output for debugging
3. Verify JWT token includes role information
4. Check browser console for routing errors

## 📄 License

This authentication system is part of the EduRise platform.

---

**Last Updated**: November 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready
