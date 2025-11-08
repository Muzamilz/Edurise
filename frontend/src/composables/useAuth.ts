import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { LoginRequest, RegisterRequest } from '@/types/api'

export const useAuth = () => {
  const authStore = useAuthStore()
  const router = useRouter()

  // Computed properties from store
  const user = computed(() => authStore.user)
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const isLoading = computed(() => authStore.isLoading)
  const error = computed(() => authStore.error)
  const isTeacher = computed(() => authStore.isTeacher)
  const isApprovedTeacher = computed(() => authStore.isApprovedTeacher)
  const isStaff = computed(() => authStore.isStaff)
  const isSuperuser = computed(() => authStore.isSuperuser)
  const fullName = computed(() => authStore.fullName)
  const currentTenant = computed(() => authStore.currentTenant)
  const userTenants = computed(() => authStore.userTenants)

  // Authentication methods
  const login = async (credentials: LoginRequest, redirectTo?: string) => {
    try {
      await authStore.login(credentials)
      
      // Redirect after successful login based on user role
      if (redirectTo) {
        await router.push(redirectTo)
      } else {
        // Use role-based dashboard route
        await router.push(authStore.dashboardRoute)
      }
    } catch (error) {
      // Error is handled by the store
      throw error
    }
  }

  const register = async (userData: RegisterRequest, redirectTo?: string) => {
    try {
      await authStore.register(userData)
      
      // Redirect after successful registration based on user role
      if (redirectTo) {
        await router.push(redirectTo)
      } else {
        // Use role-based dashboard route
        await router.push(authStore.dashboardRoute)
      }
    } catch (error) {
      // Error is handled by the store
      throw error
    }
  }

  const logout = async (redirectTo?: string) => {
    try {
      await authStore.logout()
      
      // Redirect after logout
      const redirect = redirectTo || '/auth/login'
      await router.push(redirect)
    } catch (error) {
      // Even if logout fails, redirect to login
      const redirect = redirectTo || '/auth/login'
      await router.push(redirect)
    }
  }

  const requestPasswordReset = async (email: string) => {
    try {
      await authStore.requestPasswordReset(email)
      return { success: true, message: 'Password reset email sent if account exists' }
    } catch (error) {
      throw error
    }
  }

  const confirmPasswordReset = async (token: string, password: string, passwordConfirm: string) => {
    try {
      await authStore.confirmPasswordReset(token, password, passwordConfirm)
      return { success: true, message: 'Password reset successful' }
    } catch (error) {
      throw error
    }
  }

  const loginWithGoogle = async (accessToken: string, redirectTo?: string) => {
    try {
      await authStore.googleLogin(accessToken)
      
      // Redirect after successful login based on user role
      if (redirectTo) {
        await router.push(redirectTo)
      } else {
        // Use role-based dashboard route
        await router.push(authStore.dashboardRoute)
      }
    } catch (error) {
      throw error
    }
  }

  const switchTenant = async (tenantId: string) => {
    try {
      await authStore.switchTenant(tenantId)
      // Optionally refresh the current page or redirect
      window.location.reload()
    } catch (error) {
      throw error
    }
  }

  const refreshToken = async () => {
    try {
      const success = await authStore.refreshAccessToken()
      if (!success) {
        // Token refresh failed, redirect to login
        await router.push('/auth/login')
      }
      return success
    } catch (error) {
      await router.push('/auth/login')
      return false
    }
  }

  const requireAuth = () => {
    if (!isAuthenticated.value) {
      router.push('/auth/login')
      return false
    }
    return true
  }

  const requireTeacher = () => {
    if (!isAuthenticated.value) {
      router.push('/auth/login')
      return false
    }
    if (!isApprovedTeacher.value) {
      router.push('/unauthorized')
      return false
    }
    return true
  }

  const requireStaff = () => {
    if (!isAuthenticated.value) {
      router.push('/auth/login')
      return false
    }
    if (!isStaff.value) {
      router.push('/unauthorized')
      return false
    }
    return true
  }

  const clearError = () => {
    authStore.clearError()
  }

  const initialize = () => {
    authStore.initializeAuth()
  }

  return {
    // State
    user,
    isAuthenticated,
    isLoading,
    error,
    isTeacher,
    isApprovedTeacher,
    isStaff,
    isSuperuser,
    fullName,
    currentTenant,
    userTenants,

    // Methods
    login,
    register,
    logout,
    requestPasswordReset,
    confirmPasswordReset,
    loginWithGoogle,
    switchTenant,
    refreshToken,
    requireAuth,
    requireTeacher,
    requireStaff,
    clearError,
    initialize
  }
}