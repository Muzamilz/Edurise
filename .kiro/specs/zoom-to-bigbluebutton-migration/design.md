# Design Document: Zoom to BigBlueButton Migration

## Overview

This document outlines the technical design for migrating the Edurise LMS platform from Zoom video conferencing to BigBlueButton (BBB), an open-source web conferencing system. The migration will replace all Zoom-dependent functionality while maintaining backward compatibility during the transition period and preserving all existing data.

### Migration Goals

1. Replace Zoom API integration with BigBlueButton API
2. Maintain feature parity for live classes, attendance tracking, and recordings
3. Preserve all historical data and analytics
4. Minimize disruption to existing users
5. Improve cost efficiency by using open-source solution
6. Enable self-hosted video conferencing capabilities

### Key Differences: Zoom vs BigBlueButton

| Feature | Zoom | BigBlueButton |
|---------|------|---------------|
| Authentication | OAuth 2.0 Server-to-Server | Checksum-based (HMAC-SHA256) |
| Meeting Creation | REST API with JWT/OAuth | REST API with checksum |
| Join URLs | Single URL with role parameter | Separate moderator/attendee URLs |
| Webhooks | Event subscriptions | Callback URLs with checksums |
| Recording | Cloud-based automatic | Server-based with playback URLs |
| Password | Optional meeting password | Separate moderator/attendee passwords |
| Hosting | SaaS (Zoom-hosted) | Self-hosted or managed hosting |

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Vue.js)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  videoConference.ts (renamed from zoom.ts)           │   │
│  │  - createMeeting()                                   │   │
│  │  - getMeetingInfo()                                  │   │
│  │  - joinMeeting()                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (Django)                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LiveClassViewSet                                    │   │
│  │  - create_meeting()                                  │   │
│  │  - join_info()                                       │   │
│  │  - start_class() / end_class()                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  BigBlueButtonService (replaces ZoomService)         │   │
│  │  - create_meeting()                                  │   │
│  │  - get_join_url()                                    │   │
│  │  - get_moderator_url()                               │   │
│  │  - end_meeting()                                     │   │
│  │  - get_recordings()                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  BBBWebhookView (replaces ZoomWebhookView)          │   │
│  │  - handle_meeting_events()                           │   │
│  │  - process_attendance()                              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ BBB API (HTTP + Checksum)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              BigBlueButton Server                            │
│  - Meeting Management                                        │
│  - Recording Processing                                      │
│  - Webhook Callbacks                                         │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

#### Meeting Creation Flow
```
Teacher → Frontend → Backend API → BigBlueButtonService → BBB Server
                                         ↓
                                   LiveClass Model
                                   (store meeting_id,
                                    moderator_pw,
                                    attendee_pw)
```

#### Student Join Flow
```
Student → Frontend → Backend API → BigBlueButtonService
                                         ↓
                                   Generate join URL
                                   with checksum
                                         ↓
                                   Redirect to BBB
```



#### Attendance Tracking Flow
```
BBB Server → Webhook → Backend → AttendanceService → ClassAttendance Model
                                       ↓
                                 WebSocket Broadcast
                                       ↓
                                 Frontend Updates
```

## Components and Interfaces

### Backend Components

#### 1. BigBlueButtonService (apps/classes/services.py)

Replaces the existing `ZoomService` class with BBB-specific implementation.

**Key Methods:**

```python
class BigBlueButtonService:
    """Service for BigBlueButton API integration"""
    
    def __init__(self):
        self.server_url = settings.BBB_SERVER_URL
        self.shared_secret = settings.BBB_SHARED_SECRET
        self.base_url = f"{self.server_url}/bigbluebutton/api"
    
    def _generate_checksum(self, call_name: str, query_string: str) -> str:
        """Generate HMAC-SHA256 checksum for BBB API calls"""
        # Implementation: SHA256(call_name + query_string + shared_secret)
        pass
    
    def create_meeting(self, live_class: LiveClass) -> dict:
        """
        Create a BBB meeting room for a live class
        
        Args:
            live_class: LiveClass instance
            
        Returns:
            dict: Meeting info including meeting_id, moderator_pw, attendee_pw
            
        BBB API Call: create
        Parameters:
            - name: live_class.title
            - meetingID: str(live_class.id)
            - attendeePW: generated password
            - moderatorPW: generated password
            - welcome: live_class.description
            - record: true/false based on settings
            - autoStartRecording: true
            - allowStartStopRecording: true
            - logoutURL: LMS redirect URL
        """
        pass
    
    def get_moderator_join_url(self, live_class: LiveClass, 
                               moderator_name: str) -> str:
        """
        Generate join URL for teacher/moderator
        
        BBB API Call: join
        Parameters:
            - fullName: moderator_name
            - meetingID: live_class.meeting_id
            - password: live_class.moderator_password
            - redirect: true
        """
        pass
    
    def get_attendee_join_url(self, live_class: LiveClass, 
                              student_name: str, 
                              student_id: str) -> str:
        """
        Generate join URL for student/attendee
        
        BBB API Call: join
        Parameters:
            - fullName: student_name
            - meetingID: live_class.meeting_id
            - password: live_class.attendee_password
            - userID: student_id (for attendance tracking)
            - redirect: true
        """
        pass
    
    def is_meeting_running(self, meeting_id: str) -> bool:
        """
        Check if meeting is currently active
        
        BBB API Call: isMeetingRunning
        """
        pass
    
    def get_meeting_info(self, meeting_id: str) -> dict:
        """
        Get detailed meeting information including participants
        
        BBB API Call: getMeetingInfo
        Returns: participant list, start time, attendee count, etc.
        """
        pass
    
    def end_meeting(self, meeting_id: str, moderator_password: str) -> bool:
        """
        End a meeting (moderator only)
        
        BBB API Call: end
        """
        pass
    
    def get_recordings(self, meeting_id: str) -> list:
        """
        Get recordings for a meeting
        
        BBB API Call: getRecordings
        Returns: list of recording URLs and metadata
        """
        pass
    
    def delete_recordings(self, record_id: str) -> bool:
        """
        Delete a recording
        
        BBB API Call: deleteRecordings
        """
        pass
    
    def publish_recordings(self, record_id: str, publish: bool) -> bool:
        """
        Publish or unpublish recordings
        
        BBB API Call: publishRecordings
        """
        pass
```

**Error Handling:**

- Network timeouts: Retry up to 3 times with exponential backoff
- Invalid checksums: Log error and raise ValidationError
- Meeting not found: Return None or raise appropriate exception
- Server unavailable: Log error and display user-friendly message

#### 2. AttendanceService Updates (apps/classes/services.py)

Update the existing `AttendanceService` to work with BBB webhooks.

**Modified Methods:**

```python
class AttendanceService:
    
    @staticmethod
    def process_bbb_webhook(webhook_data: dict):
        """
        Process BBB webhook events for attendance tracking
        
        BBB Webhook Events:
        - meeting-created
        - meeting-ended
        - user-joined
        - user-left
        - recording-ready
        
        Each event includes:
        - meeting_id
        - external_meeting_id (our LiveClass.id)
        - user_id (student ID)
        - timestamp
        """
        pass
```

#### 3. LiveClass Model Updates (apps/courses/models.py)

Update the model to be provider-agnostic and support BBB.

**Schema Changes:**

```python
class LiveClass(models.Model):
    # ... existing fields ...
    
    # RENAMED FIELDS (migration required)
    meeting_id = models.CharField(max_length=100, blank=True)  # was: zoom_meeting_id
    
    # NEW FIELDS for BBB
    moderator_password = models.CharField(max_length=100, blank=True)
    attendee_password = models.CharField(max_length=100, blank=True)
    
    # UPDATED FIELDS
    # join_url - now stores BBB base join URL (without checksum)
    # start_url - deprecated, will use moderator join URL instead
    # password - deprecated, split into moderator_password and attendee_password
    
    # NEW FIELD for provider flexibility
    provider = models.CharField(
        max_length=20, 
        choices=[('zoom', 'Zoom'), ('bbb', 'BigBlueButton')],
        default='bbb'
    )
```

**Migration Strategy:**

1. Add new fields with blank=True
2. Rename zoom_meeting_id to meeting_id
3. Set provider='zoom' for existing records
4. New records default to provider='bbb'


#### 4. API Endpoints Updates

**LiveClassViewSet (apps/courses/views.py)**

Update existing endpoints to work with BBB:

```python
class LiveClassViewSet(StandardViewSetMixin, viewsets.ModelViewSet):
    
    @action(detail=True, methods=['post'])
    def create_meeting(self, request, pk=None):
        """
        Create BBB meeting for live class
        
        Endpoint: POST /api/v1/courses/live-classes/{id}/create_meeting/
        
        Response:
        {
            "meeting_id": "uuid",
            "moderator_join_url": "https://bbb.example.com/...",
            "attendee_join_url": "https://bbb.example.com/...",
            "created": true
        }
        """
        pass
    
    @action(detail=True, methods=['get'])
    def join_info(self, request, pk=None):
        """
        Get join information for current user
        
        Endpoint: GET /api/v1/courses/live-classes/{id}/join_info/
        
        Returns appropriate join URL based on user role:
        - Teacher/Instructor: moderator join URL
        - Student: attendee join URL
        
        Response:
        {
            "join_url": "https://bbb.example.com/...",
            "role": "moderator" | "attendee",
            "meeting_running": true/false,
            "can_start": true/false
        }
        """
        pass
    
    @action(detail=True, methods=['post'])
    def start_class(self, request, pk=None):
        """
        Start a live class (teacher only)
        
        Endpoint: POST /api/v1/courses/live-classes/{id}/start_class/
        
        - Updates status to 'live'
        - Returns moderator join URL
        - Broadcasts status update via WebSocket
        """
        pass
    
    @action(detail=True, methods=['post'])
    def end_class(self, request, pk=None):
        """
        End a live class (teacher only)
        
        Endpoint: POST /api/v1/courses/live-classes/{id}/end_class/
        
        - Calls BBB end meeting API
        - Updates status to 'completed'
        - Processes final attendance
        - Broadcasts status update via WebSocket
        """
        pass
    
    @action(detail=True, methods=['get'])
    def recordings(self, request, pk=None):
        """
        Get recordings for a live class
        
        Endpoint: GET /api/v1/courses/live-classes/{id}/recordings/
        
        Response:
        {
            "recordings": [
                {
                    "record_id": "...",
                    "playback_url": "...",
                    "duration": 3600,
                    "size_mb": 250,
                    "published": true
                }
            ]
        }
        """
        pass
```

**New BBBWebhookView (apps/classes/views.py)**

```python
@method_decorator(csrf_exempt, name='dispatch')
class BBBWebhookView(APIView):
    """Handle BigBlueButton webhook callbacks"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Process BBB webhook events
        
        Endpoint: POST /api/v1/classes/bbb-webhook/
        
        BBB sends callbacks for:
        - meeting-created
        - meeting-ended
        - user-joined
        - user-left
        - recording-ready
        
        Webhook payload includes checksum for verification
        """
        # Verify checksum
        # Process event
        # Update attendance
        # Broadcast via WebSocket
        pass
```

### Frontend Components

#### 1. Video Conference Service (frontend/src/services/videoConference.ts)

Rename and update `zoom.ts` to be provider-agnostic.

**Key Changes:**

```typescript
class VideoConferenceService {
  // Update API endpoints
  async createMeeting(liveClassId: string): Promise<MeetingInfo> {
    // Changed from: /create_zoom_meeting/
    // Changed to: /create_meeting/
    const response = await api.post(
      `/api/v1/courses/live-classes/${liveClassId}/create_meeting/`
    )
    return response.data.data
  }

  async getJoinInfo(liveClassId: string): Promise<JoinInfo> {
    // Changed from: /join_info/ (Zoom-specific)
    // Changed to: /join_info/ (provider-agnostic)
    const response = await api.get(
      `/api/v1/courses/live-classes/${liveClassId}/join_info/`
    )
    return response.data.data
  }

  async getRecordings(liveClassId: string): Promise<Recording[]> {
    const response = await api.get(
      `/api/v1/courses/live-classes/${liveClassId}/recordings/`
    )
    return response.data.data
  }

  // Remove Zoom-specific methods:
  // - updateZoomMeeting()
  // - deleteZoomMeeting()
  
  // Keep generic methods:
  // - startClass()
  // - endClass()
  // - getAttendance()
  // - etc.
}

export const videoConferenceService = new VideoConferenceService()
```

#### 2. Type Definitions Update (frontend/src/types/api.ts)

Update types to be provider-agnostic:

```typescript
export interface LiveClass {
  id: string
  course: string
  title: string
  description?: string
  scheduled_at: string
  duration_minutes: number
  status: 'scheduled' | 'live' | 'completed' | 'cancelled'
  
  // Provider-agnostic fields
  meeting_id?: string
  provider: 'zoom' | 'bbb'
  has_recording: boolean
  
  // Deprecated Zoom-specific fields (keep for backward compatibility)
  zoom_meeting_id?: string
  join_url?: string
  start_url?: string
}

export interface MeetingInfo {
  meeting_id: string
  moderator_join_url?: string  // For teachers
  attendee_join_url?: string   // For students
  meeting_running: boolean
  can_start: boolean
}

export interface JoinInfo {
  join_url: string
  role: 'moderator' | 'attendee'
  meeting_running: boolean
  can_start: boolean
}

export interface Recording {
  record_id: string
  playback_url: string
  duration_seconds: number
  size_mb: number
  published: boolean
  recorded_at: string
}
```

#### 3. UI Component Updates

**LiveClassesView.vue** - Minimal changes needed:

- Update button text from "Join Zoom" to "Join Class"
- Handle new join flow (redirect to BBB URL)
- Display provider-agnostic meeting status
- Update recording playback to use BBB playback URLs

**Teacher Dashboard** - Support for multiple live classes per course:

```vue
<template>
  <div class="course-live-classes">
    <h3>Virtual Classes for {{ course.title }}</h3>
    
    <!-- List existing live classes -->
    <div v-for="liveClass in liveClasses" :key="liveClass.id">
      <LiveClassCard :liveClass="liveClass" />
    </div>
    
    <!-- Create new live class button -->
    <button @click="showCreateDialog = true">
      + Create New Virtual Class
    </button>
    
    <!-- Create dialog -->
    <CreateLiveClassDialog
      v-if="showCreateDialog"
      :course="course"
      @created="onLiveClassCreated"
      @close="showCreateDialog = false"
    />
  </div>
</template>
```

**Workflow for Teachers:**

1. Teacher creates a course
2. Teacher can create multiple live classes (virtual sessions) for that course:
   - "Week 1: Introduction to Python"
   - "Week 2: Data Structures"
   - "Week 3: Algorithms"
3. Each live class has its own:
   - Schedule date/time
   - Duration
   - BBB meeting room
   - Attendance tracking
   - Recording

## Data Models

### Database Schema Changes

#### Migration 1: Add BBB Fields

```python
# Migration: 0001_add_bbb_fields.py

class Migration(migrations.Migration):
    dependencies = [
        ('courses', 'previous_migration'),
    ]

    operations = [
        # Add new fields
        migrations.AddField(
            model_name='liveclass',
            name='moderator_password',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='liveclass',
            name='attendee_password',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='liveclass',
            name='provider',
            field=models.CharField(
                max_length=20,
                choices=[('zoom', 'Zoom'), ('bbb', 'BigBlueButton')],
                default='bbb'
            ),
        ),
    ]
```

#### Migration 2: Rename Zoom Fields

```python
# Migration: 0002_rename_zoom_fields.py

class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0001_add_bbb_fields'),
    ]

    operations = [
        # Rename zoom_meeting_id to meeting_id
        migrations.RenameField(
            model_name='liveclass',
            old_name='zoom_meeting_id',
            new_name='meeting_id',
        ),
        
        # Set provider='zoom' for existing records
        migrations.RunPython(set_existing_provider_to_zoom),
    ]

def set_existing_provider_to_zoom(apps, schema_editor):
    LiveClass = apps.get_model('courses', 'LiveClass')
    LiveClass.objects.filter(meeting_id__isnull=False).update(provider='zoom')
```

### Updated LiveClass Model

```python
class LiveClass(models.Model):
    """Live class sessions for courses - supports multiple providers"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PROVIDER_CHOICES = [
        ('zoom', 'Zoom'),
        ('bbb', 'BigBlueButton'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='live_classes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Scheduling
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Provider
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='bbb')
    
    # Meeting integration (provider-agnostic)
    meeting_id = models.CharField(max_length=100, blank=True)  # Renamed from zoom_meeting_id
    join_url = models.URLField(blank=True)  # Base URL without checksum
    
    # BBB-specific fields
    moderator_password = models.CharField(max_length=100, blank=True)
    attendee_password = models.CharField(max_length=100, blank=True)
    
    # Legacy Zoom fields (deprecated but kept for backward compatibility)
    start_url = models.URLField(blank=True)  # Deprecated: use moderator join URL
    password = models.CharField(max_length=50, blank=True)  # Deprecated: use moderator/attendee passwords
    
    # Recording
    recording_url = models.URLField(blank=True)
    recording_password = models.CharField(max_length=50, blank=True)
    has_recording = models.BooleanField(default=False)
    recording_processed = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'live_classes'
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['course', 'scheduled_at']),
            models.Index(fields=['status', 'scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def get_join_url_for_user(self, user):
        """Get appropriate join URL based on user role"""
        if self.provider == 'bbb':
            from apps.classes.services import BigBlueButtonService
            bbb_service = BigBlueButtonService()
            
            if self.course.instructor == user or user.is_staff:
                return bbb_service.get_moderator_join_url(self, user.get_full_name())
            else:
                return bbb_service.get_attendee_join_url(
                    self, 
                    user.get_full_name(), 
                    str(user.id)
                )
        elif self.provider == 'zoom':
            # Legacy Zoom support
            return self.join_url
        
        return None
```


## Error Handling

### Backend Error Scenarios

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| BBB server unreachable | Retry 3 times with exponential backoff (1s, 2s, 4s), then return user-friendly error |
| Invalid checksum | Log error details, raise ValidationError with message |
| Meeting creation fails | Log full error, return specific error message to user |
| Meeting not found | Return 404 with clear message |
| Webhook verification fails | Log security warning, return 403 |
| Database connection error | Use Django's built-in retry mechanism, log error |
| Concurrent meeting updates | Use database transactions with row-level locking |

### Frontend Error Scenarios

| Error Scenario | User Experience |
|----------------|-----
## A
utomatic Virtual Class Creation

### Course Creation Workflow

When a teacher creates a course, the system will automatically create an initial virtual class (live session) for that course.

#### Implementation Strategy

**1. Django Signal Handler**

```python
# apps/courses/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Course, LiveClass
from apps.classes.services import BigBlueButtonService

@receiver(post_save, sender=Course)
def create_default_virtual_class(sender, instance, created, **kwargs):
    """
    Automatically create a default virtual class when a course is created
    """
    if created:
        # Create initial virtual class scheduled 7 days from now
        default_schedule = timezone.now() + timedelta(days=7)
        
        live_class = LiveClass.objects.create(
            course=instance,
            title=f"{instance.title} - Virtual Class Session 1",
            description=f"First virtual class session for {instance.title}",
            scheduled_at=default_schedule,
            duration_minutes=60,
            status='scheduled',
            provider='bbb'
        )
        
        # Automatically create BBB meeting room
        try:
            bbb_service = BigBlueButtonService()
            meeting_info = bbb_service.create_meeting(live_class)
            
            # Update live class with meeting details
            live_class.meeting_id = meeting_info['meetingID']
            live_class.moderator_password = meeting_info['moderatorPW']
            live_class.attendee_password = meeting_info['attendeePW']
            live_class.save()
            
        except Exception as e:
            # Log error but don't fail course creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create BBB meeting for course {instance.id}: {str(e)}")
```

**2. Course Creation API Enhancement**

```python
# apps/courses/views.py

class CourseViewSet(StandardViewSetMixin, viewsets.ModelViewSet):
    
    def create(self, request, *args, **kwargs):
        """
        Create a new course with automatic virtual class creation
        
        POST /api/v1/courses/
        
        Request body can optionally include:
        {
            "title": "Python Programming",
            "description": "...",
            "auto_create_virtual_class": true,  // default: true
            "virtual_class_schedule": "2024-01-15T10:00:00Z",  // optional
            "virtual_class_duration": 90  // optional, default: 60
        }
        """
        # Create course (signal will handle virtual class creation)
        response = super().create(request, *args, **kwargs)
        
        # Include virtual class info in response
        if response.status_code == 201:
            course = Course.objects.get(id=response.data['data']['id'])
            virtual_classes = course.live_classes.all()
            
            response.data['data']['virtual_classes'] = [
                {
                    'id': str(vc.id),
                    'title': vc.title,
                    'scheduled_at': vc.scheduled_at,
                    'meeting_id': vc.meeting_id,
                    'status': vc.status
                }
                for vc in virtual_classes
            ]
        
        return response
    
    @action(detail=True, methods=['post'])
    def create_virtual_class(self, request, pk=None):
        """
        Create additional virtual classes for a course
        
        POST /api/v1/courses/{id}/create_virtual_class/
        
        Teachers can create 2-3 (or more) virtual classes per course
        
        Request:
        {
            "title": "Week 2: Advanced Topics",
            "description": "Second session covering advanced concepts",
            "scheduled_at": "2024-01-22T10:00:00Z",
            "duration_minutes": 90
        }
        """
        course = self.get_object()
        
        # Check permissions
        if course.instructor != request.user and not request.user.is_staff:
            return self.error_response(
                message='Only the course instructor can create virtual classes',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Create virtual class
        live_class = LiveClass.objects.create(
            course=course,
            title=request.data.get('title'),
            description=request.data.get('description', ''),
            scheduled_at=request.data.get('scheduled_at'),
            duration_minutes=request.data.get('duration_minutes', 60),
            status='scheduled',
            provider='bbb'
        )
        
        # Create BBB meeting room
        try:
            bbb_service = BigBlueButtonService()
            meeting_info = bbb_service.create_meeting(live_class)
            
            live_class.meeting_id = meeting_info['meetingID']
            live_class.moderator_password = meeting_info['moderatorPW']
            live_class.attendee_password = meeting_info['attendeePW']
            live_class.save()
            
            return self.success_response(
                data={
                    'id': str(live_class.id),
                    'title': live_class.title,
                    'scheduled_at': live_class.scheduled_at,
                    'duration_minutes': live_class.duration_minutes,
                    'meeting_id': live_class.meeting_id,
                    'status': live_class.status,
                    'meeting_created': True
                },
                message='Virtual class created successfully'
            )
            
        except Exception as e:
            # Rollback live class creation if BBB meeting fails
            live_class.delete()
            return self.error_response(
                message=f'Failed to create virtual class: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

### Teacher Workflow

1. **Create Course**
   - Teacher fills out course form (title, description, etc.)
   - Clicks "Create Course"
   - System automatically creates:
     - Course record
     - First virtual class (scheduled 7 days ahead)
     - BBB meeting room with join URLs

2. **Add More Virtual Classes**
   - Teacher navigates to course detail page
   - Sees "Virtual Classes" section with the auto-created class
   - Clicks "+ Add Virtual Class" button
   - Fills out form:
     - Title: "Week 2: Data Structures"
     - Date/Time: Select from calendar
     - Duration: 60/90/120 minutes
   - System creates BBB meeting room automatically
   - Can create multiple classes (2, 3, or more)

3. **Manage Virtual Classes**
   - View all virtual classes for the course
   - Edit schedule/details
   - Start class (get moderator join URL)
   - End class
   - View attendance and recordings

## Student Dashboard

### Student Virtual Classes View

Students should see all upcoming and past virtual classes from their enrolled courses on their dashboard.

#### API Endpoint

```python
# apps/courses/views.py or apps/api/dashboard_views.py

class StudentDashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_virtual_classes(self, request):
        """
        Get all virtual classes for student's enrolled courses
        
        GET /api/v1/dashboard/my-virtual-classes/
        
        Query params:
        - status: 'upcoming' | 'live' | 'completed' | 'all' (default: 'upcoming')
        - limit: number of results (default: 20)
        - offset: pagination offset
        
        Response:
        {
            "upcoming": [
                {
                    "id": "uuid",
                    "title": "Python Basics - Week 1",
                    "course": {
                        "id": "uuid",
                        "title": "Python Programming",
                        "instructor_name": "John Doe"
                    },
                    "scheduled_at": "2024-01-15T10:00:00Z",
                    "duration_minutes": 60,
                    "status": "scheduled",
                    "can_join": false,
                    "meeting_running": false,
                    "time_until_start": "2 days"
                }
            ],
            "live": [
                {
                    "id": "uuid",
                    "title": "Data Structures - Week 2",
                    "course": {...},
                    "scheduled_at": "2024-01-13T10:00:00Z",
                    "status": "live",
                    "can_join": true,
                    "meeting_running": true,
                    "join_url": "https://bbb.example.com/..."
                }
            ],
            "completed": [
                {
                    "id": "uuid",
                    "title": "Introduction - Week 1",
                    "course": {...},
                    "scheduled_at": "2024-01-08T10:00:00Z",
                    "status": "completed",
                    "has_recording": true,
                    "attendance_status": "present",
                    "duration_attended": 55
                }
            ]
        }
        """
        from apps.courses.models import Enrollment, LiveClass
        from django.db.models import Q, Prefetch
        
        # Get student's enrolled courses
        enrolled_courses = Enrollment.objects.filter(
            student=request.user,
            status='active'
        ).values_list('course_id', flat=True)
        
        # Get virtual classes from enrolled courses
        status_filter = request.query_params.get('status', 'upcoming')
        
        base_query = LiveClass.objects.filter(
            course_id__in=enrolled_courses
        ).select_related('course', 'course__instructor')
        
        if status_filter == 'upcoming':
            virtual_classes = base_query.filter(
                Q(status='scheduled') | Q(status='live'),
                scheduled_at__gte=timezone.now()
            ).order_by('scheduled_at')
        elif status_filter == 'live':
            virtual_classes = base_query.filter(
                status='live'
            ).order_by('scheduled_at')
        elif status_filter == 'completed':
            virtual_classes = base_query.filter(
                status='completed'
            ).order_by('-scheduled_at')
        else:  # all
            virtual_classes = base_query.order_by('-scheduled_at')
        
        # Pagination
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))
        virtual_classes = virtual_classes[offset:offset + limit]
        
        # Build response with attendance info
        from apps.classes.models import ClassAttendance
        
        result = {
            'upcoming': [],
            'live': [],
            'completed': []
        }
        
        for vc in virtual_classes:
            # Get attendance record if exists
            attendance = ClassAttendance.objects.filter(
                live_class=vc,
                student=request.user
            ).first()
            
            # Check if meeting is running (for live classes)
            meeting_running = False
            if vc.status == 'live' and vc.provider == 'bbb':
                bbb_service = BigBlueButtonService()
                meeting_running = bbb_service.is_meeting_running(vc.meeting_id)
            
            # Calculate time until start
            time_until_start = None
            if vc.scheduled_at > timezone.now():
                delta = vc.scheduled_at - timezone.now()
                if delta.days > 0:
                    time_until_start = f"{delta.days} days"
                elif delta.seconds > 3600:
                    time_until_start = f"{delta.seconds // 3600} hours"
                else:
                    time_until_start = f"{delta.seconds // 60} minutes"
            
            class_data = {
                'id': str(vc.id),
                'title': vc.title,
                'description': vc.description,
                'course': {
                    'id': str(vc.course.id),
                    'title': vc.course.title,
                    'instructor_name': vc.course.instructor.get_full_name(),
                    'thumbnail': vc.course.thumbnail_url if hasattr(vc.course, 'thumbnail_url') else None
                },
                'scheduled_at': vc.scheduled_at,
                'duration_minutes': vc.duration_minutes,
                'status': vc.status,
                'provider': vc.provider,
                'meeting_running': meeting_running,
                'can_join': meeting_running or vc.status == 'live',
                'time_until_start': time_until_start,
                'has_recording': vc.has_recording
            }
            
            # Add attendance info for completed classes
            if attendance and vc.status == 'completed':
                class_data['attendance'] = {
                    'status': attendance.status,
                    'duration_attended': attendance.duration_minutes,
                    'participation_score': attendance.participation_score,
                    'attendance_percentage': attendance.attendance_percentage
                }
            
            # Categorize by status
            if vc.status in ['scheduled'] and vc.scheduled_at >= timezone.now():
                result['upcoming'].append(class_data)
            elif vc.status == 'live':
                result['live'].append(class_data)
            elif vc.status == 'completed':
                result['completed'].append(class_data)
        
        return Response({
            'success': True,
            'data': result,
            'message': 'Virtual classes retrieved successfully'
        })
```

### Frontend Student Dashboard Component

```vue
<!-- frontend/src/views/StudentDashboard.vue -->

<template>
  <div class="student-dashboard">
    <h1>My Virtual Classes</h1>
    
    <!-- Live Classes (Currently Happening) -->
    <section v-if="liveClasses.length > 0" class="live-classes">
      <h2>🔴 Live Now</h2>
      <div class="class-grid">
        <VirtualClassCard
          v-for="vc in liveClasses"
          :key="vc.id"
          :virtualClass="vc"
          :highlight="true"
        >
          <template #actions>
            <button 
              class="btn-primary btn-join-live"
              @click="joinClass(vc)"
            >
              Join Now
            </button>
          </template>
        </VirtualClassCard>
      </div>
    </section>
    
    <!-- Upcoming Classes -->
    <section class="upcoming-classes">
      <h2>📅 Upcoming Classes</h2>
      <div v-if="upcomingClasses.length === 0" class="empty-state">
        <p>No upcoming virtual classes scheduled</p>
      </div>
      <div v-else class="class-list">
        <VirtualClassCard
          v-for="vc in upcomingClasses"
          :key="vc.id"
          :virtualClass="vc"
        >
          <template #actions>
            <button 
              class="btn-secondary"
              @click="addToCalendar(vc)"
            >
              Add to Calendar
            </button>
            <span class="time-until">
              Starts in {{ vc.time_until_start }}
            </span>
          </template>
        </VirtualClassCard>
      </div>
    </section>
    
    <!-- Past Classes with Recordings -->
    <section class="completed-classes">
      <h2>📼 Past Classes</h2>
      <div class="class-list">
        <VirtualClassCard
          v-for="vc in completedClasses"
          :key="vc.id"
          :virtualClass="vc"
        >
          <template #actions>
            <button 
              v-if="vc.has_recording"
              class="btn-secondary"
              @click="viewRecording(vc)"
            >
              Watch Recording
            </button>
            <div v-if="vc.attendance" class="attendance-badge">
              <span :class="`status-${vc.attendance.status}`">
                {{ vc.attendance.status }}
              </span>
              <span class="duration">
                {{ vc.attendance.duration_attended }} min
              </span>
            </div>
          </template>
        </VirtualClassCard>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { videoConferenceService } from '@/services/videoConference'
import VirtualClassCard from '@/components/VirtualClassCard.vue'

const liveClasses = ref([])
const upcomingClasses = ref([])
const completedClasses = ref([])

onMounted(async () => {
  await loadVirtualClasses()
  
  // Refresh live classes every 30 seconds
  setInterval(loadVirtualClasses, 30000)
})

async function loadVirtualClasses() {
  try {
    const response = await videoConferenceService.getMyVirtualClasses()
    liveClasses.value = response.live
    upcomingClasses.value = response.upcoming
    completedClasses.value = response.completed
  } catch (error) {
    console.error('Failed to load virtual classes:', error)
  }
}

function joinClass(virtualClass) {
  // Get join URL and redirect
  videoConferenceService.getJoinInfo(virtualClass.id)
    .then(joinInfo => {
      window.open(joinInfo.join_url, '_blank')
    })
}

function viewRecording(virtualClass) {
  // Navigate to recording view
  router.push(`/classes/${virtualClass.id}/recording`)
}

function addToCalendar(virtualClass) {
  // Generate calendar event
  // Implementation for .ics file download
}
</script>
```


## Error Handling

### BBB Server Connection Errors

**Scenario:** BBB server is unreachable or returns errors

**Handling:**
1. Retry mechanism with exponential backoff (3 attempts)
2. Log detailed error information
3. Display user-friendly error message
4. Allow manual retry by user
5. Send notification to system administrators

```python
class BigBlueButtonService:
    
    def _make_api_call(self, endpoint, params, max_retries=3):
        """Make API call with retry logic"""
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    f"{self.base_url}/{endpoint}",
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    return self._parse_xml_response(response.content)
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise BBBConnectionError("BBB server timeout")
            
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise BBBConnectionError("Cannot connect to BBB server")
        
        raise BBBAPIError(f"API call failed after {max_retries} attempts")
```

### Meeting Creation Failures

**Scenario:** BBB meeting creation fails during course creation

**Handling:**
1. Course creation succeeds (don't block course creation)
2. Virtual class is created but marked as "pending"
3. Background task retries meeting creation
4. Teacher receives notification when meeting is ready
5. Teacher can manually trigger meeting creation

### Webhook Processing Errors

**Scenario:** Webhook payload is invalid or processing fails

**Handling:**
1. Log webhook payload for debugging
2. Return 200 OK to BBB (prevent retries)
3. Queue failed webhooks for manual review
4. Send alert to administrators
5. Implement webhook replay mechanism

### Checksum Validation Failures

**Scenario:** BBB rejects API call due to invalid checksum

**Handling:**
1. Log the call parameters and generated checksum
2. Verify shared secret configuration
3. Check for encoding issues
4. Retry with fresh checksum
5. Alert administrators if persistent

## Testing Strategy

### Unit Tests

**BigBlueButtonService Tests:**
```python
# tests/test_bbb_service.py

class TestBigBlueButtonService(TestCase):
    
    def setUp(self):
        self.service = BigBlueButtonService()
        self.live_class = LiveClassFactory()
    
    def test_generate_checksum(self):
        """Test checksum generation matches BBB spec"""
        call_name = "create"
        query_string = "name=Test&meetingID=123"
        checksum = self.service._generate_checksum(call_name, query_string)
        
        # Verify checksum format and length
        self.assertEqual(len(checksum), 64)  # SHA256 hex length
    
    @mock.patch('requests.get')
    def test_create_meeting_success(self, mock_get):
        """Test successful meeting creation"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'<response><returncode>SUCCESS</returncode>...</response>'
        
        result = self.service.create_meeting(self.live_class)
        
        self.assertIn('meetingID', result)
        self.assertIn('moderatorPW', result)
        self.assertIn('attendeePW', result)
    
    @mock.patch('requests.get')
    def test_create_meeting_retry_on_timeout(self, mock_get):
        """Test retry logic on timeout"""
        mock_get.side_effect = [
            requests.exceptions.Timeout(),
            requests.exceptions.Timeout(),
            mock.Mock(status_code=200, content=b'<response>...</response>')
        ]
        
        result = self.service.create_meeting(self.live_class)
        
        self.assertEqual(mock_get.call_count, 3)
        self.assertIsNotNone(result)
    
    def test_get_join_url_with_checksum(self):
        """Test join URL generation includes valid checksum"""
        self.live_class.meeting_id = "test-meeting-123"
        self.live_class.attendee_password = "attendee-pw"
        
        join_url = self.service.get_attendee_join_url(
            self.live_class,
            "John Doe",
            "user-123"
        )
        
        self.assertIn('checksum=', join_url)
        self.assertIn('meetingID=test-meeting-123', join_url)
        self.assertIn('fullName=John+Doe', join_url)
```

### Integration Tests

**End-to-End Virtual Class Flow:**
```python
# tests/test_virtual_class_integration.py

class TestVirtualClassIntegration(APITestCase):
    
    def setUp(self):
        self.teacher = UserFactory(is_teacher=True)
        self.student = UserFactory(is_student=True)
        self.client.force_authenticate(user=self.teacher)
    
    def test_course_creation_auto_creates_virtual_class(self):
        """Test that creating a course automatically creates a virtual class"""
        response = self.client.post('/api/v1/courses/', {
            'title': 'Python Programming',
            'description': 'Learn Python',
            'category': 'programming'
        })
        
        self.assertEqual(response.status_code, 201)
        
        course_id = response.data['data']['id']
        course = Course.objects.get(id=course_id)
        
        # Verify virtual class was created
        virtual_classes = course.live_classes.all()
        self.assertEqual(virtual_classes.count(), 1)
        
        vc = virtual_classes.first()
        self.assertIsNotNone(vc.meeting_id)
        self.assertIsNotNone(vc.moderator_password)
        self.assertIsNotNone(vc.attendee_password)
    
    def test_teacher_creates_additional_virtual_classes(self):
        """Test teacher can create multiple virtual classes"""
        course = CourseFactory(instructor=self.teacher)
        
        # Create 3 virtual classes
        for i in range(3):
            response = self.client.post(
                f'/api/v1/courses/{course.id}/create_virtual_class/',
                {
                    'title': f'Week {i+1} Session',
                    'scheduled_at': (timezone.now() + timedelta(days=7*(i+1))).isoformat(),
                    'duration_minutes': 60
                }
            )
            self.assertEqual(response.status_code, 200)
        
        # Verify all classes were created
        self.assertEqual(course.live_classes.count(), 4)  # 1 auto + 3 manual
    
    def test_student_sees_enrolled_course_virtual_classes(self):
        """Test student dashboard shows virtual classes from enrolled courses"""
        course = CourseFactory(instructor=self.teacher)
        EnrollmentFactory(student=self.student, course=course, status='active')
        
        # Create virtual classes
        LiveClassFactory(course=course, status='scheduled')
        LiveClassFactory(course=course, status='live')
        LiveClassFactory(course=course, status='completed')
        
        # Switch to student user
        self.client.force_authenticate(user=self.student)
        
        response = self.client.get('/api/v1/dashboard/my-virtual-classes/')
        
        self.assertEqual(response.status_code, 200)
        data = response.data['data']
        
        self.assertEqual(len(data['upcoming']), 1)
        self.assertEqual(len(data['live']), 1)
        self.assertEqual(len(data['completed']), 1)
    
    @mock.patch('apps.classes.services.BigBlueButtonService.is_meeting_running')
    def test_student_joins_live_class(self, mock_is_running):
        """Test student can join a live virtual class"""
        mock_is_running.return_value = True
        
        course = CourseFactory(instructor=self.teacher)
        EnrollmentFactory(student=self.student, course=course, status='active')
        
        live_class = LiveClassFactory(
            course=course,
            status='live',
            meeting_id='test-meeting-123',
            attendee_password='attendee-pw'
        )
        
        # Switch to student user
        self.client.force_authenticate(user=self.student)
        
        response = self.client.get(
            f'/api/v1/courses/live-classes/{live_class.id}/join_info/'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.data['data']
        
        self.assertIn('join_url', data)
        self.assertEqual(data['role'], 'attendee')
        self.assertTrue(data['meeting_running'])
        self.assertTrue(data['can_join'])
```

### Webhook Tests

```python
# tests/test_bbb_webhooks.py

class TestBBBWebhooks(APITestCase):
    
    def test_user_joined_webhook_creates_attendance(self):
        """Test that user-joined webhook creates attendance record"""
        live_class = LiveClassFactory(meeting_id='test-meeting-123')
        student = UserFactory(email='student@example.com')
        
        webhook_payload = {
            'event': 'user-joined',
            'meeting_id': 'test-meeting-123',
            'user_id': str(student.id),
            'user_name': student.get_full_name(),
            'timestamp': timezone.now().isoformat()
        }
        
        response = self.client.post(
            '/api/v1/classes/bbb-webhook/',
            webhook_payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify attendance was created
        attendance = ClassAttendance.objects.get(
            live_class=live_class,
            student=student
        )
        self.assertEqual(attendance.status, 'present')
        self.assertIsNotNone(attendance.join_time)
    
    def test_user_left_webhook_updates_attendance(self):
        """Test that user-left webhook updates attendance duration"""
        live_class = LiveClassFactory(meeting_id='test-meeting-123')
        student = UserFactory(email='student@example.com')
        
        # Create initial attendance
        attendance = ClassAttendanceFactory(
            live_class=live_class,
            student=student,
            join_time=timezone.now() - timedelta(minutes=45)
        )
        
        webhook_payload = {
            'event': 'user-left',
            'meeting_id': 'test-meeting-123',
            'user_id': str(student.id),
            'timestamp': timezone.now().isoformat()
        }
        
        response = self.client.post(
            '/api/v1/classes/bbb-webhook/',
            webhook_payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify attendance was updated
        attendance.refresh_from_db()
        self.assertIsNotNone(attendance.leave_time)
        self.assertGreater(attendance.duration_minutes, 0)
```

## Configuration Management

### Environment Variables

**Backend (.env files):**

```bash
# BigBlueButton Configuration
BBB_SERVER_URL=https://bbb.example.com
BBB_SHARED_SECRET=your-bbb-shared-secret-here

# Optional: BBB Feature Flags
BBB_AUTO_START_RECORDING=true
BBB_ALLOW_START_STOP_RECORDING=true
BBB_WEBCAMS_ONLY_FOR_MODERATOR=false
BBB_MUTE_ON_START=true
BBB_LOCK_SETTINGS_DISABLE_CAM=false
BBB_LOCK_SETTINGS_DISABLE_MIC=false

# Webhook Configuration
BBB_WEBHOOK_URL=https://yourdomain.com/api/v1/classes/bbb-webhook/

# Legacy Zoom (for backward compatibility during transition)
ZOOM_SUPPORT_ENABLED=false  # Set to true during transition period
```

**Frontend (.env files):**

```bash
# No BBB-specific frontend config needed
# BBB is accessed via backend-generated URLs

# Optional: Feature flags
VITE_VIRTUAL_CLASSES_ENABLED=true
VITE_RECORDING_PLAYBACK_ENABLED=true
```

### Settings Configuration

```python
# backend/config/settings.py

# BigBlueButton Configuration
BBB_SERVER_URL = os.getenv('BBB_SERVER_URL', '')
BBB_SHARED_SECRET = os.getenv('BBB_SHARED_SECRET', '')

# Validate BBB configuration on startup
if not BBB_SERVER_URL or not BBB_SHARED_SECRET:
    import warnings
    warnings.warn(
        "BBB_SERVER_URL and BBB_SHARED_SECRET must be configured for virtual classes to work"
    )

# BBB Feature Settings
BBB_AUTO_START_RECORDING = os.getenv('BBB_AUTO_START_RECORDING', 'true').lower() == 'true'
BBB_ALLOW_START_STOP_RECORDING = os.getenv('BBB_ALLOW_START_STOP_RECORDING', 'true').lower() == 'true'
BBB_MUTE_ON_START = os.getenv('BBB_MUTE_ON_START', 'true').lower() == 'true'

# Webhook Configuration
BBB_WEBHOOK_URL = os.getenv('BBB_WEBHOOK_URL', '')

# Transition Period Settings
ZOOM_SUPPORT_ENABLED = os.getenv('ZOOM_SUPPORT_ENABLED', 'false').lower() == 'true'
```

## Documentation Updates

### Files to Create/Update

1. **docs/BBB_SETUP.md** (NEW)
   - BBB server installation guide
   - Configuration instructions
   - Webhook setup
   - Troubleshooting

2. **docs/ZOOM_API_SETUP.md** (UPDATE)
   - Add deprecation notice
   - Link to BBB_SETUP.md
   - Migration timeline

3. **docs/VIRTUAL_CLASSES_GUIDE.md** (NEW)
   - Teacher guide: Creating and managing virtual classes
   - Student guide: Joining classes and viewing recordings
   - Best practices

4. **docs/API_MIGRATION_GUIDE.md** (NEW)
   - API endpoint changes
   - Breaking changes
   - Migration checklist for developers

5. **README.md** (UPDATE)
   - Update "Live Classes" section
   - Change "Zoom integration" to "BigBlueButton integration"
   - Update setup instructions

## Migration Timeline

### Phase 1: Preparation (Week 1-2)
- Set up BBB server (self-hosted or managed)
- Configure BBB credentials
- Run database migrations
- Deploy code with feature flag disabled

### Phase 2: Testing (Week 3)
- Enable BBB for test courses
- Test meeting creation and joining
- Test attendance tracking
- Test recording functionality
- Fix any issues

### Phase 3: Gradual Rollout (Week 4-5)
- Enable BBB for new courses
- Keep Zoom support for existing courses
- Monitor for issues
- Gather user feedback

### Phase 4: Full Migration (Week 6)
- Migrate remaining Zoom courses to BBB
- Disable Zoom integration
- Remove Zoom-specific code
- Update all documentation

### Phase 5: Cleanup (Week 7)
- Remove Zoom environment variables
- Archive Zoom-related code
- Final documentation updates
- Post-migration review

## Success Metrics

- **Technical Metrics:**
  - Meeting creation success rate > 99%
  - Average meeting join time < 5 seconds
  - Webhook processing latency < 2 seconds
  - Zero data loss during migration

- **User Experience Metrics:**
  - Teacher satisfaction with virtual class creation
  - Student satisfaction with joining experience
  - Recording playback quality
  - Attendance tracking accuracy

- **Business Metrics:**
  - Cost savings vs Zoom
  - Number of virtual classes created per course
  - Student attendance rates
  - Recording view rates
