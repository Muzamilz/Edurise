<template>
  <div id="app">
    <AppHeader />
    <main class="main-content">
      <router-view />
    </main>
    <AppFooter />
    
    <!-- AI Assistant Widget - Available on all pages -->
    <AIAssistantWidget />
    
    <!-- Toast Notifications -->
    <NotificationToast />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useTenant } from '@/composables/useTenant'
import { useAuth } from '@/composables/useAuth'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import AIAssistantWidget from '@/components/landing/AIAssistantWidget.vue'
import NotificationToast from '@/components/notifications/NotificationToast.vue'

const { initializeTenant, applyBranding } = useTenant()
const { initialize } = useAuth()

onMounted(async () => {
  // Initialize tenant detection and branding
  await initializeTenant()
  applyBranding()
  
  // Initialize authentication
  initialize()
})
</script>

<style>
:root {
  --primary-color: #f59e0b;
  --secondary-color: #d97706;
  --accent-color: #10b981;
  --text-primary: #1f2937;
  --text-secondary: #374151;
  --text-muted: #6b7280;
  --background-warm: #fef3e2;
  --background-warm-light: #fed7aa;
}

#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  background: linear-gradient(135deg, #fef3e2 0%, #ffffff 50%, #f0f9ff 100%);
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
}

/* Global button styles */
.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
  display: inline-block;
}

.btn-primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

.btn-outline {
  background: transparent;
  color: #6b7280;
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.btn-outline:hover {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  color: #374151;
  border-color: #f59e0b;
}

.btn-secondary {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  color: #92400e;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #fed7aa, #fdba74);
  border-color: #f59e0b;
}

/* Global form styles */
.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
}

.form-input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
  background: white;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
}

/* Global card styles */
.card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15);
  transform: translateY(-2px);
}
</style>