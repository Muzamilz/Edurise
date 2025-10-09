<template>
  <header class="app-header">
    <div class="container">
      <div class="header-content">
        <!-- Logo -->
        <router-link to="/" class="logo">
          <span class="logo-text">{{ branding.name }}</span>
          <div class="logo-dot"></div>
        </router-link>

        <!-- Navigation -->
        <nav class="nav-links" v-if="!isAuthPage">
          <router-link to="/" class="nav-link">Home</router-link>
          <router-link to="/courses" class="nav-link">Courses</router-link>
          <router-link to="/about" class="nav-link" v-if="!currentTenant">About</router-link>
          <router-link to="/contact" class="nav-link" v-if="!currentTenant">Contact</router-link>
        </nav>

        <!-- User Menu -->
        <div class="user-menu">
          <!-- Authenticated User -->
          <div v-if="isAuthenticated" class="user-dropdown">
            <button @click="toggleDropdown" class="user-button">
              <div class="user-avatar">
                {{ userInitials }}
              </div>
              <span class="user-name">{{ fullName }}</span>
              <svg class="dropdown-icon" :class="{ 'rotate': showDropdown }" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M4.427 9.573L8 6l3.573 3.573a.5.5 0 0 0 .708-.708l-4-4a.5.5 0 0 0-.708 0l-4 4a.5.5 0 1 0 .708.708z"/>
              </svg>
            </button>
            
            <!-- Dropdown Menu -->
            <div v-if="showDropdown" class="dropdown-menu" @click="closeDropdown">
              <div class="dropdown-header">
                <div class="user-info">
                  <div class="user-name-full">{{ fullName }}</div>
                  <div class="user-email">{{ user?.email }}</div>
                </div>
              </div>
              
              <div class="dropdown-divider"></div>
              
              <router-link to="/dashboard" class="dropdown-item">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                  <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
                </svg>
                Dashboard
              </router-link>
              
              <router-link v-if="isTeacher" to="/teacher/courses" class="dropdown-item">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                  <path d="M8.5 2.687c.654-.689 1.782-.886 3.112-.752 1.234.124 2.503.523 3.388.893v9.923c-.918-.35-2.107-.692-3.287-.81-1.094-.111-2.278-.039-3.213.492V2.687zM8 1.783C7.015.936 5.587.81 4.287.94c-1.514.153-3.042.672-3.994 1.105A.5.5 0 0 0 0 2.5v11a.5.5 0 0 0 .707.455c.882-.4 2.303-.881 3.68-1.02 1.409-.142 2.59.087 3.223.877a.5.5 0 0 0 .78 0c.633-.79 1.814-1.019 3.222-.877 1.378.139 2.8.62 3.681 1.02A.5.5 0 0 0 16 13.5v-11a.5.5 0 0 0-.293-.455c-.952-.433-2.48-.952-3.994-1.105C10.413.809 8.985.936 8 1.783z"/>
                </svg>
                My Courses
              </router-link>
              
              <router-link v-if="isTeacher" to="/teacher/courses/create" class="dropdown-item">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                  <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
                </svg>
                Create Course
              </router-link>
              
              <!-- Tenant Switcher -->
              <div v-if="userTenants.length > 1" class="dropdown-divider"></div>
              <div v-if="userTenants.length > 1" class="dropdown-section">
                <div class="dropdown-section-title">Switch Organization</div>
                <button 
                  v-for="tenant in userTenants" 
                  :key="tenant.id"
                  @click="handleTenantSwitch(tenant.id)"
                  class="dropdown-item"
                  :class="{ 'active': currentTenant?.id === tenant.id }"
                >
                  <div class="tenant-info">
                    <div class="tenant-name">{{ tenant.name }}</div>
                    <div class="tenant-plan">{{ tenant.subscription_plan }}</div>
                  </div>
                  <svg v-if="currentTenant?.id === tenant.id" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/>
                  </svg>
                </button>
              </div>
              
              <div class="dropdown-divider"></div>
              
              <button @click="handleLogout" class="dropdown-item logout">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"/>
                  <path fill-rule="evenodd" d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/>
                </svg>
                Sign Out
              </button>
            </div>
          </div>

          <!-- Guest User -->
          <div v-else class="auth-buttons">
            <router-link to="/auth/login" class="btn btn-outline">Sign In</router-link>
            <router-link to="/auth/register" class="btn btn-primary">Sign Up</router-link>
          </div>
        </div>

        <!-- Mobile Menu Button -->
        <button @click="toggleMobileMenu" class="mobile-menu-btn" v-if="!isAuthPage">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 12h18m-9 9l9-9-9-9" v-if="showMobileMenu"/>
            <path d="M3 6h18M3 12h18M3 18h18" v-else/>
          </svg>
        </button>
      </div>

      <!-- Mobile Menu -->
      <div v-if="showMobileMenu && !isAuthPage" class="mobile-menu">
        <nav class="mobile-nav">
          <router-link to="/" class="mobile-nav-link" @click="closeMobileMenu">Home</router-link>
          <router-link to="/courses" class="mobile-nav-link" @click="closeMobileMenu">Courses</router-link>
          <router-link to="/about" class="mobile-nav-link" @click="closeMobileMenu" v-if="!currentTenant">About</router-link>
          <router-link to="/contact" class="mobile-nav-link" @click="closeMobileMenu" v-if="!currentTenant">Contact</router-link>
        </nav>
        
        <div v-if="!isAuthenticated" class="mobile-auth">
          <router-link to="/auth/login" class="btn btn-outline" @click="closeMobileMenu">Sign In</router-link>
          <router-link to="/auth/register" class="btn btn-primary" @click="closeMobileMenu">Sign Up</router-link>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTenant } from '@/composables/useTenant'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { branding, currentTenant } = useTenant()

// Local state
const showDropdown = ref(false)
const showMobileMenu = ref(false)

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)
const isTeacher = computed(() => authStore.isTeacher)
const user = computed(() => authStore.user)
const fullName = computed(() => authStore.fullName)
const userTenants = computed(() => authStore.userTenants)

const userInitials = computed(() => {
  if (!user.value) return 'U'
  const first = user.value.first_name?.[0] || ''
  const last = user.value.last_name?.[0] || ''
  return (first + last).toUpperCase() || user.value.email[0].toUpperCase()
})

const isAuthPage = computed(() => {
  return route.path.startsWith('/auth/')
})

// Methods
const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const closeDropdown = () => {
  showDropdown.value = false
}

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

const closeMobileMenu = () => {
  showMobileMenu.value = false
}

const handleTenantSwitch = async (tenantId: string) => {
  try {
    await authStore.switchTenant(tenantId)
    closeDropdown()
    // Refresh the page to apply new tenant context
    window.location.reload()
  } catch (error) {
    console.error('Failed to switch tenant:', error)
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    closeDropdown()
    router.push('/')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}

// Close dropdowns when clicking outside
const handleClickOutside = (event: Event) => {
  const target = event.target as Element
  if (!target.closest('.user-dropdown')) {
    showDropdown.value = false
  }
  if (!target.closest('.mobile-menu-btn') && !target.closest('.mobile-menu')) {
    showMobileMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(254, 243, 226, 0.5);
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: 0 1px 3px rgba(245, 158, 11, 0.1);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 4rem;
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.logo-text {
  margin-right: 0.25rem;
}

.logo-dot {
  width: 8px;
  height: 8px;
  background: var(--accent-color);
  border-radius: 50%;
}

/* Navigation */
.nav-links {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-link {
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
  position: relative;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--primary-color);
}

.nav-link.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -1rem;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--primary-color);
}

/* User Menu */
.user-menu {
  display: flex;
  align-items: center;
}

.user-dropdown {
  position: relative;
}

.user-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: background-color 0.2s ease;
}

.user-button:hover {
  background: var(--background-warm);
}

.user-avatar {
  width: 2rem;
  height: 2rem;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
}

.user-name {
  font-weight: 500;
  color: var(--text-secondary);
}

.dropdown-icon {
  transition: transform 0.2s ease;
}

.dropdown-icon.rotate {
  transform: rotate(180deg);
}

/* Dropdown Menu */
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  min-width: 16rem;
  z-index: 50;
  margin-top: 0.5rem;
}

.dropdown-header {
  padding: 1rem;
}

.user-info {
  text-align: left;
}

.user-name-full {
  font-weight: 600;
  color: #111827;
}

.user-email {
  font-size: 0.875rem;
  color: #6b7280;
}

.dropdown-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 0.5rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  text-decoration: none;
  color: #374151;
  background: none;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 0.875rem;
}

.dropdown-item:hover {
  background: var(--background-warm);
}

.dropdown-item.active {
  background: linear-gradient(135deg, var(--background-warm), var(--background-warm-light));
  color: var(--primary-color);
}

.dropdown-item.logout {
  color: #dc2626;
}

.dropdown-item.logout:hover {
  background: #fef2f2;
}

.dropdown-section {
  padding: 0.5rem 0;
}

.dropdown-section-title {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tenant-info {
  flex: 1;
  text-align: left;
}

.tenant-name {
  font-weight: 500;
}

.tenant-plan {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: capitalize;
}

/* Auth Buttons */
.auth-buttons {
  display: flex;
  gap: 0.75rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
}

.btn-outline {
  background: transparent;
  color: #6b7280;
  border: 1px solid rgba(245, 158, 11, 0.4);
  font-weight: 600;
}

.btn-outline:hover {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  color: #374151;
  border-color: #f59e0b;
}

.btn-primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
  font-weight: 600;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

/* Mobile Menu */
.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  transition: color 0.3s ease;
}

.mobile-menu-btn:hover {
  color: var(--primary-color);
}

.mobile-menu {
  display: none;
  padding: 1rem 0;
  border-top: 1px solid rgba(245, 158, 11, 0.2);
  background: linear-gradient(135deg, rgba(254, 243, 226, 0.8), rgba(255, 255, 255, 0.9));
}

.mobile-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.mobile-nav-link {
  padding: 0.75rem 0;
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500;
  border-bottom: 1px solid rgba(245, 158, 11, 0.1);
}

.mobile-nav-link:hover,
.mobile-nav-link.router-link-active {
  color: var(--primary-color);
}

.mobile-auth {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
  
  .mobile-menu-btn {
    display: block;
  }
  
  .mobile-menu {
    display: block;
  }
  
  .user-name {
    display: none;
  }
  
  .auth-buttons {
    flex-direction: column;
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .header-content {
    height: 3.5rem;
  }
  
  .logo {
    font-size: 1.25rem;
  }
  
  .container {
    padding: 0 0.75rem;
  }
}
</style>