<template>
  <div class="certificates-view">
    <div class="page-header">
      <h1>My Certificates</h1>
      <p>View and download your earned certificates</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading your certificates...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Unable to load certificates</h3>
      <p>{{ error.message }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <!-- Certificates Content -->
    <div v-else class="certificates-content">
      <!-- Stats Overview -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">🏆</div>
          <h3>Total Certificates</h3>
          <p class="stat-number">{{ totalCertificates }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📚</div>
          <h3>Courses Completed</h3>
          <p class="stat-number">{{ completedCourses }}</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⭐</div>
          <h3>Average Score</h3>
          <p class="stat-number">{{ averageScore }}%</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📅</div>
          <h3>Latest Certificate</h3>
          <p class="stat-number">{{ latestCertificateDate }}</p>
        </div>
      </div>

      <!-- Certificates Grid -->
      <div v-if="certificates.length > 0" class="certificates-grid">
        <div v-for="certificate in certificates" :key="certificate.id" class="certificate-card">
          <div class="certificate-preview">
            <div class="certificate-icon">🏆</div>
            <div class="certificate-badge" :class="certificate.type">
              {{ formatCertificateType(certificate.type) }}
            </div>
          </div>
          
          <div class="certificate-info">
            <h3>{{ certificate.course_title }}</h3>
            <p class="instructor">Instructor: {{ certificate.instructor_name }}</p>
            <p class="completion-date">Completed: {{ formatDate(certificate.issued_at) }}</p>
            <p class="score" v-if="certificate.final_score">
              Final Score: {{ certificate.final_score }}%
            </p>
          </div>

          <div class="certificate-actions">
            <button @click="viewCertificate(certificate)" class="view-btn">
              <span class="btn-icon">👁️</span>
              View
            </button>
            <button @click="downloadCertificate(certificate)" class="download-btn">
              <span class="btn-icon">⬇️</span>
              Download
            </button>
            <button @click="shareCertificate(certificate)" class="share-btn">
              <span class="btn-icon">🔗</span>
              Share
            </button>
          </div>

          <div class="certificate-verification">
            <p class="verification-code">
              Verification: {{ certificate.verification_code }}
            </p>
            <button @click="verifyCertificate(certificate)" class="verify-btn">
              Verify Certificate
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">🏆</div>
        <h3>No certificates yet</h3>
        <p>Complete courses to earn certificates and showcase your achievements</p>
        <router-link to="/courses" class="browse-courses-btn">
          Browse Courses
        </router-link>
      </div>
    </div>

    <!-- Certificate Modal -->
    <div v-if="selectedCertificate" class="certificate-modal-overlay" @click="closeCertificateModal">
      <div class="certificate-modal" @click.stop>
        <div class="modal-header">
          <h2>Certificate Preview</h2>
          <button @click="closeCertificateModal" class="close-btn">&times;</button>
        </div>
        
        <div class="certificate-preview-large">
          <div class="certificate-content">
            <div class="certificate-header">
              <h1>Certificate of Completion</h1>
              <div class="certificate-logo">🎓</div>
            </div>
            
            <div class="certificate-body">
              <p class="certificate-text">This is to certify that</p>
              <h2 class="student-name">{{ fullName }}</h2>
              <p class="certificate-text">has successfully completed the course</p>
              <h3 class="course-title">{{ selectedCertificate.course_title }}</h3>
              <p class="instructor-text">
                Instructed by {{ selectedCertificate.instructor_name }}
              </p>
              <p class="completion-text">
                Completed on {{ formatDate(selectedCertificate.issued_at) }}
              </p>
              <p v-if="selectedCertificate.final_score" class="score-text">
                Final Score: {{ selectedCertificate.final_score }}%
              </p>
            </div>
            
            <div class="certificate-footer">
              <div class="verification-info">
                <p>Verification Code: {{ selectedCertificate.verification_code }}</p>
                <p>Certificate ID: {{ selectedCertificate.id }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="downloadCertificate(selectedCertificate)" class="download-btn">
            Download PDF
          </button>
          <button @click="shareCertificate(selectedCertificate)" class="share-btn">
            Share Certificate
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useApiData } from '@/composables/useApiData'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { api } from '@/services/api'

const { fullName } = useAuth()
const { handleApiError } = useErrorHandler()

// Reactive state
const selectedCertificate = ref(null)

// API data
const { 
  data: certificatesData, 
  loading, 
  error, 
  refresh 
} = useApiData('/api/v1/certificates/', {
  immediate: true,
  transform: (data) => {
    // Transform the response to ensure consistent data structure
    if (data.results) {
      return {
        ...data,
        results: data.results.map((certificate: any) => ({
          id: certificate.id,
          course_id: certificate.course?.id || certificate.course_id,
          course_title: certificate.course?.title || certificate.course_title,
          instructor_name: certificate.instructor?.full_name || certificate.instructor_name,
          issued_at: certificate.issued_at,
          verification_code: certificate.verification_code,
          certificate_url: certificate.certificate_url,
          final_score: certificate.final_score,
          type: certificate.type || 'completion'
        }))
      }
    }
    return data
  },
  retryAttempts: 3,
  onError: (error) => {
    console.error('Failed to load certificates:', error)
  }
})

// Computed properties
const certificates = computed(() => certificatesData.value?.results || [])
const totalCertificates = computed(() => certificates.value.length)
const completedCourses = computed(() => 
  new Set(certificates.value.map(cert => cert.course_id)).size
)
const averageScore = computed(() => {
  const scoresWithValues = certificates.value.filter(cert => cert.final_score)
  if (scoresWithValues.length === 0) return 0
  const total = scoresWithValues.reduce((sum, cert) => sum + cert.final_score, 0)
  return Math.round(total / scoresWithValues.length)
})
const latestCertificateDate = computed(() => {
  if (certificates.value.length === 0) return 'None'
  const latest = certificates.value.reduce((latest, cert) => 
    new Date(cert.issued_at) > new Date(latest.issued_at) ? cert : latest
  )
  return formatDate(latest.issued_at)
})

// Methods
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatCertificateType = (type: string) => {
  return type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')
}

const viewCertificate = (certificate: any) => {
  selectedCertificate.value = certificate
}

const closeCertificateModal = () => {
  selectedCertificate.value = null
}

const downloadCertificate = async (certificate: any) => {
  try {
    const response = await api.get(`/certificates/${certificate.id}/download/`, {
      responseType: 'blob'
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `certificate-${certificate.course_title}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    handleApiError(error, { context: { action: 'download_certificate' } })
  }
}

const shareCertificate = async (certificate: any) => {
  const shareUrl = `${window.location.origin}/certificates/verify/${certificate.verification_code}`
  
  if (navigator.share) {
    try {
      await navigator.share({
        title: `Certificate - ${certificate.course_title}`,
        text: `I've completed ${certificate.course_title} and earned a certificate!`,
        url: shareUrl
      })
    } catch (error) {
      // User cancelled sharing
    }
  } else {
    // Fallback: copy to clipboard
    try {
      await navigator.clipboard.writeText(shareUrl)
      alert('Certificate link copied to clipboard!')
    } catch (error) {
      // Fallback: show URL in prompt
      prompt('Copy this link to share your certificate:', shareUrl)
    }
  }
}

const verifyCertificate = (certificate: any) => {
  const verifyUrl = `${window.location.origin}/certificates/verify/${certificate.verification_code}`
  window.open(verifyUrl, '_blank')
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as any, { context: { action: 'retry_certificates_load' } })
  }
}

onMounted(() => {
  // Any additional setup if needed
})
</script>

<style scoped>
.certificates-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
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
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15);
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

.certificates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.certificate-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  transition: all 0.3s ease;
}

.certificate-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15);
}

.certificate-preview {
  position: relative;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  margin-bottom: 1rem;
}

.certificate-icon {
  font-size: 3rem;
  color: white;
  margin-bottom: 0.5rem;
}

.certificate-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.certificate-info h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.certificate-info p {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.score {
  color: #10b981 !important;
  font-weight: 500;
}

.certificate-actions {
  display: flex;
  gap: 0.5rem;
  margin: 1rem 0;
}

.certificate-actions button {
  flex: 1;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.view-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.download-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.share-btn {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
}

.certificate-actions button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.certificate-verification {
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
  text-align: center;
}

.verification-code {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
  font-family: monospace;
}

.verify-btn {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  color: #92400e;
  border: 1px solid rgba(245, 158, 11, 0.3);
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.verify-btn:hover {
  background: linear-gradient(135deg, #fed7aa, #fdba74);
  border-color: #f59e0b;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
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
  margin-bottom: 1.5rem;
}

.browse-courses-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-block;
}

.browse-courses-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

/* Certificate Modal */
.certificate-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.certificate-modal {
  background: white;
  border-radius: 12px;
  max-width: 800px;
  width: 100%;
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

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0.25rem;
}

.close-btn:hover {
  color: #1f2937;
}

.certificate-preview-large {
  padding: 2rem;
}

.certificate-content {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  border: 2px solid #f59e0b;
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  position: relative;
}

.certificate-header {
  margin-bottom: 2rem;
}

.certificate-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #92400e;
  margin-bottom: 1rem;
}

.certificate-logo {
  font-size: 3rem;
}

.certificate-body {
  margin-bottom: 2rem;
}

.certificate-text {
  font-size: 1rem;
  color: #92400e;
  margin-bottom: 0.5rem;
}

.student-name {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin: 1rem 0;
  text-decoration: underline;
}

.course-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #92400e;
  margin: 1rem 0;
  font-style: italic;
}

.instructor-text, .completion-text, .score-text {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.certificate-footer {
  border-top: 1px solid rgba(146, 64, 14, 0.3);
  padding-top: 1rem;
}

.verification-info p {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
  font-family: monospace;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  justify-content: center;
}

.modal-actions button {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-actions .download-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.modal-actions .share-btn {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
}

.modal-actions button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* Loading and Error States */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
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

/* Responsive */
@media (max-width: 768px) {
  .certificates-view {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .certificates-grid {
    grid-template-columns: 1fr;
  }
  
  .certificate-actions {
    flex-direction: column;
  }
  
  .certificate-modal {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }
  
  .certificate-content {
    padding: 2rem 1rem;
  }
  
  .student-name {
    font-size: 1.5rem;
  }
  
  .course-title {
    font-size: 1.25rem;
  }
  
  .modal-actions {
    flex-direction: column;
  }
}
</style>