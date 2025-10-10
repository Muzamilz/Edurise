<template>
  <div class="live-classes-view">
    <!-- Page Header -->
    <div class="page-header bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Live Classes</h1>
            <p class="mt-1 text-sm text-gray-500">
              Manage and join live class sessions
            </p>
          </div>
          <div class="flex items-center space-x-4">
            <button
              v-if="isTeacher"
              @click="showScheduler = true"
              class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
            >
              <svg class="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Schedule Class
            </button>
            <div class="flex items-center space-x-2">
              <label class="text-sm text-gray-700">View:</label>
              <select
                v-model="viewMode"
                class="text-sm border border-gray-300 rounded-md px-3 py-1"
              >
                <option value="grid">Grid</option>
                <option value="list">List</option>
                <option value="calendar">Calendar</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="filters-section bg-gray-50 border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          <div class="flex items-center space-x-4">
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search classes..."
                class="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <svg class="absolute left-3 top-2.5 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <select
              v-model="statusFilter"
              class="text-sm border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All Status</option>
              <option value="scheduled">Scheduled</option>
              <option value="live">Live Now</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <select
              v-if="isTeacher"
              v-model="courseFilter"
              class="text-sm border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All Courses</option>
              <option
                v-for="course in teacherCourses"
                :key="course.id"
                :value="course.id"
              >
                {{ course.title }}
              </option>
            </select>
          </div>
          <div class="flex items-center space-x-2 text-sm text-gray-600">
            <span>{{ filteredClasses.length }} classes</span>
            <div v-if="isConnected" class="flex items-center text-green-600">
              <div class="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></div>
              Live
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Live Classes Alert -->
      <div v-if="liveClasses_active.length > 0" class="mb-6">
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
            </svg>
            <div class="flex-1">
              <h3 class="text-sm font-medium text-green-800">
                {{ liveClasses_active.length }} class{{ liveClasses_active.length > 1 ? 'es' : '' }} currently live
              </h3>
              <div class="mt-2 flex flex-wrap gap-2">
                <button
                  v-for="liveClass in liveClasses_active"
                  :key="liveClass.id"
                  @click="joinClass(liveClass)"
                  class="px-3 py-1 bg-green-600 text-white text-xs rounded-md hover:bg-green-700 transition-colors"
                >
                  Join {{ liveClass.title }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <svg class="animate-spin h-8 w-8 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-gray-500">Loading live classes...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredClasses.length === 0" class="text-center py-12">
        <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No live classes found</h3>
        <p class="text-gray-500 mb-4">
          {{ searchQuery || statusFilter || courseFilter 
            ? 'Try adjusting your filters to see more classes.' 
            : 'Get started by scheduling your first live class.' }}
        </p>
        <button
          v-if="isTeacher && !searchQuery && !statusFilter && !courseFilter"
          @click="showScheduler = true"
          class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
        >
          Schedule Your First Class
        </button>
      </div>

      <!-- Classes Grid/List View -->
      <div v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="liveClass in filteredClasses"
            :key="liveClass.id"
            class="live-class-card bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
          >
            <div class="p-6">
              <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                  <h3 class="text-lg font-medium text-gray-900 mb-1">{{ liveClass.title }}</h3>
                  <p class="text-sm text-gray-600 line-clamp-2">{{ liveClass.description }}</p>
                </div>
                <div class="status-badge" :class="getStatusClasses(liveClass.status)">
                  {{ getStatusText(liveClass.status) }}
                </div>
              </div>

              <div class="space-y-2 text-sm text-gray-600 mb-4">
                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                  </svg>
                  {{ formatDateTime(liveClass.scheduled_at) }}
                </div>
                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                  </svg>
                  {{ liveClass.duration_minutes }} minutes
                </div>
                <div v-if="liveClass.zoom_meeting_id" class="flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
                  </svg>
                  Zoom meeting ready
                </div>
              </div>

              <div class="flex items-center justify-between">
                <div class="flex space-x-2">
                  <button
                    v-if="liveClass.status === 'live'"
                    @click="joinClass(liveClass)"
                    class="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition-colors"
                  >
                    Join Class
                  </button>
                  <button
                    v-else-if="liveClass.status === 'scheduled'"
                    @click="viewClass(liveClass)"
                    class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
                  >
                    View Details
                  </button>
                  <button
                    v-else-if="liveClass.status === 'completed' && liveClass.recording_url"
                    @click="watchRecording(liveClass)"
                    class="px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-md hover:bg-purple-700 transition-colors"
                  >
                    Watch Recording
                  </button>
                </div>
                <div v-if="isTeacher" class="flex space-x-1">
                  <button
                    @click="editClass(liveClass)"
                    class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="viewAttendance(liveClass)"
                    class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else-if="viewMode === 'list'" class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Class</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Schedule</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="liveClass in filteredClasses"
                  :key="liveClass.id"
                  class="hover:bg-gray-50"
                >
                  <td class="px-6 py-4">
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ liveClass.title }}</div>
                      <div class="text-sm text-gray-500 line-clamp-1">{{ liveClass.description }}</div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDateTime(liveClass.scheduled_at) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="status-badge" :class="getStatusClasses(liveClass.status)">
                      {{ getStatusText(liveClass.status) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ liveClass.duration_minutes }}m
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      v-if="liveClass.status === 'live'"
                      @click="joinClass(liveClass)"
                      class="text-green-600 hover:text-green-900"
                    >
                      Join
                    </button>
                    <button
                      @click="viewClass(liveClass)"
                      class="text-blue-600 hover:text-blue-900"
                    >
                      View
                    </button>
                    <button
                      v-if="isTeacher"
                      @click="editClass(liveClass)"
                      class="text-gray-600 hover:text-gray-900"
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <!-- Schedule Class Modal -->
    <div v-if="showScheduler" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
        <LiveClassScheduler
          :live-class="editingClass || undefined"
          @success="handleScheduleSuccess"
          @cancel="closeScheduler"
        />
      </div>
    </div>

    <!-- Class Details Modal -->
    <div v-if="selectedClass" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-10 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900">Class Details</h2>
          <button
            @click="selectedClass = null"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <LiveClassJoinInterface :live-class-id="selectedClass.id" />
      </div>
    </div>

    <!-- Attendance Dashboard Modal -->
    <div v-if="attendanceClass" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-5 mx-auto p-5 border w-full max-w-7xl shadow-lg rounded-md bg-white">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900">Attendance Dashboard</h2>
          <button
            @click="attendanceClass = null"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <AttendanceTrackingDashboard :live-class-id="attendanceClass.id" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
// import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useZoom } from '@/composables/useZoom'
import { useCourse } from '@/composables/useCourse'
import LiveClassScheduler from '@/components/live-classes/LiveClassScheduler.vue'
import LiveClassJoinInterface from '@/components/live-classes/LiveClassJoinInterface.vue'
import AttendanceTrackingDashboard from '@/components/live-classes/AttendanceTrackingDashboard.vue'
import type { LiveClass } from '@/types/api'

// const router = useRouter()
const { user } = useAuth()
const { courses } = useCourse()

const {
  liveClasses,
  // upcomingClasses,
  liveClasses_active,
  // completedClasses,
  fetchLiveClasses,
  joinZoomMeeting,
  isLoading,
  isConnected
} = useZoom()

// Local state
const viewMode = ref('grid')
const searchQuery = ref('')
const statusFilter = ref('')
const courseFilter = ref('')
const showScheduler = ref(false)
const selectedClass = ref<LiveClass | null>(null)
const attendanceClass = ref<LiveClass | null>(null)
const editingClass = ref<LiveClass | null>(null)

// Computed properties
const isTeacher = computed(() => user.value?.is_teacher || false)

const teacherCourses = computed(() => {
  if (!isTeacher.value) return []
  return courses.value.filter(course => course.instructor.id === user.value?.id)
})

const filteredClasses = computed(() => {
  let filtered = liveClasses.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(cls => 
      cls.title.toLowerCase().includes(query) ||
      cls.description?.toLowerCase().includes(query)
    )
  }

  // Status filter
  if (statusFilter.value) {
    filtered = filtered.filter(cls => cls.status === statusFilter.value)
  }

  // Course filter
  if (courseFilter.value) {
    filtered = filtered.filter(cls => cls.course === courseFilter.value)
  }

  // Sort by scheduled time
  return filtered.sort((a, b) => 
    new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime()
  )
})

// Methods
const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

const getStatusClasses = (status: string) => {
  switch (status) {
    case 'scheduled':
      return 'bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-medium'
    case 'live':
      return 'bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium'
    case 'completed':
      return 'bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs font-medium'
    case 'cancelled':
      return 'bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium'
    default:
      return 'bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs font-medium'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'scheduled':
      return 'Scheduled'
    case 'live':
      return 'Live'
    case 'completed':
      return 'Completed'
    case 'cancelled':
      return 'Cancelled'
    default:
      return 'Unknown'
  }
}

const joinClass = (liveClass: LiveClass) => {
  if (liveClass.join_url) {
    joinZoomMeeting(liveClass.join_url)
  }
}

const viewClass = (liveClass: LiveClass) => {
  selectedClass.value = liveClass
}

const editClass = (liveClass: LiveClass) => {
  editingClass.value = liveClass
  showScheduler.value = true
}

const viewAttendance = (liveClass: LiveClass) => {
  attendanceClass.value = liveClass
}

const watchRecording = (liveClass: LiveClass) => {
  if (liveClass.recording_url) {
    window.open(liveClass.recording_url, '_blank', 'noopener,noreferrer')
  }
}

const handleScheduleSuccess = (_liveClass: LiveClass) => {
  closeScheduler()
  fetchLiveClasses() // Refresh the list
}

const closeScheduler = () => {
  showScheduler.value = false
  editingClass.value = null
}

// Lifecycle
onMounted(() => {
  fetchLiveClasses()
})
</script>

<style scoped>
.live-classes-view {
  @apply min-h-screen bg-gray-50;
}

.status-badge {
  @apply inline-flex items-center px-2 py-1 rounded-full text-xs font-medium;
}

.live-class-card {
  @apply transition-all duration-200;
}

.live-class-card:hover {
  @apply transform -translate-y-1;
}

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>