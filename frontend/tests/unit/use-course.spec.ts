import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useCourse } from '../../src/composables/useCourse'
import { CourseService } from '../../src/services/courses'

// Mock the CourseService
vi.mock('../../src/services/courses', () => ({
  CourseService: {
    getCourses: vi.fn(),
    getCourse: vi.fn(),
    createCourse: vi.fn(),
    updateCourse: vi.fn(),
    deleteCourse: vi.fn(),
    enrollInCourse: vi.fn(),
    getEnrollments: vi.fn(),
    updateEnrollmentProgress: vi.fn(),
    getCourseModules: vi.fn(),
    createCourseModule: vi.fn(),
    updateCourseModule: vi.fn(),
    deleteCourseModule: vi.fn(),
    getCourseReviews: vi.fn(),
    createCourseReview: vi.fn()
  }
}))

describe('useCourse', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with default state', () => {
    const {
      courses,
      currentCourse,
      enrollments,
      modules,
      reviews,
      loading,
      error,
      pagination
    } = useCourse()

    expect(courses.value).toEqual([])
    expect(currentCourse.value).toBeNull()
    expect(enrollments.value).toEqual([])
    expect(modules.value).toEqual([])
    expect(reviews.value).toEqual([])
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
    expect(pagination.currentPage).toBe(1)
    expect(pagination.pageSize).toBe(12)
  })

  describe('fetchCourses', () => {
    it('should fetch courses successfully', async () => {
      const mockResponse = {
        count: 2,
        next: null,
        previous: null,
        results: [
          { id: '1', title: 'Course 1' },
          { id: '2', title: 'Course 2' }
        ]
      }

      vi.mocked(CourseService.getCourses).mockResolvedValue(mockResponse)

      const { courses, loading, error, fetchCourses } = useCourse()

      await fetchCourses()

      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
      expect(courses.value).toEqual(mockResponse.results)
    })

    it('should handle fetch courses error', async () => {
      const mockError = {
        response: {
          data: { message: 'Failed to fetch courses' }
        }
      }

      vi.mocked(CourseService.getCourses).mockRejectedValue(mockError)

      const { courses, loading, error, fetchCourses } = useCourse()

      await fetchCourses()

      expect(loading.value).toBe(false)
      expect(error.value).toBe('Failed to fetch courses')
      expect(courses.value).toEqual([])
    })

    it('should set loading state during fetch', async () => {
      let resolvePromise: (value: any) => void
      const promise = new Promise(resolve => {
        resolvePromise = resolve
      })

      vi.mocked(CourseService.getCourses).mockReturnValue(promise)

      const { loading, fetchCourses } = useCourse()

      const fetchPromise = fetchCourses()
      
      expect(loading.value).toBe(true)

      resolvePromise!({
        count: 0,
        next: null,
        previous: null,
        results: []
      })

      await fetchPromise

      expect(loading.value).toBe(false)
    })
  })

  describe('fetchCourse', () => {
    it('should fetch single course successfully', async () => {
      const mockCourse = { id: '1', title: 'Test Course' }
      vi.mocked(CourseService.getCourse).mockResolvedValue(mockCourse)

      const { currentCourse, fetchCourse } = useCourse()

      await fetchCourse('1')

      expect(currentCourse.value).toEqual(mockCourse)
    })
  })

  describe('createCourse', () => {
    it('should create course successfully', async () => {
      const courseData = { title: 'New Course', description: 'Description' }
      const mockCreatedCourse = { id: '1', ...courseData }

      vi.mocked(CourseService.createCourse).mockResolvedValue(mockCreatedCourse)

      const { courses, createCourse } = useCourse()

      const result = await createCourse(courseData)

      expect(result).toEqual(mockCreatedCourse)
      expect(courses.value[0]).toEqual(mockCreatedCourse)
    })

    it('should handle create course error', async () => {
      const courseData = { title: 'New Course' }
      const mockError = {
        response: {
          data: { message: 'Failed to create course' }
        }
      }

      vi.mocked(CourseService.createCourse).mockRejectedValue(mockError)

      const { error, createCourse } = useCourse()

      await expect(createCourse(courseData)).rejects.toEqual(mockError)
      expect(error.value).toBe('Failed to create course')
    })
  })

  describe('updateCourse', () => {
    it('should update course successfully', async () => {
      const courseData = { title: 'Updated Course' }
      const mockUpdatedCourse = { id: '1', ...courseData }

      vi.mocked(CourseService.updateCourse).mockResolvedValue(mockUpdatedCourse)

      const { courses, currentCourse, updateCourse } = useCourse()

      // Set initial state
      courses.value = [{ id: '1', title: 'Original Course' }]
      currentCourse.value = { id: '1', title: 'Original Course' }

      const result = await updateCourse('1', courseData)

      expect(result).toEqual(mockUpdatedCourse)
      expect(courses.value[0]).toEqual(mockUpdatedCourse)
      expect(currentCourse.value).toEqual(mockUpdatedCourse)
    })
  })

  describe('deleteCourse', () => {
    it('should delete course successfully', async () => {
      vi.mocked(CourseService.deleteCourse).mockResolvedValue(undefined)

      const { courses, currentCourse, deleteCourse } = useCourse()

      // Set initial state
      courses.value = [
        { id: '1', title: 'Course 1' },
        { id: '2', title: 'Course 2' }
      ]
      currentCourse.value = { id: '1', title: 'Course 1' }

      await deleteCourse('1')

      expect(courses.value).toHaveLength(1)
      expect(courses.value[0].id).toBe('2')
      expect(currentCourse.value).toBeNull()
    })
  })

  describe('enrollInCourse', () => {
    it('should enroll in course successfully', async () => {
      const mockEnrollment = {
        id: '1',
        student: 'student-id',
        course: 'course-id',
        status: 'active'
      }

      vi.mocked(CourseService.enrollInCourse).mockResolvedValue(mockEnrollment)

      const { enrollments, enrollInCourse } = useCourse()

      const result = await enrollInCourse('course-id')

      expect(result).toEqual(mockEnrollment)
      expect(enrollments.value[0]).toEqual(mockEnrollment)
    })
  })

  describe('updateProgress', () => {
    it('should update enrollment progress successfully', async () => {
      const mockUpdatedEnrollment = {
        id: '1',
        student: 'student-id',
        course: 'course-id',
        status: 'active',
        progress_percentage: 75
      }

      vi.mocked(CourseService.updateEnrollmentProgress).mockResolvedValue(mockUpdatedEnrollment)

      const { enrollments, updateProgress } = useCourse()

      // Set initial state
      enrollments.value = [{
        id: '1',
        student: 'student-id',
        course: 'course-id',
        status: 'active',
        progress_percentage: 50
      }]

      const result = await updateProgress('1', 75)

      expect(result).toEqual(mockUpdatedEnrollment)
      expect(enrollments.value[0].progress_percentage).toBe(75)
    })
  })

  describe('pagination', () => {
    it('should handle pagination correctly', () => {
      const { pagination, hasNextPage, hasPreviousPage, totalPages } = useCourse()

      // Set pagination data
      pagination.count = 100
      pagination.pageSize = 12
      pagination.currentPage = 5
      pagination.next = 'next-url'
      pagination.previous = 'prev-url'

      expect(hasNextPage.value).toBe(true)
      expect(hasPreviousPage.value).toBe(true)
      expect(totalPages.value).toBe(9) // Math.ceil(100 / 12)
    })

    it('should handle first page correctly', () => {
      const { pagination, hasNextPage, hasPreviousPage } = useCourse()

      pagination.currentPage = 1
      pagination.next = 'next-url'
      pagination.previous = null

      expect(hasNextPage.value).toBe(true)
      expect(hasPreviousPage.value).toBe(false)
    })

    it('should handle last page correctly', () => {
      const { pagination, hasNextPage, hasPreviousPage } = useCourse()

      pagination.currentPage = 5
      pagination.next = null
      pagination.previous = 'prev-url'

      expect(hasNextPage.value).toBe(false)
      expect(hasPreviousPage.value).toBe(true)
    })
  })

  describe('filters', () => {
    it('should update filters correctly', () => {
      const { filters, updateFilters } = useCourse()

      const newFilters = {
        category: 'technology',
        difficulty_level: 'beginner',
        search: 'javascript'
      }

      updateFilters(newFilters)

      expect(filters.category).toBe('technology')
      expect(filters.difficulty_level).toBe('beginner')
      expect(filters.search).toBe('javascript')
    })

    it('should clear filters correctly', () => {
      const { filters, updateFilters, clearFilters } = useCourse()

      // Set some filters
      updateFilters({
        category: 'technology',
        difficulty_level: 'beginner',
        search: 'javascript'
      })

      // Clear filters
      clearFilters()

      expect(filters.category).toBeUndefined()
      expect(filters.difficulty_level).toBeUndefined()
      expect(filters.search).toBe('')
      expect(filters.ordering).toBe('-created_at')
    })
  })

  describe('reset', () => {
    it('should reset all state to initial values', () => {
      const {
        courses,
        currentCourse,
        enrollments,
        modules,
        reviews,
        error,
        pagination,
        reset
      } = useCourse()

      // Set some state
      courses.value = [{ id: '1', title: 'Course' }]
      currentCourse.value = { id: '1', title: 'Course' }
      enrollments.value = [{ id: '1', student: 'student', course: 'course' }]
      modules.value = [{ id: '1', title: 'Module' }]
      reviews.value = [{ id: '1', rating: 5 }]
      error.value = 'Some error'
      pagination.currentPage = 5
      pagination.count = 100

      // Reset
      reset()

      expect(courses.value).toEqual([])
      expect(currentCourse.value).toBeNull()
      expect(enrollments.value).toEqual([])
      expect(modules.value).toEqual([])
      expect(reviews.value).toEqual([])
      expect(error.value).toBeNull()
      expect(pagination.currentPage).toBe(1)
      expect(pagination.count).toBe(0)
    })
  })
})