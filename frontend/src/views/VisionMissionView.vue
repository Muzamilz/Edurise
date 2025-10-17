<template>
  <div class="vision-mission-view">
    <div class="container">
      <div class="page-header">
        <h1>Vision, Mission, Goals & Values</h1>
        <p>Our guiding principles and aspirations</p>
      </div>

      <div class="content">
        <section class="vision-section">
          <div class="section-card">
            <div class="icon">🎯</div>
            <h2>Our Vision</h2>
            <p>
              To be the leading global platform that democratizes education by making quality learning 
              accessible to everyone, everywhere, fostering a world where knowledge knows no boundaries.
            </p>
          </div>
        </section>

        <section class="mission-section">
          <div class="section-card">
            <div class="icon">🚀</div>
            <h2>Our Mission</h2>
            <p>
              We empower educators and learners through innovative technology, creating engaging, 
              personalized learning experiences that inspire growth, creativity, and lifelong learning.
            </p>
          </div>
        </section>

        <section class="goals-section">
          <div class="section-card">
            <div class="icon">📈</div>
            <h2>Our Goals</h2>
            <ul>
              <li>Provide accessible, high-quality education to learners worldwide</li>
              <li>Support educators with cutting-edge tools and resources</li>
              <li>Foster inclusive learning communities</li>
              <li>Continuously innovate educational technology</li>
              <li>Bridge the gap between traditional and digital learning</li>
            </ul>
          </div>
        </section>

        <section class="values-section">
          <div class="section-card">
            <div class="icon">💎</div>
            <h2>Our Values</h2>
            <div class="values-grid">
              <div class="value-item">
                <h3>Excellence</h3>
                <p>We strive for the highest quality in everything we do</p>
              </div>
              <div class="value-item">
                <h3>Innovation</h3>
                <p>We embrace new ideas and technologies to enhance learning</p>
              </div>
              <div class="value-item">
                <h3>Inclusivity</h3>
                <p>We believe education should be accessible to all</p>
              </div>
              <div class="value-item">
                <h3>Integrity</h3>
                <p>We operate with honesty, transparency, and ethical standards</p>
              </div>
              <div class="value-item">
                <h3>Collaboration</h3>
                <p>We foster partnerships and community-driven learning</p>
              </div>
              <div class="value-item">
                <h3>Growth</h3>
                <p>We support continuous learning and personal development</p>
              </div>
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
.vision-mission-view {
  min-height: 100vh;
  padding: 2rem 0;
  background: linear-gradient(135deg, #fef3e2 0%, #ffffff 100%);
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
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section-card {
  background: white;
  padding: 3rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.section-card h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1.5rem;
}

.section-card p {
  font-size: 1.125rem;
  line-height: 1.7;
  color: #6b7280;
  max-width: 800px;
  margin: 0 auto;
}

.section-card ul {
  text-align: left;
  max-width: 600px;
  margin: 0 auto;
}

.section-card li {
  font-size: 1.125rem;
  line-height: 1.7;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.values-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.value-item {
  text-align: center;
  padding: 1.5rem;
  background: #fef3e2;
  border-radius: 0.5rem;
}

.value-item h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 0.5rem;
}

.value-item p {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .section-card {
    padding: 2rem;
  }
  
  .values-grid {
    grid-template-columns: 1fr;
  }
}
</style>