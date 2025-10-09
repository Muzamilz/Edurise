import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { CourseService } from '../services/courses'
import type { Course, Enrollment, CourseFilters } from '../types/api'

export const useCourseStore = defineStore('courses', () => {
  // State
  const courses = ref<Course[]>([])
  const enrolledCourses = ref<Course[]>([])
  const myCourses = ref<Course[]>([])
  const featuredCourses = ref<Course[]>([])
  const currentCourse = ref<Course | null>(null)
  const enrollments = ref<Enrollment[]>([])
  const categories = ref<Array<{ category: string; count: number; avg_rating: number }>>([])
  
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Dashboard data
  const dashboardData = ref<any>(null)
  const instructorAnalytics = ref<any>(null)

  // Computed
  const coursesByCategory = computed(() => {
    const grouped: Record<string, Course[]> = {}
    courses.value.forEach(course => {
      if (!grouped[course.category]) {
        grouped[course.category] = []
      }
      grouped[course.category].push(course)
    })
    return grouped
  })

  const enrolledCourseIds = computed(() => 
    enrollments.value.map(enrollment => enrollment.course.id)
  )

  const isEnrolledInCourse = computed(() => (courseId: string) => 
    enrolledCourseIds.value.includes(courseId)
  )

  const completedCoursesCount = computed(() => 
    enrollments.value.filter(e => e.status === 'completed').length
  )

  const activeCoursesCount = computed(() => 
    enrollments.value.filter(e => e.status === 'active').length
  )

  const averageProgress = computed(() => {
    if (enrollments.value.length === 0) return 0
    const totalProgress = enrollments.value.reduce((sum, e) => sum + e.progress_percentage, 0)
    return Math.round(totalProgress / enrollments.value.length)
  })

  // Actions
  const fetchCourses = async (filters?: CourseFilters) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await CourseService.getCourses(filters)
      courses.value = response.results
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch courses'
      console.error('Error fetching courses:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchMarketplaceCourses = async (filters?: CourseFilters) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await CourseService.getMarketplaceCourses(filters)
      courses.value = response.results
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch marketplace courses'
      console.error('Error fetching marketplace courses:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchFeaturedCourses = async () => {
    try {
      featuredCourses.value = await CourseService.getFeaturedCourses()
    } catch (err: any) {
      console.error('Error fetching featured courses:', err)
    }
  }

  const fetchMyCourses = async () => {
    try {
      loading.value = true
      const response = await CourseService.getMyCourses()
      myCourses.value = response.results
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch my courses'
      console.error('Error fetching my courses:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchEnrolledCourses = async () => {
    try {
      enrolledCourses.value = await CourseService.getEnrolledCourses()
    } catch (err: any) {
      console.error('Error fetching enrolled courses:', err)
    }
  }

  const fetchCourse = async (id: string) => {
    try {
      loading.value = true
      error.value = null
      
      currentCourse.value = await CourseService.getCourse(id)
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch course'
      console.error('Error fetching course:', err)
    } finally {
      loading.value = false
    }
  }

  const createCourse = async (courseData: Partial<Course>) => {
    try {
      loading.value = true
      error.value = null
      
      const newCourse = await CourseService.createCourse(courseData)
      myCourses.value.unshift(newCourse)
      
      return newCourse
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create course'
      console.error('Error creating course:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateCourse = async (id: string, courseData: Partial<Course>) => {
    try {
      loading.value = true
      error.value = null
      
      const updatedCourse = await CourseService.updateCourse(id, courseData)
      
      // Update in various arrays
      const updateInArray = (array: Course[]) => {
        const index = array.findIndex(c => c.id === id)
        if (index !== -1) {
          array[index] = updatedCourse
        }
      }
      
      updateInArray(courses.value)
      updateInArray(myCourses.value)
      updateInArray(enrolledCourses.value)
      updateInArray(featuredCourses.value)
      
      if (currentCourse.value?.id === id) {
        currentCourse.value = updatedCourse
      }
      
      return updatedCourse
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update course'
      console.error('Error updating course:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteCourse = async (id: string) => {
    try {
      loading.value = true
      error.value = null
      
      await CourseService.deleteCourse(id)
      
      // Remove from various arrays
      const removeFromArray = (array: Course[]) => {
        const index = array.findIndex(c => c.id === id)
        if (index !== -1) {
          array.splice(index, 1)
        }
      }
      
      removeFromArray(courses.value)
      removeFromArray(myCourses.value)
      removeFromArray(enrolledCourses.value)
      removeFromArray(featuredCourses.value)
      
      if (currentCourse.value?.id === id) {
        currentCourse.value = null
      }
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete course'
      console.error('Error deleting course:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const duplicateCourse = async (id: string) => {
    try {
      loading.value = true
      error.value = null
      
      const duplicatedCourse = await CourseService.duplicateCourse(id)
      myCourses.value.unshift(duplicatedCourse)
      
      return duplicatedCourse
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to duplicate course'
      console.error('Error duplicating course:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const enrollInCourse = async (courseId: string) => {
    try {
      loading.value = true
      error.value = null
      
      const enrollment = await CourseService.enrollInCourse(courseId)
      enrollments.value.push(enrollment)
      
      // Add course to enrolled courses if not already there
      const course = courses.value.find(c => c.id === courseId) || currentCourse.value
      if (course && !enrolledCourses.value.find(c => c.id === courseId)) {
        enrolledCourses.value.push(course)
      }
      
      return enrollment
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to enroll in course'
      console.error('Error enrolling in course:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchEnrollments = async () => {
    try {
      const response = await CourseService.getEnrollments()
      enrollments.value = response.results
    } catch (err: any) {
      console.error('Error fetching enrollments:', err)
    }
  }

  const updateEnrollmentProgress = async (enrollmentId: string, progress: number) => {
    try {
      const updatedEnrollment = await CourseService.updateEnrollmentProgress(enrollmentId, progress)
      
      const index = enrollments.value.findIndex(e => e.id === enrollmentId)
      if (index !== -1) {
        enrollments.value[index] = updatedEnrollment
      }
      
      return updatedEnrollment
      
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update progress'
      console.error('Error updating progress:', err)
      throw err
    }
  }

  const fetchCategories = async () => {
    try {
      categories.value = await CourseService.getCourseCategories()
    } catch (err: any) {
      console.error('Error fetching categories:', err)
    }
  }

  const fetchStudentDashboard = async () => {
    try {
      dashboardData.value = await CourseService.getStudentDashboard()
    } catch (err: any) {
      console.error('Error fetching student dashboard:', err)
    }
  }

  const fetchInstructorAnalytics = async () => {
    try {
      instructorAnalytics.value = await CourseService.getInstructorAnalytics()
    } catch (err: any) {
      console.error('Error fetching instructor analytics:', err)
    }
  }

  const searchCourses = async (query: string, filters?: CourseFilters) => {
    const searchFilters = { ...filters, search: query }
    await fetchCourses(searchFilters)
  }

  // Clear state
  const clearCurrentCourse = () => {
    currentCourse.value = null
  }

  const clearError = () => {
    error.value = null
  }

  const reset = () => {
    courses.value = []
    enrolledCourses.value = []
    myCourses.value = []
    featuredCourses.value = []
    currentCourse.value = null
    enrollments.value = []
    categories.value = []
    dashboardData.value = null
    instructorAnalytics.value = null
    loading.value = false
    error.value = null
  }

  return {
    // State
    courses,
    enrolledCourses,
    myCourses,
    featuredCourses,
    currentCourse,
    enrollments,
    categories,
    dashboardData,
    instructorAnalytics,
    loading,
    error,

    // Computed
    coursesByCategory,
    enrolledCourseIds,
    isEnrolledInCourse,
    completedCoursesCount,
    activeCoursesCount,
    averageProgress,

    // Actions
    fetchCourses,
    fetchMarketplaceCourses,
    fetchFeaturedCourses,
    fetchMyCourses,
    fetchEnrolledCourses,
    fetchCourse,
    createCourse,
    updateCourse,
    deleteCourse,
    duplicateCourse,
    enrollInCourse,
    fetchEnrollments,
    updateEnrollmentProgress,
    fetchCategories,
    fetchStudentDashboard,
    fetchInstructorAnalytics,
    searchCourses,

    // Utility
    clearCurrentCourse,
    clearError,
    reset
  }
})