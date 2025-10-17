<template>
  <div class="about-view">
    <div class="container">
      <div class="page-header">
        <h1>About Us</h1>
        <p>Learn more about our mission and values</p>
      </div>

      <div class="content">
        <section class="intro-section">
          <h2>Welcome to Edurise</h2>
          <p>
            Edurise is a comprehensive learning management system designed to connect educators and learners 
            in a seamless digital environment. We believe in making quality education accessible to everyone, 
            anywhere, anytime.
          </p>
        </section>

        <section class="features-section">
          <h2>What We Offer</h2>
          <div class="features-grid">
            <div class="feature-card">
              <h3>Interactive Learning</h3>
              <p>Engage with dynamic content and interactive lessons designed to enhance your learning experience.</p>
            </div>
            <div class="feature-card">
              <h3>Expert Instructors</h3>
              <p>Learn from qualified and experienced teachers who are passionate about sharing their knowledge.</p>
            </div>
            <div class="feature-card">
              <h3>Flexible Schedule</h3>
              <p>Study at your own pace with our flexible scheduling system that fits your lifestyle.</p>
            </div>
            <div class="feature-card">
              <h3>Community Support</h3>
              <p>Join a vibrant community of learners and educators supporting each other's growth.</p>
            </div>
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
.about-view {
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

.content {
  max-width: 800px;
  margin: 0 auto;
}

.intro-section {
  margin-bottom: 3rem;
}

.intro-section h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.intro-section p {
  font-size: 1.125rem;
  line-height: 1.7;
  color: #6b7280;
}

.features-section h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 2rem;
  text-align: center;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.feature-card p {
  color: #6b7280;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>