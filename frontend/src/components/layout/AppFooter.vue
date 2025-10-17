<template>
  <footer class="app-footer" v-if="!isAuthPage">
    <!-- Main Footer Content -->
    <div class="footer-main">
      <div class="container">
        <div class="footer-content">
          <!-- Brand Section -->
          <div class="footer-brand">
            <div class="brand-logo">
              <svg class="logo-svg" width="48" height="48" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="40" height="40" rx="8" fill="url(#footerLogoGradient)"/>
                <path d="M12 14h16v2H12v-2zm0 4h16v2H12v-2zm0 4h12v2H12v-2z" fill="white"/>
                <circle cx="30" cy="12" r="3" fill="#FED7AA"/>
                <defs>
                  <linearGradient id="footerLogoGradient" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#F59E0B"/>
                    <stop offset="1" stop-color="#D97706"/>
                  </linearGradient>
                </defs>
              </svg>
              <div class="brand-info">
                <h3 class="brand-name">{{ branding.name || 'Edurise' }}</h3>
                <p class="brand-tagline">Learn • Grow • Succeed</p>
              </div>
            </div>
            <p class="brand-description">
              Empowering learners worldwide with quality education and innovative learning experiences. 
              Join thousands who have transformed their careers with us.
            </p>
            <div class="social-links">
              <a href="#" class="social-link" aria-label="Facebook">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </a>
              <a href="#" class="social-link" aria-label="Twitter">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                </svg>
              </a>
              <a href="#" class="social-link" aria-label="LinkedIn">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </a>
              <a href="#" class="social-link" aria-label="Instagram">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
              </a>
            </div>
          </div>

          <!-- Platform Section -->
          <div class="footer-section">
            <h4 class="footer-title">Platform</h4>
            <ul class="footer-links">
              <li><router-link to="/courses" class="footer-link">Browse Courses</router-link></li>
              <li><router-link to="/become-teacher" class="footer-link">Teach on Edurise</router-link></li>
              <li><router-link to="/become-student" class="footer-link">Start Learning</router-link></li>
              <li><router-link to="/testimonies" class="footer-link">Success Stories</router-link></li>
            </ul>
          </div>

          <!-- Company Section -->
          <div class="footer-section">
            <h4 class="footer-title">Company</h4>
            <ul class="footer-links">
              <li><router-link to="/about" class="footer-link">About Us</router-link></li>
              <li><router-link to="/our-team" class="footer-link">Our Team</router-link></li>
              <li><router-link to="/vision-mission" class="footer-link">Vision & Mission</router-link></li>
              <li><router-link to="/announcements" class="footer-link">News & Updates</router-link></li>
            </ul>
          </div>

          <!-- Support & Legal Section -->
          <div class="footer-section">
            <h4 class="footer-title">Support & Legal</h4>
            <ul class="footer-links">
              <li><router-link to="/faqs" class="footer-link">Help Center</router-link></li>
              <li><router-link to="/contact" class="footer-link">Contact Support</router-link></li>
              <li><router-link to="/student-guidelines" class="footer-link">Student Guide</router-link></li>
              <li><router-link to="/payment-methodologies" class="footer-link">Payment Help</router-link></li>
              <li><router-link to="/privacy-policy" class="footer-link">Privacy Policy</router-link></li>
              <li><router-link to="/terms-of-service" class="footer-link">Terms of Service</router-link></li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Trust Indicators -->
      <div class="trust-section">
        <div class="container">
          <div class="trust-content">
            <div class="trust-stats">
              <div class="trust-stat">
                <div class="trust-number">10,000+</div>
                <div class="trust-label">Students Transformed</div>
              </div>
              <div class="trust-stat">
                <div class="trust-number">94%</div>
                <div class="trust-label">Career Advancement Rate</div>
              </div>
              <div class="trust-stat">
                <div class="trust-number">4.9/5</div>
                <div class="trust-label">Average Rating</div>
              </div>
              <div class="trust-stat">
                <div class="trust-number">30-Day</div>
                <div class="trust-label">Money-Back Guarantee</div>
              </div>
            </div>
            
            <div class="security-badges">
              <div class="security-badge">
                <div class="badge-icon">🔒</div>
                <div class="badge-text">SSL Secured</div>
              </div>
              <div class="security-badge">
                <div class="badge-icon">🛡️</div>
                <div class="badge-text">GDPR Compliant</div>
              </div>
              <div class="security-badge">
                <div class="badge-icon">✅</div>
                <div class="badge-text">Verified Platform</div>
              </div>
              <div class="security-badge">
                <div class="badge-icon">🏆</div>
                <div class="badge-text">Award Winning</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Bottom -->
      <div class="footer-bottom">
        <div class="container">
          <div class="footer-bottom-content">
            <div class="copyright-section">
              <p class="copyright">
                © {{ currentYear }} {{ branding.name || 'Edurise' }}. All rights reserved.
              </p>
              <p class="compliance-text">
                Edurise is committed to protecting your privacy and ensuring a secure learning environment. 
                Our platform complies with international data protection standards.
              </p>
            </div>
            
            <div class="footer-bottom-links">
              <router-link to="/privacy-policy" class="footer-bottom-link">Privacy Policy</router-link>
              <router-link to="/terms-of-service" class="footer-bottom-link">Terms of Service</router-link>
              <router-link to="/cookie-policy" class="footer-bottom-link">Cookie Policy</router-link>
              <router-link to="/sitemap" class="footer-bottom-link">Sitemap</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTenant } from '@/composables/useTenant'

const route = useRoute()
const authStore = useAuthStore()
const { branding } = useTenant()

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)
const isTeacher = computed(() => authStore.isTeacher)
const currentYear = computed(() => new Date().getFullYear())

const isAuthPage = computed(() => {
  return route.path.startsWith('/auth/')
})
</script>

<style scoped>
.app-footer {
  background: linear-gradient(135deg, #1f2937 0%, #2d3748 50%, #374151 100%);
  color: #e2e8f0;
  margin-top: auto;
  position: relative;
}

.app-footer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #f59e0b, #d97706, #f59e0b, transparent);
  opacity: 0.6;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.footer-content {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 3rem;
  padding: 3rem 0 2rem;
  align-items: start;
}

/* Brand Section */
.footer-brand {
  max-width: 300px;
}

.brand-logo {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.logo-svg {
  margin-right: 0.75rem;
}

.brand-info {
  flex: 1;
}

.brand-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f59e0b;
  margin: 0 0 0.25rem 0;
}

.brand-tagline {
  font-size: 0.875rem;
  color: #9ca3af;
  margin: 0;
  font-style: italic;
}

.brand-description {
  color: #9ca3af;
  line-height: 1.6;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  background: rgba(55, 65, 81, 0.6);
  color: #cbd5e0;
  border-radius: 0.75rem;
  transition: all 0.3s ease;
  text-decoration: none;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.social-link:hover {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
  border-color: #f59e0b;
}

/* Footer Sections */
.footer-section {
  min-width: 0;
}

.footer-title {
  font-size: 1rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 0.5rem;
}

.footer-link {
  color: #cbd5e0;
  text-decoration: none;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.footer-link:hover {
  color: #f59e0b;
  transform: translateX(4px);
}

/* Trust Section */
.trust-section {
  background: rgba(17, 24, 39, 0.8);
  border-top: 1px solid #374151;
  padding: 2rem 0;
}

.trust-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.trust-stats {
  display: flex;
  gap: 2rem;
}

.trust-stat {
  text-align: center;
}

.trust-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f59e0b;
  margin-bottom: 0.25rem;
}

.trust-label {
  font-size: 0.75rem;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.security-badges {
  display: flex;
  gap: 1rem;
}

.security-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(55, 65, 81, 0.6);
  border-radius: 0.5rem;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-icon {
  font-size: 1rem;
}

.badge-text {
  font-size: 0.75rem;
  color: #cbd5e0;
  font-weight: 500;
}

/* Footer Bottom */
.footer-bottom {
  border-top: 1px solid #374151;
  padding: 1.5rem 0;
}

.footer-bottom-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.copyright-section {
  flex: 1;
}

.copyright {
  color: #a0aec0;
  font-size: 0.875rem;
  margin: 0 0 0.5rem 0;
}

.compliance-text {
  color: #6b7280;
  font-size: 0.75rem;
  margin: 0;
  max-width: 400px;
}

.footer-bottom-links {
  display: flex;
  gap: 1.5rem;
}

.footer-bottom-link {
  color: #a0aec0;
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.3s ease;
}

.footer-bottom-link:hover {
  color: #f59e0b;
}

/* Responsive */
@media (max-width: 1024px) {
  .footer-content {
    grid-template-columns: 1fr 1fr 1fr;
    gap: 2rem;
  }
  
  .footer-brand {
    grid-column: 1 / -1;
    max-width: none;
    text-align: center;
    margin-bottom: 2rem;
  }

  .trust-content {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }

  .trust-stats {
    justify-content: center;
    flex-wrap: wrap;
  }

  .security-badges {
    justify-content: center;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    padding: 2rem 0 1.5rem;
  }
  
  .footer-brand {
    grid-column: 1 / -1;
    margin-bottom: 2rem;
  }
  
  .footer-bottom-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .footer-bottom-links {
    justify-content: center;
    flex-wrap: wrap;
  }

  .trust-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .security-badges {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }
}

@media (max-width: 480px) {
  .footer-content {
    grid-template-columns: 1fr;
    text-align: center;
    padding: 2rem 0 1rem;
    gap: 2rem;
  }
  
  .footer-section {
    margin-bottom: 0;
  }
  
  .social-links {
    justify-content: center;
  }
  
  .container {
    padding: 0 1rem;
  }

  .trust-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .security-badges {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .security-badge {
    justify-content: center;
  }

  .footer-bottom-links {
    gap: 1rem;
  }
}
</style>