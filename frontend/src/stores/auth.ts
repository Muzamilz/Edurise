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

      const response = await api.post<AuthResponse>('/accounts/auth/login/', credentials)
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
      error.value = err.response?.data?.message || err.response?.data?.detail || 'Login failed'
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
      const { user: newUser, tokens } = responseData

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

      const response = await api.post<{ access: string; refresh?: string }>('/accounts/auth/token/refresh/', {
        refresh: refreshToken.value
      })

      // Handle both direct response and wrapped response
      const responseData = response.data as any
      const newAccessToken = responseData.access
      const newRefreshToken = responseData.refresh

      if (newAccessToken) {
        accessToken.value = newAccessToken
        localStorage.setItem('access_token', newAccessToken)

        // Update refresh token if provided
        if (newRefreshToken) {
          refreshToken.value = newRefreshToken
          localStorage.setItem('refresh_token', newRefreshToken)
        }

        return true
      } else {
        throw new Error('No access token in refresh response')
      }
    } catch (err) {
      console.error('Token refresh failed:', err)
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
      const response = await api.get<Organization[]>('/accounts/users/tenants/')
      userTenants.value = response.data as unknown as Organization[]

      // Set current tenant if not set
      if (!currentTenant.value && userTenants.value.length > 0) {
        currentTenant.value = userTenants.value[0]
      }
    } catch (err) {
      console.warn('Failed to load user tenants:', err)
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