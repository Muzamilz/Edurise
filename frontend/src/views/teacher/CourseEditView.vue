<template>
  <div class="course-edit-view">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">Edit Course</h1>
        <p class="page-subtitle" v-if="course">{{ course.title }}</p>
      </div>
      <div class="header-actions">
        <router-link 
          :to="`/courses/${courseId}`" 
          class="btn btn-outline"
          v-if="course"
        >
          View Course
        </router-link>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !course" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading course details...</p>
    </div>

    <!-- Course Form -->
    <CourseForm
      v-else-if="course"
      :course="course"
      :loading="saving"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />

    <!-- Error State -->
    <div v-else class="error-state">
      <h3>Course not found</h3>
      <p>The course you're trying to edit doesn't exist or you don't have permission to edit it.</p>
      <router-link to="/teacher/courses" class="btn btn-primary">
        Back to My Courses
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CourseForm from '../../components/courses/CourseForm.vue'
import { useCourseStore } from '../../stores/courses'
import type { Course } from '../../types/api'

const route = useRoute()
const router = useRouter()
const courseStore = useCourseStore()

const saving = ref(false)

// Computed
const courseId = computed(() => route.params.id as string)
const course = computed(() => courseStore.currentCourse)
const loading = computed(() => courseStore.loading)

const handleSubmit = async (courseData: Partial<Course>) => {
  if (!course.value) return

  try {
    saving.value = true
    await courseStore.updateCourse(course.value.id, courseData)
    
    // Show success message
    // Could redirect or stay on the same page
    
  } catch (error) {
    console.error('Failed to update course:', error)
    // Show error message to user
  } finally {
    saving.value = false
  }
}

const handleCancel = () => {
  router.push('/teacher/courses')
}

// Lifecycle
onMounted(async () => {
  if (courseId.value) {
    await courseStore.fetchCourse(courseId.value)
  }
})
</script>

<style scoped>
.course-edit-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  background: #F9FAFB;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
}

.header-content {
  text-align: left;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #6B7280;
  font-size: 1.125rem;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: #3B82F6;
  color: white;
}

.btn-primary:hover {
  background: #2563EB;
}

.btn-outline {
  background: transparent;
  color: #6B7280;
  border: 1px solid #D1D5DB;
}

.btn-outline:hover {
  background: #F9FAFB;
  border-color: #9CA3AF;
}

.loading-state, .error-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #F3F4F6;
  border-top: 4px solid #3B82F6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 8px;
}

.error-state p {
  color: #6B7280;
  margin-bottom: 24px;
}

/* Responsive */
@media (max-width: 768px) {
  .course-edit-view {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 20px;
    align-items: stretch;
  }
  
  .header-content {
    text-align: center;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
}
</style>