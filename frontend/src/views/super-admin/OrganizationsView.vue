<template>
  <div class="super-admin-organizations-view">
    <div class="page-header">
      <h1>Manage Organizations</h1>
      <p>Oversee all organizations on the platform</p>
    </div>

    <!-- Organizations Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">🏢</div>
        <h3>Total Organizations</h3>
        <p class="stat-number">{{ totalOrganizations }}</p>
        <span class="stat-change positive">+5 this month</span>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <h3>Active Organizations</h3>
        <p class="stat-number">{{ activeOrganizations }}</p>
        <span class="stat-change positive">98% active</span>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <h3>Total Users</h3>
        <p class="stat-number">{{ totalUsers }}</p>
        <span class="stat-change positive">+12% growth</span>
      </div>
      <div class="stat-card">
        <div class="stat-icon">💰</div>
        <h3>Platform Revenue</h3>
        <p class="stat-number">${{ formatNumber(totalRevenue) }}</p>
        <span class="stat-change positive">+8.5% this month</span>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="filters-section">
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search organizations..."
          class="search-input"
        />
      </div>
      <div class="filter-controls">
        <select v-model="statusFilter" class="filter-select">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="suspended">Suspended</option>
        </select>
        <select v-model="planFilter" class="filter-select">
          <option value="">All Plans</option>
          <option value="basic">Basic</option>
          <option value="pro">Professional</option>
          <option value="enterprise">Enterprise</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading organizations...</p>
    </div>

    <!-- Organizations Grid -->
    <div v-else class="organizations-container">
      <div class="organizations-header">
        <h2>Organizations ({{ filteredOrganizations.length }})</h2>
        <button @click="showCreateModal = true" class="create-btn">
          <span class="btn-icon">➕</span>
          Add Organization
        </button>
      </div>

      <div class="organizations-grid">
        <div v-for="org in paginatedOrganizations" :key="org.id" class="organization-card">
          <div class="org-header">
            <div class="org-logo">
              <img :src="org.logo || '/default-org-logo.png'" :alt="org.name" />
            </div>
            <div class="org-info">
              <h3>{{ org.name }}</h3>
              <p class="org-subdomain">{{ org.subdomain }}.edurise.com</p>
              <span class="plan-badge" :class="org.subscription_plan">
                {{ formatPlan(org.subscription_plan) }}
              </span>
            </div>
            <div class="org-status" :class="org.is_active ? 'active' : 'inactive'">
              {{ org.is_active ? 'Active' : 'Inactive' }}
            </div>
          </div>

          <div class="org-stats">
            <div class="org-stat">
              <span class="stat-label">Users</span>
              <span class="stat-value">{{ org.user_count || 0 }}</span>
            </div>
            <div class="org-stat">
              <span class="stat-label">Courses</span>
              <span class="stat-value">{{ org.course_count || 0 }}</span>
            </div>
            <div class="org-stat">
              <span class="stat-label">Revenue</span>
              <span class="stat-value">${{ formatNumber(org.revenue || 0) }}</span>
            </div>
            <div class="org-stat">
              <span class="stat-label">Created</span>
              <span class="stat-value">{{ formatDate(org.created_at) }}</span>
            </div>
          </div>

          <div class="org-actions">
            <button @click="viewOrganization(org)" class="action-btn view">
              View Details
            </button>
            <button @click="switchToOrg(org)" class="action-btn switch">
              Switch To
            </button>
            <button 
              @click="toggleOrgStatus(org)" 
              :class="['action-btn', org.is_active ? 'suspend' : 'activate']"
            >
              {{ org.is_active ? 'Suspend' : 'Activate' }}
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

    <!-- Create Organization Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Create New Organization</h3>
          <button @click="closeCreateModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createOrganization">
            <div class="form-group">
              <label>Organization Name</label>
              <input v-model="orgForm.name" type="text" required />
            </div>
            <div class="form-group">
              <label>Subdomain</label>
              <input v-model="orgForm.subdomain" type="text" required />
            </div>
            <div class="form-group">
              <label>Subscription Plan</label>
              <select v-model="orgForm.subscription_plan" required>
                <option value="basic">Basic</option>
                <option value="pro">Professional</option>
                <option value="enterprise">Enterprise</option>
              </select>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeCreateModal" class="cancel-btn">Cancel</button>
              <button type="submit" class="create-btn">Create Organization</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApiData, useApiMutation } from '@/composables/useApiData'
import type { APIError } from '@/services/api'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { api } from '@/services/api'

const router = useRouter()
const { handleApiError } = useErrorHandler()

// Data fetching
const { data: organizationsData, loading, refresh } = useApiData('/organizations/', {
  immediate: true,
  transform: (data) => {
    // Transform the response to ensure consistent data structure
    if (data.results) {
      return data.results.map((org: any) => ({
        id: org.id,
        name: org.name,
        subdomain: org.subdomain,
        logo: org.logo,
        subscription_plan: org.subscription_plan || 'basic',
        is_active: org.is_active !== false,
        user_count: org.user_count || 0,
        course_count: org.course_count || 0,
        revenue: org.revenue || 0,
        created_at: org.created_at
      }))
    }
    return []
  },
  retryAttempts: 3,
  onError: (error) => {
    console.error('Failed to load organizations:', error)
  }
})

// Computed property for organizations
const organizations = computed(() => organizationsData.value || [])

// Filters and search
const searchQuery = ref('')
const statusFilter = ref('')
const planFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 12

// Modal state
const showCreateModal = ref(false)
const orgForm = ref({
  name: '',
  subdomain: '',
  subscription_plan: 'basic'
})

// Mock stats (would come from API)
const totalOrganizations = ref(156)
const activeOrganizations = ref(152)
const totalUsers = ref(12450)
const totalRevenue = ref(245000)

// Mutations
const { mutate: createOrg } = useApiMutation(
  (orgData: any) => api.post('/organizations/', orgData),
  {
    onSuccess: () => {
      closeCreateModal()
      refresh()
    },
    onError: (error) => handleApiError(error as APIError, { context: { action: 'create_organization' } })
  }
)

const { mutate: updateOrg } = useApiMutation(
  ({ id, ...data }: any) => api.patch(`/organizations/${id}/`, data),
  {
    onSuccess: () => refresh(),
    onError: (error) => handleApiError(error as APIError, { context: { action: 'update_organization' } })
  }
)

// Computed properties
const filteredOrganizations = computed(() => {
  if (!organizations.value) return []
  
  return organizations.value.filter(org => {
    const matchesSearch = !searchQuery.value || 
      org.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      org.subdomain.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesStatus = !statusFilter.value || 
      (statusFilter.value === 'active' && org.is_active) ||
      (statusFilter.value === 'inactive' && !org.is_active)
    
    const matchesPlan = !planFilter.value || org.subscription_plan === planFilter.value
    
    return matchesSearch && matchesStatus && matchesPlan
  })
})

const totalPages = computed(() => Math.ceil(filteredOrganizations.value.length / itemsPerPage))

const paginatedOrganizations = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredOrganizations.value.slice(start, end)
})

// Methods
const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num)
}

const formatPlan = (plan) => {
  return plan.charAt(0).toUpperCase() + plan.slice(1)
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

const viewOrganization = (org) => {
  router.push(`/super-admin/organizations/${org.id}`)
}

const switchToOrg = async (org) => {
  try {
    const response = await api.post('/users/switch_tenant/', { tenant_id: org.id })
    
    if (response.data) {
      // Update tokens and redirect
      localStorage.setItem('access_token', response.data.tokens.access)
      localStorage.setItem('refresh_token', response.data.tokens.refresh)
      window.location.href = '/dashboard'
    }
  } catch (error) {
    handleApiError(error as APIError, { context: { action: 'switch_organization' } })
  }
}

const toggleOrgStatus = async (org) => {
  const action = org.is_active ? 'suspend' : 'activate'
  if (confirm(`Are you sure you want to ${action} ${org.name}?`)) {
    await updateOrg({ id: org.id, is_active: !org.is_active })
  }
}

const createOrganization = async () => {
  await createOrg(orgForm.value)
}

const closeCreateModal = () => {
  showCreateModal.value = false
  orgForm.value = {
    name: '',
    subdomain: '',
    subscription_plan: 'basic'
  }
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.super-admin-organizations-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
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
  border: 1px solid rgba(124, 58, 237, 0.1);
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(124, 58, 237, 0.15);
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
  letter-spacing: 0.05em;
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

.filters-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-bar {
  flex: 1;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
}

.filter-controls {
  display: flex;
  gap: 1rem;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  min-width: 150px;
}

.organizations-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.organizations-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.organizations-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.create-btn {
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
}

.organizations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.organization-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.organization-card:hover {
  border-color: #7c3aed;
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.1);
}

.org-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.org-logo {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.org-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.org-info {
  flex: 1;
}

.org-info h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.org-subdomain {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0 0 0.5rem 0;
}

.plan-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.plan-badge.basic {
  background: #fef3c7;
  color: #92400e;
}

.plan-badge.pro {
  background: #dbeafe;
  color: #1e40af;
}

.plan-badge.enterprise {
  background: #f3e8ff;
  color: #5b21b6;
}

.org-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.org-status.active {
  background: #dcfce7;
  color: #166534;
}

.org-status.inactive {
  background: #fee2e2;
  color: #dc2626;
}

.org-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.org-stat {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.org-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
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

.action-btn.switch {
  background: #f3e8ff;
  color: #5b21b6;
}

.action-btn.switch:hover {
  background: #e9d5ff;
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  font-weight: 500;
}

.cancel-btn:hover {
  background: #f9fafb;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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
</style>