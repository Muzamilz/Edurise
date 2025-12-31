# Implementation Plan

This implementation plan breaks down the Zoom to BigBlueButton migration into discrete, manageable coding tasks. Each task builds incrementally on previous tasks, with all code properly integrated.

## Task Overview

- **Phase 1:** Database and Model Updates (Tasks 1-2)
- **Phase 2:** BigBlueButton Service Implementation (Tasks 3-4)
- **Phase 3:** API Endpoints and Views (Tasks 5-7)
- **Phase 4:** Automatic Virtual Class Creation (Task 8)
- **Phase 5:** Student Dashboard (Task 9)
- **Phase 6:** Frontend Updates (Tasks 10-11)
- **Phase 7:** Webhook Integration (Task 12)
- **Phase 8:** Documentation and Configuration (Tasks 13-14)

---

## Phase 1: Database and Model Updates

- [ ] 1. Create database migrations for BBB support
  - Create migration to add new fields: `moderator_password`, `attendee_password`, `provider`
  - Create migration to rename `zoom_meeting_id` to `meeting_id`
  - Add data migration to set `provider='zoom'` for existing records with meeting_id
  - Add database indexes for performance: `(course, scheduled_at)`, `(status, scheduled_at)`
  - _Requirements: 9.1, 9.2, 9.3_

- [ ] 2. Update LiveClass model for provider-agnostic support
  - Add `provider` field with choices: 'zoom', 'bbb'
  - Add `moderator_password` and `attendee_password` fields
  - Rename `zoom_meeting_id` to `meeting_id` in model definition
  - Add `get_join_url_for_user(user)` method that returns appropriate URL based on provider and role
  - Update `__str__` method and Meta class with new indexes
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

## Phase 2: BigBlueButton Service Implementation

- [ ] 3. Implement BigBlueButtonService class
- [ ] 3.1 Create service class structure and initialization
  - Create `apps/classes/services.py::BigBlueButtonService` class
  - Initialize with `BBB_SERVER_URL` and `BBB_SHARED_SECRET` from settings
  - Implement `_generate_checksum(call_name, query_string)` method using HMAC-SHA256
  - Implement `_build_url(endpoint, params)` helper method
  - Implement `_make_api_call(endpoint, params)` with retry logic (3 attempts, exponential backoff)
  - _Requirements: 1.1, 1.5, 13.1, 13.2_

- [ ] 3.2 Implement meeting management methods
  - Implement `create_meeting(live_class)` method that calls BBB create API
  - Generate random moderator and attendee passwords
  - Parse XML response and return meeting info dict
  - Implement `get_meeting_info(meeting_id)` method
  - Implement `is_meeting_running(meeting_id)` method
  - Implement `end_meeting(meeting_id, moderator_password)` method
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 3.3 Implement join URL generation methods
  - Implement `get_moderator_join_url(live_class, moderator_name)` method
  - Implement `get_attendee_join_url(live_class, student_name, student_id)` method
  - Both methods should build join URL with proper checksum
  - Include redirect=true parameter
  - _Requirements: 4.1, 4.2, 4.4, 5.1, 5.2_

- [ ] 3.4 Implement recording management methods
  - Implement `get_recordings(meeting_id)` method
  - Implement `publish_recordings(record_id, publish)` method
  - Implement `delete_recordings(record_id)` method
  - Parse recording XML responses and return structured data
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 3.5 Write unit tests for BigBlueButtonService
  - Test checksum generation matches BBB specification
  - Test meeting creation with mocked API responses
  - Test retry logic on network failures
  - Test join URL generation includes valid checksums
  - Test error handling for invalid responses
  - _Requirements: 14.1, 14.2_

- [ ] 4. Update AttendanceService for BBB webhooks
  - Rename `process_zoom_webhook` to `process_webhook` with provider parameter
  - Add `process_bbb_webhook(webhook_data)` method
  - Handle BBB webhook events: meeting-created, meeting-ended, user-joined, user-left
  - Map BBB user_id to student records for attendance tracking
  - Update attendance records with join/leave times
  - Broadcast WebSocket updates for real-time UI updates
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5_

## Phase 3: API Endpoints and Views

- [ ] 5. Update LiveClassViewSet endpoints
- [ ] 5.1 Update create_meeting action
  - Rename `create_zoom_meeting` action to `create_meeting`
  - Detect provider from live_class.provider field
  - Call BigBlueButtonService.create_meeting() for BBB provider
  - Keep ZoomService.create_meeting() for legacy Zoom support
  - Update live_class with meeting_id, moderator_password, attendee_password
  - Return meeting info with moderator and attendee join URLs
  - _Requirements: 2.1, 2.2, 10.1, 10.2_

- [ ] 5.2 Update join_info action
  - Modify endpoint to be provider-agnostic
  - Check user role (instructor vs student)
  - For BBB: call get_moderator_join_url or get_attendee_join_url based on role
  - For Zoom: return existing join_url
  - Check if meeting is running using is_meeting_running()
  - Return join_url, role, meeting_running, can_start
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3_

- [ ] 5.3 Update start_class and end_class actions
  - Update start_class to work with BBB provider
  - Update status to 'live' and broadcast via WebSocket
  - Update end_class to call BBB end_meeting API
  - Process final attendance for students without leave_time
  - Update status to 'completed'
  - _Requirements: 5.3, 5.4, 5.5, 6.5_

- [ ] 5.4 Add recordings action
  - Create new `recordings` action in LiveClassViewSet
  - Call BigBlueButtonService.get_recordings() for BBB provider
  - Return list of recordings with playback URLs, duration, size
  - Check user permissions (enrolled students and instructor)
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 6. Create BBBWebhookView
  - Create new `BBBWebhookView` class in `apps/classes/views.py`
  - Add POST handler that accepts BBB webhook callbacks
  - Verify webhook checksum for security
  - Parse webhook payload and extract event type
  - Call AttendanceService.process_bbb_webhook() to handle event
  - Return HTTP 200 response
  - Log errors but don't fail webhook processing
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 13.3_

- [ ] 7. Update URL routing
  - Add route for BBBWebhookView: `/api/v1/classes/bbb-webhook/`
  - Update LiveClassViewSet routes to use new action names
  - Keep legacy Zoom routes for backward compatibility during transition
  - _Requirements: 10.1, 10.2, 10.3_

## Phase 4: Automatic Virtual Class Creation

- [ ] 8. Implement automatic virtual class creation on course creation
- [ ] 8.1 Create Django signal handler
  - Create `apps/courses/signals.py` file if it doesn't exist
  - Implement `create_default_virtual_class` signal handler for `post_save` on Course model
  - When course is created, create LiveClass with title "{course.title} - Virtual Class Session 1"
  - Schedule 7 days from creation date, 60 minutes duration
  - Set provider='bbb' and status='scheduled'
  - _Requirements: 2.1, 2.2_

- [ ] 8.2 Auto-create BBB meeting room in signal
  - In signal handler, call BigBlueButtonService.create_meeting()
  - Update live_class with meeting_id, moderator_password, attendee_password
  - Handle errors gracefully (log but don't fail course creation)
  - Send notification to teacher when meeting room is ready
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 13.1_

- [ ] 8.3 Add create_virtual_class action to CourseViewSet
  - Add `create_virtual_class` action to CourseViewSet
  - Accept title, description, scheduled_at, duration_minutes in request
  - Verify user is course instructor
  - Create LiveClass with provider='bbb'
  - Automatically create BBB meeting room
  - Return virtual class details with meeting info
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 8.4 Update Course create endpoint response
  - Modify CourseViewSet.create() to include virtual_classes in response
  - Query course.live_classes.all() after creation
  - Include virtual class details in response data
  - _Requirements: 10.1, 10.2_

- [ ] 8.5 Write integration tests for automatic creation
  - Test course creation automatically creates virtual class
  - Test virtual class has valid meeting_id and passwords
  - Test teacher can create additional virtual classes
  - Test multiple virtual classes can exist for same course
  - _Requirements: 14.3, 14.4_

## Phase 5: Student Dashboard

- [ ] 9. Implement student virtual classes dashboard API
- [ ] 9.1 Create my_virtual_classes endpoint
  - Add `my_virtual_classes` action to StudentDashboardViewSet or create new viewset
  - Query enrolled courses for current user
  - Get all LiveClass records for enrolled courses
  - Filter by status parameter: 'upcoming', 'live', 'completed', 'all'
  - Implement pagination with limit and offset
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 9.2 Add attendance and meeting status to response
  - For each virtual class, query ClassAttendance for current user
  - For live classes, check if meeting is running using is_meeting_running()
  - Calculate time_until_start for upcoming classes
  - Include attendance status and duration for completed classes
  - Categorize classes into upcoming, live, and completed arrays
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 9.3 Add course and instructor details
  - Use select_related to optimize queries
  - Include course title, instructor name, course thumbnail
  - Include virtual class title, description, scheduled_at, duration
  - Include meeting_running, can_join, has_recording flags
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 9.4 Write integration tests for student dashboard
  - Test student sees virtual classes from enrolled courses only
  - Test classes are correctly categorized by status
  - Test attendance information is included for completed classes
  - Test pagination works correctly
  - _Requirements: 14.3, 14.4_

## Phase 6: Frontend Updates

- [ ] 10. Rename and update video conference service
- [ ] 10.1 Rename zoom.ts to videoConference.ts
  - Rename `frontend/src/services/zoom.ts` to `videoConference.ts`
  - Rename class from `ZoomService` to `VideoConferenceService`
  - Update all imports in Vue components
  - _Requirements: 11.1, 11.2_

- [ ] 10.2 Update API endpoint calls
  - Change `create_zoom_meeting` to `create_meeting`
  - Update `getZoomMeetingInfo` to `getJoinInfo`
  - Remove Zoom-specific methods: `updateZoomMeeting`, `deleteZoomMeeting`
  - Keep generic methods: `startClass`, `endClass`, `getAttendance`
  - Add `getRecordings(liveClassId)` method
  - Add `getMyVirtualClasses()` method for student dashboard
  - _Requirements: 10.1, 10.2, 10.3, 11.3, 11.4_

- [ ] 10.3 Update TypeScript type definitions
  - Update `LiveClass` interface to include `provider` field
  - Rename `zoom_meeting_id` to `meeting_id` in types
  - Add `MeetingInfo` interface with moderator_join_url and attendee_join_url
  - Add `JoinInfo` interface with role and meeting_running
  - Update `Recording` interface for BBB recording structure
  - _Requirements: 11.1, 11.2, 11.3_

- [ ] 11. Update Vue components
- [ ] 11.1 Update LiveClassesView component
  - Change button text from "Join Zoom" to "Join Class"
  - Update join flow to use new getJoinInfo() method
  - Handle redirect to BBB URL (open in new tab or iframe)
  - Update meeting status display to be provider-agnostic
  - Update recording playback to use BBB playback URLs
  - _Requirements: 4.5, 5.1, 5.2, 8.4, 8.5_

- [ ] 11.2 Create VirtualClassCard component
  - Create reusable card component for displaying virtual class info
  - Show course title, instructor name, scheduled time
  - Show status badge (scheduled, live, completed)
  - Show "Join Now" button for live classes
  - Show "Watch Recording" button for completed classes with recordings
  - Show attendance badge for completed classes
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 8.4_

- [ ] 11.3 Create StudentDashboard component
  - Create `frontend/src/views/StudentDashboard.vue`
  - Add sections for: Live Now, Upcoming Classes, Past Classes
  - Use VirtualClassCard component for each virtual class
  - Implement joinClass() method that calls getJoinInfo and redirects
  - Implement viewRecording() method for playback
  - Add auto-refresh every 30 seconds for live classes
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 8.4, 8.5_

- [ ] 11.4 Create teacher virtual class management UI
  - Add "Virtual Classes" section to course detail page
  - List all virtual classes for the course
  - Add "+ Create Virtual Class" button
  - Create dialog/modal for creating new virtual class
  - Show meeting status and join URLs for each class
  - Add "Start Class" and "End Class" buttons for instructors
  - _Requirements: 2.1, 2.2, 5.1, 5.2, 5.3, 5.4_

## Phase 7: Webhook Integration

- [ ] 12. Configure and test BBB webhooks
- [ ] 12.1 Set up webhook endpoint on BBB server
  - Configure BBB server to send webhooks to `/api/v1/classes/bbb-webhook/`
  - Set up webhook events: meeting-created, meeting-ended, user-joined, user-left, recording-ready
  - Configure webhook checksum validation
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 12.2 Test webhook event processing
  - Test user-joined event creates attendance record
  - Test user-left event updates attendance with leave time and duration
  - Test meeting-ended event updates live class status to completed
  - Test recording-ready event updates live class with recording URL
  - Verify WebSocket broadcasts work for real-time updates
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 7.4, 7.5, 8.2_

- [ ] 12.3 Write webhook integration tests
  - Test webhook payload parsing and validation
  - Test attendance creation and updates
  - Test error handling for invalid payloads
  - Test checksum verification
  - _Requirements: 14.3, 14.4_

## Phase 8: Documentation and Configuration

- [ ] 13. Update configuration files
- [ ] 13.1 Update environment variable files
  - Add BBB_SERVER_URL and BBB_SHARED_SECRET to `.env.example`
  - Add BBB configuration to `.env.development`
  - Remove or deprecate Zoom environment variables
  - Add BBB feature flags (auto_start_recording, mute_on_start, etc.)
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 13.2 Update Django settings
  - Add BBB configuration to `backend/config/settings.py`
  - Add validation for required BBB settings on startup
  - Add BBB feature flag settings
  - Add ZOOM_SUPPORT_ENABLED flag for transition period
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 13.3 Register signal handlers
  - Import and register signal handlers in `apps/courses/apps.py`
  - Ensure signals are connected on app startup
  - _Requirements: 2.1_

- [ ] 14. Create and update documentation
- [ ] 14.1 Create BBB_SETUP.md guide
  - Document BBB server installation (self-hosted or managed)
  - Document configuration steps for BBB_SERVER_URL and BBB_SHARED_SECRET
  - Document webhook configuration
  - Add troubleshooting section for common issues
  - _Requirements: 15.1, 15.2, 15.3, 15.4_

- [ ] 14.2 Update ZOOM_API_SETUP.md with deprecation notice
  - Add deprecation warning at top of file
  - Link to BBB_SETUP.md for new installations
  - Document migration timeline
  - _Requirements: 15.5_

- [ ] 14.3 Create VIRTUAL_CLASSES_GUIDE.md
  - Document teacher workflow: creating courses and virtual classes
  - Document student workflow: viewing and joining classes
  - Document recording access and playback
  - Add best practices and tips
  - _Requirements: 15.1, 15.2, 15.3_

- [ ] 14.4 Create API_MIGRATION_GUIDE.md
  - Document API endpoint changes
  - List breaking changes and deprecations
  - Provide migration checklist for developers
  - Include code examples for before/after
  - _Requirements: 15.5_

- [ ] 14.5 Update README.md
  - Change "Zoom integration" to "BigBlueButton integration"
  - Update setup instructions to reference BBB_SETUP.md
  - Update features list
  - Update technology stack section
  - _Requirements: 15.1, 15.2_
