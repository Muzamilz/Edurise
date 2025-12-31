# Requirements Document

## Introduction

This document outlines the requirements for migrating the Edurise LMS platform from Zoom video conferencing integration to BigBlueButton (BBB), an open-source web conferencing system. The migration aims to replace all Zoom-dependent functionality while maintaining or improving the current live class experience, attendance tracking, and analytics capabilities.

## Glossary

- **BBB**: BigBlueButton - The open-source web conferencing system that will replace Zoom
- **LMS**: Learning Management System - The Edurise platform
- **Live Class**: A scheduled virtual classroom session conducted through video conferencing
- **Meeting Room**: A BBB conference room instance where live classes are conducted
- **Join URL**: The web address students use to enter a live class
- **Moderator URL**: The web address teachers use to host and control a live class
- **Attendance Record**: A database entry tracking student participation in a live class
- **Recording**: A saved video file of a completed live class session
- **Webhook**: An HTTP callback that BBB sends to notify the LMS of meeting events
- **API Client**: The backend service component that communicates with BBB servers
- **Frontend Service**: The TypeScript service layer that handles live class operations in the UI

## Requirements

### Requirement 1: BBB Server Integration

**User Story:** As a system administrator, I want the LMS to connect to a BigBlueButton server, so that the platform can create and manage virtual classrooms without depending on Zoom.

#### Acceptance Criteria

1. THE LMS SHALL establish authenticated connections to a configured BBB server using API credentials
2. WHEN the BBB server is unreachable, THE LMS SHALL log connection errors and display user-friendly error messages
3. THE LMS SHALL validate BBB server configuration on application startup
4. THE LMS SHALL support configurable BBB server URL and shared secret through environment variables
5. THE LMS SHALL generate valid BBB API checksums for all API requests using HMAC-SHA256

### Requirement 2: Meeting Room Creation

**User Story:** As a teacher, I want to create live class sessions that generate BBB meeting rooms, so that I can conduct virtual classes with my students.

#### Acceptance Criteria

1. WHEN a teacher creates a live class, THE LMS SHALL create a corresponding BBB meeting room with unique meeting ID
2. THE LMS SHALL store the BBB meeting ID, moderator password, and attendee password in the LiveClass model
3. THE LMS SHALL generate a moderator join URL for teachers with host privileges
4. THE LMS SHALL generate an attendee join URL for students with participant privileges
5. WHEN meeting creation fails, THE LMS SHALL return a descriptive error message to the user

### Requirement 3: Meeting Room Configuration

**User Story:** As a teacher, I want to configure meeting room settings when creating a live class, so that I can control the classroom environment and participant capabilities.

#### Acceptance Criteria

1. THE LMS SHALL configure BBB meeting rooms with the live class title as the meeting name
2. THE LMS SHALL set the teacher as the moderator with full control permissions
3. THE LMS SHALL enable waiting room functionality where attendees wait for moderator approval
4. THE LMS SHALL configure participant audio and video settings based on teacher preferences
5. THE LMS SHALL set maximum participant limits based on subscription tier or configuration

### Requirement 4: Student Join Experience

**User Story:** As a student, I want to join live classes through the LMS interface, so that I can attend virtual classroom sessions seamlessly.

#### Acceptance Criteria

1. WHEN a student clicks to join a live class, THE LMS SHALL redirect them to the BBB meeting room with their name pre-filled
2. THE LMS SHALL authenticate students before generating join URLs to prevent unauthorized access
3. WHEN a meeting has not started, THE LMS SHALL display a waiting message to students
4. THE LMS SHALL pass student identification data to BBB for attendance tracking purposes
5. THE LMS SHALL open the BBB meeting in a new browser tab or embedded iframe based on configuration

### Requirement 5: Teacher Host Experience

**User Story:** As a teacher, I want to start and control live class sessions, so that I can manage the virtual classroom effectively.

#### Acceptance Criteria

1. WHEN a teacher starts a live class, THE LMS SHALL provide the moderator join URL with host privileges
2. THE LMS SHALL grant teachers full moderator controls including mute, kick, and screen sharing permissions
3. THE LMS SHALL allow teachers to end meetings for all participants
4. WHEN a teacher ends a class, THE LMS SHALL update the live class status to completed
5. THE LMS SHALL enable teachers to access meeting recordings after class completion

### Requirement 6: Attendance Tracking

**User Story:** As a teacher, I want the system to automatically track student attendance in live classes, so that I can monitor participation without manual effort.

#### Acceptance Criteria

1. WHEN a student joins a BBB meeting, THE LMS SHALL create an attendance record with join timestamp
2. WHEN a student leaves a BBB meeting, THE LMS SHALL update the attendance record with leave timestamp
3. THE LMS SHALL calculate total participation duration for each student
4. THE LMS SHALL mark attendance status as present, absent, late, or partial based on participation duration
5. WHEN webhook events are received, THE LMS SHALL process them within 5 seconds to maintain real-time accuracy

### Requirement 7: Webhook Event Processing

**User Story:** As a system administrator, I want the LMS to receive and process BBB webhook events, so that attendance and meeting status are automatically updated in real-time.

#### Acceptance Criteria

1. THE LMS SHALL expose a webhook endpoint that accepts POST requests from BBB servers
2. WHEN a meeting-started event is received, THE LMS SHALL update the live class status to in-progress
3. WHEN a meeting-ended event is received, THE LMS SHALL update the live class status to completed
4. WHEN a user-joined event is received, THE LMS SHALL create or update the attendance record
5. WHEN a user-left event is received, THE LMS SHALL update the attendance record with departure time

### Requirement 8: Recording Management

**User Story:** As a teacher, I want live class sessions to be recorded automatically, so that students can review the content later.

#### Acceptance Criteria

1. WHEN a teacher enables recording for a live class, THE LMS SHALL configure the BBB meeting to record automatically
2. WHEN a recording is ready, THE LMS SHALL receive a webhook notification with the recording URL
3. THE LMS SHALL store recording URLs and metadata in the LiveClass model
4. THE LMS SHALL provide teachers and enrolled students access to view recordings
5. THE LMS SHALL support downloading recordings in standard video formats

### Requirement 9: Migration of Existing Data

**User Story:** As a system administrator, I want to migrate existing Zoom-based live class data to the new BBB structure, so that historical records are preserved.

#### Acceptance Criteria

1. THE LMS SHALL provide a database migration script that updates the LiveClass model schema
2. THE LMS SHALL rename zoom_meeting_id field to meeting_id for provider-agnostic naming
3. THE LMS SHALL add new fields for BBB-specific data including moderator_password and attendee_password
4. THE LMS SHALL preserve all existing attendance records and analytics data
5. WHEN migration completes, THE LMS SHALL generate a summary report of migrated records

### Requirement 10: API Endpoint Updates

**User Story:** As a frontend developer, I want updated API endpoints that work with BBB instead of Zoom, so that the UI can interact with the new video conferencing system.

#### Acceptance Criteria

1. THE LMS SHALL replace the create_zoom_meeting endpoint with create_meeting endpoint
2. THE LMS SHALL update the join_info endpoint to return BBB join URLs instead of Zoom URLs
3. THE LMS SHALL maintain backward compatibility during a transition period with feature flags
4. THE LMS SHALL return consistent response formats for all meeting-related endpoints
5. THE LMS SHALL document all API changes in the API specification

### Requirement 11: Frontend Service Updates

**User Story:** As a frontend developer, I want to update the zoom.ts service to work with BBB, so that the UI components continue to function correctly.

#### Acceptance Criteria

1. THE Frontend Service SHALL rename zoom.ts to videoConference.ts for provider-agnostic naming
2. THE Frontend Service SHALL update all API calls to use new BBB-compatible endpoints
3. THE Frontend Service SHALL handle BBB-specific response formats and data structures
4. THE Frontend Service SHALL maintain the same public interface to minimize component changes
5. THE Frontend Service SHALL implement proper error handling for BBB-specific error scenarios

### Requirement 12: Configuration Management

**User Story:** As a system administrator, I want to configure BBB connection settings through environment variables, so that I can easily deploy to different environments.

#### Acceptance Criteria

1. THE LMS SHALL read BBB server URL from BBB_SERVER_URL environment variable
2. THE LMS SHALL read BBB shared secret from BBB_SHARED_SECRET environment variable
3. THE LMS SHALL remove all Zoom-related environment variables from configuration files
4. THE LMS SHALL provide example configuration in .env.example files
5. THE LMS SHALL validate required BBB environment variables on application startup

### Requirement 13: Error Handling and Resilience

**User Story:** As a user, I want the system to handle BBB service failures gracefully, so that I receive clear feedback when issues occur.

#### Acceptance Criteria

1. WHEN BBB server is unavailable, THE LMS SHALL display a user-friendly error message
2. WHEN meeting creation fails, THE LMS SHALL retry the operation up to 3 times with exponential backoff
3. THE LMS SHALL log all BBB API errors with sufficient detail for troubleshooting
4. WHEN webhook processing fails, THE LMS SHALL queue the event for retry processing
5. THE LMS SHALL provide system health checks that verify BBB connectivity

### Requirement 14: Testing and Validation

**User Story:** As a developer, I want comprehensive tests for BBB integration, so that I can verify the migration works correctly.

#### Acceptance Criteria

1. THE LMS SHALL include unit tests for BBB API client methods with mocked responses
2. THE LMS SHALL include integration tests that verify meeting creation and join URL generation
3. THE LMS SHALL include tests for webhook event processing with sample payloads
4. THE LMS SHALL include tests for attendance tracking accuracy
5. THE LMS SHALL include end-to-end tests that simulate complete live class workflows

### Requirement 15: Documentation Updates

**User Story:** As a system administrator, I want updated documentation for BBB setup and configuration, so that I can deploy and maintain the system.

#### Acceptance Criteria

1. THE LMS SHALL provide a BBB_SETUP.md guide replacing ZOOM_API_SETUP.md
2. THE Documentation SHALL include BBB server installation and configuration instructions
3. THE Documentation SHALL include webhook configuration steps
4. THE Documentation SHALL include troubleshooting guides for common BBB issues
5. THE Documentation SHALL include API endpoint migration guide for developers
