# Render Deployment Guide - Edurise Frontend

## Overview
This guide will help you deploy the Edurise frontend as a static site on Render's free plan.

## Prerequisites
- Render account (free)
- GitHub repository with your code
- Backend API deployed (if needed)

## Quick Deployment Steps

### 1. Connect Repository to Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Static Site"
3. Connect your GitHub repository
4. Select the repository containing this code

### 2. Configure Build Settings
```
Name: edurise-frontend
Branch: main (or your default branch)
Build Command: cd frontend && npm install && npm run build
Publish Directory: frontend/dist
```

### 3. Environment Variables
Add these in Render's environment variables section:

**Required:**
- `VITE_API_BASE_URL`: Your backend API URL (e.g., `https://your-backend.onrender.com/api/v1`)
- `VITE_WS_BASE_URL`: Your WebSocket URL (e.g., `wss://your-backend.onrender.com/ws`)
- `VITE_APP_NAME`: `Edurise`
- `VITE_DEBUG`: `false`

**Optional (add your production keys):**
- `VITE_GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `VITE_STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
- `VITE_PAYPAL_CLIENT_ID`: Your PayPal client ID
- `VITE_ZOOM_SDK_KEY`: Your Zoom SDK key

### 4. Deploy
Click "Create Static Site" and wait for deployment to complete.

## Alternative: Using render.yaml

If you prefer Infrastructure as Code, use the included `render.yaml`:

1. Update the environment variables in `render.yaml` with your actual values
2. Push to your repository
3. Render will automatically detect and deploy using the configuration

## Post-Deployment Checklist

### ✅ Verify Deployment
- [ ] Site loads at your Render URL
- [ ] All routes work (navigation doesn't show 404)
- [ ] API calls reach your backend
- [ ] WebSocket connections work (if applicable)
- [ ] OAuth flows work (if configured)

### 🔧 Troubleshooting

**Issue: 404 on direct URL access**
- Solution: The `_redirects` file should handle this. Verify it exists in `frontend/dist/`

**Issue: API calls fail**
- Check `VITE_API_BASE_URL` environment variable
- Verify backend CORS settings allow your frontend domain
- Check browser network tab for specific errors

**Issue: WebSocket connection fails**
- Ensure `VITE_WS_BASE_URL` uses `wss://` (not `ws://`)
- Verify backend WebSocket endpoint is accessible

**Issue: Build fails**
- Check build logs in Render dashboard
- Verify all dependencies are in `package.json`
- Try building locally first: `cd frontend && npm install && npm run build`

## Performance Optimization

### Already Implemented
- ✅ Code splitting by route
- ✅ Manual chunks for heavy libraries (Three.js, animations)
- ✅ CSS extraction and minification
- ✅ Asset hashing for cache busting

### Additional Optimizations
- Consider lazy loading 3D features if not needed immediately
- Monitor bundle size with `npm run build` and check output
- Use Render's CDN for global distribution

## Cost Considerations

### Render Free Plan Limits
- ✅ Static sites are completely free
- ✅ No runtime costs
- ✅ Automatic SSL certificates
- ✅ Global CDN included

### Backend Considerations
- Backend services on Render free plan sleep after 15 minutes
- Consider upgrading backend to paid plan for production use
- Frontend will work even if backend is sleeping (graceful degradation)

## Security Notes

### Environment Variables
- Never commit production keys to repository
- Use Render's environment variable system
- Rotate keys regularly
- Use different keys for development/production

### HTTPS
- Render provides automatic HTTPS
- All API calls should use HTTPS endpoints
- WebSocket connections should use WSS

## Monitoring

### Built-in Monitoring
- Render provides basic analytics
- Monitor build times and success rates
- Check error logs in Render dashboard

### Custom Monitoring
- Add error tracking (Sentry, LogRocket, etc.)
- Monitor API response times
- Track user interactions and performance

## Scaling

### Static Site Scaling
- Render automatically handles traffic spikes
- Global CDN provides fast loading worldwide
- No server management required

### When to Upgrade
- Consider paid plans for:
  - Custom domains
  - Advanced analytics
  - Priority support
  - Higher bandwidth limits

## Support

### Render Documentation
- [Static Sites Guide](https://render.com/docs/static-sites)
- [Environment Variables](https://render.com/docs/environment-variables)
- [Custom Domains](https://render.com/docs/custom-domains)

### Common Issues
- Check Render's status page for service issues
- Review build logs for deployment problems
- Test locally before deploying changes

---

## Summary

Your Edurise frontend is now ready for Render deployment! The setup includes:

- ✅ SPA routing configuration (`_redirects` file)
- ✅ Production environment variables (`.env.render`)
- ✅ Render configuration (`render.yaml`)
- ✅ Optimized build process
- ✅ Security best practices

Simply connect your repository to Render and follow the configuration steps above.