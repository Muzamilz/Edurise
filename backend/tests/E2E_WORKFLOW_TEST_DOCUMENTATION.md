# E2E Workflow Integration Test Documentation

## Overview

This documentation covers the comprehensive end-to-end (E2E) workflow integration tests implemented for the centralized API endpoints. These tests verify complete user workflows from frontend through backend API to ensure data integration and functionality work correctly across the entire system.

**Requirement**: 11.2 - Implement end-to-end workflow tests for centralized API

## Test Structure

### Backend Tests (`test_e2e_workflow_integration.py`)

#### 1. UserWorkflowE2ETest
Tests complete user journeys from registration to course completion.

**Workflows Tested:**
- User registration through centralized API
- User authentication and token management
- Course browsing and enrollment
- Course progress tracking
- Course completion and review submission

**Key Test Methods:**
- `test_complete_user_registration_to_course_completion_workflow()`
- `test_teacher_course_creation_and_management_workflow()`

**API Endpoints Covered:**
- `/api/v1/accounts/auth/register/`
- `/api/v1/accounts/auth/login/`
- `/api/v1/courses/`
- `/api/v1/enrollments/`
- `/api/v1/course-reviews/`

#### 2. LiveClassAndAttendanceWorkflowE2ETest
Tests live class scheduling, management, and attendance tracking workflows.

**Workflows Tested:**
- Live class creation with Zoom integration
- Student enrollment and class joining
- Real-time attendance tracking
- Class completion and reporting

**Key Test Methods:**
- `test_complete_live_class_workflow()`
- `test_attendance_tracking_workflow()`

**API Endpoints Covered:**
- `/api/v1/live-classes/`
- `/api/v1/attendance/`
- `/api/v1/live-classes/{id}/start/`
- `/api/v1/live-classes/{id}/join/`
- `/api/v1/live-classes/{id}/end/`

**External Integrations Tested:**
- Zoom API integration (mocked)
- Real-time WebSocket connections

#### 3. PaymentAndSubscriptionWorkflowE2ETest
Tests payment processing and subscription management workflows.

**Workflows Tested:**
- Course payment processing with Stripe
- Enrollment creation after successful payment
- Invoice generation and delivery
- Subscription creation and management
- Payment history and billing

**Key Test Methods:**
- `test_complete_course_payment_workflow()`
- `test_subscription_management_workflow()`

**API Endpoints Covered:**
- `/api/v1/payments/payments/create_course_payment/`
- `/api/v1/payments/payments/{id}/confirm_payment/`
- `/api/v1/payments/subscriptions/`
- `/api/v1/payments/invoices/`

**External Integrations Tested:**
- Stripe payment processing (mocked)
- PayPal integration (mocked)
- Email delivery for invoices

#### 4. FileManagementAndCertificateWorkflowE2ETest
Tests file upload, management, and certificate generation workflows.

**Workflows Tested:**
- Course material upload and management
- Student file access and downloads
- Certificate generation after course completion
- Certificate verification and sharing
- Profile image upload

**Key Test Methods:**
- `test_complete_file_upload_workflow()`
- `test_certificate_generation_workflow()`
- `test_profile_image_upload_workflow()`

**API Endpoints Covered:**
- `/api/v1/files/uploads/`
- `/api/v1/assignments/certificates/generate/`
- `/api/v1/assignments/certificates/verify/`
- `/api/v1/accounts/users/profile/`

**External Integrations Tested:**
- File storage services (S3/MinIO mocked)
- PDF generation for certificates
- Email delivery for certificates

### Frontend Tests (`e2e-workflow.spec.ts`)

#### 1. Complete Student Learning Workflow
Tests the entire student experience from login to course completion.

**User Journey:**
1. Student login with authentication
2. Dashboard view with real data
3. Course browsing and selection
4. Course enrollment process
5. Accessing course content and materials
6. Participating in live classes
7. Course completion and certificate generation

**UI Components Tested:**
- Authentication forms
- Dashboard widgets
- Course marketplace
- Course detail pages
- Learning interface
- Live class interface
- Certificate display

#### 2. Complete Teacher Course Management Workflow
Tests the teacher experience for course creation and management.

**User Journey:**
1. Teacher login and dashboard access
2. Course creation with content
3. Module and material upload
4. Live class scheduling
5. Student management and analytics
6. Attendance tracking and reporting

**UI Components Tested:**
- Teacher dashboard
- Course creation forms
- Content management interface
- Live class scheduling
- Analytics dashboard
- Student management tools

#### 3. Complete Payment and Enrollment Workflow
Tests the payment process from course selection to enrollment.

**User Journey:**
1. Course selection and checkout
2. Payment form completion
3. Payment processing with Stripe
4. Enrollment confirmation
5. Course access after payment
6. Payment history and invoice download

**UI Components Tested:**
- Checkout interface
- Payment forms
- Payment processing indicators
- Enrollment confirmation
- Payment history
- Invoice management

#### 4. Complete Live Class Attendance Workflow
Tests live class participation and attendance tracking.

**User Journey:**
1. Viewing scheduled live classes
2. Joining live classes via Zoom
3. Attendance tracking and recording
4. Attendance history viewing
5. Teacher attendance reporting

**UI Components Tested:**
- Live class listings
- Class joining interface
- Attendance tracking
- Attendance reports
- Real-time updates

#### 5. Complete File Upload and Certificate Workflow
Tests file management and certificate generation.

**User Journey:**
1. Teacher file upload for course materials
2. Student access to course materials
3. File download and viewing
4. Course completion tracking
5. Certificate generation and download
6. Certificate sharing and verification

**UI Components Tested:**
- File upload interface
- Material listings
- Download functionality
- Certificate generation
- Certificate display and sharing

#### 6. Error Handling and Recovery Workflows
Tests error scenarios and recovery mechanisms.

**Error Scenarios:**
- Network connectivity issues
- API server errors
- Authentication failures
- Payment processing errors
- File upload failures

**Recovery Mechanisms:**
- Retry functionality
- Graceful error display
- Automatic token refresh
- Fallback UI states
- User guidance for resolution

## Test Data Setup

### Base Test Data
Each test suite creates comprehensive test data including:

- **Organizations/Tenants**: Multi-tenant test environments
- **Users**: Students, teachers, admins with proper roles
- **Courses**: Various course types and configurations
- **Enrollments**: Active, completed, and pending enrollments
- **Payments**: Successful, failed, and pending payments
- **Live Classes**: Scheduled, in-progress, and completed classes
- **Files**: Course materials, profile images, certificates
- **Subscriptions**: Active, cancelled, and expired subscriptions

### External Service Mocking
All external services are properly mocked:

- **Stripe API**: Payment intents, customers, subscriptions
- **PayPal API**: Orders, captures, webhooks
- **Zoom API**: Meeting creation, management, webhooks
- **Email Services**: SMTP, delivery tracking
- **File Storage**: S3/MinIO upload, download, URLs
- **PDF Generation**: Certificate and invoice creation

## Running the Tests

### Backend Tests
```bash
# Run all E2E workflow tests
python backend/tests/run_e2e_workflow_tests.py

# Run specific test class
python manage.py test tests.test_e2e_workflow_integration.UserWorkflowE2ETest -v 2

# Run specific test method
python manage.py test tests.test_e2e_workflow_integration.UserWorkflowE2ETest.test_complete_user_registration_to_course_completion_workflow -v 2
```

### Frontend Tests
```bash
# Run all frontend E2E tests
cd frontend
npx playwright test tests/integration/e2e-workflow.spec.ts

# Run specific test
npx playwright test tests/integration/e2e-workflow.spec.ts -g "complete student learning workflow"

# Run with UI mode for debugging
npx playwright test tests/integration/e2e-workflow.spec.ts --ui
```

### Combined Test Execution
```bash
# Run both backend and frontend E2E tests
python backend/tests/run_e2e_workflow_tests.py
```

## Test Coverage

### API Endpoints Tested
- ✅ Authentication endpoints (`/api/v1/accounts/auth/`)
- ✅ Course management (`/api/v1/courses/`)
- ✅ Enrollment management (`/api/v1/enrollments/`)
- ✅ Live class management (`/api/v1/live-classes/`)
- ✅ Attendance tracking (`/api/v1/attendance/`)
- ✅ Payment processing (`/api/v1/payments/`)
- ✅ File management (`/api/v1/files/`)
- ✅ Certificate generation (`/api/v1/assignments/certificates/`)
- ✅ Dashboard endpoints (`/api/v1/dashboard/`)
- ✅ Notification system (`/api/v1/notifications/`)

### User Workflows Covered
- ✅ Student registration and onboarding
- ✅ Course discovery and enrollment
- ✅ Learning progress tracking
- ✅ Live class participation
- ✅ Payment and billing
- ✅ Certificate earning and sharing
- ✅ Teacher course creation
- ✅ Content management
- ✅ Student analytics
- ✅ File upload and sharing

### Integration Points Tested
- ✅ Frontend ↔ Centralized API
- ✅ API ↔ Database (PostgreSQL/SQLite)
- ✅ API ↔ External Payment Services
- ✅ API ↔ Zoom Integration
- ✅ API ↔ File Storage Services
- ✅ API ↔ Email Services
- ✅ API ↔ PDF Generation
- ✅ Real-time WebSocket connections
- ✅ Multi-tenant data isolation

## Expected Test Results

### Success Criteria
All tests should pass with the following outcomes:

1. **Authentication Workflows**: Users can register, login, and maintain sessions
2. **Course Workflows**: Courses can be created, enrolled in, and completed
3. **Payment Workflows**: Payments process successfully and create enrollments
4. **Live Class Workflows**: Classes can be scheduled, joined, and tracked
5. **File Workflows**: Files can be uploaded, accessed, and downloaded
6. **Certificate Workflows**: Certificates generate and deliver correctly
7. **Error Handling**: Errors are handled gracefully with recovery options

### Performance Expectations
- API response times < 2 seconds for most endpoints
- File uploads complete within reasonable time limits
- Payment processing completes within 30 seconds
- Certificate generation completes within 10 seconds
- Dashboard loading completes within 3 seconds

### Data Integrity Verification
- All database transactions complete successfully
- Multi-tenant data isolation is maintained
- File uploads are stored securely
- Payment records are accurate and complete
- Enrollment status updates correctly
- Progress tracking functions properly

## Troubleshooting

### Common Issues

#### Backend Test Failures
- **Database Connection**: Ensure test database is configured
- **External Service Mocks**: Verify all external services are properly mocked
- **Tenant Context**: Check that tenant middleware is working correctly
- **Permissions**: Ensure user roles and permissions are set up correctly

#### Frontend Test Failures
- **API Mocking**: Verify all API endpoints are properly mocked
- **Timing Issues**: Add appropriate waits for async operations
- **Element Selectors**: Ensure test selectors match actual UI elements
- **Browser Context**: Check that browser state is properly managed

#### Integration Issues
- **CORS Configuration**: Ensure CORS is properly configured for tests
- **Authentication**: Verify JWT token handling works correctly
- **File Uploads**: Check that multipart form handling works
- **WebSocket Connections**: Ensure real-time features are testable

### Debugging Tips

1. **Use Verbose Output**: Run tests with `-v 2` for detailed output
2. **Check Logs**: Review Django and application logs for errors
3. **Isolate Tests**: Run individual test methods to isolate issues
4. **Mock Verification**: Ensure external service mocks are called correctly
5. **Database State**: Check database state before and after tests
6. **Network Inspection**: Use browser dev tools to inspect API calls

## Maintenance

### Regular Updates Required
- Update test data when models change
- Refresh external service mocks when APIs change
- Update UI selectors when frontend components change
- Maintain test coverage as new features are added
- Update documentation when workflows change

### Performance Monitoring
- Monitor test execution times
- Optimize slow-running tests
- Maintain reasonable test suite execution time
- Balance comprehensive coverage with execution speed

This comprehensive E2E workflow testing ensures that all user journeys through the centralized API work correctly and provides confidence in the system's reliability and functionality.