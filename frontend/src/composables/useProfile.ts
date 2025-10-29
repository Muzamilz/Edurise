import { ref, computed, readonly } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { userService, type UserProfileResponse, type UserProfileUpdateData } from '@/services/userService'
import type { User, Organization } from '@/types/api'

export const useProfile = () => {
  const authStore = useAuthStore()
  
  // State
  const userProfile = ref<UserProfileResponse | null>(null)
  const userTenants = ref<Organization[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const uploadingAvatar = ref(false)

  // Computed
  const currentUser = computed(() => authStore.user)
  const currentTenant = computed(() => authStore.currentTenant)
  const fullName = computed(() => {
    if (!currentUser.value) return ''
    return `${currentUser.value.first_name} ${currentUser.value.last_name}`.trim()
  })

  // Actions
  const loadUserProfile = async (): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null
      
      userProfile.value = await userService.getUserProfile()
    } catch (err: any) {
      // If it's a "no profile found" error, set error to trigger profile creation UI
      if (err.message?.includes('No user profile found')) {
        error.value = 'profile_not_found'
      } else {
        error.value = err.response?.data?.message || err.message || 'Failed to load user profile'
      }
      console.error('Failed to load user profile:', err)
    } finally {
      isLoading.value = false
    }
  }

  const createUserProfile = async (profileData: UserProfileUpdateData): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      // Create profile with basic data (no role field - backend will handle tenant_id)
      const createData = {
        bio: profileData.bio || '',
        phone_number: profileData.phone_number || '',
        date_of_birth: profileData.date_of_birth,
        timezone: profileData.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: profileData.language || 'en'
      }

      userProfile.value = await userService.createUserProfile(createData)

      // Update user basic info if provided
      if (profileData.first_name || profileData.last_name) {
        const userData: Partial<User> = {}
        if (profileData.first_name) userData.first_name = profileData.first_name
        if (profileData.last_name) userData.last_name = profileData.last_name
        
        await userService.updateCurrentUser(userData)
        
        // Update auth store
        await authStore.getCurrentUser()
      }

    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to create profile'
      console.error('Failed to create profile:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateUserProfile = async (profileData: UserProfileUpdateData): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      if (!userProfile.value) {
        // If no profile exists, create one instead
        await createUserProfile(profileData)
        return
      }

      // Update user basic info if provided
      if (profileData.first_name || profileData.last_name) {
        const userData: Partial<User> = {}
        if (profileData.first_name) userData.first_name = profileData.first_name
        if (profileData.last_name) userData.last_name = profileData.last_name
        
        await userService.updateCurrentUser(userData)
        
        // Update auth store
        await authStore.getCurrentUser()
      }

      // Update profile-specific data
      const profileUpdateData = {
        bio: profileData.bio,
        phone_number: profileData.phone_number,
        date_of_birth: profileData.date_of_birth,
        timezone: profileData.timezone,
        language: profileData.language
      }

      userProfile.value = await userService.updateUserProfile(
        userProfile.value.id,
        profileUpdateData
      )

    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to update profile'
      console.error('Failed to update profile:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const uploadAvatar = async (file: File): Promise<void> => {
    try {
      uploadingAvatar.value = true
      error.value = null

      if (!userProfile.value) {
        throw new Error('No user profile loaded')
      }

      // Validate file
      if (!file.type.startsWith('image/')) {
        throw new Error('Please select an image file')
      }

      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        throw new Error('Image file must be less than 5MB')
      }

      const uploadResult = await userService.uploadAvatar(file)
      
      // Update profile with new avatar URL
      userProfile.value = await userService.updateUserProfile(
        userProfile.value.id,
        { avatar: uploadResult.url }
      )

    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to upload avatar'
      console.error('Failed to upload avatar:', err)
      throw err
    } finally {
      uploadingAvatar.value = false
    }
  }

  const loadUserTenants = async (): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null
      
      userTenants.value = await userService.getUserTenants()
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to load user tenants'
      console.error('Failed to load user tenants:', err)
    } finally {
      isLoading.value = false
    }
  }

  const switchTenant = async (tenantId: string): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      await userService.switchTenant(tenantId)
      
      // Update auth store with new tokens and tenant
      await authStore.switchTenant(tenantId)
      
      // Reload profile for new tenant
      await loadUserProfile()

    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to switch tenant'
      console.error('Failed to switch tenant:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const changePassword = async (currentPassword: string, newPassword: string): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      await userService.changePassword(currentPassword, newPassword)

    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to change password'
      console.error('Failed to change password:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updatePreferences = async (preferences: {
    email_notifications?: boolean
    push_notifications?: boolean
    marketing_emails?: boolean
    language?: string
    timezone?: string
    theme?: 'light' | 'dark' | 'auto'
  }): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      await userService.updatePreferences(preferences)

    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to update preferences'
      console.error('Failed to update preferences:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const exportUserData = async (): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      const blob = await userService.exportUserData()
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `user-data-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Failed to export user data'
      console.error('Failed to export user data:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const clearError = (): void => {
    error.value = null
  }

  return {
    // State
    userProfile: readonly(userProfile),
    userTenants: readonly(userTenants),
    isLoading: readonly(isLoading),
    error: readonly(error),
    uploadingAvatar: readonly(uploadingAvatar),

    // Computed
    currentUser,
    currentTenant,
    fullName,

    // Actions
    loadUserProfile,
    updateUserProfile,
    uploadAvatar,
    loadUserTenants,
    switchTenant,
    changePassword,
    updatePreferences,
    exportUserData,
    clearError
  }
}