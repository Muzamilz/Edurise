import { ref, onUnmounted } from 'vue'
import * as THREE from 'three'
import type { ProgressVisualizationData } from '../types/assignments'

export const useThreeJS = () => {
  const scene = ref<THREE.Scene | null>(null)
  const camera = ref<THREE.PerspectiveCamera | null>(null)
  const renderer = ref<THREE.WebGLRenderer | null>(null)
  const animationId = ref<number | null>(null)

  // Initialize Three.js scene
  const initScene = (container: HTMLElement) => {
    // Create scene
    scene.value = new THREE.Scene()
    scene.value.background = new THREE.Color(0xf8fafc)

    // Create camera
    const width = container.clientWidth
    const height = container.clientHeight
    camera.value = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
    camera.value.position.set(0, 5, 10)

    // Create renderer
    renderer.value = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.value.setSize(width, height)
    renderer.value.shadowMap.enabled = true
    renderer.value.shadowMap.type = THREE.PCFSoftShadowMap

    // Add renderer to container
    container.appendChild(renderer.value.domElement)

    // Add lights
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6)
    scene.value.add(ambientLight)

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
    directionalLight.position.set(10, 10, 5)
    directionalLight.castShadow = true
    scene.value.add(directionalLight)

    // Start animation loop
    animate()

    // Handle window resize
    const handleResize = () => {
      if (camera.value && renderer.value) {
        const newWidth = container.clientWidth
        const newHeight = container.clientHeight
        
        camera.value.aspect = newWidth / newHeight
        camera.value.updateProjectionMatrix()
        renderer.value.setSize(newWidth, newHeight)
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }

  // Animation loop
  const animate = () => {
    if (!scene.value || !camera.value || !renderer.value) return

    animationId.value = requestAnimationFrame(animate)

    // Rotate camera around the scene
    const time = Date.now() * 0.0005
    camera.value.position.x = Math.cos(time) * 10
    camera.value.position.z = Math.sin(time) * 10
    camera.value.lookAt(0, 0, 0)

    renderer.value.render(scene.value, camera.value)
  }

  // Create progress visualization
  const createProgressVisualization = (progressData?: ProgressVisualizationData) => {
    if (!scene.value || !progressData) return

    // Clear existing objects
    while (scene.value.children.length > 2) { // Keep lights
      scene.value.remove(scene.value.children[2])
    }

    // Create progress spheres
    const sphereGeometry = new THREE.SphereGeometry(1, 32, 32)
    
    // Overall progress sphere (center)
    const overallMaterial = new THREE.MeshPhongMaterial({ 
      color: 0x3b82f6,
      transparent: true,
      opacity: progressData.overall_progress / 100
    })
    const overallSphere = new THREE.Mesh(sphereGeometry, overallMaterial)
    overallSphere.position.set(0, 0, 0)
    overallSphere.castShadow = true
    scene.value.add(overallSphere)

    // Modules progress sphere
    const modulesMaterial = new THREE.MeshPhongMaterial({ 
      color: 0x10b981,
      transparent: true,
      opacity: progressData.modules_progress / 100
    })
    const modulesSphere = new THREE.Mesh(sphereGeometry, modulesMaterial)
    modulesSphere.position.set(-3, 0, 0)
    modulesSphere.scale.setScalar(0.8)
    modulesSphere.castShadow = true
    scene.value.add(modulesSphere)

    // Assignments progress sphere
    const assignmentsMaterial = new THREE.MeshPhongMaterial({ 
      color: 0x8b5cf6,
      transparent: true,
      opacity: progressData.assignments_progress / 100
    })
    const assignmentsSphere = new THREE.Mesh(sphereGeometry, assignmentsMaterial)
    assignmentsSphere.position.set(3, 0, 0)
    assignmentsSphere.scale.setScalar(0.8)
    assignmentsSphere.castShadow = true
    scene.value.add(assignmentsSphere)

    // Attendance progress sphere
    const attendanceMaterial = new THREE.MeshPhongMaterial({ 
      color: 0xf59e0b,
      transparent: true,
      opacity: progressData.attendance_progress / 100
    })
    const attendanceSphere = new THREE.Mesh(sphereGeometry, attendanceMaterial)
    attendanceSphere.position.set(0, 3, 0)
    attendanceSphere.scale.setScalar(0.8)
    attendanceSphere.castShadow = true
    scene.value.add(attendanceSphere)

    // Create connecting lines
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x6b7280, opacity: 0.5, transparent: true })
    
    // Connect center to modules
    const moduleLineGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(-3, 0, 0)
    ])
    const moduleLine = new THREE.Line(moduleLineGeometry, lineMaterial)
    scene.value.add(moduleLine)

    // Connect center to assignments
    const assignmentLineGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(3, 0, 0)
    ])
    const assignmentLine = new THREE.Line(assignmentLineGeometry, lineMaterial)
    scene.value.add(assignmentLine)

    // Connect center to attendance
    const attendanceLineGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(0, 3, 0)
    ])
    const attendanceLine = new THREE.Line(attendanceLineGeometry, lineMaterial)
    scene.value.add(attendanceLine)

    // Add ground plane
    const planeGeometry = new THREE.PlaneGeometry(20, 20)
    const planeMaterial = new THREE.MeshPhongMaterial({ 
      color: 0xffffff,
      transparent: true,
      opacity: 0.1
    })
    const plane = new THREE.Mesh(planeGeometry, planeMaterial)
    plane.rotation.x = -Math.PI / 2
    plane.position.y = -2
    plane.receiveShadow = true
    scene.value.add(plane)
  }

  // Create assignment scores visualization
  const createAssignmentScoresVisualization = (scores: Array<{
    assignment_title: string
    score: number
    max_score: number
    percentage: number
  }>) => {
    if (!scene.value) return

    // Clear existing objects
    while (scene.value.children.length > 2) { // Keep lights
      scene.value.remove(scene.value.children[2])
    }

    scores.forEach((score, index) => {
      // Create bar for each assignment
      const barHeight = (score.percentage / 100) * 5
      const barGeometry = new THREE.BoxGeometry(0.5, barHeight, 0.5)
      
      // Color based on score
      let color = 0xef4444 // red
      if (score.percentage >= 90) color = 0x10b981 // green
      else if (score.percentage >= 80) color = 0x3b82f6 // blue
      else if (score.percentage >= 70) color = 0xf59e0b // yellow
      else if (score.percentage >= 60) color = 0xf97316 // orange

      const barMaterial = new THREE.MeshPhongMaterial({ color })
      const bar = new THREE.Mesh(barGeometry, barMaterial)
      
      // Position bars in a row
      bar.position.set((index - scores.length / 2) * 1.5, barHeight / 2, 0)
      bar.castShadow = true
      scene.value!.add(bar)

      // Add text label (simplified - in real implementation you'd use TextGeometry)
      const labelGeometry = new THREE.PlaneGeometry(1, 0.2)
      const labelMaterial = new THREE.MeshBasicMaterial({ 
        color: 0x374151,
        transparent: true,
        opacity: 0.8
      })
      const label = new THREE.Mesh(labelGeometry, labelMaterial)
      label.position.set((index - scores.length / 2) * 1.5, -1, 0)
      scene.value!.add(label)
    })

    // Add ground plane
    const planeGeometry = new THREE.PlaneGeometry(20, 20)
    const planeMaterial = new THREE.MeshPhongMaterial({ 
      color: 0xffffff,
      transparent: true,
      opacity: 0.1
    })
    const plane = new THREE.Mesh(planeGeometry, planeMaterial)
    plane.rotation.x = -Math.PI / 2
    plane.position.y = -2
    plane.receiveShadow = true
    scene.value.add(plane)
  }

  // Cleanup function
  const cleanup = () => {
    if (animationId.value) {
      cancelAnimationFrame(animationId.value)
      animationId.value = null
    }

    if (renderer.value) {
      renderer.value.dispose()
      renderer.value = null
    }

    scene.value = null
    camera.value = null
  }

  // Cleanup on unmount
  onUnmounted(() => {
    cleanup()
  })

  return {
    scene,
    camera,
    renderer,
    initScene,
    createProgressVisualization,
    createAssignmentScoresVisualization,
    cleanup
  }
}

export default useThreeJS