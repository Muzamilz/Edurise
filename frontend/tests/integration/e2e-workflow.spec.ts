/**
 * End-to-end workflow integration tests for centralized API endpoints.
 * Tests complete user workflows from frontend through centralized API.
 * Requirement: 11.2 - Complete workflow verification through centralized API
 */

import { test, expect } from '@playwright/test'

test.describe('E2E Workflow Integration Tests', () => {
  // Mock centralized API responses
  test.beforeEach(async ({ page }) => {
    // Mock authentication endpoints
    await page.route('**/api/v1/accounts/auth/login/', async route => {
      if (route.request().method() === 'POST') {
        const requestBody = JSON.parse(route.request().postData() || '{}')
        
        if (requestBody.email === 'student@e2etest.com' && requestBody.password === 'TestPass123!') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              user: {
                id: '1',
                email: 'student@e2etest.com',
                first_name: 'E2E',
                last_name: 'Student',
                is_teacher: false,
                is_approved_teacher: false,
                is_staff: false,
                is_superuser: false
              },
              tokens: {
                access: 'mock-student-access-token',
                refresh: 'mock-student-refresh-token'
              }
            })
          })
        } else if (requestBody.email === 'teacher@e2etest.com' && requestBody.password === 'TestPass123!') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              user: {
                id: '2',
                email: 'teacher@e2etest.com',
                first_name: 'E2E',
                last_name: 'Teacher',
                is_teacher: true,
                is_approved_teacher: true,
                is_staff: false,
                is_superuser: false
              },
              tokens: {
                access: 'mock-teacher-access-token',
                refresh: 'mock-teacher-refresh-token'
              }
            })
          })
        }
      }
    })

    // Mock course endpoints
    await page.route('**/api/v1/courses/', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: [
              {
                id: 'course-1',
                title: 'E2E Test Course',
                description: 'Complete E2E testing course',
                instructor: {
                  id: '2',
                  first_name: 'E2E',
                  last_name: 'Teacher'
                },
                price: '99.99',
                category: 'technology',
                is_public: true,
                duration_weeks: 8,
                average_rating: 4.8,
                total_enrollments: 150,
                created_at: '2024-01-01T00:00:00Z'
              }
            ],
            meta: {
              pagination: {
                count: 1,
                page: 1,
                pages: 1,
                page_size: 20
              }
            }
          })
        })
      } else if (route.request().method() === 'POST') {
        const requestBody = JSON.parse(route.request().postData() || '{}')
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              id: 'new-course-1',
              title: requestBody.title,
              description: requestBody.description,
              price: requestBody.price,
              category: requestBody.category,
              is_public: requestBody.is_public,
              duration_weeks: requestBody.duration_weeks,
              instructor: {
                id: '2',
                first_name: 'E2E',
                last_name: 'Teacher'
              }
            }
          })
        })
      }
    })

    // Mock course detail endpoint
    await page.route('**/api/v1/courses/course-1/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            id: 'course-1',
            title: 'E2E Test Course',
            description: 'Complete E2E testing course with detailed content',
            instructor: {
              id: '2',
              first_name: 'E2E',
              last_name: 'Teacher',
              bio: 'Experienced instructor'
            },
            price: '99.99',
            category: 'technology',
            is_public: true,
            duration_weeks: 8,
            average_rating: 4.8,
            total_enrollments: 150,
            modules: [
              {
                id: 'module-1',
                title: 'Introduction to E2E Testing',
                description: 'Basic concepts',
                order: 1,
                is_published: true
              }
            ],
            reviews: [
              {
                id: 'review-1',
                student: { first_name: 'Test', last_name: 'User' },
                rating: 5,
                comment: 'Excellent course!',
                created_at: '2024-01-01T00:00:00Z'
              }
            ]
          }
        })
      })
    })

    // Mock enrollment endpoints
    await page.route('**/api/v1/enrollments/', async route => {
      if (route.request().method() === 'POST') {
        const requestBody = JSON.parse(route.request().postData() || '{}')
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              id: 'enrollment-1',
              student: { id: '1', first_name: 'E2E', last_name: 'Student' },
              course: { id: requestBody.course, title: 'E2E Test Course' },
              status: 'active',
              progress_percentage: 0,
              enrolled_at: new Date().toISOString()
            }
          })
        })
      } else if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: [
              {
                id: 'enrollment-1',
                course: {
                  id: 'course-1',
                  title: 'E2E Test Course',
                  instructor: { first_name: 'E2E', last_name: 'Teacher' }
                },
                status: 'active',
                progress_percentage: 45,
                enrolled_at: '2024-01-01T00:00:00Z'
              }
            ]
          })
        })
      }
    })

    // Mock live class endpoints
    await page.route('**/api/v1/live-classes/', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: [
              {
                id: 'live-class-1',
                course: {
                  id: 'course-1',
                  title: 'E2E Test Course'
                },
                title: 'Interactive E2E Session',
                description: 'Live coding session',
                scheduled_at: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2 hours from now
                duration_minutes: 90,
                status: 'scheduled',
                join_url: 'https://zoom.us/j/123456789'
              }
            ]
          })
        })
      } else if (route.request().method() === 'POST') {
        const requestBody = JSON.parse(route.request().postData() || '{}')
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              id: 'new-live-class-1',
              course: { id: requestBody.course },
              title: requestBody.title,
              description: requestBody.description,
              scheduled_at: requestBody.scheduled_at,
              duration_minutes: requestBody.duration_minutes,
              status: 'scheduled',
              join_url: 'https://zoom.us/j/987654321'
            }
          })
        })
      }
    })

    // Mock payment endpoints
    await page.route('**/api/v1/payments/payments/create_course_payment/', async route => {
      if (route.request().method() === 'POST') {
        const requestBody = JSON.parse(route.request().postData() || '{}')
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              payment_id: 'payment-1',
              client_secret: 'pi_test_client_secret',
              amount: requestBody.amount,
              currency: requestBody.currency || 'USD',
              status: 'pending'
            }
          })
        })
      }
    })

    await page.route('**/api/v1/payments/payments/payment-1/confirm_payment/', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            message: 'Payment confirmed successfully',
            data: {
              payment_id: 'payment-1',
              status: 'completed',
              completed_at: new Date().toISOString()
            }
          })
        })
      }
    })

    // Mock file upload endpoints
    await page.route('**/api/v1/files/uploads/', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              id: 'file-upload-1',
              original_filename: 'test_document.pdf',
              title: 'Course Material',
              description: 'Important course document',
              file_size: 1024,
              content_type: 'application/pdf',
              is_public: true,
              uploaded_at: new Date().toISOString()
            }
          })
        })
      } else if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: [
              {
                id: 'file-upload-1',
                original_filename: 'course_syllabus.pdf',
                title: 'Course Syllabus',
                description: 'Detailed course syllabus',
                file_size: 2048,
                content_type: 'application/pdf',
                is_public: true,
                uploaded_at: '2024-01-01T00:00:00Z'
              }
            ]
          })
        })
      }
    })

    // Mock certificate endpoints
    await page.route('**/api/v1/assignments/certificates/generate/', async route => {
      if (route.request().method() === 'POST') {
        const requestBody = JSON.parse(route.request().postData() || '{}')
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              id: 'certificate-1',
              certificate_number: 'CERT-E2E12345',
              course: { id: requestBody.course_id, title: 'E2E Test Course' },
              student: { first_name: 'E2E', last_name: 'Student' },
              issued_at: new Date().toISOString(),
              is_valid: true
            }
          })
        })
      }
    })

    await page.route('**/api/v1/assignments/certificates/', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: [
              {
                id: 'certificate-1',
                certificate_number: 'CERT-E2E12345',
                course: { title: 'E2E Test Course' },
                issued_at: '2024-01-01T00:00:00Z',
                is_valid: true
              }
            ]
          })
        })
      }
    })

    // Mock dashboard endpoints
    await page.route('**/api/v1/dashboard/student/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            enrolled_courses: [
              {
                id: 'course-1',
                title: 'E2E Test Course',
                progress_percentage: 45,
                instructor: { first_name: 'E2E', last_name: 'Teacher' }
              }
            ],
            completed_courses: [],
            total_hours: 15,
            certificates: [],
            current_courses: [
              {
                id: 'course-1',
                title: 'E2E Test Course',
                next_lesson: 'Introduction to Testing'
              }
            ],
            recommendations: []
          }
        })
      })
    })

    await page.route('**/api/v1/dashboard/teacher/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            instructor_info: {
              total_courses: 5,
              total_students: 150,
              average_rating: 4.8
            },
            overview_stats: {
              active_courses: 3,
              pending_reviews: 2,
              upcoming_classes: 1
            },
            recent_enrollments: [
              {
                student: { first_name: 'E2E', last_name: 'Student' },
                course: { title: 'E2E Test Course' },
                enrolled_at: '2024-01-01T00:00:00Z'
              }
            ],
            course_performance: [],
            upcoming_classes: [
              {
                id: 'live-class-1',
                title: 'Interactive E2E Session',
                scheduled_at: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString()
              }
            ],
            enrollment_trend: []
          }
        })
      })
    })

    // Navigate to the application
    await page.goto('/')
  })

  test('complete student learning workflow', async ({ page }) => {
    // Step 1: Student Login
    await page.goto('/auth/login')
    await page.fill('[data-testid="email"]', 'student@e2etest.com')
    await page.fill('[data-testid="password"]', 'TestPass123!')
    await page.click('[data-testid="login-button"]')

    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard')

    // Step 2: View Dashboard with Real Data
    await expect(page.locator('[data-testid="enrolled-courses-count"]')).toContainText('1')
    await expect(page.locator('[data-testid="total-hours"]')).toContainText('15')
    await expect(page.locator('[data-testid="current-course-title"]')).toContainText('E2E Test Course')

    // Step 3: Browse Available Courses
    await page.click('[data-testid="browse-courses"]')
    await expect(page).toHaveURL('/courses')

    // Should see courses from API
    await expect(page.locator('[data-testid="course-card"]')).toBeVisible()
    await expect(page.locator('[data-testid="course-title"]')).toContainText('E2E Test Course')
    await expect(page.locator('[data-testid="course-price"]')).toContainText('$99.99')

    // Step 4: View Course Details
    await page.click('[data-testid="course-card"]')
    await expect(page).toHaveURL('/courses/course-1')

    // Should show detailed course information
    await expect(page.locator('[data-testid="course-title"]')).toContainText('E2E Test Course')
    await expect(page.locator('[data-testid="instructor-name"]')).toContainText('E2E Teacher')
    await expect(page.locator('[data-testid="course-rating"]')).toContainText('4.8')
    await expect(page.locator('[data-testid="total-enrollments"]')).toContainText('150')

    // Should show course modules
    await expect(page.locator('[data-testid="module-title"]')).toContainText('Introduction to E2E Testing')

    // Should show course reviews
    await expect(page.locator('[data-testid="review-comment"]')).toContainText('Excellent course!')

    // Step 5: Enroll in Course (if not already enrolled)
    const enrollButton = page.locator('[data-testid="enroll-button"]')
    if (await enrollButton.isVisible()) {
      await enrollButton.click()
      
      // Should show enrollment success
      await expect(page.locator('[data-testid="enrollment-success"]')).toBeVisible()
    }

    // Step 6: Access Course Content
    await page.click('[data-testid="access-course"]')
    await expect(page).toHaveURL('/courses/course-1/learn')

    // Should show course learning interface
    await expect(page.locator('[data-testid="course-content"]')).toBeVisible()
    await expect(page.locator('[data-testid="progress-bar"]')).toBeVisible()

    // Step 7: View Live Classes
    await page.click('[data-testid="live-classes-tab"]')
    
    // Should show scheduled live classes
    await expect(page.locator('[data-testid="live-class-card"]')).toBeVisible()
    await expect(page.locator('[data-testid="live-class-title"]')).toContainText('Interactive E2E Session')
    await expect(page.locator('[data-testid="join-class-button"]')).toBeVisible()

    // Step 8: View Course Materials
    await page.click('[data-testid="materials-tab"]')
    
    // Should show uploaded course materials
    await expect(page.locator('[data-testid="material-item"]')).toBeVisible()
    await expect(page.locator('[data-testid="material-title"]')).toContainText('Course Syllabus')

    // Step 9: Complete Course and Get Certificate
    // Simulate course completion
    await page.evaluate(() => {
      // Mock course completion
      localStorage.setItem('course-progress', JSON.stringify({
        'course-1': { progress: 100, completed: true }
      }))
    })

    await page.reload()
    
    // Should show certificate generation option
    await expect(page.locator('[data-testid="generate-certificate"]')).toBeVisible()
    await page.click('[data-testid="generate-certificate"]')

    // Should show certificate generation success
    await expect(page.locator('[data-testid="certificate-generated"]')).toBeVisible()
    await expect(page.locator('[data-testid="certificate-number"]')).toContainText('CERT-E2E12345')

    // Step 10: View Certificates
    await page.goto('/certificates')
    
    // Should show earned certificates
    await expect(page.locator('[data-testid="certificate-card"]')).toBeVisible()
    await expect(page.locator('[data-testid="certificate-course"]')).toContainText('E2E Test Course')
  })

  test('complete teacher course management workflow', async ({ page }) => {
    // Step 1: Teacher Login
    await page.goto('/auth/login')
    await page.fill('[data-testid="email"]', 'teacher@e2etest.com')
    await page.fill('[data-testid="password"]', 'TestPass123!')
    await page.click('[data-testid="login-button"]')

    await expect(page).toHaveURL('/dashboard')

    // Step 2: View Teacher Dashboard
    await expect(page.locator('[data-testid="total-courses"]')).toContainText('5')
    await expect(page.locator('[data-testid="total-students"]')).toContainText('150')
    await expect(page.locator('[data-testid="average-rating"]')).toContainText('4.8')

    // Should show recent enrollments
    await expect(page.locator('[data-testid="recent-enrollment"]')).toBeVisible()
    await expect(page.locator('[data-testid="student-name"]')).toContainText('E2E Student')

    // Should show upcoming classes
    await expect(page.locator('[data-testid="upcoming-class"]')).toBeVisible()
    await expect(page.locator('[data-testid="class-title"]')).toContainText('Interactive E2E Session')

    // Step 3: Create New Course
    await page.click('[data-testid="create-course"]')
    await expect(page).toHaveURL('/courses/create')

    // Fill course creation form
    await page.fill('[data-testid="course-title"]', 'Advanced E2E Testing')
    await page.fill('[data-testid="course-description"]', 'Deep dive into E2E testing strategies')
    await page.fill('[data-testid="course-price"]', '149.99')
    await page.selectOption('[data-testid="course-category"]', 'technology')
    await page.fill('[data-testid="duration-weeks"]', '10')
    await page.check('[data-testid="is-public"]')

    // Submit course creation
    await page.click('[data-testid="create-course-button"]')

    // Should show course creation success
    await expect(page.locator('[data-testid="course-created"]')).toBeVisible()
    await expect(page).toHaveURL('/courses/new-course-1')

    // Step 4: Add Course Content
    await page.click('[data-testid="add-module"]')
    
    // Fill module form
    await page.fill('[data-testid="module-title"]', 'Advanced Testing Concepts')
    await page.fill('[data-testid="module-description"]', 'Learn advanced testing patterns')
    await page.click('[data-testid="save-module"]')

    // Should show module added
    await expect(page.locator('[data-testid="module-added"]')).toBeVisible()

    // Step 5: Upload Course Materials
    await page.click('[data-testid="upload-materials"]')
    
    // Mock file upload
    const fileInput = page.locator('[data-testid="file-input"]')
    await fileInput.setInputFiles({
      name: 'course_material.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('Mock PDF content')
    })

    await page.fill('[data-testid="file-title"]', 'Course Handbook')
    await page.fill('[data-testid="file-description"]', 'Comprehensive course handbook')
    await page.click('[data-testid="upload-button"]')

    // Should show upload success
    await expect(page.locator('[data-testid="upload-success"]')).toBeVisible()

    // Step 6: Schedule Live Class
    await page.click('[data-testid="schedule-class"]')
    
    // Fill live class form
    await page.fill('[data-testid="class-title"]', 'Advanced Testing Workshop')
    await page.fill('[data-testid="class-description"]', 'Hands-on testing workshop')
    
    // Set future date and time
    const futureDate = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 days from now
    await page.fill('[data-testid="scheduled-date"]', futureDate.toISOString().split('T')[0])
    await page.fill('[data-testid="scheduled-time"]', '14:00')
    await page.fill('[data-testid="duration"]', '120')

    await page.click('[data-testid="schedule-button"]')

    // Should show scheduling success
    await expect(page.locator('[data-testid="class-scheduled"]')).toBeVisible()

    // Step 7: View Course Analytics
    await page.click('[data-testid="view-analytics"]')
    
    // Should show analytics dashboard
    await expect(page.locator('[data-testid="analytics-dashboard"]')).toBeVisible()
    await expect(page.locator('[data-testid="enrollment-chart"]')).toBeVisible()
    await expect(page.locator('[data-testid="engagement-metrics"]')).toBeVisible()

    // Step 8: Manage Students
    await page.click('[data-testid="manage-students"]')
    
    // Should show student list
    await expect(page.locator('[data-testid="student-list"]')).toBeVisible()
    await expect(page.locator('[data-testid="student-progress"]')).toBeVisible()
  })

  test('complete payment and enrollment workflow', async ({ page }) => {
    // Step 1: Student Login
    await page.goto('/auth/login')
    await page.fill('[data-testid="email"]', 'student@e2etest.com')
    await page.fill('[data-testid="password"]', 'TestPass123!')
    await page.click('[data-testid="login-button"]')

    // Step 2: Browse and Select Course
    await page.goto('/courses')
    await page.click('[data-testid="course-card"]')
    await expect(page).toHaveURL('/courses/course-1')

    // Step 3: Initiate Payment
    await page.click('[data-testid="enroll-now"]')
    await expect(page).toHaveURL('/courses/course-1/checkout')

    // Should show payment form
    await expect(page.locator('[data-testid="payment-form"]')).toBeVisible()
    await expect(page.locator('[data-testid="course-price"]')).toContainText('$99.99')

    // Step 4: Fill Payment Information
    await page.selectOption('[data-testid="payment-method"]', 'stripe')
    
    // Mock Stripe elements
    await page.evaluate(() => {
      // Mock Stripe card element
      window.mockStripeCard = {
        mount: () => {},
        on: () => {},
        confirmPayment: () => Promise.resolve({ error: null })
      }
    })

    // Fill billing information
    await page.fill('[data-testid="billing-name"]', 'E2E Student')
    await page.fill('[data-testid="billing-email"]', 'student@e2etest.com')
    await page.fill('[data-testid="billing-address"]', '123 Test Street')
    await page.fill('[data-testid="billing-city"]', 'Test City')
    await page.fill('[data-testid="billing-zip"]', '12345')

    // Step 5: Process Payment
    await page.click('[data-testid="pay-now"]')

    // Should show payment processing
    await expect(page.locator('[data-testid="payment-processing"]')).toBeVisible()

    // Wait for payment confirmation
    await page.waitForTimeout(2000)

    // Should show payment success
    await expect(page.locator('[data-testid="payment-success"]')).toBeVisible()
    await expect(page.locator('[data-testid="enrollment-confirmed"]')).toBeVisible()

    // Step 6: Access Purchased Course
    await page.click('[data-testid="access-course"]')
    await expect(page).toHaveURL('/courses/course-1/learn')

    // Should show course content
    await expect(page.locator('[data-testid="course-content"]')).toBeVisible()
    await expect(page.locator('[data-testid="enrollment-status"]')).toContainText('Enrolled')

    // Step 7: View Payment History
    await page.goto('/profile/payments')
    
    // Should show payment record
    await expect(page.locator('[data-testid="payment-record"]')).toBeVisible()
    await expect(page.locator('[data-testid="payment-amount"]')).toContainText('$99.99')
    await expect(page.locator('[data-testid="payment-status"]')).toContainText('Completed')

    // Step 8: Download Invoice
    await page.click('[data-testid="download-invoice"]')
    
    // Should trigger download (mock)
    await expect(page.locator('[data-testid="download-started"]')).toBeVisible()
  })

  test('complete live class attendance workflow', async ({ page }) => {
    // Step 1: Student Login and Navigate to Live Classes
    await page.goto('/auth/login')
    await page.fill('[data-testid="email"]', 'student@e2etest.com')
    await page.fill('[data-testid="password"]', 'TestPass123!')
    await page.click('[data-testid="login-button"]')

    await page.goto('/live-classes')

    // Step 2: View Scheduled Classes
    await expect(page.locator('[data-testid="live-class-card"]')).toBeVisible()
    await expect(page.locator('[data-testid="class-title"]')).toContainText('Interactive E2E Session')
    await expect(page.locator('[data-testid="class-status"]')).toContainText('Scheduled')

    // Step 3: Join Live Class
    await page.click('[data-testid="join-class"]')
    
    // Should redirect to Zoom (mock)
    await expect(page.locator('[data-testid="joining-class"]')).toBeVisible()
    await expect(page.locator('[data-testid="zoom-redirect"]')).toBeVisible()

    // Mock returning from Zoom
    await page.evaluate(() => {
      // Simulate attendance tracking
      localStorage.setItem('class-attendance', JSON.stringify({
        'live-class-1': {
          joined_at: new Date().toISOString(),
          status: 'present'
        }
      }))
    })

    // Step 4: View Attendance Record
    await page.goto('/profile/attendance')
    
    // Should show attendance history
    await expect(page.locator('[data-testid="attendance-record"]')).toBeVisible()
    await expect(page.locator('[data-testid="class-attended"]')).toContainText('Interactive E2E Session')
    await expect(page.locator('[data-testid="attendance-status"]')).toContainText('Present')

    // Step 5: Teacher Views Attendance Report
    await page.goto('/auth/login')
    await page.fill('[data-testid="email"]', 'teacher@e2etest.com')
    await page.fill('[data-testid="password"]', 'TestPass123!')
    await page.click('[data-testid="login-button"]')

    await page.goto('/live-classes/live-class-1/attendance')
    
    // Should show attendance report
    await expect(page.locator('[data-testid="attendance-report"]')).toBeVisible()
    await expect(page.locator('[data-testid="student-attendance"]')).toBeVisible()
    await expect(page.locator('[data-testid="attendance-summary"]')).toBeVisible()
  })

  test('complete file upload and certificate workflow', async ({ page }) => {
    // Step 1: Teacher Login and Upload Course Material
    await page.goto('/auth/login')
    await page.fill('[data-testid="email"]', 'teacher@e2etest.com')
    await page.fill('[data-testid="password"]', 'TestPass123!')
    await page.click('[data-testid="login-button"]')

    await page.goto('/courses/course-1/materials')

    // Step 2: Upload File
    await page.click('[data-testid="upload-file"]')
    
    const fileInput = page.locator('[data-testid="file-input"]')
    await fileInput.setInputFiles({
      name: 'lesson_notes.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('Mock lesson notes content')
    })

    await page.fill('[data-testid="file-title"]', 'Lesson Notes')
    await page.fill('[data-testid="file-description"]', 'Detailed lesson notes and examples')
    await page.check('[data-testid="make-public"]')
    await page.click('[data-testid="upload-button"]')

    // Should show upload success
    await expect(page.locator('[data-testid="upload-success"]')).toBeVisible()
    await expect(page.locator('[data-testid="file-uploaded"]')).toContainText('Lesson Notes')

    // Step 3: Student Accesses File
    await page.goto('/auth/login')
    await page.fill('[data-testid="email"]', 'student@e2etest.com')
    await page.fill('[data-testid="password"]', 'TestPass123!')
    await page.click('[data-testid="login-button"]')

    await page.goto('/courses/course-1/materials')
    
    // Should see uploaded materials
    await expect(page.locator('[data-testid="material-item"]')).toBeVisible()
    await expect(page.locator('[data-testid="material-title"]')).toContainText('Lesson Notes')

    // Step 4: Download File
    await page.click('[data-testid="download-material"]')
    
    // Should trigger download
    await expect(page.locator('[data-testid="download-started"]')).toBeVisible()

    // Step 5: Complete Course and Generate Certificate
    // Mock course completion
    await page.evaluate(() => {
      localStorage.setItem('course-completion', JSON.stringify({
        'course-1': {
          completed: true,
          completion_date: new Date().toISOString(),
          final_grade: 95
        }
      }))
    })

    await page.goto('/courses/course-1')
    
    // Should show certificate option
    await expect(page.locator('[data-testid="generate-certificate"]')).toBeVisible()
    await page.click('[data-testid="generate-certificate"]')

    // Should show certificate generation
    await expect(page.locator('[data-testid="generating-certificate"]')).toBeVisible()
    
    // Wait for generation to complete
    await page.waitForTimeout(2000)
    
    // Should show certificate success
    await expect(page.locator('[data-testid="certificate-ready"]')).toBeVisible()
    await expect(page.locator('[data-testid="certificate-number"]')).toContainText('CERT-E2E12345')

    // Step 6: View and Download Certificate
    await page.click('[data-testid="view-certificate"]')
    
    // Should show certificate details
    await expect(page.locator('[data-testid="certificate-details"]')).toBeVisible()
    await expect(page.locator('[data-testid="student-name"]')).toContainText('E2E Student')
    await expect(page.locator('[data-testid="course-name"]')).toContainText('E2E Test Course')

    await page.click('[data-testid="download-certificate"]')
    
    // Should trigger PDF download
    await expect(page.locator('[data-testid="certificate-download"]')).toBeVisible()

    // Step 7: Share Certificate
    await page.click('[data-testid="share-certificate"]')
    await page.selectOption('[data-testid="share-platform"]', 'linkedin')
    await page.fill('[data-testid="share-message"]', 'Just completed an amazing course!')
    await page.click('[data-testid="share-button"]')

    // Should show sharing success
    await expect(page.locator('[data-testid="share-success"]')).toBeVisible()
  })

  test('error handling and recovery workflows', async ({ page }) => {
    // Test network error handling
    await page.route('**/api/v1/courses/', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          message: 'Internal server error'
        })
      })
    })

    await page.goto('/courses')
    
    // Should show error state
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible()
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible()

    // Test retry functionality
    await page.route('**/api/v1/courses/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: [],
          meta: { pagination: { count: 0, page: 1, pages: 1, page_size: 20 } }
        })
      })
    })

    await page.click('[data-testid="retry-button"]')
    
    // Should recover and show empty state
    await expect(page.locator('[data-testid="no-courses"]')).toBeVisible()

    // Test authentication error handling
    await page.route('**/api/v1/dashboard/student/', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          message: 'Authentication required'
        })
      })
    })

    await page.goto('/dashboard')
    
    // Should redirect to login
    await expect(page).toHaveURL('/auth/login')
    await expect(page.locator('[data-testid="auth-required"]')).toBeVisible()
  })
})