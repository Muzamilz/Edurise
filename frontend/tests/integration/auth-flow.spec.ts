import { test, expect } from '@playwright/test'

test.describe('Authentication Flow Integration Tests', () => {
  // Mock API responses for authentication endpoints
  test.beforeEach(async ({ page }) => {
    // Mock successful registration
    await page.route('**/api/v1/accounts/auth/register/', async route => {
      if (route.request().method() === 'POST') {
        const requestBody = JSON.parse(route.request().postData() || '{}')
        
        if (requestBody.email === 'john.doe@example.com') {
          await route.fulfill({
            status: 201,
            contentType: 'application/json',
            body: JSON.stringify({
              user: {
                id: '1',
                email: 'john.doe@example.com',
                first_name: 'John',
                last_name: 'Doe',
                is_teacher: false,
                is_approved_teacher: false,
                is_staff: false,
                is_superuser: false,
                date_joined: '2024-01-01T00:00:00Z',
                last_login: null
              },
              tokens: {
                access: 'mock-access-token-12345',
                refresh: 'mock-refresh-token-67890'
              }
            })
          })
        } else {
          await route.fulfill({
            status: 400,
            contentType: 'application/json',
            body: JSON.stringify({
              message: 'Registration failed',
              errors: { email: ['User with this email already exists'] }
            })
          })
        }
      }
    })

    // Mock successful login
    await page.route('**/api/v1/accounts/auth/login/', async route => {
      if (route.request().method() === 'POST') {
        const requestBody = JSON.parse(route.request().postData() || '{}')
        
        if (requestBody.email === 'test@example.com' && requestBody.password === 'password123') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              user: {
                id: '2',
                email: 'test@example.com',
                first_name: 'Test',
                last_name: 'User',
                is_teacher: false,
                is_approved_teacher: false,
                is_staff: false,
                is_superuser: false,
                date_joined: '2024-01-01T00:00:00Z',
                last_login: '2024-01-02T00:00:00Z'
              },
              tokens: {
                access: 'mock-access-token-login-12345',
                refresh: 'mock-refresh-token-login-67890'
              }
            })
          })
        } else {
          await route.fulfill({
            status: 401,
            contentType: 'application/json',
            body: JSON.stringify({
              message: 'Invalid credentials'
            })
          })
        }
      }
    })

    // Mock user tenants endpoint
    await page.route('**/api/v1/accounts/users/tenants/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: '1',
            name: 'University A',
            subdomain: 'university-a',
            primary_color: '#FF0000',
            secondary_color: '#AA0000',
            logo: null,
            subscription_plan: 'pro',
            is_active: true,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          },
          {
            id: '2',
            name: 'School B',
            subdomain: 'school-b',
            primary_color: '#00FF00',
            secondary_color: '#00AA00',
            logo: null,
            subscription_plan: 'basic',
            is_active: true,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          }
        ])
      })
    })

    // Mock password reset request
    await page.route('**/api/v1/accounts/auth/password-reset/', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            message: 'Password reset email sent if account exists'
          })
        })
      }
    })

    // Mock password reset confirmation
    await page.route('**/api/v1/accounts/auth/password-reset-confirm/', async route => {
      if (route.request().method() === 'POST') {
        const requestBody = JSON.parse(route.request().postData() || '{}')
        
        if (requestBody.token === 'valid-reset-token') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              message: 'Password reset successful'
            })
          })
        } else {
          await route.fulfill({
            status: 400,
            contentType: 'application/json',
            body: JSON.stringify({
              message: 'Invalid or expired token'
            })
          })
        }
      }
    })

    // Mock Google OAuth login
    await page.route('**/api/v1/accounts/auth/google/', async route => {
      if (route.request().method() === 'POST') {
        const requestBody = JSON.parse(route.request().postData() || '{}')
        
        if (requestBody.access_token === 'valid-google-token') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              user: {
                id: '3',
                email: 'google.user@gmail.com',
                first_name: 'Google',
                last_name: 'User',
                is_teacher: false,
                is_approved_teacher: false,
                is_staff: false,
                is_superuser: false,
                date_joined: '2024-01-01T00:00:00Z',
                last_login: '2024-01-02T00:00:00Z'
              },
              tokens: {
                access: 'mock-access-token-google-12345',
                refresh: 'mock-refresh-token-google-67890'
              }
            })
          })
        } else {
          await route.fulfill({
            status: 400,
            contentType: 'application/json',
            body: JSON.stringify({
              message: 'Invalid Google token'
            })
          })
        }
      }
    })

    // Mock token refresh
    await page.route('**/api/v1/accounts/auth/token/refresh/', async route => {
      if (route.request().method() === 'POST') {
        const requestBody = JSON.parse(route.request().postData() || '{}')
        
        if (requestBody.refresh && requestBody.refresh.includes('mock-refresh-token')) {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              access: 'new-mock-access-token-12345'
            })
          })
        } else {
          await route.fulfill({
            status: 401,
            contentType: 'application/json',
            body: JSON.stringify({
              message: 'Token is invalid or expired'
            })
          })
        }
      }
    })

    // Mock logout
    await page.route('**/api/v1/accounts/auth/logout/', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            message: 'Successfully logged out'
          })
        })
      }
    })

    // Mock tenant switching
    await page.route('**/api/v1/accounts/users/switch_tenant/', async route => {
      if (route.request().method() === 'POST') {
        const requestBody = JSON.parse(route.request().postData() || '{}')
        
        if (requestBody.tenant_id === '1') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              message: 'Tenant switched successfully',
              tenant: {
                id: '1',
                name: 'University A',
                subdomain: 'university-a',
                primary_color: '#FF0000',
                secondary_color: '#AA0000',
                logo: null,
                subscription_plan: 'pro',
                is_active: true,
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z'
              },
              tokens: {
                access: 'new-tenant-access-token-12345',
                refresh: 'new-tenant-refresh-token-67890'
              }
            })
          })
        }
      }
    })

    // Navigate to the application
    await page.goto('/')
  })

  test('complete user registration and login process', async ({ page }) => {
    // Test Registration Flow
    await page.click('text=Sign up')
    await expect(page).toHaveURL('/auth/register')

    // Fill registration form
    await page.fill('[data-testid="first-name"]', 'John')
    await page.fill('[data-testid="last-name"]', 'Doe')
    await page.fill('[data-testid="email"]', 'john.doe@example.com')
    await page.fill('[data-testid="password"]', 'SecurePass123!')
    await page.fill('[data-testid="password-confirm"]', 'SecurePass123!')
    
    // Select user type (student)
    await page.check('[data-testid="user-type-student"]')
    
    // Accept terms
    await page.check('[data-testid="accept-terms"]')
    
    // Submit form
    await page.click('[data-testid="register-button"]')
    
    // Should redirect to dashboard after successful registration
    await expect(page).toHaveURL('/dashboard')
    
    // Should show welcome message
    await expect(page.locator('[data-testid="welcome-message"]')).toContainText('Welcome John!')
    
    // Logout to test login flow
    await page.click('[data-testid="user-menu"]')
    await page.click('[data-testid="logout-button"]')
    
    // Should redirect to login page
    await expect(page).toHaveURL('/auth/login')
    
    // Test Login Flow
    await page.fill('[data-testid="email"]', 'test@example.com')
    await page.fill('[data-testid="password"]', 'password123')
    
    // Submit form
    await page.click('[data-testid="login-button"]')
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard')
    
    // Should show user information
    await expect(page.locator('[data-testid="user-name"]')).toContainText('Test User')
  })

  test('JWT token generation and validation', async ({ page }) => {
    // Login to get tokens
    await page.goto('/auth/login')
    await page.fill('[data-testid="email"]', 'test@example.com')
    await page.fill('[data-testid="password"]', 'password123')
    await page.click('[data-testid="login-button"]')
    
    // Wait for redirect to dashboard
    await expect(page).toHaveURL('/dashboard')
    
    // Check that tokens are stored in localStorage
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'))
    const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'))
    
    expect(accessToken).toBe('mock-access-token-login-12345')
    expect(refreshToken).toBe('mock-refresh-token-login-67890')
    
    // Check that user data is stored
    const userData = await page.evaluate(() => localStorage.getItem('user'))
    const user = JSON.parse(userData || '{}')
    
    expect(user.email).toBe('test@example.com')
    expect(user.first_name).toBe('Test')
    expect(user.last_name).toBe('User')
    
    // Test token validation by making an authenticated request
    // Navigate to a protected page that requires authentication
    await page.goto('/profile')
    
    // Should not redirect to login (token is valid)
    await expect(page).toHaveURL('/profile')
  })

  test('tenant-aware user access and isolation', async ({ page }) => {
    // Login first
    await page.goto('/auth/login')
    await page.fill('[data-testid="email"]', 'test@example.com')
    await page.fill('[data-testid="password"]', 'password123')
    await page.click('[data-testid="login-button"]')
    
    await expect(page).toHaveURL('/dashboard')
    
    // Check that user tenants are loaded
    await page.waitForTimeout(1000) // Wait for tenants to load
    
    // Should show tenant switcher with available tenants
    await page.click('[data-testid="tenant-switcher"]')
    await expect(page.locator('text=University A')).toBeVisible()
    await expect(page.locator('text=School B')).toBeVisible()
    
    // Switch to University A tenant
    await page.click('text=University A')
    
    // Wait for tenant switch to complete
    await page.waitForTimeout(1000)
    
    // Check that tenant context is updated
    const tenantId = await page.evaluate(() => localStorage.getItem('tenant_id'))
    expect(tenantId).toBe('1')
    
    // Check that new tokens are stored after tenant switch
    const newAccessToken = await page.evaluate(() => localStorage.getItem('access_token'))
    expect(newAccessToken).toBe('new-tenant-access-token-12345')
    
    // Test tenant isolation by visiting tenant-specific subdomain
    await page.goto('http://university-a.localhost:3000/dashboard')
    
    // Should show University A branding
    await expect(page.locator('text=University A')).toBeVisible()
    
    // Switch to different tenant subdomain
    await page.goto('http://school-b.localhost:3000/dashboard')
    
    // Should show School B branding (tenant isolation)
    await expect(page.locator('text=School B')).toBeVisible()
    await expect(page.locator('text=University A')).not.toBeVisible()
  })

  test('Google OAuth integration end-to-end', async ({ page }) => {
    // Navigate to login page
    await page.goto('/auth/login')
    
    // Mock Google OAuth flow
    await page.evaluate(() => {
      // Mock Google OAuth response
      window.googleOAuthCallback = (token: string) => {
        // This would normally be called by Google OAuth
        const event = new CustomEvent('google-oauth-success', {
          detail: { access_token: token }
        })
        window.dispatchEvent(event)
      }
    })
    
    // Click Google login button
    await page.click('[data-testid="google-login-button"]')
    
    // Simulate successful Google OAuth callback
    await page.evaluate(() => {
      window.googleOAuthCallback('valid-google-token')
    })
    
    // Should redirect to dashboard after successful Google login
    await expect(page).toHaveURL('/dashboard')
    
    // Check that tokens are stored
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'))
    const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'))
    
    expect(accessToken).toBe('mock-access-token-google-12345')
    expect(refreshToken).toBe('mock-refresh-token-google-67890')
    
    // Check that user data is stored
    const userData = await page.evaluate(() => localStorage.getItem('user'))
    const user = JSON.parse(userData || '{}')
    
    expect(user.email).toBe('google.user@gmail.com')
    expect(user.first_name).toBe('Google')
    expect(user.last_name).toBe('User')
    
    // Should show user information in dashboard
    await expect(page.locator('[data-testid="user-name"]')).toContainText('Google User')
  })

  test('password reset flow with token validation', async ({ page }) => {
    // Navigate to forgot password page
    await page.goto('/auth/login')
    await page.click('text=Forgot your password?')
    await expect(page).toHaveURL('/auth/forgot-password')

    // Fill email
    await page.fill('[data-testid="email"]', 'test@example.com')
    
    // Submit form
    await page.click('[data-testid="reset-button"]')
    
    // Should show success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible()
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Password reset email sent')
    
    // Navigate to password reset confirmation page (simulating email link click)
    await page.goto('/auth/reset-password?token=valid-reset-token')
    
    // Fill new password form
    await page.fill('[data-testid="new-password"]', 'NewSecurePass123!')
    await page.fill('[data-testid="confirm-password"]', 'NewSecurePass123!')
    
    // Submit form
    await page.click('[data-testid="confirm-reset-button"]')
    
    // Should show success message and redirect to login
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Password reset successful')
    await expect(page).toHaveURL('/auth/login')
  })

  test('token refresh mechanism', async ({ page }) => {
    // Login first
    await page.goto('/auth/login')
    await page.fill('[data-testid="email"]', 'test@example.com')
    await page.fill('[data-testid="password"]', 'password123')
    await page.click('[data-testid="login-button"]')
    
    await expect(page).toHaveURL('/dashboard')
    
    // Store initial tokens
    const initialAccessToken = await page.evaluate(() => localStorage.getItem('access_token'))
    expect(initialAccessToken).toBe('mock-access-token-login-12345')
    
    // Mock an API call that returns 401 (expired token)
    await page.route('**/api/v1/test-protected-endpoint/', async route => {
      const authHeader = route.request().headers()['authorization']
      
      if (authHeader === 'Bearer mock-access-token-login-12345') {
        // First call with original token - return 401
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({ message: 'Token expired' })
        })
      } else if (authHeader === 'Bearer new-mock-access-token-12345') {
        // Second call with refreshed token - return success
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ message: 'Success' })
        })
      }
    })
    
    // Trigger an API call that will cause token refresh
    await page.evaluate(async () => {
      try {
        const response = await fetch('/api/v1/test-protected-endpoint/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        return response.json()
      } catch (error) {
        return { error: error.message }
      }
    })
    
    // Wait for token refresh to complete
    await page.waitForTimeout(1000)
    
    // Check that access token was refreshed
    const newAccessToken = await page.evaluate(() => localStorage.getItem('access_token'))
    expect(newAccessToken).toBe('new-mock-access-token-12345')
    
    // User should still be logged in and on dashboard
    await expect(page).toHaveURL('/dashboard')
  })

  test('secure logout with token blacklisting', async ({ page }) => {
    // Login first
    await page.goto('/auth/login')
    await page.fill('[data-testid="email"]', 'test@example.com')
    await page.fill('[data-testid="password"]', 'password123')
    await page.click('[data-testid="login-button"]')
    
    await expect(page).toHaveURL('/dashboard')
    
    // Verify tokens are stored
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'))
    const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'))
    
    expect(accessToken).toBeTruthy()
    expect(refreshToken).toBeTruthy()
    
    // Logout
    await page.click('[data-testid="user-menu"]')
    await page.click('[data-testid="logout-button"]')
    
    // Should redirect to login page
    await expect(page).toHaveURL('/auth/login')
    
    // Check that tokens are cleared from localStorage
    const clearedAccessToken = await page.evaluate(() => localStorage.getItem('access_token'))
    const clearedRefreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'))
    const clearedUser = await page.evaluate(() => localStorage.getItem('user'))
    
    expect(clearedAccessToken).toBeNull()
    expect(clearedRefreshToken).toBeNull()
    expect(clearedUser).toBeNull()
    
    // Try to access protected page - should redirect to login
    await page.goto('/dashboard')
    await expect(page).toHaveURL('/auth/login')
  })

  test('authentication error handling', async ({ page }) => {
    // Test invalid login credentials
    await page.goto('/auth/login')
    await page.fill('[data-testid="email"]', 'invalid@example.com')
    await page.fill('[data-testid="password"]', 'wrongpassword')
    await page.click('[data-testid="login-button"]')
    
    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Invalid credentials')
    
    // Should remain on login page
    await expect(page).toHaveURL('/auth/login')
    
    // Test registration with existing email
    await page.goto('/auth/register')
    await page.fill('[data-testid="first-name"]', 'Test')
    await page.fill('[data-testid="last-name"]', 'User')
    await page.fill('[data-testid="email"]', 'existing@example.com')
    await page.fill('[data-testid="password"]', 'SecurePass123!')
    await page.fill('[data-testid="password-confirm"]', 'SecurePass123!')
    await page.check('[data-testid="user-type-student"]')
    await page.check('[data-testid="accept-terms"]')
    await page.click('[data-testid="register-button"]')
    
    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toContainText('User with this email already exists')
    
    // Should remain on registration page
    await expect(page).toHaveURL('/auth/register')
  })

  test('multi-tenant authentication isolation', async ({ page }) => {
    // Test authentication on University A subdomain
    await page.goto('http://university-a.localhost:3000/auth/login')
    
    // Login should work on tenant subdomain
    await page.fill('[data-testid="email"]', 'test@example.com')
    await page.fill('[data-testid="password"]', 'password123')
    await page.click('[data-testid="login-button"]')
    
    await expect(page).toHaveURL('http://university-a.localhost:3000/dashboard')
    
    // Should show University A branding
    await expect(page.locator('text=University A')).toBeVisible()
    
    // Navigate to different tenant subdomain while logged in
    await page.goto('http://school-b.localhost:3000/dashboard')
    
    // Should show School B branding (tenant context should switch)
    await expect(page.locator('text=School B')).toBeVisible()
    
    // User should still be authenticated but in different tenant context
    await expect(page.locator('[data-testid="user-name"]')).toBeVisible()
  })
})