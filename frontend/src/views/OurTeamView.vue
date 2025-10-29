<template>
  <div class="our-team-view">
    <div class="container">
      <div class="page-header">
        <h1>Our Team</h1>
        <p>Meet the passionate individuals behind Edurise</p>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Loading team members...</p>
      </div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="loadTeamMembers" class="btn btn-primary">Try Again</button>
      </div>

      <div v-else class="content">
        <section 
          v-for="(members, department) in teamByDepartment" 
          :key="department"
          class="department-section"
        >
          <h2>{{ department }}</h2>
          <div class="team-grid">
            <div 
              v-for="member in members" 
              :key="member.id" 
              class="team-member"
            >
              <div class="member-avatar">
                <img 
                  v-if="member.profile_image" 
                  :src="member.profile_image" 
                  :alt="member.name"
                  class="avatar-image"
                />
                <span v-else class="avatar-initials">
                  {{ getInitials(member.name) }}
                </span>
              </div>
              <h3>{{ member.name }}</h3>
              <p class="role">{{ member.role }}</p>
              <p class="bio">{{ member.bio }}</p>
              <div v-if="member.linkedin_url || member.twitter_url" class="social-links">
                <a 
                  v-if="member.linkedin_url" 
                  :href="member.linkedin_url" 
                  target="_blank"
                  class="social-link"
                >
                  LinkedIn
                </a>
                <a 
                  v-if="member.twitter_url" 
                  :href="member.twitter_url" 
                  target="_blank"
                  class="social-link"
                >
                  Twitter
                </a>
              </div>
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
import { ref, onMounted, computed } from 'vue'
import { contentService, type TeamMember } from '@/services/content'

const teamMembers = ref<TeamMember[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map((word: any) => word.charAt(0).toUpperCase())
    .join('')
    .substring(0, 2)
}

const teamByDepartment = computed(() => {
  const grouped: Record<string, TeamMember[]> = {}
  
  teamMembers.value.forEach(member => {
    const dept = member.department.charAt(0).toUpperCase() + member.department.slice(1)
    if (!grouped[dept]) {
      grouped[dept] = []
    }
    grouped[dept].push(member)
  })
  
  return grouped
})

const loadTeamMembers = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await contentService.getTeamMembers()
    // Handle the API response structure: { success: true, data: [...] }
    teamMembers.value = Array.isArray(response) ? response : (response.data || (response as any).results || [])
  } catch (err) {
    console.error('Error loading team members:', err)
    error.value = 'Failed to load team members. Please try again later.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTeamMembers()
})
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

.department-section h2 {
  font-size: 2rem;
  font-weight: 600;
  color: #f59e0b;
  text-align: center;
  margin-bottom: 2rem;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  margin-bottom: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  color: #dc2626;
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
  overflow: hidden;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-initials {
  font-size: 2rem;
  font-weight: 700;
}

.social-links {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.social-link {
  padding: 0.25rem 0.75rem;
  background: #f59e0b;
  color: white;
  text-decoration: none;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  transition: background 0.3s ease;
}

.social-link:hover {
  background: #d97706;
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