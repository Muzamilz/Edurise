import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'
import test from 'node:test'

describe('Live Class Functionality Integration', () => {
  // Test data
  const testInstructor = {
    email: 'instructor@test.com',
    password: 'testpass123',
    firstName: 'John',
    lastName: 'Instructor'
  }

  const testStudent1 = {
    email: 'student1@test.com',
    password: 'testpass123',
    firstName: 'Jane',
    lastName: 'Student'
  }

  const testStudent2 = {
    email: 'student2@test.com',
    password: 'testpass123',
    firstName: 'Bob',
    lastName: 'Learner'
  }

  const testCourse = {
    title: 'Live Class Integration Test Course',
    description: 'Course for testing live class functionality',
    category: 'technology',
    difficulty: 'beginner'
  }

  const testLiveClass = {
    title: 'Integration Test Live Class',
    description: 'Live class for integration testing',
    duration: 60,
    scheduledAt: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString() // 2 hours from now
  }

  // Mock Zoom API responses
  const mockZoomMeetingResponse = {
    id: '123456789',
    topic: testLiveClass.title,
    join_url: 'https://zoom.us/j/123456789?pwd=testpassword',
    start_url: 'https://zoom.us/s/123456789?zak=testtoken',
    password: 'testpass',
    status: 'waiting'
  }

  const mockZoomParticipantsResponse = {
    participants: [
      {
        id: 'participant1',
        user_name: 'Jane Student',
        user_email: 'student1@test.com',
        join_time: '2024-01-15T10:00:00Z',
        leave_time: '2024-01-15T10:45:00Z',
        duration: 45
      },
      {
        id: 'participant2',
        user_name: 'Bob Learner',
        user_email: 'student2@test.com',
        join_time: '2024-01-15T10:05:00Z',
        leave_time: '2024-01-15T10:50:00Z',
        duration: 45
      }
    ]
  }

  test.beforeEach(async ({ page }) => {
    // Mock API endpoints
    await page.route('**/api/v1/accounts/organizations/by_subdomain/*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '1',
          name: 'Test Organization',
          subdomain: 'test-org',
          primary_color: '#3b82f6',
          secondary_color: '#1e40af',
          logo: null,
          subscription_plan: 'pro'
        })
      })
    })

    // Navigate to the application
    await page.goto('/')
  })

  test.describe('Zoom Meeting Creation and URL Generation', () => {
    test('instructor can create live class with Zoom meeting integration', async ({ page }) => {
      // Mock Zoom meeting creation API
      await page.route('**/api/v1/classes/zoom-meetings/*', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              message: 'Zoom meeting created successfully',
              meeting_info: mockZoomMeetingResponse
            })
          })
        }
      })

      // Mock live class creation API
      await page.route('**/api/v1/courses/live-classes/', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 201,
            contentType: 'application/json',
            body: JSON.stringify({
              id: 'live-class-1',
              ...testLiveClass,
              zoom_meeting_id: mockZoomMeetingResponse.id,
              join_url: mockZoomMeetingResponse.join_url,
              start_url: mockZoomMeetingResponse.start_url,
              password: mockZoomMeetingResponse.password,
              status: 'scheduled'
            })
          })
        }
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to live classes management
      await page.click('text=Live Classes')
      await expect(page.locator('h1:has-text("Live Classes")')).toBeVisible()

      // Create new live class
      await page.click('text=Schedule Live Class')
      await expect(page.locator('h1:has-text("Schedule New Live Class")')).toBeVisible()

      // Fill live class form
      await page.fill('input[id="title"]', testLiveClass.title)
      await page.fill('textarea[id="description"]', testLiveClass.description)
      await page.fill('input[id="duration_minutes"]', testLiveClass.duration.toString())
      
      // Set scheduled date/time
      const scheduledDate = new Date(testLiveClass.scheduledAt)
      await page.fill('input[type="datetime-local"]', scheduledDate.toISOString().slice(0, 16))

      // Enable Zoom integration
      await page.check('input[id="enable_zoom"]')

      // Submit form
      await page.click('button[type="submit"]')

      // Should show success message and Zoom meeting details
      await expect(page.locator('text=Live class scheduled successfully')).toBeVisible({ timeout: 10000 })
      await expect(page.locator('text=Zoom meeting created')).toBeVisible()

      // Verify Zoom meeting details are displayed
      await expect(page.locator(`text=${mockZoomMeetingResponse.join_url}`)).toBeVisible()
      await expect(page.locator('text=Meeting ID: 123456789')).toBeVisible()
      await expect(page.locator('text=Password: testpass')).toBeVisible()
    })

    test('instructor can update live class and sync with Zoom', async ({ page }) => {
      // Mock existing live class
      await page.route('**/api/v1/courses/live-classes/live-class-1/', async route => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              id: 'live-class-1',
              ...testLiveClass,
              zoom_meeting_id: mockZoomMeetingResponse.id,
              join_url: mockZoomMeetingResponse.join_url,
              start_url: mockZoomMeetingResponse.start_url,
              status: 'scheduled'
            })
          })
        } else if (route.request().method() === 'PUT') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              id: 'live-class-1',
              title: 'Updated Live Class Title',
              ...testLiveClass,
              zoom_meeting_id: mockZoomMeetingResponse.id
            })
          })
        }
      })

      // Mock Zoom meeting update API
      await page.route('**/api/v1/classes/zoom-meetings/live-class-1', async route => {
        if (route.request().method() === 'PUT') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              message: 'Zoom meeting updated successfully'
            })
          })
        }
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to live class edit
      await page.goto('/live-classes/live-class-1/edit')

      // Update live class details
      await page.fill('input[id="title"]', 'Updated Live Class Title')
      await page.click('button[type="submit"]')

      // Should show success message
      await expect(page.locator('text=Live class updated successfully')).toBeVisible({ timeout: 10000 })
      await expect(page.locator('text=Zoom meeting updated')).toBeVisible()
    })

    test('handles Zoom API errors gracefully', async ({ page }) => {
      // Mock Zoom API error
      await page.route('**/api/v1/classes/zoom-meetings/*', async route => {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            error: 'Zoom API error: Failed to create meeting'
          })
        })
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Try to create live class
      await page.goto('/live-classes/create')
      await page.fill('input[id="title"]', testLiveClass.title)
      await page.fill('textarea[id="description"]', testLiveClass.description)
      await page.check('input[id="enable_zoom"]')
      await page.click('button[type="submit"]')

      // Should show error message
      await expect(page.locator('text=Failed to create Zoom meeting')).toBeVisible({ timeout: 10000 })
      await expect(page.locator('text=Please try again or contact support')).toBeVisible()
    })
  })

  test.describe('Attendance Tracking Accuracy', () => {
    test('instructor can manually mark attendance for students', async ({ page }) => {
      // Mock live class with enrolled students
      await page.route('**/api/v1/courses/live-classes/live-class-1/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'live-class-1',
            ...testLiveClass,
            status: 'live',
            enrolled_students: [
              { id: 'student-1', name: 'Jane Student', email: 'student1@test.com' },
              { id: 'student-2', name: 'Bob Learner', email: 'student2@test.com' }
            ]
          })
        })
      })

      // Mock attendance marking API
      await page.route('**/api/v1/classes/attendance/mark_attendance/', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              message: 'Attendance marked successfully',
              attendance_id: 'attendance-1'
            })
          })
        }
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to live class attendance
      await page.goto('/live-classes/live-class-1/attendance')

      // Should show attendance interface
      await expect(page.locator('h1:has-text("Class Attendance")')).toBeVisible()
      await expect(page.locator('text=Jane Student')).toBeVisible()
      await expect(page.locator('text=Bob Learner')).toBeVisible()

      // Mark attendance for first student
      const student1Row = page.locator('[data-testid="student-row-student-1"]')
      await student1Row.locator('select[name="status"]').selectOption('present')
      await student1Row.locator('button:has-text("Save")').click()

      // Should show success message
      await expect(page.locator('text=Attendance marked successfully')).toBeVisible()

      // Mark attendance for second student as late
      const student2Row = page.locator('[data-testid="student-row-student-2"]')
      await student2Row.locator('select[name="status"]').selectOption('late')
      await student2Row.locator('input[name="join_time"]').fill('10:05')
      await student2Row.locator('button:has-text("Save")').click()

      await expect(page.locator('text=Attendance marked successfully')).toBeVisible()
    })

    test('system processes Zoom webhook for automatic attendance tracking', async ({ page }) => {
      // Mock webhook processing endpoint
      await page.route('**/api/v1/classes/zoom-webhook/', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ status: 'processed' })
          })
        }
      })

      // Mock attendance report API
      await page.route('**/api/v1/classes/attendance/class_report/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            live_class: {
              id: 'live-class-1',
              title: testLiveClass.title,
              scheduled_at: testLiveClass.scheduledAt,
              duration_minutes: testLiveClass.duration
            },
            metrics: {
              total_students: 2,
              attendance_rate: 100.0,
              average_duration: 45.0,
              engagement_score: 85.5,
              status_breakdown: {
                present: 1,
                late: 1,
                absent: 0,
                partial: 0
              }
            },
            attendances: [
              {
                student_name: 'Jane Student',
                student_email: 'student1@test.com',
                status: 'present',
                join_time: '2024-01-15T10:00:00Z',
                leave_time: '2024-01-15T10:45:00Z',
                duration_minutes: 45,
                attendance_percentage: 75.0,
                participation_score: 80
              },
              {
                student_name: 'Bob Learner',
                student_email: 'student2@test.com',
                status: 'late',
                join_time: '2024-01-15T10:05:00Z',
                leave_time: '2024-01-15T10:50:00Z',
                duration_minutes: 45,
                attendance_percentage: 75.0,
                participation_score: 70
              }
            ]
          })
        })
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to attendance report
      await page.goto('/live-classes/live-class-1/report')

      // Should show attendance report with Zoom-tracked data
      await expect(page.locator('h1:has-text("Attendance Report")')).toBeVisible()
      
      // Verify metrics
      await expect(page.locator('text=Total Students: 2')).toBeVisible()
      await expect(page.locator('text=Attendance Rate: 100%')).toBeVisible()
      await expect(page.locator('text=Average Duration: 45 minutes')).toBeVisible()
      await expect(page.locator('text=Engagement Score: 85.5')).toBeVisible()

      // Verify individual attendance records
      await expect(page.locator('text=Jane Student')).toBeVisible()
      await expect(page.locator('text=Present')).toBeVisible()
      await expect(page.locator('text=45 minutes')).toBeVisible()

      await expect(page.locator('text=Bob Learner')).toBeVisible()
      await expect(page.locator('text=Late')).toBeVisible()
    })

    test('calculates engagement metrics accurately', async ({ page }) => {
      // Mock detailed analytics API
      await page.route('**/api/v1/classes/attendance/class_report/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            live_class: {
              id: 'live-class-1',
              title: testLiveClass.title,
              duration_minutes: 60
            },
            metrics: {
              total_students: 3,
              attendance_rate: 66.67,
              average_duration: 40.0,
              engagement_score: 72.5,
              status_breakdown: {
                present: 1,
                late: 1,
                absent: 1,
                partial: 0
              },
              duration_stats: {
                min_duration: 30.0,
                max_duration: 50.0,
                median_duration: 40.0,
                duration_retention_rate: 66.67
              },
              participation_stats: {
                average_participation: 65.0,
                total_questions: 5,
                active_participants: 2,
                participation_rate: 66.67
              }
            },
            timing_analysis: {
              on_time_students: 1,
              late_students: 1,
              peak_join_time: '2024-01-15T10:00:00Z',
              peak_join_count: 1
            },
            recommendations: [
              {
                type: 'engagement',
                message: 'Students are leaving early. Consider adding interactive elements or breaks',
                priority: 'high'
              },
              {
                type: 'participation',
                message: 'Good participation rate. Keep encouraging student interaction',
                priority: 'medium'
              }
            ]
          })
        })
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to analytics dashboard
      await page.goto('/live-classes/live-class-1/analytics')

      // Should show comprehensive analytics
      await expect(page.locator('h1:has-text("Class Analytics")')).toBeVisible()

      // Verify engagement metrics
      await expect(page.locator('text=Engagement Score: 72.5')).toBeVisible()
      await expect(page.locator('text=Duration Retention: 66.67%')).toBeVisible()
      await expect(page.locator('text=Participation Rate: 66.67%')).toBeVisible()

      // Verify timing analysis
      await expect(page.locator('text=On-time Students: 1')).toBeVisible()
      await expect(page.locator('text=Late Students: 1')).toBeVisible()

      // Verify recommendations
      await expect(page.locator('text=Students are leaving early')).toBeVisible()
      await expect(page.locator('text=Good participation rate')).toBeVisible()

      // Should show visual charts (Three.js visualizations)
      await expect(page.locator('[data-testid="engagement-chart"]')).toBeVisible()
      await expect(page.locator('[data-testid="attendance-breakdown"]')).toBeVisible()
    })
  })

  test.describe('Recording Storage and Retrieval', () => {
    test('instructor can access and manage class recordings', async ({ page }) => {
      // Mock recordings API
      await page.route('**/api/v1/courses/live-classes/live-class-1/recordings/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            recordings: [
              {
                id: 'recording-1',
                title: 'Live Class Recording - Jan 15, 2024',
                recording_url: 'https://storage.example.com/recordings/recording-1.mp4',
                duration_minutes: 58,
                file_size_mb: 245.6,
                created_at: '2024-01-15T11:00:00Z',
                status: 'processed'
              }
            ]
          })
        })
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to recordings
      await page.goto('/live-classes/live-class-1/recordings')

      // Should show recordings list
      await expect(page.locator('h1:has-text("Class Recordings")')).toBeVisible()
      await expect(page.locator('text=Live Class Recording - Jan 15, 2024')).toBeVisible()
      await expect(page.locator('text=58 minutes')).toBeVisible()
      await expect(page.locator('text=245.6 MB')).toBeVisible()

      // Should have download and play options
      await expect(page.locator('button:has-text("Play")')).toBeVisible()
      await expect(page.locator('button:has-text("Download")')).toBeVisible()
    })

    test('students can access recordings after class completion', async ({ page }) => {
      // Mock student enrollment check
      await page.route('**/api/v1/courses/courses/course-1/enrollment/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            is_enrolled: true,
            enrollment_status: 'active'
          })
        })
      })

      // Mock recordings API for students (limited access)
      await page.route('**/api/v1/courses/live-classes/live-class-1/recordings/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            recordings: [
              {
                id: 'recording-1',
                title: 'Live Class Recording - Jan 15, 2024',
                recording_url: 'https://storage.example.com/recordings/recording-1.mp4',
                duration_minutes: 58,
                created_at: '2024-01-15T11:00:00Z',
                status: 'processed',
                can_download: false // Students can only stream
              }
            ]
          })
        })
      })

      // Login as student
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testStudent1.email)
      await page.fill('input[type="password"]', testStudent1.password)
      await page.click('button[type="submit"]')

      // Navigate to course recordings
      await page.goto('/courses/course-1/recordings')

      // Should show recordings available to student
      await expect(page.locator('text=Live Class Recording - Jan 15, 2024')).toBeVisible()
      await expect(page.locator('button:has-text("Play")')).toBeVisible()
      
      // Download should not be available for students
      await expect(page.locator('button:has-text("Download")')).not.toBeVisible()
    })

    test('handles recording processing status updates', async ({ page }) => {
      // Mock recordings with different statuses
      await page.route('**/api/v1/courses/live-classes/live-class-1/recordings/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            recordings: [
              {
                id: 'recording-1',
                title: 'Processing Recording',
                status: 'processing',
                progress_percentage: 75,
                created_at: '2024-01-15T11:00:00Z'
              },
              {
                id: 'recording-2',
                title: 'Failed Recording',
                status: 'failed',
                error_message: 'Processing failed due to corrupted file',
                created_at: '2024-01-15T10:00:00Z'
              },
              {
                id: 'recording-3',
                title: 'Completed Recording',
                status: 'processed',
                recording_url: 'https://storage.example.com/recordings/recording-3.mp4',
                duration_minutes: 60,
                created_at: '2024-01-15T09:00:00Z'
              }
            ]
          })
        })
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to recordings
      await page.goto('/live-classes/live-class-1/recordings')

      // Should show different recording statuses
      await expect(page.locator('text=Processing Recording')).toBeVisible()
      await expect(page.locator('text=Processing... 75%')).toBeVisible()

      await expect(page.locator('text=Failed Recording')).toBeVisible()
      await expect(page.locator('text=Processing failed')).toBeVisible()

      await expect(page.locator('text=Completed Recording')).toBeVisible()
      await expect(page.locator('button:has-text("Play")')).toBeVisible()
    })
  })

  test.describe('Real-time Updates During Live Classes', () => {
    test('instructor sees real-time attendance updates during live class', async ({ page }) => {
      // Mock WebSocket connection for real-time updates
      await page.addInitScript(() => {
        // Mock WebSocket
        class MockWebSocket {
          constructor(url) {
            this.url = url
            this.readyState = WebSocket.CONNECTING
            setTimeout(() => {
              this.readyState = WebSocket.OPEN
              if (this.onopen) this.onopen()
            }, 100)
          }

          send(data) {
            // Simulate receiving attendance updates
            setTimeout(() => {
              if (this.onmessage) {
                this.onmessage({
                  data: JSON.stringify({
                    type: 'attendance_update',
                    data: {
                      student_id: 'student-1',
                      student_name: 'Jane Student',
                      action: 'joined',
                      timestamp: new Date().toISOString()
                    }
                  })
                })
              }
            }, 500)
          }

          close() {
            this.readyState = WebSocket.CLOSED
            if (this.onclose) this.onclose()
          }
        }

        window.WebSocket = MockWebSocket
      })

      // Mock live class status
      await page.route('**/api/v1/courses/live-classes/live-class-1/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'live-class-1',
            ...testLiveClass,
            status: 'live',
            current_participants: 0
          })
        })
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to live class control panel
      await page.goto('/live-classes/live-class-1/control')

      // Should show live class interface
      await expect(page.locator('h1:has-text("Live Class Control")')).toBeVisible()
      await expect(page.locator('text=Status: Live')).toBeVisible()
      await expect(page.locator('[data-testid="participant-count"]')).toContainText('0')

      // Wait for WebSocket connection and real-time update
      await page.waitForTimeout(1000)

      // Should show real-time attendance update
      await expect(page.locator('text=Jane Student joined')).toBeVisible({ timeout: 5000 })
      await expect(page.locator('[data-testid="participant-count"]')).toContainText('1')
    })

    test('students receive real-time class status updates', async ({ page }) => {
      // Mock WebSocket for student updates
      await page.addInitScript(() => {
        class MockWebSocket {
          constructor(url) {
            this.url = url
            this.readyState = WebSocket.CONNECTING
            setTimeout(() => {
              this.readyState = WebSocket.OPEN
              if (this.onopen) this.onopen()
            }, 100)
          }

          send(data) {
            // Simulate class status updates
            setTimeout(() => {
              if (this.onmessage) {
                this.onmessage({
                  data: JSON.stringify({
                    type: 'class_status_update',
                    data: {
                      class_id: 'live-class-1',
                      status: 'live',
                      message: 'Class has started! Join now.',
                      join_url: 'https://zoom.us/j/123456789'
                    }
                  })
                })
              }
            }, 500)
          }

          close() {
            this.readyState = WebSocket.CLOSED
            if (this.onclose) this.onclose()
          }
        }

        window.WebSocket = MockWebSocket
      })

      // Mock student enrollment
      await page.route('**/api/v1/courses/courses/course-1/enrollment/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            is_enrolled: true,
            enrollment_status: 'active'
          })
        })
      })

      // Login as student
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testStudent1.email)
      await page.fill('input[type="password"]', testStudent1.password)
      await page.click('button[type="submit"]')

      // Navigate to course dashboard
      await page.goto('/courses/course-1/dashboard')

      // Should show upcoming live class
      await expect(page.locator('text=Upcoming Live Class')).toBeVisible()
      await expect(page.locator(`text=${testLiveClass.title}`)).toBeVisible()

      // Wait for real-time status update
      await page.waitForTimeout(1000)

      // Should show live class notification
      await expect(page.locator('text=Class has started! Join now.')).toBeVisible({ timeout: 5000 })
      
      // Should show join button with Zoom URL
      const joinButton = page.locator('button:has-text("Join Live Class")')
      await expect(joinButton).toBeVisible()
      await expect(joinButton).toHaveAttribute('data-zoom-url', 'https://zoom.us/j/123456789')
    })

    test('handles WebSocket connection failures gracefully', async ({ page }) => {
      // Mock WebSocket connection failure
      await page.addInitScript(() => {
        class MockWebSocket {
          constructor(url) {
            this.url = url
            this.readyState = WebSocket.CONNECTING
            setTimeout(() => {
              this.readyState = WebSocket.CLOSED
              if (this.onerror) {
                this.onerror(new Error('Connection failed'))
              }
              if (this.onclose) {
                this.onclose({ code: 1006, reason: 'Connection failed' })
              }
            }, 100)
          }

          send(data) {}
          close() {}
        }

        window.WebSocket = MockWebSocket
      })

      // Login as student
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testStudent1.email)
      await page.fill('input[type="password"]', testStudent1.password)
      await page.click('button[type="submit"]')

      // Navigate to course dashboard
      await page.goto('/courses/course-1/dashboard')

      // Should show connection error message
      await expect(page.locator('text=Connection lost')).toBeVisible({ timeout: 5000 })
      await expect(page.locator('text=Trying to reconnect...')).toBeVisible()
      
      // Should show retry button
      await expect(page.locator('button:has-text("Retry Connection")')).toBeVisible()
    })

    test('instructor can broadcast messages to all participants', async ({ page }) => {
      // Mock WebSocket for broadcasting
      await page.addInitScript(() => {
        class MockWebSocket {
          constructor(url) {
            this.url = url
            this.readyState = WebSocket.CONNECTING
            setTimeout(() => {
              this.readyState = WebSocket.OPEN
              if (this.onopen) this.onopen()
            }, 100)
          }

          send(data) {
            const message = JSON.parse(data)
            if (message.type === 'broadcast_message') {
              // Simulate message broadcast confirmation
              setTimeout(() => {
                if (this.onmessage) {
                  this.onmessage({
                    data: JSON.stringify({
                      type: 'message_broadcast_success',
                      data: {
                        message: message.data.message,
                        timestamp: new Date().toISOString(),
                        recipients: 15
                      }
                    })
                  })
                }
              }, 200)
            }
          }

          close() {
            this.readyState = WebSocket.CLOSED
            if (this.onclose) this.onclose()
          }
        }

        window.WebSocket = MockWebSocket
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to live class control panel
      await page.goto('/live-classes/live-class-1/control')

      // Should show broadcast message interface
      await expect(page.locator('[data-testid="broadcast-panel"]')).toBeVisible()
      
      // Send broadcast message
      await page.fill('textarea[data-testid="broadcast-message"]', 'Welcome everyone! Please turn on your cameras.')
      await page.click('button[data-testid="send-broadcast"]')

      // Should show success confirmation
      await expect(page.locator('text=Message sent to 15 participants')).toBeVisible({ timeout: 3000 })
      
      // Should show message in broadcast history
      await expect(page.locator('text=Welcome everyone! Please turn on your cameras.')).toBeVisible()
    })
  })

  test.describe('Complete Live Class Workflow Integration', () => {
    test('end-to-end live class workflow from creation to completion', async ({ page }) => {
      // Mock all required APIs for complete workflow
      await page.route('**/api/v1/courses/live-classes/', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 201,
            contentType: 'application/json',
            body: JSON.stringify({
              id: 'live-class-e2e',
              ...testLiveClass,
              zoom_meeting_id: mockZoomMeetingResponse.id,
              join_url: mockZoomMeetingResponse.join_url,
              start_url: mockZoomMeetingResponse.start_url,
              status: 'scheduled'
            })
          })
        }
      })

      await page.route('**/api/v1/courses/live-classes/live-class-e2e/start/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            message: 'Live class started successfully',
            status: 'live'
          })
        })
      })

      await page.route('**/api/v1/courses/live-classes/live-class-e2e/end/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            message: 'Live class ended successfully',
            status: 'completed',
            attendance_summary: {
              total_students: 25,
              attended: 22,
              attendance_rate: 88.0
            }
          })
        })
      })

      await page.route('**/api/v1/classes/attendance/class_report/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            live_class: {
              id: 'live-class-e2e',
              title: testLiveClass.title,
              duration_minutes: testLiveClass.duration
            },
            metrics: {
              total_students: 25,
              attendance_rate: 88.0,
              average_duration: 52.5,
              engagement_score: 82.3,
              status_breakdown: {
                present: 20,
                late: 2,
                absent: 3,
                partial: 0
              }
            },
            recommendations: [
              {
                type: 'engagement',
                message: 'Excellent attendance rate! Students are highly engaged.',
                priority: 'low'
              }
            ]
          })
        })
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Step 1: Create live class
      await page.goto('/live-classes/create')
      await page.fill('input[id="title"]', testLiveClass.title)
      await page.fill('textarea[id="description"]', testLiveClass.description)
      await page.fill('input[id="duration_minutes"]', testLiveClass.duration.toString())
      await page.check('input[id="enable_zoom"]')
      await page.click('button[type="submit"]')

      // Should show creation success
      await expect(page.locator('text=Live class scheduled successfully')).toBeVisible({ timeout: 10000 })

      // Step 2: Start the class
      await page.goto('/live-classes/live-class-e2e/control')
      await page.click('button[data-testid="start-class"]')

      // Should show class started confirmation
      await expect(page.locator('text=Live class started successfully')).toBeVisible({ timeout: 5000 })
      await expect(page.locator('text=Status: Live')).toBeVisible()

      // Should show instructor controls
      await expect(page.locator('[data-testid="instructor-controls"]')).toBeVisible()
      await expect(page.locator('button:has-text("End Class")')).toBeVisible()
      await expect(page.locator('[data-testid="participant-list"]')).toBeVisible()

      // Step 3: Monitor class progress
      await expect(page.locator('[data-testid="live-metrics"]')).toBeVisible()
      await expect(page.locator('text=Participants: 0')).toBeVisible()

      // Step 4: End the class
      await page.click('button:has-text("End Class")')
      await page.click('button:has-text("Confirm End Class")')  // Confirmation dialog

      // Should show class ended confirmation
      await expect(page.locator('text=Live class ended successfully')).toBeVisible({ timeout: 5000 })
      await expect(page.locator('text=Attendance Rate: 88%')).toBeVisible()

      // Step 5: View final report
      await page.click('button:has-text("View Full Report")')

      // Should show comprehensive report
      await expect(page.locator('h1:has-text("Class Report")')).toBeVisible()
      await expect(page.locator('text=Total Students: 25')).toBeVisible()
      await expect(page.locator('text=Attendance Rate: 88%')).toBeVisible()
      await expect(page.locator('text=Engagement Score: 82.3')).toBeVisible()
      await expect(page.locator('text=Excellent attendance rate!')).toBeVisible()

      // Should show visual analytics
      await expect(page.locator('[data-testid="attendance-chart"]')).toBeVisible()
      await expect(page.locator('[data-testid="engagement-visualization"]')).toBeVisible()
    })

    test('student experience throughout live class lifecycle', async ({ page }) => {
      // Mock student enrollment and class data
      await page.route('**/api/v1/courses/course-1/enrollment/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            is_enrolled: true,
            enrollment_status: 'active'
          })
        })
      })

      await page.route('**/api/v1/courses/course-1/live-classes/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            upcoming_classes: [
              {
                id: 'live-class-student',
                title: testLiveClass.title,
                scheduled_at: testLiveClass.scheduledAt,
                status: 'scheduled',
                join_url: mockZoomMeetingResponse.join_url
              }
            ],
            past_classes: []
          })
        })
      })

      // Mock real-time updates for student
      await page.addInitScript(() => {
        class MockWebSocket {
          constructor(url) {
            this.url = url
            this.readyState = WebSocket.CONNECTING
            setTimeout(() => {
              this.readyState = WebSocket.OPEN
              if (this.onopen) this.onopen()
              
              // Simulate class starting notification
              setTimeout(() => {
                if (this.onmessage) {
                  this.onmessage({
                    data: JSON.stringify({
                      type: 'class_status_update',
                      data: {
                        class_id: 'live-class-student',
                        status: 'live',
                        message: 'Your class has started! Join now.',
                        join_url: 'https://zoom.us/j/123456789'
                      }
                    })
                  })
                }
              }, 1000)
            }, 100)
          }

          send(data) {}
          close() {}
        }

        window.WebSocket = MockWebSocket
      })

      // Login as student
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testStudent1.email)
      await page.fill('input[type="password"]', testStudent1.password)
      await page.click('button[type="submit"]')

      // Navigate to course dashboard
      await page.goto('/courses/course-1/dashboard')

      // Should show upcoming live class
      await expect(page.locator('text=Upcoming Live Classes')).toBeVisible()
      await expect(page.locator(`text=${testLiveClass.title}`)).toBeVisible()
      await expect(page.locator('text=Scheduled')).toBeVisible()

      // Wait for class to start (real-time notification)
      await expect(page.locator('text=Your class has started! Join now.')).toBeVisible({ timeout: 5000 })

      // Should show join button
      const joinButton = page.locator('button:has-text("Join Live Class")')
      await expect(joinButton).toBeVisible()
      await expect(joinButton).toHaveAttribute('data-zoom-url', mockZoomMeetingResponse.join_url)

      // Click join button (would open Zoom in real scenario)
      await joinButton.click()

      // Should show joining confirmation
      await expect(page.locator('text=Joining live class...')).toBeVisible()
      await expect(page.locator('text=You will be redirected to Zoom')).toBeVisible()
    })

    test('handles error scenarios gracefully throughout workflow', async ({ page }) => {
      // Mock various error scenarios
      let requestCount = 0
      
      await page.route('**/api/v1/courses/live-classes/', async route => {
        requestCount++
        if (requestCount === 1) {
          // First request fails
          await route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({
              error: 'Zoom API temporarily unavailable'
            })
          })
        } else {
          // Retry succeeds
          await route.fulfill({
            status: 201,
            contentType: 'application/json',
            body: JSON.stringify({
              id: 'live-class-retry',
              ...testLiveClass,
              status: 'scheduled'
            })
          })
        }
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Try to create live class
      await page.goto('/live-classes/create')
      await page.fill('input[id="title"]', testLiveClass.title)
      await page.fill('textarea[id="description"]', testLiveClass.description)
      await page.check('input[id="enable_zoom"]')
      await page.click('button[type="submit"]')

      // Should show error message
      await expect(page.locator('text=Zoom API temporarily unavailable')).toBeVisible({ timeout: 10000 })
      
      // Should show retry option
      await expect(page.locator('button:has-text("Retry")')).toBeVisible()
      
      // Click retry
      await page.click('button:has-text("Retry")')
      
      // Should succeed on retry
      await expect(page.locator('text=Live class scheduled successfully')).toBeVisible({ timeout: 10000 })
    })
  })

  test.describe('Performance and Load Testing', () => {
    test('handles multiple concurrent users during live class', async ({ page, context }) => {
      // Create multiple browser contexts to simulate concurrent users
      const contexts = []
      const pages = []
      
      for (let i = 0; i < 5; i++) {
        const newContext = await context.browser().newContext()
        const newPage = await newContext.newPage()
        contexts.push(newContext)
        pages.push(newPage)
      }

      // Mock WebSocket for all pages
      for (const testPage of pages) {
        await testPage.addInitScript(() => {
          class MockWebSocket {
            constructor(url) {
              this.url = url
              this.readyState = WebSocket.CONNECTING
              setTimeout(() => {
                this.readyState = WebSocket.OPEN
                if (this.onopen) this.onopen()
              }, Math.random() * 500) // Random delay to simulate real conditions
            }

            send(data) {}
            close() {}
          }

          window.WebSocket = MockWebSocket
        })
      }

      // Login all users concurrently
      const loginPromises = pages.map(async (testPage, index) => {
        await testPage.goto('/')
        await testPage.click('text=Sign In')
        await testPage.fill('input[type="email"]', `student${index + 1}@test.com`)
        await testPage.fill('input[type="password"]', 'testpass123')
        await testPage.click('button[type="submit"]')
        return testPage.goto('/courses/course-1/dashboard')
      })

      // Wait for all logins to complete
      await Promise.all(loginPromises)

      // Verify all pages loaded successfully
      for (const testPage of pages) {
        await expect(testPage.locator('text=Dashboard')).toBeVisible({ timeout: 10000 })
      }

      // Clean up
      for (const ctx of contexts) {
        await ctx.close()
      }
    })

    test('measures page load performance for live class interface', async ({ page }) => {
      // Start performance measurement
      await page.goto('/')
      
      // Login
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Measure live class control panel load time
      const startTime = Date.now()
      await page.goto('/live-classes/live-class-1/control')
      await expect(page.locator('h1:has-text("Live Class Control")')).toBeVisible()
      const loadTime = Date.now() - startTime

      // Verify performance requirement (should load within 2 seconds)
      expect(loadTime).toBeLessThan(2000)

      // Verify Three.js visualizations load
      await expect(page.locator('[data-testid="3d-visualization"]')).toBeVisible({ timeout: 3000 })
      
      // Verify animations are smooth (no specific assertion, but ensures components render)
      await expect(page.locator('[data-testid="animated-metrics"]')).toBeVisible()
    })
  })
})rted! Join now.')).toBeVisible({ timeout: 5000 })
      await expect(page.locator('button:has-text("Join Live Class")')).toBeVisible()

      // Should show animated notification
      const notification = page.locator('[data-testid="live-class-notification"]')
      await expect(notification).toHaveClass(/animate-pulse/)
    })

    test('handles WebSocket connection failures gracefully', async ({ page }) => {
      // Mock failing WebSocket
      await page.addInitScript(() => {
        class MockWebSocket {
          constructor(url) {
            this.url = url
            this.readyState = WebSocket.CONNECTING
            setTimeout(() => {
              this.readyState = WebSocket.CLOSED
              if (this.onerror) this.onerror(new Error('Connection failed'))
              if (this.onclose) this.onclose()
            }, 100)
          }

          send(data) {}
          close() {}
        }

        window.WebSocket = MockWebSocket
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to live class control
      await page.goto('/live-classes/live-class-1/control')

      // Should show connection error and fallback to polling
      await expect(page.locator('text=Real-time updates unavailable')).toBeVisible({ timeout: 5000 })
      await expect(page.locator('text=Refreshing every 30 seconds')).toBeVisible()
      await expect(page.locator('button:has-text("Refresh Now")')).toBeVisible()
    })

    test('displays Three.js visualizations for real-time engagement', async ({ page }) => {
      // Mock real-time engagement data
      await page.route('**/api/v1/classes/attendance/live-metrics/live-class-1/', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            current_participants: 15,
            engagement_level: 78,
            participation_rate: 65,
            attention_score: 82,
            interaction_points: [
              { timestamp: '10:05', participants: 12, engagement: 75 },
              { timestamp: '10:10', participants: 15, engagement: 80 },
              { timestamp: '10:15', participants: 14, engagement: 78 }
            ]
          })
        })
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to live analytics
      await page.goto('/live-classes/live-class-1/live-analytics')

      // Should show Three.js engagement visualization
      await expect(page.locator('[data-testid="engagement-3d-viz"]')).toBeVisible()
      await expect(page.locator('canvas')).toBeVisible() // Three.js canvas

      // Should show real-time metrics
      await expect(page.locator('text=Current Participants: 15')).toBeVisible()
      await expect(page.locator('text=Engagement Level: 78%')).toBeVisible()
      await expect(page.locator('text=Attention Score: 82%')).toBeVisible()

      // Should show animated metrics updates
      const engagementMeter = page.locator('[data-testid="engagement-meter"]')
      await expect(engagementMeter).toHaveClass(/animate-pulse/)
    })
  })

  test.describe('Error Handling and Edge Cases', () => {
    test('handles network failures during live class operations', async ({ page }) => {
      // Mock network failure
      await page.route('**/api/v1/classes/**', route => route.abort('failed'))

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Try to access live class
      await page.goto('/live-classes/live-class-1/control')

      // Should show error message
      await expect(page.locator('text=Unable to load live class')).toBeVisible({ timeout: 10000 })
      await expect(page.locator('button:has-text("Retry")')).toBeVisible()
    })

    test('validates live class scheduling constraints', async ({ page }) => {
      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to create live class
      await page.goto('/live-classes/create')

      // Try to schedule class in the past
      const pastDate = new Date(Date.now() - 24 * 60 * 60 * 1000) // Yesterday
      await page.fill('input[id="title"]', 'Past Class')
      await page.fill('input[type="datetime-local"]', pastDate.toISOString().slice(0, 16))
      await page.click('button[type="submit"]')

      // Should show validation error
      await expect(page.locator('text=Cannot schedule class in the past')).toBeVisible()

      // Try to schedule overlapping class
      const futureDate = new Date(Date.now() + 2 * 60 * 60 * 1000)
      await page.fill('input[type="datetime-local"]', futureDate.toISOString().slice(0, 16))
      await page.fill('input[id="duration_minutes"]', '120') // 2 hours
      await page.click('button[type="submit"]')

      // Should show overlap warning if there's a conflict
      // This would depend on existing scheduled classes
    })
  })

  test.describe('Performance and Accessibility', () => {
    test('live class interface loads within acceptable time', async ({ page }) => {
      const startTime = Date.now()

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to live class control
      await page.goto('/live-classes/live-class-1/control')
      await expect(page.locator('h1:has-text("Live Class Control")')).toBeVisible()

      const loadTime = Date.now() - startTime
      expect(loadTime).toBeLessThan(3000) // Should load within 3 seconds
    })

    test('live class interface is keyboard accessible', async ({ page }) => {
      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      await page.goto('/live-classes/live-class-1/control')

      // Test keyboard navigation
      await page.keyboard.press('Tab')
      await expect(page.locator('button:focus')).toBeVisible()

      // Test keyboard shortcuts
      await page.keyboard.press('Space') // Should activate focused button
      
      // Test ARIA labels
      const startButton = page.locator('button:has-text("Start Class")')
      await expect(startButton).toHaveAttribute('aria-label')
    })

    test('Three.js visualizations perform well with real-time data', async ({ page }) => {
      // Mock high-frequency data updates
      await page.route('**/api/v1/classes/attendance/live-metrics/**', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            current_participants: Math.floor(Math.random() * 50) + 10,
            engagement_level: Math.floor(Math.random() * 40) + 60,
            participation_rate: Math.floor(Math.random() * 30) + 50
          })
        })
      })

      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      await page.goto('/live-classes/live-class-1/live-analytics')

      // Monitor performance
      const performanceEntries = await page.evaluate(() => {
        return performance.getEntriesByType('measure')
      })

      // Should maintain smooth frame rate
      const canvas = page.locator('canvas')
      await expect(canvas).toBeVisible()

      // Test that animations don't cause performance issues
      await page.waitForTimeout(5000) // Let it run for 5 seconds
      
      // Check that the page is still responsive
      await expect(page.locator('button:has-text("Refresh")')).toBeVisible()
    })
  })
})