<template>
  <div class="assignments-view">
    <!-- Page Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Assignments</h1>
              <p class="mt-1 text-sm text-gray-600">
                {{ isTeacher ? 'Manage course assignments and grade submissions' : 'View and submit your assignments' }}
              </p>
            </div>
            
            <div class="flex space-x-3">
              <button
                v-if="!isTeacher"
                @click="showProgressVisualization = !showProgressVisualization"
                class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                {{ showProgressVisualization ? 'Hide Progress' : 'Show Progress' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Progress Visualization (for students) -->
      <div v-if="!isTeacher && showProgressVisualization && courseId" class="mb-8">
        <ProgressVisualization :course-id="courseId" />
      </div>

      <!-- Assignment List -->
      <div class="mb-8">
        <AssignmentList
          :course-id="courseId"
          :show-progress="isTeacher"
          @create-assignment="handleCreateAssignment"
          @edit-assignment="handleEditAssignment"
          @view-assignment="handleViewAssignment"
          @view-submissions="handleViewSubmissions"
          @start-submission="handleStartSubmission"
        />
      </div>
    </div>

    <!-- Assignment Form Modal -->
    <div
      v-if="showAssignmentForm"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="closeAssignmentForm"
    >
      <div class="relative top-20 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ editingAssignment ? 'Edit Assignment' : 'Create Assignment' }}
            </h3>
            <button
              @click="closeAssignmentForm"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <AssignmentForm
            :course-id="courseId!"
            :assignment="editingAssignment || undefined"
            @submit="handleAssignmentSubmit"
            @cancel="closeAssignmentForm"
          />
        </div>
      </div>
    </div>

    <!-- Submission Form Modal -->
    <div
      v-if="showSubmissionForm && selectedAssignment"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="closeSubmissionForm"
    >
      <div class="relative top-20 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">Submit Assignment</h3>
            <button
              @click="closeSubmissionForm"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <SubmissionForm
            :assignment="selectedAssignment"
            :existing-submission="currentSubmission"
            @submit="handleSubmissionSubmit"
            @cancel="closeSubmissionForm"
          />
        </div>
      </div>
    </div>

    <!-- Grading Dashboard Modal -->
    <div
      v-if="showGradingDashboard && selectedAssignment"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="closeGradingDashboard"
    >
      <div class="relative top-20 mx-auto p-5 border w-full max-w-7xl shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">Grading Dashboard</h3>
            <button
              @click="closeGradingDashboard"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <GradingDashboard :assignment="selectedAssignment" />
        </div>
      </div>
    </div>

    <!-- Certificate Display Modal -->
    <div
      v-if="showCertificateModal && selectedCertificate"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="closeCertificateModal"
    >
      <div class="relative top-20 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">Certificate</h3>
            <button
              @click="closeCertificateModal"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <CertificateDisplay :certificate="selectedCertificate" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../../composables/useAuth'
import { useAssignments } from '../../composables/useAssignments'
import AssignmentList from '../../components/assignments/AssignmentList.vue'
import AssignmentForm from '../../components/assignments/AssignmentForm.vue'
import SubmissionForm from '../../components/assignments/SubmissionForm.vue'
import GradingDashboard from '../../components/assignments/GradingDashboard.vue'
import CertificateDisplay from '../../components/assignments/CertificateDisplay.vue'
import ProgressVisualization from '../../components/assignments/ProgressVisualization.vue'
import type { Assignment, Submission, Certificate } from '../../types/assignments'

const route = useRoute()
const { user } = useAuth()
const { fetchMySubmission, currentSubmission } = useAssignments()

// Route params
const courseId = computed(() => route.params.courseId as string)

// User role
const isTeacher = computed(() => 
  user.value?.current_profile?.role === 'teacher' || 
  user.value?.current_profile?.role === 'admin' || 
  user.value?.is_staff
)

// Modal states
const showAssignmentForm = ref(false)
const showSubmissionForm = ref(false)
const showGradingDashboard = ref(false)
const showCertificateModal = ref(false)
const showProgressVisualization = ref(false)

// Selected items
const editingAssignment = ref<Assignment | null>(null)
const selectedAssignment = ref<Assignment | null>(null)
const selectedCertificate = ref<Certificate | null>(null)

// Assignment form handlers
const handleCreateAssignment = () => {
  editingAssignment.value = null
  showAssignmentForm.value = true
}

const handleEditAssignment = (assignment: Assignment) => {
  editingAssignment.value = assignment
  showAssignmentForm.value = true
}

const handleAssignmentSubmit = (_assignment: Assignment) => {
  showAssignmentForm.value = false
  editingAssignment.value = null
  // Assignment list will automatically update via the composable
}

const closeAssignmentForm = () => {
  showAssignmentForm.value = false
  editingAssignment.value = null
}

// Submission form handlers
const handleStartSubmission = async (assignment: Assignment) => {
  selectedAssignment.value = assignment
  
  // Fetch existing submission if any
  await fetchMySubmission(assignment.id)
  
  showSubmissionForm.value = true
}

const handleSubmissionSubmit = (_submission: Submission) => {
  showSubmissionForm.value = false
  selectedAssignment.value = null
  // Submission will be updated via the composable
}

const closeSubmissionForm = () => {
  showSubmissionForm.value = false
  selectedAssignment.value = null
}

// Grading dashboard handlers
const handleViewSubmissions = (assignment: Assignment) => {
  selectedAssignment.value = assignment
  showGradingDashboard.value = true
}

const closeGradingDashboard = () => {
  showGradingDashboard.value = false
  selectedAssignment.value = null
}

// Assignment view handler
const handleViewAssignment = (assignment: Assignment) => {
  // For now, just show the assignment details
  // In a full implementation, this might navigate to a detailed view
  console.log('Viewing assignment:', assignment)
}

// Certificate modal handlers (unused for now)
// const handleViewCertificate = (certificate: Certificate) => {
//   selectedCertificate.value = certificate
//   showCertificateModal.value = true
// }

const closeCertificateModal = () => {
  showCertificateModal.value = false
  selectedCertificate.value = null
}

// Initialize component
onMounted(() => {
  // Any initialization logic can go here
})
</script>

<style scoped>
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

/* Responsive design */
@media (max-width: 768px) {
  .relative.top-20 {
    top: 10px;
    margin: 10px;
    width: calc(100% - 20px);
  }
}
</style>