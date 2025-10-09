<template>
  <div class="password-reset-form">
    <div class="form-header">
      <h2>Reset Password</h2>
      <p>Enter your email address and we'll send you a link to reset your password</p>
    </div>

    <form @submit.prevent="handlePasswordReset" class="auth-form">
      <div class="form-group">
        <label for="email">Email Address</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          required
          :disabled="isLoading"
          placeholder="Enter your email"
          class="form-input"
        />
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
        {{ isLoading ? 'Sending...' : 'Send Reset Link' }}
      </button>
    </form>

    <div class="form-footer">
      <p>
        Remember your password? 
        <router-link to="/auth/login" class="login-link">
          Sign in here
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { requestPasswordReset, isLoading, error, clearError } = useAuth()

const form = ref({
  email: ''
})

const successMessage = ref('')

const isFormValid = computed(() => {
  return form.value.email.trim() !== ''
})

const handlePasswordReset = async () => {
  clearError()
  successMessage.value = ''
  
  try {
    await requestPasswordReset(form.value.email)
    successMessage.value = 'If an account with that email exists, we\'ve sent you a password reset link.'
    form.value.email = ''
  } catch (err) {
    // Error is handled by the composable
  }
}
</script>

<style scoped>
.password-reset-form {
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
  line-height: 1.5;
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