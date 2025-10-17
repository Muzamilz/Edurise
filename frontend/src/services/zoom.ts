import { api } from './api'
import type { 
  LiveClass, 
  ClassAttendance, 
  EngagementMetrics, 
  ClassAnalyticsReport,
  ZoomMeetingInfo,
  PaginatedResponse 
} from '@/types/api'

export interface CreateLiveClassRequest {
  course: string
  title: string
  description?: string
  scheduled_at: string
  duration_minutes: number
}

export interface UpdateLiveClassRequest {
  title?: string
  description?: string
  scheduled_at?: string
  duration_minutes?: number
}

export interface AttendanceUpdateRequest {
  student: string
  status: 'present' | 'absent' | 'partial' | 'late'
  join_time?: string
  leave_time?: string
  participation_score?: number
  questions_asked?: number
}

class ZoomService {
  // Live Class Management
  async getLiveClasses(courseId?: string): Promise<PaginatedResponse<LiveClass>> {
    const params = courseId ? { course: courseId } : {}
    const response = await api.get('/api/v1/courses/live-classes/', { params })
    return response.data.data
  }

  async getLiveClass(id: string): Promise<LiveClass> {
    const response = await api.get(`/api/v1/courses/live-classes/${id}/`)
    return response.data.data
  }

  async createLiveClass(data: CreateLiveClassRequest): Promise<LiveClass> {
    const response = await api.post('/api/v1/courses/live-classes/', data)
    return response.data.data
  }

  async updateLiveClass(id: string, data: UpdateLiveClassRequest): Promise<LiveClass> {
    const response = await api.patch(`/api/v1/courses/live-classes/${id}/`, data)
    return response.data.data
  }

  async deleteLiveClass(id: string): Promise<void> {
    await api.delete(`/api/v1/courses/live-classes/${id}/`)
  }

  // Zoom Integration
  async createZoomMeeting(liveClassId: string): Promise<ZoomMeetingInfo> {
    const response = await api.post(`/api/v1/courses/live-classes/${liveClassId}/create_zoom_meeting/`)
    return response.data.data
  }

  async updateZoomMeeting(liveClassId: string): Promise<ZoomMeetingInfo> {
    const response = await api.put(`/api/v1/classes/zoom/meetings/${liveClassId}/`)
    return response.data.data
  }

  async deleteZoomMeeting(liveClassId: string): Promise<void> {
    await api.delete(`/api/v1/classes/zoom/meetings/${liveClassId}/`)
  }

  async getZoomMeetingInfo(liveClassId: string): Promise<ZoomMeetingInfo> {
    const response = await api.get(`/api/v1/courses/live-classes/${liveClassId}/join_info/`)
    return response.data.data
  }

  // Attendance Management
  async getClassAttendance(liveClassId: string): Promise<PaginatedResponse<ClassAttendance>> {
    const response = await api.get(`/api/v1/classes/attendance/`, {
      params: { live_class_id: liveClassId }
    })
    return response.data.data
  }

  async updateAttendance(liveClassId: string, data: AttendanceUpdateRequest): Promise<ClassAttendance> {
    const response = await api.post(`/api/v1/classes/attendance/`, {
      live_class_id: liveClassId,
      ...data
    })
    return response.data.data
  }

  async markAttendance(liveClassId: string, studentId: string, status: string): Promise<ClassAttendance> {
    const response = await api.post(`/api/v1/classes/attendance/mark_attendance/`, {
      live_class_id: liveClassId,
      student_id: studentId,
      status
    })
    return response.data.data
  }

  // Analytics and Metrics
  async getEngagementMetrics(liveClassId: string): Promise<EngagementMetrics> {
    const response = await api.get(`/api/v1/courses/live-classes/${liveClassId}/attendance_report/`)
    return response.data.data
  }

  async getAnalyticsReport(liveClassId: string): Promise<ClassAnalyticsReport> {
    const response = await api.get(`/api/v1/courses/live-classes/${liveClassId}/attendance_report/`)
    return response.data.data
  }

  // Real-time Status
  async updateClassStatus(liveClassId: string, status: string): Promise<LiveClass> {
    const response = await api.patch(`/api/v1/courses/live-classes/${liveClassId}/`, { status })
    return response.data.data
  }

  async startClass(liveClassId: string): Promise<LiveClass> {
    const response = await api.post(`/api/v1/courses/live-classes/${liveClassId}/start_class/`)
    return response.data.data
  }

  async endClass(liveClassId: string): Promise<LiveClass> {
    const response = await api.post(`/api/v1/courses/live-classes/${liveClassId}/end_class/`)
    return response.data.data
  }

  // Bulk Operations
  async bulkUpdateAttendance(liveClassId: string, attendanceData: AttendanceUpdateRequest[]): Promise<ClassAttendance[]> {
    const response = await api.post(`/api/v1/classes/attendance/bulk_update/`, {
      live_class_id: liveClassId,
      attendance_data: attendanceData
    })
    return response.data.data
  }

  async exportAttendanceReport(liveClassId: string, format: 'csv' | 'pdf' = 'csv'): Promise<Blob> {
    const response = await api.get(`/api/v1/courses/live-classes/${liveClassId}/attendance_report/`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data.data
  }
}

export const zoomService = new ZoomService()