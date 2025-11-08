# 🔧 Login Issue Fix Guide

## Issue Identified

The login is failing with a 400 Bad Request error. Here's what was fixed and what to check:

## ✅ Fixed

### 1. API Base URL Configuration
**Problem**: The API service was using `globalThis.VITE_API_BASE_URL` instead of `import.meta.env.VITE_API_BASE_URL`

**Fixed in**: `frontend/src/services/api.ts`

```typescript
// Before (WRONG)
const API_BASE_URL = (globalThis as any)?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// After (CORRECT)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
```

### 2. Development Mode Checks
**Problem**: Using `globalThis.DEV` instead of `import.meta.env.DEV`

**Fixed**: All development mode checks now use `import.meta.env.DEV`

## 🔍 Troubleshooting Steps

### Step 1: Verify Backend is Running

```bash
# Check if backend is running
curl http://localhost:8000/api/v1/health/

# Or check in browser
# Open: http://localhost:8000/api/v1/
```

**Expected**: Should return a response (not connection refused)

### Step 2: Check Environment Variables

```bash
# In frontend directory
cat .env.development
```

**Verify**:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Step 3: Restart Frontend Dev Server

```bash
# Stop the frontend server (Ctrl+C)
# Then restart
cd frontend
npm run dev
# or
pnpm run dev
```

### Step 4: Check Backend Logs

Look at the backend terminal for the actual error. The 400 error might be due to:

1. **Missing required fields** in login request
2. **Invalid data format**
3. **CSRF token issues**
4. **Serializer validation errors**

### Step 5: Test Backend Directly

```bash
# Test login endpoint directly
curl -X POST http://localhost:8000/api/v1/accounts/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"student@test.com","password":"test123"}'
```

**Expected**: Should return tokens or specific error message

## 🔧 Quick Fixes

### Fix 1: Clear Browser Cache

1. Open DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"

### Fix 2: Clear LocalStorage

```javascript
// In browser console
localStorage.clear()
location.reload()
```

### Fix 3: Restart Both Servers

```bash
# Terminal 1 - Backend
cd backend
python manage.py runserver

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## 📋 Checklist

- [ ] Backend server is running on port 8000
- [ ] Frontend server is running on port 5173
- [ ] Environment variables are correct
- [ ] Browser cache cleared
- [ ] LocalStorage cleared
- [ ] Both servers restarted

## 🐛 Common Issues

### Issue: "ERR_NAME_NOT_RESOLVED"
**Cause**: Backend not running or wrong URL
**Fix**: Start backend server

### Issue: 400 Bad Request
**Causes**:
1. Missing email or password field
2. Invalid email format
3. Backend validation error

**Check**: Backend terminal for specific error

### Issue: CORS Error
**Cause**: CORS not configured
**Fix**: Already configured in `backend/config/settings/base.py`

### Issue: 401 Unauthorized
**Cause**: Invalid credentials
**Fix**: Use correct test credentials:
```
Email: student@test.com
Password: test123
```

## 🔍 Debug Mode

### Enable Detailed Logging

The API service now logs all requests in development mode. Check browser console for:

```
🚀 API Request [req_xxx]: { method, url, data }
✅ API Response [req_xxx]: { status, duration, data }
❌ API Error [req_xxx]: { status, message, response }
```

### Check Network Tab

1. Open DevTools (F12)
2. Go to Network tab
3. Try to login
4. Click on the failed request
5. Check:
   - Request URL
   - Request Headers
   - Request Payload
   - Response

## 📝 Expected Login Flow

1. **Frontend sends**:
```json
POST /api/v1/accounts/auth/login/
{
  "email": "student@test.com",
  "password": "test123"
}
```

2. **Backend responds**:
```json
{
  "success": true,
  "data": {
    "user": { ... },
    "access": "jwt_token",
    "refresh": "refresh_token"
  }
}
```

3. **Frontend stores**:
- `access_token` in localStorage
- `refresh_token` in localStorage
- `user` data in localStorage

4. **Frontend redirects** to role-specific dashboard

## 🚀 Next Steps

1. **Restart both servers**
2. **Clear browser cache**
3. **Try login again**
4. **Check backend logs** for specific error
5. **Check browser console** for detailed logs

## 📞 Still Having Issues?

If the issue persists:

1. **Check backend logs** - Look for the actual error message
2. **Test backend directly** - Use curl or Postman
3. **Verify test users exist** - Run `python manage.py shell < test_auth_roles.py`
4. **Check database** - Ensure migrations are applied

## 🔗 Related Documentation

- [Auth System Guide](docs/auth/AUTH_SYSTEM_GUIDE.md)
- [API Documentation](docs/api/API_README.md)
- [Troubleshooting](docs/frontend/TROUBLESHOOTING.md)

---

**Last Updated**: November 2025  
**Status**: Fixed - Restart servers to apply changes
