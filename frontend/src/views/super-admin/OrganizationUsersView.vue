<template>
  <div class="organization-users-view">
    <div class="page-header">
      <div class="header-content">
        <router-link :to="`/super-admin/organizations/${organizationId}`" class="back-link">
          ← Back to Organization
        </router-link>
        <h1>{{ organization?.name || 'Loading...' }} - Users</h1>
        <p class="header-description">
          Manage users for this organization
        </p>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading users...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load users</h3>
      <p>{{ error.message }}</p>
      <button @click="loadUsers" class="retry-btn">Try Again</button>
    </div>

    <div v-else class="users-content">
      <!-- Users Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon total">
            <i class="fas fa-users"></i>
          </div>
          <div class="stat-content">
            <h3>{{ users.length }}</h3>
            <p>Total Users</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon students">
            <i class="fas fa-user-graduate"></i>
          </div>
          <div class="stat-content">
            <h3>{{ students.length }}</h3>
            <p>Students</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon teachers">
            <i class="fas fa-chalkboard-teacher"></i>
          </div>
          <div class="stat-content">
            <h3>{{ teachers.length }}</h3>
            <p>Teachers</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon admins">
            <i class="fas fa-user-shield"></i>
          </div>
          <div class="stat-content">
            <h3>{{ admins.length }}</h3>
            <p>Admins</p>
          </div>
        </div>
      </div>

      <!-- Filters and Search -->
      <div class="filters-section">
        <div class="search-bar">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search users..."
            class="search-input"
          />
        </div>
        <div class="filter-controls">
          <select v-model="roleFilter" class="filter-select">
            <option value="">All Roles</option>
            <option value="student">Students</option>
            <option value="teacher">Teachers</option>
            <option value="admin">Admins</option>
          </select>
          <select v-model="statusFilter" class="filter-select">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      <!-- Users List -->
      <div class="users-list">
        <div class="list-header">
          <h3>Users ({{ filteredUsers.length }})</h3>
        </div>
        
        <div v-if="filteredUsers.length === 0" class="empty-state">
          <i class="fas fa-users"></i>
          <h4>No users found</h4>
          <p>No users match your current filters.</p>
        </div>

        <div v-else class="users-grid">
          <div
            v-for="user in paginatedUsers"
            :key="user.id"
            class="user-card"
          >
            <div class="user-avatar">
              <img
                v-if="user.avatar"
                :src="user.avatar"
                :alt="user.full_name"
                class="avatar-image"
              />
              <div v-else class="avatar-placeholder">
                {{ user.full_name?.charAt(0) || user.email.charAt(0) }}
              </div>
            </div>
            
            <div class="user-info">
              <h4>{{ user.full_name || `${user.first_name} ${user.last_name}` }}</h4>
              <p class="user-email">{{ user.email }}</p>
              <div class="user-meta">
                <span class="role-badge" :class="user.role">
                  {{ user.role }}
                </span>
                <span class="status-badge" :class="user.is_active ? 'active' : 'inactive'">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <div class="user-details">
                <small>Joined: {{ formatDate(user.created_at) }}</small>
                <small v-if="user.last_seen">Last seen: {{ formatDate(user.last_seen) }}</small>
              </div>
            </div>

            <div class="user-actions">
              <button
                @click="viewUserDetails(user)"
                class="action-btn view"
                title="View Details"
              >
                <i class="fas fa-eye"></i>
              </button>
              <button
                @click="editUser(user)"
                class="action-btn edit"
                title="Edit User"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button
                @click="toggleUserStatus(user)"
                class="action-btn"
                :class="user.is_active ? 'deactivate' : 'activate'"
                :title="user.is_active ? 'Deactivate' : 'Activate'"
              >
                <i :class="user.is_active ? 'fas fa-user-slash' : 'fas fa-user-check'"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination">
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { type APIError } from '@/services/api'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { OrganizationService } from '@/services/organizations'
import { AdminService } from '@/services/admin'

const route = useRoute()
const { handleApiError } = useErrorHandler()

const organizationId = route.params.id as string
const organization = ref<any>(null)
const users = ref<any[]>([])
const loading = ref(true)
const error = ref<any>(null)

// Filters
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 12

// Computed properties
const students = computed(() => users.value.filter(user => user.role === 'student'))
const teachers = computed(() => users.value.filter(user => user.role === 'teacher'))
const admins = computed(() => users.value.filter(user => user.role === 'admin'))

const filteredUsers = computed(() => {
  let filtered = users.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(user =>
      user.full_name?.toLowerCase().includes(query) ||
      user.first_name?.toLowerCase().includes(query) ||
      user.last_name?.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query)
    )
  }

  // Role filter
  if (roleFilter.value) {
    filtered = filtered.filter(user => user.role === roleFilter.value)
  }

  // Status filter
  if (statusFilter.value) {
    const isActive = statusFilter.value === 'active'
    filtered = filtered.filter(user => user.is_active === isActive)
  }

  return filtered
})

const totalPages = computed(() => Math.ceil(filteredUsers.value.length / itemsPerPage))

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredUsers.value.slice(start, end)
})

// Methods
const loadUsers = async () => {
  try {
    loading.value = true
    error.value = null

    // Load organization info
    organization.value = await OrganizationService.getOrganization(organizationId)

    // Load users for this organization
    users.value = await OrganizationService.getOrganizationUsers(organizationId)

  } catch (err) {
    error.value = err
    handleApiError(err as APIError, { context: { action: 'load_organization_users' } })
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const viewUserDetails = (user: any) => {
  // Navigate to user detail page or show modal
  console.log('View user details:', user)
}

const editUser = (user: any) => {
  // Navigate to user edit page or show modal
  console.log('Edit user:', user)
}

const toggleUserStatus = async (user: any) => {
  try {
    const newStatus = !user.is_active
    await AdminService.updateUser(user.id, {
      is_active: newStatus
    })
    
    user.is_active = newStatus
  } catch (err) {
    handleApiError(err as APIError, { context: { action: 'toggle_user_status' } })
  }
}

// Lifecycle
onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.organization-users-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.back-link {
  display: inline-flex;
  align-items: center;
  color: #6b7280;
  text-decoration: none;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.back-link:hover {
  color: #374151;
}

.header-content h1 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 2rem;
  font-weight: 600;
}

.header-description {
  margin: 0;
  color: #6b7280;
  font-size: 1rem;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.retry-btn {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  margin-top: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  margin-right: 1rem;
  font-size: 1.25rem;
  color: white;
}

.stat-icon.total {
  background: #3b82f6;
}

.stat-icon.students {
  background: #10b981;
}

.stat-icon.teachers {
  background: #f59e0b;
}

.stat-icon.admins {
  background: #8b5cf6;
}

.stat-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.stat-content p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.filters-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1rem;
}

.search-bar {
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.filter-controls {
  display: flex;
  gap: 0.75rem;
}

.filter-select {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
}

.users-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.list-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.list-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  color: #6b7280;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1rem;
  padding: 1.5rem;
}

.user-card {
  display: flex;
  align-items: center;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
}

.user-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-avatar {
  margin-right: 1rem;
}

.avatar-image {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.25rem;
}

.user-info {
  flex: 1;
}

.user-info h4 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
}

.user-email {
  margin: 0 0 0.5rem 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.user-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.role-badge,
.status-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
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
  background: #ede9fe;
  color: #6b21a8;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.user-details small {
  color: #9ca3af;
  font-size: 0.75rem;
}

.user-actions {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.action-btn.view:hover {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.edit:hover {
  background: #fef3c7;
  color: #92400e;
}

.action-btn.activate:hover {
  background: #d1fae5;
  color: #065f46;
}

.action-btn.deactivate:hover {
  background: #fee2e2;
  color: #991b1b;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: #2563eb;
}

.pagination-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.pagination-info {
  color: #6b7280;
  font-size: 0.875rem;
}
</style>