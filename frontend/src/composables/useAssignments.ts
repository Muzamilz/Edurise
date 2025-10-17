import { ref, computed, watch } from 'vue'
import AssignmentService from '../services/assignments'
import { useErrorHandler } from './useErrorHandler'
import { useAnimations } from './useAnimations'
import type {
  Assignment,
  Submission,
  Certificate,
  CourseProgress,
  CreateAssignmentRequest,
  UpdateAssignmentRequest,
  CreateSubmissionRequest,
  UpdateSubmissionRequest,
  GradeSubmissionRequest,
  AssignmentFilters,
  SubmissionFilters,
  CertificateFilters,
  DeadlineReminder,
  ProgressVisualizationData
} from '../types/assignments'

export const useAssignments = () => {
  const { handleError } = useErrorHandler()
  const { pulse, shake, bounce } = useAnimations()

  // State
  const assignments = ref<Assignment[]>([])
  const currentAssignment = ref<Assignment | null>(null)
  const submissions = ref<Submission[]>([])
  const currentSubmission = ref<Submission | null>(null)
  const certificates = ref<Certificate[]>([])
  const courseProgress = ref<CourseProgress | null>(null)
  const progressVisualization = ref<ProgressVisualizationData | null>(null)
  
  const loading = ref(false)
  const submitting = ref(false)
  const grading = ref(false)
  
  // Pagination
  const currentPage = ref(1)
  const totalPages = ref(1)
  const totalCount = ref(0)
  const hasNext = ref(false)
  const hasPrevious = ref(false)

  // Filters
  const assignmentFilters = ref<AssignmentFilters>({})
  const submissionFilters = ref<SubmissionFilters>({})
  const certificateFilters = ref<CertificateFilters>({})

  // Computed properties
  const publishedAssignments = computed(() => 
    assignments.value.filter(a => a.status === 'published')
  )

  const overdueAssignments = computed(() => 
    assignments.value.filter(a => a.is_overdue && a.status === 'published')
  )

  const upcomingAssignments = computed(() => 
    assignments.value.filter(a => !a.is_overdue && a.status === 'published')
      .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
  )

  const pendingSubmissions = computed(() => 
    submissions.value.filter(s => !s.is_graded)
  )

  const gradedSubmissions = computed(() => 
    submissions.value.filter(s => s.is_graded)
  )

  const lateSubmissions = computed(() => 
    submissions.value.filter(s => s.is_late)
  )

  const deadlineReminders = computed((): DeadlineReminder[] => {
    return upcomingAssignments.value.map(assignment => {
      const daysRemaining = assignment.days_until_due
      let urgencyLevel: DeadlineReminder['urgency_level'] = 'low'
      let animationType: DeadlineReminder['animation_type'] = 'pulse'

      if (daysRemaining <= 1) {
        urgencyLevel = 'critical'
        animationType = 'shake'
      } else if (daysRemaining <= 3) {
        urgencyLevel = 'high'
        animationType = 'bounce'
      } else if (daysRemaining <= 7) {
        urgencyLevel = 'medium'
        animationType = 'glow'
      }

      return {
        assignment_id: assignment.id,
        assignment_title: assignment.title,
        due_date: assignment.due_date,
        days_remaining: daysRemaining,
        urgency_level: urgencyLevel,
        animation_type: animationType
      }
    })
  })

  // Assignment operations
  const fetchAssignments = async (filters?: AssignmentFilters) => {
    loading.value = true
    try {
      const response = await AssignmentService.getAssignments(filters)
      assignments.value = response.results
      totalCount.value = response.count
      hasNext.value = !!response.next
      hasPrevious.value = !!response.previous
      totalPages.value = Math.ceil(response.count / 20) // Assuming 20 per page
    } catch (error) {
      handleError(error as Error, 'api')
    } finally {
      loading.value = false
    }
  }

  const fetchAssignment = async (id: string) => {
    loading.value = true
    try {
      currentAssignment.value = await AssignmentService.getAssignment(id)
    } catch (error) {
      handleError(error as Error, 'api')
    } finally {
      loading.value = false
    }
  }

  const createAssignment = async (data: CreateAssignmentRequest) => {
    submitting.value = true
    try {
      const assignment = await AssignmentService.createAssignment(data)
      assignments.value.unshift(assignment)
      return assignment
    } catch (error) {
      handleError(error as Error, 'api')
      throw error
    } finally {
      submitting.value = false
    }
  }

  const updateAssignment = async (id: string, data: UpdateAssignmentRequest) => {
    submitting.value = true
    try {
      const assignment = await AssignmentService.updateAssignment(id, data)
      const index = assignments.value.findIndex(a => a.id === id)
      if (index !== -1) {
        assignments.value[index] = assignment
      }
      if (currentAssignment.value?.id === id) {
        currentAssignment.value = assignment
      }
      return assignment
    } catch (error) {
      handleError(error as Error, 'api')
      throw error
    } finally {
      submitting.value = false
    }
  }

  const deleteAssignment = async (id: string) => {
    try {
      await AssignmentService.deleteAssignment(id)
      assignments.value = assignments.value.filter(a => a.id !== id)
      if (currentAssignment.value?.id === id) {
        currentAssignment.value = null
      }
    } catch (error) {
      handleError(error as Error, 'api')
      throw error
    }
  }

  const publishAssignment = async (id: string) => {
    try {
      const assignment = await AssignmentService.publishAssignment(id)
      const index = assignments.value.findIndex(a => a.id === id)
      if (index !== -1) {
        assignments.value[index] = assignment
      }
      if (currentAssignment.value?.id === id) {
        currentAssignment.value = assignment
      }
      return assignment
    } catch (error) {
      handleError(error as Error, 'api')
      throw error
    }
  }

  const closeAssignment = async (id: string) => {
    try {
      const assignment = await AssignmentService.closeAssignment(id)
      const index = assignments.value.findIndex(a => a.id === id)
      if (index !== -1) {
        assignments.value[index] = assignment
      }
      if (currentAssignment.value?.id === id) {
        currentAssignment.value = assignment
      }
      return assignment
    } catch (error) {
      handleError(error as Error, 'api')
      throw error
    }
  }

  // Submission operations
  const fetchSubmissions = async (filters?: SubmissionFilters) => {
    loading.value = true
    try {
      const response = await AssignmentService.getSubmissions(filters)
      submissions.value = response.results
    } catch (error) {
      handleError(error as Error, 'api')
    } finally {
      loading.value = false
    }
  }

  const fetchMySubmission = async (assignmentId: string) => {
    loading.value = true
    try {
      currentSubmission.value = await AssignmentService.getMySubmission(assignmentId)
    } catch (error) {
      handleError(error as Error, 'api')
    } finally {
      loading.value = false
    }
  }

  const createSubmission = async (data: CreateSubmissionRequest) => {
    submitting.value = true
    try {
      const submission = await AssignmentService.createSubmission(data)
      submissions.value.unshift(submission)
      currentSubmission.value = submission
      return submission
    } catch (error) {
      handleError(error as Error, 'api')
      throw error
    } finally {
      submitting.value = false
    }
  }

  const updateSubmission = async (id: string, data: UpdateSubmissionRequest) => {
    submitting.value = true
    try {
      const submission = await AssignmentService.updateSubmission(id, data)
      const index = submissions.value.findIndex(s => s.id === id)
      if (index !== -1) {
        submissions.value[index] = submission
      }
      if (currentSubmission.value?.id === id) {
        currentSubmission.value = submission
      }
      return submission
    } catch (error) {
      handleError(error as Error, 'api')
      throw error
    } finally {
      submitting.value = false
    }
  }

  const submitAssignment = async (id: string) => {
    submitting.value = true
    try {
      const submission = await AssignmentService.submitAssignment(id)
      const index = submissions.value.findIndex(s => s.id === id)
      if (index !== -1) {
        submissions.value[index] = submission
      }
      if (currentSubmission.value?.id === id) {
        currentSubmission.value = submission
      }
      return submission
    } catch (error) {
      handleError(error as Error, 'api')
      throw error
    } finally {
      submitting.value = false
    }
  }

  const gradeSubmission = async (id: string, data: GradeSubmissionRequest) => {
    grading.value = true
    try {
      const submission = await AssignmentService.gradeSubmission(id, data)
      const index = submissions.value.findIndex(s => s.id === id)
      if (index !== -1) {
        submissions.value[index] = submission
      }
      return submission
    } catch (error) {
      handleError(error as Error, 'api')
      throw error
    } finally {
      grading.value = false
    }
  }

  // Certificate operations
  const fetchCertificates = async (filters?: CertificateFilters) => {
    loading.value = true
    try {
      const response = await AssignmentService.getCertificates(filters)
      certificates.value = response.results
    } catch (error) {
      handleError(error as Error, 'api')
    } finally {
      loading.value = false
    }
  }

  const generateCertificate = async (courseId: string, studentId: string) => {
    submitting.value = true
    try {
      const certificate = await AssignmentService.generateCertificate(courseId, studentId)
      certificates.value.unshift(certificate)
      return certificate
    } catch (error) {
      handleError(error as Error, 'api')
      throw error
    } finally {
      submitting.value = false
    }
  }

  const downloadCertificate = async (id: string, filename?: string) => {
    try {
      const downloadUrl = await AssignmentService.downloadCertificate(id)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || `certificate-${id}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      // window.URL.revokeObjectURL(downloadUrl) // Not needed for direct URLs
    } catch (error) {
      handleError(error as Error, 'api')
      throw error
    }
  }

  // Progress tracking
  const fetchCourseProgress = async (courseId: string, studentId?: string) => {
    loading.value = true
    try {
      courseProgress.value = await AssignmentService.getCourseProgress(courseId, studentId)
    } catch (error) {
      handleError(error as Error, 'api')
    } finally {
      loading.value = false
    }
  }

  const fetchProgressVisualization = async (courseId: string, studentId?: string) => {
    loading.value = true
    try {
      progressVisualization.value = await AssignmentService.getProgressVisualizationData(courseId, studentId)
    } catch (error) {
      handleError(error as Error, 'api')
    } finally {
      loading.value = false
    }
  }

  // Animation helpers for deadline reminders
  const animateDeadlineReminder = (elementId: string, reminder: DeadlineReminder) => {
    const element = document.getElementById(elementId)
    if (!element) return

    switch (reminder.animation_type) {
      case 'pulse':
        pulse(element)
        break
      case 'shake':
        shake(element)
        break
      case 'glow':
        // Use pulse with different styling for glow effect
        pulse(element, { scale: [1, 1.02, 1], duration: 1500 })
        break
      case 'bounce':
        bounce(element)
        break
    }
  }

  const startDeadlineReminderAnimations = () => {
    deadlineReminders.value.forEach(reminder => {
      const elementId = `assignment-${reminder.assignment_id}`
      animateDeadlineReminder(elementId, reminder)
    })
  }

  // Utility functions
  const getAssignmentStatusColor = (assignment: Assignment) => {
    switch (assignment.status) {
      case 'draft': return 'gray'
      case 'published': return assignment.is_overdue ? 'red' : 'green'
      case 'closed': return 'orange'
      case 'archived': return 'gray'
      default: return 'gray'
    }
  }

  const getSubmissionStatusColor = (submission: Submission) => {
    switch (submission.status) {
      case 'draft': return 'gray'
      case 'submitted': return 'blue'
      case 'late': return 'orange'
      case 'graded': return submission.is_passing ? 'green' : 'red'
      case 'returned': return 'yellow'
      default: return 'gray'
    }
  }

  const formatTimeRemaining = (dueDate: string) => {
    const now = new Date()
    const due = new Date(dueDate)
    const diff = due.getTime() - now.getTime()
    
    if (diff <= 0) return 'Overdue'
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
    
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} remaining`
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} remaining`
    return 'Due soon'
  }

  // Watch for filter changes
  watch(assignmentFilters, (newFilters) => {
    fetchAssignments(newFilters)
  }, { deep: true })

  watch(submissionFilters, (newFilters) => {
    fetchSubmissions(newFilters)
  }, { deep: true })

  watch(certificateFilters, (newFilters) => {
    fetchCertificates(newFilters)
  }, { deep: true })

  return {
    // State
    assignments,
    currentAssignment,
    submissions,
    currentSubmission,
    certificates,
    courseProgress,
    progressVisualization,
    loading,
    submitting,
    grading,
    
    // Pagination
    currentPage,
    totalPages,
    totalCount,
    hasNext,
    hasPrevious,
    
    // Filters
    assignmentFilters,
    submissionFilters,
    certificateFilters,
    
    // Computed
    publishedAssignments,
    overdueAssignments,
    upcomingAssignments,
    pendingSubmissions,
    gradedSubmissions,
    lateSubmissions,
    deadlineReminders,
    
    // Assignment operations
    fetchAssignments,
    fetchAssignment,
    createAssignment,
    updateAssignment,
    deleteAssignment,
    publishAssignment,
    closeAssignment,
    
    // Submission operations
    fetchSubmissions,
    fetchMySubmission,
    createSubmission,
    updateSubmission,
    submitAssignment,
    gradeSubmission,
    
    // Certificate operations
    fetchCertificates,
    generateCertificate,
    downloadCertificate,
    
    // Progress tracking
    fetchCourseProgress,
    fetchProgressVisualization,
    
    // Animation helpers
    animateDeadlineReminder,
    startDeadlineReminderAnimations,
    
    // Utility functions
    getAssignmentStatusColor,
    getSubmissionStatusColor,
    formatTimeRemaining
  }
}

export default useAssignments