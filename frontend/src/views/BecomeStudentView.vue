<template>
  <div class="become-student-view">
    <div class="container">
      <div class="page-header">
        <h1>Become a Student</h1>
        <p>Start your learning journey today</p>
      </div>

      <div class="content">
        <section class="hero-section">
          <div class="hero-content">
            <h2>Unlock Your Potential</h2>
            <p>
              Join millions of learners who are advancing their careers and achieving their goals 
              through our comprehensive learning platform.
            </p>
            <div class="features-grid">
              <div class="feature-card">
                <div class="feature-icon">📚</div>
                <h3>Unlimited Access</h3>
                <p>Access thousands of courses across multiple disciplines</p>
              </div>
              <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <h3>Personalized Learning</h3>
                <p>AI-powered recommendations tailored to your goals</p>
              </div>
              <div class="feature-card">
                <div class="feature-icon">🏆</div>
                <h3>Certificates</h3>
                <p>Earn recognized certificates to boost your career</p>
              </div>
            </div>
          </div>
        </section>

        <section class="signup-section">
          <h2>Ready to Start Learning?</h2>
          <p>Join our community and begin your transformation today</p>
          <div class="cta-buttons">
            <router-link to="/auth/register" class="cta-button primary">
              Sign Up Free
            </router-link>
            <router-link to="/courses" class="cta-button secondary">
              Browse Courses
            </router-link>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component logic can be added here
</script>

<style scoped>
.become-student-view {
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

.hero-section {
  margin-bottom: 4rem;
}

.hero-content h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  text-align: center;
  margin-bottom: 1rem;
}

.hero-content p {
  font-size: 1.125rem;
  color: #6b7280;
  text-align: center;
  margin-bottom: 3rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.feature-card p {
  color: #6b7280;
}

.signup-section {
  text-align: center;
  background: white;
  padding: 3rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.signup-section h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.signup-section p {
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

.cta-button {
  display: inline-block;
  padding: 1rem 2rem;
  text-decoration: none;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.cta-button.primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.cta-button.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}

.cta-button.secondary {
  background: transparent;
  color: #f59e0b;
  border: 2px solid #f59e0b;
}

.cta-button.secondary:hover {
  background: #f59e0b;
  color: white;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .signup-section {
    padding: 2rem;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style>