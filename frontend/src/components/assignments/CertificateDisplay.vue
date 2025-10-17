<template>
  <div class="certificate-display">
    <!-- Certificate Card -->
    <div class="bg-white rounded-lg shadow-lg border-2 border-gray-200 overflow-hidden">
      <!-- Certificate Header -->
      <div class="bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-6 text-white">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-2xl font-bold">{{ formatCertificateType(certificate.certificate_type) }}</h2>
            <p class="text-blue-100 mt-1">Certificate #{{ certificate.certificate_number }}</p>
          </div>
          
          <div class="text-right">
            <div class="text-sm text-blue-100">Status</div>
            <span
              :class="getCertificateStatusClass()"
              class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
            >
              {{ certificate.status.charAt(0).toUpperCase() + certificate.status.slice(1) }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- Certificate Body -->
      <div class="px-8 py-8">
        <div class="text-center mb-8">
          <div class="text-lg text-gray-600 mb-2">This is to certify that</div>
          <div class="text-3xl font-bold text-gray-900 mb-2">
            {{ certificate.student.full_name }}
          </div>
          <div class="text-lg text-gray-600 mb-6">has successfully completed</div>
          <div class="text-2xl font-semibold text-blue-600 mb-4">
            {{ certificate.course.title }}
          </div>
          <div class="text-gray-600">
            Instructed by {{ certificate.instructor.full_name }}
          </div>
        </div>
        
        <!-- Achievement Details -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <div class="text-2xl font-bold text-gray-900">
              {{ certificate.final_grade ? `${certificate.final_grade}%` : 'N/A' }}
            </div>
            <div class="text-sm text-gray-600">Final Grade</div>
          </div>
          
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <div class="text-2xl font-bold text-gray-900">
              {{ formatDate(certificate.completion_date) }}
            </div>
            <div class="text-sm text-gray-600">Completion Date</div>
          </div>
          
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <div class="text-2xl font-bold text-gray-900">
              {{ certificate.is_valid ? 'Valid' : 'Invalid' }}
            </div>
            <div class="text-sm text-gray-600">Certificate Status</div>
          </div>
        </div>
        
        <!-- QR Code and Verification -->
        <div class="flex items-center justify-between border-t border-gray-200 pt-6">
          <div class="flex items-center space-x-4">
            <div v-if="certificate.qr_code_url" class="flex-shrink-0">
              <img
                :src="certificate.qr_code_url"
                alt="QR Code for verification"
                class="w-16 h-16 border border-gray-300 rounded"
              />
            </div>
            <div>
              <div class="text-sm font-medium text-gray-900">Verification</div>
              <div class="text-sm text-gray-600">
                Scan QR code or visit: 
                <a
                  :href="getFullVerificationUrl()"
                  target="_blank"
                  class="text-blue-600 hover:text-blue-800"
                >
                  {{ getFullVerificationUrl() }}
                </a>
              </div>
            </div>
          </div>
          
          <div class="text-right text-sm text-gray-500">
            <div>Issued: {{ certificate.issued_at ? formatDate(certificate.issued_at) : 'Pending' }}</div>
            <div>Certificate ID: {{ certificate.id }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Action Buttons -->
    <div class="mt-6 flex justify-center space-x-4">
      <button
        v-if="certificate.certificate_file_url || certificate.pdf_file"
        @click="handleDownloadCertificate"
        class="inline-flex items-center px-6 py-3 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Download PDF
      </button>
      
      <button
        v-if="!certificate.certificate_file_url && !certificate.pdf_file"
        @click="generateCertificatePDF"
        :disabled="generatingPDF"
        class="inline-flex items-center px-6 py-3 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
      >
        <svg v-if="!generatingPDF" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <svg v-else class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ generatingPDF ? 'Generating...' : 'Generate PDF' }}
      </button>
      
      <button
        @click="shareCertificate"
        class="inline-flex items-center px-6 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
        </svg>
        Share
      </button>
      
      <button
        @click="verifyCertificate"
        class="inline-flex items-center px-6 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Verify
      </button>
    </div>
    
    <!-- Verification Modal -->
    <div
      v-if="showVerificationModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="closeVerificationModal"
    >
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">Certificate Verification</h3>
            <button
              @click="closeVerificationModal"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="mb-4">
            <label for="certificate-number" class="block text-sm font-medium text-gray-700 mb-2">
              Certificate Number
            </label>
            <input
              id="certificate-number"
              v-model="verificationNumber"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter certificate number"
            />
          </div>
          
          <div class="flex justify-end space-x-3">
            <button
              @click="closeVerificationModal"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              @click="handleVerification"
              :disabled="!verificationNumber || verifying"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {{ verifying ? 'Verifying...' : 'Verify' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Verification Result Modal -->
    <div
      v-if="showVerificationResult"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="closeVerificationResult"
    >
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">Verification Result</h3>
            <button
              @click="closeVerificationResult"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="text-center">
            <div
              :class="verificationResult?.valid ? 'text-green-600' : 'text-red-600'"
              class="text-4xl mb-4"
            >
              <svg v-if="verificationResult?.valid" class="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <svg v-else class="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            
            <h4 class="text-lg font-semibold mb-2" :class="verificationResult?.valid ? 'text-green-600' : 'text-red-600'">
              {{ verificationResult?.valid ? 'Certificate Valid' : 'Certificate Invalid' }}
            </h4>
            
            <p class="text-gray-600 mb-4">{{ verificationResult?.message }}</p>
            
            <div v-if="verificationResult?.certificate" class="text-left bg-gray-50 p-4 rounded-md">
              <div class="text-sm space-y-2">
                <div><strong>Student:</strong> {{ verificationResult.certificate.student.first_name }} {{ verificationResult.certificate.student.last_name }}</div>
                <div><strong>Course:</strong> {{ verificationResult.certificate.course.title }}</div>
                <div><strong>Completion Date:</strong> {{ formatDate(verificationResult.certificate.completion_date) }}</div>
                <div v-if="verificationResult.certificate.final_grade">
                  <strong>Final Grade:</strong> {{ verificationResult.certificate.final_grade }}%
                </div>
              </div>
            </div>
          </div>
          
          <div class="mt-6 flex justify-center">
            <button
              @click="closeVerificationResult"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
// import { useAssignments } from '../../composables/useAssignments' // Unused for now
import AssignmentService from '../../services/assignments'
import type { Certificate, CertificateVerificationResponse } from '../../types/assignments'

interface Props {
  certificate: Certificate
}

const props = defineProps<Props>()

// const { downloadCertificate } = useAssignments() // Unused for now

// Verification state
const showVerificationModal = ref(false)
const showVerificationResult = ref(false)
const verificationNumber = ref('')
const verifying = ref(false)
const verificationResult = ref<CertificateVerificationResponse | null>(null)

// PDF generation state
const generatingPDF = ref(false)

// Methods
const formatCertificateType = (type: string) => {
  const types = {
    completion: 'Certificate of Completion',
    achievement: 'Certificate of Achievement',
    participation: 'Certificate of Participation',
    excellence: 'Certificate of Excellence'
  }
  return types[type as keyof typeof types] || type
}

const getCertificateStatusClass = () => {
  switch (props.certificate.status) {
    case 'issued':
      return 'bg-green-100 text-green-800'
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'revoked':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getFullVerificationUrl = () => {
  return `${window.location.origin}${props.certificate.verification_url}`
}

const handleDownloadCertificate = async () => {
  try {
    // Use centralized API to get download URL
    const downloadUrl = await AssignmentService.downloadCertificate(props.certificate.id)
    
    // Create download link
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `${props.certificate.certificate_number}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download certificate:', error)
    alert('Failed to download certificate. Please try again.')
  }
}

const shareCertificate = async () => {
  const shareData = {
    title: `${formatCertificateType(props.certificate.certificate_type)} - ${props.certificate.course.title}`,
    text: `I have successfully completed ${props.certificate.course.title} and earned a ${formatCertificateType(props.certificate.certificate_type)}!`,
    url: getFullVerificationUrl()
  }
  
  if (navigator.share) {
    try {
      await navigator.share(shareData)
    } catch (error) {
      // User cancelled sharing or sharing not supported
      copyToClipboard(getFullVerificationUrl())
    }
  } else {
    copyToClipboard(getFullVerificationUrl())
  }
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('Certificate verification URL copied to clipboard!')
  } catch (error) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    alert('Certificate verification URL copied to clipboard!')
  }
}

const verifyCertificate = () => {
  verificationNumber.value = props.certificate.certificate_number
  showVerificationModal.value = true
}

const closeVerificationModal = () => {
  showVerificationModal.value = false
  verificationNumber.value = ''
}

const handleVerification = async () => {
  if (!verificationNumber.value) return
  
  verifying.value = true
  try {
    const result = await AssignmentService.verifyCertificate({
      certificate_number: verificationNumber.value
    })
    
    // Transform the result to match the expected format
    verificationResult.value = {
      valid: result.valid,
      message: result.valid ? 'Certificate is valid' : result.message,
      certificate: result.valid && result.certificate && result.student_name ? {
        id: result.certificate.id,
        student: {
          first_name: result.student_name.split(' ')[0],
          last_name: result.student_name.split(' ').slice(1).join(' ')
        },
        course: {
          title: result.course_title || 'Unknown Course'
        },
        completion_date: result.completion_date,
        final_grade: result.final_grade
      } : undefined
    }
    
    showVerificationModal.value = false
    showVerificationResult.value = true
  } catch (error) {
    console.error('Verification failed:', error)
    verificationResult.value = {
      valid: false,
      message: 'Verification failed. Please try again.'
    }
    showVerificationModal.value = false
    showVerificationResult.value = true
  } finally {
    verifying.value = false
  }
}

const closeVerificationResult = () => {
  showVerificationResult.value = false
  verificationResult.value = null
}

const generateCertificatePDF = async () => {
  generatingPDF.value = true
  try {
    const result = await AssignmentService.generateCertificatePDF(props.certificate.id)
    
    // Update certificate data with new file URL
    props.certificate.certificate_file_url = result.download_url
    
    alert('Certificate PDF generated successfully!')
  } catch (error) {
    console.error('Failed to generate certificate PDF:', error)
    alert('Failed to generate certificate PDF. Please try again.')
  } finally {
    generatingPDF.value = false
  }
}
</script>

<style scoped>
/* Certificate styling */
.certificate-display {
  max-width: 800px;
  margin: 0 auto;
}

/* Print styles */
@media print {
  .certificate-display > div:last-child {
    display: none;
  }
  
  .certificate-display > div:first-child {
    box-shadow: none;
    border: 2px solid #000;
  }
}

/* Animation for certificate display */
.certificate-display > div:first-child {
  animation: certificateSlideIn 0.6s ease-out;
}

@keyframes certificateSlideIn {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Modal backdrop animation */
.fixed.inset-0 {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Modal content animation */
.relative.top-20 {
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>