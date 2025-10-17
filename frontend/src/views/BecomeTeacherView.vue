<template>
  <div class="become-teacher-view">
    <div class="container">
      <div class="page-header">
        <h1>Become a Teacher</h1>
        <p>Share your expertise and inspire learners worldwide</p>
      </div>

      <div class="content">
        <section class="hero-section">
          <div class="hero-content">
            <h2>Transform Lives Through Teaching</h2>
            <p>
              Join thousands of educators who are making a difference on our platform. 
              Share your knowledge, build your reputation, and earn while you teach.
            </p>
            <div class="benefits-grid">
              <div class="benefit-card">
                <div class="benefit-icon">💰</div>
                <h3>Earn While Teaching</h3>
                <p>Set your own rates and keep up to 85% of your earnings</p>
              </div>
              <div class="benefit-card">
                <div class="benefit-icon">🌍</div>
                <h3>Global Reach</h3>
                <p>Teach students from around the world, anytime</p>
              </div>
              <div class="benefit-card">
                <div class="benefit-icon">🛠️</div>
                <h3>Professional Tools</h3>
                <p>Access cutting-edge teaching tools and resources</p>
              </div>
            </div>
          </div>
        </section>

        <section class="application-section">
          <h2>Ready to Get Started?</h2>
          <p>Apply now and join our community of expert educators</p>
          <router-link to="/auth/register" class="cta-button">
            Start Your Application
          </router-link>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component logic can be added here
</script>

<style scoped>
.become-teacher-view {
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

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.benefit-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease;
}

.benefit-card:hover {
  transform: translateY(-5px);
}

.benefit-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.benefit-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.benefit-card p {
  color: #6b7280;
}

.application-section {
  text-align: center;
  background: white;
  padding: 3rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.application-section h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.application-section p {
  font-size: 1.125rem;
  color: #6b7280;
  margin-bottom: 2rem;
}

.cta-button {
  display: inline-block;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  text-decoration: none;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .benefits-grid {
    grid-template-columns: 1fr;
  }
  
  .application-section {
    padding: 2rem;
  }
}
</style>