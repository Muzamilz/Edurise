<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-brand">
        <h1>Edurise</h1>
        <p>Your gateway to knowledge</p>
      </div>
      
      <LoginForm />
    </div>
  </div>
</template>

<script setup lang="ts">
import LoginForm from '@/components/auth/LoginForm.vue'
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #92400e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  position: relative;
}

.auth-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(254, 243, 226, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.auth-container {
  width: 100%;
  max-width: 400px;
}

.auth-brand {
  text-align: center;
  margin-bottom: 2rem;
  color: white;
}

.auth-brand h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.auth-brand p {
  font-size: 1.125rem;
  opacity: 0.9;
}
</style>