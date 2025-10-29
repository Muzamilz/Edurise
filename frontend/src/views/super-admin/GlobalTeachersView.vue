<template>
  <div class="global-teachers-view">
    <div class="page-header">
      <h1>Global Teacher Management</h1>
      <p>Manage teacher approvals across all organizations</p>
    </div>

    <!-- Global Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">👨‍🏫</div>
        <h3>Total Teachers</h3>
        <p class="stat-number">{{ totalTeachers }}</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⏳</div>
        <h3>Pending Approvals</h3>
        <p class="stat-number">{{ pendingApprovals }}</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <h3>Approved This Month</h3>
        <p class="stat-number">{{ approvedThisMonth }}</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏢</div>
        <h3>Organizations</h3>
        <p class="stat-number">{{ organizationsCount }}</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading teacher applications...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load teacher applications</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Teacher Applications -->
    <div v-else class="applications-container">
      <div class="applications-header">
        <h2>Global Teacher Applications</h2>
        <div class="filter-controls">
          <select v-model="statusFilter" class="filter-select">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      <div class="applications-list">
        <div v-for="application in filteredApplications" :key="application.id" class="application-card">
          <div class="application-header">
            <div class="teacher-info">
              <div class="teacher-avatar">
                <img :src="application.user.avatar || '/default-avatar.jpg'" :alt="application.user.name" />
              </div>
              <div class="teacher-details">
                <h3>{{ application.user.first_name }} {{ application.user.last_name }}</h3>
                <p>{{ application.user.email }}</p>
                <span class="organization">{{ application.organization.name }}</span>
              </div>
            </div>
            <div class="status-badge" :class="application.status">
              {{ formatStatus(application.status) }}
            </div>
          </div>

          <div class="application-content">
            <div class="qualification-summary">
              <p><strong>Experience:</strong> {{ application.experience || 'Not provided' }}</p>
              <p><strong>Expertise:</strong> {{ application.expertise_areas || 'Not provided' }}</p>
            </div>
          </div>

          <div v-if="application.status === 'pending'" class="application-actions">
            <button @click="approveApplication(application)" class="action-btn approve">
              Approve
            </button>
            <button @click="rejectApplication(application)" class="action-btn reject">
              Reject
            </button>
            <button @click="viewDetails(application)" class="action-btn view">
              View Details
            </button>
          </div>
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

// Reactive state
const statusFilter = ref('')

// API data
const { data: teacherApplicationsData, loading, error, refresh } = useApiData('/teacher-approvals/', {
  immediate: true,
  transform: (data) => {
    console.log('🔍 Raw teacher approvals data:', data)
    
    // Handle both paginated and direct array responses
    const results = data.results || data.data || data || []
    
    return results.map((app: any) => {
      return {
        id: app.id,
        user: {
          first_name: app.user_first_name || 'Unknown',
          last_name: app.user_last_name || 'User',
          email: app.user_email || 'No email',
          avatar: app.avatar || null
        },
        organization: {
          name: app.organization_name || 'No Organization'
        },
        status: app.status || 'pending',
        experience: app.teaching_experience || 'Not provided',
        expertise_areas: app.subject_expertise || 'Not provided',
        submitted_at: app.applied_at || app.created_at
      }
    })
  },
  retryAttempts: 3,
  onError: (error) => {
    console.error('Failed to load teacher applications:', error)
  }
})

// Computed properties
const applications = computed(() => {
  const apps = teacherApplicationsData.value || []
  console.log('📋 Processed teacher applications:', apps)
  return apps
})
const totalTeachers = computed(() => applications.value.filter(app => app.status === 'approved').length)
const pendingApprovals = computed(() => applications.value.filter(app => app.status === 'pending').length)
const approvedThisMonth = computed(() => {
  const thisMonth = new Date()
  thisMonth.setDate(1)
  return applications.value.filter(app => 
    app.status === 'approved' && 
    new Date(app.submitted_at) >= thisMonth
  ).length
})
const organizationsCount = computed(() => {
  const orgs = new Set(applications.value.map(app => app.organization?.name))
  return orgs.size
})

// Mutations
const { mutate: approveApplicationMutation } = useApiMutation(
  (id: string) => api.post(`/teacher-approvals/${id}/approve/`),
  {
    onSuccess: () => {
      console.log('✅ Teacher application approved successfully')
      refresh()
    },
    onError: (error) => handleApiError(error as APIError, { context: { action: 'approve_teacher_application' } })
  }
)

const { mutate: rejectApplicationMutation } = useApiMutation(
  ({ id, notes }: { id: string; notes: string }) => api.post(`/teacher-approvals/${id}/reject/`, { notes }),
  {
    onSuccess: () => {
      console.log('❌ Teacher application rejected successfully')
      refresh()
    },
    onError: (error) => handleApiError(error as APIError, { context: { action: 'reject_teacher_application' } })
  }
)

const filteredApplications = computed(() => {
  if (!statusFilter.value) return applications.value
  return applications.value.filter(app => app.status === statusFilter.value)
})

const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const approveApplication = async (application) => {
  if (confirm(`Approve ${application.user.first_name} ${application.user.last_name}'s application?`)) {
    try {
      await approveApplicationMutation(application.id)
    } catch (error) {
      console.error('Failed to approve application:', error)
    }
  }
}

const rejectApplication = async (application) => {
  const reason = prompt(`Reject ${application.user.first_name} ${application.user.last_name}'s application? Please provide a reason:`)
  if (reason) {
    try {
      await rejectApplicationMutation({ id: application.id, notes: reason })
    } catch (error) {
      console.error('Failed to reject application:', error)
    }
  }
}

const viewDetails = (application) => {
  router.push(`/super-admin/teachers/${application.id}`)
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as any, { context: { action: 'retry_teacher_applications_load' } })
  }
}

onMounted(() => {
  // Data is loaded automatically via useApiData
})
</script>

<style scoped>
.global-teachers-view {
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
  margin: 0;
}

.applications-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.applications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.applications-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.applications-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.application-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
}

.application-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.teacher-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.teacher-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
}

.teacher-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.teacher-details h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.teacher-details p {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0 0 0.25rem 0;
}

.organization {
  color: #7c3aed;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.approved {
  background: #dcfce7;
  color: #166534;
}

.status-badge.rejected {
  background: #fee2e2;
  color: #dc2626;
}

.qualification-summary p {
  color: #374151;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.application-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
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

.action-btn.approve {
  background: #dcfce7;
  color: #166534;
}

.action-btn.approve:hover {
  background: #bbf7d0;
}

.action-btn.reject {
  background: #fee2e2;
  color: #dc2626;
}

.action-btn.reject:hover {
  background: #fecaca;
}

.action-btn.view {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.view:hover {
  background: #bfdbfe;
}
</style>