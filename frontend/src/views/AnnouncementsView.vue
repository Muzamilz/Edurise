<template>
  <div class="announcements-view">
    <div class="container">
      <div class="page-header">
        <h1>Announcements</h1>
        <p>Stay updated with the latest news and updates from Edurise</p>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Loading announcements...</p>
      </div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="loadAnnouncements" class="btn btn-primary">Try Again</button>
      </div>

      <div v-else class="announcements-list">
        <article 
          v-for="announcement in announcements" 
          :key="announcement.id"
          :class="['announcement-card', { featured: announcement.featured }]"
        >
          <div v-if="announcement.featured" class="announcement-badge">Featured</div>
          <div class="announcement-meta">
            <div class="announcement-date">{{ formatDate(announcement.publish_at) }}</div>
            <div class="announcement-category">{{ announcement.category }}</div>
            <div v-if="announcement.priority !== 'normal'" class="announcement-priority" :class="announcement.priority">
              {{ announcement.priority }}
            </div>
          </div>
          <h2>{{ announcement.title }}</h2>
          <p>{{ announcement.content }}</p>
          <div class="announcement-footer">
            <span class="author">By {{ announcement.author_name }}</span>
            <div v-if="announcement.tags" class="tags">
              <span 
                v-for="tag in announcement.tags.split(',')" 
                :key="tag.trim()" 
                class="tag"
              >
                {{ tag.trim() }}
              </span>
            </div>
          </div>
        </article>
      </div>

      <div class="newsletter-signup">
        <h2>Stay Informed</h2>
        <p>Subscribe to our newsletter to receive the latest announcements directly in your inbox</p>
        <form class="newsletter-form" @submit.prevent="subscribeNewsletter">
          <input 
            v-model="email" 
            type="email" 
            placeholder="Enter your email address" 
            required
          >
          <button type="submit" class="btn btn-primary" :disabled="subscribing">
            {{ subscribing ? 'Subscribing...' : 'Subscribe' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { contentService, type Announcement } from '@/services/content'

const announcements = ref<Announcement[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const email = ref('')
const subscribing = ref(false)

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const loadAnnouncements = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await contentService.getAnnouncements()
    // Handle the API response structure: { success: true, data: [...] }
    announcements.value = Array.isArray(response) ? response : (response.data || (response as any).results || [])
  } catch (err) {
    console.error('Error loading announcements:', err)
    error.value = 'Failed to load announcements. Please try again later.'
  } finally {
    loading.value = false
  }
}

const subscribeNewsletter = async () => {
  try {
    subscribing.value = true
    // This would typically call a newsletter subscription API
    // For now, just simulate the action
    await new Promise(resolve => setTimeout(resolve, 1000))
    alert('Successfully subscribed to newsletter!')
    email.value = ''
  } catch (err) {
    console.error('Error subscribing to newsletter:', err)
    alert('Failed to subscribe. Please try again.')
  } finally {
    subscribing.value = false
  }
}

onMounted(() => {
  loadAnnouncements()
})
</script>

<style scoped>
.announcements-view {
  min-height: 100vh;
  padding: 2rem 0;
}

.container {
  max-width: 800px;
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

.announcements-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-bottom: 4rem;
}

.announcement-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  position: relative;
}

.announcement-card:hover {
  transform: translateY(-3px);
}

.announcement-card.featured {
  border: 2px solid #f59e0b;
  background: linear-gradient(135deg, #fef3e2, #ffffff);
}

.announcement-badge {
  position: absolute;
  top: -10px;
  right: 20px;
  background: #f59e0b;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
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

.announcement-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.announcement-date {
  font-size: 0.875rem;
  color: #6b7280;
}

.announcement-category {
  font-size: 0.75rem;
  background: #f3f4f6;
  color: #6b7280;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  text-transform: capitalize;
}

.announcement-priority {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 600;
  text-transform: uppercase;
}

.announcement-priority.high {
  background: #fef3c7;
  color: #d97706;
}

.announcement-priority.urgent {
  background: #fee2e2;
  color: #dc2626;
}

.announcement-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.author {
  font-size: 0.875rem;
  color: #6b7280;
  font-style: italic;
}

.tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag {
  font-size: 0.75rem;
  background: #f59e0b;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.announcement-card h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.announcement-card p {
  font-size: 1rem;
  line-height: 1.6;
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.read-more {
  color: #f59e0b;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.read-more:hover {
  color: #d97706;
}

.newsletter-signup {
  background: white;
  padding: 3rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.newsletter-signup h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.newsletter-signup p {
  font-size: 1.125rem;
  color: #6b7280;
  margin-bottom: 2rem;
}

.newsletter-form {
  display: flex;
  gap: 1rem;
  max-width: 400px;
  margin: 0 auto;
}

.newsletter-form input {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.newsletter-form input:focus {
  outline: none;
  border-color: #f59e0b;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
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

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .announcement-card {
    padding: 1.5rem;
  }
  
  .newsletter-form {
    flex-direction: column;
  }
  
  .newsletter-signup {
    padding: 2rem;
  }
}
</style>