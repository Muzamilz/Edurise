# Authentication System Testing Checklist

## 📋 Pre-Testing Setup

### ✅ Backend Setup
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] Test users created (`python manage.py shell < test_auth_roles.py`)
- [ ] Backend server running (`python manage.py runserver`)
- [ ] Backend accessible at `http://localhost:8000`

### ✅ Frontend Setup
- [ ] Frontend dependencies installed (`npm install` or `pnpm install`)
- [ ] Environment variables configured (`.env.development`)
- [ ] Frontend server running (`npm run dev`)
- [ ] Frontend accessible at `http://localhost:5173`

## 🧪 Test Scenarios

### Test 1: Superuser Login & Routing
- [ ] Navigate to `http://localhost:5173/auth/login`
- [ ] Login with `superuser@test.com` / `test123`
- [ ] **Expected**: Automatic redirect to `/super-admin/organizations`
- [ ] **Verify**: SuperAdmin dashboard is displayed
- [ ] **Verify**: Navigation shows superuser-specific items
- [ ] **Verify**: Can access all admin routes

**Result**: ✅ Pass / ❌ Fail

**Notes**: _______________________________________

---

### Test 2: Admin Login & Routing
- [ ] Logout (if logged in)
- [ ] Navigate to `http://localhost:5173/auth/login`
- [ ] Login with `admin@test.com` / `test123`
- [ ] **Expected**: Automatic redirect to `/admin/users`
- [ ] **Verify**: Admin dashboard is displayed
- [ ] **Verify**: Can access admin routes
- [ ] **Verify**: Cannot access super-admin routes (should see unauthorized)

**Result**: ✅ Pass / ❌ Fail

**Notes**: _______________________________________

---

### Test 3: Approved Teacher Login & Routing
- [ ] Logout (if logged in)
- [ ] Navigate to `http://localhost:5173/auth/login`
- [ ] Login with `teacher@test.com` / `test123`
- [ ] **Expected**: Automatic redirect to `/teacher/courses`
- [ ] **Verify**: Teacher dashboard is displayed
- [ ] **Verify**: Can access "Create Course" button
- [ ] **Verify**: Can access teacher-specific routes
- [ ] **Verify**: Cannot access admin routes

**Result**: ✅ Pass / ❌ Fail

**Notes**: _______________________________________

---

### Test 4: Pending Teacher Login & Routing
- [ ] Logout (if logged in)
- [ ] Navigate to `http://localhost:5173/auth/login`
- [ ] Login with `teacher-pending@test.com` / `test123`
- [ ] **Expected**: Automatic redirect to `/teacher/application-status`
- [ ] **Verify**: Application status page is displayed
- [ ] **Verify**: Cannot access "Create Course" (should be disabled/hidden)
- [ ] **Verify**: Can access student features

**Result**: ✅ Pass / ❌ Fail

**Notes**: _______________________________________

---

### Test 5: Student Login & Routing
- [ ] Logout (if logged in)
- [ ] Navigate to `http://localhost:5173/auth/login`
- [ ] Login with `student@test.com` / `test123`
- [ ] **Expected**: Automatic redirect to `/dashboard`
- [ ] **Verify**: Student dashboard is displayed
- [ ] **Verify**: Can access "My Courses", "Live Classes", etc.
- [ ] **Verify**: Cannot access teacher or admin routes

**Result**: ✅ Pass / ❌ Fail

**Notes**: _______________________________________

---

### Test 6: Guest Guard (Already Logged In)
- [ ] Ensure you're logged in (any role)
- [ ] Try to navigate to `/auth/login`
- [ ] **Expected**: Automatic redirect to role-specific dashboard
- [ ] **Verify**: Cannot access login page while authenticated

**Result**: ✅ Pass / ❌ Fail

**Notes**: _______________________________________

---

### Test 7: Auth Guard (Not Logged In)
- [ ] Logout completely
- [ ] Try to navigate to `/dashboard`
- [ ] **Expected**: Redirect to `/auth/login`
- [ ] **Verify**: Login page is displayed
- [ ] **Verify**: After login, redirected to intended page or dashboard

**Result**: ✅ Pass / ❌ Fail

**Notes**: _______________________________________

---

### Test 8: Role-Based Route Protection
- [ ] Login as student (`student@test.com`)
- [ ] Try to navigate to `/teacher/courses`
- [ ] **Expected**: Redirect to `/unauthorized` or blocked
- [ ] Try to navigate to `/admin/users`
- [ ] **Expected**: Redirect to `/unauthorized` or blocked

**Result**: ✅ Pass / ❌ Fail

**Notes**: _______________________________________

---

### Test 9: Token Refresh
- [ ] Login with any user
- [ ] Wait for access token to expire (or manually expire it)
- [ ] Make an API request
- [ ] **Expected**: Token automatically refreshes
- [ ] **Verify**: User remains logged in
- [ ] **Verify**: Request succeeds after refresh

**Result**: ✅ Pass / ❌ Fail

**Notes**: _______________________________________

---

### Test 10: Logout & Cleanup
- [ ] Login with any user
- [ ] Click logout
- [ ] **Expected**: Redirect to `/auth/login`
- [ ] **Verify**: Tokens removed from localStorage
- [ ] **Verify**: User state cleared
- [ ] **Verify**: Cannot access protected routes

**Result**: ✅ Pass / ❌ Fail

**Notes**: _______________________________________

---

### Test 11: Registration with Role
- [ ] Navigate to `/auth/register`
- [ ] Register as a new student
- [ ] **Expected**: Automatic redirect to `/dashboard`
- [ ] Register as a new teacher
- [ ] **Expected**: Automatic redirect to `/teacher/application-status`

**Result**: ✅ Pass / ❌ Fail

**Notes**: _______________________________________

---

### Test 12: Multi-Tenant Switching
- [ ] Login as a user with multiple organizations
- [ ] Use tenant switcher to change organization
- [ ] **Expected**: New JWT token generated
- [ ] **Verify**: Tenant-specific data displayed
- [ ] **Verify**: Role may change based on tenant

**Result**: ✅ Pass / ❌ Fail

**Notes**: _______________________________________

---

## 🔍 Browser Console Checks

### Check 1: JWT Token Structure
- [ ] Login with any user
- [ ] Open browser console
- [ ] Check localStorage: `localStorage.getItem('access_token')`
- [ ] Decode JWT at https://jwt.io
- [ ] **Verify**: Token includes `role` field
- [ ] **Verify**: Token includes `is_teacher`, `is_approved_teacher`, etc.
- [ ] **Verify**: Token includes tenant information (if applicable)

**Result**: ✅ Pass / ❌ Fail

**Token Payload**:
```json
{
  "role": "___________",
  "is_teacher": _______,
  "is_approved_teacher": _______,
  "is_staff": _______,
  "is_superuser": _______
}
```

---

### Check 2: Auth Store State
- [ ] Login with any user
- [ ] Open Vue DevTools
- [ ] Navigate to Pinia store → auth
- [ ] **Verify**: `user` object is populated
- [ ] **Verify**: `userRole` computed property is correct
- [ ] **Verify**: `dashboardRoute` computed property is correct
- [ ] **Verify**: `isAuthenticated` is true

**Result**: ✅ Pass / ❌ Fail

**Store State**:
```
userRole: ___________
dashboardRoute: ___________
isAuthenticated: ___________
```

---

### Check 3: API Requests
- [ ] Login with any user
- [ ] Open Network tab in DevTools
- [ ] Make any API request
- [ ] **Verify**: Request includes `Authorization: Bearer <token>` header
- [ ] **Verify**: Request includes `X-Tenant-ID` header (if applicable)
- [ ] **Verify**: Response is successful (200-299)

**Result**: ✅ Pass / ❌ Fail

---

## 🐛 Common Issues & Solutions

### Issue: Not redirected after login
**Check**:
- [ ] Browser console for errors
- [ ] `authStore.dashboardRoute` value
- [ ] Router navigation logs
- [ ] JWT token includes role field

**Solution**: _______________________________________

---

### Issue: See "Unauthorized" page
**Check**:
- [ ] User role in database
- [ ] Route guard requirements
- [ ] Token expiration
- [ ] Role hierarchy logic

**Solution**: _______________________________________

---

### Issue: Wrong dashboard displayed
**Check**:
- [ ] `authStore.userRole` value
- [ ] Role detection logic in auth store
- [ ] User flags in database (is_staff, is_superuser, etc.)

**Solution**: _______________________________________

---

### Issue: Token refresh fails
**Check**:
- [ ] Refresh token in localStorage
- [ ] Token expiration time
- [ ] Backend token refresh endpoint
- [ ] Network connectivity

**Solution**: _______________________________________

---

## 📊 Test Results Summary

| Test | Status | Notes |
|------|--------|-------|
| 1. Superuser Login | ⬜ | |
| 2. Admin Login | ⬜ | |
| 3. Teacher Login | ⬜ | |
| 4. Pending Teacher Login | ⬜ | |
| 5. Student Login | ⬜ | |
| 6. Guest Guard | ⬜ | |
| 7. Auth Guard | ⬜ | |
| 8. Route Protection | ⬜ | |
| 9. Token Refresh | ⬜ | |
| 10. Logout | ⬜ | |
| 11. Registration | ⬜ | |
| 12. Tenant Switching | ⬜ | |

**Overall Status**: ⬜ All Pass / ⬜ Some Fail / ⬜ Not Tested

---

## 📝 Additional Notes

### Environment
- Backend URL: _______________________________________
- Frontend URL: _______________________________________
- Database: _______________________________________
- Browser: _______________________________________
- Date Tested: _______________________________________

### Observations
_______________________________________
_______________________________________
_______________________________________

### Recommendations
_______________________________________
_______________________________________
_______________________________________

---

## ✅ Sign-Off

**Tested By**: _______________________________________

**Date**: _______________________________________

**Signature**: _______________________________________

---

**Next Steps After Testing**:
1. [ ] Document any issues found
2. [ ] Create tickets for bugs
3. [ ] Update documentation if needed
4. [ ] Deploy to staging environment
5. [ ] Conduct user acceptance testing
