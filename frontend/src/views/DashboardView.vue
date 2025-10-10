<template>
  <div class="dashboard-container">
    <!-- Super Admin Dashboard -->
    <SuperAdminDashboard v-if="isSuperuser" />
    
    <!-- Admin Dashboard -->
    <AdminDashboard v-else-if="isStaff" />
    
    <!-- Teacher Dashboard -->
    <TeacherDashboard v-else-if="isTeacher" />
    
    <!-- Student Dashboard (Default) -->
    <StudentDashboard v-else />

    <!-- Tenant Switcher (Global) -->
    <div v-if="currentTenant && userTenants.length > 1" class="tenant-switcher-global">
      <div class="tenant-switcher-card">
        <h3>Organization: {{ currentTenant.name }}</h3>
        <div class="tenant-switcher">
          <label for="tenant-select">Switch Organization:</label>
          <select 
            id="tenant-select" 
            @change="handleTenantSwitch"
            :value="currentTenant.id"
          >
            <option 
              v-for="tenant in userTenants" 
              :key="tenant.id" 
              :value="tenant.id"
            >
              {{ tenant.name }}
            </option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// import { computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import StudentDashboard from '@/components/dashboard/StudentDashboard.vue'
import TeacherDashboard from '@/components/dashboard/TeacherDashboard.vue'
import AdminDashboard from '@/components/dashboard/AdminDashboard.vue'
import SuperAdminDashboard from '@/components/dashboard/SuperAdminDashboard.vue'

const { 
  // user,
  isTeacher, 
  isStaff,
  isSuperuser,
  currentTenant, 
  userTenants, 
  switchTenant 
} = useAuth()

// const currentDashboard = computed(() => {
//   if (isSuperuser.value) return 'SuperAdmin'
//   if (isStaff.value) return 'Admin'
//   if (isTeacher.value) return 'Teacher'
//   return 'Student'
// })

const handleTenantSwitch = async (event: Event) => {
  const target = event.target as HTMLSelectElement
  const tenantId = target.value
  
  if (tenantId !== currentTenant.value?.id) {
    try {
      await switchTenant(tenantId)
    } catch (error) {
      console.error('Failed to switch tenant:', error)
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
}

.tenant-switcher-global {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 40;
}

.tenant-switcher-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(254, 243, 226, 0.3));
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.2);
  backdrop-filter: blur(10px);
  min-width: 250px;
}

.tenant-switcher-card h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.75rem;
}

.tenant-switcher {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tenant-switcher label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tenant-switcher select {
  padding: 0.5rem;
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 6px;
  background: white;
  transition: all 0.3s ease;
  font-size: 0.875rem;
}

.tenant-switcher select:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

/* Responsive */
@media (max-width: 768px) {
  .tenant-switcher-global {
    position: static;
    margin: 1rem;
  }
  
  .tenant-switcher-card {
    min-width: auto;
  }
}
</style>