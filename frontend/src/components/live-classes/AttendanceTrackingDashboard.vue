<template>
  <div class="attendance-dashboard">
    <!-- Header -->
    <div class="dashboard-header bg-white border-b border-gray-200 p-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ liveClass?.title }}</h1>
          <p class="text-gray-600 mt-1">Attendance Dashboard</p>
        </div>
        <div class="flex items-center space-x-4">
          <div class="status-indicator" :class="statusClasses">
            <div class="status-dot"></div>
            {{ statusText }}
          </div>
          <button
            @click="refreshData"
            :disabled="isLoading"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            <svg class="w-4 h-4 mr-2 inline" :class="{ 'animate-spin': isLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="stats-grid grid grid-cols-1 md:grid-cols-4 gap-6 p-6">
      <div class="stat-card bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Students</p>
            <p class="text-2xl font-semibold text-gray-900">{{ engagementMetrics?.total_students || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="stat-card bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Attendance Rate</p>
            <p class="text-2xl font-semibold text-gray-900">{{ Math.round(engagementMetrics?.attendance_rate || 0) }}%</p>
          </div>
        </div>
      </div>

      <div class="stat-card bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="w-8 h-8 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Avg Duration</p>
            <p class="text-2xl font-semibold text-gray-900">{{ Math.round(engagementMetrics?.average_duration || 0) }}m</p>
          </div>
        </div>
      </div>

      <div class="stat-card bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="w-8 h-8 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Engagement Score</p>
            <p class="text-2xl font-semibold text-gray-900">{{ Math.round(engagementMetrics?.engagement_score || 0) }}%</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
      <!-- Attendance List -->
      <div class="lg:col-span-2">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">Student Attendance</h3>
              <div class="flex items-center space-x-2">
                <select
                  v-model="attendanceFilter"
                  class="text-sm border border-gray-300 rounded-md px-3 py-1"
                >
                  <option value="all">All Students</option>
                  <option value="present">Present</option>
                  <option value="absent">Absent</option>
                  <option value="late">Late</option>
                  <option value="partial">Partial</option>
                </select>
                <button
                  @click="exportAttendance"
                  class="px-3 py-1 text-sm text-blue-600 hover:text-blue-800"
                >
                  Export
                </button>
              </div>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Student
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Join Time
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duration
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Participation
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="attendanceRecord in filteredAttendance"
                  :key="attendanceRecord.id"
                  class="hover:bg-gray-50"
                >
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-8 w-8">
                        <div class="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                          <span class="text-sm font-medium text-gray-700">
                            {{ getInitials(attendanceRecord.student.first_name, attendanceRecord.student.last_name) }}
                          </span>
                        </div>
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">
                          {{ attendanceRecord.student.first_name }} {{ attendanceRecord.student.last_name }}
                        </div>
                        <div class="text-sm text-gray-500">
                          {{ attendanceRecord.student.email }}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <select
                      :value="attendanceRecord.status"
                      @change="updateAttendanceStatus(attendanceRecord, ($event.target as HTMLSelectElement).value)"
                      class="text-sm border border-gray-300 rounded-md px-2 py-1"
                      :class="getStatusClasses(attendanceRecord.status)"
                    >
                      <option value="present">Present</option>
                      <option value="absent">Absent</option>
                      <option value="late">Late</option>
                      <option value="partial">Partial</option>
                    </select>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatTime(attendanceRecord.join_time) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ attendanceRecord.duration_minutes }}m
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          class="bg-blue-600 h-2 rounded-full"
                          :style="{ width: `${Math.min(100, attendanceRecord.participation_score)}%` }"
                        ></div>
                      </div>
                      <span class="text-sm text-gray-600">{{ attendanceRecord.participation_score }}%</span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      @click="editAttendance(attendanceRecord)"
                      class="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      Edit
                    </button>
                    <button
                      @click="viewStudentDetails(attendanceRecord.student)"
                      class="text-gray-600 hover:text-gray-900"
                    >
                      View
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="filteredAttendance.length === 0" class="text-center py-8">
            <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <p class="text-gray-500">No attendance records found</p>
          </div>
        </div>
      </div>

      <!-- Engagement Metrics Sidebar -->
      <div class="space-y-6">
        <!-- Status Breakdown -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Status Breakdown</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Present</span>
              <div class="flex items-center">
                <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                  <div
                    class="bg-green-500 h-2 rounded-full"
                    :style="{ width: `${getStatusPercentage('present')}%` }"
                  ></div>
                </div>
                <span class="text-sm font-medium">{{ engagementMetrics?.status_breakdown?.present || 0 }}</span>
              </div>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Late</span>
              <div class="flex items-center">
                <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                  <div
                    class="bg-yellow-500 h-2 rounded-full"
                    :style="{ width: `${getStatusPercentage('late')}%` }"
                  ></div>
                </div>
                <span class="text-sm font-medium">{{ engagementMetrics?.status_breakdown?.late || 0 }}</span>
              </div>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Partial</span>
              <div class="flex items-center">
                <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                  <div
                    class="bg-orange-500 h-2 rounded-full"
                    :style="{ width: `${getStatusPercentage('partial')}%` }"
                  ></div>
                </div>
                <span class="text-sm font-medium">{{ engagementMetrics?.status_breakdown?.partial || 0 }}</span>
              </div>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Absent</span>
              <div class="flex items-center">
                <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                  <div
                    class="bg-red-500 h-2 rounded-full"
                    :style="{ width: `${getStatusPercentage('absent')}%` }"
                  ></div>
                </div>
                <span class="text-sm font-medium">{{ engagementMetrics?.status_breakdown?.absent || 0 }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Participation Stats -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Participation</h3>
          <div class="space-y-4">
            <div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Active Participants</span>
                <span class="font-medium">{{ engagementMetrics?.participation_stats?.active_participants || 0 }}</span>
              </div>
              <div class="mt-1 bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-500 h-2 rounded-full"
                  :style="{ width: `${engagementMetrics?.participation_stats?.participation_rate || 0}%` }"
                ></div>
              </div>
            </div>
            <div class="text-sm">
              <span class="text-gray-600">Questions Asked:</span>
              <span class="font-medium ml-2">{{ engagementMetrics?.participation_stats?.total_questions || 0 }}</span>
            </div>
            <div class="text-sm">
              <span class="text-gray-600">Avg Participation:</span>
              <span class="font-medium ml-2">{{ Math.round(engagementMetrics?.participation_stats?.average_participation || 0) }}%</span>
            </div>
          </div>
        </div>

        <!-- Real-time Updates -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Live Updates</h3>
          <div class="space-y-3">
            <div class="flex items-center text-sm">
              <div class="w-2 h-2 rounded-full mr-3" :class="isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'"></div>
              <span class="text-gray-600">
                {{ isConnected ? 'Connected' : 'Disconnected' }}
              </span>
            </div>
            <div v-if="lastUpdateTime" class="text-xs text-gray-500">
              Last update: {{ lastUpdateTime.toLocaleTimeString() }}
            </div>
            
            <!-- Real-time update feed -->
            <div v-if="realtimeUpdates.length > 0" class="mt-4">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Recent Activity</h4>
              <div class="space-y-2 max-h-48 overflow-y-auto">
                <div 
                  v-for="update in realtimeUpdates.slice(0, 5)" 
                  :key="update.id"
                  class="text-xs p-2 bg-gray-50 rounded border-l-2 border-blue-400"
                >
                  <p class="text-gray-700">{{ update.message }}</p>
                  <p class="text-gray-500 mt-1">{{ update.timestamp.toLocaleTimeString() }}</p>
                </div>
              </div>
            </div>

            <!-- Class control buttons for live classes -->
            <div v-if="liveClass?.status === 'scheduled'" class="mt-4 space-y-2">
              <button
                @click="startClass"
                class="w-full px-3 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700"
              >
                Start Class
              </button>
            </div>
            
            <div v-if="liveClass?.status === 'live'" class="mt-4 space-y-2">
              <button
                @click="endClass"
                class="w-full px-3 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700"
              >
                End Class
              </button>
              <button
                @click="showAnnouncementModal = true"
                class="w-full px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Send Announcement
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Attendance Modal -->
    <div v-if="editingAttendance" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Edit Attendance</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                v-model="editForm.status"
                class="w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="present">Present</option>
                <option value="absent">Absent</option>
                <option value="late">Late</option>
                <option value="partial">Partial</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Participation Score (%)</label>
              <input
                v-model="editForm.participation_score"
                type="number"
                min="0"
                max="100"
                class="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Questions Asked</label>
              <input
                v-model="editForm.questions_asked"
                type="number"
                min="0"
                class="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
          </div>
          <div class="flex justify-end space-x-3 mt-6">
            <button
              @click="cancelEdit"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              @click="saveAttendanceEdit"
              :disabled="isUpdatingAttendance"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Announcement Modal -->
    <div v-if="showAnnouncementModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Send Class Announcement</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Message</label>
              <textarea
                v-model="announcementMessage"
                rows="4"
                class="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="Enter your announcement message..."
              ></textarea>
            </div>
          </div>
          <div class="flex justify-end space-x-3 mt-6">
            <button
              @click="showAnnouncementModal = false; announcementMessage = ''"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              @click="sendClassAnnouncement"
              :disabled="!announcementMessage.trim()"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              Send Announcement
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useZoom } from '@/composables/useZoom'
import { useWebSocketStore } from '@/stores/websocket'
import type { ClassAttendance } from '@/types/api'

interface Props {
  liveClassId: string
}

const props = defineProps<Props>()

const {
  currentLiveClass: liveClass,
  attendance,
  engagementMetrics,
  fetchLiveClass,
  fetchAttendance,
  fetchEngagementMetrics,
  markAttendance,
  exportAttendanceReport,
  isLoading,
  isUpdatingAttendance
} = useZoom()

const websocketStore = useWebSocketStore()

// WebSocket connection for real-time updates
const instructorWs = ref<any>(null)
const isConnected = ref(false)
const realtimeUpdates = ref<any[]>([])
const lastUpdateTime = ref<Date | null>(null)

// Local state
const attendanceFilter = ref('all')
const editingAttendance = ref<ClassAttendance | null>(null)
const editForm = ref({
  status: '',
  participation_score: 0,
  questions_asked: 0
})
const showAnnouncementModal = ref(false)
const announcementMessage = ref('')

// Computed properties
const statusClasses = computed(() => {
  switch (liveClass.value?.status) {
    case 'scheduled':
      return 'text-yellow-600 bg-yellow-100'
    case 'live':
      return 'text-green-600 bg-green-100'
    case 'completed':
      return 'text-gray-600 bg-gray-100'
    case 'cancelled':
      return 'text-red-600 bg-red-100'
    default:
      return 'text-gray-600 bg-gray-100'
  }
})

const statusText = computed(() => {
  switch (liveClass.value?.status) {
    case 'scheduled':
      return 'Scheduled'
    case 'live':
      return 'Live Now'
    case 'completed':
      return 'Completed'
    case 'cancelled':
      return 'Cancelled'
    default:
      return 'Unknown'
  }
})

const filteredAttendance = computed(() => {
  if (attendanceFilter.value === 'all') {
    return attendance.value
  }
  return attendance.value.filter(record => record.status === attendanceFilter.value)
})

// Methods
const getInitials = (firstName: string, lastName: string) => {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
}

const formatTime = (timeString?: string) => {
  if (!timeString) return '-'
  return new Date(timeString).toLocaleTimeString()
}

const getStatusClasses = (status: string) => {
  switch (status) {
    case 'present':
      return 'text-green-700 bg-green-100 border-green-300'
    case 'absent':
      return 'text-red-700 bg-red-100 border-red-300'
    case 'late':
      return 'text-yellow-700 bg-yellow-100 border-yellow-300'
    case 'partial':
      return 'text-orange-700 bg-orange-100 border-orange-300'
    default:
      return 'text-gray-700 bg-gray-100 border-gray-300'
  }
}

const getStatusPercentage = (status: string) => {
  const total = engagementMetrics.value?.total_students || 1
  const count = engagementMetrics.value?.status_breakdown?.[status as keyof typeof engagementMetrics.value.status_breakdown] || 0
  return Math.round((count / total) * 100)
}

// Removed duplicate function - using enhanced version below

const editAttendance = (attendanceRecord: ClassAttendance) => {
  editingAttendance.value = attendanceRecord
  editForm.value = {
    status: attendanceRecord.status,
    participation_score: attendanceRecord.participation_score,
    questions_asked: attendanceRecord.questions_asked
  }
}

const cancelEdit = () => {
  editingAttendance.value = null
  editForm.value = {
    status: '',
    participation_score: 0,
    questions_asked: 0
  }
}

const saveAttendanceEdit = async () => {
  if (!editingAttendance.value) return

  try {
    // Update attendance with new values
    await markAttendance(props.liveClassId, editingAttendance.value.student.id, editForm.value.status)
    
    // Update local record
    const index = attendance.value.findIndex(att => att.id === editingAttendance.value!.id)
    if (index !== -1) {
      attendance.value[index] = {
        ...attendance.value[index],
        status: editForm.value.status as 'present' | 'absent' | 'partial' | 'late',
        participation_score: editForm.value.participation_score,
        questions_asked: editForm.value.questions_asked
      }
    }

    cancelEdit()
    await refreshData()
  } catch (error) {
    console.error('Failed to save attendance edit:', error)
  }
}

const viewStudentDetails = (student: any) => {
  // Navigate to student profile or show details modal
  console.log('View student details:', student)
}

const exportAttendance = async () => {
  try {
    await exportAttendanceReport(props.liveClassId, 'csv')
  } catch (error) {
    console.error('Failed to export attendance:', error)
  }
}

const refreshData = async () => {
  await Promise.all([
    fetchLiveClass(props.liveClassId),
    fetchAttendance(props.liveClassId),
    fetchEngagementMetrics(props.liveClassId)
  ])
}

// WebSocket connection management for instructor dashboard
const connectToInstructorDashboard = () => {
  instructorWs.value = websocketStore.connectToInstructorLiveClass(props.liveClassId)
  
  if (instructorWs.value) {
    // Set up event handlers
    instructorWs.value.onConnect(() => {
      isConnected.value = true
      addRealtimeUpdate('Connected to real-time dashboard updates')
    })

    instructorWs.value.onDisconnect(() => {
      isConnected.value = false
      addRealtimeUpdate('Disconnected from real-time updates')
    })

    instructorWs.value.onError(() => {
      isConnected.value = false
      addRealtimeUpdate('Connection error - attempting to reconnect')
    })

    // Subscribe to real-time events
    instructorWs.value.subscribe('dashboard_update', (data: any) => {
      // Update dashboard data
      if (data.dashboard) {
        updateDashboardData(data.dashboard)
      }
      lastUpdateTime.value = new Date()
    })

    instructorWs.value.subscribe('attendance_update', (data: any) => {
      // Update attendance data
      if (data.attendance) {
        updateAttendanceData(data.attendance)
        addRealtimeUpdate(`Attendance updated for ${data.attendance.length} students`)
      }
    })

    instructorWs.value.subscribe('participant_joined', (data: any) => {
      addRealtimeUpdate(`${data.user_name} joined the class`)
      // Refresh attendance data
      fetchAttendance(props.liveClassId)
    })

    instructorWs.value.subscribe('participant_left', (data: any) => {
      addRealtimeUpdate(`${data.user_name} left the class`)
      // Refresh attendance data
      fetchAttendance(props.liveClassId)
    })

    instructorWs.value.subscribe('engagement_update', (data: any) => {
      // Update engagement metrics
      if (data.metrics) {
        Object.assign(engagementMetrics.value || {}, data.metrics)
        addRealtimeUpdate('Engagement metrics updated')
      }
    })

    instructorWs.value.subscribe('question_asked', (data: any) => {
      addRealtimeUpdate(`${data.user_name} asked a question`)
      // Refresh engagement metrics
      fetchEngagementMetrics(props.liveClassId)
    })

    instructorWs.value.subscribe('attendance_report', () => {
      addRealtimeUpdate('Attendance report generated')
    })

    // Connect to WebSocket
    instructorWs.value.connect().catch((error: any) => {
      console.error('Failed to connect to instructor WebSocket:', error)
      addRealtimeUpdate('Failed to connect to real-time updates')
    })
  }
}

const disconnectFromInstructorDashboard = () => {
  if (instructorWs.value) {
    websocketStore.disconnectFromInstructorLiveClass(props.liveClassId)
    instructorWs.value = null
    isConnected.value = false
  }
}

const addRealtimeUpdate = (message: string) => {
  realtimeUpdates.value.unshift({
    id: Date.now(),
    message,
    timestamp: new Date()
  })
  
  // Keep only last 10 updates
  if (realtimeUpdates.value.length > 10) {
    realtimeUpdates.value = realtimeUpdates.value.slice(0, 10)
  }
}

const updateDashboardData = (dashboardData: any) => {
  if (dashboardData.attendance) {
    attendance.value = dashboardData.attendance
  }
  if (dashboardData.metrics) {
    Object.assign(engagementMetrics.value || {}, dashboardData.metrics)
  }
}

const updateAttendanceData = (attendanceData: any[]) => {
  // Update attendance records
  attendanceData.forEach(newRecord => {
    const existingIndex = attendance.value.findIndex(att => att.id === newRecord.id)
    if (existingIndex !== -1) {
      attendance.value[existingIndex] = { ...attendance.value[existingIndex], ...newRecord }
    } else {
      attendance.value.push(newRecord)
    }
  })
}

// Enhanced methods with real-time updates
const updateAttendanceStatus = async (attendanceRecord: ClassAttendance, newStatus: string) => {
  try {
    await markAttendance(props.liveClassId, attendanceRecord.student.id, newStatus)
    
    // Send real-time update via WebSocket
    if (instructorWs.value?.isConnected) {
      instructorWs.value.send('update_attendance', {
        student_id: attendanceRecord.student.id,
        status: newStatus,
        timestamp: new Date().toISOString()
      })
    }
    
    addRealtimeUpdate(`Updated ${attendanceRecord.student.first_name} ${attendanceRecord.student.last_name} to ${newStatus}`)
    await refreshData()
  } catch (error) {
    console.error('Failed to update attendance status:', error)
    addRealtimeUpdate('Failed to update attendance status')
  }
}

const startClass = async () => {
  if (instructorWs.value?.isConnected) {
    instructorWs.value.send('start_class', {
      timestamp: new Date().toISOString()
    })
    addRealtimeUpdate('Class started')
  }
}

const endClass = async () => {
  if (instructorWs.value?.isConnected) {
    instructorWs.value.send('end_class', {
      timestamp: new Date().toISOString()
    })
    addRealtimeUpdate('Class ended')
  }
}

const sendAnnouncement = async (message: string) => {
  if (instructorWs.value?.isConnected) {
    instructorWs.value.send('send_announcement', {
      message,
      timestamp: new Date().toISOString()
    })
    addRealtimeUpdate(`Sent announcement: ${message}`)
  }
}

const sendClassAnnouncement = async () => {
  if (announcementMessage.value.trim()) {
    await sendAnnouncement(announcementMessage.value.trim())
    showAnnouncementModal.value = false
    announcementMessage.value = ''
  }
}

// Lifecycle
onMounted(async () => {
  await refreshData()
  connectToInstructorDashboard()
})

onUnmounted(() => {
  disconnectFromInstructorDashboard()
})

// Watch for live class status changes
watch(() => liveClass.value?.status, (newStatus) => {
  if (newStatus) {
    addRealtimeUpdate(`Class status changed to: ${newStatus}`)
  }
})
</script>

<style scoped>
.attendance-dashboard {
  @apply min-h-screen bg-gray-50;
}

.status-indicator {
  @apply flex items-center px-3 py-1 rounded-full text-sm font-medium;
}

.status-dot {
  @apply w-2 h-2 rounded-full mr-2;
  background-color: currentColor;
}

.stat-card {
  @apply transition-shadow hover:shadow-md;
}

.status-indicator.text-green-600 .status-dot {
  @apply animate-pulse;
}
</style>