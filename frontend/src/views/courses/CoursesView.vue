<template>
  <div class="courses-view">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">Discover Amazing Courses</h1>
        <p class="hero-subtitle">
          Learn new skills from expert instructors and advance your career
        </p>
        <div class="hero-search">
          <input
            v-model="searchQuery"
            @keydown.enter="performSearch"
            type="text"
            placeholder="What do you want to learn?"
            class="search-input"
          />
          <button @click="performSearch" class="search-btn">
            Search
          </button>
        </div>
      </div>
    </div>

    <!-- Featured Courses -->
    <section v-if="featuredCourses.length > 0" class="featured-section">
      <div class="container">
        <h2 class="section-title">Featured Courses</h2>
        <div class="featured-grid">
          <CourseCard
            v-for="course in featuredCourses"
            :key="course.id"
            :course="course"
            :is-enrolled="isEnrolledInCourse(course.id)"
            @click="goToCourse"
            @enroll="handleEnroll"
            @continue="handleContinue"
          />
        </div>
      </div>
    </section>

    <!-- Categories -->
    <section v-if="categories.length > 0" class="categories-section">
      <div class="container">
        <h2 class="section-title">Browse by Category</h2>
        <div class="categories-grid">
          <div
            v-for="category in categories"
            :key="category.category"
            @click="filterByCategory(category.category)"
            class="category-card"
          >
            <div class="category-icon">
              {{ getCategoryIcon(category.category) }}
            </div>
            <h3 class="category-name">{{ formatCategory(category.category) }}</h3>
            <p class="category-stats">
              {{ category.count }} courses
              <span v-if="category.avg_rating > 0">
                • {{ category.avg_rating.toFixed(1) }}★
              </span>
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- All Courses -->
    <section class="courses-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">All Courses</h2>
          <div class="view-toggle">
            <button
              @click="viewMode = 'grid'"
              class="toggle-btn"
              :class="{ active: viewMode === 'grid' }"
            >
              Grid
            </button>
            <button
              @click="viewMode = 'list'"
              class="toggle-btn"
              :class="{ active: viewMode === 'list' }"
            >
              List
            </button>
          </div>
        </div>

        <CourseList
          :use-marketplace="true"
          :show-enroll-button="true"
          @course-click="goToCourse"
          @enroll="handleEnroll"
          @continue="handleContinue"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import CourseCard from '../../components/courses/CourseCard.vue'
import CourseList from '../../components/courses/CourseList.vue'
import { useCourseStore } from '../../stores/courses'
import { useAuthStore } from '../../stores/auth'
import type { Course } from '../../types/api'

const router = useRouter()
const courseStore = useCourseStore()
const authStore = useAuthStore()

// Local state
const searchQuery = ref('')
const viewMode = ref<'grid' | 'list'>('grid')

// Computed
const featuredCourses = computed(() => courseStore.featuredCourses)
const categories = computed(() => courseStore.categories)
const isEnrolledInCourse = computed(() => courseStore.isEnrolledInCourse)

// Methods
const performSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({
      name: 'courses',
      query: { search: searchQuery.value.trim() }
    })
  }
}

const filterByCategory = (category: string) => {
  router.push({
    name: 'courses',
    query: { category }
  })
}

const goToCourse = (course: Course) => {
  router.push(`/courses/${course.id}`)
}

const handleEnroll = async (course: Course) => {
  if (!authStore.isAuthenticated) {
    router.push('/auth/login')
    return
  }

  try {
    await courseStore.enrollInCourse(course.id)
    // Show success message or redirect
    router.push(`/courses/${course.id}`)
  } catch (error) {
    console.error('Failed to enroll in course:', error)
    // Show error message
  }
}

const handleContinue = (course: Course) => {
  router.push(`/courses/${course.id}/learn`)
}

const formatCategory = (category: string) => {
  return category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')
}

const getCategoryIcon = (category: string) => {
  const icons: Record<string, string> = {
    technology: '💻',
    business: '💼',
    design: '🎨',
    marketing: '📈',
    language: '🗣️',
    science: '🔬',
    other: '📚'
  }
  return icons[category] || '📚'
}

// Lifecycle
onMounted(async () => {
  // Load featured courses and categories
  await Promise.all([
    courseStore.fetchFeaturedCourses(),
    courseStore.fetchCategories()
  ])

  // Load enrollment status if user is logged in
  if (authStore.isAuthenticated) {
    await courseStore.fetchEnrollments()
  }
})
</script>

<style scoped>
.courses-view {
  min-height: 100vh;
}

.hero-section {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #92400e 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
  position: relative;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(254, 243, 226, 0.1) 0%, transparent 50%);
  pointer-events: none;
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

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 40px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.5;
}

.hero-search {
  display: flex;
  max-width: 500px;
  margin: 0 auto;
  gap: 12px;
}

.search-input {
  flex: 1;
  padding: 16px 20px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
}

.search-input::placeholder {
  color: #9CA3AF;
}

.search-btn {
  padding: 16px 32px;
  background: linear-gradient(135deg, #fed7aa, #fdba74);
  color: #92400e;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(254, 215, 170, 0.4);
}

.search-btn:hover {
  background: linear-gradient(135deg, #fdba74, #fb923c);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(254, 215, 170, 0.6);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.featured-section,
.categories-section,
.courses-section {
  padding: 60px 0;
}

.categories-section {
  background: linear-gradient(135deg, #fef3e2 0%, #ffffff 50%, #f0f9ff 100%);
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 40px;
  text-align: center;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.category-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.category-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 35px rgba(245, 158, 11, 0.2);
  background: linear-gradient(135deg, rgba(254, 243, 226, 0.8), rgba(254, 215, 170, 0.4));
}

.category-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.category-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 8px;
}

.category-stats {
  color: #6B7280;
  font-size: 0.875rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.section-header .section-title {
  margin: 0;
  text-align: left;
}

.view-toggle {
  display: flex;
  background: rgba(254, 243, 226, 0.5);
  border-radius: 8px;
  padding: 4px;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.toggle-btn {
  padding: 8px 16px;
  background: none;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6B7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn.active {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-search {
    flex-direction: column;
    max-width: 100%;
  }
  
  .search-btn {
    padding: 16px;
  }
  
  .featured-section,
  .categories-section,
  .courses-section {
    padding: 40px 0;
  }
  
  .section-title {
    font-size: 1.5rem;
    margin-bottom: 24px;
  }
  
  .featured-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .categories-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
  }
  
  .category-card {
    padding: 20px;
  }
  
  .category-icon {
    font-size: 2rem;
    margin-bottom: 12px;
  }
  
  .section-header {
    flex-direction: column;
    gap: 20px;
    align-items: stretch;
  }
  
  .section-header .section-title {
    text-align: center;
  }
  
  .view-toggle {
    align-self: center;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 60px 20px;
  }
  
  .categories-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>