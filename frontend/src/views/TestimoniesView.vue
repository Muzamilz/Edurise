<template>
  <div class="testimonies-view">
    <div class="container">
      <div class="page-header">
        <h1>Testimonies</h1>
        <p>Hear from our amazing community of learners and educators</p>
      </div>

      <div class="testimonies-grid">
        <div class="testimony-card">
          <div class="stars">⭐⭐⭐⭐⭐</div>
          <p class="quote">
            "Edurise has transformed my learning experience. The interactive courses 
            and supportive community have helped me achieve my goals faster than I ever imagined."
          </p>
          <div class="author">
            <div class="avatar">EW</div>
            <div class="info">
              <h4>Emma Wilson</h4>
              <span>Computer Science Student</span>
            </div>
          </div>
        </div>

        <div class="testimony-card">
          <div class="stars">⭐⭐⭐⭐⭐</div>
          <p class="quote">
            "As an educator, Edurise provides me with all the tools I need to create 
            engaging content and connect with students worldwide. It's incredible!"
          </p>
          <div class="author">
            <div class="avatar">JR</div>
            <div class="info">
              <h4>Dr. James Rodriguez</h4>
              <span>Mathematics Instructor</span>
            </div>
          </div>
        </div>

        <div class="testimony-card">
          <div class="stars">⭐⭐⭐⭐⭐</div>
          <p class="quote">
            "The flexibility of learning at my own pace while having access to 
            expert instructors has made all the difference in my career development."
          </p>
          <div class="author">
            <div class="avatar">SC</div>
            <div class="info">
              <h4>Sarah Chen</h4>
              <span>Marketing Professional</span>
            </div>
          </div>
        </div>

        <div class="testimony-card">
          <div class="stars">⭐⭐⭐⭐⭐</div>
          <p class="quote">
            "Edurise's platform is intuitive and powerful. I've been able to reach 
            students globally and share my passion for teaching like never before."
          </p>
          <div class="author">
            <div class="avatar">MG</div>
            <div class="info">
              <h4>Prof. Maria Garcia</h4>
              <span>Language Arts Teacher</span>
            </div>
          </div>
        </div>

        <div class="testimony-card">
          <div class="stars">⭐⭐⭐⭐⭐</div>
          <p class="quote">
            "The community support and interactive features make learning enjoyable 
            and effective. I've completed 5 courses and earned 3 certifications!"
          </p>
          <div class="author">
            <div class="avatar">AT</div>
            <div class="info">
              <h4>Alex Thompson</h4>
              <span>Lifelong Learner</span>
            </div>
          </div>
        </div>

        <div class="testimony-card">
          <div class="stars">⭐⭐⭐⭐⭐</div>
          <p class="quote">
            "Edurise has helped me transition into a new career field. The courses 
            are comprehensive and the instructors are incredibly supportive."
          </p>
          <div class="author">
            <div class="avatar">MP</div>
            <div class="info">
              <h4>Michael Park</h4>
              <span>Career Changer</span>
            </div>
          </div>
        </div>
      </div>

      <div class="cta-section">
        <h2>Join Our Community</h2>
        <p>Start your learning journey today and become part of our success stories</p>
        <div class="cta-buttons">
          <router-link to="/auth/register" class="btn btn-primary">Get Started</router-link>
          <router-link to="/courses" class="btn btn-outline">Browse Courses</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component logic can be added here
</script>

<style scoped>
.testimonies-view {
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

.testimonies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
}

.testimony-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.testimony-card:hover {
  transform: translateY(-5px);
}

.stars {
  font-size: 1.25rem;
  margin-bottom: 1rem;
}

.quote {
  font-size: 1rem;
  line-height: 1.6;
  color: #6b7280;
  margin-bottom: 1.5rem;
  font-style: italic;
}

.author {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar {
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

.info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.info span {
  font-size: 0.875rem;
  color: #6b7280;
}

.cta-section {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.cta-section h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.cta-section p {
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

.btn {
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}

.btn-outline {
  background: transparent;
  color: #f59e0b;
  border: 2px solid #f59e0b;
}

.btn-outline:hover {
  background: #f59e0b;
  color: white;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .testimonies-grid {
    grid-template-columns: 1fr;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style>