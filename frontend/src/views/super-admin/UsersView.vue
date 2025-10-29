<template>
  <div class="super-admin-users-view">
    <div class="page-header">
      <h1>Global User Management</h1>
      <p>Manage all users across the platform</p>
    </div>

    <!-- Global User Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <h3>Total Users</h3>
        <p class="stat-number">{{ formatNumber(totalUsers) }}</p>
        <span class="stat-change positive">+12% this month</span>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👨‍🎓</div>
        <h3>Students</h3>
        <p class="stat-number">{{ formatNumber(totalStudents) }}</p>
        <span class="stat-change positive">85% of users</span>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👨‍🏫</div>
        <h3>Teachers</h3>
        <p class="stat-number">{{ formatNumber(totalTeachers) }}</p>
        <span class="stat-change positive">12% of users</span>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👨‍💼</div>
        <h3>Admins</h3>
        <p class="stat-number">{{ formatNumber(totalAdmins) }}</p>
        <span class="stat-change neutral">3% of users</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading users...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load users</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- User Management Interface -->
    <div v-else class="users-container">
      <div class="users-header">
        <h2>Platform Users</h2>
        <div class="header-controls">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search users..."
            class="search-input"
          />
          <select v-model="roleFilter" class="filter-select">
            <option value="">All Roles</option>
            <option value="student">Students</option>
            <option value="teacher">Teachers</option>
            <option value="admin">Admins</option>
          </select>
          <select v-model="organizationFilter" class="filter-select">
            <option value="">All Organizations</option>
            <option v-for="org in organizations" :key="org.id" :value="org.id">
              {{ org.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Users Table -->
      <div class="users-table">
        <table>
          <thead>
            <tr>
              <th>User</th>
              <th>Role</th>
              <th>Organization</th>
              <th>Status</th>
              <th>Joined</th>
              <th>Last Active</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedUsers" :key="user.id" class="user-row">
              <td class="user-info">
                <div class="user-avatar">
                  <img :src="user.avatar || '/default-avatar.jpg'" :alt="user.name" />
                </div>
                <div class="user-details">
                  <h4>{{ user.first_name }} {{ user.last_name }}</h4>
                  <p>{{ user.email }}</p>
                </div>
              </td>
              <td>
                <span class="role-badge" :class="user.role">
                  {{ formatRole(user.role) }}
                </span>
              </td>
              <td>{{ user.organization?.name || 'No Organization' }}</td>
              <td>
                <span class="status-badge" :class="user.is_active ? 'active' : 'inactive'">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>{{ formatDate(user.date_joined) }}</td>
              <td>{{ formatDate(user.last_login) }}</td>
              <td class="actions">
                <button @click="viewUser(user)" class="action-btn view">View</button>
                <button @click="toggleUserStatus(user)" :class="['action-btn', user.is_active ? 'suspend' : 'activate']">
                  {{ user.is_active ? 'Suspend' : 'Activate' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pagination">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="pagination-btn"
        >
          Previous
        </button>
        <span class="pagination-info">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="pagination-btn"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
// import { useRouter } from 'vue-router'
import { useApiData, useApiMutation } from '@/composables/useApiData'
import type { APIError } from '@/services/api'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { api } from '@/services/api'

// const router = useRouter() // Unused for now
const { handleApiError } = useErrorHandler()

// Reactive state
const searchQuery = ref('')
const roleFilter = ref('')
const organizationFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 20

// API data
const { data: usersData, loading, error, refresh } = useApiData<any[]>('/users/', {
  immediate: true,
  transform: (data) => {
    console.log('🔍 Raw users data:', data)
    
    // Handle both paginated and direct array responses
    const results = data.results || data.data || data || []
    
    return results.map((user: any) => {
      // Determine user role based on flags
      let role = 'student'
      if (user.is_superuser) role = 'superuser'
      else if (user.is_staff) role = 'admin'
      else if (user.is_teacher) role = 'teacher'
      
      return {
        id: user.id,
        first_name: user.first_name || 'Unknown',
        last_name: user.last_name || 'User',
        email: user.email,
        role: role,
        organization: user.organization_name || 'No Organization',
        is_active: user.is_active !== false,
        date_joined: user.date_joined,
        last_login: user.last_login,
        avatar: user.avatar || null,
        is_teacher: user.is_teacher,
        is_approved_teacher: user.is_approved_teacher,
        is_staff: user.is_staff,
        is_superuser: user.is_superuser
      }
    })
  },
  retryAttempts: 3,
  onError: (error) => {
    console.error('Failed to load users:', error)
  }
})

const { data: organizationsData } = useApiData<any[]>('/organizations/', {
  immediate: true,
  transform: (data) => {
    console.log('🔍 Raw organizations data:', data)
    
    // Handle both paginated and direct array responses
    const results = data.results || data.data || data || []
    
    return results.map((org: any) => ({
      id: org.id,
      name: org.name || 'Unknown Organization'
    }))
  }
})

// Computed properties
const users = computed(() => usersData.value || [])
const organizations = computed(() => organizationsData.value || [])

const totalUsers = computed(() => users.value.length)
const totalStudents = computed(() => users.value.filter((u: any) => u.role === 'student').length)
const totalTeachers = computed(() => users.value.filter((u: any) => u.role === 'teacher').length)
const totalAdmins = computed(() => users.value.filter((u: any) => u.role === 'admin').length)

// Mutations
const { mutate: updateUser } = useApiMutation(
  ({ id, ...data }) => api.patch(`/users/${id}/`, data),
  {
    onSuccess: () => refresh(),
    onError: (error) => handleApiError(error as APIError, { context: { action: 'update_user' } })
  }
)

const filteredUsers = computed(() => {
  return users.value.filter((user: any) => {
    const matchesSearch = !searchQuery.value || 
      user.first_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      user.last_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesRole = !roleFilter.value || user.role === roleFilter.value
    const matchesOrg = !organizationFilter.value || user.organization?.id === parseInt(organizationFilter.value)
    
    return matchesSearch && matchesRole && matchesOrg
  })
})

const totalPages = computed(() => Math.ceil(filteredUsers.value.length / itemsPerPage))

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredUsers.value.slice(start, end)
})

const formatNumber = (num: number) => {
  return new Intl.NumberFormat().format(num)
}

const formatRole = (role: string) => {
  return role.charAt(0).toUpperCase() + role.slice(1)
}

const formatDate = (date: string) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleDateString()
}

const viewUser = (user: any) => {
  // Navigate to user detail view
  console.log('View user:', user)
}

const toggleUserStatus = async (user: any) => {
  const action = user.is_active ? 'suspend' : 'activate'
  if (confirm(`Are you sure you want to ${action} ${user.first_name} ${user.last_name}?`)) {
    await updateUser({ id: user.id, is_active: !user.is_active })
  }
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as any, { context: { action: 'retry_users_load' } })
  }
}

onMounted(() => {
  // Data is loaded automatically via useApiData
})
</script>

<style scoped>
.super-admin-users-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: #6b7280;
  font-size: 1.125rem;
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(243, 232, 255, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.1);
  text-align: center;
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.stat-card h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #7c3aed;
  margin: 0 0 0.25rem 0;
}

.stat-change {
  font-size: 0.75rem;
  font-weight: 500;
}

.stat-change.positive {
  color: #10b981;
}

.stat-change.neutral {
  color: #6b7280;
}

.users-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.users-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.header-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  min-width: 200px;
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  min-width: 120px;
}

.users-table {
  overflow-x: auto;
}

.users-table table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  background: #f9fafb;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.user-row:hover {
  background: #f9fafb;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.user-details p {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.role-badge, .status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.role-badge.student {
  background: #dbeafe;
  color: #1e40af;
}

.role-badge.teacher {
  background: #fef3c7;
  color: #92400e;
}

.role-badge.admin {
  background: #f3e8ff;
  color: #5b21b6;
}

.status-badge.active {
  background: #dcfce7;
  color: #166534;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #dc2626;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.25rem 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.view {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.view:hover {
  background: #bfdbfe;
}

.action-btn.activate {
  background: #dcfce7;
  color: #166534;
}

.action-btn.activate:hover {
  background: #bbf7d0;
}

.action-btn.suspend {
  background: #fee2e2;
  color: #dc2626;
}

.action-btn.suspend:hover {
  background: #fecaca;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #7c3aed;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Loading and Error States */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(243, 232, 255, 0.3));
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.1);
  border: 1px solid rgba(124, 58, 237, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #7c3aed;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  color: #6b7280;
  font-size: 1rem;
  margin: 0;
}

.error-state .error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 0.5rem;
}

.error-state p {
  color: #6b7280;
  margin-bottom: 1.5rem;
  max-width: 400px;
}

.retry-btn {
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
}
</style>