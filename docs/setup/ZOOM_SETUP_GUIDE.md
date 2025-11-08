# 🎥 Zoom Integration Setup Guide

## Step 1: Create Zoom Developer Account

1. **Go to Zoom Marketplace**: https://marketplace.zoom.us/
2. **Sign in** with your Zoom account (create one if needed)
3. **Click "Develop"** → **"Build App"**

## Step 2: Create Server-to-Server OAuth App

1. **Choose App Type**: Select **"Server-to-Server OAuth"**
2. **Fill App Information**:
   ```
   App Name: EduRise Platform
   Company Name: [Your Company]
   Developer Email: [Your Email]
   Description: Live class integration for EduRise education platform
   ```

## Step 3: Get Your Credentials

After creating the app, go to the **"App Credentials"** tab:

```bash
# Copy these values to your .env.development file:
ZOOM_API_KEY=your_account_id_here          # Account ID from credentials
ZOOM_API_SECRET=your_client_secret_here    # Client Secret from credentials
```

## Step 4: Configure Scopes

In the **"Scopes"** tab, add these permissions:

### Required Scopes (Essential):
```
✅ meeting:write:meeting:admin - Create meetings
✅ meeting:read:meeting:admin - View meetings  
✅ meeting:update:meeting:admin - Update meetings
✅ meeting:delete:meeting:admin - Delete meetings
✅ meeting:read:participant:admin - View participants
✅ user:read:user:admin - View user information
✅ cloud_recording:read:recording:admin - Access recordings
```

### Recommended Scopes (Enhanced Features):
```
✅ meeting:read:list_meetings:admin - List user meetings
✅ meeting:update:status:admin - Update meeting status
✅ meeting:read:list_past_participants:admin - View past participants
✅ meeting:read:past_meeting:admin - View past meetings
✅ meeting:write:registrant:admin - Add registrants
✅ meeting:read:registrant:admin - View registrants
✅ cloud_recording:read:list_user_recordings:admin - List recordings
✅ cloud_recording:read:list_recording_files:admin - List recording files
```

## Step 5: Set Up Webhooks (Optional - for automatic attendance)

1. **Go to "Feature" tab** in your Zoom app
2. **Add Event Subscriptions**:
   ```
   Endpoint URL: https://yourdomain.com/api/v1/classes/zoom/webhook/
   ```
3. **Subscribe to Events**:
   - ✅ `meeting.participant_joined`
   - ✅ `meeting.participant_left` 
   - ✅ `meeting.started`
   - ✅ `meeting.ended`

4. **Get Webhook Secret** and add to your `.env`:
   ```bash
   ZOOM_WEBHOOK_SECRET=your_webhook_secret_here
   ```

## Step 6: Update Your Environment File

Your `backend/.env.development` should look like this:

```bash
# Zoom API Configuration
ZOOM_API_KEY=your_account_id_from_zoom_app_credentials
ZOOM_API_SECRET=your_client_secret_from_zoom_app_credentials
ZOOM_BASE_URL=https://api.zoom.us/v2

# Optional: For webhook-based attendance tracking
ZOOM_WEBHOOK_SECRET=your_webhook_secret_from_zoom_app
```

## Step 7: Test Your Integration

Run this test to verify your setup:

```bash
cd backend
python manage.py shell
```

```python
from apps.classes.services import ZoomService
from apps.courses.models import LiveClass
from datetime import datetime, timedelta
from django.utils import timezone

# Test Zoom service
zoom_service = ZoomService()
token = zoom_service.get_access_token()
print(f"✅ Zoom token generated: {token[:20]}...")

# Test meeting creation (you'll need a real LiveClass)
# meeting_info = zoom_service.create_meeting(live_class)
# print(f"✅ Meeting created: {meeting_info}")
```

## Step 8: Production Setup

For production, create a separate Zoom app and update your production environment:

```bash
# In your production .env file
ZOOM_API_KEY=your_production_account_id
ZOOM_API_SECRET=your_production_client_secret
ZOOM_WEBHOOK_SECRET=your_production_webhook_secret
```

## Troubleshooting

### Common Issues:

1. **"Invalid API Key"**
   - Make sure you're using the Account ID, not the App Name
   - Check that your app is activated

2. **"Insufficient Privileges"**
   - Verify all required scopes are added
   - Make sure your Zoom account has meeting creation permissions

3. **"Webhook Verification Failed"**
   - Check that your webhook URL is publicly accessible
   - Verify the webhook secret matches

### Testing Endpoints:

```bash
# Test meeting creation
curl -X POST http://localhost:8000/api/v1/live-classes/{id}/create_zoom_meeting/ \
  -H "Authorization: Bearer your_jwt_token"

# Test join info
curl -X GET http://localhost:8000/api/v1/live-classes/{id}/join_info/ \
  -H "Authorization: Bearer your_jwt_token"
```

## Security Notes

- ✅ Never commit real API keys to version control
- ✅ Use different credentials for development/production
- ✅ Regularly rotate your API secrets
- ✅ Monitor API usage in Zoom dashboard

## Support

- **Zoom API Documentation**: https://developers.zoom.us/docs/api/
- **Zoom Marketplace**: https://marketplace.zoom.us/
- **EduRise Integration**: Check `backend/apps/classes/services.py`

---

🎉 **Once configured, your Live Class System will automatically:**
- Create Zoom meetings when teachers create live classes
- Provide secure join links to enrolled students
- Track attendance via webhooks
- Generate comprehensive analytics