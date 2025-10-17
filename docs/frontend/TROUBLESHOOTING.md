# Troubleshooting Guide

## 🚨 Common Issues and Solutions

### TypeScript Errors

#### Issue: "Failed to resolve import" or "Cannot find module"
**Cause:** Old plugin files trying to import non-existent composables
**Solution:**
✅ **FIXED**: Updated all plugin files to use the new API structure
- `src/plugins/api.ts` - Now uses `services/api`
- `src/plugins/auth.ts` - Now uses `services/auth`
- `src/plugins/toast.ts` - Simple implementation without external dependencies

#### Issue: "Cannot find name 'useRuntimeConfig'" or similar import errors
**Solution:**
```bash
# Clear TypeScript cache
rm -rf node_modules/.vite
rm -rf node_modules/.cache
rm -f tsconfig.tsbuildinfo

# Restart development server
npm run dev
```

#### Issue: "Module has no exported member 'useTokens'"
**Cause:** Old cached files or conflicting imports
**Solution:**
✅ **FIXED**: Removed all references to old composables and stores

### API Connection Issues

#### Issue: Network errors or CORS issues
**Solution:**
1. Ensure Django backend is running:
```bash
cd backend
python manage.py runserver
```

2. Check CORS settings in Django `settings/development.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

3. Verify API base URL in `.env.development`:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

#### Issue: 401 Unauthorized errors
**Cause:** JWT token issues
**Solution:**
1. Clear localStorage:
```javascript
localStorage.clear()
```
2. Try logging in again
3. Check token expiration settings in Django

### Authentication Issues

#### Issue: Login redirects not working
**Solution:**
1. Check route middleware in `src/middleware/auth.ts`
2. Verify user roles are properly set in backend
3. Check Vue Router configuration

#### Issue: Role-based access not working
**Solution:**
1. Verify user object structure matches API response
2. Check `getUserRole()` function in `useAuth` composable
3. Ensure backend returns correct user permissions

### Development Server Issues

#### Issue: Hot reload not working
**Solution:**
```bash
# Restart with clean cache
npm run dev -- --force
```

#### Issue: Build errors
**Solution:**
```bash
# Type check
npm run type-check

# Build for production
npm run build
```

## 🔧 Testing Commands

### Test API Integration
```bash
node test-integration.js
```

### Clear All Cache
```bash
node clear-cache.js
```

### Check TypeScript
```bash
npx vue-tsc --noEmit
```

### Test Backend Connection
```bash
curl http://localhost:8000/api/v1/accounts/users/
```

## 📋 Verification Checklist

### ✅ Backend Setup
- [ ] Django server running on port 8000
- [ ] Database migrations applied
- [ ] CORS configured for localhost:3000
- [ ] JWT settings configured
- [ ] API endpoints accessible

### ✅ Frontend Setup
- [ ] Node.js dependencies installed
- [ ] Environment variables configured
- [ ] TypeScript compilation successful
- [ ] Development server starts without errors
- [ ] API services properly imported

### ✅ Integration Tests
- [ ] Login/logout functionality works
- [ ] Role-based routing works
- [ ] API calls return expected data
- [ ] Error handling works properly
- [ ] Token refresh works automatically

## 🐛 Debug Mode

### Enable Debug Logging
Add to `.env.development`:
```env
VITE_DEBUG=true
```

### Check Network Requests
1. Open browser DevTools (F12)
2. Go to Network tab
3. Filter by XHR/Fetch
4. Monitor API requests and responses

### Check Console Errors
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for JavaScript errors
4. Check for failed API requests

## 📞 Getting Help

### Common Error Messages

#### "Failed to fetch"
- Backend server not running
- CORS configuration issue
- Network connectivity problem

#### "401 Unauthorized"
- Invalid or expired JWT token
- Authentication middleware issue
- Backend authentication configuration

#### "404 Not Found"
- API endpoint doesn't exist
- Incorrect API base URL
- Backend routing issue

#### "500 Internal Server Error"
- Backend application error
- Database connection issue
- Check Django logs

### Debug Information to Collect

When reporting issues, include:
1. Browser console errors
2. Network tab showing failed requests
3. Backend server logs
4. Environment configuration
5. Steps to reproduce the issue

## 🔄 Reset Everything

If all else fails, complete reset:

```bash
# Frontend
rm -rf node_modules
rm -rf dist
rm -f package-lock.json
npm install
npm run dev

# Backend
cd backend
python manage.py migrate
python manage.py runserver

# Browser
# Clear all site data in DevTools > Application > Storage
```

## 📚 Additional Resources

- [Vue 3 Documentation](https://vuejs.org/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Axios Documentation](https://axios-http.com/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Configuration](https://vitejs.dev/config/)