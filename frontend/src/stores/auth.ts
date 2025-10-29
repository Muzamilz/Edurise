import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import { api } from '@/services/api'
import type { User, LoginRequest, RegisterRequest, AuthResponse, Organization } from '@/types/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const currentTenant = ref<Organization | null>(null)
  const userTenants = ref<Organization[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const isTeacher = computed(() => user.value?.is_teacher || false)
  const isApprovedTeacher = computed(() => user.value?.is_approved_teacher || false)
  const isStaff = computed(() => user.value?.is_staff || false)
  const isSuperuser = computed(() => user.value?.is_superuser || false)
  const fullName = computed(() => {
    if (!user.value) return ''
    return `${user.value.first_name} ${user.value.last_name}`.trim()
  })

  // Actions
  const login = async (credentials: LoginRequest): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      console.log('🔐 Attempting login with:', { email: credentials.email })
      
      const response = await api.post<AuthResponse>('/accounts/auth/login/', credentials)
      console.log('🔐 Raw login response:', response)
      console.log('🔐 Response data:', response.data)
      
      const responseData = response.data as any
      
      // Handle both old and new response formats
      let userData, tokens
      if (responseData.success && responseData.data) {
        // New standardized format
        console.log('🔐 Using new standardized format')
        const data = responseData.data
        userData = data.user
        tokens = {
          access: data.access,
          refresh: data.refresh
        }
      } else if (responseData.user && (responseData.tokens || responseData.access)) {
        // Old format (fallback)
        console.log('🔐 Using old format')
        userData = responseData.user
        tokens = responseData.tokens || {
          access: responseData.access,
          refresh: responseData.refresh
        }
      } else {
        console.error('🔐 Unexpected response format:', responseData)
        throw new Error('Invalid response format from server')
      }

      console.log('🔐 Parsed user data:', userData)
      console.log('🔐 Parsed tokens:', { access: tokens.access ? 'present' : 'missing', refresh: tokens.refresh ? 'present' : 'missing' })

      if (!userData || !tokens.access || !tokens.refresh) {
        throw new Error('Missing required authentication data')
      }

      // Store user data and tokens
      user.value = userData
      accessToken.value = tokens.access
      refreshToken.value = tokens.refresh

      // Persist to localStorage
      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
      localStorage.setItem('user', JSON.stringify(userData))

      console.log('🔐 Login successful, loading user tenants...')
      
      // Load user tenants
      await loadUserTenants()

      console.log('🔐 Login process completed successfully')

    } catch (err: any) {
      console.error('🔐 Login error:', err)
      error.value = err.response?.data?.message || err.response?.data?.detail || err.message || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData: RegisterRequest): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      const response = await api.post<AuthResponse>('/accounts/auth/register/', userData)
      const responseData = response.data as any
      
      // Handle both old and new response formats
      let newUser, tokens
      if (responseData.success && responseData.data) {
        // New standardized format
        const data = responseData.data
        newUser = data.user
        tokens = {
          access: data.access,
          refresh: data.refresh
        }
      } else {
        // Old format (fallback)
        newUser = responseData.user
        tokens = responseData.tokens || responseData
      }

      // Store user data and tokens
      user.value = newUser
      accessToken.value = tokens.access
      refreshToken.value = tokens.refresh

      // Persist to localStorage
      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
      localStorage.setItem('user', JSON.stringify(newUser))

      // Load user tenants
      await loadUserTenants()

    } catch (err: any) {
      error.value = err.response?.data?.message || err.response?.data?.detail || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = async (): Promise<void> => {
    try {
      // Call logout endpoint if refresh token exists
      if (refreshToken.value) {
        await api.post('/accounts/auth/logout/', {
          refresh_token: refreshToken.value
        })
      }
    } catch (err) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', err)
    } finally {
      // Clear state
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      currentTenant.value = null
      userTenants.value = []
      error.value = null

      // Clear localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      localStorage.removeItem('tenant_id')
    }
  }

  const refreshAccessToken = async (): Promise<boolean> => {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token available')
      }

      console.log('🔄 Refreshing access token...')
      
      const response = await api.post<{ access: string; refresh?: string }>('/accounts/auth/token/refresh/', {
        refresh: refreshToken.value
      })

      console.log('🔄 Token refresh response:', response.data)

      // Handle both direct response and wrapped response
      const responseData = response.data as any
      let newAccessToken, newRefreshToken
      
      if (responseData.success && responseData.data) {
        // New standardized format
        newAccessToken = responseData.data.access
        newRefreshToken = responseData.data.refresh
      } else {
        // Old format
        newAccessToken = responseData.access
        newRefreshToken = responseData.refresh
      }

      if (newAccessToken) {
        accessToken.value = newAccessToken
        localStorage.setItem('access_token', newAccessToken)

        // Update refresh token if provided
        if (newRefreshToken) {
          refreshToken.value = newRefreshToken
          localStorage.setItem('refresh_token', newRefreshToken)
        }

        console.log('🔄 Token refresh successful')
        return true
      } else {
        throw new Error('No access token in refresh response')
      }
    } catch (err) {
      console.error('🔄 Token refresh failed:', err)
      // Refresh failed, logout user
      await logout()
      return false
    }
  }

  const requestPasswordReset = async (email: string): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      await api.post('/accounts/auth/password-reset/', { email })
    } catch (err: any) {
      error.value = err.response?.data?.message || err.response?.data?.detail || 'Password reset request failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const confirmPasswordReset = async (token: string, password: string, passwordConfirm: string): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      await api.post('/accounts/auth/password-reset-confirm/', {
        token,
        password,
        password_confirm: passwordConfirm
      })
    } catch (err: any) {
      error.value = err.response?.data?.message || err.response?.data?.detail || 'Password reset failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const googleLogin = async (googleAccessToken: string): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      const response = await api.post<AuthResponse>('/accounts/auth/google/', {
        access_token: googleAccessToken
      })
      const responseData = response.data as any
      const { user: userData, tokens } = responseData

      // Store user data and tokens
      user.value = userData
      accessToken.value = tokens.access
      refreshToken.value = tokens.refresh

      // Persist to localStorage
      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
      localStorage.setItem('user', JSON.stringify(userData))

      // Load user tenants
      await loadUserTenants()

    } catch (err: any) {
      error.value = err.response?.data?.message || err.response?.data?.detail || 'Google login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const loadUserTenants = async (): Promise<void> => {
    try {
      console.log('🏢 Loading user tenants...')
      const response = await api.get<Organization[]>('/users/tenants/')
      console.log('🏢 Tenants response:', response.data)
      
      // Handle standardized response format
      let tenantsData
      if (response.data && typeof response.data === 'object' && 'success' in response.data) {
        tenantsData = (response.data as any).data || []
      } else {
        tenantsData = response.data || []
      }
      
      userTenants.value = tenantsData as Organization[]
      console.log('🏢 Loaded tenants:', userTenants.value)

      // Set current tenant if not set
      if (!currentTenant.value && userTenants.value.length > 0) {
        currentTenant.value = userTenants.value[0]
        // Store tenant ID in localStorage for API headers
        localStorage.setItem('tenant_id', currentTenant.value.id)
        console.log('🏢 Set current tenant:', currentTenant.value)
      }
    } catch (err) {
      console.warn('🏢 Failed to load user tenants:', err)
      // Don't throw error, just continue without tenants
    }
  }

  const switchTenant = async (tenantId: string): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      const response = await api.post<{
        message: string
        tenant: Organization
        tokens: { access: string; refresh: string }
      }>('/accounts/users/switch_tenant/', {
        tenant_id: tenantId
      })

      const responseData = response.data as any
      const { tenant, tokens } = responseData

      // Update tokens and tenant
      accessToken.value = tokens.access
      refreshToken.value = tokens.refresh
      currentTenant.value = tenant

      // Persist to localStorage
      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
      localStorage.setItem('tenant_id', tenant.id)

    } catch (err: any) {
      error.value = err.response?.data?.message || err.response?.data?.detail || 'Failed to switch tenant'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const getCurrentUser = async (): Promise<void> => {
    try {
      const response = await api.get<User>('/accounts/users/me/')
      user.value = response.data as unknown as User
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (err) {
      console.warn('Failed to get current user:', err)
    }
  }

  const initializeAuth = (): void => {
    // Restore auth state from localStorage
    const storedToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedUser = localStorage.getItem('user')
    const storedTenantId = localStorage.getItem('tenant_id')

    if (storedToken && storedRefreshToken && storedUser) {
      try {
        accessToken.value = storedToken
        refreshToken.value = storedRefreshToken
        user.value = JSON.parse(storedUser)

        // Load user tenants and set current tenant
        loadUserTenants().then(() => {
          if (storedTenantId) {
            const tenant = userTenants.value.find(t => t.id === storedTenantId)
            if (tenant) {
              currentTenant.value = tenant
            }
          }
          // Ensure tenant_id is in localStorage for API headers
          if (currentTenant.value) {
            localStorage.setItem('tenant_id', currentTenant.value.id)
          }
        })
      } catch (err) {
        console.error('Failed to parse stored user data:', err)
        logout()
      }
    }
  }

  const clearError = (): void => {
    error.value = null
  }

  return {
    // State
    user: readonly(user),
    accessToken: readonly(accessToken),
    refreshToken: readonly(refreshToken),
    currentTenant: readonly(currentTenant),
    userTenants: readonly(userTenants),
    isLoading: readonly(isLoading),
    error: readonly(error),

    // Getters
    isAuthenticated,
    isTeacher,
    isApprovedTeacher,
    isStaff,
    isSuperuser,
    fullName,

    // Actions
    login,
    register,
    logout,
    refreshAccessToken,
    requestPasswordReset,
    confirmPasswordReset,
    googleLogin,
    loadUserTenants,
    switchTenant,
    getCurrentUser,
    initializeAuth,
    clearError
  }
})