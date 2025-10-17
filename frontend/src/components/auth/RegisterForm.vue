<template>
  <div class="register-form">
    <form @submit.prevent="handleRegister" class="auth-form">
      <div class="form-row">
        <div class="form-group">
          <label for="first_name">First Name</label>
          <input
            id="first_name"
            v-model="form.first_name"
            type="text"
            required
            :disabled="isLoading"
            placeholder="Enter your first name"
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label for="last_name">Last Name</label>
          <input
            id="last_name"
            v-model="form.last_name"
            type="text"
            required
            :disabled="isLoading"
            placeholder="Enter your last name"
            class="form-input"
          />
        </div>
      </div>

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
      
      <div class="form-group">
        <label for="password">Password</label>
        <div class="password-input-container">
          <input
            id="password"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            required
            :disabled="isLoading"
            placeholder="Create a password"
            class="form-input password-input"
            minlength="8"
          />
          <button
            type="button"
            @click="togglePasswordVisibility"
            class="password-toggle"
            :disabled="isLoading"
          >
            <svg v-if="showPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
              <line x1="1" y1="1" x2="23" y2="23"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </button>
        </div>
        <div class="password-hint">
          Password must be at least 8 characters long
        </div>
      </div>

      <div class="form-group">
        <label for="password_confirm">Confirm Password</label>
        <div class="password-input-container">
          <input
            id="password_confirm"
            v-model="form.password_confirm"
            :type="showConfirmPassword ? 'text' : 'password'"
            required
            :disabled="isLoading"
            placeholder="Confirm your password"
            class="form-input password-input"
            :class="{ 'error': passwordMismatch }"
          />
          <button
            type="button"
            @click="toggleConfirmPasswordVisibility"
            class="password-toggle"
            :disabled="isLoading"
          >
            <svg v-if="showConfirmPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
              <line x1="1" y1="1" x2="23" y2="23"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </button>
        </div>
        <div v-if="passwordMismatch" class="field-error">
          Passwords do not match
        </div>
      </div>

      <div class="form-group">
        <label class="checkbox-label">
          <input
            v-model="form.is_teacher"
            type="checkbox"
            :disabled="isLoading"
            class="checkbox-input"
          />
          <span class="checkbox-text">
            I want to apply as a teacher
          </span>
        </label>
        <div class="checkbox-hint">
          Teachers can create and sell courses on our marketplace
        </div>
      </div>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <button 
        type="submit" 
        :disabled="isLoading || !isFormValid"
        class="submit-btn"
      >
        <span v-if="isLoading" class="loading-spinner"></span>
        {{ isLoading ? 'Creating Account...' : 'Create Account' }}
      </button>
    </form>

    <div class="divider">
      <span>or</span>
    </div>

    <GoogleOAuthButton @success="handleGoogleSuccess" :disabled="isLoading" />


  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import GoogleOAuthButton from './GoogleOAuthButton.vue'

const { register, loginWithGoogle, isLoading, error, clearError } = useAuth()

const form = ref({
  email: '',
  password: '',
  password_confirm: '',
  first_name: '',
  last_name: '',
  is_teacher: false
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const toggleConfirmPasswordVisibility = () => {
  showConfirmPassword.value = !showConfirmPassword.value
}

const passwordMismatch = computed(() => {
  return form.value.password_confirm !== '' && 
         form.value.password !== form.value.password_confirm
})

const isFormValid = computed(() => {
  return form.value.email.trim() !== '' && 
         form.value.password.trim() !== '' &&
         form.value.password_confirm.trim() !== '' &&
         form.value.first_name.trim() !== '' &&
         form.value.last_name.trim() !== '' &&
         form.value.password === form.value.password_confirm &&
         form.value.password.length >= 8
})

const handleRegister = async () => {
  clearError()
  try {
    await register(form.value)
  } catch (err) {
    // Error is handled by the composable
  }
}

const handleGoogleSuccess = async (accessToken: string) => {
  clearError()
  try {
    await loginWithGoogle(accessToken)
  } catch (err) {
    // Error is handled by the composable
  }
}
</script>

<style scoped>
.register-form {
  width: 100%;
}



.auth-form {
  space-y: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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

.password-input-container {
  position: relative;
}

.password-input {
  padding-right: 3rem;
}

.password-toggle {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7280;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.password-toggle:hover {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.password-toggle:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.form-input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
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

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.checkbox-input {
  margin-top: 0.125rem;
  flex-shrink: 0;
}

.checkbox-text {
  color: #374151;
  font-weight: 500;
}

.checkbox-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
  margin-left: 1.5rem;
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

.submit-btn {
  width: 100%;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
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

.divider {
  position: relative;
  margin: 1.5rem 0;
  text-align: center;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background-color: #e5e7eb;
}

.divider span {
  background-color: white;
  color: #6b7280;
  padding: 0 1rem;
  font-size: 0.875rem;
}



@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .register-form {
    padding: 1.5rem;
  }
}
</style>