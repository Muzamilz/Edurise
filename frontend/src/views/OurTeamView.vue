<template>
  <div class="our-team-view">
    <div class="container">
      <div class="page-header">
        <h1>Our Team</h1>
        <p>Meet the passionate individuals behind Edurise</p>
      </div>

      <div class="content">
        <section class="leadership-section">
          <h2>Leadership Team</h2>
          <div class="team-grid">
            <div class="team-member">
              <div class="member-avatar">JS</div>
              <h3>John Smith</h3>
              <p class="role">Chief Executive Officer</p>
              <p class="bio">
                With over 15 years in educational technology, John leads our vision 
                to transform learning experiences worldwide.
              </p>
            </div>
            
            <div class="team-member">
              <div class="member-avatar">SJ</div>
              <h3>Sarah Johnson</h3>
              <p class="role">Chief Technology Officer</p>
              <p class="bio">
                Sarah brings cutting-edge technical expertise to create innovative 
                learning platforms that scale globally.
              </p>
            </div>
            
            <div class="team-member">
              <div class="member-avatar">MC</div>
              <h3>Michael Chen</h3>
              <p class="role">Chief Product Officer</p>
              <p class="bio">
                Michael focuses on user experience and product strategy to ensure 
                our platform meets learners' evolving needs.
              </p>
            </div>
          </div>
        </section>

        <section class="departments-section">
          <h2>Our Departments</h2>
          <div class="departments-grid">
            <div class="department-card">
              <div class="dept-icon">💻</div>
              <h3>Engineering</h3>
              <p>Building robust, scalable technology solutions</p>
              <span class="team-count">12 members</span>
            </div>
            
            <div class="department-card">
              <div class="dept-icon">🎨</div>
              <h3>Design</h3>
              <p>Creating intuitive and engaging user experiences</p>
              <span class="team-count">6 members</span>
            </div>
            
            <div class="department-card">
              <div class="dept-icon">📚</div>
              <h3>Education</h3>
              <p>Developing curriculum and learning methodologies</p>
              <span class="team-count">8 members</span>
            </div>
            
            <div class="department-card">
              <div class="dept-icon">📈</div>
              <h3>Marketing</h3>
              <p>Connecting with learners and educators globally</p>
              <span class="team-count">5 members</span>
            </div>
            
            <div class="department-card">
              <div class="dept-icon">🤝</div>
              <h3>Support</h3>
              <p>Ensuring exceptional customer experience</p>
              <span class="team-count">7 members</span>
            </div>
            
            <div class="department-card">
              <div class="dept-icon">⚖️</div>
              <h3>Operations</h3>
              <p>Managing business operations and growth</p>
              <span class="team-count">4 members</span>
            </div>
          </div>
        </section>

        <section class="join-team-section">
          <div class="join-card">
            <h2>Join Our Team</h2>
            <p>
              We're always looking for talented individuals who share our passion 
              for education and innovation. Explore career opportunities with us.
            </p>
            <router-link to="/careers" class="btn btn-primary">View Open Positions</router-link>
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
.our-team-view {
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

.leadership-section h2,
.departments-section h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  text-align: center;
  margin-bottom: 2rem;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.team-member {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease;
}

.team-member:hover {
  transform: translateY(-5px);
}

.member-avatar {
  width: 120px;
  height: 120px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 2rem;
  border: 4px solid #f59e0b;
}

.team-member h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.role {
  font-size: 1rem;
  font-weight: 500;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.bio {
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.6;
}

.departments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.department-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease;
}

.department-card:hover {
  transform: translateY(-3px);
}

.dept-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.department-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 0.5rem;
}

.department-card p {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 1rem;
}

.team-count {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.join-team-section {
  text-align: center;
}

.join-card {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 3rem;
  border-radius: 1rem;
  max-width: 600px;
  margin: 0 auto;
}

.join-card h2 {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.join-card p {
  font-size: 1.125rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.btn {
  display: inline-block;
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary {
  background: white;
  color: #f59e0b;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .team-grid {
    grid-template-columns: 1fr;
  }
  
  .departments-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .join-card {
    padding: 2rem;
  }
}
</style>