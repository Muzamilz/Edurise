<template>
  <div class="teacher-detail-view">
    <div class="page-header">
      <h1>Teacher Details</h1>
      <p>Review teacher application and profile information</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading teacher details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Failed to load teacher details</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Teacher Details -->
    <div v-else-if="teacher" class="teacher-details">
      <div class="teacher-profile">
        <div class="profile-header">
          <div class="teacher-avatar">
            <img :src="teacher.avatar || '/default-avatar.jpg'" :alt="teacher.name" />
          </div>
          <div class="teacher-info">
            <h2>{{ teacher.first_name }} {{ teacher.last_name }}</h2>
            <p class="teacher-email">{{ teacher.email }}</p>
            <div class="status-badge" :class="teacher.status">
              {{ formatStatus(teacher.status) }}
            </div>
          </div>
        </div>

        <div class="profile-content">
          <div class="info-section">
            <h3>Application Details</h3>
            <div class="info-grid">
              <div class="info-item">
                <strong>Education:</strong>
                <p>{{ teacher.education || 'Not provided' }}</p>
              </div>
              <div class="info-item">
                <strong>Experience:</strong>
                <p>{{ teacher.experience || 'Not provided' }}</p>
              </div>
              <div class="info-item">
                <strong>Expertise Areas:</strong>
                <p>{{ teacher.expertise_areas || 'Not provided' }}</p>
              </div>
              <div class="info-item">
                <strong>Teaching Philosophy:</strong>
                <p>{{ teacher.teaching_philosophy || 'Not provided' }}</p>
              </div>
            </div>
          </div>

          <div v-if="teacher.status === 'pending'" class="actions-section">
            <button @click="approveTeacher" class="action-btn approve">
              <span class="btn-icon">✅</span>
              Approve Teacher
            </button>
            <button @click="showRejectModal = true" class="action-btn reject">
              <span class="btn-icon">❌</span>
              Reject Application
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="modal-overlay" @click="closeRejectModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Reject Application</h3>
          <button @click="closeRejectModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <p>Provide a reason for rejecting this application:</p>
          <textarea 
            v-model="rejectionReason" 
            placeholder="Reason for rejection..."
            rows="4"
          ></textarea>
          <div class="form-actions">
            <button @click="closeRejectModal" class="cancel-btn">Cancel</button>
            <button @click="rejectTeacher" class="reject-btn">Reject</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApiData, useApiMutation } from '@/composables/useApiData'
import { useErrorHandler } from '@/composables/useErrorHandler'

const route = useRoute()
const router = useRouter()
const { handleApiError } = useErrorHandler()

const teacherId = route.params.id
const showRejectModal = ref(false)
const rejectionReason = ref('')

// Data fetching
const { data: teacher, loading, error, refresh } = useApiData(`/api/v1/teacher-approvals/${teacherId}/`)

// Mutations
const { mutate: approveTeacherMutation } = useApiMutation(
  () => ({ method: 'POST', url: `/api/v1/teacher-approvals/${teacherId}/approve/` }),
  {
    onSuccess: () => {
      router.push('/admin/teachers/pending')
    },
    onError: (error) => handleApiError(error, { context: { action: 'approve_teacher' } })
  }
)

const { mutate: rejectTeacherMutation } = useApiMutation(
  (reason) => ({ 
    method: 'POST', 
    url: `/api/v1/teacher-approvals/${teacherId}/reject/`,
    data: { notes: reason }
  }),
  {
    onSuccess: () => {
      router.push('/admin/teachers/pending')
    },
    onError: (error) => handleApiError(error, { context: { action: 'reject_teacher' } })
  }
)

// Methods
const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const approveTeacher = async () => {
  if (confirm('Are you sure you want to approve this teacher application?')) {
    await approveTeacherMutation()
  }
}

const rejectTeacher = async () => {
  await rejectTeacherMutation(rejectionReason.value)
  closeRejectModal()
}

const closeRejectModal = () => {
  showRejectModal.value = false
  rejectionReason.value = ''
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err, { context: { action: 'retry_teacher_load' } })
  }
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.teacher-detail-view {
  max-width: 1000px;
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

.teacher-details {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.teacher-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.teacher-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.teacher-info h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.teacher-email {
  color: #6b7280;
  font-size: 1rem;
  margin-bottom: 1rem;
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
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

.profile-content {
  padding: 2rem;
}

.info-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.info-grid {
  display: grid;
  gap: 1.5rem;
}

.info-item strong {
  display: block;
  color: #374151;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.info-item p {
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

.actions-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 1rem;
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

.modal-body p {
  margin-bottom: 1rem;
  color: #374151;
}

.modal-body textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
  resize: vertical;
  margin-bottom: 1.5rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.cancel-btn, .reject-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
}

.cancel-btn {
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
}

.reject-btn {
  border: none;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
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