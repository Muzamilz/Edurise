# 🔐 Authentication System Documentation

Complete documentation for the EduRise authentication and role-based routing system.

## 📚 Documentation Files

### 🚀 Getting Started
- **[README_AUTH_SYSTEM.md](README_AUTH_SYSTEM.md)** - Start here! Quick overview and setup guide

### 📖 Complete Guides
- **[AUTH_SYSTEM_INDEX.md](AUTH_SYSTEM_INDEX.md)** - Complete documentation index
- **[AUTH_SYSTEM_GUIDE.md](AUTH_SYSTEM_GUIDE.md)** - Comprehensive architecture guide
- **[AUTH_SYSTEM_IMPLEMENTATION_SUMMARY.md](AUTH_SYSTEM_IMPLEMENTATION_SUMMARY.md)** - Implementation details

### 🎯 Quick References
- **[QUICK_AUTH_REFERENCE.md](QUICK_AUTH_REFERENCE.md)** - Quick reference card
- **[AUTH_FLOW_DIAGRAM.md](AUTH_FLOW_DIAGRAM.md)** - Visual flow diagrams

### 🧪 Testing
- **[AUTH_TESTING_CHECKLIST.md](AUTH_TESTING_CHECKLIST.md)** - Testing checklist

## 🎭 Role-Based Dashboards

| Role | Dashboard | Access Level |
|------|-----------|--------------|
| 🔴 Superuser | `/super-admin/organizations` | Platform-wide admin |
| 🟠 Admin | `/admin/users` | Organization admin |
| 🟢 Teacher | `/teacher/courses` | Course creator |
| 🟡 Pending Teacher | `/teacher/application-status` | Awaiting approval |
| 🔵 Student | `/dashboard` | Learner |

## 🚀 Quick Start

```bash
# 1. Create test users
cd backend
python manage.py shell < test_auth_roles.py

# 2. Start servers
# Terminal 1
cd backend && python manage.py runserver

# Terminal 2
cd frontend && npm run dev

# 3. Test login at http://localhost:5173/auth/login
```

## 🔐 Test Credentials

```
Superuser:  superuser@test.com / test123
Admin:      admin@test.com / test123
Teacher:    teacher@test.com / test123
Pending:    teacher-pending@test.com / test123
Student:    student@test.com / test123
```

## 📖 Reading Order

1. **New to the system?** → [README_AUTH_SYSTEM.md](README_AUTH_SYSTEM.md)
2. **Need quick reference?** → [QUICK_AUTH_REFERENCE.md](QUICK_AUTH_REFERENCE.md)
3. **Want deep dive?** → [AUTH_SYSTEM_GUIDE.md](AUTH_SYSTEM_GUIDE.md)
4. **Ready to test?** → [AUTH_TESTING_CHECKLIST.md](AUTH_TESTING_CHECKLIST.md)
5. **Visual learner?** → [AUTH_FLOW_DIAGRAM.md](AUTH_FLOW_DIAGRAM.md)

## 🔑 Key Features

- ✅ Automatic role detection
- ✅ Smart dashboard routing
- ✅ JWT authentication
- ✅ Multi-tenant support
- ✅ Teacher approval workflow
- ✅ Type-safe TypeScript
- ✅ Comprehensive testing

---

**Back to**: [Main Documentation Index](../INDEX.md)
