<template>
  <div class="real-time-assignment-updates">
    <!-- Assignment Submission Notifications -->
    <div v-if="recentSubmissions.length > 0" class="submissions-feed">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Recent Submissions</h3>
      <div class="space-y-3">
        <div 
          v-for="submission in recentSubmissions" 
          :key="submission.id"
          class="submission-notification p-4 bg-blue-50 border border-blue-200 rounded-lg"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span class="text-blue-600">📄</span>
                </div>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">
                  {{ submission.student_name }} submitted {{ submission.assignment_title }}
                </p>
                <p class="text-xs text-gray-500 mt-1">
                  {{ formatTimeAgo(submission.submitted_at) }}
                </p>
                <div v-if="submission.late" class="mt-1">
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                    Late Submission
                  </span>
                </div>
              </div>
            </div>
            <div class="flex space-x-2">
              <button
                @click="viewSubmission(submission)"
                class="text-xs text-blue-600 hover:text-blue-800"
              >
                View
              </button>
              <button
                @click="gradeSubmission(submission)"
                class="text-xs text-green-600 hover:text-green-800"
              >
                Grade
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Grade Updates -->
    <div v-if="recentGrades.length > 0" class="grades-feed mt-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Recent Grades</h3>
      <div class="space-y-3">
        <div 
          v-for="grade in recentGrades" 
          :key="grade.id"
          class="grade-notification p-4 bg-green-50 border border-green-200 rounded-lg"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <span class="text-green-600">🎓</span>
                </div>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">
                  {{ grade.assignment_title }} - Grade: {{ grade.score }}/{{ grade.max_score }}
                </p>
                <p class="text-xs text-gray-500 mt-1">
                  Graded {{ formatTimeAgo(grade.graded_at) }}
                </p>
                <div v-if="grade.feedback" class="mt-2">
                  <p class="text-sm text-gray-700 bg-white p-2 rounded border">
                    {{ grade.feedback }}
                  </p>
                </div>
              </div>
            </div>
            <div class="flex items-center">
              <span 
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                :class="getGradeClasses(grade.score, grade.max_score)"
              >
                {{ Math.round((grade.score / grade.max_score) * 100) }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Course Enrollment Notifications -->
    <div v-if="recentEnrollments.length > 0" class="enrollments-feed mt-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">New Enrollments</h3>
      <div class="space-y-3">
        <div 
          v-for="enrollment in recentEnrollments" 
          :key="enrollment.id"
          class="enrollment-notification p-4 bg-purple-50 border border-purple-200 rounded-lg"
        >
          <div class="flex items-start space-x-3">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <span class="text-purple-600">👥</span>
              </div>
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900">
                {{ enrollment.student_name }} enrolled in {{ enrollment.course_title }}
              </p>
              <p class="text-xs text-gray-500 mt-1">
                {{ formatTimeAgo(enrollment.enrolled_at) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- System Announcements -->
    <div v-if="systemAnnouncements.length > 0" class="announcements-feed mt-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">System Announcements</h3>
      <div class="space-y-3">
        <div 
          v-for="announcement in systemAnnouncements" 
          :key="announcement.id"
          class="announcement-notification p-4 border rounded-lg"
          :class="getAnnouncementClasses(announcement.priority)"
        >
          <div class="flex items-start space-x-3">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 rounded-full flex items-center justify-center"
                   :class="getAnnouncementIconClasses(announcement.priority)">
                <span>{{ getAnnouncementIcon(announcement.priority) }}</span>
              </div>
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900">
                {{ announcement.title }}
              </p>
              <p class="text-sm text-gray-700 mt-1">
                {{ announcement.message }}
              </p>
              <p class="text-xs text-gray-500 mt-2">
                {{ formatTimeAgo(announcement.created_at) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- User Status Indicators -->
    <div v-if="onlineUsers.length > 0" class="online-users mt-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Online Now</h3>
      <div class="flex flex-wrap gap-2">
        <div 
          v-for="user in onlineUsers" 
          :key="user.id"
          class="flex items-center space-x-2 bg-green-50 border border-green-200 rounded-full px-3 py-1"
        >
          <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span class="text-sm text-green-800">{{ user.name }}</span>
        </div>
      </div>
    </div>

    <!-- Connection Status -->
    <div class="connection-status mt-6 p-3 bg-gray-50 rounded-lg">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <div 
            class="w-2 h-2 rounded-full"
            :class="isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'"
          ></div>
          <span class="text-sm text-gray-600">
            {{ isConnected ? 'Connected to real-time updates' : 'Disconnected' }}
          </span>
        </div>
        <button 
          v-if="!isConnected"
          @click="reconnect"
          class="text-xs text-blue-600 hover:text-blue-800"
        >
          Reconnect
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
// Icons temporarily commented out due to missing module
// import {
//   DocumentTextIcon,
//   AcademicCapIcon,
//   UserGroupIcon,
//   InformationCircleIcon,
//   ExclamationTriangleIcon,
//   BellIcon
// } from '@heroicons/vue/24/outline'
import { useWebSocketStore } from '@/stores/websocket'
import { useNotificationStore } from '@/stores/notifications'

interface AssignmentSubmission {
  id: string
  student_name: string
  assignment_title: string
  submitted_at: string
  late: boolean
}

interface GradeUpdate {
  id: string
  assignment_title: string
  score: number
  max_score: number
  graded_at: string
  feedback?: string
}

interface CourseEnrollment {
  id: string
  student_name: string
  course_title: string
  enrolled_at: string
}

interface SystemAnnouncement {
  id: string
  title: string
  message: string
  priority: 'low' | 'normal' | 'high' | 'urgent'
  created_at: string
}

interface OnlineUser {
  id: string
  name: string
  status: 'online' | 'away' | 'busy'
}

const websocketStore = useWebSocketStore()
const notificationStore = useNotificationStore()

// State
const isConnected = ref(false)
const recentSubmissions = ref<AssignmentSubmission[]>([])
const recentGrades = ref<GradeUpdate[]>([])
const recentEnrollments = ref<CourseEnrollment[]>([])
const systemAnnouncements = ref<SystemAnnouncement[]>([])
const onlineUsers = ref<OnlineUser[]>([])

// WebSocket connection
let collaborationWs: any = null

const connectToCollaborationUpdates = () => {
  collaborationWs = websocketStore.getConnection('notifications')
  
  if (collaborationWs) {
    collaborationWs.onConnect(() => {
      isConnected.value = true
    })

    collaborationWs.onDisconnect(() => {
      isConnected.value = false
    })

    // Subscribe to collaboration events
    collaborationWs.subscribe('assignment_submitted', (data: any) => {
      const submission: AssignmentSubmission = {
        id: data.submission_id,
        student_name: data.student_name,
        assignment_title: data.assignment_title,
        submitted_at: data.submitted_at,
        late: data.late || false
      }
      
      recentSubmissions.value.unshift(submission)
      
      // Keep only last 10 submissions
      if (recentSubmissions.value.length > 10) {
        recentSubmissions.value = recentSubmissions.value.slice(0, 10)
      }

      // Show notification
      notificationStore.addNotification({
        id: `submission-${submission.id}`,
        type: 'assignment_submitted',
        title: 'New Assignment Submission',
        message: `${submission.student_name} submitted ${submission.assignment_title}`,
        data: { submission_id: submission.id },
        is_read: false,
        created_at: new Date().toISOString(),
        priority: submission.late ? 'high' : 'normal',
        category: 'assignment'
      })
    })

    collaborationWs.subscribe('assignment_graded', (data: any) => {
      const grade: GradeUpdate = {
        id: data.grade_id,
        assignment_title: data.assignment_title,
        score: data.score,
        max_score: data.max_score,
        graded_at: data.graded_at,
        feedback: data.feedback
      }
      
      recentGrades.value.unshift(grade)
      
      // Keep only last 10 grades
      if (recentGrades.value.length > 10) {
        recentGrades.value = recentGrades.value.slice(0, 10)
      }

      // Show notification
      notificationStore.addNotification({
        id: `grade-${grade.id}`,
        type: 'assignment_graded',
        title: 'Assignment Graded',
        message: `Your assignment "${grade.assignment_title}" has been graded: ${grade.score}/${grade.max_score}`,
        data: { grade_id: grade.id },
        is_read: false,
        created_at: new Date().toISOString(),
        priority: 'normal',
        category: 'grade'
      })
    })

    collaborationWs.subscribe('course_enrolled', (data: any) => {
      const enrollment: CourseEnrollment = {
        id: data.enrollment_id,
        student_name: data.student_name,
        course_title: data.course_title,
        enrolled_at: data.enrolled_at
      }
      
      recentEnrollments.value.unshift(enrollment)
      
      // Keep only last 10 enrollments
      if (recentEnrollments.value.length > 10) {
        recentEnrollments.value = recentEnrollments.value.slice(0, 10)
      }

      // Show notification
      notificationStore.addNotification({
        id: `enrollment-${enrollment.id}`,
        type: 'course_enrolled',
        title: 'New Course Enrollment',
        message: `${enrollment.student_name} enrolled in ${enrollment.course_title}`,
        data: { enrollment_id: enrollment.id },
        is_read: false,
        created_at: new Date().toISOString(),
        priority: 'normal',
        category: 'course'
      })
    })

    collaborationWs.subscribe('system_announcement', (data: any) => {
      const announcement: SystemAnnouncement = {
        id: data.announcement_id,
        title: data.title,
        message: data.message,
        priority: data.priority || 'normal',
        created_at: data.created_at
      }
      
      systemAnnouncements.value.unshift(announcement)
      
      // Keep only last 5 announcements
      if (systemAnnouncements.value.length > 5) {
        systemAnnouncements.value = systemAnnouncements.value.slice(0, 5)
      }

      // Show notification
      notificationStore.addNotification({
        id: `announcement-${announcement.id}`,
        type: 'system_announcement',
        title: announcement.title,
        message: announcement.message,
        data: { announcement_id: announcement.id },
        is_read: false,
        created_at: new Date().toISOString(),
        priority: announcement.priority,
        category: 'system'
      })
    })

    collaborationWs.subscribe('user_status_update', (data: any) => {
      const userIndex = onlineUsers.value.findIndex(u => u.id === data.user_id)
      
      if (data.status === 'online') {
        if (userIndex === -1) {
          onlineUsers.value.push({
            id: data.user_id,
            name: data.user_name,
            status: 'online'
          })
        }
      } else if (userIndex !== -1) {
        onlineUsers.value.splice(userIndex, 1)
      }
    })
  }
}

const reconnect = async () => {
  if (collaborationWs) {
    try {
      await collaborationWs.connect()
    } catch (error) {
      console.error('Failed to reconnect:', error)
    }
  }
}

// Helper methods
const formatTimeAgo = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) {
    return 'Just now'
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}m ago`
  } else if (diffInMinutes < 1440) {
    const hours = Math.floor(diffInMinutes / 60)
    return `${hours}h ago`
  } else {
    const days = Math.floor(diffInMinutes / 1440)
    return `${days}d ago`
  }
}

const getGradeClasses = (score: number, maxScore: number) => {
  const percentage = (score / maxScore) * 100
  
  if (percentage >= 90) {
    return 'bg-green-100 text-green-800'
  } else if (percentage >= 80) {
    return 'bg-blue-100 text-blue-800'
  } else if (percentage >= 70) {
    return 'bg-yellow-100 text-yellow-800'
  } else {
    return 'bg-red-100 text-red-800'
  }
}

const getAnnouncementClasses = (priority: string) => {
  switch (priority) {
    case 'urgent':
      return 'bg-red-50 border-red-200'
    case 'high':
      return 'bg-orange-50 border-orange-200'
    case 'normal':
      return 'bg-blue-50 border-blue-200'
    default:
      return 'bg-gray-50 border-gray-200'
  }
}

const getAnnouncementIconClasses = (priority: string) => {
  switch (priority) {
    case 'urgent':
      return 'bg-red-100 text-red-600'
    case 'high':
      return 'bg-orange-100 text-orange-600'
    case 'normal':
      return 'bg-blue-100 text-blue-600'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

const getAnnouncementIcon = (priority: string) => {
  switch (priority) {
    case 'urgent':
    case 'high':
      return '⚠️'
    case 'normal':
      return 'ℹ️'
    default:
      return '🔔'
  }
}

// Actions
const viewSubmission = (submission: AssignmentSubmission) => {
  // Navigate to submission view
  console.log('View submission:', submission)
}

const gradeSubmission = (submission: AssignmentSubmission) => {
  // Navigate to grading interface
  console.log('Grade submission:', submission)
}

// Lifecycle
onMounted(() => {
  connectToCollaborationUpdates()
})

onUnmounted(() => {
  // Cleanup handled by WebSocket store
})
</script>

<style scoped>
.real-time-assignment-updates {
  @apply space-y-6;
}

.submission-notification,
.grade-notification,
.enrollment-notification,
.announcement-notification {
  @apply transition-all duration-200 hover:shadow-md;
}

.connection-status {
  @apply border border-gray-200;
}
</style>