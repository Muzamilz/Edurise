<template>
  <div class="super-admin-dashboard">
    <div class="dashboard-header">
      <div class="super-admin-badge">⚡ SUPER ADMIN</div>
      <h1>Platform Control Center</h1>
      <p>Manage the entire Edurise platform and all organizations</p>
    </div>

    <div class="dashboard-content">
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
import { ref, onMounted } from 'vue'

// Mock data - replace with real data from API
const totalPlatformUsers = ref(5247)
const totalStudents = ref(4589)
const totalTeachers = ref(658)
const totalOrganizations = ref(156)
const activeOrganizations = ref(142)
const pendingTeachersCount = ref(23)
const totalCourses = ref(1847)
const publicCourses = ref(1203)
const privateCourses = ref(644)
const totalRevenue = ref(2847650)
const monthlyRevenue = ref(284920)
const totalEnrollments = ref(15847)
const enrollmentGrowth = ref(18)
const securityAlerts = ref(2)
const systemHealth = ref(98)
const systemStatus = ref('Excellent')

// Platform health metrics
const apiResponseTime = ref(85)
const apiRequestsPerMin = ref(2847)
const dbConnections = ref(245)
const maxDbConnections = ref(500)
const dbQueryTime = ref(12)
const usedStorage = ref(2.4)
const availableStorage = ref(7.6)
const storageStatus = ref('Healthy')
const cacheHitRate = ref(94)
const cdnBandwidth = ref(156)

// Mock organizations
const organizations = ref([
  {
    id: '1',
    name: 'Tech University',
    subdomain: 'techuni',
    logo: null,
    subscription_plan: 'enterprise',
    user_count: 1247,
    course_count: 89,
    revenue: 45680
  },
  {
    id: '2',
    name: 'Business Academy',
    subdomain: 'bizacademy',
    logo: null,
    subscription_plan: 'pro',
    user_count: 856,
    course_count: 67,
    revenue: 32450
  },
  {
    id: '3',
    name: 'Creative Institute',
    subdomain: 'creative',
    logo: null,
    subscription_plan: 'basic',
    user_count: 423,
    course_count: 34,
    revenue: 12890
  }
])

// Mock pending teachers
const pendingTeachers = ref([
  {
    id: '1',
    name: 'John Smith',
    email: 'john.smith@example.com',
    organization: 'Tech University',
    avatar: '/default-avatar.jpg',
    appliedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    experience: '5 years in web development',
    expertise: 'JavaScript, React, Node.js'
  },
  {
    id: '2',
    name: 'Sarah Johnson',
    email: 'sarah.j@example.com',
    organization: 'Business Academy',
    avatar: '/default-avatar.jpg',
    appliedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    experience: '8 years in UX/UI design',
    expertise: 'Design Systems, Figma, User Research'
  }
])

const formatPlan = (plan: string) => {
  return plan.charAt(0).toUpperCase() + plan.slice(1)
}

const formatDate = (date: Date) => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return 'today'
  if (days === 1) return 'yesterday'
  return `${days} days ago`
}

const approveTeacher = async (teacherId: string) => {
  console.log('Approving teacher:', teacherId)
  pendingTeachers.value = pendingTeachers.value.filter(t => t.id !== teacherId)
  pendingTeachersCount.value--
}

const rejectTeacher = async (teacherId: string) => {
  console.log('Rejecting teacher:', teacherId)
  pendingTeachers.value = pendingTeachers.value.filter(t => t.id !== teacherId)
  pendingTeachersCount.value--
}

const switchToOrg = async (orgId: string) => {
  console.log('Switching to organization:', orgId)
  // Implement organization switching logic
}

onMounted(() => {
  // Load super admin dashboard data
  // superAdminStore.fetchPlatformStats()
  // superAdminStore.fetchOrganizations()
  // superAdminStore.fetchGlobalTeacherApprovals()
  // superAdminStore.fetchPlatformHealth()
})
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