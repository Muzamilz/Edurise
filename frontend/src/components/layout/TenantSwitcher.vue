<template>
  <div class="relative" v-if="userTenants.length > 1">
    <!-- Trigger Button -->
    <button
      @click="showDropdown = !showDropdown"
      class="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      :disabled="isLoading"
    >
      <div class="flex items-center space-x-2">
        <div 
          class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
          :style="{ backgroundColor: currentTenant?.primary_color || '#3B82F6' }"
        >
          {{ currentTenant?.name?.charAt(0).toUpperCase() || 'T' }}
        </div>
        <span class="hidden sm:block">{{ currentTenant?.name || 'Select Organization' }}</span>
      </div>
      <svg 
        class="w-4 h-4 transition-transform duration-200"
        :class="{ 'rotate-180': showDropdown }"
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
      </svg>
    </button>

    <!-- Dropdown Menu -->
    <div 
      v-if="showDropdown"
      class="absolute right-0 mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50"
      @click.stop
    >
      <!-- Header -->
      <div class="px-4 py-3 border-b border-gray-200">
        <p class="text-sm font-medium text-gray-900">Switch Organization</p>
        <p class="text-xs text-gray-500">Choose which organization to work with</p>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="px-4 py-2 bg-red-50 border-b border-red-200">
        <p class="text-sm text-red-800">{{ error }}</p>
      </div>

      <!-- Tenant List -->
      <div class="max-h-64 overflow-y-auto">
        <button
          v-for="tenant in userTenants"
          :key="tenant.id"
          @click="handleTenantSwitch(tenant)"
          :disabled="isLoading || tenant.id === currentTenant?.id"
          class="w-full px-4 py-3 text-left hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          :class="{ 'bg-blue-50 border-l-4 border-blue-500': tenant.id === currentTenant?.id }"
        >
          <div class="flex items-center space-x-3">
            <!-- Tenant Avatar -->
            <div 
              class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold text-white flex-shrink-0"
              :style="{ backgroundColor: tenant.primary_color || '#3B82F6' }"
            >
              {{ tenant.name.charAt(0).toUpperCase() }}
            </div>
            
            <!-- Tenant Info -->
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">
                {{ tenant.name }}
              </p>
              <p class="text-xs text-gray-500 truncate">
                {{ tenant.subdomain }}.edurise.com
              </p>
              <div class="flex items-center mt-1">
                <span 
                  class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                  :class="tenant.subscription_plan === 'enterprise' 
                    ? 'bg-yellow-100 text-yellow-800' 
                    : tenant.subscription_plan === 'pro'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-800'"
                >
                  {{ tenant.subscription_plan || 'basic' }}
                </span>
              </div>
            </div>

            <!-- Current Indicator -->
            <div v-if="tenant.id === currentTenant?.id" class="flex-shrink-0">
              <svg class="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
              </svg>
            </div>

            <!-- Loading Indicator -->
            <div v-else-if="isLoading && switchingToTenant === tenant.id" class="flex-shrink-0">
              <svg class="w-4 h-4 animate-spin text-blue-500" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
          </div>
        </button>
      </div>

      <!-- Footer -->
      <div class="px-4 py-3 border-t border-gray-200 bg-gray-50">
        <button
          @click="showCreateTenantModal = true"
          class="w-full text-left text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          + Create New Organization
        </button>
      </div>
    </div>

    <!-- Backdrop -->
    <div 
      v-if="showDropdown"
      class="fixed inset-0 z-40"
      @click="showDropdown = false"
    ></div>

    <!-- Create Tenant Modal -->
    <CreateTenantModal 
      v-if="showCreateTenantModal"
      @close="showCreateTenantModal = false"
      @created="handleTenantCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useProfile } from '@/composables/useProfile'
import CreateTenantModal from './CreateTenantModal.vue'
import type { Organization } from '@/types/api'

// Stores and composables
const authStore = useAuthStore()
const { 
  userTenants, 
  isLoading, 
  error, 
  loadUserTenants, 
  switchTenant,
  clearError 
} = useProfile()

// Local state
const showDropdown = ref(false)
const showCreateTenantModal = ref(false)
const switchingToTenant = ref<string | null>(null)

// Computed
const currentTenant = computed(() => authStore.currentTenant)

// Methods
const handleTenantSwitch = async (tenant: Organization) => {
  if (tenant.id === currentTenant.value?.id || isLoading.value) {
    return
  }

  try {
    clearError()
    switchingToTenant.value = tenant.id
    showDropdown.value = false
    
    await switchTenant(tenant.id)
    
    // The page will reload after successful tenant switch
  } catch (err) {
    console.error('Failed to switch tenant:', err)
    // Error is handled by the composable
  } finally {
    switchingToTenant.value = null
  }
}

const handleTenantCreated = (_newTenant: Organization) => {
  showCreateTenantModal.value = false
  loadUserTenants()
}

const handleClickOutside = (event: Event) => {
  const target = event.target as Element
  if (!target.closest('.relative')) {
    showDropdown.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await loadUserTenants()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Dropdown animation */
.absolute {
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .absolute {
    right: 0;
    left: 0;
    width: auto;
  }
}
</style>