<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b">
        <h2 class="text-xl font-semibold text-gray-900">Create Organization</h2>
        <button 
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="p-6">
        <!-- Error Display -->
        <div v-if="error" class="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
            </svg>
            <span class="text-red-800">{{ error }}</span>
          </div>
        </div>

        <div class="space-y-4">
          <!-- Organization Name -->
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
              Organization Name *
            </label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              :class="{ 'border-red-300': errors.name }"
              placeholder="Enter organization name"
            >
            <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
          </div>

          <!-- Subdomain -->
          <div>
            <label for="subdomain" class="block text-sm font-medium text-gray-700 mb-1">
              Subdomain *
            </label>
            <div class="flex">
              <input
                id="subdomain"
                v-model="form.subdomain"
                type="text"
                required
                class="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-300': errors.subdomain }"
                placeholder="myorg"
                @input="validateSubdomain"
              >
              <span class="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 bg-gray-50 text-gray-500 text-sm rounded-r-lg">
                .edurise.com
              </span>
            </div>
            <p v-if="errors.subdomain" class="mt-1 text-sm text-red-600">{{ errors.subdomain }}</p>
            <p v-else class="mt-1 text-sm text-gray-500">
              Your organization will be accessible at {{ form.subdomain || 'subdomain' }}.edurise.com
            </p>
          </div>

          <!-- Primary Color -->
          <div>
            <label for="primaryColor" class="block text-sm font-medium text-gray-700 mb-1">
              Primary Color
            </label>
            <div class="flex items-center space-x-3">
              <input
                id="primaryColor"
                v-model="form.primary_color"
                type="color"
                class="w-12 h-10 border border-gray-300 rounded cursor-pointer"
              >
              <input
                v-model="form.primary_color"
                type="text"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="#3B82F6"
              >
            </div>
            <p class="mt-1 text-sm text-gray-500">This color will be used for branding</p>
          </div>

          <!-- Subscription Plan -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Subscription Plan
            </label>
            <div class="space-y-2">
              <label class="flex items-center">
                <input
                  v-model="form.subscription_plan"
                  type="radio"
                  value="basic"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                >
                <span class="ml-2 text-sm text-gray-700">
                  <strong>Basic</strong> - Free (Up to 50 students)
                </span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="form.subscription_plan"
                  type="radio"
                  value="pro"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                >
                <span class="ml-2 text-sm text-gray-700">
                  <strong>Pro</strong> - $29/month (Up to 500 students)
                </span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="form.subscription_plan"
                  type="radio"
                  value="premium"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                >
                <span class="ml-2 text-sm text-gray-700">
                  <strong>Premium</strong> - $99/month (Unlimited students)
                </span>
              </label>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-3 mt-8 pt-6 border-t">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            :disabled="isLoading"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="isLoading || !isFormValid"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Creating...
            </span>
            <span v-else>Create Organization</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { api } from '@/services/api'
import type { Organization } from '@/types/api'

// Emits
const emit = defineEmits<{
  close: []
  created: [tenant: Organization]
}>()

// Local state
const isLoading = ref(false)
const error = ref<string | null>(null)

// Form data
const form = reactive({
  name: '',
  subdomain: '',
  primary_color: '#3B82F6',
  subscription_plan: 'basic'
})

// Form validation
const errors = ref<Record<string, string>>({})

// Computed
const isFormValid = computed(() => {
  return form.name.trim() && 
         form.subdomain.trim() && 
         /^[a-z0-9-]+$/.test(form.subdomain) &&
         Object.keys(errors.value).length === 0
})

// Methods
const validateSubdomain = () => {
  errors.value = { ...errors.value }
  delete errors.value.subdomain

  if (form.subdomain) {
    // Convert to lowercase and remove invalid characters
    form.subdomain = form.subdomain.toLowerCase().replace(/[^a-z0-9-]/g, '')
    
    if (form.subdomain.length < 3) {
      errors.value.subdomain = 'Subdomain must be at least 3 characters'
    } else if (form.subdomain.length > 63) {
      errors.value.subdomain = 'Subdomain must be less than 63 characters'
    } else if (form.subdomain.startsWith('-') || form.subdomain.endsWith('-')) {
      errors.value.subdomain = 'Subdomain cannot start or end with a hyphen'
    } else if (['www', 'api', 'admin', 'app', 'mail', 'ftp'].includes(form.subdomain)) {
      errors.value.subdomain = 'This subdomain is reserved'
    }
  }
}

const validateForm = () => {
  errors.value = {}

  if (!form.name.trim()) {
    errors.value.name = 'Organization name is required'
  } else if (form.name.length > 100) {
    errors.value.name = 'Organization name must be less than 100 characters'
  }

  validateSubdomain()

  if (!form.primary_color || !/^#[0-9A-Fa-f]{6}$/.test(form.primary_color)) {
    errors.value.primary_color = 'Please enter a valid hex color'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  error.value = null
  
  if (!validateForm()) {
    return
  }

  try {
    isLoading.value = true
    
    const response = await api.post<Organization>('/organizations/', form)
    const newTenant = response.data.data || response.data
    
    emit('created', newTenant)
  } catch (err: any) {
    if (err.response?.data?.errors) {
      // Handle field-specific errors
      const apiErrors = err.response.data.errors
      if (apiErrors.subdomain) {
        errors.value.subdomain = apiErrors.subdomain[0]
      }
      if (apiErrors.name) {
        errors.value.name = apiErrors.name[0]
      }
    } else {
      error.value = err.response?.data?.message || err.message || 'Failed to create organization'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* Modal animations */
.fixed {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.bg-white {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>