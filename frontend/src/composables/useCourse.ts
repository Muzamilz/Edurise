import { ref, computed, reactive } from 'vue'
import { CourseService } from '../services/courses'
import type { Course, CourseFilters, Enrollment, CourseModule, CourseReview } from '../types/api'

export const useCourse = () => {
  // State
  const courses = ref<Course[]>([])
  const currentCourse = ref<Course | null>(null)
  const enrollments = ref<Enrollment[]>([])
  const modules = ref<CourseModule[]>([])
  const reviews = ref<CourseReview[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Pagination
  const pagination = reactive({
    count: 0,
    next: null as string | null,
    previous: null as string | null,
    currentPage: 1,
    pageSize: 12
  })

  // Filters
  const filters = reactive<CourseFilters>({
    category: undefined,
    difficulty_level: undefined,
    search: '',
    ordering: '-created_at'
  })

  // Computed
  const hasNextPage = computed(() => !!pagination.next)
  const hasPreviousPage = computed(() => !!pagination.previous)
  const totalPages = computed(() => Math.ceil(pagination.count / pagination.pageSize))

  // Course operations
  const fetchCourses = async (resetPagination = true) => {
    try {
      loading.value = true
      error.value = null

      if (resetPagination) {
        pagination.currentPage = 1
      }

      const response = await CourseService.getCourses(filters)

      courses.value = resetPagination ? response.results : [...courses.value, ...response.results]
      pagination.count = response.count
      pagination.next = response.next
      pagination.previous = response.previous

    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch courses'
      console.error('Error fetching courses:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchMarketplaceCourses = async (resetPagination = true) => {
    try {
      loading.value = true
      error.value = null

      if (resetPagination) {
        pagination.currentPage = 1
      }

      const response = await CourseService.getMarketplaceCourses(filters)

      courses.value = resetPagination ? response.results : [...courses.value, ...response.results]
      pagination.count = response.count
      pagination.next = response.next
      pagination.previous = response.previous

    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch marketplace courses'
      console.error('Error fetching marketplace courses:', err)
    } finally {
      loading.value = false
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
      courses.value.unshift(newCourse)
      
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
      
      // Update in courses list
      const index = courses.value.findIndex(c => c.id === id)
      if (index !== -1) {
        courses.value[index] = updatedCourse
      }
      
      // Update current course if it's the same
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
      
      // Remove from courses list
      courses.value = courses.value.filter(c => c.id !== id)
      
      // Clear current course if it's the same
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
      courses.value.unshift(duplicatedCourse)
      
      return duplicatedCourse

    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to duplicate course'
      console.error('Error duplicating course:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Enrollment operations
  const enrollInCourse = async (courseId: string) => {
    try {
      loading.value = true
      error.value = null

      const enrollment = await CourseService.enrollInCourse(courseId)
      enrollments.value.push(enrollment)
      
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
      loading.value = true
      error.value = null

      const response = await CourseService.getEnrollments()
      enrollments.value = response.results

    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch enrollments'
      console.error('Error fetching enrollments:', err)
    } finally {
      loading.value = false
    }
  }

  const updateProgress = async (enrollmentId: string, progress: number) => {
    try {
      const updatedEnrollment = await CourseService.updateEnrollmentProgress(enrollmentId, progress)
      
      // Update in enrollments list
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

  // Module operations
  const fetchCourseModules = async (courseId: string) => {
    try {
      loading.value = true
      error.value = null

      modules.value = await CourseService.getCourseModules(courseId)

    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch course modules'
      console.error('Error fetching course modules:', err)
    } finally {
      loading.value = false
    }
  }

  const createModule = async (moduleData: Partial<CourseModule>) => {
    try {
      const newModule = await CourseService.createCourseModule(moduleData)
      modules.value.push(newModule)
      
      return newModule

    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create module'
      console.error('Error creating module:', err)
      throw err
    }
  }

  const updateModule = async (id: string, moduleData: Partial<CourseModule>) => {
    try {
      const updatedModule = await CourseService.updateCourseModule(id, moduleData)
      
      const index = modules.value.findIndex(m => m.id === id)
      if (index !== -1) {
        modules.value[index] = updatedModule
      }

      return updatedModule

    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update module'
      console.error('Error updating module:', err)
      throw err
    }
  }

  const deleteModule = async (id: string) => {
    try {
      await CourseService.deleteCourseModule(id)
      modules.value = modules.value.filter(m => m.id !== id)

    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete module'
      console.error('Error deleting module:', err)
      throw err
    }
  }

  // Review operations
  const fetchCourseReviews = async (courseId: string) => {
    try {
      reviews.value = await CourseService.getCourseReviews(courseId)

    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch reviews'
      console.error('Error fetching reviews:', err)
    }
  }

  const createReview = async (reviewData: Partial<CourseReview>) => {
    try {
      const newReview = await CourseService.createCourseReview(reviewData)
      reviews.value.push(newReview)
      
      return newReview

    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create review'
      console.error('Error creating review:', err)
      throw err
    }
  }

  // Pagination
  const nextPage = async () => {
    if (hasNextPage.value) {
      pagination.currentPage++
      await fetchCourses(false)
    }
  }

  const previousPage = async () => {
    if (hasPreviousPage.value) {
      pagination.currentPage--
      await fetchCourses(false)
    }
  }

  const goToPage = async (page: number) => {
    pagination.currentPage = page
    await fetchCourses()
  }

  // Filters
  const updateFilters = (newFilters: Partial<CourseFilters>) => {
    Object.assign(filters, newFilters)
  }

  const clearFilters = () => {
    Object.assign(filters, {
      category: undefined,
      difficulty_level: undefined,
      search: '',
      ordering: '-created_at'
    })
  }

  const searchCourses = async (query: string) => {
    filters.search = query
    await fetchCourses()
  }

  // Reset state
  const reset = () => {
    courses.value = []
    currentCourse.value = null
    enrollments.value = []
    modules.value = []
    reviews.value = []
    error.value = null
    pagination.currentPage = 1
    pagination.count = 0
    pagination.next = null
    pagination.previous = null
  }

  return {
    // State
    courses,
    currentCourse,
    enrollments,
    modules,
    reviews,
    loading,
    error,
    pagination,
    filters,

    // Computed
    hasNextPage,
    hasPreviousPage,
    totalPages,

    // Course operations
    fetchCourses,
    fetchMarketplaceCourses,
    fetchCourse,
    createCourse,
    updateCourse,
    deleteCourse,
    duplicateCourse,

    // Enrollment operations
    enrollInCourse,
    fetchEnrollments,
    updateProgress,

    // Module operations
    fetchCourseModules,
    createModule,
    updateModule,
    deleteModule,

    // Review operations
    fetchCourseReviews,
    createReview,

    // Pagination
    nextPage,
    previousPage,
    goToPage,

    // Filters
    updateFilters,
    clearFilters,
    searchCourses,

    // Utility
    reset
  }
}