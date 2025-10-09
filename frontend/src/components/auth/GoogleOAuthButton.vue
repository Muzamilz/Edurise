<template>
  <button
    @click="handleGoogleLogin"
    :disabled="disabled || isLoading"
    class="google-btn"
    type="button"
  >
    <svg class="google-icon" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>
    <span v-if="isLoading" class="loading-spinner"></span>
    {{ isLoading ? 'Connecting...' : 'Continue with Google' }}
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  disabled?: boolean
}

interface Emits {
  (e: 'success', accessToken: string): void
  (e: 'error', error: string): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const isLoading = ref(false)

const handleGoogleLogin = async () => {
  isLoading.value = true
  
  try {
    // Initialize Google OAuth
    if (!window.google) {
      throw new Error('Google OAuth not loaded')
    }

    // Configure Google OAuth
    const client = window.google.accounts.oauth2.initTokenClient({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      scope: 'email profile',
      callback: (response: any) => {
        if (response.access_token) {
          emit('success', response.access_token)
        } else {
          emit('error', 'Failed to get access token from Google')
        }
        isLoading.value = false
      },
      error_callback: (error: any) => {
        emit('error', error.message || 'Google OAuth failed')
        isLoading.value = false
      }
    })

    // Request access token
    client.requestAccessToken()
    
  } catch (error: any) {
    emit('error', error.message || 'Failed to initialize Google OAuth')
    isLoading.value = false
  }
}

// Load Google OAuth script if not already loaded
if (typeof window !== 'undefined' && !window.google) {
  const script = document.createElement('script')
  script.src = 'https://accounts.google.com/gsi/client'
  script.async = true
  script.defer = true
  document.head.appendChild(script)
}
</script>

<script lang="ts">
// Extend Window interface for Google OAuth
declare global {
  interface Window {
    google: any
  }
}
</script>

<style scoped>
.google-btn {
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: #374151;
}

.google-btn:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.google-btn:disabled {
  background-color: #f9fafb;
  color: #9ca3af;
  cursor: not-allowed;
}

.google-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>