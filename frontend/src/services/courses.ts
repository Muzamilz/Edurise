import { api } from './api'
import type { 
  Course, 
  CourseModule, 
  Enrollment, 
  CourseReview, 
  LiveClass,
  PaginatedResponse, 
  CourseFilters 
} from '../types/api'

export class CourseService {
  // Course CRUD operations
  static async getCourses(filters?: CourseFilters): Promise<PaginatedResponse<Course>> {
    const response = await api.get('/courses/courses/', { params: filters })
    return response.data.data
  }

  static async getCourse(id: string): Promise<Course> {
    const response = await api.get(`/courses/courses/${id}/`)
    return response.data.data
  }

  static async createCourse(courseData: Partial<Course>): Promise<Course> {
    const response = await api.post('/courses/courses/', courseData)
    return response.data.data
  }

  static async updateCourse(id: string, courseData: Partial<Course>): Promise<Course> {
    const response = await api.patch(`/courses/courses/${id}/`, courseData)
    return response.data.data
  }

  static async deleteCourse(id: string): Promise<void> {
    await api.delete(`/courses/courses/${id}/`)
  }

  // Marketplace and special endpoints
  static async getMarketplaceCourses(filters?: CourseFilters): Promise<PaginatedResponse<Course>> {
    const response = await api.get('/courses/courses/marketplace/', { params: filters })
    return response.data.data
  }

  static async getFeaturedCourses(): Promise<Course[]> {
    const response = await api.get('/courses/courses/featured/')
    return response.data.data
  }

  static async getMyCourses(): Promise<PaginatedResponse<Course>> {
    const response = await api.get('/courses/courses/my_courses/')
    return response.data.data
  }

  static async getEnrolledCourses(): Promise<Course[]> {
    const response = await api.get('/courses/courses/enrolled_courses/')
    return response.data.data
  }

  static async getCourseCategories(): Promise<Array<{ category: string; count: number; avg_rating: number }>> {
    const response = await api.get('/courses/courses/categories/')
    return response.data.data
  }

  static async duplicateCourse(id: string): Promise<Course> {
    const response = await api.post(`/courses/courses/${id}/duplicate/`)
    return response.data.data
  }

  static async getCourseStatistics(id: string): Promise<any> {
    const response = await api.get(`/courses/courses/${id}/statistics/`)
    return response.data.data
  }

  static async getCourseStudents(id: string): Promise<Enrollment[]> {
    const response = await api.get(`/courses/courses/${id}/students/`)
    return response.data.data
  }

  // Enrollment operations
  static async enrollInCourse(courseId: string): Promise<Enrollment> {
    const response = await api.post(`/courses/courses/${courseId}/enroll/`)
    return response.data.data
  }

  static async getEnrollments(filters?: any): Promise<PaginatedResponse<Enrollment>> {
    const response = await api.get('/courses/enrollments/', { params: filters })
    return response.data.data
  }

  static async updateEnrollmentProgress(enrollmentId: string, progressPercentage: number): Promise<Enrollment> {
    const response = await api.patch(`/courses/enrollments/${enrollmentId}/update_progress/`, {
      progress_percentage: progressPercentage
    })
    return response.data.data
  }

  static async dropFromCourse(enrollmentId: string): Promise<Enrollment> {
    const response = await api.post(`/courses/enrollments/${enrollmentId}/drop/`)
    return response.data.data
  }

  static async getEnrollmentAnalytics(): Promise<any> {
    const response = await api.get('/courses/enrollments/analytics/')
    return response.data.data
  }

  static async getStudentDashboard(): Promise<any> {
    const response = await api.get('/courses/enrollments/dashboard/')
    return response.data.data
  }

  static async getEnrollmentProgressDetail(enrollmentId: string): Promise<any> {
    const response = await api.get(`/courses/enrollments/${enrollmentId}/progress_detail/`)
    return response.data.data
  }

  // Course modules
  static async getCourseModules(courseId: string): Promise<CourseModule[]> {
    const response = await api.get('/courses/modules/', { params: { course: courseId } })
    return response.data.data.results
  }

  static async createCourseModule(moduleData: Partial<CourseModule>): Promise<CourseModule> {
    const response = await api.post('/courses/modules/', moduleData)
    return response.data.data
  }

  static async updateCourseModule(id: string, moduleData: Partial<CourseModule>): Promise<CourseModule> {
    const response = await api.patch(`/courses/modules/${id}/`, moduleData)
    return response.data.data
  }

  static async deleteCourseModule(id: string): Promise<void> {
    await api.delete(`/courses/modules/${id}/`)
  }

  // Course reviews
  static async getCourseReviews(courseId: string): Promise<CourseReview[]> {
    const response = await api.get('/courses/reviews/', { params: { course: courseId } })
    return response.data.data.results
  }

  static async createCourseReview(reviewData: Partial<CourseReview>): Promise<CourseReview> {
    const response = await api.post('/courses/reviews/', reviewData)
    return response.data.data
  }

  static async updateCourseReview(id: string, reviewData: Partial<CourseReview>): Promise<CourseReview> {
    const response = await api.patch(`/courses/reviews/${id}/`, reviewData)
    return response.data.data
  }

  static async deleteCourseReview(id: string): Promise<void> {
    await api.delete(`/courses/reviews/${id}/`)
  }

  // Live classes
  static async getLiveClasses(courseId?: string): Promise<LiveClass[]> {
    const params = courseId ? { course: courseId } : {}
    const response = await api.get('/courses/live-classes/', { params })
    return response.data.data.results
  }

  static async createLiveClass(classData: Partial<LiveClass>): Promise<LiveClass> {
    const response = await api.post('/courses/live-classes/', classData)
    return response.data.data
  }

  static async updateLiveClass(id: string, classData: Partial<LiveClass>): Promise<LiveClass> {
    const response = await api.patch(`/courses/live-classes/${id}/`, classData)
    return response.data.data
  }

  static async deleteLiveClass(id: string): Promise<void> {
    await api.delete(`/courses/live-classes/${id}/`)
  }

  // Recommendations and analytics
  static async getRecommendedCourses(): Promise<Course[]> {
    const response = await api.get('/courses/courses/recommendations/')
    return response.data.data
  }

  static async getInstructorAnalytics(): Promise<any> {
    const response = await api.get('/courses/courses/instructor_analytics/')
    return response.data.data
  }

  // Wishlist operations
  static async addToWishlist(courseId: string): Promise<any> {
    const response = await api.post('/courses/wishlist/add_course/', { course_id: courseId })
    return response.data.data
  }

  static async removeFromWishlist(courseId: string): Promise<void> {
    await api.delete('/courses/wishlist/remove_course/', { data: { course_id: courseId } })
  }

  static async getWishlistItems(): Promise<any> {
    const response = await api.get('/courses/wishlist/')
    return response.data.data
  }

  static async getWishlistAnalytics(): Promise<any> {
    const response = await api.get('/courses/wishlist/analytics/')
    return response.data.data
  }
}