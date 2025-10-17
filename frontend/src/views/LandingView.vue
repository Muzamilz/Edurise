<template>
  <div class="landing-page">
    <!-- Background Elements -->
    <div class="background-elements">
      <div class="absolute inset-0">
        <div class="absolute top-0 left-0 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div class="absolute top-0 right-0 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div class="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>
      
      <!-- Floating shapes -->
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
      <div class="circle circle-4"></div>
      <div class="circle circle-5"></div>
      <div class="circle circle-6"></div>
      <div class="circle circle-7"></div>
    </div>

    <!-- Hero Section -->
    <section class="hero-section">
      <div class="container">
        <div class="hero-content">
          <div class="text-section">
            <div class="badge">
              <span class="badge-text">🚀 Trusted by 10,000+ learners worldwide</span>
            </div>
            
            <h1 class="main-title">
              Stop Wasting Time on <span class="highlight">Outdated Learning</span>
            </h1>
            
            <h2 class="sub-title">
              Transform Your Career in 90 Days with AI-Powered Education
            </h2>
            
            <p class="description">
              Tired of boring courses that lead nowhere? Our interactive platform uses AI to personalize your learning journey, 
              helping you master in-demand skills 3x faster than traditional methods.
            </p>
            
            <div class="cta-buttons">
              <button @click="startDemo" class="cta-button primary">
                🎯 Try Interactive Demo
              </button>
              <router-link to="/courses" class="cta-button secondary">
                Browse Courses
              </router-link>
            </div>

            <div class="trust-indicators">
              <div class="stat">
                <span class="number">10,000+</span>
                <span class="label">Students Transformed</span>
              </div>
              <div class="stat">
                <span class="number">94%</span>
                <span class="label">Career Advancement</span>
              </div>
              <div class="stat">
                <span class="number">4.9/5</span>
                <span class="label">Student Rating</span>
              </div>
            </div>
          </div>

          <div class="demo-section">
            <div class="interactive-demo" :class="{ active: demoActive }">
              <div class="demo-header">
                <div class="demo-controls">
                  <div class="control red"></div>
                  <div class="control yellow"></div>
                  <div class="control green"></div>
                </div>
                <span class="demo-title">Live Learning Dashboard</span>
              </div>
              <div class="demo-content">
                <div class="progress-bar">
                  <div class="progress" :style="{ width: progressWidth + '%' }"></div>
                </div>
                <div class="demo-stats">
                  <div class="demo-stat">
                    <span class="demo-number">{{ completedLessons }}</span>
                    <span class="demo-label">Lessons Completed</span>
                  </div>
                  <div class="demo-stat">
                    <span class="demo-number">{{ skillLevel }}%</span>
                    <span class="demo-label">Skill Mastery</span>
                  </div>
                </div>
                <div class="ai-recommendation">
                  <div class="ai-icon">🤖</div>
                  <div class="ai-text">{{ aiMessage }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Problem Agitation Section -->
    <section class="problem-section">
      <div class="container">
        <div class="problem-content">
          <div class="before-after">
            <div class="before">
              <h3>😤 Your Current Reality</h3>
              <ul>
                <li>Stuck in dead-end job with no growth</li>
                <li>Wasting hours on courses that don't work</li>
                <li>Falling behind while others advance</li>
                <li>No clear path to your dream career</li>
              </ul>
            </div>
            <div class="arrow">→</div>
            <div class="after">
              <h3>🎉 Your New Reality</h3>
              <ul>
                <li>Land your dream job in 90 days</li>
                <li>Master skills that actually matter</li>
                <li>Join the top 10% in your field</li>
                <li>Build a future-proof career</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Social Proof Section -->
    <section class="social-proof-section">
      <div class="container">
        <h2>Join 10,000+ Success Stories</h2>
        <div class="testimonials-grid">
          <div class="testimonial-card">
            <div class="testimonial-header">
              <div class="testimonial-avatar">SM</div>
              <div class="testimonial-info">
                <h4>Sarah M.</h4>
                <span>Software Engineer at Google</span>
              </div>
            </div>
            <p>"Went from retail to Google in 6 months. The AI-powered learning path was incredible!"</p>
            <div class="result">💰 Salary increased by 180%</div>
          </div>
          
          <div class="testimonial-card">
            <div class="testimonial-header">
              <div class="testimonial-avatar">MR</div>
              <div class="testimonial-info">
                <h4>Mike R.</h4>
                <span>Marketing Director at Tesla</span>
              </div>
            </div>
            <p>"Finally found courses that actually work. Got promoted twice in one year!"</p>
            <div class="result">📈 Career advancement in 8 months</div>
          </div>
          
          <div class="testimonial-card">
            <div class="testimonial-header">
              <div class="testimonial-avatar">LK</div>
              <div class="testimonial-info">
                <h4>Lisa K.</h4>
                <span>UX Designer at Airbnb</span>
              </div>
            </div>
            <p>"The personalized learning made all the difference. I'm now designing for millions of users!"</p>
            <div class="result">🚀 Dream job achieved</div>
          </div>
        </div>

        <div class="company-logos">
          <h3>Our graduates work at:</h3>
          <div class="logos-grid">
            <div class="logo">Google</div>
            <div class="logo">Microsoft</div>
            <div class="logo">Apple</div>
            <div class="logo">Tesla</div>
            <div class="logo">Netflix</div>
            <div class="logo">Airbnb</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing Section -->
    <section class="pricing-section">
      <div class="container">
        <h2>Choose Your Success Plan</h2>
        <p class="pricing-subtitle">Join thousands who transformed their careers</p>
        
        <div class="pricing-grid">
          <div class="pricing-card">
            <h3>Starter</h3>
            <div class="price">
              <span class="currency">$</span>
              <span class="amount">29</span>
              <span class="period">/month</span>
            </div>
            <ul class="features">
              <li>✅ 50+ Courses</li>
              <li>✅ Basic AI Recommendations</li>
              <li>✅ Community Access</li>
              <li>✅ Mobile App</li>
            </ul>
            <button class="pricing-btn">Get Started</button>
          </div>

          <div class="pricing-card popular">
            <div class="popular-badge">Most Popular</div>
            <h3>Professional</h3>
            <div class="price">
              <span class="currency">$</span>
              <span class="amount">79</span>
              <span class="period">/month</span>
            </div>
            <ul class="features">
              <li>✅ 200+ Premium Courses</li>
              <li>✅ Advanced AI Learning Path</li>
              <li>✅ 1-on-1 Mentorship</li>
              <li>✅ Career Coaching</li>
              <li>✅ Job Placement Support</li>
              <li>✅ Certificates</li>
            </ul>
            <button class="pricing-btn primary">Start Free Trial</button>
          </div>

          <div class="pricing-card">
            <h3>Enterprise</h3>
            <div class="price">
              <span class="currency">$</span>
              <span class="amount">199</span>
              <span class="period">/month</span>
            </div>
            <ul class="features">
              <li>✅ Unlimited Access</li>
              <li>✅ Custom Learning Paths</li>
              <li>✅ Team Management</li>
              <li>✅ Priority Support</li>
              <li>✅ Analytics Dashboard</li>
            </ul>
            <button class="pricing-btn">Contact Sales</button>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ Section -->
    <section class="faq-section">
      <div class="container">
        <h2>Common Questions</h2>
        <div class="faq-grid">
          <div class="faq-item">
            <h3>Will this actually help me get a better job?</h3>
            <p>Yes! 94% of our graduates get promoted or land better jobs within 6 months. We track every success story and provide job placement support.</p>
          </div>
          
          <div class="faq-item">
            <h3>What if I don't have time to study?</h3>
            <p>Our AI creates personalized 15-minute daily lessons that fit your schedule. Most students see results studying just 30 minutes a day.</p>
          </div>
          
          <div class="faq-item">
            <h3>Is this just another online course platform?</h3>
            <p>No way! We use AI to personalize your learning, provide 1-on-1 mentorship, and guarantee results. If you don't advance your career in 6 months, we'll refund everything.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Final CTA Section -->
    <section class="final-cta-section">
      <div class="container">
        <div class="cta-content">
          <h2>Ready to Transform Your Career?</h2>
          <p>Join 10,000+ professionals who chose success over settling</p>
          <div class="cta-buttons">
            <button @click="startDemo" class="cta-button primary large">
              🚀 Start Your Transformation
            </button>
            <p class="guarantee">30-day money-back guarantee • No risk, all reward</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// Interactive demo state
const demoActive = ref(false)
const progressWidth = ref(0)
const completedLessons = ref(0)
const skillLevel = ref(0)
const aiMessage = ref("Click 'Try Interactive Demo' to see your personalized learning path!")

const aiMessages = [
  "Great progress! Let's focus on advanced JavaScript concepts next.",
  "You're excelling at React! Time to learn Node.js for full-stack development.",
  "Based on your goals, I recommend the Machine Learning fundamentals course.",
  "You're ready for the final project! This will showcase your new skills."
]

let demoInterval: NodeJS.Timeout | null = null

const startDemo = () => {
  demoActive.value = true
  let step = 0
  
  demoInterval = setInterval(() => {
    step++
    
    switch(step) {
      case 1:
        progressWidth.value = 25
        completedLessons.value = 12
        skillLevel.value = 35
        aiMessage.value = aiMessages[0]
        break
      case 2:
        progressWidth.value = 50
        completedLessons.value = 24
        skillLevel.value = 65
        aiMessage.value = aiMessages[1]
        break
      case 3:
        progressWidth.value = 75
        completedLessons.value = 36
        skillLevel.value = 85
        aiMessage.value = aiMessages[2]
        break
      case 4:
        progressWidth.value = 100
        completedLessons.value = 48
        skillLevel.value = 95
        aiMessage.value = aiMessages[3]
        break
      default:
        // Reset demo
        step = 0
        progressWidth.value = 0
        completedLessons.value = 0
        skillLevel.value = 0
        aiMessage.value = "Click 'Try Interactive Demo' to see your personalized learning path!"
    }
  }, 2000)
}

onMounted(() => {
  // Auto-start demo after 3 seconds
  setTimeout(() => {
    if (!demoActive.value) {
      startDemo()
    }
  }, 3000)
})

onUnmounted(() => {
  if (demoInterval) {
    clearInterval(demoInterval)
  }
})
</script>

<style scoped>
.landing-page {
  position: relative;
  overflow-x: hidden;
  background: linear-gradient(135deg, #fef3e2 0%, #ffffff 50%, #f0f9ff 100%);
  min-height: 100vh;
}

/* Background Elements */
.background-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

/* Blob animations */
@keyframes blob {
  0% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  100% {
    transform: translate(0px, 0px) scale(1);
  }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

/* Floating shapes */
.shape {
  position: absolute;
  border-radius: 50% 30% 70% 40%;
  opacity: 0.4;
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 400px;
  height: 300px;
  background: linear-gradient(45deg, #f59e0b, #d97706);
  top: -50px;
  right: -100px;
  transform: rotate(15deg);
  animation-delay: 0s;
}

.shape-2 {
  width: 300px;
  height: 400px;
  background: linear-gradient(135deg, #fed7aa, #fdba74);
  bottom: -100px;
  left: -50px;
  transform: rotate(-20deg);
  animation-delay: 2s;
}

.shape-3 {
  width: 200px;
  height: 250px;
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
  top: 50%;
  right: 10%;
  transform: rotate(45deg);
  opacity: 0.3;
  animation-delay: 4s;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(45deg, #fbbf24, #f59e0b);
  opacity: 0.3;
  animation: float 4s ease-in-out infinite;
}

.circle-1 { 
  width: 80px; 
  height: 80px; 
  top: 20%; 
  right: 15%; 
  background: linear-gradient(45deg, #f59e0b, #d97706);
  animation-delay: 0s;
}

.circle-2 { 
  width: 60px; 
  height: 60px; 
  top: 60%; 
  right: 25%; 
  background: linear-gradient(45deg, #fbbf24, #f59e0b);
  animation-delay: 1s;
}

.circle-3 { 
  width: 40px; 
  height: 40px; 
  top: 30%; 
  right: 5%; 
  background: linear-gradient(45deg, #fed7aa, #fdba74);
  animation-delay: 2s;
}

.circle-4 { 
  width: 100px; 
  height: 100px; 
  bottom: 30%; 
  right: 8%; 
  opacity: 0.2;
  background: linear-gradient(45deg, #f59e0b, #92400e);
  animation-delay: 3s;
}

.circle-5 { 
  width: 30px; 
  height: 30px; 
  top: 70%; 
  right: 35%; 
  background: linear-gradient(45deg, #fbbf24, #f59e0b);
  animation-delay: 1.5s;
}

.circle-6 { 
  width: 50px; 
  height: 50px; 
  bottom: 20%; 
  left: 20%; 
  background: linear-gradient(45deg, #fed7aa, #fdba74);
  animation-delay: 2.5s;
}

.circle-7 { 
  width: 70px; 
  height: 70px; 
  top: 15%; 
  left: 10%; 
  opacity: 0.25;
  background: linear-gradient(45deg, #f59e0b, #d97706);
  animation-delay: 0.5s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(10deg);
  }
}

/* Container */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Hero Section */
.hero-section {
  position: relative;
  z-index: 5;
  padding: 4rem 0;
  min-height: 90vh;
  display: flex;
  align-items: center;
}

.hero-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}

.text-section {
  text-align: left;
}

.badge {
  display: inline-block;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
}

.main-title {
  font-size: 3.5rem;
  font-weight: 800;
  color: #1f2937;
  margin: 0 0 1rem 0;
  line-height: 1.1;
}

.highlight {
  color: #dc2626;
  text-decoration: line-through;
  position: relative;
}

.sub-title {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 2rem 0;
  line-height: 1.2;
}

.description {
  font-size: 1.25rem;
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 2.5rem;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  margin-bottom: 3rem;
  flex-wrap: wrap;
}

.cta-button {
  padding: 1rem 2rem;
  border: none;
  border-radius: 0.75rem;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.cta-button.primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
}

.cta-button.primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

.cta-button.secondary {
  background: transparent;
  color: #374151;
  border: 2px solid #d1d5db;
}

.cta-button.secondary:hover {
  border-color: #f59e0b;
  color: #f59e0b;
}

.cta-button.large {
  padding: 1.25rem 3rem;
  font-size: 1.25rem;
}

.trust-indicators {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.stat {
  text-align: center;
}

.stat .number {
  display: block;
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat .label {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Interactive Demo */
.demo-section {
  display: flex;
  justify-content: center;
  align-items: center;
}

.interactive-demo {
  width: 400px;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.5s ease;
  position: relative;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.interactive-demo::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1));
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.interactive-demo.active {
  transform: scale(1.05) rotateY(5deg) rotateX(5deg);
  box-shadow: 0 25px 50px rgba(59, 130, 246, 0.2);
}

.interactive-demo.active::before {
  opacity: 1;
}

.demo-header {
  background: #f3f4f6;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.demo-controls {
  display: flex;
  gap: 0.5rem;
}

.control {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.control.red { background: #ef4444; }
.control.yellow { background: #f59e0b; }
.control.green { background: #10b981; }

.demo-title {
  font-weight: 600;
  color: #374151;
}

.demo-content {
  padding: 2rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 2rem;
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #d97706);
  transition: width 1s ease;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.progress::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

.demo-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
}

.demo-stat {
  text-align: center;
}

.demo-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.demo-label {
  font-size: 0.75rem;
  color: #6b7280;
}

.ai-recommendation {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #f0f9ff;
  padding: 1rem;
  border-radius: 0.5rem;
  border-left: 4px solid #0ea5e9;
}

.ai-icon {
  font-size: 1.5rem;
}

.ai-text {
  font-size: 0.875rem;
  color: #0c4a6e;
}

/* Problem Section */
.problem-section {
  padding: 4rem 0;
  background: #f9fafb;
}

.before-after {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 2rem;
  align-items: center;
  max-width: 800px;
  margin: 0 auto;
}

.before, .after {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.before h3 {
  color: #dc2626;
  margin-bottom: 1rem;
}

.after h3 {
  color: #059669;
  margin-bottom: 1rem;
}

.before ul li, .after ul li {
  margin-bottom: 0.5rem;
  padding-left: 1rem;
}

.arrow {
  font-size: 2rem;
  color: #f59e0b;
  font-weight: bold;
}

/* Social Proof Section */
.social-proof-section {
  padding: 4rem 0;
}

.social-proof-section h2 {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 3rem;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
}

.testimonial-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.testimonial-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.testimonial-avatar {
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

.testimonial-info h4 {
  font-weight: 600;
  color: #1f2937;
}

.testimonial-info span {
  font-size: 0.875rem;
  color: #6b7280;
}

.testimonial-card p {
  font-style: italic;
  color: #4b5563;
  margin-bottom: 1rem;
}

.result {
  background: #f0fdf4;
  color: #166534;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
}

.company-logos {
  text-align: center;
}

.company-logos h3 {
  color: #6b7280;
  margin-bottom: 2rem;
}

.logos-grid {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.logo {
  padding: 1rem 2rem;
  background: #f3f4f6;
  border-radius: 0.5rem;
  font-weight: 600;
  color: #374151;
}

/* Pricing Section */
.pricing-section {
  padding: 4rem 0;
  background: #f9fafb;
}

.pricing-section h2 {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
}

.pricing-subtitle {
  text-align: center;
  color: #6b7280;
  font-size: 1.125rem;
  margin-bottom: 3rem;
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.pricing-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: relative;
  text-align: center;
}

.pricing-card.popular {
  border: 3px solid #f59e0b;
  transform: scale(1.05);
}

.popular-badge {
  position: absolute;
  top: -15px;
  left: 50%;
  transform: translateX(-50%);
  background: #f59e0b;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.pricing-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin-bottom: 2rem;
}

.currency {
  font-size: 1.5rem;
  color: #6b7280;
}

.amount {
  font-size: 3rem;
  font-weight: 800;
  color: #1f2937;
}

.period {
  font-size: 1rem;
  color: #6b7280;
}

.features {
  list-style: none;
  padding: 0;
  margin-bottom: 2rem;
}

.features li {
  padding: 0.5rem 0;
  color: #4b5563;
}

.pricing-btn {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f3f4f6;
  color: #374151;
}

.pricing-btn.primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.pricing-btn:hover {
  transform: translateY(-2px);
}

/* FAQ Section */
.faq-section {
  padding: 4rem 0;
}

.faq-section h2 {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 3rem;
}

.faq-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.faq-item {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.faq-item h3 {
  color: #1f2937;
  font-weight: 600;
  margin-bottom: 1rem;
}

.faq-item p {
  color: #4b5563;
  line-height: 1.6;
}

/* Final CTA Section */
.final-cta-section {
  padding: 4rem 0;
  background: linear-gradient(135deg, #1f2937, #374151);
  color: white;
  text-align: center;
}

.cta-content h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.cta-content p {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.guarantee {
  font-size: 0.875rem;
  opacity: 0.8;
  margin-top: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-content {
    grid-template-columns: 1fr;
    gap: 2rem;
    text-align: center;
  }
  
  .main-title {
    font-size: 2.5rem;
  }
  
  .sub-title {
    font-size: 1.5rem;
  }
  
  .before-after {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .arrow {
    transform: rotate(90deg);
  }
  
  .trust-indicators {
    justify-content: center;
  }
  
  .interactive-demo {
    width: 100%;
    max-width: 350px;
  }
  
  .pricing-card.popular {
    transform: none;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
}

@media (max-width: 480px) {
  .main-title {
    font-size: 2rem;
  }
  
  .container {
    padding: 0 1rem;
  }
  
  .testimonials-grid,
  .faq-grid {
    grid-template-columns: 1fr;
  }
}

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* 3D perspective for interactive elements */
.demo-section {
  perspective: 1000px;
}

/* Enhanced card hover effects */
.testimonial-card,
.faq-item,
.pricing-card {
  transition: all 0.3s ease;
  transform-style: preserve-3d;
}

.testimonial-card:hover,
.faq-item:hover {
  transform: translateY(-5px) rotateX(5deg);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.pricing-card:hover {
  transform: translateY(-10px) rotateX(5deg);
  box-shadow: 0 20px 40px rgba(59, 130, 246, 0.15);
}

/* Gradient text utilities */
.bg-clip-text {
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Enhanced button animations */
.cta-button,
.pricing-btn {
  position: relative;
  overflow: hidden;
}

.cta-button::before,
.pricing-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.cta-button:hover::before,
.pricing-btn:hover::before {
  left: 100%;
}
</style>