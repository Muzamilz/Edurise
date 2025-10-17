<template>
  <div class="auth-page">
    <!-- Animated Background Elements -->
    <div class="background-elements">
      <div class="floating-shape shape-1"></div>
      <div class="floating-shape shape-2"></div>
      <div class="floating-shape shape-3"></div>
      <div class="floating-circle circle-1"></div>
      <div class="floating-circle circle-2"></div>
      <div class="floating-circle circle-3"></div>
      <div class="floating-circle circle-4"></div>
    </div>

    <div class="auth-container">
      <div class="auth-brand">
        <div class="brand-logo">
          <div class="logo-circle">
            <span class="logo-text">E</span>
          </div>
        </div>
        <h1 class="brand-title">Join Edurise</h1>
        <p class="brand-subtitle">Create your account and start learning today</p>
      </div>
      
      <div class="form-container">
        <RegisterForm />
      </div>

      <!-- Social Proof -->
      <div class="social-proof">
        <p>Join 10,000+ learners worldwide</p>
        <div class="trust-badges">
          <div class="trust-badge">🎓 Expert Teachers</div>
          <div class="trust-badge">📚 Quality Content</div>
          <div class="trust-badge">🏆 Certificates</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import RegisterForm from '@/components/auth/RegisterForm.vue'
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #92400e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  position: relative;
  overflow: hidden;
}

/* Animated Background Elements */
.background-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.floating-shape {
  position: absolute;
  border-radius: 50% 30% 70% 40%;
  opacity: 0.1;
  animation: float 8s ease-in-out infinite;
}

.shape-1 {
  width: 300px;
  height: 200px;
  background: linear-gradient(45deg, #fed7aa, #fdba74);
  top: 10%;
  left: -50px;
  animation-delay: 0s;
}

.shape-2 {
  width: 200px;
  height: 300px;
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  bottom: 10%;
  right: -50px;
  animation-delay: 2s;
}

.shape-3 {
  width: 150px;
  height: 200px;
  background: linear-gradient(90deg, #fdba74, #fb923c);
  top: 50%;
  left: 10%;
  animation-delay: 4s;
}

.floating-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(45deg, #fed7aa, #fdba74);
  opacity: 0.15;
  animation: float 6s ease-in-out infinite;
}

.circle-1 { width: 60px; height: 60px; top: 20%; right: 15%; animation-delay: 1s; }
.circle-2 { width: 80px; height: 80px; top: 70%; left: 20%; animation-delay: 3s; }
.circle-3 { width: 40px; height: 40px; bottom: 30%; right: 25%; animation-delay: 5s; }
.circle-4 { width: 100px; height: 100px; top: 40%; right: 5%; animation-delay: 7s; }

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(5deg);
  }
}

.auth-container {
  width: 100%;
  max-width: 450px;
  position: relative;
  z-index: 10;
  animation: slideUp 0.8s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-brand {
  text-align: center;
  margin-bottom: 3rem;
  color: white;
}

.brand-logo {
  margin-bottom: 2rem;
  animation: logoFloat 3s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.logo-circle {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.logo-text {
  font-size: 2rem;
  font-weight: 800;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.brand-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  animation: titleGlow 2s ease-in-out infinite alternate;
}

@keyframes titleGlow {
  from {
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
  to {
    text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3), 0 0 20px rgba(255, 255, 255, 0.1);
  }
}

.brand-subtitle {
  font-size: 1.125rem;
  opacity: 0.9;
  margin-bottom: 0;
}

.form-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 2rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.form-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

.social-proof {
  text-align: center;
  color: white;
}

.social-proof p {
  font-size: 0.875rem;
  opacity: 0.8;
  margin-bottom: 1rem;
}

.trust-badges {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.trust-badge {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.trust-badge:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

@media (max-width: 480px) {
  .auth-container {
    max-width: 100%;
  }
  
  .form-container {
    padding: 2rem;
    border-radius: 15px;
  }
  
  .brand-title {
    font-size: 2rem;
  }
  
  .trust-badges {
    flex-direction: column;
    align-items: center;
  }
}
</style>