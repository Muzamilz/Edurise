import { api } from './api'
import type { 
  Course, 
  CourseModule, 
  Enrollment, 
  CourseReview, 
  LiveClass,
  PaginatedResponse, 
  CourseFilters,
  EnrollmentFilters,
  CourseStatistics
} from '../types/api'

export class CourseService {
  // Course CRUD operations
  static async getCourses(filters?: CourseFilters): Promise<PaginatedResponse<Course>> {
    const response = await api.get('/courses/', { params: filters })
    return response.data.data
  }

  static async getCourse(id: string): Promise<Course> {
    const response = await api.get(`/courses/${id}/`)
    return response.data.data
  }

  static async createCourse(courseData: Partial<Course>): Promise<Course> {
    const response = await api.post('/courses/', courseData)
    return response.data.data
  }

  static async updateCourse(id: string, courseData: Partial<Course>): Promise<Course> {
    const response = await api.patch(`/courses/${id}/`, courseData)
    return response.data.data
  }

  static async deleteCourse(id: string): Promise<void> {
    await api.delete(`/courses/${id}/`)
  }

  // Marketplace and special endpoints
  static async getMarketplaceCourses(filters?: CourseFilters): Promise<PaginatedResponse<Course>> {
    const response = await api.get('/courses/marketplace/', { params: filters })
    return response.data.data
  }

  static async getFeaturedCourses(): Promise<Course[]> {
    const response = await api.get('/courses/featured/')
    return response.data.data
  }

  static async getMyCourses(): Promise<PaginatedResponse<Course>> {
    const response = await api.get('/courses/my_courses/')
    return response.data.data
  }

  static async getEnrolledCourses(): Promise<Course[]> {
    const response = await api.get('/courses/enrolled_courses/')
    return response.data.data
  }

  static async getCourseCategories(): Promise<Array<{ category: string; count: number; avg_rating: number }>> {
    const response = await api.get('/courses/categories/')
    return response.data.data
  }

  static async duplicateCourse(id: string): Promise<Course> {
    const response = await api.post(`/courses/${id}/duplicate/`)
    return response.data.data
  }

  /**
   * Get course statistics
   * @param id - Course ID
   * @returns Course statistics including enrollments, ratings, and revenue
   */
  static async getCourseStatistics(id: string): Promise<CourseStatistics> {
    const response = await api.get<CourseStatistics>(`/courses/${id}/statistics/`)
    return response.data.data
  }

  static async getCourseStudents(id: string): Promise<Enrollment[]> {
    const response = await api.get(`/courses/${id}/students/`)
    return response.data.data
  }

  // Enrollment operations
  static async enrollInCourse(courseId: string): Promise<Enrollment> {
    const response = await api.post(`/courses/${courseId}/enroll/`)
    return response.data.data
  }

  /**
   * Get enrollments with optional filtering
   * @param filters - Optional filters for enrollments
   * @returns Paginated list of enrollments
   */
  static async getEnrollments(filters?: EnrollmentFilters): Promise<PaginatedResponse<Enrollment>> {
    const response = await api.get<PaginatedResponse<Enrollment>>('/enrollments/', { params: filters })
    return response.data.data
  }

  static async updateEnrollmentProgress(enrollmentId: string, progressPercentage: number): Promise<Enrollment> {
    const response = await api.patch(`/enrollments/${enrollmentId}/update_progress/`, {
      progress_percentage: progressPercentage
    })
    return response.data.data
  }

  static async dropFromCourse(enrollmentId: string): Promise<Enrollment> {
    const response = await api.post(`/enrollments/${enrollmentId}/drop/`)
    return response.data.data
  }

  static async getEnrollmentAnalytics(): Promise<any> {
    const response = await api.get('/enrollments/analytics/')
    return response.data.data
  }

  static async getStudentDashboard(): Promise<any> {
    const response = await api.get('/enrollments/dashboard/')
    return response.data.data
  }

  static async getEnrollmentProgressDetail(enrollmentId: string): Promise<any> {
    const response = await api.get(`/enrollments/${enrollmentId}/progress_detail/`)
    return response.data.data
  }

  // Course modules
  static async getCourseModules(courseId: string): Promise<CourseModule[]> {
    const response = await api.get('/course-modules/', { params: { course: courseId } })
    return response.data.data.results
  }

  static async createCourseModule(moduleData: Partial<CourseModule>): Promise<CourseModule> {
    const response = await api.post('/course-modules/', moduleData)
    return response.data.data
  }

  static async updateCourseModule(id: string, moduleData: Partial<CourseModule>): Promise<CourseModule> {
    const response = await api.patch(`/course-modules/${id}/`, moduleData)
    return response.data.data
  }

  static async deleteCourseModule(id: string): Promise<void> {
    await api.delete(`/course-modules/${id}/`)
  }

  // Course reviews
  static async getCourseReviews(courseId: string): Promise<CourseReview[]> {
    const response = await api.get('/course-reviews/', { params: { course: courseId } })
    return response.data.data.results
  }

  static async createCourseReview(reviewData: Partial<CourseReview>): Promise<CourseReview> {
    const response = await api.post('/course-reviews/', reviewData)
    return response.data.data
  }

  static async updateCourseReview(id: string, reviewData: Partial<CourseReview>): Promise<CourseReview> {
    const response = await api.patch(`/course-reviews/${id}/`, reviewData)
    return response.data.data
  }

  static async deleteCourseReview(id: string): Promise<void> {
    await api.delete(`/course-reviews/${id}/`)
  }

  // Live classes
  static async getLiveClasses(courseId?: string): Promise<LiveClass[]> {
    const params = courseId ? { course: courseId } : {}
    const response = await api.get('/live-classes/', { params })
    return response.data.data.results
  }

  static async createLiveClass(classData: Partial<LiveClass>): Promise<LiveClass> {
    const response = await api.post('/live-classes/', classData)
    return response.data.data
  }

  static async updateLiveClass(id: string, classData: Partial<LiveClass>): Promise<LiveClass> {
    const response = await api.patch(`/live-classes/${id}/`, classData)
    return response.data.data
  }

  static async deleteLiveClass(id: string): Promise<void> {
    await api.delete(`/live-classes/${id}/`)
  }

  // Recommendations and analytics
  static async getRecommendedCourses(): Promise<Course[]> {
    const response = await api.get('/recommendations/')
    return response.data.data
  }

  static async getInstructorAnalytics(): Promise<any> {
    const response = await api.get('/courses/instructor_analytics/')
    return response.data.data
  }

  // Wishlist operations
  static async addToWishlist(courseId: string): Promise<any> {
    const response = await api.post('/wishlist/add_course/', { course_id: courseId })
    return response.data.data
  }

  static async removeFromWishlist(courseId: string): Promise<void> {
    await api.delete('/wishlist/remove_course/', { data: { course_id: courseId } })
  }

  static async getWishlistItems(): Promise<any> {
    const response = await api.get('/wishlist/')
    return response.data.data
  }

  static async getWishlistAnalytics(): Promise<any> {
    const response = await api.get('/wishlist/analytics/')
    return response.data.data
  }

  /**
   * Download materials for a live class
   * @param liveClassId - ID of the live class
   * @returns Blob containing the materials zip file
   */
  static async downloadClassMaterials(liveClassId: string): Promise<Blob> {
    try {
      const response = await api.get(`/live-classes/${liveClassId}/materials/`, {
        responseType: 'blob'
      })
      return response.data as unknown as Blob
    } catch (error) {
      console.error('Error downloading class materials:', error)
      throw error
    }
  }

  /**
   * Start a live class session
   * @param liveClassId - ID of the live class
   * @returns Updated live class with join URL
   */
  static async startLiveClass(liveClassId: string): Promise<LiveClass> {
    try {
      const response = await api.post<LiveClass>(`/live-classes/${liveClassId}/start_class/`)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error starting live class:', error)
      throw error
    }
  }

  /**
   * End a live class session
   * @param liveClassId - ID of the live class
   */
  static async endLiveClass(liveClassId: string): Promise<void> {
    try {
      await api.post(`/live-classes/${liveClassId}/end_class/`)
    } catch (error) {
      console.error('Error ending live class:', error)
      throw error
    }
  }

  /**
   * Cancel a scheduled live class
   * @param liveClassId - ID of the live class
   * @returns Updated live class with cancelled status
   */
  static async cancelLiveClass(liveClassId: string): Promise<LiveClass> {
    try {
      const response = await api.patch<LiveClass>(`/live-classes/${liveClassId}/`, {
        status: 'cancelled'
      })
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error cancelling live class:', error)
      throw error
    }
  }

  /**
   * Mark a course module as complete
   * @param moduleId - ID of the course module
   * @returns Updated module with completion status
   */
  static async markModuleComplete(moduleId: string): Promise<CourseModule> {
    try {
      const response = await api.patch<CourseModule>(`/course-modules/${moduleId}/complete/`)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error marking module complete:', error)
      throw error
    }
  }

  /**
   * Update course module progress
   * @param moduleId - ID of the course module
   * @param data - Progress data to update
   * @returns Updated module
   */
  static async updateModuleProgress(moduleId: string, data: {
    progress_percentage?: number
    time_spent?: number
    is_completed?: boolean
  }): Promise<CourseModule> {
    try {
      const response = await api.patch<CourseModule>(`/course-modules/${moduleId}/`, data)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error updating module progress:', error)
      throw error
    }
  }
}