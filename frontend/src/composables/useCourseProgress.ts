import { computed } from 'vue'
import { useApiData, useApiMutation } from './useApiData'
import { useErrorHandler } from './useErrorHandler'
import { useAuth } from './useAuth'
import { api } from '@/services/api'
import { CachePresets, CacheInvalidation } from '@/utils/apiCache'

export interface CourseProgress {
  id: string
  enrollment: {
    id: string
    course: {
      id: string
      title: string
      total_modules: number
    }
    student: {
      id: string
      first_name: string
      last_name: string
    }
  }
  progress_percentage: number
  completed_modules: number
  total_time_spent: number // in minutes
  last_accessed: string
  completion_date?: string
  status: 'active' | 'completed' | 'paused'
  module_progress: ModuleProgress[]
}

export interface ModuleProgress {
  id: string
  module: {
    id: string
    title: string
    order: number
    estimated_duration: number
  }
  is_completed: boolean
  completion_date?: string
  time_spent: number // in minutes
  progress_percentage: number
  last_accessed?: string
}

export interface ProgressUpdate {
  enrollmentId: string
  moduleId?: string
  progressPercentage: number
  timeSpent?: number
  isCompleted?: boolean
}

export const useCourseProgress = (courseId?: string) => {
  const { user, isAuthenticated } = useAuth()
  const { handleApiError } = useErrorHandler()

  // Course progress data from centralized API
  const { 
    data: courseProgress, 
    loading: progressLoading,
    refresh: refreshProgress
  } = useApiData<CourseProgress>(() => `/enrollments/${courseId}/progress_detail/`, {
    immediate: isAuthenticated.value && !!courseId,
    transform: (data) => data.data || data,
    ...CachePresets.userProfile
  })

  // All user progress data from centralized API
  const { 
    data: allProgress, 
    loading: allProgressLoading,
    refresh: refreshAllProgress
  } = useApiData<CourseProgress[]>('/enrollments/', {
    immediate: isAuthenticated.value,
    transform: (data) => {
      const progressData = data.data || data
      return progressData.results || progressData || []
    },
    ...CachePresets.userProfile
  })

  // Progress update mutation
  const { mutate: updateProgressMutation, loading: updatingProgress } = useApiMutation(
    (update: ProgressUpdate) => {
      const { enrollmentId, moduleId, progressPercentage, timeSpent, isCompleted } = update
      
      if (moduleId) {
        // Update module progress - using centralized course-modules endpoint
        return api.patch(`/course-modules/${moduleId}/`, {
          progress_percentage: progressPercentage,
          time_spent: timeSpent,
          is_completed: isCompleted
        })
      } else {
        // Update overall course progress using centralized enrollments endpoint
        return api.patch(`/enrollments/${enrollmentId}/`, {
          progress_percentage: progressPercentage,
          total_time_spent: timeSpent
        })
      }
    },
    {
      onSuccess: () => {
        refreshProgress()
        refreshAllProgress()
        CacheInvalidation.invalidateUser(user.value?.id || '')
      },
      onError: (error) => {
        handleApiError(error, { context: { action: 'update_progress' } })
      }
    }
  )

  // Mark module as completed mutation
  const { mutate: completeModuleMutation, loading: completingModule } = useApiMutation(
    ({ moduleId, timeSpent }: { enrollmentId: string; moduleId: string; timeSpent?: number }) =>
      api.patch(`/course-modules/${moduleId}/`, {
        is_completed: true,
        time_spent: timeSpent
      }),
    {
      onSuccess: () => {
        refreshProgress()
        refreshAllProgress()
        CacheInvalidation.invalidateUser(user.value?.id || '')
      },
      onError: (error) => {
        handleApiError(error, { context: { action: 'complete_module' } })
      }
    }
  )

  // Mark course as completed mutation using centralized API
  const { mutate: completeCourseMutation, loading: completingCourse } = useApiMutation(
    (enrollmentId: string) => api.patch(`/enrollments/${enrollmentId}/`, {
      progress_percentage: 100,
      status: 'completed',
      completed_at: new Date().toISOString()
    }),
    {
      onSuccess: () => {
        refreshProgress()
        refreshAllProgress()
        CacheInvalidation.invalidateUser(user.value?.id || '')
        CacheInvalidation.invalidateCourses()
      },
      onError: (error) => {
        handleApiError(error, { context: { action: 'complete_course' } })
      }
    }
  )

  // Resume course mutation
  const { mutate: resumeCourseMutation, loading: resumingCourse } = useApiMutation(
    (enrollmentId: string) => api.patch(`/enrollments/${enrollmentId}/`, {
      status: 'active'
    }),
    {
      onSuccess: () => {
        refreshProgress()
        refreshAllProgress()
      },
      onError: (error) => {
        handleApiError(error, { context: { action: 'resume_course' } })
      }
    }
  )

  // Computed properties
  const progressPercentage = computed(() => 
    courseProgress.value?.progress_percentage || 0
  )

  const completedModules = computed(() => 
    courseProgress.value?.completed_modules || 0
  )

  const totalModules = computed(() => 
    courseProgress.value?.enrollment.course.total_modules || 0
  )

  const timeSpent = computed(() => 
    courseProgress.value?.total_time_spent || 0
  )

  const isCompleted = computed(() => 
    courseProgress.value?.status === 'completed'
  )

  const isPaused = computed(() => 
    courseProgress.value?.status === 'paused'
  )

  const nextModule = computed(() => {
    if (!courseProgress.value?.module_progress) return null
    
    return courseProgress.value.module_progress
      .filter(mp => !mp.is_completed)
      .sort((a, b) => a.module.order - b.module.order)[0]
  })

  const currentModule = computed(() => {
    if (!courseProgress.value?.module_progress) return null
    
    // Find the module that was last accessed
    const lastAccessed = courseProgress.value.module_progress
      .filter(mp => mp.last_accessed)
      .sort((a, b) => new Date(b.last_accessed!).getTime() - new Date(a.last_accessed!).getTime())[0]
    
    return lastAccessed || nextModule.value
  })

  const estimatedTimeRemaining = computed(() => {
    if (!courseProgress.value?.module_progress) return 0
    
    return courseProgress.value.module_progress
      .filter(mp => !mp.is_completed)
      .reduce((total, mp) => total + mp.module.estimated_duration, 0)
  })

  const averageTimePerModule = computed(() => {
    if (!courseProgress.value?.module_progress || completedModules.value === 0) return 0
    
    const completedModuleProgress = courseProgress.value.module_progress
      .filter(mp => mp.is_completed)
    
    const totalTime = completedModuleProgress
      .reduce((total, mp) => total + mp.time_spent, 0)
    
    return totalTime / completedModuleProgress.length
  })

  const progressStats = computed(() => {
    if (!allProgress.value) return null
    
    const active = allProgress.value.filter(p => p.status === 'active')
    const completed = allProgress.value.filter(p => p.status === 'completed')
    const paused = allProgress.value.filter(p => p.status === 'paused')
    
    const totalTimeSpent = allProgress.value.reduce((total, p) => total + p.total_time_spent, 0)
    const averageProgress = allProgress.value.length > 0 
      ? allProgress.value.reduce((total, p) => total + p.progress_percentage, 0) / allProgress.value.length
      : 0
    
    return {
      totalCourses: allProgress.value.length,
      activeCourses: active.length,
      completedCourses: completed.length,
      pausedCourses: paused.length,
      totalTimeSpent,
      averageProgress: Math.round(averageProgress),
      completionRate: allProgress.value.length > 0 
        ? Math.round((completed.length / allProgress.value.length) * 100)
        : 0
    }
  })

  // Methods
  const updateProgress = async (update: ProgressUpdate) => {
    await updateProgressMutation(update)
  }

  const updateModuleProgress = async (
    enrollmentId: string, 
    moduleId: string, 
    progressPercentage: number, 
    timeSpent?: number
  ) => {
    await updateProgressMutation({
      enrollmentId,
      moduleId,
      progressPercentage,
      timeSpent
    })
  }

  const completeModule = async (enrollmentId: string, moduleId: string, timeSpent?: number) => {
    await completeModuleMutation({ enrollmentId, moduleId, timeSpent })
  }

  const completeCourse = async (enrollmentId: string) => {
    await completeCourseMutation(enrollmentId)
  }

  const resumeCourse = async (enrollmentId: string) => {
    await resumeCourseMutation(enrollmentId)
  }

  const pauseCourse = async (enrollmentId: string) => {
    // Pause is handled by updating status
    await api.patch(`/enrollments/${enrollmentId}/`, { status: 'paused' })
    await refreshProgress()
    await refreshAllProgress()
  }

  // Time tracking helpers
  const startTimeTracking = () => {
    const startTime = Date.now()
    
    return {
      getElapsedTime: () => Math.floor((Date.now() - startTime) / 1000 / 60), // in minutes
      stop: () => Math.floor((Date.now() - startTime) / 1000 / 60)
    }
  }

  const formatTime = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes}m`
    }
    
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    
    if (hours < 24) {
      return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`
    }
    
    const days = Math.floor(hours / 24)
    const remainingHours = hours % 24
    
    return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`
  }

  const calculateProgress = (completedItems: number, totalItems: number) => {
    if (totalItems === 0) return 0
    return Math.round((completedItems / totalItems) * 100)
  }

  return {
    // State
    courseProgress,
    allProgress,
    
    // Loading states
    progressLoading,
    allProgressLoading,
    updatingProgress,
    completingModule,
    completingCourse,
    resumingCourse,
    
    // Computed
    progressPercentage,
    completedModules,
    totalModules,
    timeSpent,
    isCompleted,
    isPaused,
    nextModule,
    currentModule,
    estimatedTimeRemaining,
    averageTimePerModule,
    progressStats,
    
    // Methods
    updateProgress,
    updateModuleProgress,
    completeModule,
    completeCourse,
    resumeCourse,
    pauseCourse,
    refreshProgress,
    refreshAllProgress,
    
    // Utilities
    startTimeTracking,
    formatTime,
    calculateProgress
  }
}