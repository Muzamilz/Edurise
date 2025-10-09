<template>
  <div class="password-reset-confirm-form">
    <div class="form-header">
      <h2>Set New Password</h2>
      <p>Enter your new password below</p>
    </div>

    <form @submit.prevent="handlePasswordResetConfirm" class="auth-form">
      <div class="form-group">
        <label for="password">New Password</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          required
          :disabled="isLoading"
          placeholder="Enter your new password"
          class="form-input"
          minlength="8"
        />
        <div class="password-hint">
          Password must be at least 8 characters long
        </div>
      </div>

      <div class="form-group">
        <label for="password_confirm">Confirm New Password</label>
        <input
          id="password_confirm"
          v-model="form.password_confirm"
          type="password"
          required
          :disabled="isLoading"
          placeholder="Confirm your new password"
          class="form-input"
          :class="{ 'error': passwordMismatch }"
        />
        <div v-if="passwordMismatch" class="field-error">
          Passwords do not match
        </div>
      </div>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>
      
      <button 
        type="submit" 
        :disabled="isLoading || !isFormValid"
        class="submit-btn"
      >
        <span v-if="isLoading" class="loading-spinner"></span>
        {{ isLoading ? 'Updating Password...' : 'Update Password' }}
      </button>
    </form>

    <div class="form-footer">
      <p>
        <router-link to="/auth/login" class="login-link">
          Back to Sign In
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const router = useRouter()
const { confirmPasswordReset, isLoading, error, clearError } = useAuth()

const form = ref({
  password: '',
  password_confirm: ''
})

const successMessage = ref('')
const token = ref('')

const passwordMismatch = computed(() => {
  return form.value.password_confirm !== '' && 
         form.value.password !== form.value.password_confirm
})

const isFormValid = computed(() => {
  return form.value.password.trim() !== '' &&
         form.value.password_confirm.trim() !== '' &&
         form.value.password === form.value.password_confirm &&
         form.value.password.length >= 8
})

const handlePasswordResetConfirm = async () => {
  clearError()
  successMessage.value = ''
  
  try {
    await confirmPasswordReset(token.value, form.value.password, form.value.password_confirm)
    successMessage.value = 'Password updated successfully! Redirecting to login...'
    
    // Redirect to login after 2 seconds
    setTimeout(() => {
      router.push('/auth/login')
    }, 2000)
  } catch (err) {
    // Error is handled by the composable
  }
}

onMounted(() => {
  // Get token from URL query params
  token.value = route.query.token as string || ''
  
  if (!token.value) {
    router.push('/auth/forgot-password')
  }
})
</script>

<style scoped>
.password-reset-confirm-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-header h2 {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.form-header p {
  color: #6b7280;
  font-size: 0.875rem;
}

.auth-form {
  space-y: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input:disabled {
  background-color: #f9fafb;
  cursor: not-allowed;
}

.form-input.error {
  border-color: #dc2626;
}

.password-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.field-error {
  font-size: 0.75rem;
  color: #dc2626;
  margin-top: 0.25rem;
}

.error-message {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.success-message {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.submit-btn {
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.submit-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
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

.form-footer {
  text-align: center;
  margin-top: 1.5rem;
}

.form-footer p {
  color: #6b7280;
  font-size: 0.875rem;
}

.login-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.login-link:hover {
  color: #2563eb;
}
</style>