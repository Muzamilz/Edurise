<template>
  <div class="announcements-view">
    <div class="container">
      <div class="page-header">
        <h1>Announcements</h1>
        <p>Stay updated with the latest news and updates from Edurise</p>
      </div>

      <div class="announcements-list">
        <article class="announcement-card featured">
          <div class="announcement-badge">Featured</div>
          <div class="announcement-date">December 15, 2024</div>
          <h2>New AI-Powered Learning Assistant Now Available</h2>
          <p>
            We're excited to introduce our new AI learning assistant that provides 
            personalized study recommendations and instant help with course materials.
          </p>
          <router-link to="/announcements/ai-assistant" class="read-more">Read More →</router-link>
        </article>

        <article class="announcement-card">
          <div class="announcement-date">December 10, 2024</div>
          <h2>Winter Course Catalog Released</h2>
          <p>
            Explore our expanded winter course catalog featuring over 200 new courses 
            across technology, business, arts, and sciences.
          </p>
          <router-link to="/announcements/winter-catalog" class="read-more">Read More →</router-link>
        </article>

        <article class="announcement-card">
          <div class="announcement-date">December 5, 2024</div>
          <h2>Platform Maintenance Scheduled</h2>
          <p>
            Scheduled maintenance on December 20th from 2:00 AM to 4:00 AM EST to 
            improve platform performance and add new features.
          </p>
          <router-link to="/announcements/maintenance" class="read-more">Read More →</router-link>
        </article>

        <article class="announcement-card">
          <div class="announcement-date">November 28, 2024</div>
          <h2>Black Friday Course Sale - Up to 70% Off</h2>
          <p>
            Don't miss our biggest sale of the year! Get access to premium courses 
            at incredible discounts. Sale ends December 1st.
          </p>
          <router-link to="/announcements/black-friday" class="read-more">Read More →</router-link>
        </article>

        <article class="announcement-card">
          <div class="announcement-date">November 20, 2024</div>
          <h2>New Mobile App Features</h2>
          <p>
            Our mobile app now supports offline course downloads, push notifications 
            for live classes, and improved video streaming quality.
          </p>
          <router-link to="/announcements/mobile-update" class="read-more">Read More →</router-link>
        </article>

        <article class="announcement-card">
          <div class="announcement-date">November 15, 2024</div>
          <h2>Teacher Certification Program Launch</h2>
          <p>
            Introducing our new teacher certification program to help educators 
            enhance their skills and earn recognized credentials.
          </p>
          <router-link to="/announcements/teacher-certification" class="read-more">Read More →</router-link>
        </article>

        <article class="announcement-card">
          <div class="announcement-date">November 8, 2024</div>
          <h2>Student Success Stories Contest</h2>
          <p>
            Share your learning journey and win amazing prizes! Submit your success 
            story and inspire other learners in our community.
          </p>
          <router-link to="/announcements/success-contest" class="read-more">Read More →</router-link>
        </article>

        <article class="announcement-card">
          <div class="announcement-date">November 1, 2024</div>
          <h2>Enhanced Live Class Experience</h2>
          <p>
            We've upgraded our live class technology with better video quality, 
            interactive whiteboards, and breakout room capabilities.
          </p>
          <router-link to="/announcements/live-class-upgrade" class="read-more">Read More →</router-link>
        </article>
      </div>

      <div class="newsletter-signup">
        <h2>Stay Informed</h2>
        <p>Subscribe to our newsletter to receive the latest announcements directly in your inbox</p>
        <form class="newsletter-form">
          <input type="email" placeholder="Enter your email address" required>
          <button type="submit" class="btn btn-primary">Subscribe</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component logic can be added here
</script>

<style scoped>
.announcements-view {
  min-height: 100vh;
  padding: 2rem 0;
}

.container {
  max-width: 800px;
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

.announcements-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-bottom: 4rem;
}

.announcement-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  position: relative;
}

.announcement-card:hover {
  transform: translateY(-3px);
}

.announcement-card.featured {
  border: 2px solid #f59e0b;
  background: linear-gradient(135deg, #fef3e2, #ffffff);
}

.announcement-badge {
  position: absolute;
  top: -10px;
  right: 20px;
  background: #f59e0b;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.announcement-date {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 1rem;
}

.announcement-card h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.announcement-card p {
  font-size: 1rem;
  line-height: 1.6;
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.read-more {
  color: #f59e0b;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.read-more:hover {
  color: #d97706;
}

.newsletter-signup {
  background: white;
  padding: 3rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.newsletter-signup h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.newsletter-signup p {
  font-size: 1.125rem;
  color: #6b7280;
  margin-bottom: 2rem;
}

.newsletter-form {
  display: flex;
  gap: 1rem;
  max-width: 400px;
  margin: 0 auto;
}

.newsletter-form input {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.newsletter-form input:focus {
  outline: none;
  border-color: #f59e0b;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
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

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }
  
  .announcement-card {
    padding: 1.5rem;
  }
  
  .newsletter-form {
    flex-direction: column;
  }
  
  .newsletter-signup {
    padding: 2rem;
  }
}
</style>