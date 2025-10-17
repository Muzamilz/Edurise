import { ref, computed } from 'vue'
import { useApiMutation, useApiData } from './useApiData'
import { useErrorHandler } from './useErrorHandler'
import { useAuth } from './useAuth'
import { api } from '@/services/api'
import { CacheInvalidation, CachePresets } from '@/utils/apiCache'

export interface EnrollmentData {
  id: string
  course: {
    id: string
    title: string
    price: number
    instructor: {
      id: string
      first_name: string
      last_name: string
    }
  }
  student: {
    id: string
    first_name: string
    last_name: string
    email: string
  }
  enrolled_at: string
  status: 'active' | 'completed' | 'dropped'
  progress_percentage: number
  completed_at?: string
}

export interface PaymentData {
  id: string
  amount: number
  currency: string
  status: 'pending' | 'completed' | 'failed' | 'refunded'
  payment_method: 'stripe' | 'paypal' | 'bank_transfer'
  course: {
    id: string
    title: string
  }
  created_at: string
  updated_at: string
}

export interface EnrollmentOptions {
  courseId: string
  paymentMethod?: 'stripe' | 'paypal' | 'bank_transfer'
  paymentData?: {
    stripeToken?: string
    paypalOrderId?: string
    bankTransferReference?: string
  }
}

export const useEnrollment = () => {
  const { user, isAuthenticated } = useAuth()
  const { handleApiError } = useErrorHandler()

  // Current enrollment process state
  const currentEnrollment = ref<EnrollmentData | null>(null)
  const enrollmentStep = ref<'course' | 'payment' | 'processing' | 'complete' | 'error'>('course')
  const paymentMethod = ref<'stripe' | 'paypal' | 'bank_transfer'>('stripe')

  // User enrollments
  const { 
    data: enrollments, 
    loading: enrollmentsLoading,
    refresh: refreshEnrollments
  } = useApiData<EnrollmentData[]>('/enrollments/', {
    immediate: isAuthenticated.value,
    transform: (data) => data.results || data,
    ...CachePresets.userProfile
  })

  // User payments
  const { 
    data: payments, 
    loading: paymentsLoading,
    refresh: refreshPayments
  } = useApiData<PaymentData[]>('/payments/', {
    immediate: isAuthenticated.value,
    transform: (data) => data.results || data,
    ...CachePresets.userProfile
  })

  // Enrollment mutation
  const { mutate: enrollMutation, loading: enrolling, error: enrollmentError } = useApiMutation(
    async (options: EnrollmentOptions) => {
      const { courseId, paymentMethod: method, paymentData } = options
      
      // For free courses, direct enrollment
      if (!paymentData) {
        return api.post(`/courses/${courseId}/enroll/`)
      }
      
      // For paid courses, process payment first
      const paymentResponse = await api.post('/payments/', {
        course: courseId,
        payment_method: method,
        ...paymentData
      })
      
      // If payment is successful, enroll
      const paymentResult = paymentResponse.data.data || paymentResponse.data
      if (paymentResult.status === 'completed') {
        return api.post(`/courses/${courseId}/enroll/`, {
          payment_id: paymentResult.id
        })
      }
      
      throw new Error('Payment processing failed')
    },
    {
      onSuccess: (data) => {
        currentEnrollment.value = data.data || data
        enrollmentStep.value = 'complete'
        
        // Refresh user data
        refreshEnrollments()
        refreshPayments()
        
        // Invalidate course cache to update enrollment status
        CacheInvalidation.invalidateCourses()
        CacheInvalidation.invalidateUser(user.value?.id || '')
      },
      onError: (error, variables) => {
        enrollmentStep.value = 'error'
        handleApiError(error, { 
          context: { 
            action: 'course_enrollment', 
            courseId: variables.courseId,
            paymentMethod: variables.paymentMethod
          } 
        })
      }
    }
  )

  // Progress update mutation
  const { mutate: updateProgressMutation, loading: updatingProgress } = useApiMutation(
    ({ enrollmentId, progress }: { enrollmentId: string; progress: number }) =>
      api.patch(`/enrollments/${enrollmentId}/update_progress/`, {
        progress_percentage: progress
      }),
    {
      onSuccess: () => {
        refreshEnrollments()
      },
      onError: (error) => {
        handleApiError(error, { context: { action: 'update_progress' } })
      }
    }
  )

  // Drop course mutation
  const { mutate: dropCourseMutation, loading: droppingCourse } = useApiMutation(
    (enrollmentId: string) => api.post(`/enrollments/${enrollmentId}/drop/`),
    {
      onSuccess: () => {
        refreshEnrollments()
        CacheInvalidation.invalidateCourses()
      },
      onError: (error) => {
        handleApiError(error, { context: { action: 'drop_course' } })
      }
    }
  )

  // Computed properties
  const enrolledCourseIds = computed(() => 
    enrollments.value?.map(enrollment => enrollment.course.id) || []
  )

  const isEnrolledInCourse = computed(() => (courseId: string) => 
    enrolledCourseIds.value.includes(courseId)
  )

  const getEnrollmentForCourse = computed(() => (courseId: string) => 
    enrollments.value?.find(enrollment => enrollment.course.id === courseId)
  )

  const activeEnrollments = computed(() => 
    enrollments.value?.filter(enrollment => enrollment.status === 'active') || []
  )

  const completedEnrollments = computed(() => 
    enrollments.value?.filter(enrollment => enrollment.status === 'completed') || []
  )

  const totalHoursLearned = computed(() => {
    // Calculate from completed enrollments and progress
    return enrollments.value?.reduce((total, enrollment) => {
      // Use a default duration if not available
      const courseHours = (enrollment.course as any).duration_weeks ? 
        (enrollment.course as any).duration_weeks * 5 : 20 // Default 20 hours
      return total + (courseHours * (enrollment.progress_percentage / 100))
    }, 0) || 0
  })

  const completionRate = computed(() => {
    if (!enrollments.value || enrollments.value.length === 0) return 0
    const completed = completedEnrollments.value.length
    const total = enrollments.value.length
    return Math.round((completed / total) * 100)
  })

  // Methods
  const enrollInCourse = async (courseId: string, course?: any) => {
    if (!isAuthenticated.value) {
      throw new Error('Authentication required')
    }

    enrollmentStep.value = 'course'
    
    // Check if course is free
    if (!course?.price || course.price === 0) {
      enrollmentStep.value = 'processing'
      await enrollMutation({ courseId })
      return
    }

    // For paid courses, proceed to payment
    enrollmentStep.value = 'payment'
  }

  const processPayment = async (courseId: string, method: 'stripe' | 'paypal' | 'bank_transfer', paymentData: any) => {
    enrollmentStep.value = 'processing'
    paymentMethod.value = method
    
    await enrollMutation({
      courseId,
      paymentMethod: method,
      paymentData
    })
  }

  const updateProgress = async (enrollmentId: string, progress: number) => {
    await updateProgressMutation({ enrollmentId, progress })
  }

  const dropCourse = async (enrollmentId: string) => {
    await dropCourseMutation(enrollmentId)
  }

  const resetEnrollmentProcess = () => {
    currentEnrollment.value = null
    enrollmentStep.value = 'course'
    paymentMethod.value = 'stripe'
  }

  // Stripe integration helpers using centralized API
  const createStripePayment = async (courseId: string, amount: number) => {
    try {
      const response = await api.post('/payments/', {
        course: courseId,
        amount: Math.round(amount * 100), // Convert to cents
        currency: 'usd',
        payment_method: 'stripe',
        status: 'pending'
      })
      
      return response.data.data || response.data
    } catch (error) {
      handleApiError(error as any, { context: { action: 'create_stripe_payment' } })
      throw error
    }
  }

  const confirmStripePayment = async (paymentIntentId: string, courseId: string) => {
    await processPayment(courseId, 'stripe', {
      stripeToken: paymentIntentId
    })
  }

  // PayPal integration helpers using centralized API
  const createPayPalOrder = async (courseId: string, amount: number) => {
    try {
      const response = await api.post('/payments/', {
        course: courseId,
        amount: amount,
        currency: 'USD',
        payment_method: 'paypal',
        status: 'pending'
      })
      
      return response.data.data || response.data
    } catch (error) {
      handleApiError(error as any, { context: { action: 'create_paypal_order' } })
      throw error
    }
  }

  const confirmPayPalPayment = async (orderId: string, courseId: string) => {
    await processPayment(courseId, 'paypal', {
      paypalOrderId: orderId
    })
  }

  // Bank transfer helpers using centralized API
  const initiateBankTransfer = async (courseId: string, amount: number) => {
    try {
      const response = await api.post('/payments/', {
        course: courseId,
        amount: amount,
        payment_method: 'bank_transfer',
        status: 'pending'
      })
      
      return response.data.data || response.data
    } catch (error) {
      handleApiError(error as any, { context: { action: 'initiate_bank_transfer' } })
      throw error
    }
  }

  const confirmBankTransfer = async (reference: string, courseId: string) => {
    await processPayment(courseId, 'bank_transfer', {
      bankTransferReference: reference
    })
  }

  return {
    // State
    enrollments,
    payments,
    currentEnrollment,
    enrollmentStep,
    paymentMethod,
    
    // Loading states
    enrollmentsLoading,
    paymentsLoading,
    enrolling,
    updatingProgress,
    droppingCourse,
    
    // Errors
    enrollmentError,
    
    // Computed
    enrolledCourseIds,
    isEnrolledInCourse,
    getEnrollmentForCourse,
    activeEnrollments,
    completedEnrollments,
    totalHoursLearned,
    completionRate,
    
    // Methods
    enrollInCourse,
    processPayment,
    updateProgress,
    dropCourse,
    resetEnrollmentProcess,
    refreshEnrollments,
    refreshPayments,
    
    // Payment methods
    createStripePayment,
    confirmStripePayment,
    createPayPalOrder,
    confirmPayPalPayment,
    initiateBankTransfer,
    confirmBankTransfer
  }
}