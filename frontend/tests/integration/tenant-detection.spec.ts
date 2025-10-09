import { test, expect } from '@playwright/test'

test.describe('Multi-Tenant Detection', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses for tenant detection
    await page.route('**/api/v1/accounts/organizations/by_subdomain/*', async route => {
      const url = new URL(route.request().url())
      const subdomain = url.searchParams.get('subdomain')
      
      if (subdomain === 'university-a') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: '1',
            name: 'University A',
            subdomain: 'university-a',
            primary_color: '#FF0000',
            secondary_color: '#AA0000',
            logo: null,
            subscription_plan: 'pro'
          })
        })
      } else if (subdomain === 'school-b') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: '2',
            name: 'School B',
            subdomain: 'school-b',
            primary_color: '#00FF00',
            secondary_color: '#00AA00',
            logo: null,
            subscription_plan: 'basic'
          })
        })
      } else {
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Organization not found' })
        })
      }
    })
  })

  test('should detect tenant from subdomain and apply branding', async ({ page }) => {
    // Visit with university-a subdomain
    await page.goto('http://university-a.localhost:3000')
    
    // Wait for tenant detection to complete
    await page.waitForTimeout(1000)
    
    // Check if tenant branding is applied
    const rootElement = page.locator('html')
    const primaryColor = await rootElement.evaluate(el => 
      getComputedStyle(el).getPropertyValue('--primary-color')
    )
    
    // Should apply University A's primary color
    expect(primaryColor.trim()).toBe('#FF0000')
    
    // Check if organization name is displayed
    await expect(page.locator('text=University A')).toBeVisible()
  })

  test('should apply different branding for different tenants', async ({ page }) => {
    // Visit with school-b subdomain
    await page.goto('http://school-b.localhost:3000')
    
    await page.waitForTimeout(1000)
    
    // Check School B branding
    const rootElement = page.locator('html')
    const primaryColor = await rootElement.evaluate(el => 
      getComputedStyle(el).getPropertyValue('--primary-color')
    )
    
    expect(primaryColor.trim()).toBe('#00FF00')
    await expect(page.locator('text=School B')).toBeVisible()
  })

  test('should handle invalid subdomain gracefully', async ({ page }) => {
    // Visit with non-existent subdomain
    await page.goto('http://invalid.localhost:3000')
    
    await page.waitForTimeout(1000)
    
    // Should fall back to default branding
    const rootElement = page.locator('html')
    const primaryColor = await rootElement.evaluate(el => 
      getComputedStyle(el).getPropertyValue('--primary-color')
    )
    
    // Should use default primary color
    expect(primaryColor.trim()).toBe('#3b82f6')
    
    // Should show default app name
    await expect(page.locator('text=Edurise')).toBeVisible()
  })

  test('should isolate tenant data in course listings', async ({ page }) => {
    // Mock course API responses for different tenants
    await page.route('**/api/v1/courses/courses/', async route => {
      const host = route.request().headers()['host'] || ''
      
      if (host.includes('university-a')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            results: [
              {
                id: '1',
                title: 'University A Course 1',
                description: 'Course for University A',
                instructor_name: 'Prof. Smith',
                price: '100.00'
              }
            ]
          })
        })
      } else if (host.includes('school-b')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            results: [
              {
                id: '2',
                title: 'School B Course 1',
                description: 'Course for School B',
                instructor_name: 'Teacher Jones',
                price: '150.00'
              }
            ]
          })
        })
      }
    })

    // Test University A sees only their courses
    await page.goto('http://university-a.localhost:3000/courses')
    await expect(page.locator('text=University A Course 1')).toBeVisible()
    await expect(page.locator('text=School B Course 1')).not.toBeVisible()

    // Test School B sees only their courses
    await page.goto('http://school-b.localhost:3000/courses')
    await expect(page.locator('text=School B Course 1')).toBeVisible()
    await expect(page.locator('text=University A Course 1')).not.toBeVisible()
  })

  test('should persist tenant context across navigation', async ({ page }) => {
    await page.goto('http://university-a.localhost:3000')
    
    // Navigate to different pages
    await page.click('text=Courses')
    await page.waitForURL('**/courses')
    
    // Tenant branding should persist
    await expect(page.locator('text=University A')).toBeVisible()
    
    await page.click('text=About')
    await page.waitForURL('**/about')
    
    // Still should show University A branding
    await expect(page.locator('text=University A')).toBeVisible()
  })

  test('should handle tenant switching correctly', async ({ page }) => {
    // Start with University A
    await page.goto('http://university-a.localhost:3000')
    await expect(page.locator('text=University A')).toBeVisible()
    
    // Switch to School B
    await page.goto('http://school-b.localhost:3000')
    await page.waitForTimeout(1000)
    
    // Should now show School B branding
    await expect(page.locator('text=School B')).toBeVisible()
    await expect(page.locator('text=University A')).not.toBeVisible()
  })
})