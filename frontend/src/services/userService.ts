import { api } from './api'
import type { User, Organization } from '@/types/api'

export interface UserProfileUpdateData {
  first_name?: string
  last_name?: string
  bio?: string
  phone_number?: string
  date_of_birth?: string
  timezone?: string
  language?: string
}

export interface UserProfileResponse {
  id: string
  user: User
  tenant: string
  tenant_name: string
  avatar?: string
  bio?: string
  phone_number?: string
  date_of_birth?: string
  timezone?: string
  language?: string
}

export interface FileUploadResponse {
  url: string
  filename: string
  size: number
  content_type: string
}

export const userService = {
  // Get current user profile
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/users/me/')
    return response.data as unknown as User
  },

  // Update current user basic info
  async updateCurrentUser(userData: Partial<User>): Promise<User> {
    const response = await api.patch<User>('/users/me/', userData)
    return response.data as unknown as User
  },

  // Get user profile for current tenant
  async getUserProfile(): Promise<UserProfileResponse> {
    console.log('🔍 Getting user profile...')
    console.log('🔍 Current tenant_id from localStorage:', localStorage.getItem('tenant_id'))
    console.log('🔍 Current user from localStorage:', localStorage.getItem('user'))
    
    const response = await api.get<UserProfileResponse[]>('/user-profiles/')
    
    console.log('🔍 API response profiles:', response.data)
    
    // Handle standardized API response format
    let profiles: UserProfileResponse[]
    if (response.data && typeof response.data === 'object' && 'data' in response.data) {
      // Standardized format: {success: true, data: [...], ...}
      profiles = (response.data as any).data
      console.log('🔍 Extracted profiles from standardized response:', profiles)
    } else {
      // Direct array format
      profiles = response.data as unknown as UserProfileResponse[]
    }
    
    // Return the first profile (current tenant)
    if (Array.isArray(profiles) && profiles.length > 0) {
      console.log('✅ Found existing user profile:', profiles[0])
      return profiles[0]
    }
    
    // If no profile exists, create one automatically
    console.log('🔧 No user profile found, creating default profile...')
    try {
      const newProfile = await this.createUserProfile({
        bio: '',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: 'en'
      })
      console.log('✅ Default user profile created:', newProfile)
      return newProfile
    } catch (error) {
      console.error('❌ Failed to create default user profile:', error)
      throw new Error('No user profile found and failed to create one')
    }
  },

  // Create user profile
  async createUserProfile(profileData: {
    bio?: string
    phone_number?: string
    timezone?: string
    language?: string
  }): Promise<UserProfileResponse> {
    const response = await api.post<UserProfileResponse>('/user-profiles/', profileData)
    return response.data as unknown as UserProfileResponse
  },

  // Update user profile
  async updateUserProfile(profileId: string, profileData: Partial<UserProfileResponse>): Promise<UserProfileResponse> {
    const response = await api.patch<UserProfileResponse>(`/user-profiles/${profileId}/`, profileData)
    return response.data as unknown as UserProfileResponse
  },

  // Upload profile avatar
  async uploadAvatar(file: File): Promise<FileUploadResponse> {
    const formData = new FormData()
    formData.append('avatar', file)
    
    const response = await api.post<FileUploadResponse>('/user-profiles/upload-avatar/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    return response.data as unknown as FileUploadResponse
  },

  // Get user tenants
  async getUserTenants(): Promise<Organization[]> {
    const response = await api.get<Organization[]>('/users/tenants/')
    return response.data as unknown as Organization[]
  },

  // Switch tenant
  async switchTenant(tenantId: string): Promise<{
    message: string
    tenant: Organization
    tokens: { access: string; refresh: string }
  }> {
    const response = await api.post<{
      message: string
      tenant: Organization
      tokens: { access: string; refresh: string }
    }>('/users/switch_tenant/', {
      tenant_id: tenantId
    })
    
    return response.data as any
  },

  // Change password
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post('/accounts/auth/password/change/', {
      old_password: currentPassword,
      new_password1: newPassword,
      new_password2: newPassword
    })
  },

  // Update user preferences
  async updatePreferences(preferences: {
    email_notifications?: boolean
    push_notifications?: boolean
    marketing_emails?: boolean
    language?: string
    timezone?: string
    theme?: 'light' | 'dark' | 'auto'
  }): Promise<void> {
    await api.patch('/users/preferences/', preferences)
  },

  // Get user activity log
  async getUserActivity(page = 1, pageSize = 20): Promise<{
    count: number
    next: string | null
    previous: string | null
    results: Array<{
      id: string
      action: string
      timestamp: string
      ip_address: string
      user_agent: string
      details?: Record<string, any>
    }>
  }> {
    const response = await api.get(`/users/activity/?page=${page}&page_size=${pageSize}`)
    return response.data as any
  },

  // Delete user account
  async deleteAccount(password: string): Promise<void> {
    await api.post('/users/delete-account/', {
      password
    })
  },

  // Export user data
  async exportUserData(): Promise<Blob> {
    const response = await api.get('/users/export-data/', {
      responseType: 'blob'
    })
    return response.data as unknown as Blob
  }
}