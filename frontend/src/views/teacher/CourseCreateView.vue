<template>
  <div class="course-create-view">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">Create New Course</h1>
        <p class="page-subtitle">Share your knowledge and start teaching</p>
      </div>
    </div>

    <CourseForm
      :loading="loading"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import CourseForm from '../../components/courses/CourseForm.vue'
import { useCourseStore } from '../../stores/courses'
import type { Course } from '../../types/api'

const router = useRouter()
const courseStore = useCourseStore()

const loading = ref(false)

const handleSubmit = async (courseData: Partial<Course>) => {
  try {
    loading.value = true
    const newCourse = await courseStore.createCourse(courseData)
    
    // Redirect to the new course edit page or course detail
    router.push(`/teacher/courses/${newCourse.id}/edit`)
    
  } catch (error) {
    console.error('Failed to create course:', error)
    // Show error message to user
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  router.push('/teacher/courses')
}
</script>

<style scoped>
.course-create-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  background: #F9FAFB;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
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

/* Responsive */
@media (max-width: 768px) {
  .course-create-view {
    padding: 16px;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
}
</style>