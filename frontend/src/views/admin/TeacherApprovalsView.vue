<template>
  <div class="teacher-approvals-view">
    <div class="page-header">
      <h1>Teacher Approvals</h1>
      <p>Review and approve teacher applications for your organization</p>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">⏳</div>
        <h3>Pending</h3>
        <p class="stat-number">{{ pendingCount }}</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <h3>Approved</h3>
        <p class="stat-number">{{ approvedCount }}</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon">❌</div>
        <h3>Rejected</h3>
        <p class="stat-number">{{ rejectedCount }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-controls">
        <select v-model="statusFilter" class="filter-select">
          <option value="">All Applications</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by name or email..."
          class="search-input"
        />
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
      <h3>Failed to load applications</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Applications List -->
    <div v-else class="applications-container">
      <div v-if="filteredApplications.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>No applications found</h3>
        <p>{{ statusFilter ? `No ${statusFilter} applications` : 'No teacher applications yet' }}</p>
      </div>

      <div v-else class="applications-grid">
        <div v-for="application in filteredApplications" :key="application.id" class="application-card">
          <div class="application-header">
            <div class="applicant-info">
              <div class="applicant-avatar">
                <img :src="application.user.avatar || '/default-avatar.jpg'" :alt="application.user.name" />
              </div>
              <div class="applicant-details">
                <h3>{{ application.user.first_name }} {{ application.user.last_name }}</h3>
                <p class="applicant-email">{{ application.user.email }}</p>
                <span class="application-date">Applied {{ formatDate(application.created_at) }}</span>
              </div>
            </div>
            <div class="status-badge" :class="application.status">
              {{ formatStatus(application.status) }}
            </div>
          </div>

          <div class="application-content">
            <div class="qualification-section">
              <h4>Qualifications</h4>
              <div class="qualification-item">
                <strong>Education:</strong>
                <p>{{ application.education || 'Not provided' }}</p>
              </div>
              <div class="qualification-item">
                <strong>Experience:</strong>
                <p>{{ application.experience || 'Not provided' }}</p>
              </div>
              <div class="qualification-item">
                <strong>Expertise Areas:</strong>
                <p>{{ application.expertise_areas || 'Not provided' }}</p>
              </div>
              <div class="qualification-item">
                <strong>Teaching Philosophy:</strong>
                <p>{{ application.teaching_philosophy || 'Not provided' }}</p>
              </div>
            </div>

            <div v-if="application.documents && application.documents.length > 0" class="documents-section">
              <h4>Supporting Documents</h4>
              <div class="documents-list">
                <div v-for="doc in application.documents" :key="doc.id" class="document-item">
                  <span class="document-icon">📄</span>
                  <span class="document-name">{{ doc.name }}</span>
                  <button @click="downloadDocument(doc)" class="download-btn">Download</button>
                </div>
              </div>
            </div>

            <div v-if="application.status === 'rejected' && application.rejection_reason" class="rejection-reason">
              <h4>Rejection Reason</h4>
              <p>{{ application.rejection_reason }}</p>
            </div>
          </div>

          <div v-if="application.status === 'pending'" class="application-actions">
            <button @click="showRejectModal(application)" class="action-btn reject">
              <span class="btn-icon">❌</span>
              Reject
            </button>
            <button @click="approveApplication(application)" class="action-btn approve">
              <span class="btn-icon">✅</span>
              Approve
            </button>
          </div>

          <div v-else class="application-info">
            <p class="processed-info">
              {{ application.status === 'approved' ? 'Approved' : 'Rejected' }} 
              {{ application.processed_at ? `on ${formatDate(application.processed_at)}` : '' }}
              {{ application.processed_by ? `by ${application.processed_by.first_name} ${application.processed_by.last_name}` : '' }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Rejection Modal -->
    <div v-if="showRejectModalFlag" class="modal-overlay" @click="closeRejectModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Reject Application</h3>
          <button @click="closeRejectModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to reject {{ selectedApplication?.user.first_name }} {{ selectedApplication?.user.last_name }}'s application?</p>
          <div class="form-group">
            <label>Reason for rejection (optional)</label>
            <textarea 
              v-model="rejectionReason" 
              placeholder="Provide feedback to help the applicant improve..."
              rows="4"
            ></textarea>
          </div>
          <div class="form-actions">
            <button @click="closeRejectModal" class="cancel-btn">Cancel</button>
            <button @click="rejectApplication" class="reject-btn">Reject Application</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useApiData, useApiMutation } from '@/composables/useApiData'
import type { APIError } from '@/services/api'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { AdminService } from '@/services/admin'

const { handleApiError } = useErrorHandler()

// Data fetching
const { data: applications, loading, error, refresh } = useApiData<any[]>('/teacher-approvals/')

// Filters and search
const statusFilter = ref('')
const searchQuery = ref('')

// Modal state
const showRejectModalFlag = ref(false)
const selectedApplication = ref<any>(null)
const rejectionReason = ref('')

// Mutations
const { mutate: approveTeacher } = useApiMutation(
  (applicationId) => AdminService.approveTeacher(applicationId),
  {
    onSuccess: () => {
      refresh()
    },
    onError: (error) => handleApiError(error as APIError, { context: { action: 'approve_teacher' } })
  }
)

const { mutate: rejectTeacher } = useApiMutation(
  ({ applicationId, reason }) => AdminService.rejectTeacher(applicationId, reason),
  {
    onSuccess: () => {
      closeRejectModal()
      refresh()
    },
    onError: (error) => handleApiError(error as APIError, { context: { action: 'reject_teacher' } })
  }
)

// Computed properties
const filteredApplications = computed(() => {
  if (!applications.value) return []
  
  return applications.value.filter((app: any) => {
    const matchesStatus = !statusFilter.value || app.status === statusFilter.value
    const matchesSearch = !searchQuery.value || 
      app.user.first_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      app.user.last_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      app.user.email.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    return matchesStatus && matchesSearch
  })
})

const pendingCount = computed(() => 
  applications.value?.filter((app: any) => app.status === 'pending').length || 0
)

const approvedCount = computed(() => 
  applications.value?.filter((app: any) => app.status === 'approved').length || 0
)

const rejectedCount = computed(() => 
  applications.value?.filter((app: any) => app.status === 'rejected').length || 0
)

// Methods
const formatDate = (date: any) => {
  if (!date) return 'Unknown'
  return new Date(date).toLocaleDateString()
}

const formatStatus = (status: any) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const showRejectModal = (application: any) => {
  selectedApplication.value = application
  showRejectModalFlag.value = true
  rejectionReason.value = ''
}

const closeRejectModal = () => {
  showRejectModalFlag.value = false
  selectedApplication.value = null
  rejectionReason.value = ''
}

const approveApplication = async (application: any) => {
  if (confirm(`Are you sure you want to approve ${application.user.first_name} ${application.user.last_name}'s application?`)) {
    await approveTeacher(application.id)
  }
}

const rejectApplication = async () => {
  if (selectedApplication.value) {
    await rejectTeacher({
      applicationId: selectedApplication.value.id,
      reason: rejectionReason.value
    })
  }
}

const downloadDocument = (document: any) => {
  // Implement document download
  window.open(document.url, '_blank')
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as APIError, { context: { action: 'retry_applications_load' } })
  }
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.teacher-approvals-view {
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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
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
  color: #f59e0b;
  margin: 0;
}

.filters-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.filter-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  min-width: 200px;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
}

.search-input:focus, .filter-select:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.applications-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.applications-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.application-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.application-card:hover {
  border-color: #f59e0b;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.1);
}

.application-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.applicant-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.applicant-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.applicant-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.applicant-details h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.applicant-email {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0 0 0.25rem 0;
}

.application-date {
  color: #f59e0b;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
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

.application-content {
  margin-bottom: 1.5rem;
}

.qualification-section, .documents-section, .rejection-reason {
  margin-bottom: 1.5rem;
}

.qualification-section h4, .documents-section h4, .rejection-reason h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.qualification-item {
  margin-bottom: 1rem;
}

.qualification-item strong {
  display: block;
  color: #374151;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.qualification-item p {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
  line-height: 1.5;
}

.documents-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.document-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
}

.document-icon {
  font-size: 1.25rem;
}

.document-name {
  flex: 1;
  font-size: 0.875rem;
  color: #374151;
}

.download-btn {
  padding: 0.25rem 0.75rem;
  background: #dbeafe;
  color: #1e40af;
  border: none;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.download-btn:hover {
  background: #bfdbfe;
}

.rejection-reason p {
  color: #dc2626;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
}

.application-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.action-btn {
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

.action-btn.approve {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.action-btn.approve:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

.action-btn.reject {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.action-btn.reject:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
}

.application-info {
  text-align: right;
}

.processed-info {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
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
  max-height: 90vh;
  overflow-y: auto;
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
  padding: 0.25rem;
}

.close-btn:hover {
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.modal-body p {
  margin-bottom: 1.5rem;
  color: #374151;
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

.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
  resize: vertical;
}

.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
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

.reject-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.reject-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
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