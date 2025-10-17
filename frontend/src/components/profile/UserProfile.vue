<template>
  <div class="user-profile">
    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      <p class="text-center mt-2 text-gray-600">Loading profile...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
        </svg>
        <span class="text-red-800">{{ error }}</span>
      </div>
      <button @click="clearError" class="mt-2 text-red-600 hover:text-red-800 text-sm underline">
        Dismiss
      </button>
    </div>

    <!-- Profile Content -->
    <div v-else class="profile-content">
      <!-- Profile Header -->
      <div class="profile-header bg-white rounded-lg shadow-sm border p-6 mb-6">
        <div class="flex items-start space-x-6">
          <!-- Avatar Section -->
          <div class="flex-shrink-0">
            <div class="relative">
              <img 
                :src="userProfile?.avatar || defaultAvatar" 
                :alt="fullName"
                class="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg"
              >
              <button 
                @click="triggerAvatarUpload"
                :disabled="uploadingAvatar"
                class="absolute bottom-0 right-0 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-2 shadow-lg transition-colors disabled:opacity-50"
              >
                <svg v-if="!uploadingAvatar" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </button>
              <input 
                ref="avatarInput"
                type="file"
                accept="image/*"
                @change="handleAvatarUpload"
                class="hidden"
              >
            </div>
          </div>

          <!-- User Info -->
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900">{{ fullName }}</h1>
            <p class="text-gray-600">{{ currentUser?.email }}</p>
            <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500">
              <span v-if="currentTenant" class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                </svg>
                {{ currentTenant.name }}
              </span>
              <span v-if="currentUser?.is_teacher" class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                </svg>
                Teacher
              </span>
              <span v-if="currentUser?.is_staff" class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                </svg>
                Staff
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex-shrink-0">
            <button 
              @click="showEditModal = true"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Edit Profile
            </button>
          </div>
        </div>
      </div>

      <!-- Profile Details -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Personal Information -->
        <div class="bg-white rounded-lg shadow-sm border p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Personal Information</h2>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Bio</label>
              <p class="mt-1 text-gray-900">{{ userProfile?.bio || 'No bio provided' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Phone Number</label>
              <p class="mt-1 text-gray-900">{{ userProfile?.phone_number || 'Not provided' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Date of Birth</label>
              <p class="mt-1 text-gray-900">{{ formatDate(userProfile?.date_of_birth) || 'Not provided' }}</p>
            </div>
          </div>
        </div>

        <!-- Settings -->
        <div class="bg-white rounded-lg shadow-sm border p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Settings</h2>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Timezone</label>
              <p class="mt-1 text-gray-900">{{ userProfile?.timezone || 'UTC' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Language</label>
              <p class="mt-1 text-gray-900">{{ userProfile?.language || 'English' }}</p>
            </div>
            <div class="pt-4">
              <button 
                @click="showPreferencesModal = true"
                class="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Manage Preferences
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tenant Management -->
      <div v-if="userTenants.length > 1" class="mt-6 bg-white rounded-lg shadow-sm border p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Organizations</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div 
            v-for="tenant in userTenants" 
            :key="tenant.id"
            class="border rounded-lg p-4 hover:shadow-md transition-shadow"
            :class="{ 'border-blue-500 bg-blue-50': tenant.id === currentTenant?.id }"
          >
            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-medium text-gray-900">{{ tenant.name }}</h3>
                <p class="text-sm text-gray-500">{{ tenant.subdomain }}.edurise.com</p>
              </div>
              <button 
                v-if="tenant.id !== currentTenant?.id"
                @click="handleTenantSwitch(tenant.id)"
                :disabled="isLoading"
                class="text-blue-600 hover:text-blue-800 text-sm font-medium disabled:opacity-50"
              >
                Switch
              </button>
              <span v-else class="text-blue-600 text-sm font-medium">Current</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <ProfileEditModal 
      v-if="showEditModal"
      :user-profile="userProfile"
      :current-user="currentUser"
      @close="showEditModal = false"
      @updated="handleProfileUpdated"
    />

    <!-- Preferences Modal -->
    <PreferencesModal 
      v-if="showPreferencesModal"
      @close="showPreferencesModal = false"
      @updated="handlePreferencesUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useProfile } from '@/composables/useProfile'
import ProfileEditModal from './ProfileEditModal.vue'
import PreferencesModal from './PreferencesModal.vue'

// Composables
const {
  userProfile,
  userTenants,
  isLoading,
  error,
  uploadingAvatar,
  currentUser,
  currentTenant,
  fullName,
  loadUserProfile,
  loadUserTenants,
  uploadAvatar,
  switchTenant,
  clearError
} = useProfile()

// Local state
const showEditModal = ref(false)
const showPreferencesModal = ref(false)
const avatarInput = ref<HTMLInputElement>()

// Computed
const defaultAvatar = computed(() => {
  const name = fullName.value || 'User'
  const initials = name.split(' ').map(n => n[0]).join('').toUpperCase()
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(initials)}&background=3B82F6&color=fff&size=96`
})

// Methods
const triggerAvatarUpload = () => {
  avatarInput.value?.click()
}

const handleAvatarUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    try {
      await uploadAvatar(file)
    } catch (error) {
      // Error is handled by the composable
    }
  }
  
  // Reset input
  target.value = ''
}

const handleTenantSwitch = async (tenantId: string) => {
  try {
    await switchTenant(tenantId)
    // Page will reload after tenant switch
  } catch (error) {
    // Error is handled by the composable
  }
}

const handleProfileUpdated = () => {
  showEditModal.value = false
  loadUserProfile()
}

const handlePreferencesUpdated = () => {
  showPreferencesModal.value = false
}

const formatDate = (dateString?: string) => {
  if (!dateString) return null
  return new Date(dateString).toLocaleDateString()
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadUserProfile(),
    loadUserTenants()
  ])
})
</script>

<style scoped>
.user-profile {
  max-width: 4xl;
  margin: 0 auto;
  padding: 1.5rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

@media (max-width: 768px) {
  .user-profile {
    padding: 1rem;
  }
  
  .profile-header .flex {
    flex-direction: column;
    space-x: 0;
    gap: 1rem;
  }
  
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>