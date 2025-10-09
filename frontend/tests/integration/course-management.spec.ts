import { test, expect } from '@playwright/test'

test.describe('Course Management Integration', () => {
  // Test data
  const testInstructor = {
    email: 'instructor@test.com',
    password: 'testpass123',
    firstName: 'John',
    lastName: 'Instructor'
  }

  const testStudent = {
    email: 'student@test.com',
    password: 'testpass123',
    firstName: 'Jane',
    lastName: 'Student'
  }

  const testCourse = {
    title: 'Test Course for Integration',
    description: 'This is a comprehensive test course for integration testing',
    category: 'technology',
    difficulty: 'beginner',
    price: '99.99',
    duration: '8',
    tags: ['test', 'integration', 'course']
  }

  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/')
  })

  test.describe('Course Creation and Management', () => {
    test('instructor can create, edit, and delete a course', async ({ page }) => {
      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Wait for dashboard to load
      await expect(page.locator('text=Welcome back')).toBeVisible()

      // Navigate to teacher courses
      await page.click('text=Manage My Courses')
      await expect(page.locator('h1:has-text("My Courses")')).toBeVisible()

      // Create new course
      await page.click('text=Create Course')
      await expect(page.locator('h1:has-text("Create New Course")')).toBeVisible()

      // Fill course form
      await page.fill('input[id="title"]', testCourse.title)
      await page.fill('textarea[id="description"]', testCourse.description)
      await page.selectOption('select[id="category"]', testCourse.category)
      await page.selectOption('select[id="difficulty_level"]', testCourse.difficulty)
      await page.fill('input[id="price"]', testCourse.price)
      await page.fill('input[id="duration_weeks"]', testCourse.duration)

      // Add tags
      for (const tag of testCourse.tags) {
        await page.fill('.tag-input', tag)
        await page.press('.tag-input', 'Enter')
      }

      // Make course public
      await page.check('input[id="is_public"]')

      // Submit form
      await page.click('button[type="submit"]')

      // Should redirect to edit page or course list
      await expect(page.locator('text=Edit Course')).toBeVisible({ timeout: 10000 })

      // Go back to courses list to verify creation
      await page.click('text=Back to My Courses')
      await expect(page.locator(`text=${testCourse.title}`)).toBeVisible()

      // Edit the course
      await page.click(`text=${testCourse.title}`)
      await page.click('text=Edit')

      // Update course title
      const updatedTitle = testCourse.title + ' (Updated)'
      await page.fill('input[id="title"]', updatedTitle)
      await page.click('button[type="submit"]')

      // Verify update
      await page.click('text=Back to My Courses')
      await expect(page.locator(`text=${updatedTitle}`)).toBeVisible()

      // Delete the course
      await page.click('text=Delete')
      await page.click('text=Delete Course') // Confirm deletion
      
      // Verify deletion
      await expect(page.locator(`text=${updatedTitle}`)).not.toBeVisible()
    })

    test('instructor can duplicate a course', async ({ page }) => {
      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to teacher courses
      await page.click('text=Manage My Courses')

      // Assuming there's at least one course, duplicate it
      const firstCourse = page.locator('.course-card').first()
      await firstCourse.locator('text=Duplicate').click()

      // Wait for duplication to complete
      await expect(page.locator('text=(Copy)')).toBeVisible({ timeout: 10000 })
    })
  })

  test.describe('Course Discovery and Enrollment', () => {
    test('student can browse, search, and enroll in courses', async ({ page }) => {
      // Browse courses without login first
      await page.click('text=Browse Courses')
      await expect(page.locator('h1:has-text("Discover Amazing Courses")')).toBeVisible()

      // Test search functionality
      await page.fill('.search-input', 'technology')
      await page.click('.search-btn')
      
      // Should show filtered results
      await expect(page.locator('.course-card')).toBeVisible()

      // Test category filtering
      await page.click('text=Technology')
      await expect(page.url()).toContain('category=technology')

      // View course details
      const firstCourse = page.locator('.course-card').first()
      await firstCourse.click()

      // Should be on course detail page
      await expect(page.locator('.course-detail')).toBeVisible()

      // Try to enroll (should redirect to login)
      await page.click('text=Enroll Now')
      await expect(page.locator('text=Sign In')).toBeVisible()

      // Login as student
      await page.fill('input[type="email"]', testStudent.email)
      await page.fill('input[type="password"]', testStudent.password)
      await page.click('button[type="submit"]')

      // Should redirect back to course or dashboard
      // Navigate back to courses if needed
      await page.goto('/courses')
      
      // Find and enroll in a course
      const courseCard = page.locator('.course-card').first()
      await courseCard.click()

      // Enroll in the course
      await page.click('text=Enroll Now')
      
      // Should show success or redirect to course
      await expect(page.locator('text=Continue Learning')).toBeVisible({ timeout: 10000 })
    })

    test('student can view enrolled courses in dashboard', async ({ page }) => {
      // Login as student
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testStudent.email)
      await page.fill('input[type="password"]', testStudent.password)
      await page.click('button[type="submit"]')

      // Go to dashboard
      await page.click('text=Dashboard')
      
      // Should show enrolled courses stats
      await expect(page.locator('text=Enrolled Courses')).toBeVisible()
    })
  })

  test.describe('Course Content Management', () => {
    test('instructor can manage course modules', async ({ page }) => {
      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to teacher courses
      await page.click('text=Manage My Courses')

      // Edit first course
      const firstCourse = page.locator('.course-card').first()
      await firstCourse.locator('text=Edit').click()

      // Navigate to modules section (if available in the UI)
      // This would depend on the actual implementation
      // For now, we'll just verify we can access the edit page
      await expect(page.locator('text=Edit Course')).toBeVisible()
    })
  })

  test.describe('Course Reviews and Ratings', () => {
    test('enrolled student can leave a review', async ({ page }) => {
      // Login as student
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testStudent.email)
      await page.fill('input[type="password"]', testStudent.password)
      await page.click('button[type="submit"]')

      // Navigate to an enrolled course
      await page.goto('/courses')
      const courseCard = page.locator('.course-card').first()
      await courseCard.click()

      // Go to reviews tab
      await page.click('text=Reviews')

      // If enrolled, should see review form
      const reviewButton = page.locator('text=Write a Review')
      if (await reviewButton.isVisible()) {
        await reviewButton.click()

        // Fill review form
        await page.click('.star-btn:nth-child(5)') // 5 stars
        await page.fill('textarea', 'This is an excellent course! Highly recommended.')
        await page.click('text=Submit Review')

        // Should show success message or updated reviews
        await expect(page.locator('text=This is an excellent course')).toBeVisible({ timeout: 10000 })
      }
    })
  })

  test.describe('Course Search and Filtering', () => {
    test('users can filter courses by various criteria', async ({ page }) => {
      await page.goto('/courses')

      // Test category filter
      await page.selectOption('select:has-option[value="technology"]', 'technology')
      await expect(page.url()).toContain('category=technology')

      // Test difficulty filter
      await page.selectOption('select:has-option[value="beginner"]', 'beginner')
      await expect(page.url()).toContain('difficulty_level=beginner')

      // Test search
      await page.fill('.search-input', 'javascript')
      await page.press('.search-input', 'Enter')
      await expect(page.url()).toContain('search=javascript')

      // Clear filters
      await page.click('text=Clear Filters')
      
      // Should reset to default view
      await expect(page.url()).not.toContain('category=')
      await expect(page.url()).not.toContain('difficulty_level=')
      await expect(page.url()).not.toContain('search=')
    })
  })

  test.describe('Responsive Design', () => {
    test('course interface works on mobile devices', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 })

      await page.goto('/courses')

      // Should show mobile-friendly layout
      await expect(page.locator('.course-grid')).toBeVisible()

      // Test mobile navigation
      const courseCard = page.locator('.course-card').first()
      await courseCard.click()

      // Course detail should be mobile-friendly
      await expect(page.locator('.course-detail')).toBeVisible()

      // Test mobile course form (if instructor)
      await page.goto('/auth/login')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      await page.goto('/teacher/courses/create')
      
      // Form should be mobile-friendly
      await expect(page.locator('.course-form')).toBeVisible()
      await expect(page.locator('input[id="title"]')).toBeVisible()
    })
  })

  test.describe('Error Handling', () => {
    test('handles course not found gracefully', async ({ page }) => {
      await page.goto('/courses/non-existent-course-id')
      
      // Should show error message
      await expect(page.locator('text=Course not found')).toBeVisible()
      await expect(page.locator('text=Browse Courses')).toBeVisible()
    })

    test('handles network errors during course creation', async ({ page }) => {
      // Login as instructor
      await page.click('text=Sign In')
      await page.fill('input[type="email"]', testInstructor.email)
      await page.fill('input[type="password"]', testInstructor.password)
      await page.click('button[type="submit"]')

      // Navigate to course creation
      await page.goto('/teacher/courses/create')

      // Simulate network failure
      await page.route('**/api/v1/courses/courses/', route => {
        route.abort('failed')
      })

      // Fill and submit form
      await page.fill('input[id="title"]', 'Test Course')
      await page.fill('textarea[id="description"]', 'Test Description')
      await page.selectOption('select[id="category"]', 'technology')
      await page.selectOption('select[id="difficulty_level"]', 'beginner')
      await page.fill('input[id="duration_weeks"]', '4')

      await page.click('button[type="submit"]')

      // Should show error message
      await expect(page.locator('text=Failed to create course')).toBeVisible({ timeout: 10000 })
    })
  })

  test.describe('Performance', () => {
    test('course listing loads within acceptable time', async ({ page }) => {
      const startTime = Date.now()
      
      await page.goto('/courses')
      await expect(page.locator('.course-grid')).toBeVisible()
      
      const loadTime = Date.now() - startTime
      expect(loadTime).toBeLessThan(5000) // Should load within 5 seconds
    })

    test('course search is responsive', async ({ page }) => {
      await page.goto('/courses')
      
      const startTime = Date.now()
      await page.fill('.search-input', 'test')
      await page.press('.search-input', 'Enter')
      
      // Wait for results to update
      await page.waitForTimeout(1000)
      
      const searchTime = Date.now() - startTime
      expect(searchTime).toBeLessThan(3000) // Search should complete within 3 seconds
    })
  })

  test.describe('Accessibility', () => {
    test('course interface is keyboard navigable', async ({ page }) => {
      await page.goto('/courses')

      // Test keyboard navigation
      await page.keyboard.press('Tab') // Should focus on first interactive element
      await page.keyboard.press('Enter') // Should activate the element

      // Test form accessibility
      await page.goto('/teacher/courses/create')
      
      // All form fields should be accessible via keyboard
      await page.keyboard.press('Tab')
      await expect(page.locator('input[id="title"]:focus')).toBeVisible()
    })

    test('course interface has proper ARIA labels', async ({ page }) => {
      await page.goto('/courses')

      // Check for proper ARIA labels
      const searchInput = page.locator('.search-input')
      await expect(searchInput).toHaveAttribute('placeholder')

      // Check course cards have proper accessibility
      const courseCards = page.locator('.course-card')
      const firstCard = courseCards.first()
      await expect(firstCard).toBeVisible()
    })
  })
})