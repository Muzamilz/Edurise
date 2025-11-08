# Quick Authentication & Routing Reference

## 🎯 Role-Based Dashboard Routes

| Role | Dashboard | Access Level |
|------|-----------|--------------|
| 🔴 **Superuser** | `/super-admin/organizations` | Platform-wide admin |
| 🟠 **Admin** | `/admin/users` | Organization admin |
| 🟢 **Teacher** | `/teacher/courses` | Course creator |
| 🟡 **Teacher (Pending)** | `/teacher/application-status` | Awaiting approval |
| 🔵 **Student** | `/dashboard` | Learner |

## 🔐 Test Credentials

```
Superuser:  superuser@test.com / test123
Admin:      admin@test.com / test123
Teacher:    teacher@test.com / test123
Pending:    teacher-pending@test.com / test123
Student:    student@test.com / test123
```

## 🚀 Quick Start

### Create Test Users
```bash
cd backend
python manage.py shell < test_auth_roles.py
```

### Start Servers
```bash
# Terminal 1 - Backend
cd backend && python manage.py runserver

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Test Login
1. Go to http://localhost:5173/auth/login
2. Login with any test credential
3. Verify automatic redirect to correct dashboard

## 💻 Code Examples

### Frontend: Get User Role
```typescript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const role = authStore.userRole // 'superuser', 'admin', 'teacher', 'student'
const dashboard = authStore.dashboardRoute // Role-specific route
```

### Frontend: Navigate to Dashboard
```typescript
import { useRoleBasedRouting } from '@/composables/useRoleBasedRouting'

const { goToDashboard } = useRoleBasedRouting()
await goToDashboard() // Goes to role-specific dashboard
```

### Frontend: Check Role
```typescript
import { useRoleBasedRouting } from '@/composables/useRoleBasedRouting'

const { hasRole } = useRoleBasedRouting()

if (hasRole('teacher')) {
  // Show teacher features
}
```

### Frontend: Role-Based UI
```vue
<template>
  <button v-if="isSuperuser">Manage Platform</button>
  <button v-if="isStaff">Manage Organization</button>
  <button v-if="isApprovedTeacher">Create Course</button>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const { isSuperuser, isStaff, isApprovedTeacher } = useAuthStore()
</script>
```

### Backend: Generate Tokens with Role
```python
from apps.accounts.services import JWTAuthService

tokens = JWTAuthService.generate_tokens(user, tenant)
# Returns tokens with role information
```

### Backend: Check User Role
```python
# In views or services
if request.user.is_superuser:
    # Superuser access
elif request.user.is_staff:
    # Admin access
elif request.user.is_approved_teacher:
    # Teacher access
else:
    # Student access
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

## 📋 Common Tasks

### Add New Role
1. Update role hierarchy in `services.py`
2. Add dashboard route in `auth.ts`
3. Create route guard if needed
4. Update documentation

### Change User Role
```python
# In Django shell or admin
profile = UserProfile.objects.get(user=user, tenant=tenant)
profile.role = 'teacher'
profile.is_approved_teacher = True
profile.save()
```

### Debug Login Issues
1. Check browser console for errors
2. Verify JWT token includes role
3. Check `authStore.userRole` value
4. Verify `authStore.dashboardRoute` is correct
5. Check route guards aren't blocking

## 📚 Documentation

- **Full Guide**: `AUTH_SYSTEM_GUIDE.md`
- **Implementation Summary**: `AUTH_SYSTEM_IMPLEMENTATION_SUMMARY.md`
- **This Reference**: `QUICK_AUTH_REFERENCE.md`

## ✅ Verification Checklist

- [ ] Test users created successfully
- [ ] Backend server running
- [ ] Frontend server running
- [ ] Login redirects to correct dashboard
- [ ] Role-specific features visible
- [ ] Unauthorized access blocked
- [ ] Navigation items match role

## 🐛 Troubleshooting

**Issue**: Not redirected after login
- Check `authStore.dashboardRoute` in console
- Verify JWT token has role field
- Check router navigation logs

**Issue**: See "Unauthorized" page
- Verify user role in database
- Check route guard requirements
- Ensure token not expired

**Issue**: Wrong dashboard shown
- Check `authStore.userRole` value
- Verify role hierarchy logic
- Clear localStorage and re-login

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

## 🔄 Login Flow

```
User Login
    ↓
Backend Auth
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

## 📞 Need Help?

1. Read `AUTH_SYSTEM_GUIDE.md` for details
2. Check test script output
3. Verify JWT token structure
4. Review browser console
5. Check backend logs

---

**Last Updated**: November 2025
**Version**: 1.0
