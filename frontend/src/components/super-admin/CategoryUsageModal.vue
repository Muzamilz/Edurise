<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Category Usage: {{ category?.name }}</h3>
        <button @click="$emit('close')" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <div v-if="loading" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading usage data...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <i class="fas fa-exclamation-triangle"></i>
          <p>{{ error }}</p>
        </div>

        <div v-else class="usage-content">
          <!-- Usage Summary -->
          <div class="usage-summary">
            <div class="summary-grid">
              <div class="summary-item">
                <div class="summary-icon courses">
                  <i class="fas fa-book"></i>
                </div>
                <div class="summary-details">
                  <h4>{{ usageData.total_courses }}</h4>
                  <p>Courses</p>
                </div>
              </div>
              <div class="summary-item">
                <div class="summary-icon organizations">
                  <i class="fas fa-building"></i>
                </div>
                <div class="summary-details">
                  <h4>{{ usageData.organizations_count }}</h4>
                  <p>Organizations</p>
                </div>
              </div>
              <div class="summary-item">
                <div class="summary-icon subcategories">
                  <i class="fas fa-sitemap"></i>
                </div>
                <div class="summary-details">
                  <h4>{{ usageData.subcategories_count }}</h4>
                  <p>Subcategories</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Organizations Using This Category -->
          <div v-if="usageData.organizations?.length" class="usage-section">
            <h4>Organizations Using This Category</h4>
            <div class="organizations-list">
              <div
                v-for="org in usageData.organizations"
                :key="org.id"
                class="organization-item"
              >
                <div class="org-info">
                  <h5>{{ org.name }}</h5>
                  <p>{{ org.subdomain }}.edurise.com</p>
                </div>
                <div class="org-stats">
                  <span class="course-count">{{ org.course_count }} courses</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Courses -->
          <div v-if="usageData.recent_courses?.length" class="usage-section">
            <h4>Recent Courses in This Category</h4>
            <div class="courses-list">
              <div
                v-for="course in usageData.recent_courses"
                :key="course.id"
                class="course-item"
              >
                <div class="course-info">
                  <h5>{{ course.title }}</h5>
                  <p>{{ course.organization_name }}</p>
                  <small>Created {{ formatDate(course.created_at) }}</small>
                </div>
                <div class="course-stats">
                  <span class="enrollment-count">
                    {{ course.enrollment_count }} enrolled
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Subcategories -->
          <div v-if="usageData.subcategories?.length" class="usage-section">
            <h4>Subcategories</h4>
            <div class="subcategories-list">
              <div
                v-for="subcategory in usageData.subcategories"
                :key="subcategory.id"
                class="subcategory-item"
              >
                <div class="subcategory-info">
                  <h5>{{ subcategory.name }}</h5>
                  <p v-if="subcategory.description">{{ subcategory.description }}</p>
                </div>
                <div class="subcategory-stats">
                  <span class="course-count">{{ subcategory.course_count }} courses</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="!hasUsageData" class="empty-state">
            <i class="fas fa-inbox"></i>
            <h4>No Usage Data</h4>
            <p>This category is not currently being used by any organizations or courses.</p>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="$emit('close')" class="btn btn-outline">
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { CourseCategory as Category } from '@/types/api'

interface UsageData {
  total_courses: number
  organizations_count: number
  subcategories_count: number
  organizations?: Array<{
    id: string
    name: string
    subdomain: string
    course_count: number
  }>
  recent_courses?: Array<{
    id: string
    title: string
    organization_name: string
    created_at: string
    enrollment_count: number
  }>
  subcategories?: Array<{
    id: string
    name: string
    description?: string
    course_count: number
  }>
}

interface Props {
  show: boolean
  category?: Category | null
}

interface Emits {
  (e: 'close'): void
}

const props = withDefaults(defineProps<Props>(), {
  category: null
})

const emit = defineEmits<Emits>()

const loading = ref(false)
const error = ref<string | null>(null)
const usageData = ref<UsageData>({
  total_courses: 0,
  organizations_count: 0,
  subcategories_count: 0
})

const hasUsageData = computed(() => {
  return usageData.value.total_courses > 0 || 
         usageData.value.organizations_count > 0 || 
         usageData.value.subcategories_count > 0
})

const handleOverlayClick = () => {
  emit('close')
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const fetchUsageData = async () => {
  if (!props.category) return

  loading.value = true
  error.value = null

  try {
    // Mock data for now - replace with actual API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    usageData.value = {
      total_courses: 15,
      organizations_count: 3,
      subcategories_count: 5,
      organizations: [
        {
          id: '1',
          name: 'Tech University',
          subdomain: 'techuni',
          course_count: 8
        },
        {
          id: '2',
          name: 'Business Academy',
          subdomain: 'bizacademy',
          course_count: 5
        },
        {
          id: '3',
          name: 'Creative Institute',
          subdomain: 'creative',
          course_count: 2
        }
      ],
      recent_courses: [
        {
          id: '1',
          title: 'Advanced JavaScript Programming',
          organization_name: 'Tech University',
          created_at: '2024-01-15T10:00:00Z',
          enrollment_count: 45
        },
        {
          id: '2',
          title: 'React Development Fundamentals',
          organization_name: 'Tech University',
          created_at: '2024-01-10T14:30:00Z',
          enrollment_count: 32
        },
        {
          id: '3',
          title: 'Business Strategy Essentials',
          organization_name: 'Business Academy',
          created_at: '2024-01-08T09:15:00Z',
          enrollment_count: 28
        }
      ],
      subcategories: [
        {
          id: '1',
          name: 'Frontend Development',
          description: 'Client-side web development technologies',
          course_count: 8
        },
        {
          id: '2',
          name: 'Backend Development',
          description: 'Server-side programming and databases',
          course_count: 5
        },
        {
          id: '3',
          name: 'Mobile Development',
          description: 'iOS and Android app development',
          course_count: 2
        }
      ]
    }
  } catch (err) {
    error.value = 'Failed to load usage data'
    console.error('Error fetching usage data:', err)
  } finally {
    loading.value = false
  }
}

// Watch for category changes
watch(() => props.category, (newCategory) => {
  if (newCategory && props.show) {
    fetchUsageData()
  }
}, { immediate: true })

// Watch for modal show/hide
watch(() => props.show, (show) => {
  if (show && props.category) {
    fetchUsageData()
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
  min-height: 200px;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
}

.loading-state i,
.error-state i,
.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #6b7280;
}

.loading-state i {
  color: #3b82f6;
}

.error-state i {
  color: #dc2626;
}

.usage-summary {
  margin-bottom: 2rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.summary-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  margin-right: 1rem;
  font-size: 1.25rem;
  color: white;
}

.summary-icon.courses {
  background: #3b82f6;
}

.summary-icon.organizations {
  background: #10b981;
}

.summary-icon.subcategories {
  background: #8b5cf6;
}

.summary-details h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.summary-details p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.usage-section {
  margin-bottom: 2rem;
}

.usage-section h4 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.organizations-list,
.courses-list,
.subcategories-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.organization-item,
.course-item,
.subcategory-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.org-info h5,
.course-info h5,
.subcategory-info h5 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.org-info p,
.course-info p,
.subcategory-info p {
  margin: 0 0 0.25rem 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.course-info small {
  color: #9ca3af;
  font-size: 0.75rem;
}

.org-stats,
.course-stats,
.subcategory-stats {
  text-align: right;
}

.course-count,
.enrollment-count {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #f3f4f6;
  color: #374151;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline {
  background: transparent;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-outline:hover {
  background: #f9fafb;
}
</style>