<template>
  <div class="user-profile">
    <div class="profile-header">
      <div class="profile-badge">👤 PROFILE</div>
      <h1>My Profile</h1>
      <p>Manage your account settings and personal information</p>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading your profile...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Unable to load profile</h3>
      <p>{{ error }}</p>
      <button @click="handleRetry" class="retry-btn">Try Again</button>
    </div>

    <div v-else class="profile-content">
      <div class="profile-overview">
        <div class="avatar-section">
          <div class="avatar-container">
            <img 
              :src="userProfile?.avatar || '/default-avatar.png'" 
              :alt="fullName"
              class="avatar-image"
            />
          </div>
        </div>
        
        <div class="profile-info">
          <h2>{{ fullName || 'User' }}</h2>
          <p class="email">{{ currentUser?.email }}</p>
          <p class="role">{{ formatRole((currentUser as any)?.role || 'student') }}</p>
        </div>
      </div>

      <div class="profile-stats">
        <div class="stat-card">
          <div class="stat-icon">📚</div>
          <h3>Courses</h3>
          <p class="stat-number">12</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🏆</div>
          <h3>Certificates</h3>
          <p class="stat-number">3</p>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⏱️</div>
          <h3>Hours Learned</h3>
          <p class="stat-number">45</p>
        </div>
      </div>

      <div class="profile-section">
        <div class="section-header">
          <h3>Personal Information</h3>
        </div>
        
        <div class="section-content">
          <div class="info-grid">
            <div class="info-item">
              <label>First Name</label>
              <p>{{ currentUser?.first_name || 'Not set' }}</p>
            </div>
            <div class="info-item">
              <label>Last Name</label>
              <p>{{ currentUser?.last_name || 'Not set' }}</p>
            </div>
            <div class="info-item">
              <label>Email</label>
              <p>{{ currentUser?.email }}</p>
            </div>
            <div class="info-item">
              <label>Phone</label>
              <p>{{ userProfile?.phone_number || 'Not set' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useProfile } from '@/composables/useProfile'

const { 
  userProfile, 
  isLoading, 
  error, 
  currentUser,
  fullName,
  loadUserProfile,
  clearError
} = useProfile()

const handleRetry = async () => {
  clearError()
  await loadUserProfile()
}

const formatRole = (role: string) => {
  return role.charAt(0).toUpperCase() + role.slice(1).replace('_', ' ')
}

onMounted(async () => {
  await loadUserProfile()
})
</script>

<style scoped>
.user-profile {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.profile-header {
  margin-bottom: 2rem;
}

.profile-badge {
  display: inline-block;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
}

.profile-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.profile-header p {
  color: #6b7280;
  font-size: 1.125rem;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.profile-overview {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  display: flex;
  align-items: center;
  gap: 2rem;
}

.avatar-container {
  width: 120px;
  height: 120px;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid rgba(245, 158, 11, 0.2);
}

.profile-info h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.email {
  color: #6b7280;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.role {
  color: #f59e0b;
  font-weight: 600;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15);
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.stat-card h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #f59e0b;
  margin: 0;
}

.profile-section {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.section-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1.5rem 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-item p {
  color: #6b7280;
  font-size: 1rem;
  margin: 0;
}

.retry-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

@media (max-width: 768px) {
  .user-profile {
    padding: 1rem;
  }
  
  .profile-overview {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-stats {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>