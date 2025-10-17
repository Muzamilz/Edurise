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
            
            <div class="contact-methods">
              <div class="contact-method">
                <div class="method-icon">📧</div>
                <div class="method-info">
                  <h3>Email</h3>
                  <p>support@edurise.com</p>
                  <span>We'll respond within 24 hours</span>
                </div>
              </div>
              
              <div class="contact-method">
                <div class="method-icon">📞</div>
                <div class="method-info">
                  <h3>Phone</h3>
                  <p>+1 (555) 123-4567</p>
                  <span>Mon-Fri, 9AM-6PM EST</span>
                </div>
              </div>
              
              <div class="contact-method">
                <div class="method-icon">💬</div>
                <div class="method-info">
                  <h3>Live Chat</h3>
                  <p>Available 24/7</p>
                  <span>Click the chat icon below</span>
                </div>
              </div>
              
              <div class="contact-method">
                <div class="method-icon">📍</div>
                <div class="method-info">
                  <h3>Office</h3>
                  <p>123 Learning Street<br>Education City, EC 12345</p>
                  <span>Visit us during business hours</span>
                </div>
              </div>
            </div>

            <div class="social-links">
              <h3>Follow Us</h3>
              <div class="social-icons">
                <a href="#" class="social-link">📘 Facebook</a>
                <a href="#" class="social-link">🐦 Twitter</a>
                <a href="#" class="social-link">💼 LinkedIn</a>
                <a href="#" class="social-link">📸 Instagram</a>
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
import { ref } from 'vue'

const form = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const isSubmitting = ref(false)

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