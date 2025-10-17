<template>
  <div class="application-status-view">
    <div class="page-header">
      <h1>Teacher Application Status</h1>
      <p>Track the status of your teacher application</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading application status...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load application status</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Application Status Card -->
    <div v-else class="status-container">
      <div class="status-card">
        <div class="status-header">
          <div class="status-icon" :class="application.status">
            {{ getStatusIcon(application.status) }}
          </div>
          <div class="status-info">
            <h2>Application {{ formatStatus(application.status) }}</h2>
            <p class="status-description">{{ getStatusDescription(application.status) }}</p>
          </div>
        </div>

        <div class="status-timeline">
          <div class="timeline-item" :class="{ completed: true }">
            <div class="timeline-dot completed"></div>
            <div class="timeline-content">
              <h4>Application Submitted</h4>
              <p>{{ formatDate(application.submitted_at) }}</p>
            </div>
          </div>

          <div class="timeline-item" :class="{ completed: application.status !== 'pending' }">
            <div class="timeline-dot" :class="{ completed: application.status !== 'pending' }"></div>
            <div class="timeline-content">
              <h4>Under Review</h4>
              <p v-if="application.status === 'pending'">Your application is being reviewed by our team</p>
              <p v-else>{{ formatDate(application.reviewed_at) }}</p>
            </div>
          </div>

          <div class="timeline-item" :class="{ completed: application.status === 'approved' }">
            <div class="timeline-dot" :class="{ completed: application.status === 'approved' }"></div>
            <div class="timeline-content">
              <h4>Decision</h4>
              <p v-if="application.status === 'approved'">Congratulations! You've been approved as a teacher</p>
              <p v-else-if="application.status === 'rejected'">Application was not approved</p>
              <p v-else>Pending review completion</p>
            </div>
          </div>
        </div>

        <div v-if="application.status === 'rejected' && application.rejection_reason" class="rejection-feedback">
          <h4>Feedback</h4>
          <p>{{ application.rejection_reason }}</p>
          <div class="reapply-section">
            <p>You can improve your application and reapply after addressing the feedback above.</p>
            <button @click="reapply" class="reapply-btn">Reapply</button>
          </div>
        </div>

        <div v-if="application.status === 'approved'" class="approval-actions">
          <h4>Next Steps</h4>
          <p>You can now start creating courses and teaching on our platform!</p>
          <div class="action-buttons">
            <router-link to="/teacher/courses/create" class="action-btn primary">
              Create Your First Course
            </router-link>
            <router-link to="/teacher/profile" class="action-btn secondary">
              Complete Your Profile
            </router-link>
          </div>
        </div>
      </div>

      <!-- Application Details -->
      <div class="details-card">
        <h3>Application Details</h3>
        <div class="details-grid">
          <div class="detail-item">
            <strong>Application ID:</strong>
            <span>{{ application.id }}</span>
          </div>
          <div class="detail-item">
            <strong>Submitted:</strong>
            <span>{{ formatDate(application.submitted_at) }}</span>
          </div>
          <div class="detail-item">
            <strong>Status:</strong>
            <span class="status-badge" :class="application.status">
              {{ formatStatus(application.status) }}
            </span>
          </div>
          <div v-if="application.reviewed_at" class="detail-item">
            <strong>Reviewed:</strong>
            <span>{{ formatDate(application.reviewed_at) }}</span>
          </div>
        </div>

        <div class="submitted-info">
          <h4>Submitted Information</h4>
          <div class="info-section">
            <div class="info-item">
              <strong>Education:</strong>
              <p>{{ application.education || 'Not provided' }}</p>
            </div>
            <div class="info-item">
              <strong>Experience:</strong>
              <p>{{ application.experience || 'Not provided' }}</p>
            </div>
            <div class="info-item">
              <strong>Expertise Areas:</strong>
              <p>{{ application.expertise_areas || 'Not provided' }}</p>
            </div>
            <div class="info-item">
              <strong>Teaching Philosophy:</strong>
              <p>{{ application.teaching_philosophy || 'Not provided' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApiData } from '@/composables/useApiData'
import { useErrorHandler } from '@/composables/useErrorHandler'

const router = useRouter()
const { handleApiError } = useErrorHandler()

// API data
const { 
  data: applicationData, 
  loading, 
  error, 
  refresh 
} = useApiData('/api/v1/teacher-approvals/', {
  immediate: true,
  transform: (data) => {
    // Transform the response to ensure consistent data structure
    if (data.results && data.results.length > 0) {
      const app = data.results[0] // Get the latest application
      return {
        id: app.id,
        status: app.status || 'pending',
        submitted_at: app.submitted_at || app.created_at,
        reviewed_at: app.reviewed_at,
        rejection_reason: app.rejection_reason,
        education: app.education,
        experience: app.experience,
        expertise_areas: app.expertise_areas,
        teaching_philosophy: app.teaching_philosophy
      }
    }
    return null
  },
  retryAttempts: 3,
  onError: (error) => {
    console.error('Failed to load application status:', error)
  }
})

// Computed application data
const application = computed(() => applicationData.value || {
  id: 'Not available',
  status: 'pending',
  submitted_at: null,
  reviewed_at: null,
  rejection_reason: null,
  education: 'Not provided',
  experience: 'Not provided',
  expertise_areas: 'Not provided',
  teaching_philosophy: 'Not provided'
})

const formatStatus = (status) => {
  const statusMap = {
    pending: 'Pending Review',
    approved: 'Approved',
    rejected: 'Not Approved'
  }
  return statusMap[status] || status
}

const getStatusIcon = (status) => {
  const iconMap = {
    pending: '⏳',
    approved: '✅',
    rejected: '❌'
  }
  return iconMap[status] || '📋'
}

const getStatusDescription = (status) => {
  const descriptionMap = {
    pending: 'Your application is currently being reviewed by our team. This process typically takes 1-2 business days.',
    approved: 'Congratulations! Your teacher application has been approved. You can now start creating courses.',
    rejected: 'Your application was not approved at this time. Please review the feedback below.'
  }
  return descriptionMap[status] || ''
}

const formatDate = (date) => {
  if (!date) return 'Not available'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const reapply = () => {
  // Navigate to reapplication form
  router.push('/teacher/apply')
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as any, { context: { action: 'retry_application_status_load' } })
  }
}

onMounted(() => {
  // Application status is loaded automatically via useApiData
})
</script>

<style scoped>
.application-status-view {
  max-width: 1000px;
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

.status-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.status-card, .details-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.status-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.status-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  flex-shrink: 0;
}

.status-icon.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-icon.approved {
  background: #dcfce7;
  color: #166534;
}

.status-icon.rejected {
  background: #fee2e2;
  color: #dc2626;
}

.status-info h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.status-description {
  color: #6b7280;
  font-size: 1rem;
  line-height: 1.6;
  margin: 0;
}

.status-timeline {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  position: relative;
}

.timeline-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 15px;
  top: 30px;
  width: 2px;
  height: calc(100% + 1.5rem);
  background: #e5e7eb;
}

.timeline-item.completed:not(:last-child)::after {
  background: #10b981;
}

.timeline-dot {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #e5e7eb;
  border: 3px solid white;
  box-shadow: 0 0 0 2px #e5e7eb;
  flex-shrink: 0;
  z-index: 1;
}

.timeline-dot.completed {
  background: #10b981;
  box-shadow: 0 0 0 2px #10b981;
}

.timeline-content h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.timeline-content p {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.rejection-feedback {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.rejection-feedback h4 {
  color: #dc2626;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.rejection-feedback p {
  color: #7f1d1d;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.reapply-section p {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.reapply-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reapply-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.approval-actions {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.approval-actions h4 {
  color: #166534;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.approval-actions p {
  color: #15803d;
  margin-bottom: 1.5rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  display: inline-block;
}

.action-btn.primary {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.action-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.action-btn.secondary {
  background: white;
  color: #10b981;
  border: 1px solid #10b981;
}

.action-btn.secondary:hover {
  background: #f0fdf4;
}

.details-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item strong {
  color: #374151;
  font-size: 0.875rem;
}

.detail-item span {
  color: #1f2937;
  font-weight: 500;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  width: fit-content;
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

.submitted-info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-item strong {
  display: block;
  color: #374151;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.info-item p {
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

/* Loading and Error States */
.loading-state, .error-state {
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
  border-top: 4px solid #f59e0b;
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
  background: linear-gradient(135deg, #f59e0b, #d97706);
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
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}
</style>