<template>
  <div class="faqs-view">
    <div class="container">
      <div class="page-header">
        <h1>Frequently Asked Questions</h1>
        <p>Find answers to common questions about our platform</p>
      </div>

      <div class="content">
        <div class="search-section">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search FAQs..." 
            class="search-input"
          >
        </div>

        <div class="faq-categories">
          <button 
            v-for="category in categories" 
            :key="category"
            @click="selectedCategory = category"
            :class="['category-btn', { active: selectedCategory === category }]"
          >
            {{ category }}
          </button>
        </div>

        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>Loading FAQs...</p>
        </div>

        <div v-else-if="error" class="error">
          <p>{{ error }}</p>
          <button @click="loadFAQs" class="btn btn-primary">Try Again</button>
        </div>

        <div v-else class="faq-list">
          <div 
            v-for="(faq, index) in filteredFAQs" 
            :key="faq.id"
            class="faq-item"
          >
            <button 
              @click="toggleFAQ(faq, index)"
              class="faq-question"
              :class="{ active: openFAQs.includes(index) }"
            >
              <span>{{ faq.question }}</span>
              <div class="faq-meta">
                <span class="view-count">{{ faq.view_count }} views</span>
                <svg 
                  class="faq-icon" 
                  :class="{ rotate: openFAQs.includes(index) }"
                  width="20" 
                  height="20" 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
                </svg>
              </div>
            </button>
            <div 
              v-if="openFAQs.includes(index)"
              class="faq-answer"
            >
              <p>{{ faq.answer }}</p>
              <div class="faq-feedback">
                <span>Was this helpful?</span>
                <div class="feedback-buttons">
                  <button 
                    @click="submitFeedback(faq, true)"
                    class="feedback-btn helpful"
                  >
                    👍 Yes ({{ faq.helpful_count }})
                  </button>
                  <button 
                    @click="submitFeedback(faq, false)"
                    class="feedback-btn not-helpful"
                  >
                    👎 No ({{ faq.not_helpful_count }})
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="contact-section">
          <h2>Still have questions?</h2>
          <p>Can't find what you're looking for? Our support team is here to help.</p>
          <router-link to="/contact" class="contact-btn">
            Contact Support
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { contentService, type FAQ } from '@/services/content'

const searchQuery = ref('')
const selectedCategory = ref('All')
const openFAQs = ref<number[]>([])
const faqs = ref<FAQ[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const categories = computed(() => {
  const uniqueCategories = new Set(['All'])
  faqs.value.forEach(faq => {
    uniqueCategories.add(faq.category.charAt(0).toUpperCase() + faq.category.slice(1))
  })
  return Array.from(uniqueCategories)
})

const filteredFAQs = computed(() => {
  let filtered = faqs.value

  if (selectedCategory.value !== 'All') {
    filtered = filtered.filter((faq: any) => 
      faq.category.toLowerCase() === selectedCategory.value.toLowerCase()
    )
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter((faq: any) => 
      faq.question.toLowerCase().includes(query) || 
      faq.answer.toLowerCase().includes(query)
    )
  }

  return filtered
})

const loadFAQs = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await contentService.getFAQs()
    // Handle the API response structure: { success: true, data: [...] }
    faqs.value = Array.isArray(response) ? response : (response.data || (response as any).results || [])
  } catch (err) {
    console.error('Error loading FAQs:', err)
    error.value = 'Failed to load FAQs. Please try again later.'
  } finally {
    loading.value = false
  }
}

const toggleFAQ = async (_faq: FAQ, index: number) => {
  const faqIndex = openFAQs.value.indexOf(index)
  if (faqIndex > -1) {
    openFAQs.value.splice(faqIndex, 1)
  } else {
    openFAQs.value.push(index)
    // Track view when FAQ is opened
    try {
      // This will increment the view count
      await contentService.getFAQs()
    } catch (err) {
      console.error('Error tracking FAQ view:', err)
    }
  }
}

const submitFeedback = async (faq: FAQ, helpful: boolean) => {
  try {
    await contentService.submitFAQFeedback(faq.id, helpful)
    // Reload FAQs to get updated counts
    await loadFAQs()
  } catch (err) {
    console.error('Error submitting feedback:', err)
  }
}

// Watch for search query changes and reset open FAQs
watch([searchQuery, selectedCategory], () => {
  openFAQs.value = []
})

onMounted(() => {
  loadFAQs()
})
</script>

<style scoped>
.faqs-view {
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

.search-section {
  margin-bottom: 2rem;
}

.search-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #f59e0b;
}

.faq-categories {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  justify-content: center;
}

.category-btn {
  padding: 0.5rem 1rem;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.category-btn:hover,
.category-btn.active {
  border-color: #f59e0b;
  background: #f59e0b;
  color: white;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 4rem;
}

.faq-item {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
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

.faq-question {
  width: 100%;
  padding: 1.5rem;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  transition: background-color 0.3s ease;
}

.faq-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.view-count {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 400;
}

.faq-question:hover {
  background: #fef3e2;
}

.faq-question.active {
  background: #fef3e2;
  color: #f59e0b;
}

.faq-icon {
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.faq-icon.rotate {
  transform: rotate(180deg);
}

.faq-answer {
  padding: 0 1.5rem 1.5rem;
  animation: slideDown 0.3s ease;
}

.faq-answer p {
  color: #6b7280;
  line-height: 1.6;
  margin: 0 0 1rem 0;
}

.faq-feedback {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
  font-size: 0.875rem;
}

.feedback-buttons {
  display: flex;
  gap: 0.5rem;
}

.feedback-btn {
  padding: 0.25rem 0.75rem;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.3s ease;
}

.feedback-btn:hover {
  background: #f3f4f6;
}

.feedback-btn.helpful:hover {
  background: #dcfce7;
  border-color: #16a34a;
}

.feedback-btn.not-helpful:hover {
  background: #fee2e2;
  border-color: #dc2626;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.contact-section {
  text-align: center;
  background: white;
  padding: 3rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.contact-section h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.contact-section p {
  font-size: 1.125rem;
  color: #6b7280;
  margin-bottom: 2rem;
}

.contact-btn {
  display: inline-block;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  text-decoration: none;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.contact-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .faq-categories {
    justify-content: flex-start;
  }
  
  .contact-section {
    padding: 2rem;
  }
}
</style>