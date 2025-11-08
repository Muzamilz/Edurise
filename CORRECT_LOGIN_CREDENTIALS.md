# ✅ Correct Login Credentials

## 🔴 Issue

You're trying to login with `admin@edurise.com` but that user doesn't exist in the database.

## ✅ Solution

Use the correct test user credentials that were created by the test script.

## 🔐 Valid Test Credentials

| Role | Email | Password | Dashboard |
|------|-------|----------|-----------|
| 🔴 **Superuser** | `superuser@test.com` | `test123` | /super-admin/organizations |
| 🟠 **Admin** | `admin@test.com` | `test123` | /admin/users |
| 🟢 **Teacher** | `teacher@test.com` | `test123` | /teacher/courses |
| 🟡 **Pending Teacher** | `teacher-pending@test.com` | `test123` | /teacher/application-status |
| 🔵 **Student** | `student@test.com` | `test123` | /dashboard |

## 🚀 Quick Test

Try logging in with:
```
Email: admin@test.com
Password: test123
```

This should redirect you to `/admin/users` dashboard.

## 📋 API Routing

The authentication goes through the centralized API:

```
Frontend Request:
POST http://localhost:8000/api/v1/accounts/auth/login/

Routing:
/api/ → apps.api.urls
  /v1/accounts/ → apps.accounts.urls
    /auth/login/ → LoginView
```

## 🔧 If Users Don't Exist

Run the test script to create them:

```bash
cd backend
python manage.py shell < test_auth_roles.py
```

This will create all 5 test users with the correct credentials.

## ✨ Expected Behavior

1. **Enter credentials**: `admin@test.com` / `test123`
2. **Backend validates**: Checks email and password
3. **Backend generates JWT**: With role information
4. **Frontend stores tokens**: In localStorage
5. **Frontend redirects**: To `/admin/users` (admin dashboard)

## 🐛 Common Mistakes

❌ **Wrong**: `admin@edurise.com`  
✅ **Correct**: `admin@test.com`

❌ **Wrong**: `student@edurise.com`  
✅ **Correct**: `student@test.com`

❌ **Wrong**: `teacher@edurise.com`  
✅ **Correct**: `teacher@test.com`

## 📝 Create Custom User

If you want to use `admin@edurise.com`, create it:

```bash
cd backend
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from apps.accounts.models import Organization, UserProfile

User = get_user_model()

# Get or create organization
org, _ = Organization.objects.get_or_create(
    subdomain='edurise',
    defaults={'name': 'Edurise', 'is_active': True}
)

# Create admin user
admin = User.objects.create_user(
    email='admin@edurise.com',
    password='test123',
    first_name='Admin',
    last_name='User',
    is_staff=True
)

# Create profile
UserProfile.objects.create(
    user=admin,
    tenant=org,
    role='admin'
)

print("✅ Created admin@edurise.com")
```

## 🎯 Summary

**Use these credentials to login:**
- Email: `admin@test.com`
- Password: `test123`

**Or run the test script to create all users:**
```bash
python manage.py shell < test_auth_roles.py
```

---

**Status**: ✅ API is working correctly  
**Issue**: Wrong email address  
**Fix**: Use `admin@test.com` instead of `admin@edurise.com`
