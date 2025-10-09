<template>
  <div class="engagement-visualization">
    <div class="visualization-header mb-6">
      <h3 class="text-lg font-medium text-gray-900 mb-2">Class Engagement Visualization</h3>
      <div class="flex items-center space-x-4">
        <select
          v-model="visualizationType"
          @change="updateVisualization"
          class="text-sm border border-gray-300 rounded-md px-3 py-1"
        >
          <option value="attendance">Attendance Flow</option>
          <option value="participation">Participation Levels</option>
          <option value="engagement">Engagement Timeline</option>
          <option value="overview">Class Overview</option>
        </select>
        <button
          @click="toggleAnimation"
          class="px-3 py-1 text-sm text-blue-600 hover:text-blue-800"
        >
          {{ isAnimating ? 'Pause' : 'Play' }}
        </button>
        <button
          @click="resetView"
          class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
        >
          Reset View
        </button>
      </div>
    </div>

    <!-- Three.js Canvas Container -->
    <div class="visualization-container relative">
      <div
        ref="canvasContainer"
        class="w-full h-96 bg-gray-900 rounded-lg overflow-hidden"
        @mousedown="onMouseDown"
        @mousemove="onMouseMove"
        @mouseup="onMouseUp"
        @wheel="onWheel"
      ></div>

      <!-- Loading Overlay -->
      <div
        v-if="isLoading"
        class="absolute inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center rounded-lg"
      >
        <div class="text-white text-center">
          <svg class="animate-spin h-8 w-8 mx-auto mb-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="text-sm">Loading visualization...</p>
        </div>
      </div>

      <!-- Controls Overlay -->
      <div class="absolute top-4 right-4 bg-black bg-opacity-50 rounded-lg p-3 text-white text-xs">
        <div class="space-y-1">
          <div>Mouse: Rotate view</div>
          <div>Scroll: Zoom in/out</div>
          <div>Click: Select student</div>
        </div>
      </div>

      <!-- Legend -->
      <div class="absolute bottom-4 left-4 bg-black bg-opacity-50 rounded-lg p-3 text-white text-xs">
        <div class="space-y-1">
          <div class="flex items-center">
            <div class="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span>Present</span>
          </div>
          <div class="flex items-center">
            <div class="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
            <span>Late</span>
          </div>
          <div class="flex items-center">
            <div class="w-3 h-3 bg-orange-500 rounded-full mr-2"></div>
            <span>Partial</span>
          </div>
          <div class="flex items-center">
            <div class="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
            <span>Absent</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Visualization Info Panel -->
    <div v-if="selectedStudent" class="mt-4 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h4 class="font-medium text-gray-900 mb-2">Student Details</h4>
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span class="text-gray-600">Name:</span>
          <span class="ml-2 font-medium">{{ selectedStudent.name }}</span>
        </div>
        <div>
          <span class="text-gray-600">Status:</span>
          <span class="ml-2 font-medium" :class="getStatusColor(selectedStudent.status)">
            {{ selectedStudent.status }}
          </span>
        </div>
        <div>
          <span class="text-gray-600">Join Time:</span>
          <span class="ml-2 font-medium">{{ selectedStudent.joinTime }}</span>
        </div>
        <div>
          <span class="text-gray-600">Duration:</span>
          <span class="ml-2 font-medium">{{ selectedStudent.duration }}m</span>
        </div>
        <div>
          <span class="text-gray-600">Participation:</span>
          <span class="ml-2 font-medium">{{ selectedStudent.participation }}%</span>
        </div>
        <div>
          <span class="text-gray-600">Questions:</span>
          <span class="ml-2 font-medium">{{ selectedStudent.questions }}</span>
        </div>
      </div>
    </div>

    <!-- Metrics Summary -->
    <div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h4 class="font-medium text-gray-900 mb-2">Attendance Flow</h4>
        <div class="text-sm text-gray-600">
          <p>Peak join time: {{ peakJoinTime }}</p>
          <p>Average join delay: {{ averageJoinDelay }}m</p>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h4 class="font-medium text-gray-900 mb-2">Participation Trends</h4>
        <div class="text-sm text-gray-600">
          <p>Most active period: {{ mostActiveTime }}</p>
          <p>Engagement drop-off: {{ engagementDropOff }}%</p>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h4 class="font-medium text-gray-900 mb-2">Class Dynamics</h4>
        <div class="text-sm text-gray-600">
          <p>Interaction clusters: {{ interactionClusters }}</p>
          <p>Question frequency: {{ questionFrequency }}/min</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as THREE from 'three'
import { useZoom } from '@/composables/useZoom'
import type { ClassAttendance, EngagementMetrics } from '@/types/api'

interface Props {
  liveClassId: string
  attendanceData: ClassAttendance[]
  engagementMetrics: EngagementMetrics | null
}

const props = defineProps<Props>()

// Refs
const canvasContainer = ref<HTMLDivElement>()
const isLoading = ref(true)
const isAnimating = ref(true)
const visualizationType = ref('attendance')
const selectedStudent = ref<any>(null)

// Three.js objects
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animationId: number
let studentSpheres: THREE.Mesh[] = []
let connectionLines: THREE.Line[] = []

// Mouse interaction
const mouse = ref({ x: 0, y: 0 })
const isMouseDown = ref(false)
const raycaster = new THREE.Raycaster()
const mouseVector = new THREE.Vector2()

// Computed metrics
const peakJoinTime = ref('10:05 AM')
const averageJoinDelay = ref('3.2')
const mostActiveTime = ref('10:15-10:30')
const engagementDropOff = ref('15')
const interactionClusters = ref('3')
const questionFrequency = ref('2.1')

// Initialize Three.js scene
const initThreeJS = () => {
  if (!canvasContainer.value) return

  // Scene setup
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x1a1a1a)

  // Camera setup
  camera = new THREE.PerspectiveCamera(
    75,
    canvasContainer.value.clientWidth / canvasContainer.value.clientHeight,
    0.1,
    1000
  )
  camera.position.set(0, 5, 10)
  camera.lookAt(0, 0, 0)

  // Renderer setup
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight)
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  canvasContainer.value.appendChild(renderer.domElement)

  // Lighting
  const ambientLight = new THREE.AmbientLight(0x404040, 0.6)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(10, 10, 5)
  directionalLight.castShadow = true
  scene.add(directionalLight)

  // Add grid helper
  const gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x222222)
  scene.add(gridHelper)

  isLoading.value = false
}

// Create student visualization based on attendance data
const createStudentVisualization = () => {
  // Clear existing objects
  studentSpheres.forEach(sphere => scene.remove(sphere))
  connectionLines.forEach(line => scene.remove(line))
  studentSpheres = []
  connectionLines = []

  if (!props.attendanceData.length) return

  const studentCount = props.attendanceData.length
  const radius = Math.max(3, studentCount * 0.3)

  props.attendanceData.forEach((attendance, index) => {
    // Position students in a circle
    const angle = (index / studentCount) * Math.PI * 2
    const x = Math.cos(angle) * radius
    const z = Math.sin(angle) * radius
    const y = getStudentHeight(attendance)

    // Create student sphere
    const geometry = new THREE.SphereGeometry(0.2, 16, 16)
    const material = new THREE.MeshLambertMaterial({
      color: getStatusColor3D(attendance.status),
      transparent: true,
      opacity: getStudentOpacity(attendance)
    })

    const sphere = new THREE.Mesh(geometry, material)
    sphere.position.set(x, y, z)
    sphere.castShadow = true
    sphere.userData = {
      studentId: attendance.student.id,
      attendance: attendance
    }

    scene.add(sphere)
    studentSpheres.push(sphere)

    // Add participation indicator
    if (attendance.participation_score > 0) {
      const participationHeight = (attendance.participation_score / 100) * 2
      const participationGeometry = new THREE.CylinderGeometry(0.05, 0.05, participationHeight, 8)
      const participationMaterial = new THREE.MeshLambertMaterial({
        color: 0x00ff88,
        transparent: true,
        opacity: 0.7
      })
      const participationCylinder = new THREE.Mesh(participationGeometry, participationMaterial)
      participationCylinder.position.set(x, y + participationHeight / 2, z)
      scene.add(participationCylinder)
    }

    // Add connection lines for engagement visualization
    if (visualizationType.value === 'engagement' && index > 0) {
      const prevStudent = studentSpheres[index - 1]
      const points = [
        new THREE.Vector3(prevStudent.position.x, prevStudent.position.y, prevStudent.position.z),
        new THREE.Vector3(x, y, z)
      ]
      const lineGeometry = new THREE.BufferGeometry().setFromPoints(points)
      const lineMaterial = new THREE.LineBasicMaterial({
        color: 0x666666,
        transparent: true,
        opacity: 0.3
      })
      const line = new THREE.Line(lineGeometry, lineMaterial)
      scene.add(line)
      connectionLines.push(line)
    }
  })

  // Add center instructor position
  const instructorGeometry = new THREE.ConeGeometry(0.3, 0.6, 8)
  const instructorMaterial = new THREE.MeshLambertMaterial({ color: 0x4f46e5 })
  const instructor = new THREE.Mesh(instructorGeometry, instructorMaterial)
  instructor.position.set(0, 0.3, 0)
  scene.add(instructor)
}

// Get student height based on engagement
const getStudentHeight = (attendance: ClassAttendance) => {
  const baseHeight = 0.2
  const engagementMultiplier = attendance.participation_score / 100
  return baseHeight + engagementMultiplier * 1.5
}

// Get student opacity based on duration
const getStudentOpacity = (attendance: ClassAttendance) => {
  if (attendance.status === 'absent') return 0.3
  const durationRatio = Math.min(1, attendance.duration_minutes / 60) // Assuming 60min class
  return 0.5 + durationRatio * 0.5
}

// Get 3D color based on status
const getStatusColor3D = (status: string) => {
  switch (status) {
    case 'present':
      return 0x10b981 // green
    case 'late':
      return 0xf59e0b // yellow
    case 'partial':
      return 0xf97316 // orange
    case 'absent':
      return 0xef4444 // red
    default:
      return 0x6b7280 // gray
  }
}

// Get status color for UI
const getStatusColor = (status: string) => {
  switch (status) {
    case 'present':
      return 'text-green-600'
    case 'late':
      return 'text-yellow-600'
    case 'partial':
      return 'text-orange-600'
    case 'absent':
      return 'text-red-600'
    default:
      return 'text-gray-600'
  }
}

// Animation loop
const animate = () => {
  if (!isAnimating.value) return

  animationId = requestAnimationFrame(animate)

  // Rotate camera around the scene
  const time = Date.now() * 0.0005
  camera.position.x = Math.cos(time) * 10
  camera.position.z = Math.sin(time) * 10
  camera.lookAt(0, 0, 0)

  // Animate student spheres
  studentSpheres.forEach((sphere, index) => {
    const attendance = sphere.userData.attendance
    if (attendance.status === 'present') {
      sphere.position.y = getStudentHeight(attendance) + Math.sin(time * 2 + index) * 0.1
    }
  })

  renderer.render(scene, camera)
}

// Mouse interaction handlers
const onMouseDown = (event: MouseEvent) => {
  isMouseDown.value = true
  mouse.value.x = event.clientX
  mouse.value.y = event.clientY
}

const onMouseMove = (event: MouseEvent) => {
  if (!isMouseDown.value) return

  const deltaX = event.clientX - mouse.value.x
  const deltaY = event.clientY - mouse.value.y

  camera.position.x += deltaX * 0.01
  camera.position.y += deltaY * 0.01

  mouse.value.x = event.clientX
  mouse.value.y = event.clientY
}

const onMouseUp = (event: MouseEvent) => {
  if (!isMouseDown.value) return
  isMouseDown.value = false

  // Check for student selection
  const rect = canvasContainer.value!.getBoundingClientRect()
  mouseVector.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouseVector.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  raycaster.setFromCamera(mouseVector, camera)
  const intersects = raycaster.intersectObjects(studentSpheres)

  if (intersects.length > 0) {
    const selectedSphere = intersects[0].object as THREE.Mesh
    const attendance = selectedSphere.userData.attendance
    
    selectedStudent.value = {
      name: `${attendance.student.first_name} ${attendance.student.last_name}`,
      status: attendance.status,
      joinTime: attendance.join_time ? new Date(attendance.join_time).toLocaleTimeString() : '-',
      duration: attendance.duration_minutes,
      participation: attendance.participation_score,
      questions: attendance.questions_asked
    }
  } else {
    selectedStudent.value = null
  }
}

const onWheel = (event: WheelEvent) => {
  event.preventDefault()
  const scale = event.deltaY > 0 ? 1.1 : 0.9
  camera.position.multiplyScalar(scale)
}

// Control methods
const updateVisualization = () => {
  createStudentVisualization()
}

const toggleAnimation = () => {
  isAnimating.value = !isAnimating.value
  if (isAnimating.value) {
    animate()
  } else {
    cancelAnimationFrame(animationId)
  }
}

const resetView = () => {
  camera.position.set(0, 5, 10)
  camera.lookAt(0, 0, 0)
  selectedStudent.value = null
}

// Handle window resize
const onWindowResize = () => {
  if (!canvasContainer.value) return

  camera.aspect = canvasContainer.value.clientWidth / canvasContainer.value.clientHeight
  camera.updateProjectionMatrix()
  renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight)
}

// Watchers
watch(() => props.attendanceData, () => {
  if (scene) {
    createStudentVisualization()
  }
}, { deep: true })

watch(() => props.engagementMetrics, () => {
  // Update computed metrics based on new data
  if (props.engagementMetrics) {
    // Update visualization metrics here
  }
}, { deep: true })

// Lifecycle
onMounted(async () => {
  await nextTick()
  initThreeJS()
  createStudentVisualization()
  animate()
  
  window.addEventListener('resize', onWindowResize)
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  if (renderer) {
    renderer.dispose()
  }
  window.removeEventListener('resize', onWindowResize)
})
</script>

<style scoped>
.engagement-visualization {
  @apply w-full;
}

.visualization-container {
  @apply relative;
}

.visualization-container canvas {
  @apply w-full h-full;
}
</style>