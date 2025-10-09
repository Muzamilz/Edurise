<template>
  <div class="landing-page">
    <!-- Background Shapes -->
    <div class="background-shapes">
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



    <!-- Main Content -->
    <main class="main-content">
      <div class="container">
        <div class="content-wrapper">
          <!-- Left Side - Content -->
          <div class="text-section">
            <div class="badge">
              <span class="badge-text">Digital Learning Program</span>
            </div>
            
            <h1 class="main-title">
              Develop <span class="highlight">Yourself</span>
            </h1>
            
            <h2 class="sub-title">
              In a Different and Distinguished Way
            </h2>
            
            <p class="description">
              Our platform combines experience and modern technology to provide you with an integrated educational experience through online educational programs that suit your time and aspirations.
            </p>
            
            <router-link to="/courses" class="cta-button">
              Explore Programs
            </router-link>
          </div>

          <!-- Right Side - Image -->
          <div class="image-section">
            <div class="student-image">
              <div class="student-placeholder">
                <div class="placeholder-content">
                  <div class="laptop-icon">💻</div>
                  <div class="student-icon">👩‍🎓</div>
                  <div class="success-icon">👍</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

onMounted(() => {
  // Add any initialization logic here
})
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #fef3e2 0%, #ffffff 50%, #f0f9ff 100%);
}

/* Background Shapes */
.background-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.shape {
  position: absolute;
  border-radius: 50% 30% 70% 40%;
  opacity: 0.6;
}

.shape-1 {
  width: 400px;
  height: 300px;
  background: linear-gradient(45deg, #fbbf24, #f59e0b);
  top: -50px;
  right: -100px;
  transform: rotate(15deg);
}

.shape-2 {
  width: 300px;
  height: 400px;
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  bottom: -100px;
  left: -50px;
  transform: rotate(-20deg);
}

.shape-3 {
  width: 200px;
  height: 250px;
  background: linear-gradient(90deg, #dbeafe, #bfdbfe);
  top: 50%;
  right: 10%;
  transform: rotate(45deg);
  opacity: 0.4;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(45deg, #fbbf24, #f59e0b);
  opacity: 0.3;
}

.circle-1 {
  width: 80px;
  height: 80px;
  top: 20%;
  right: 15%;
}

.circle-2 {
  width: 60px;
  height: 60px;
  top: 60%;
  right: 25%;
  background: linear-gradient(45deg, #fed7aa, #fdba74);
}

.circle-3 {
  width: 40px;
  height: 40px;
  top: 30%;
  right: 5%;
  background: linear-gradient(45deg, #dbeafe, #93c5fd);
}

.circle-4 {
  width: 100px;
  height: 100px;
  bottom: 30%;
  right: 8%;
  opacity: 0.2;
}

.circle-5 {
  width: 30px;
  height: 30px;
  top: 70%;
  right: 35%;
  background: linear-gradient(45deg, #fef3e2, #fed7aa);
}

.circle-6 {
  width: 50px;
  height: 50px;
  bottom: 20%;
  left: 20%;
  background: linear-gradient(45deg, #dbeafe, #bfdbfe);
}

.circle-7 {
  width: 70px;
  height: 70px;
  top: 15%;
  left: 10%;
  opacity: 0.25;
}

/* Container for landing page content */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Main Content */
.main-content {
  position: relative;
  z-index: 5;
  padding: 4rem 0;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  min-height: 70vh;
}

/* Image Section */
.image-section {
  display: flex;
  justify-content: center;
  align-items: center;
}

.student-image {
  position: relative;
  width: 400px;
  height: 500px;
  border-radius: 2rem;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, #fef3e2, #ffffff);
  display: flex;
  align-items: center;
  justify-content: center;
}

.student-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  border-radius: 2rem;
  position: relative;
  overflow: hidden;
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  z-index: 2;
}

.laptop-icon,
.student-icon,
.success-icon {
  font-size: 4rem;
  animation: float 3s ease-in-out infinite;
}

.student-icon {
  animation-delay: -1s;
}

.success-icon {
  animation-delay: -2s;
  position: absolute;
  top: 20%;
  right: 20%;
  font-size: 2rem;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* Text Section */
.text-section {
  text-align: left;
  direction: ltr;
}

.badge {
  display: inline-block;
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  margin-bottom: 1.5rem;
  position: relative;
}

.badge::before {
  content: '';
  position: absolute;
  left: -10px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-right: 10px solid #fed7aa;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
}

.badge-text {
  color: #92400e;
  font-weight: 600;
  font-size: 0.875rem;
}

.main-title {
  font-size: 3.5rem;
  font-weight: 800;
  color: #1f2937;
  margin: 0 0 1rem 0;
  line-height: 1.1;
}

.highlight {
  color: #f59e0b;
  position: relative;
}

.sub-title {
  font-size: 2rem;
  font-weight: 700;
  color: #374151;
  margin: 0 0 2rem 0;
  line-height: 1.2;
}

.description {
  font-size: 1.125rem;
  color: #6b7280;
  line-height: 1.6;
  margin-bottom: 2.5rem;
  max-width: 500px;
  margin-right: auto;
}

.cta-button {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 1rem 2.5rem;
  border: none;
  border-radius: 0.75rem;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
  text-decoration: none;
  display: inline-block;
}

.cta-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

/* Responsive Design */
@media (max-width: 768px) {
  .content-wrapper {
    grid-template-columns: 1fr;
    gap: 2rem;
    text-align: center;
  }
  
  .text-section {
    text-align: center;
  }
  
  .main-title {
    font-size: 2.5rem;
  }
  
  .sub-title {
    font-size: 1.5rem;
  }
  
  .student-image {
    width: 300px;
    height: 400px;
  }
  

  
  .description {
    margin-right: 0;
  }
}

@media (max-width: 480px) {

  
  .main-title {
    font-size: 2rem;
  }
  
  .student-image {
    width: 250px;
    height: 350px;
  }
}
</style>