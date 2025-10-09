# Zoom API Setup Guide for Edurise LMS

This guide will help you set up Zoom API integration for the live class functionality in Edurise LMS.

## Prerequisites

1. A Zoom account (Pro, Business, Education, or Enterprise)
2. Access to the Zoom Marketplace to create apps

## Step 1: Create a Zoom App

1. Go to the [Zoom Marketplace](https://marketplace.zoom.us/)
2. Sign in with your Zoom account
3. Click "Develop" → "Build App"
4. Choose "Server-to-Server OAuth" app type (recommended for backend integration)
5. Fill in the app information:
   - App Name: `Edurise LMS Integration`
   - Company Name: Your organization name
   - Developer Contact: Your email
   - App Description: `Integration for managing live classes and meetings`

## Step 2: Configure App Permissions

In your Zoom app settings, add the following scopes:

### Required Scopes:
- `meeting:write:admin` - Create and manage meetings
- `meeting:read:admin` - Read meeting information
- `user:read:admin` - Read user information
- `recording:read:admin` - Access meeting recordings
- `webinar:write:admin` - Create and manage webinars (if using webinars)
- `report:read:admin` - Access meeting reports and analytics

### Webhook Events (Optional but Recommended):
- `meeting.started` - When a meeting starts
- `meeting.ended` - When a meeting ends
- `meeting.participant_joined` - When a participant joins
- `meeting.participant_left` - When a participant leaves
- `recording.completed` - When recording is ready

## Step 3: Get Your API Credentials

After creating the app, you'll get:

1. **Account ID** - Your Zoom account identifier
2. **Client ID** - Your app's client ID
3. **Client Secret** - Your app's client secret

## Step 4: Configure Environment Variables

### Backend Configuration (`backend/.env.development`)

```bash
# Zoom API Configuration
ZOOM_ACCOUNT_ID=your-zoom-account-id
ZOOM_CLIENT_ID=your-zoom-client-id
ZOOM_CLIENT_SECRET=your-zoom-client-secret
ZOOM_BASE_URL=https://api.zoom.us/v2
ZOOM_WEBHOOK_SECRET=your-webhook-secret-token
```

### Frontend Configuration (`frontend/.env.development`)

```bash
# Zoom SDK Configuration (for frontend integration)
VITE_ZOOM_SDK_KEY=your-zoom-sdk-key
VITE_ZOOM_SDK_SECRET=your-zoom-sdk-secret
```

## Step 5: Set Up Webhook Endpoint (Optional)

If you want real-time attendance tracking, set up a webhook endpoint:

1. In your Zoom app settings, go to "Event Subscriptions"
2. Add your webhook URL: `https://yourdomain.com/api/v1/classes/zoom-webhook/`
3. Set the webhook secret token in your environment variables
4. Subscribe to the events listed above

## Step 6: Test Your Integration

### Backend Test:
```bash
cd backend
python manage.py shell
```

```python
from apps.classes.services import ZoomService

# Test authentication
zoom_service = ZoomService()
token = zoom_service.get_access_token()
print(f"Access token: {token}")

# Test meeting creation
meeting_data = {
    'topic': 'Test Meeting',
    'type': 2,  # Scheduled meeting
    'start_time': '2024-01-15T10:00:00Z',
    'duration': 60,
    'settings': {
        'host_video': True,
        'participant_video': True,
        'join_before_host': False,
        'mute_upon_entry': True
    }
}

meeting = zoom_service.create_meeting(meeting_data)
print(f"Meeting created: {meeting}")
```

## Step 7: Production Configuration

For production, update your environment variables:

### Backend (`backend/.env.production`)
```bash
ZOOM_ACCOUNT_ID=your-production-zoom-account-id
ZOOM_CLIENT_ID=your-production-zoom-client-id
ZOOM_CLIENT_SECRET=your-production-zoom-client-secret
ZOOM_BASE_URL=https://api.zoom.us/v2
ZOOM_WEBHOOK_SECRET=your-production-webhook-secret
```

### Frontend (`frontend/.env.production`)
```bash
VITE_ZOOM_SDK_KEY=your-production-zoom-sdk-key
VITE_ZOOM_SDK_SECRET=your-production-zoom-sdk-secret
```

## Security Best Practices

1. **Never commit API credentials to version control**
2. **Use different credentials for development and production**
3. **Rotate your webhook secret regularly**
4. **Implement proper error handling and logging**
5. **Use HTTPS for all webhook endpoints**
6. **Validate webhook signatures to ensure authenticity**

## Troubleshooting

### Common Issues:

1. **401 Unauthorized**: Check your credentials and ensure they're correctly set
2. **403 Forbidden**: Verify your app has the required scopes
3. **Webhook not receiving events**: Check your endpoint URL and webhook secret
4. **Rate limiting**: Implement proper retry logic with exponential backoff

### Debug Mode:
Set `LOG_LEVEL=DEBUG` in your backend environment to see detailed API requests and responses.

## API Rate Limits

Zoom API has the following rate limits:
- **Light**: 10 requests per second
- **Medium**: 5 requests per second  
- **Heavy**: 1 request per second

Plan your API usage accordingly and implement proper rate limiting in your application.

## Support

- [Zoom API Documentation](https://developers.zoom.us/docs/api/)
- [Zoom SDK Documentation](https://developers.zoom.us/docs/sdk/)
- [Zoom Developer Forum](https://devforum.zoom.us/)

## Next Steps

After setting up the Zoom API:

1. Implement the `ZoomService` class in `backend/apps/classes/services.py`
2. Create the webhook handler in `backend/apps/classes/views.py`
3. Build the frontend components for live class management
4. Test the complete integration with real meetings
5. Set up monitoring and logging for production use