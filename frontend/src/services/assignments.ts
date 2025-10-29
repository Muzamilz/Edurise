import { api, type PaginatedResponse } from './api'
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
  CertificateVerificationRequest,
  CertificateVerificationResponse,
  AssignmentFilters,
  SubmissionFilters,
  CertificateFilters,
  ProgressVisualizationData
} from '../types/assignments'

export class AssignmentService {
  // Assignment CRUD operations
  static async getAssignments(filters?: AssignmentFilters): Promise<PaginatedResponse<Assignment>> {
    const params = new URLSearchParams()
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString())
        }
      })
    }
    
    const response = await api.get<PaginatedResponse<Assignment>>(`/assignments/?${params}`)
    return response.data.data
  }

  static async getAssignment(id: string): Promise<Assignment> {
    const response = await api.get<Assignment>(`/assignments/${id}/`)
    return response.data.data
  }

  static async createAssignment(data: CreateAssignmentRequest): Promise<Assignment> {
    const response = await api.post<Assignment>('/assignments/', data)
    return response.data.data
  }

  static async updateAssignment(id: string, data: UpdateAssignmentRequest): Promise<Assignment> {
    const response = await api.patch<Assignment>(`/assignments/${id}/`, data)
    return response.data.data
  }

  static async deleteAssignment(id: string): Promise<void> {
    await api.delete(`/assignments/${id}/`)
  }

  static async publishAssignment(id: string): Promise<Assignment> {
    const response = await api.post<Assignment>(`/assignments/${id}/publish/`)
    return response.data.data
  }

  static async closeAssignment(id: string): Promise<Assignment> {
    const response = await api.post<Assignment>(`/assignments/${id}/close/`)
    return response.data.data
  }

  // Submission operations
  static async getSubmissions(filters?: SubmissionFilters): Promise<PaginatedResponse<Submission>> {
    const params = new URLSearchParams()
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString())
        }
      })
    }
    
    const response = await api.get<PaginatedResponse<Submission>>(`/submissions/?${params}`)
    return response.data.data
  }

  static async getSubmission(id: string): Promise<Submission> {
    const response = await api.get<Submission>(`/submissions/${id}/`)
    return response.data.data
  }

  static async getMySubmission(assignmentId: string): Promise<Submission | null> {
    try {
      const response = await api.get<Submission>(`/assignments/${assignmentId}/my-submission/`)
      return response.data.data
    } catch (error: any) {
      if (error.status === 404) {
        return null
      }
      throw error
    }
  }

  static async createSubmission(data: CreateSubmissionRequest): Promise<Submission> {
    const formData = new FormData()
    formData.append('assignment', data.assignment)
    
    if (data.text_content) {
      formData.append('text_content', data.text_content)
    }
    
    if (data.file_upload) {
      formData.append('file_upload', data.file_upload)
    }
    
    const response = await api.post<Submission>('/submissions/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data.data
  }

  static async updateSubmission(id: string, data: UpdateSubmissionRequest): Promise<Submission> {
    const formData = new FormData()
    
    if (data.text_content !== undefined) {
      formData.append('text_content', data.text_content)
    }
    
    if (data.file_upload) {
      formData.append('file_upload', data.file_upload)
    }
    
    const response = await api.patch<Submission>(`/submissions/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data.data
  }

  static async submitAssignment(id: string): Promise<Submission> {
    const response = await api.post<Submission>(`/submissions/${id}/submit/`)
    return response.data.data
  }

  static async gradeSubmission(id: string, data: GradeSubmissionRequest): Promise<Submission> {
    const response = await api.post<Submission>(`/submissions/${id}/grade/`, data)
    return response.data.data
  }

  static async deleteSubmission(id: string): Promise<void> {
    await api.delete(`/submissions/${id}/`)
  }

  // Certificate operations
  static async getCertificates(filters?: CertificateFilters): Promise<PaginatedResponse<Certificate>> {
    const params = new URLSearchParams()
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString())
        }
      })
    }
    
    const response = await api.get<PaginatedResponse<Certificate>>(`/certificates/?${params}`)
    return response.data.data
  }

  static async getCertificate(id: string): Promise<Certificate> {
    const response = await api.get<Certificate>(`/certificates/${id}/`)
    return response.data.data
  }

  static async generateCertificate(courseId: string, studentId: string): Promise<Certificate> {
    const response = await api.post<Certificate>('/certificates/', {
      course: courseId,
      student: studentId
    })
    return response.data.data
  }

  static async issueCertificate(id: string): Promise<Certificate> {
    const response = await api.post<Certificate>(`/api/v1/certificates/${id}/issue/`)
    return response.data.data
  }

  static async revokeCertificate(id: string): Promise<Certificate> {
    const response = await api.post<Certificate>(`/api/v1/certificates/${id}/revoke/`)
    return response.data.data
  }

  static async verifyCertificate(data: CertificateVerificationRequest): Promise<CertificateVerificationResponse> {
    const response = await api.get<CertificateVerificationResponse>(`/api/v1/certificates/verify/?certificate_number=${data.certificate_number}`)
    return response.data.data
  }

  static async verifyByQRCode(qrData: string): Promise<CertificateVerificationResponse> {
    const response = await api.post<CertificateVerificationResponse>('/api/v1/certificates/verify_by_qr/', {
      qr_data: qrData
    })
    return response.data.data
  }

  static async downloadCertificate(id: string): Promise<string> {
    const response = await api.get(`/api/v1/certificates/${id}/download/`)
    return response.data.data.download_url
  }

  static async generateCertificatePDF(id: string, templateType: string = 'completion'): Promise<{
    certificate_file_id: string
    download_url: string
    file_size: number
    filename: string
  }> {
    const response = await api.post(`/api/v1/certificates/${id}/generate_pdf/`, {
      template_type: templateType
    })
    return response.data.data
  }

  static async sendCertificateEmail(id: string): Promise<void> {
    await api.post(`/api/v1/certificates/${id}/send_email/`)
  }

  static async generateQRCode(id: string): Promise<{
    qr_code_file_id: string
    qr_code_url: string
    verification_url: string
  }> {
    const response = await api.post(`/api/v1/certificates/${id}/generate_qr_code/`)
    return response.data.data
  }

  static async getMyCertificates(): Promise<Certificate[]> {
    const response = await api.get<Certificate[]>('/api/v1/certificates/my_certificates/')
    return response.data.data
  }

  // Progress tracking
  static async getCourseProgress(courseId: string, studentId?: string): Promise<CourseProgress> {
    const url = studentId 
      ? `/courses/${courseId}/progress/?student=${studentId}`
      : `/courses/${courseId}/progress/`
    
    const response = await api.get<CourseProgress>(url)
    return response.data.data
  }

  static async getProgressVisualizationData(courseId: string, studentId?: string): Promise<ProgressVisualizationData> {
    const url = studentId 
      ? `/courses/${courseId}/progress/visualization/?student=${studentId}`
      : `/courses/${courseId}/progress/visualization/`
    
    const response = await api.get<ProgressVisualizationData>(url)
    return response.data.data
  }

  static async updateProgress(courseId: string, data: {
    module_id?: string
    assignment_id?: string
    class_id?: string
  }): Promise<CourseProgress> {
    const response = await api.post<CourseProgress>(`/courses/${courseId}/progress/update/`, data)
    return response.data.data
  }

  // Bulk operations
  static async bulkGradeSubmissions(submissions: Array<{
    id: string
    score: number
    feedback?: string
  }>): Promise<Submission[]> {
    const response = await api.post<Submission[]>('/submissions/bulk-grade/', {
      submissions
    })
    return response.data.data
  }

  static async exportGrades(assignmentId: string, format: 'csv' | 'xlsx' = 'csv'): Promise<Blob> {
    const response = await api.get(`/assignments/${assignmentId}/export-grades/?format=${format}`, {
      responseType: 'blob'
    })
    return response.data as unknown as Blob
  }

  static async importGrades(assignmentId: string, file: File): Promise<{ success: number; errors: string[] }> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post<{ success: number; errors: string[] }>(
      `/assignments/${assignmentId}/import-grades/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    return response.data.data
  }

  // Analytics
  static async getAssignmentAnalytics(assignmentId: string): Promise<{
    submission_stats: {
      total_submissions: number
      graded_submissions: number
      pending_submissions: number
      late_submissions: number
    }
    grade_distribution: Array<{
      range: string
      count: number
      percentage: number
    }>
    average_score: number
    passing_rate: number
    completion_rate: number
  }> {
    const response = await api.get(`/assignments/${assignmentId}/analytics/`)
    return response.data.data
  }

  static async getCourseAssignmentSummary(courseId: string): Promise<{
    total_assignments: number
    published_assignments: number
    overdue_assignments: number
    average_completion_rate: number
    assignments: Array<{
      id: string
      title: string
      due_date: string
      submission_count: number
      graded_count: number
      average_score: number
    }>
  }> {
    const response = await api.get(`/courses/${courseId}/assignments/summary/`)
    return response.data.data
  }
}

export default AssignmentService