/**
 * Authentication Flow Integration Tests
 * 
 * This test suite validates the complete authentication flow including:
 * - User registration and login process
 * - JWT token generation and validation
 * - Tenant-aware user access and isolation
 * - Google OAuth integration
 * - Password reset functionality
 * 
 * Requirements: 1.1, 1.2, 1.5
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useTenant } from '@/composables/useTenant'
import { api } from '@/services/api'
import type { AuthResponse, User, Organization } from '@/types/api'

// Mock the API service
vi.mock('@/services/api', () => ({
  api: {
    post: vi.fn(),
    get: vi.fn(),
  }
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

// Mock window.location
Object.defineProperty(window, 'location', {
  value: {
    hostname: 'localhost',
    reload: vi.fn(),
  },
  writable: true,
})

describe('Authentication Flow Integration Tests', () => {
  let authStore: ReturnType<typeof useAuthStore>
  
  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks()
    
    // Create fresh Pinia instance
    setActivePinia(createPinia())
    authStore = useAuthStore()
    
    // Reset localStorage mock
    localStorageMock.getItem.mockReturnValue(null)
  })

  describe('Complete User Registration and Login Process', () => {
    it('should successfully register a new user and store tokens', async () => {
      // Mock successful registration response
      const mockAuthResponse: AuthResponse = {
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
      }

      const mockTenants: Organization[] = [
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
        }
      ]

      // Mock API calls
      vi.mocked(api.post).mockResolvedValueOnce({ data: mockAuthResponse })
      vi.mocked(api.get).mockResolvedValueOnce({ data: mockTenants })

      // Perform registration
      await authStore.register({
        email: 'john.doe@example.com',
        password: 'SecurePass123!',
        password_confirm: 'SecurePass123!',
        first_name: 'John',
        last_name: 'Doe',
        is_teacher: false
      })

      // Verify API was called correctly
      expect(api.post).toHaveBeenCalledWith('/accounts/auth/register/', {
        email: 'john.doe@example.com',
        password: 'SecurePass123!',
        password_confirm: 'SecurePass123!',
        first_name: 'John',
        last_name: 'Doe',
        is_teacher: false
      })

      // Verify user data is stored
      expect(authStore.user).toEqual(mockAuthResponse.user)
      expect(authStore.isAuthenticated).toBe(true)

      // Verify tokens are stored in localStorage
      expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'mock-access-token-12345')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'mock-refresh-token-67890')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockAuthResponse.user))

      // Verify tenants are loaded
      expect(api.get).toHaveBeenCalledWith('/accounts/users/tenants/')
      expect(authStore.userTenants).toEqual(mockTenants)
    })

    it('should successfully login existing user', async () => {
      const mockAuthResponse: AuthResponse = {
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
      }

      vi.mocked(api.post).mockResolvedValueOnce({ data: mockAuthResponse })
      vi.mocked(api.get).mockResolvedValueOnce({ data: [] })

      await authStore.login({
        email: 'test@example.com',
        password: 'password123'
      })

      expect(api.post).toHaveBeenCalledWith('/accounts/auth/login/', {
        email: 'test@example.com',
        password: 'password123'
      })

      expect(authStore.user).toEqual(mockAuthResponse.user)
      expect(authStore.isAuthenticated).toBe(true)
      expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'mock-access-token-login-12345')
    })

    it('should handle registration errors correctly', async () => {
      const mockError = {
        response: {
          data: {
            message: 'Registration failed',
            errors: { email: ['User with this email already exists'] }
          }
        }
      }

      vi.mocked(api.post).mockRejectedValueOnce(mockError)

      await expect(authStore.register({
        email: 'existing@example.com',
        password: 'SecurePass123!',
        password_confirm: 'SecurePass123!',
        first_name: 'Test',
        last_name: 'User'
      })).rejects.toThrow()

      expect(authStore.error).toBe('Registration failed')
      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('JWT Token Generation and Validation', () => {
    it('should store and validate JWT tokens correctly', async () => {
      const mockAuthResponse: AuthResponse = {
        user: {
          id: '1',
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
          access: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.mock-payload',
          refresh: 'refresh-token-12345'
        }
      }

      vi.mocked(api.post).mockResolvedValueOnce({ data: mockAuthResponse })
      vi.mocked(api.get).mockResolvedValueOnce({ data: [] })

      await authStore.login({
        email: 'test@example.com',
        password: 'password123'
      })

      // Verify tokens are stored
      expect(authStore.accessToken).toBe('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.mock-payload')
      expect(authStore.refreshToken).toBe('refresh-token-12345')

      // Verify localStorage storage
      expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.mock-payload')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'refresh-token-12345')
    })

    it('should refresh access token when expired', async () => {
      // Setup initial tokens by setting localStorage and store state
      localStorage.setItem('refresh_token', 'valid-refresh-token')
      authStore.$patch({
        refreshToken: 'valid-refresh-token'
      })

      const mockRefreshResponse = {
        access: 'new-access-token-12345'
      }

      vi.mocked(api.post).mockResolvedValueOnce({ data: mockRefreshResponse })

      const result = await authStore.refreshAccessToken()

      expect(result).toBe(true)
      expect(api.post).toHaveBeenCalledWith('/accounts/auth/token/refresh/', {
        refresh: 'valid-refresh-token'
      })
      expect(authStore.accessToken).toBe('new-access-token-12345')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'new-access-token-12345')
    })

    it('should logout user when refresh token is invalid', async () => {
      authStore.$patch({
        refreshToken: 'invalid-refresh-token'
      })

      const mockError = {
        response: {
          status: 401,
          data: { message: 'Token is invalid or expired' }
        }
      }

      vi.mocked(api.post).mockRejectedValueOnce(mockError)

      const result = await authStore.refreshAccessToken()

      expect(result).toBe(false)
      expect(authStore.user).toBeNull()
      expect(authStore.accessToken).toBeNull()
      expect(authStore.refreshToken).toBeNull()
    })
  })

  describe('Tenant-Aware User Access and Isolation', () => {
    it('should load user tenants after authentication', async () => {
      const mockTenants: Organization[] = [
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
      ]

      vi.mocked(api.get).mockResolvedValueOnce({ data: mockTenants })

      await authStore.loadUserTenants()

      expect(api.get).toHaveBeenCalledWith('/accounts/users/tenants/')
      expect(authStore.userTenants).toEqual(mockTenants)
      expect(authStore.currentTenant).toEqual(mockTenants[0]) // Should set first tenant as current
    })

    it('should switch tenant context correctly', async () => {
      const mockSwitchResponse = {
        message: 'Tenant switched successfully',
        tenant: {
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
        },
        tokens: {
          access: 'new-tenant-access-token',
          refresh: 'new-tenant-refresh-token'
        }
      }

      vi.mocked(api.post).mockResolvedValueOnce({ data: mockSwitchResponse })

      await authStore.switchTenant('2')

      expect(api.post).toHaveBeenCalledWith('/accounts/users/switch_tenant/', {
        tenant_id: '2'
      })

      expect(authStore.currentTenant).toEqual(mockSwitchResponse.tenant)
      expect(authStore.accessToken).toBe('new-tenant-access-token')
      expect(authStore.refreshToken).toBe('new-tenant-refresh-token')

      // Verify new tokens are stored
      expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'new-tenant-access-token')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'new-tenant-refresh-token')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('tenant_id', '2')
    })

    it('should detect tenant from subdomain', () => {
      const { detectTenantFromSubdomain } = useTenant()

      // Mock different hostnames
      Object.defineProperty(window, 'location', {
        value: { hostname: 'university-a.edurise.com' },
        writable: true,
      })
      expect(detectTenantFromSubdomain()).toBe('university-a')

      Object.defineProperty(window, 'location', {
        value: { hostname: 'school-b.localhost' },
        writable: true,
      })
      expect(detectTenantFromSubdomain()).toBe('school-b')

      Object.defineProperty(window, 'location', {
        value: { hostname: 'edurise.com' },
        writable: true,
      })
      expect(detectTenantFromSubdomain()).toBeNull()

      Object.defineProperty(window, 'location', {
        value: { hostname: 'www.edurise.com' },
        writable: true,
      })
      expect(detectTenantFromSubdomain()).toBeNull()
    })
  })

  describe('Google OAuth Integration', () => {
    it('should authenticate user with Google OAuth token', async () => {
      const mockAuthResponse: AuthResponse = {
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
      }

      vi.mocked(api.post).mockResolvedValueOnce({ data: mockAuthResponse })
      vi.mocked(api.get).mockResolvedValueOnce({ data: [] })

      await authStore.googleLogin('valid-google-access-token')

      expect(api.post).toHaveBeenCalledWith('/accounts/auth/google/', {
        access_token: 'valid-google-access-token'
      })

      expect(authStore.user).toEqual(mockAuthResponse.user)
      expect(authStore.isAuthenticated).toBe(true)
      expect(authStore.accessToken).toBe('mock-access-token-google-12345')
    })

    it('should handle Google OAuth errors', async () => {
      const mockError = {
        response: {
          data: {
            message: 'Invalid Google token'
          }
        }
      }

      vi.mocked(api.post).mockRejectedValueOnce(mockError)

      await expect(authStore.googleLogin('invalid-google-token')).rejects.toThrow()

      expect(authStore.error).toBe('Invalid Google token')
      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('Password Reset Flow', () => {
    it('should request password reset successfully', async () => {
      const mockResponse = {
        message: 'Password reset email sent if account exists'
      }

      vi.mocked(api.post).mockResolvedValueOnce({ data: mockResponse })

      await authStore.requestPasswordReset('test@example.com')

      expect(api.post).toHaveBeenCalledWith('/accounts/auth/password-reset/', {
        email: 'test@example.com'
      })

      expect(authStore.error).toBeNull()
    })

    it('should confirm password reset with valid token', async () => {
      const mockResponse = {
        message: 'Password reset successful'
      }

      vi.mocked(api.post).mockResolvedValueOnce({ data: mockResponse })

      await authStore.confirmPasswordReset('valid-reset-token', 'NewPassword123!', 'NewPassword123!')

      expect(api.post).toHaveBeenCalledWith('/accounts/auth/password-reset-confirm/', {
        token: 'valid-reset-token',
        password: 'NewPassword123!',
        password_confirm: 'NewPassword123!'
      })

      expect(authStore.error).toBeNull()
    })

    it('should handle invalid password reset token', async () => {
      const mockError = {
        response: {
          data: {
            message: 'Invalid or expired token'
          }
        }
      }

      vi.mocked(api.post).mockRejectedValueOnce(mockError)

      await expect(authStore.confirmPasswordReset('invalid-token', 'NewPassword123!', 'NewPassword123!')).rejects.toThrow()

      expect(authStore.error).toBe('Invalid or expired token')
    })
  })

  describe('Secure Logout with Token Blacklisting', () => {
    it('should logout user and clear all stored data', async () => {
      // Setup authenticated user using $patch
      authStore.$patch({
        user: {
          id: '1',
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
        accessToken: 'access-token',
        refreshToken: 'refresh-token'
      })

      const mockResponse = {
        message: 'Successfully logged out'
      }

      vi.mocked(api.post).mockResolvedValueOnce({ data: mockResponse })

      await authStore.logout()

      // Verify logout API call with refresh token
      expect(api.post).toHaveBeenCalledWith('/accounts/auth/logout/', {
        refresh_token: 'refresh-token'
      })

      // Verify all state is cleared
      expect(authStore.user).toBeNull()
      expect(authStore.accessToken).toBeNull()
      expect(authStore.refreshToken).toBeNull()
      expect(authStore.currentTenant).toBeNull()
      expect(authStore.userTenants).toEqual([])

      // Verify localStorage is cleared
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('tenant_id')
    })

    it('should clear state even if logout API fails', async () => {
      authStore.$patch({
        user: { id: '1' } as User,
        accessToken: 'access-token',
        refreshToken: 'refresh-token'
      })

      const mockError = new Error('Network error')
      vi.mocked(api.post).mockRejectedValueOnce(mockError)

      await authStore.logout()

      // Should still clear state even if API call fails
      expect(authStore.user).toBeNull()
      expect(authStore.accessToken).toBeNull()
      expect(authStore.refreshToken).toBeNull()
    })
  })

  describe('Authentication State Persistence', () => {
    it('should initialize auth state from localStorage', () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
        is_teacher: false,
        is_approved_teacher: false,
        is_staff: false,
        is_superuser: false,
        date_joined: '2024-01-01T00:00:00Z',
        last_login: '2024-01-02T00:00:00Z'
      }

      localStorageMock.getItem.mockImplementation((key: string) => {
        switch (key) {
          case 'access_token':
            return 'stored-access-token'
          case 'refresh_token':
            return 'stored-refresh-token'
          case 'user':
            return JSON.stringify(mockUser)
          case 'tenant_id':
            return '1'
          default:
            return null
        }
      })

      vi.mocked(api.get).mockResolvedValueOnce({ 
        data: [
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
          }
        ] 
      })

      authStore.initializeAuth()

      expect(authStore.user).toEqual(mockUser)
      expect(authStore.accessToken).toBe('stored-access-token')
      expect(authStore.refreshToken).toBe('stored-refresh-token')
      expect(authStore.isAuthenticated).toBe(true)
    })

    it('should handle corrupted localStorage data gracefully', () => {
      localStorageMock.getItem.mockImplementation((key: string) => {
        switch (key) {
          case 'access_token':
            return 'stored-access-token'
          case 'refresh_token':
            return 'stored-refresh-token'
          case 'user':
            return 'invalid-json-data'
          default:
            return null
        }
      })

      // Should not throw error and should clear invalid data
      expect(() => authStore.initializeAuth()).not.toThrow()

      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      const networkError = new Error('Network Error')
      vi.mocked(api.post).mockRejectedValueOnce(networkError)

      await expect(authStore.login({
        email: 'test@example.com',
        password: 'password123'
      })).rejects.toThrow('Network Error')

      expect(authStore.isLoading).toBe(false)
      expect(authStore.isAuthenticated).toBe(false)
    })

    it('should clear error state when requested', () => {
      authStore.error = 'Some error message'
      
      authStore.clearError()
      
      expect(authStore.error).toBeNull()
    })
  })
})