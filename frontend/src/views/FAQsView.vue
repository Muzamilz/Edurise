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

        <div class="faq-list">
          <div 
            v-for="(faq, index) in filteredFAQs" 
            :key="index"
            class="faq-item"
          >
            <button 
              @click="toggleFAQ(index)"
              class="faq-question"
              :class="{ active: openFAQs.includes(index) }"
            >
              <span>{{ faq.question }}</span>
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
            </button>
            <div 
              v-if="openFAQs.includes(index)"
              class="faq-answer"
            >
              <p>{{ faq.answer }}</p>
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
import { ref, computed } from 'vue'

const searchQuery = ref('')
const selectedCategory = ref('All')
const openFAQs = ref<number[]>([])

const categories = ['All', 'General', 'Courses', 'Payment', 'Technical', 'Account']

const faqs = [
  {
    category: 'General',
    question: 'What is Edurise?',
    answer: 'Edurise is a comprehensive learning management system that connects educators and learners worldwide through interactive online courses, live classes, and AI-powered learning assistance.'
  },
  {
    category: 'General',
    question: 'How do I get started?',
    answer: 'Simply create a free account, browse our course catalog, and enroll in courses that match your learning goals. You can start learning immediately after enrollment.'
  },
  {
    category: 'Courses',
    question: 'How many courses can I take?',
    answer: 'With our subscription plans, you can access unlimited courses. Free users can access a limited selection of courses and materials.'
  },
  {
    category: 'Courses',
    question: 'Do I get certificates?',
    answer: 'Yes! You receive a certificate of completion for each course you successfully finish. These certificates can be shared on LinkedIn and added to your resume.'
  },
  {
    category: 'Payment',
    question: 'What payment methods do you accept?',
    answer: 'We accept all major credit cards, PayPal, bank transfers, and various digital wallets. We also offer installment payment options for premium plans.'
  },
  {
    category: 'Payment',
    question: 'Can I get a refund?',
    answer: 'Yes, we offer a 30-day money-back guarantee for all courses and subscriptions. If you\'re not satisfied, contact our support team for a full refund.'
  },
  {
    category: 'Technical',
    question: 'What devices can I use?',
    answer: 'Edurise works on all devices including computers, tablets, and smartphones. We have dedicated mobile apps for iOS and Android for learning on the go.'
  },
  {
    category: 'Technical',
    question: 'Do I need special software?',
    answer: 'No special software is required. Edurise runs in your web browser. For the best experience, we recommend using the latest version of Chrome, Firefox, Safari, or Edge.'
  },
  {
    category: 'Account',
    question: 'How do I reset my password?',
    answer: 'Click on "Forgot Password" on the login page, enter your email address, and we\'ll send you instructions to reset your password.'
  },
  {
    category: 'Account',
    question: 'Can I change my email address?',
    answer: 'Yes, you can update your email address in your account settings. You\'ll need to verify the new email address before the change takes effect.'
  }
]

const filteredFAQs = computed(() => {
  let filtered = faqs

  if (selectedCategory.value !== 'All') {
    filtered = filtered.filter(faq => faq.category === selectedCategory.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(faq => 
      faq.question.toLowerCase().includes(query) || 
      faq.answer.toLowerCase().includes(query)
    )
  }

  return filtered
})

const toggleFAQ = (index: number) => {
  const faqIndex = openFAQs.value.indexOf(index)
  if (faqIndex > -1) {
    openFAQs.value.splice(faqIndex, 1)
  } else {
    openFAQs.value.push(index)
  }
}
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
  margin: 0;
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