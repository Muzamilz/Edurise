<template>
  <div class="student-guidelines-view">
    <div class="container">
      <div class="page-header">
        <h1>Student Guidelines</h1>
        <p>Everything you need to know for a successful learning experience</p>
      </div>

      <div class="content">
        <section class="getting-started">
          <h2>Getting Started</h2>
          <div class="steps-grid">
            <div class="step-card">
              <div class="step-number">1</div>
              <h3>Create Your Account</h3>
              <p>Sign up with your email and complete your profile</p>
            </div>
            <div class="step-card">
              <div class="step-number">2</div>
              <h3>Choose Your Courses</h3>
              <p>Browse our catalog and enroll in courses that match your goals</p>
            </div>
            <div class="step-card">
              <div class="step-number">3</div>
              <h3>Start Learning</h3>
              <p>Access your courses and begin your learning journey</p>
            </div>
          </div>
        </section>

        <section class="learning-tips">
          <h2>Learning Best Practices</h2>
          <div class="tips-grid">
            <div class="tip-card">
              <div class="tip-icon">⏰</div>
              <h3>Set a Schedule</h3>
              <p>Dedicate specific times for learning to build consistency</p>
            </div>
            <div class="tip-card">
              <div class="tip-icon">🎯</div>
              <h3>Set Clear Goals</h3>
              <p>Define what you want to achieve from each course</p>
            </div>
            <div class="tip-card">
              <div class="tip-icon">📝</div>
              <h3>Take Notes</h3>
              <p>Use our note-taking feature to capture key insights</p>
            </div>
            <div class="tip-card">
              <div class="tip-icon">🤝</div>
              <h3>Engage with Community</h3>
              <p>Participate in discussions and connect with peers</p>
            </div>
          </div>
        </section>

        <section class="platform-features">
          <h2>Platform Features</h2>
          <div class="features-list">
            <div class="feature-item">
              <h3>📱 Mobile Learning</h3>
              <p>Access your courses on any device, anywhere, anytime</p>
            </div>
            <div class="feature-item">
              <h3>📊 Progress Tracking</h3>
              <p>Monitor your learning progress with detailed analytics</p>
            </div>
            <div class="feature-item">
              <h3>🏆 Certificates</h3>
              <p>Earn certificates upon successful course completion</p>
            </div>
            <div class="feature-item">
              <h3>💬 Support</h3>
              <p>Get help from our support team whenever you need it</p>
            </div>
          </div>
        </section>

        <section class="policies">
          <h2>Important Policies</h2>
          <div class="policy-cards">
            <div class="policy-card">
              <h3>Academic Integrity</h3>
              <p>We expect all students to maintain honesty and integrity in their learning</p>
            </div>
            <div class="policy-card">
              <h3>Refund Policy</h3>
              <p>30-day money-back guarantee for all courses and subscriptions</p>
            </div>
            <div class="policy-card">
              <h3>Community Guidelines</h3>
              <p>Respectful and constructive interaction with all community members</p>
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
.student-guidelines-view {
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
  display: flex;
  flex-direction: column;
  gap: 4rem;
}

.getting-started h2,
.learning-tips h2,
.platform-features h2,
.policies h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  text-align: center;
  margin-bottom: 2rem;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.step-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease;
}

.step-card:hover {
  transform: translateY(-5px);
}

.step-number {
  width: 50px;
  height: 50px;
  background: #f59e0b;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 auto 1rem;
}

.step-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.step-card p {
  color: #6b7280;
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.tip-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease;
}

.tip-card:hover {
  transform: translateY(-5px);
}

.tip-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.tip-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.tip-card p {
  color: #6b7280;
}

.features-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-item {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.feature-item h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.feature-item p {
  color: #6b7280;
}

.policy-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.policy-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #f59e0b;
}

.policy-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.policy-card p {
  color: #6b7280;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .steps-grid,
  .tips-grid,
  .features-list,
  .policy-cards {
    grid-template-columns: 1fr;
  }
}
</style>