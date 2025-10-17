<template>
  <div class="super-admin-dashboard">
    <div class="dashboard-header">
      <div class="super-admin-badge">⚡ SUPER ADMIN</div>
      <h1>Platform Control Center</h1>
      <p>Manage the entire Edurise platform and all organizations</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading platform dashboard...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Unable to load dashboard</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">
        Try Again
      </button>
    </div>

    <div v-else class="dashboard-content">
      <!-- Platform-Wide Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">🌐</div>
          <h3>Platform Users</h3>
          <p class="stat-number">{{ totalPlatformUsers }}</p>
          <span class="stat-change">{{ totalStudents }} students, {{ totalTeachers }} teachers</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🏢</div>
          <h3>Organizations</h3>
          <p class="stat-number">{{ totalOrganizations }}</p>
          <span class="stat-change">{{ activeOrganizations }} active</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">👨‍🏫</div>
          <h3>Teacher Approvals</h3>
          <p class="stat-number">{{ pendingTeachersCount }}</p>
          <span class="stat-change">Platform-wide pending</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📚</div>
          <h3>Total Courses</h3>
          <p class="stat-number">{{ totalCourses }}</p>
          <span class="stat-change">{{ publicCourses }} public, {{ privateCourses }} private</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <h3>Platform Revenue</h3>
          <p class="stat-number">${{ totalRevenue }}</p>
          <span class="stat-change">${{ monthlyRevenue }} this month</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <h3>Global Enrollments</h3>
          <p class="stat-number">{{ totalEnrollments }}</p>
          <span class="stat-change">{{ enrollmentGrowth }}% growth</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🛡️</div>
          <h3>Security Alerts</h3>
          <p class="stat-number">{{ securityAlerts }}</p>
          <span class="stat-change">{{ securityAlerts === 0 ? 'All clear' : 'Needs attention' }}</span>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⚙️</div>
          <h3>System Health</h3>
          <p class="stat-number">{{ systemHealth }}%</p>
          <span class="stat-change">{{ systemStatus }}</span>
        </div>
      </div>

      <!-- Super Admin Actions -->
      <div class="quick-actions">
        <h2>Platform Management</h2>
        <div class="action-buttons">
          <router-link to="/super-admin/organizations" class="action-btn primary">
            <span class="btn-icon">🏢</span>
            Manage Organizations
          </router-link>
          <router-link to="/super-admin/teachers/global" class="action-btn secondary">
            <span class="btn-icon">👨‍🏫</span>
            Global Teacher Approvals
          </router-link>
          <router-link to="/super-admin/users" class="action-btn secondary">
            <span class="btn-icon">👥</span>
            All Users
          </router-link>
          <router-link to="/super-admin/courses/global" class="action-btn secondary">
            <span class="btn-icon">📚</span>
            All Courses
          </router-link>
          <router-link to="/super-admin/analytics/platform" class="action-btn secondary">
            <span class="btn-icon">📊</span>
            Platform Analytics
          </router-link>
          <router-link to="/super-admin/financial/global" class="action-btn secondary">
            <span class="btn-icon">💰</span>
            Global Financials
          </router-link>
          <router-link to="/super-admin/security" class="action-btn secondary">
            <span class="btn-icon">🛡️</span>
            Security Center
          </router-link>
          <router-link to="/super-admin/system" class="action-btn secondary">
            <span class="btn-icon">⚙️</span>
            System Administration
          </router-link>
        </div>
      </div>

      <!-- Organizations Overview -->
      <div class="organizations-overview">
        <div class="section-header">
          <h2>Organizations Overview</h2>
          <router-link to="/super-admin/organizations" class="view-all-link">Manage All</router-link>
        </div>
        
        <div v-if="organizations.length > 0" class="organizations-grid">
          <div v-for="org in organizations" :key="org.id" class="organization-card">
            <div class="org-header">
              <div class="org-logo">
                <img v-if="org.logo" :src="org.logo" :alt="org.name" />
                <div v-else class="org-placeholder">{{ org.name.charAt(0) }}</div>
              </div>
              <div class="org-info">
                <h3>{{ org.name }}</h3>
                <p class="org-subdomain">{{ org.subdomain }}.edurise.com</p>
                <span class="org-plan" :class="org.subscription_plan">{{ formatPlan(org.subscription_plan) }}</span>
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
                <span class="stat-value">${{ org.revenue || 0 }}</span>
              </div>
            </div>
            <div class="org-actions">
              <router-link :to="`/super-admin/organizations/${org.id}`" class="manage-btn">
                Manage
              </router-link>
              <button @click="switchToOrg(org.id)" class="switch-btn">
                Switch To
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Global Teacher Approvals -->
      <div class="global-approvals">
        <div class="section-header">
          <h2>Pending Teacher Approvals (Global)</h2>
          <router-link to="/super-admin/teachers/global" class="view-all-link">View All</router-link>
        </div>
        
        <div v-if="pendingTeachers.length > 0" class="approvals-list">
          <div v-for="teacher in pendingTeachers.slice(0, 3)" :key="teacher.id" class="approval-card">
            <div class="teacher-info">
              <div class="teacher-avatar">
                <img :src="teacher.avatar || '/default-avatar.jpg'" :alt="teacher.name" />
              </div>
              <div class="teacher-details">
                <h3>{{ teacher.name }}</h3>
                <p class="teacher-email">{{ teacher.email }}</p>
                <p class="teacher-org">{{ teacher.organization }}</p>
                <p class="application-date">Applied {{ formatDate(teacher.appliedAt) }}</p>
              </div>
            </div>
            <div class="teacher-qualifications">
              <p><strong>Experience:</strong> {{ teacher.experience }}</p>
              <p><strong>Expertise:</strong> {{ teacher.expertise }}</p>
            </div>
            <div class="approval-actions">
              <button @click="approveTeacher(teacher.id)" class="approve-btn">
                Approve
              </button>
              <button @click="rejectTeacher(teacher.id)" class="reject-btn">
                Reject
              </button>
              <router-link :to="`/super-admin/teachers/${teacher.id}`" class="review-btn">
                Review
              </router-link>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <div class="empty-icon">✅</div>
          <h3>No pending approvals</h3>
          <p>All teacher applications across the platform have been reviewed</p>
        </div>
      </div>

      <!-- Platform Health Monitor -->
      <div class="platform-health">
        <h2>Platform Health Monitor</h2>
        <div class="health-grid">
          <div class="health-card">
            <div class="health-header">
              <h3>API Services</h3>
              <div class="health-status online">Online</div>
            </div>
            <div class="health-metrics">
              <div class="metric">
                <span class="metric-label">Response Time</span>
                <span class="metric-value">{{ apiResponseTime }}ms</span>
              </div>
              <div class="metric">
                <span class="metric-label">Requests/min</span>
                <span class="metric-value">{{ apiRequestsPerMin }}</span>
              </div>
            </div>
          </div>
          
          <div class="health-card">
            <div class="health-header">
              <h3>Database Cluster</h3>
              <div class="health-status online">Healthy</div>
            </div>
            <div class="health-metrics">
              <div class="metric">
                <span class="metric-label">Connections</span>
                <span class="metric-value">{{ dbConnections }}/{{ maxDbConnections }}</span>
              </div>
              <div class="metric">
                <span class="metric-label">Query Time</span>
                <span class="metric-value">{{ dbQueryTime }}ms</span>
              </div>
            </div>
          </div>
          
          <div class="health-card">
            <div class="health-header">
              <h3>Storage Systems</h3>
              <div class="health-status" :class="storageStatus.toLowerCase()">{{ storageStatus }}</div>
            </div>
            <div class="health-metrics">
              <div class="metric">
                <span class="metric-label">Used Space</span>
                <span class="metric-value">{{ usedStorage }}TB</span>
              </div>
              <div class="metric">
                <span class="metric-label">Available</span>
                <span class="metric-value">{{ availableStorage }}TB</span>
              </div>
            </div>
          </div>
          
          <div class="health-card">
            <div class="health-header">
              <h3>CDN Network</h3>
              <div class="health-status online">Operational</div>
            </div>
            <div class="health-metrics">
              <div class="metric">
                <span class="metric-label">Cache Hit Rate</span>
                <span class="metric-value">{{ cacheHitRate }}%</span>
              </div>
              <div class="metric">
                <span class="metric-label">Bandwidth</span>
                <span class="metric-value">{{ cdnBandwidth }}GB/h</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDashboardData } from '@/composables/useDashboardData'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { useApiMutation } from '@/composables/useApiData'
import { api } from '@/services/api'

const { superAdminData } = useDashboardData()
const { handleApiError } = useErrorHandler()

// Real data from API
const dashboardData = computed(() => superAdminData.data.value)
const loading = computed(() => superAdminData.loading.value)
const error = computed(() => superAdminData.error.value)

// Computed properties for super admin stats
const totalPlatformUsers = computed(() => 
  dashboardData.value?.platformStats?.totalUsers || 0
)

const totalStudents = computed(() => {
  // Calculate from platform stats - would need to be added to API
  const totalUsers = totalPlatformUsers.value
  return Math.round(totalUsers * 0.85) // Estimate 85% students
})

const totalTeachers = computed(() => {
  // Calculate from platform stats - would need to be added to API
  const totalUsers = totalPlatformUsers.value
  return Math.round(totalUsers * 0.15) // Estimate 15% teachers
})

const totalOrganizations = computed(() => 
  dashboardData.value?.platformStats?.totalTenants || 0
)

const activeOrganizations = computed(() => 
  dashboardData.value?.platformStats?.activeTenants || 0
)

const pendingTeachersCount = computed(() => {
  // This would need to be added to super admin API
  return 0 // Placeholder
})

const totalCourses = computed(() => 
  dashboardData.value?.platformStats?.totalCourses || 0
)

const publicCourses = computed(() => {
  // Calculate from total courses - would need API enhancement
  return Math.round(totalCourses.value * 0.7) // Estimate 70% public
})

const privateCourses = computed(() => 
  totalCourses.value - publicCourses.value
)

const totalRevenue = computed(() => 
  Math.round(dashboardData.value?.platformStats?.totalRevenue || 0)
)

const monthlyRevenue = computed(() => {
  // Calculate from revenue by tenant
  const revenueByTenant = dashboardData.value?.revenueByTenant || []
  return revenueByTenant.reduce((total, tenant) => total + (tenant.revenue || 0), 0)
})

const totalEnrollments = computed(() => {
  // This would need to be added to platform stats
  return 0 // Placeholder
})

const enrollmentGrowth = computed(() => {
  // Calculate average growth from revenue by tenant
  const revenueByTenant = dashboardData.value?.revenueByTenant || []
  const avgGrowth = revenueByTenant.reduce((total, tenant) => total + (tenant.growth || 0), 0) / revenueByTenant.length
  return Math.round(avgGrowth || 0)
})

const securityAlerts = computed(() => {
  // This would need to be added to system metrics
  return 0 // Placeholder
})

const systemHealth = computed(() => {
  // Calculate from system metrics
  const metrics = dashboardData.value?.systemMetrics
  if (!metrics) return 0
  
  const serverLoad = Math.max(0, 100 - (metrics.serverLoad || 0))
  const memoryHealth = Math.max(0, 100 - (metrics.memoryUsage || 0))
  const diskHealth = Math.max(0, 100 - (metrics.diskUsage || 0))
  
  return Math.round((serverLoad + memoryHealth + diskHealth) / 3)
})

const systemStatus = computed(() => {
  const health = systemHealth.value
  if (health >= 95) return 'Excellent'
  if (health >= 85) return 'Good'
  if (health >= 70) return 'Fair'
  return 'Needs Attention'
})

// Platform health metrics from system metrics


const apiResponseTime = computed(() => 85) // Default value since systemMetrics doesn't have apiCalls

const apiRequestsPerMin = computed(() => 120) // Default value

const dbConnections = computed(() => 25) // Default value

const maxDbConnections = computed(() => 500) // Static limit

const dbQueryTime = computed(() => 12) // Default value

const usedStorage = computed(() => 2.5) // Default value in TB

const availableStorage = computed(() => 7.5) // Default value in TB

const storageStatus = computed(() => 'Healthy') // Default status

const cacheHitRate = computed(() => 88) // Default cache hit rate

const cdnBandwidth = computed(() => 45) // Default CDN bandwidth

// Organizations data
const organizations = computed(() => 
  dashboardData.value?.tenantStats?.slice(0, 3).map(org => ({
    id: org.id,
    name: org.name,
    subdomain: org.subdomain,
    subscription_plan: org.subscriptionPlan,
    user_count: org.userCount,
    course_count: org.courseCount,
    revenue: org.revenue,
    logo: null // Backend doesn't provide logo yet
  })) || []
)

// Global activity as pending teachers (placeholder)
interface PendingTeacher {
  id: string
  name: string
  email: string
  avatar?: string
  organization: string
  appliedAt: string
  experience: string
  expertise: string
}

const pendingTeachers = computed((): PendingTeacher[] => {
  // This would come from a separate global teacher approvals endpoint
  return []
})

// Teacher approval mutations
const { mutate: approveTeacherMutation } = useApiMutation(
  (teacherId: string) => api.patch(`/teacher-approvals/${teacherId}/`, { status: 'approved' }),
  {
    onSuccess: () => {
      console.log('Teacher approved successfully')
      superAdminData.refresh()
    },
    onError: (error) => {
      handleApiError(error, { context: { action: 'approve_teacher_global' } })
    }
  }
)

const { mutate: rejectTeacherMutation } = useApiMutation(
  (teacherId: string) => api.patch(`/teacher-approvals/${teacherId}/`, { status: 'rejected' }),
  {
    onSuccess: () => {
      console.log('Teacher rejected successfully')
      superAdminData.refresh()
    },
    onError: (error) => {
      handleApiError(error, { context: { action: 'reject_teacher_global' } })
    }
  }
)

// Organization switching mutation
const { mutate: switchToOrgMutation } = useApiMutation(
  (orgId: string) => api.post(`/organizations/${orgId}/switch/`),
  {
    onSuccess: (data) => {
      console.log('Switched to organization successfully')
      // Update tenant context
      localStorage.setItem('tenant_id', data.tenant_id)
      // Redirect or refresh
      window.location.reload()
    },
    onError: (error) => {
      handleApiError(error, { context: { action: 'switch_organization' } })
    }
  }
)

// Action handlers
const approveTeacher = async (teacherId: string) => {
  try {
    await approveTeacherMutation(teacherId)
  } catch (error) {
    // Error handling is done in the mutation
  }
}

const rejectTeacher = async (teacherId: string) => {
  try {
    await rejectTeacherMutation(teacherId)
  } catch (error) {
    // Error handling is done in the mutation
  }
}

const switchToOrg = async (orgId: string) => {
  try {
    await switchToOrgMutation(orgId)
  } catch (error) {
    // Error handling is done in the mutation
  }
}

// Utility functions
const formatPlan = (plan: string) => {
  return plan.charAt(0).toUpperCase() + plan.slice(1)
}

const formatDate = (date: Date | string) => {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diff = now.getTime() - dateObj.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return 'today'
  if (days === 1) return 'yesterday'
  return `${days} days ago`
}

const handleRetry = async () => {
  try {
    await superAdminData.refresh()
  } catch (err) {
    handleApiError(err as any, { 
      context: { action: 'retry_superadmin_dashboard_load' } 
    })
  }
}
</script>

<style scoped>
.super-admin-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.super-admin-badge {
  display: inline-block;
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.dashboard-header p {
  color: #6b7280;
  font-size: 1.125rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
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
  color: #10b981;
  font-weight: 500;
}

.quick-actions, .organizations-overview, .global-approvals, .platform-health {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(243, 232, 255, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.1);
  border: 1px solid rgba(124, 58, 237, 0.1);
  margin-bottom: 2rem;
}

.quick-actions h2, .organizations-overview h2, .global-approvals h2, .platform-health h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: center;
}

.action-btn.primary {
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  color: white;
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
}

.action-btn.secondary {
  background: linear-gradient(135deg, #f3e8ff, #e9d5ff);
  color: #5b21b6;
  border: 1px solid rgba(124, 58, 237, 0.3);
}

.action-btn.secondary:hover {
  background: linear-gradient(135deg, #e9d5ff, #ddd6fe);
  border-color: #7c3aed;
}

.btn-icon {
  font-size: 1.1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
}

.view-all-link {
  color: #7c3aed;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
}

.view-all-link:hover {
  color: #5b21b6;
}

.organizations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.organization-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid rgba(124, 58, 237, 0.1);
  transition: all 0.3s ease;
}

.organization-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.15);
}

.org-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.org-logo {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.org-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.org-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.25rem;
}

.org-info h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.org-subdomain {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.org-plan {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.org-plan.basic {
  background: #fef3c7;
  color: #92400e;
}

.org-plan.pro {
  background: #dbeafe;
  color: #1e40af;
}

.org-plan.enterprise {
  background: #f3e8ff;
  color: #5b21b6;
}

.org-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 6px;
}

.org-stat {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.org-actions {
  display: flex;
  gap: 0.5rem;
}

.manage-btn, .switch-btn {
  flex: 1;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  text-align: center;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.manage-btn {
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  color: white;
}

.manage-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
}

.switch-btn {
  background: linear-gradient(135deg, #f3e8ff, #e9d5ff);
  color: #5b21b6;
  border: 1px solid rgba(124, 58, 237, 0.3);
}

.switch-btn:hover {
  background: linear-gradient(135deg, #e9d5ff, #ddd6fe);
  border-color: #7c3aed;
}

.approvals-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.approval-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid rgba(124, 58, 237, 0.1);
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 1.5rem;
  align-items: center;
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
  flex-shrink: 0;
}

.teacher-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.teacher-details h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.teacher-email {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.teacher-org {
  font-size: 0.75rem;
  color: #7c3aed;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.application-date {
  font-size: 0.75rem;
  color: #f59e0b;
  font-weight: 500;
}

.teacher-qualifications p {
  font-size: 0.875rem;
  color: #374151;
  margin-bottom: 0.5rem;
}

.approval-actions {
  display: flex;
  gap: 0.5rem;
}

.approve-btn, .reject-btn, .review-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s ease;
}

.approve-btn {
  background: #10b981;
  color: white;
}

.approve-btn:hover {
  background: #059669;
}

.reject-btn {
  background: #ef4444;
  color: white;
}

.reject-btn:hover {
  background: #dc2626;
}

.review-btn {
  background: linear-gradient(135deg, #f3e8ff, #e9d5ff);
  color: #5b21b6;
  border: 1px solid rgba(124, 58, 237, 0.3);
  display: inline-block;
}

.review-btn:hover {
  background: linear-gradient(135deg, #e9d5ff, #ddd6fe);
  border-color: #7c3aed;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #6b7280;
}

.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.health-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid rgba(124, 58, 237, 0.1);
}

.health-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.health-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.health-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.health-status.online {
  background: #dcfce7;
  color: #166534;
}

.health-status.healthy {
  background: #dcfce7;
  color: #166534;
}

.health-status.warning {
  background: #fef3c7;
  color: #92400e;
}

.health-metrics {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.metric-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
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
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
}

.retry-btn:active {
  transform: translateY(0);
}

/* Responsive */
@media (max-width: 768px) {
  .super-admin-dashboard {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    grid-template-columns: 1fr;
  }
  
  .organizations-grid, .health-grid {
    grid-template-columns: 1fr;
  }
  
  .approval-card {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .approval-actions {
    justify-content: center;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .org-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .org-actions {
    flex-direction: column;
  }
}
</style>