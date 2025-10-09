import { describe, it, expect, vi, beforeEach } from 'vitest'
import { CourseService } from '../../src/services/courses'
import { api } from '../../src/services/api'

// Mock the API
vi.mock('../../src/services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  }
}))

describe('CourseService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getCourses', () => {
    it('should fetch courses with filters', async () => {
      const mockResponse = {
        data: {
          count: 2,
          next: null,
          previous: null,
          results: [
            {
              id: '1',
              title: 'Test Course 1',
              description: 'Test Description 1',
              category: 'technology',
              difficulty_level: 'beginner'
            },
            {
              id: '2',
              title: 'Test Course 2',
              description: 'Test Description 2',
              category: 'business',
              difficulty_level: 'intermediate'
            }
          ]
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const filters = { category: 'technology', search: 'test' }
      const result = await CourseService.getCourses(filters)

      expect(api.get).toHaveBeenCalledWith('/courses/courses/', { params: filters })
      expect(result).toEqual(mockResponse.data)
    })

    it('should fetch courses without filters', async () => {
      const mockResponse = {
        data: {
          count: 1,
          next: null,
          previous: null,
          results: [
            {
              id: '1',
              title: 'Test Course',
              description: 'Test Description',
              category: 'technology',
              difficulty_level: 'beginner'
            }
          ]
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await CourseService.getCourses()

      expect(api.get).toHaveBeenCalledWith('/courses/courses/', { params: undefined })
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('getCourse', () => {
    it('should fetch a single course by id', async () => {
      const mockCourse = {
        id: '1',
        title: 'Test Course',
        description: 'Test Description',
        category: 'technology',
        difficulty_level: 'beginner'
      }

      const mockResponse = { data: mockCourse }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await CourseService.getCourse('1')

      expect(api.get).toHaveBeenCalledWith('/courses/courses/1/')
      expect(result).toEqual(mockCourse)
    })
  })

  describe('createCourse', () => {
    it('should create a new course', async () => {
      const courseData = {
        title: 'New Course',
        description: 'New Description',
        category: 'technology',
        difficulty_level: 'beginner' as const
      }

      const mockResponse = { data: { id: '1', ...courseData } }
      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await CourseService.createCourse(courseData)

      expect(api.post).toHaveBeenCalledWith('/courses/courses/', courseData)
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('updateCourse', () => {
    it('should update an existing course', async () => {
      const courseData = {
        title: 'Updated Course',
        description: 'Updated Description'
      }

      const mockResponse = { data: { id: '1', ...courseData } }
      vi.mocked(api.patch).mockResolvedValue(mockResponse)

      const result = await CourseService.updateCourse('1', courseData)

      expect(api.patch).toHaveBeenCalledWith('/courses/courses/1/', courseData)
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('deleteCourse', () => {
    it('should delete a course', async () => {
      vi.mocked(api.delete).mockResolvedValue({ data: null })

      await CourseService.deleteCourse('1')

      expect(api.delete).toHaveBeenCalledWith('/courses/courses/1/')
    })
  })

  describe('enrollInCourse', () => {
    it('should enroll in a course', async () => {
      const mockEnrollment = {
        id: '1',
        student: 'student-id',
        course: 'course-id',
        status: 'active',
        progress_percentage: 0
      }

      const mockResponse = { data: mockEnrollment }
      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await CourseService.enrollInCourse('course-id')

      expect(api.post).toHaveBeenCalledWith('/courses/courses/course-id/enroll/')
      expect(result).toEqual(mockEnrollment)
    })
  })

  describe('updateEnrollmentProgress', () => {
    it('should update enrollment progress', async () => {
      const mockEnrollment = {
        id: '1',
        student: 'student-id',
        course: 'course-id',
        status: 'active',
        progress_percentage: 75
      }

      const mockResponse = { data: mockEnrollment }
      vi.mocked(api.patch).mockResolvedValue(mockResponse)

      const result = await CourseService.updateEnrollmentProgress('1', 75)

      expect(api.patch).toHaveBeenCalledWith('/courses/enrollments/1/update_progress/', {
        progress_percentage: 75
      })
      expect(result).toEqual(mockEnrollment)
    })
  })

  describe('getMarketplaceCourses', () => {
    it('should fetch marketplace courses', async () => {
      const mockResponse = {
        data: {
          count: 1,
          next: null,
          previous: null,
          results: [
            {
              id: '1',
              title: 'Marketplace Course',
              description: 'Public course',
              is_public: true
            }
          ]
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await CourseService.getMarketplaceCourses()

      expect(api.get).toHaveBeenCalledWith('/courses/courses/marketplace/', { params: undefined })
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('getFeaturedCourses', () => {
    it('should fetch featured courses', async () => {
      const mockCourses = [
        {
          id: '1',
          title: 'Featured Course 1',
          average_rating: 4.8
        },
        {
          id: '2',
          title: 'Featured Course 2',
          average_rating: 4.9
        }
      ]

      const mockResponse = { data: mockCourses }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await CourseService.getFeaturedCourses()

      expect(api.get).toHaveBeenCalledWith('/courses/courses/featured/')
      expect(result).toEqual(mockCourses)
    })
  })

  describe('getCourseCategories', () => {
    it('should fetch course categories with counts', async () => {
      const mockCategories = [
        { category: 'technology', count: 15, avg_rating: 4.5 },
        { category: 'business', count: 8, avg_rating: 4.2 }
      ]

      const mockResponse = { data: mockCategories }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await CourseService.getCourseCategories()

      expect(api.get).toHaveBeenCalledWith('/courses/courses/categories/')
      expect(result).toEqual(mockCategories)
    })
  })

  describe('duplicateCourse', () => {
    it('should duplicate a course', async () => {
      const mockDuplicatedCourse = {
        id: '2',
        title: 'Original Course (Copy)',
        description: 'Duplicated course'
      }

      const mockResponse = { data: mockDuplicatedCourse }
      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await CourseService.duplicateCourse('1')

      expect(api.post).toHaveBeenCalledWith('/courses/courses/1/duplicate/')
      expect(result).toEqual(mockDuplicatedCourse)
    })
  })

  describe('getCourseStatistics', () => {
    it('should fetch course statistics', async () => {
      const mockStats = {
        total_enrollments: 25,
        active_enrollments: 20,
        completed_enrollments: 5,
        completion_rate: 20.0,
        average_rating: 4.5
      }

      const mockResponse = { data: mockStats }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await CourseService.getCourseStatistics('1')

      expect(api.get).toHaveBeenCalledWith('/courses/courses/1/statistics/')
      expect(result).toEqual(mockStats)
    })
  })

  describe('createCourseReview', () => {
    it('should create a course review', async () => {
      const reviewData = {
        course: 'course-id',
        rating: 5,
        comment: 'Excellent course!'
      }

      const mockReview = {
        id: '1',
        ...reviewData,
        student: 'student-id',
        is_approved: false
      }

      const mockResponse = { data: mockReview }
      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await CourseService.createCourseReview(reviewData)

      expect(api.post).toHaveBeenCalledWith('/courses/reviews/', reviewData)
      expect(result).toEqual(mockReview)
    })
  })

  describe('error handling', () => {
    it('should handle API errors gracefully', async () => {
      const mockError = new Error('Network error')
      vi.mocked(api.get).mockRejectedValue(mockError)

      await expect(CourseService.getCourses()).rejects.toThrow('Network error')
    })

    it('should handle 404 errors for course not found', async () => {
      const mockError = {
        response: {
          status: 404,
          data: { message: 'Course not found' }
        }
      }
      vi.mocked(api.get).mockRejectedValue(mockError)

      await expect(CourseService.getCourse('non-existent')).rejects.toEqual(mockError)
    })
  })
})