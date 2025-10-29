<template>
  <div class="testimonies-view">
    <div class="container">
      <div class="page-header">
        <h1>Testimonies</h1>
        <p>Hear from our amazing community of learners and educators</p>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Loading testimonials...</p>
      </div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="loadTestimonials" class="btn btn-primary">Try Again</button>
      </div>

      <div v-else class="testimonies-grid">
        <div 
          v-for="testimonial in testimonials" 
          :key="testimonial.id" 
          class="testimony-card"
        >
          <div class="stars">
            <span v-for="i in testimonial.rating" :key="i">⭐</span>
          </div>
          <p class="quote">{{ testimonial.content }}</p>
          <div class="author">
            <div class="avatar">
              {{ getInitials(testimonial.user_name) }}
            </div>
            <div class="info">
              <h4>{{ testimonial.user_name }}</h4>
              <span>
                {{ testimonial.position }}
                <template v-if="testimonial.company">
                  {{ testimonial.position ? ' at ' : '' }}{{ testimonial.company }}
                </template>
              </span>
              <div v-if="testimonial.course_title" class="course">
                Course: {{ testimonial.course_title }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="cta-section">
        <h2>Join Our Community</h2>
        <p>Start your learning journey today and become part of our success stories</p>
        <div class="cta-buttons">
          <router-link to="/auth/register" class="btn btn-primary">Get Started</router-link>
          <router-link to="/courses" class="btn btn-outline">Browse Courses</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { contentService, type Testimonial } from '@/services/content'

const testimonials = ref<Testimonial[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map((word: any) => word.charAt(0).toUpperCase())
    .join('')
    .substring(0, 2)
}

const loadTestimonials = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await contentService.getTestimonials()
    // Handle the API response structure: { success: true, data: [...] }
    testimonials.value = Array.isArray(response) ? response : (response.data || (response as any).results || [])
  } catch (err) {
    console.error('Error loading testimonials:', err)
    error.value = 'Failed to load testimonials. Please try again later.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTestimonials()
})
</script>

<style scoped>
.testimonies-view {
  min-height: 100vh;
  padding: 2rem 0;
  background: linear-gradient(135deg, #fef3e2 0%, #ffffff 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-header h1 {
  font-size: 3rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.page-header p {
  font-size: 1.25rem;
  color: #6b7280;
}

.testimonies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
}

.testimony-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.testimony-card:hover {
  transform: translateY(-5px);
}

.stars {
  font-size: 1.25rem;
  margin-bottom: 1rem;
}

.quote {
  font-size: 1rem;
  line-height: 1.6;
  color: #6b7280;
  margin-bottom: 1.5rem;
  font-style: italic;
}

.author {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.info span {
  font-size: 0.875rem;
  color: #6b7280;
}

.cta-section {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.cta-section h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.cta-section p {
  font-size: 1.125rem;
  color: #6b7280;
  margin-bottom: 2rem;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}

.btn-outline {
  background: transparent;
  color: #f59e0b;
  border: 2px solid #f59e0b;
}

.btn-outline:hover {
  background: #f59e0b;
  color: white;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  margin-bottom: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  color: #dc2626;
}

.course {
  font-size: 0.75rem;
  color: #f59e0b;
  margin-top: 0.25rem;
  font-weight: 500;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .testimonies-grid {
    grid-template-columns: 1fr;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style>