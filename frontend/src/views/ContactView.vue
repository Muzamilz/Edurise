<template>
  <div class="contact-view">
    <div class="container">
      <div class="page-header">
        <h1>Contact Us</h1>
        <p>Get in touch with our team - we're here to help</p>
      </div>

      <div class="content">
        <div class="contact-grid">
          <!-- Contact Form -->
          <div class="contact-form-section">
            <h2>Send us a Message</h2>
            <form @submit.prevent="submitForm" class="contact-form">
              <div class="form-group">
                <label for="name">Full Name</label>
                <input 
                  id="name"
                  v-model="form.name" 
                  type="text" 
                  required 
                  class="form-input"
                >
              </div>
              
              <div class="form-group">
                <label for="email">Email Address</label>
                <input 
                  id="email"
                  v-model="form.email" 
                  type="email" 
                  required 
                  class="form-input"
                >
              </div>
              
              <div class="form-group">
                <label for="subject">Subject</label>
                <select 
                  id="subject"
                  v-model="form.subject" 
                  required 
                  class="form-input"
                >
                  <option value="">Select a subject</option>
                  <option value="general">General Inquiry</option>
                  <option value="technical">Technical Support</option>
                  <option value="billing">Billing Question</option>
                  <option value="course">Course Related</option>
                  <option value="partnership">Partnership</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="message">Message</label>
                <textarea 
                  id="message"
                  v-model="form.message" 
                  required 
                  rows="5" 
                  class="form-input"
                  placeholder="Tell us how we can help you..."
                ></textarea>
              </div>
              
              <button type="submit" class="submit-btn" :disabled="isSubmitting">
                {{ isSubmitting ? 'Sending...' : 'Send Message' }}
              </button>
            </form>
          </div>

          <!-- Contact Information -->
          <div class="contact-info-section">
            <h2>Get in Touch</h2>
            
            <div v-if="loadingContact" class="loading">
              <div class="spinner"></div>
              <p>Loading contact information...</p>
            </div>

            <div v-else-if="contactError" class="error">
              <p>{{ contactError }}</p>
              <button @click="loadContactInfo" class="btn btn-primary">Try Again</button>
            </div>

            <div v-else-if="contactInfo" class="contact-methods">
              <div class="contact-method">
                <div class="method-icon">📧</div>
                <div class="method-info">
                  <h3>Email</h3>
                  <p>{{ contactInfo.email }}</p>
                  <span>We'll respond within 24 hours</span>
                </div>
              </div>
              
              <div v-if="contactInfo.phone" class="contact-method">
                <div class="method-icon">📞</div>
                <div class="method-info">
                  <h3>Phone</h3>
                  <p>{{ contactInfo.phone }}</p>
                  <span>{{ contactInfo.business_hours || 'Mon-Fri, 9AM-6PM EST' }}</span>
                </div>
              </div>
              
              <div v-if="contactInfo.support_url" class="contact-method">
                <div class="method-icon">💬</div>
                <div class="method-info">
                  <h3>Live Chat</h3>
                  <p>Available 24/7</p>
                  <a :href="contactInfo.support_url" target="_blank" class="support-link">
                    Start Chat
                  </a>
                </div>
              </div>
              
              <div v-if="contactInfo.address" class="contact-method">
                <div class="method-icon">📍</div>
                <div class="method-info">
                  <h3>Office</h3>
                  <p v-html="contactInfo.address.replace(/\n/g, '<br>')"></p>
                  <span>{{ contactInfo.business_hours || 'Visit us during business hours' }}</span>
                </div>
              </div>
            </div>

            <div v-if="contactInfo" class="social-links">
              <h3>Follow Us</h3>
              <div class="social-icons">
                <a 
                  v-if="contactInfo.facebook_url" 
                  :href="contactInfo.facebook_url" 
                  target="_blank"
                  class="social-link"
                >
                  📘 Facebook
                </a>
                <a 
                  v-if="contactInfo.twitter_url" 
                  :href="contactInfo.twitter_url" 
                  target="_blank"
                  class="social-link"
                >
                  🐦 Twitter
                </a>
                <a 
                  v-if="contactInfo.linkedin_url" 
                  :href="contactInfo.linkedin_url" 
                  target="_blank"
                  class="social-link"
                >
                  💼 LinkedIn
                </a>
                <a 
                  v-if="contactInfo.instagram_url" 
                  :href="contactInfo.instagram_url" 
                  target="_blank"
                  class="social-link"
                >
                  📸 Instagram
                </a>
                <a 
                  v-if="contactInfo.youtube_url" 
                  :href="contactInfo.youtube_url" 
                  target="_blank"
                  class="social-link"
                >
                  📺 YouTube
                </a>
              </div>
            </div>
          </div>
        </div>

        <div class="faq-section">
          <h2>Quick Answers</h2>
          <p>Before reaching out, check if your question is answered in our FAQ section</p>
          <router-link to="/faqs" class="faq-btn">
            View FAQs
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { contentService, type ContactInfo } from '@/services/content'

const form = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const isSubmitting = ref(false)
const contactInfo = ref<ContactInfo | null>(null)
const loadingContact = ref(true)
const contactError = ref<string | null>(null)

const submitForm = async () => {
  isSubmitting.value = true
  
  // Simulate form submission
  setTimeout(() => {
    alert('Thank you for your message! We\'ll get back to you soon.')
    form.value = {
      name: '',
      email: '',
      subject: '',
      message: ''
    }
    isSubmitting.value = false
  }, 1000)
}

const loadContactInfo = async () => {
  try {
    loadingContact.value = true
    contactError.value = null
    contactInfo.value = await contentService.getContactInfo()
  } catch (err) {
    console.error('Error loading contact info:', err)
    contactError.value = 'Failed to load contact information. Please try again later.'
  } finally {
    loadingContact.value = false
  }
}

onMounted(() => {
  loadContactInfo()
})
</script>

<style scoped>
.contact-view {
  min-height: 100vh;
  padding: 2rem 0;
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

.contact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  margin-bottom: 4rem;
}

.contact-form-section,
.contact-info-section {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.contact-form-section h2,
.contact-info-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #f59e0b;
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #f59e0b;
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
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.support-link {
  color: #f59e0b;
  text-decoration: none;
  font-weight: 600;
}

.support-link:hover {
  text-decoration: underline;
}

.contact-methods {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-bottom: 3rem;
}

.contact-method {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.method-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.method-info h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 0.5rem;
}

.method-info p {
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.method-info span {
  font-size: 0.875rem;
  color: #6b7280;
}

.social-links h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.social-icons {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.social-link {
  color: #6b7280;
  text-decoration: none;
  transition: color 0.3s ease;
}

.social-link:hover {
  color: #f59e0b;
}

.faq-section {
  text-align: center;
  background: white;
  padding: 3rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.faq-section h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.faq-section p {
  font-size: 1.125rem;
  color: #6b7280;
  margin-bottom: 2rem;
}

.faq-btn {
  display: inline-block;
  padding: 1rem 2rem;
  background: transparent;
  color: #f59e0b;
  text-decoration: none;
  border: 2px solid #f59e0b;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.faq-btn:hover {
  background: #f59e0b;
  color: white;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .contact-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .contact-form-section,
  .contact-info-section,
  .faq-section {
    padding: 1.5rem;
  }
}
</style>