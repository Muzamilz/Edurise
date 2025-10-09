import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { useAuthStore } from './stores/auth'

// Import global styles
import './assets/css/main.css'

const app = createApp(App)
const pinia = createPinia()

// Setup Pinia store
app.use(pinia)

// Setup router
app.use(router)

// Initialize auth store after Pinia is set up
const authStore = useAuthStore()
authStore.initializeAuth()

app.mount('#app')