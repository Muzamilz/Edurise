<template>
  <div class="enhanced-courses-view">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="title-word">Discover</span>
          <span class="title-word">Amazing</span>
          <span class="title-word">Courses</span>
        </h1>
        <p class="hero-subtitle">
          Learn new skills from expert instructors and advance your career with our comprehensive learning platform
        </p>
        <div class="hero-search">
          <div class="search-container">
            <input
              v-model="searchQuery"
              @keydown.enter="performSearch"
              @input="handleSearchInput"
              type="text"
              placeholder="Search courses, instructors, or topics..."
              class="search-input"
            />
            <button @click="performSearch" class="search-btn" :disabled="!searchQuery.trim()">
              <span v-if="!searchLoading" class="search-icon">🔍</span>
              <span v-else class="search-spinner">⏳</span>
              Search
            </button>
          </div>
        </div>
        
        <!-- Stats -->
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-number">10K+</span>
            <span class="stat-label">Students</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">500+</span>
            <span class="stat-label">Courses</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">50+</span>
            <span class="stat-label">Instructors</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Platform Courses Section -->
    <section class="main-courses-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">
            <span class="platform-badge">🏛️ Platform</span>
            Main Courses
          </h2>
          <p class="section-description">
            Core courses available across all organizations
          </p>
        </div>

        <!-- Featured Main Courses -->
        <div v-if="featuredMainCourses && featuredMainCourses.length > 0" class="featured-subsection">
          <h3 class="subsection-title">Featured</h3>
          <div class="featured-grid">
            <CourseCard
              v-for="course in featuredMainCourses"
              :key="course.id"
              :course="course"
              :is-enrolled="isEnrolledInCourse(course.id)"
              @click="goToCourse"
              @enroll="handleEnroll"
              @continue="handleContinue"
            />
          </div>
        </div>

        <!-- All Main Courses -->
        <div class="courses-grid">
          <CourseCard
            v-for="course in paginatedMainCourses"
            :key="course.id"
            :course="course"
            :is-enrolled="isEnrolledInCourse(course.id)"
            :loading="enrollingCourseId === course.id"
            @click="goToCourse"
            @enroll="handleEnroll"
            @continue="handleContinue"
          />
        </div>

        <!-- Load More Main Courses -->
        <div v-if="hasMoreMainCourses" class="load-more-section">
          <button @click="loadMoreMainCourses" class="load-more-btn" :disabled="loadingMoreMain">
            <span v-if="!loadingMoreMain">Load More Main Courses</span>
            <span v-else>Loading...</span>
          </button>
        </div>
      </div>
    </section>

    <!-- Organization Courses Section -->
    <section class="org-courses-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">
            <span class="org-badge">🏢</span>
            Organization Courses
          </h2>
          <p class="section-description">
            Specialized courses from different organizations
          </p>
        </div>

        <!-- Organization Filters -->
        <div class="org-filters">
          <button
            v-for="org in availableOrganizations"
            :key="org.id"
            @click="toggleOrganization(org.id)"
            class="org-filter-btn"
            :class="{ active: selectedOrganizations.includes(org.id) }"
          >
            <img v-if="org.logo" :src="org.logo" :alt="org.name" class="org-logo" />
            <span class="org-name">{{ org.name }}</span>
            <span class="org-course-count">({{ org.course_count }})</span>
          </button>
        </div>

        <!-- Organization Course Groups -->
        <div v-for="org in filteredOrganizations" :key="org.id" class="org-group">
          <div class="org-header">
            <div class="org-info">
              <img v-if="org.logo" :src="org.logo" :alt="org.name" class="org-header-logo" />
              <div class="org-details">
                <h3 class="org-title">{{ org.name }}</h3>
                <p class="org-description">{{ org.description || 'Specialized courses and training programs' }}</p>
                <div class="org-stats">
                  <span class="stat">{{ org.course_count }} courses</span>
                  <span class="stat" v-if="org.avg_rating">{{ org.avg_rating.toFixed(1) }}★ average</span>
                  <span class="stat">{{ org.total_students }} students</span>
                </div>
              </div>
            </div>
            <button @click="toggleOrgExpansion(org.id)" class="expand-btn">
              <span v-if="expandedOrgs.includes(org.id)">Show Less</span>
              <span v-else>Show All ({{ org.course_count }})</span>
            </button>
          </div>

          <!-- Organization Courses -->
          <div class="org-courses">
            <div v-if="orgCoursesLoading[org.id]" class="loading-state">
              <div class="loading-spinner"></div>
              <p>Loading {{ org.name }} courses...</p>
            </div>
            
            <div v-else-if="orgCoursesError[org.id]" class="error-state">
              <div class="error-icon">⚠️</div>
              <p>Failed to load courses from {{ org.name }}</p>
              <button @click="retryOrgCourses(org.id)" class="retry-btn">Try Again</button>
            </div>
            
            <div v-else class="courses-grid">
              <CourseCard
                v-for="course in getDisplayedOrgCourses(org.id)"
                :key="course.id"
                :course="course"
                :is-enrolled="isEnrolledInCourse(course.id)"
                :loading="enrollingCourseId === course.id"
                @click="goToCourse"
                @enroll="handleEnroll"
                @continue="handleContinue"
              />
            </div>

            <!-- Load More for Organization -->
            <div v-if="hasMoreOrgCourses(org.id)" class="load-more-section">
              <button 
                @click="loadMoreOrgCourses(org.id)" 
                class="load-more-btn secondary"
                :disabled="loadingMoreOrg[org.id]"
              >
                <span v-if="!loadingMoreOrg[org.id]">Load More from {{ org.name }}</span>
                <span v-else>Loading...</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="filteredOrganizations.length === 0" class="empty-state">
          <div class="empty-icon">🏢</div>
          <h3>No organization courses found</h3>
          <p>Try adjusting your organization filters</p>
        </div>
      </div>
    </section>

    <!-- Payment Modal -->
    <PaymentModal
      v-if="selectedCourse && selectedCourse.price !== undefined"
      :show="showPaymentModal"
      :course="{
        id: selectedCourse.id,
        title: selectedCourse.title,
        price: selectedCourse.price || 0,
        thumbnail: selectedCourse.thumbnail,
        instructor: {
          first_name: selectedCourse.instructor.first_name,
          last_name: selectedCourse.instructor.last_name
        }
      }"
      @close="handlePaymentClose"
      @success="handlePaymentSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import CourseCard from '../../components/courses/CourseCard.vue'
import PaymentModal from '../../components/payments/PaymentModal.vue'
import { useApiData } from '../../composables/useApiData'
import { useErrorHandler } from '../../composables/useErrorHandler'
import { useAuth } from '../../composables/useAuth'
import { useEnrollment } from '../../composables/useEnrollment'
import { CachePresets } from '../../utils/apiCache'
import { OrganizationService } from '../../services/organizationService'
import type { Course, Organization } from '../../types/api'

const router = useRouter()
const { isAuthenticated } = useAuth()
const { handleApiError } = useErrorHandler()
const { enrollInCourse, isEnrolledInCourse } = useEnrollment()

// Local state
const searchQuery = ref('')
const searchLoading = ref(false)
const showPaymentModal = ref(false)
const selectedCourse = ref<Course | null>(null)
const enrollingCourseId = ref<string | null>(null)

// Main courses pagination
const mainCoursesPage = ref(1)
const mainCoursesPerPage = 12
const loadingMoreMain = ref(false)

// Organization state
const selectedOrganizations = ref<string[]>([])
const expandedOrgs = ref<string[]>([])
const orgCoursesData = ref<Record<string, Course[]>>({})
const orgCoursesLoading = ref<Record<string, boolean>>({})
const orgCoursesError = ref<Record<string, any>>({})
const orgCoursesPages = ref<Record<string, number>>({})
const loadingMoreOrg = ref<Record<string, boolean>>({})

// API calls for main platform courses
const { 
  data: allMainCourses
} = useApiData<Course[]>('/courses/?tenant=main&page_size=100&is_public=true', {
  ...CachePresets.courseCatalog,
  transform: (data) => {
    const courses = data.results || data.data || data
    return Array.isArray(courses) ? courses : []
  }
})

// Featured main courses
const { 
  data: featuredMainCourses
} = useApiData<Course[]>('/courses/featured/?tenant=main', {
  ...CachePresets.courseCatalog,
  transform: (data) => {
    const courses = data.data || data
    return Array.isArray(courses) ? courses.slice(0, 6) : []
  }
})

// Available organizations
const { 
  data: availableOrganizations
} = useApiData<Organization[]>('/organizations/', {
  ...CachePresets.courseCatalog,
  transform: (data) => {
    const orgs = data.results || data.data || data
    return Array.isArray(orgs) ? orgs.filter(org => org.id !== 'main') : []
  }
})

// Computed properties
const paginatedMainCourses = computed(() => {
  if (!allMainCourses.value) return []
  const start = 0
  const end = mainCoursesPage.value * mainCoursesPerPage
  return allMainCourses.value.slice(start, end)
})

const hasMoreMainCourses = computed(() => {
  if (!allMainCourses.value) return false
  return (mainCoursesPage.value * mainCoursesPerPage) < allMainCourses.value.length
})

const filteredOrganizations = computed(() => {
  if (!availableOrganizations.value) return []
  
  if (selectedOrganizations.value.length === 0) {
    return availableOrganizations.value
  }
  
  return availableOrganizations.value.filter(org => 
    selectedOrganizations.value.includes(org.id)
  )
})

// Methods
const performSearch = () => {
  // Implement search functionality
  console.log('Searching for:', searchQuery.value)
}

const handleSearchInput = () => {
  // Implement search suggestions
}

const loadMoreMainCourses = () => {
  loadingMoreMain.value = true
  mainCoursesPage.value++
  
  // Simulate loading delay
  setTimeout(() => {
    loadingMoreMain.value = false
  }, 500)
}

const toggleOrganization = (orgId: string) => {
  const index = selectedOrganizations.value.indexOf(orgId)
  if (index > -1) {
    selectedOrganizations.value.splice(index, 1)
  } else {
    selectedOrganizations.value.push(orgId)
  }
}

const toggleOrgExpansion = async (orgId: string) => {
  const index = expandedOrgs.value.indexOf(orgId)
  if (index > -1) {
    expandedOrgs.value.splice(index, 1)
  } else {
    expandedOrgs.value.push(orgId)
    await loadOrgCourses(orgId)
  }
}

const loadOrgCourses = async (orgId: string) => {
  if (orgCoursesData.value[orgId]) return // Already loaded
  
  orgCoursesLoading.value[orgId] = true
  orgCoursesError.value[orgId] = null
  
  try {
    const response = await OrganizationService.getOrganizationCourses(orgId, 1, 6)
    orgCoursesData.value[orgId] = response.results
    orgCoursesPages.value[orgId] = 1
  } catch (error) {
    orgCoursesError.value[orgId] = error
    handleApiError(error as any, { context: { action: 'load_org_courses', orgId } })
  } finally {
    orgCoursesLoading.value[orgId] = false
  }
}

const loadMoreOrgCourses = async (orgId: string) => {
  loadingMoreOrg.value[orgId] = true
  
  try {
    const nextPage = (orgCoursesPages.value[orgId] || 1) + 1
    const response = await OrganizationService.getOrganizationCourses(orgId, nextPage, 6)
    
    if (response.results.length > 0) {
      orgCoursesData.value[orgId] = [...(orgCoursesData.value[orgId] || []), ...response.results]
      orgCoursesPages.value[orgId] = nextPage
    }
  } catch (error) {
    handleApiError(error as any, { context: { action: 'load_more_org_courses', orgId } })
  } finally {
    loadingMoreOrg.value[orgId] = false
  }
}

const getDisplayedOrgCourses = (orgId: string) => {
  const courses = orgCoursesData.value[orgId] || []
  const isExpanded = expandedOrgs.value.includes(orgId)
  return isExpanded ? courses : courses.slice(0, 3)
}

const hasMoreOrgCourses = (orgId: string) => {
  // This would be determined by API response metadata
  const courses = orgCoursesData.value[orgId] || []
  return courses.length > 0 && courses.length % 6 === 0 // Simple heuristic
}

const retryOrgCourses = (orgId: string) => {
  delete orgCoursesData.value[orgId]
  delete orgCoursesError.value[orgId]
  loadOrgCourses(orgId)
}

const goToCourse = (course: Course) => {
  router.push(`/courses/${course.id}`)
}

const handleEnroll = async (course: Course) => {
  if (!isAuthenticated.value) {
    router.push('/auth/login')
    return
  }

  try {
    enrollingCourseId.value = course.id
    
    if (!course.price || course.price === 0) {
      await enrollInCourse(course.id, course)
      router.push(`/courses/${course.id}`)
    } else {
      selectedCourse.value = course
      showPaymentModal.value = true
    }
  } catch (error) {
    handleApiError(error as any, {
      context: { action: 'enroll_in_course', courseId: course.id }
    })
  } finally {
    enrollingCourseId.value = null
  }
}

const handleContinue = (course: Course) => {
  router.push(`/courses/${course.id}/learn`)
}

const handlePaymentSuccess = () => {
  showPaymentModal.value = false
  if (selectedCourse.value) {
    router.push(`/courses/${selectedCourse.value.id}`)
  }
  selectedCourse.value = null
}

const handlePaymentClose = () => {
  showPaymentModal.value = false
  selectedCourse.value = null
}

// Lifecycle
onMounted(async () => {
  // Auto-load first few organizations
  await nextTick()
  if (availableOrganizations.value && availableOrganizations.value.length > 0) {
    const firstThreeOrgs = availableOrganizations.value.slice(0, 3)
    for (const org of firstThreeOrgs) {
      await loadOrgCourses(org.id)
    }
  }
})
</script>

<style scoped>
.enhanced-courses-view {
  min-height: 100vh;
}

.hero-section {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #92400e 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
  position: relative;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}

.title-word {
  display: inline-block;
  margin-right: 0.5rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 40px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.5;
}

.hero-search {
  max-width: 600px;
  margin: 0 auto;
}

.search-container {
  display: flex;
  gap: 12px;
}

.search-input {
  flex: 1;
  padding: 16px 20px;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  outline: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.search-btn {
  padding: 16px 32px;
  background: linear-gradient(135deg, #fed7aa, #fdba74);
  color: #92400e;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.search-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.search-icon {
  font-size: 1.2rem;
}

.search-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 3rem;
  margin-top: 3rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #fed7aa;
}

.stat-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.8);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.main-courses-section {
  padding: 60px 0;
  background: linear-gradient(135deg, #ffffff 0%, #fef3e2 100%);
}

.org-courses-section {
  padding: 60px 0;
  background: linear-gradient(135deg, #fef3e2 0%, #fed7aa 50%, #fdba74 100%);
}

.section-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.platform-badge {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
}

.org-badge {
  background: linear-gradient(135deg, #d97706, #92400e);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
}

.section-description {
  color: #6b7280;
  font-size: 1rem;
  max-width: 600px;
  margin: 0 auto;
}

.featured-subsection {
  margin-bottom: 40px;
}

.subsection-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 24px;
  text-align: center;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.load-more-section {
  text-align: center;
  margin-top: 40px;
}

.load-more-btn {
  padding: 12px 32px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
}

.load-more-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

.load-more-btn.secondary {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  box-shadow: 0 4px 15px rgba(107, 114, 128, 0.3);
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.org-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  margin-bottom: 40px;
}

.org-filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.875rem;
}

.org-filter-btn:hover {
  border-color: #f59e0b;
  background: #fef3e2;
}

.org-filter-btn.active {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.org-logo {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  object-fit: cover;
}

.org-course-count {
  color: #6b7280;
  font-size: 0.75rem;
}

.org-filter-btn.active .org-course-count {
  color: rgba(255, 255, 255, 0.8);
}

.org-group {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.1);
  margin-bottom: 32px;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.org-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid rgba(245, 158, 11, 0.1);
  background: linear-gradient(135deg, #fef3e2, #ffffff);
}

.org-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.org-header-logo {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.org-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #92400e;
  margin-bottom: 4px;
}

.org-description {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 8px;
}

.org-stats {
  display: flex;
  gap: 16px;
}

.stat {
  color: #6b7280;
  font-size: 0.75rem;
  font-weight: 500;
}

.expand-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.expand-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}

.org-courses {
  padding: 24px;
}

.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state .error-icon, .empty-state .empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.retry-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* Enhanced hover effects */
.org-group:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.25);
}

/* Responsive */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .search-container {
    flex-direction: column;
  }
  
  .section-title {
    font-size: 1.5rem;
    flex-direction: column;
    gap: 8px;
  }
  
  .org-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .org-info {
    flex-direction: column;
    text-align: center;
  }
  
  .org-stats {
    justify-content: center;
  }
  
  .courses-grid {
    grid-template-columns: 1fr;
  }
  
  .featured-grid {
    grid-template-columns: 1fr;
  }
}
</style>