import { ref, computed } from 'vue'
import { zoomService } from '@/services/zoom'
import type { 
  LiveClass, 
  ClassAttendance, 
  EngagementMetrics, 
  ClassAnalyticsReport,
  ZoomMeetingInfo 
} from '@/types/api'

export const useZoom = () => {
  // State
  const liveClasses = ref<LiveClass[]>([])
  const currentLiveClass = ref<LiveClass | null>(null)
  const attendance = ref<ClassAttendance[]>([])
  const engagementMetrics = ref<EngagementMetrics | null>(null)
  const analyticsReport = ref<ClassAnalyticsReport | null>(null)
  const zoomMeetingInfo = ref<ZoomMeetingInfo | null>(null)
  
  // Loading states
  const isLoading = ref(false)
  const isCreatingMeeting = ref(false)
  const isUpdatingAttendance = ref(false)
  const isLoadingMetrics = ref(false)
  
  // Error handling
  const error = ref<string | null>(null)
  
  // WebSocket connection for real-time updates
  const wsConnection = ref<any>(null)
  const isConnected = ref(false)

  // Computed properties
  const upcomingClasses = computed(() => 
    liveClasses.value.filter(cls => 
      cls.status === 'scheduled' && new Date(cls.scheduled_at) > new Date()
    )
  )

  const liveClasses_active = computed(() => 
    liveClasses.value.filter(cls => cls.status === 'live')
  )

  const completedClasses = computed(() => 
    liveClasses.value.filter(cls => cls.status === 'completed')
  )

  const attendanceRate = computed(() => {
    if (!attendance.value.length) return 0
    const presentCount = attendance.value.filter(att => 
      ['present', 'partial', 'late'].includes(att.status)
    ).length
    return Math.round((presentCount / attendance.value.length) * 100)
  })

  // Live Class Management
  const fetchLiveClasses = async (courseId?: string) => {
    try {
      isLoading.value = true
      error.value = null
      const response = await zoomService.getLiveClasses(courseId)
      liveClasses.value = response.results
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch live classes'
      console.error('Error fetching live classes:', err)
    } finally {
      isLoading.value = false
    }
  }

  const fetchLiveClass = async (id: string) => {
    try {
      isLoading.value = true
      error.value = null
      currentLiveClass.value = await zoomService.getLiveClass(id)
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch live class'
      console.error('Error fetching live class:', err)
    } finally {
      isLoading.value = false
    }
  }

  const createLiveClass = async (data: {
    course: string
    title: string
    description?: string
    scheduled_at: string
    duration_minutes: number
  }) => {
    try {
      isLoading.value = true
      error.value = null
      const newClass = await zoomService.createLiveClass(data)
      liveClasses.value.push(newClass)
      return newClass
    } catch (err: any) {
      error.value = err.message || 'Failed to create live class'
      console.error('Error creating live class:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateLiveClass = async (id: string, data: {
    title?: string
    description?: string
    scheduled_at?: string
    duration_minutes?: number
  }) => {
    try {
      isLoading.value = true
      error.value = null
      const updatedClass = await zoomService.updateLiveClass(id, data)
      
      // Update in local state
      const index = liveClasses.value.findIndex(cls => cls.id === id)
      if (index !== -1) {
        liveClasses.value[index] = updatedClass
      }
      
      if (currentLiveClass.value?.id === id) {
        currentLiveClass.value = updatedClass
      }
      
      return updatedClass
    } catch (err: any) {
      error.value = err.message || 'Failed to update live class'
      console.error('Error updating live class:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteLiveClass = async (id: string) => {
    try {
      isLoading.value = true
      error.value = null
      await zoomService.deleteLiveClass(id)
      
      // Remove from local state
      liveClasses.value = liveClasses.value.filter(cls => cls.id !== id)
      
      if (currentLiveClass.value?.id === id) {
        currentLiveClass.value = null
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to delete live class'
      console.error('Error deleting live class:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Zoom Meeting Management
  const createZoomMeeting = async (liveClassId: string) => {
    try {
      isCreatingMeeting.value = true
      error.value = null
      const meetingInfo = await zoomService.createZoomMeeting(liveClassId)
      zoomMeetingInfo.value = meetingInfo
      
      // Update live class with Zoom details
      await fetchLiveClass(liveClassId)
      
      return meetingInfo
    } catch (err: any) {
      error.value = err.message || 'Failed to create Zoom meeting'
      console.error('Error creating Zoom meeting:', err)
      throw err
    } finally {
      isCreatingMeeting.value = false
    }
  }

  const updateZoomMeeting = async (liveClassId: string) => {
    try {
      isCreatingMeeting.value = true
      error.value = null
      const meetingInfo = await zoomService.updateZoomMeeting(liveClassId)
      zoomMeetingInfo.value = meetingInfo
      return meetingInfo
    } catch (err: any) {
      error.value = err.message || 'Failed to update Zoom meeting'
      console.error('Error updating Zoom meeting:', err)
      throw err
    } finally {
      isCreatingMeeting.value = false
    }
  }

  const joinZoomMeeting = (joinUrl: string) => {
    if (joinUrl) {
      window.open(joinUrl, '_blank', 'noopener,noreferrer')
    }
  }

  const startZoomMeeting = (startUrl: string) => {
    if (startUrl) {
      window.open(startUrl, '_blank', 'noopener,noreferrer')
    }
  }

  // Attendance Management
  const fetchAttendance = async (liveClassId: string) => {
    try {
      isLoading.value = true
      error.value = null
      const response = await zoomService.getClassAttendance(liveClassId)
      attendance.value = response.results
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch attendance'
      console.error('Error fetching attendance:', err)
    } finally {
      isLoading.value = false
    }
  }

  const markAttendance = async (liveClassId: string, studentId: string, status: string) => {
    try {
      isUpdatingAttendance.value = true
      error.value = null
      const updatedAttendance = await zoomService.markAttendance(liveClassId, studentId, status)
      
      // Update local state
      const index = attendance.value.findIndex(att => att.student.id === studentId)
      if (index !== -1) {
        attendance.value[index] = updatedAttendance
      } else {
        attendance.value.push(updatedAttendance)
      }
      
      return updatedAttendance
    } catch (err: any) {
      error.value = err.message || 'Failed to mark attendance'
      console.error('Error marking attendance:', err)
      throw err
    } finally {
      isUpdatingAttendance.value = false
    }
  }

  const bulkUpdateAttendance = async (liveClassId: string, attendanceData: any[]) => {
    try {
      isUpdatingAttendance.value = true
      error.value = null
      const updatedAttendance = await zoomService.bulkUpdateAttendance(liveClassId, attendanceData)
      attendance.value = updatedAttendance
      return updatedAttendance
    } catch (err: any) {
      error.value = err.message || 'Failed to update attendance'
      console.error('Error updating attendance:', err)
      throw err
    } finally {
      isUpdatingAttendance.value = false
    }
  }

  // Analytics and Metrics
  const fetchEngagementMetrics = async (liveClassId: string) => {
    try {
      isLoadingMetrics.value = true
      error.value = null
      engagementMetrics.value = await zoomService.getEngagementMetrics(liveClassId)
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch engagement metrics'
      console.error('Error fetching engagement metrics:', err)
    } finally {
      isLoadingMetrics.value = false
    }
  }

  const fetchAnalyticsReport = async (liveClassId: string) => {
    try {
      isLoadingMetrics.value = true
      error.value = null
      analyticsReport.value = await zoomService.getAnalyticsReport(liveClassId)
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch analytics report'
      console.error('Error fetching analytics report:', err)
    } finally {
      isLoadingMetrics.value = false
    }
  }

  // Real-time Updates with WebSocket
  const connectWebSocket = async (liveClassId: string) => {
    if (wsConnection.value) {
      wsConnection.value.disconnect()
    }

    try {
      const { createWebSocketConnection, getWebSocketUrl } = await import('@/services/websocket')
      const wsUrl = getWebSocketUrl(`/ws/live-class/${liveClassId}/`)
      
      wsConnection.value = createWebSocketConnection({ url: wsUrl })
      
      wsConnection.value.onConnect(() => {
        isConnected.value = true
        console.log('WebSocket connected for live class:', liveClassId)
      })
      
      wsConnection.value.onDisconnect(() => {
        isConnected.value = false
        console.log('WebSocket disconnected')
      })
      
      wsConnection.value.onError((error: Event) => {
        console.error('WebSocket error:', error)
        isConnected.value = false
      })

      // Subscribe to different message types
      wsConnection.value.subscribe('class_status_update', handleClassStatusUpdate)
      wsConnection.value.subscribe('attendance_update', handleAttendanceUpdate)
      wsConnection.value.subscribe('participant_joined', handleParticipantJoined)
      wsConnection.value.subscribe('participant_left', handleParticipantLeft)
      wsConnection.value.subscribe('engagement_update', handleEngagementUpdate)

      await wsConnection.value.connect()
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
    }
  }

  const disconnectWebSocket = () => {
    if (wsConnection.value) {
      wsConnection.value.disconnect()
      wsConnection.value = null
      isConnected.value = false
    }
  }

  // WebSocket message handlers
  const handleClassStatusUpdate = (data: any) => {
    if (currentLiveClass.value && currentLiveClass.value.id === data.class_id) {
      currentLiveClass.value.status = data.status
    }
  }

  const handleAttendanceUpdate = (data: any) => {
    const attendanceIndex = attendance.value.findIndex(att => att.id === data.attendance.id)
    if (attendanceIndex !== -1) {
      attendance.value[attendanceIndex] = data.attendance
    } else {
      attendance.value.push(data.attendance)
    }
  }

  const handleParticipantJoined = (data: any) => {
    console.log('Participant joined:', data.participant)
  }

  const handleParticipantLeft = (data: any) => {
    console.log('Participant left:', data.participant)
  }

  const handleEngagementUpdate = (data: any) => {
    if (data.metrics) {
      engagementMetrics.value = data.metrics
    }
  }

  // Class Status Management
  const startClass = async (liveClassId: string) => {
    try {
      const updatedClass = await zoomService.startClass(liveClassId)
      if (currentLiveClass.value?.id === liveClassId) {
        currentLiveClass.value = updatedClass
      }
      return updatedClass
    } catch (err: any) {
      error.value = err.message || 'Failed to start class'
      throw err
    }
  }

  const endClass = async (liveClassId: string) => {
    try {
      const updatedClass = await zoomService.endClass(liveClassId)
      if (currentLiveClass.value?.id === liveClassId) {
        currentLiveClass.value = updatedClass
      }
      return updatedClass
    } catch (err: any) {
      error.value = err.message || 'Failed to end class'
      throw err
    }
  }

  // Utility functions
  const exportAttendanceReport = async (liveClassId: string, format: 'csv' | 'pdf' = 'csv') => {
    try {
      const blob = await zoomService.exportAttendanceReport(liveClassId, format)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `attendance-report-${liveClassId}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      error.value = err.message || 'Failed to export attendance report'
      throw err
    }
  }

  const clearError = () => {
    error.value = null
  }

  const resetState = () => {
    liveClasses.value = []
    currentLiveClass.value = null
    attendance.value = []
    engagementMetrics.value = null
    analyticsReport.value = null
    zoomMeetingInfo.value = null
    error.value = null
    disconnectWebSocket()
  }

  return {
    // State
    liveClasses,
    currentLiveClass,
    attendance,
    engagementMetrics,
    analyticsReport,
    zoomMeetingInfo,
    
    // Loading states
    isLoading,
    isCreatingMeeting,
    isUpdatingAttendance,
    isLoadingMetrics,
    
    // WebSocket
    isConnected,
    
    // Error handling
    error,
    clearError,
    
    // Computed
    upcomingClasses,
    liveClasses_active,
    completedClasses,
    attendanceRate,
    
    // Live Class Management
    fetchLiveClasses,
    fetchLiveClass,
    createLiveClass,
    updateLiveClass,
    deleteLiveClass,
    
    // Zoom Integration
    createZoomMeeting,
    updateZoomMeeting,
    joinZoomMeeting,
    startZoomMeeting,
    
    // Attendance
    fetchAttendance,
    markAttendance,
    bulkUpdateAttendance,
    
    // Analytics
    fetchEngagementMetrics,
    fetchAnalyticsReport,
    
    // Real-time
    connectWebSocket,
    disconnectWebSocket,
    
    // Class Status
    startClass,
    endClass,
    
    // Utilities
    exportAttendanceReport,
    resetState
  }
}