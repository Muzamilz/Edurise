<template>
  <div class="organization-detail-view">
    <div class="page-header">
      <div class="header-content">
        <router-link to="/super-admin/organizations" class="back-link">
          ← Back to Organizations
        </router-link>
        <h1>{{ organization?.name || 'Loading...' }}</h1>
        <div class="organization-status" :class="organization?.is_active ? 'active' : 'inactive'">
          {{ organization?.is_active ? 'Active' : 'Inactive' }}
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading organization details...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load organization</h3>
      <p>{{ error.message }}</p>
      <button @click="loadOrganization" class="retry-btn">Try Again</button>
    </div>

    <div v-else-if="organization" class="organization-content">
      <!-- Organization Info -->
      <div class="info-section">
        <h2>Organization Information</h2>
        <div class="info-grid">
          <div class="info-item">
            <label>Name</label>
            <span>{{ organization.name }}</span>
          </div>
          <div class="info-item">
            <label>Subdomain</label>
            <span>{{ organization.subdomain }}.edurise.com</span>
          </div>
          <div class="info-item">
            <label>Subscription Plan</label>
            <span class="plan-badge" :class="organization.subscription_plan">
              {{ formatPlan(organization.subscription_plan) }}
            </span>
          </div>
          <div class="info-item">
            <label>Created</label>
            <span>{{ formatDate(organization.created_at) }}</span>
          </div>
        </div>
      </div>

      <!-- Statistics -->
      <div class="stats-section">
        <h2>Statistics</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <h3>Total Users</h3>
              <p class="stat-number">{{ stats.total_users || 0 }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-content">
              <h3>Total Courses</h3>
              <p class="stat-number">{{ stats.total_courses || 0 }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🎓</div>
            <div class="stat-content">
              <h3>Total Enrollments</h3>
              <p class="stat-number">{{ stats.total_enrollments || 0 }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-content">
              <h3>Total Revenue</h3>
              <p class="stat-number">${{ stats.total_revenue || 0 }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions-section">
        <h2>Actions</h2>
        <div class="action-buttons">
          <button 
            @click="toggleOrganizationStatus" 
            :class="organization.is_active ? 'danger' : 'primary'"
            :disabled="actionLoading"
          >
            {{ organization.is_active ? 'Deactivate' : 'Activate' }} Organization
          </button>
          <button @click="viewUsers" class="secondary">
            View Users
          </button>
          <button @click="viewCourses" class="secondary">
            View Courses
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApiData } from '@/composables/useApiData'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { api } from '@/services/api'

const route = useRoute()
const router = useRouter()
const { handleApiError } = useErrorHandler()

const organizationId = route.params.id as string
const organization = ref(null)
const stats = ref({})
const loading = ref(true)
const error = ref(null)
const actionLoading = ref(false)

const loadOrganization = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await api.get(`/organizations/${organizationId}/`)
    organization.value = response.data.data
    
    // Load organization stats
    const statsResponse = await api.get(`/organizations/${organizationId}/stats/`)
    stats.value = statsResponse.data.data
    
  } catch (err) {
    error.value = err
    handleApiError(err, { context: { action: 'load_organization_detail' } })
  } finally {
    loading.value = false
  }
}

const toggleOrganizationStatus = async () => {
  try {
    actionLoading.value = true
    
    const newStatus = !organization.value.is_active
    await api.patch(`/organizations/${organizationId}/`, {
      is_active: newStatus
    })
    
    organization.value.is_active = newStatus
    
  } catch (err) {
    handleApiError(err, { context: { action: 'toggle_organization_status' } })
  } finally {
    actionLoading.value = false
  }
}

const viewUsers = () => {
  router.push(`/super-admin/organizations/${organizationId}/users`)
}

const viewCourses = () => {
  router.push(`/super-admin/organizations/${organizationId}/courses`)
}

const formatPlan = (plan: string) => {
  return plan.charAt(0).toUpperCase() + plan.slice(1)
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

onMounted(() => {
  loadOrganization()
})
</script>

<style scoped>
.organization-detail-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.back-link {
  color: #7c3aed;
  text-decoration: none;
  font-weight: 500;
}

.back-link:hover {
  color: #5b21b6;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  flex: 1;
}

.organization-status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
}

.organization-status.active {
  background: #dcfce7;
  color: #166534;
}

.organization-status.inactive {
  background: #fef2f2;
  color: #dc2626;
}

.info-section, .stats-section, .actions-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.1);
  border: 1px solid rgba(124, 58, 237, 0.1);
  margin-bottom: 2rem;
}

.info-section h2, .stats-section h2, .actions-section h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-item span {
  font-size: 1rem;
  color: #1f2937;
}

.plan-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  width: fit-content;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.05), rgba(124, 58, 237, 0.1));
  border-radius: 8px;
  border: 1px solid rgba(124, 58, 237, 0.1);
}

.stat-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.stat-content h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #7c3aed;
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-buttons button {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-buttons button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-buttons button.primary {
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  color: white;
}

.action-buttons button.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
}

.action-buttons button.secondary {
  background: linear-gradient(135deg, #f3e8ff, #e9d5ff);
  color: #5b21b6;
  border: 1px solid rgba(124, 58, 237, 0.3);
}

.action-buttons button.secondary:hover:not(:disabled) {
  background: linear-gradient(135deg, #e9d5ff, #ddd6fe);
  border-color: #7c3aed;
}

.action-buttons button.danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.action-buttons button.danger:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: white;
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

.error-icon {
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