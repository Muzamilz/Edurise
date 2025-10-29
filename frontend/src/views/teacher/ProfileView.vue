<template>
  <div class="profile-view">
    <div class="page-header">
      <h1>Teacher Profile</h1>
      <p>Manage your teaching profile and credentials</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading profile...</p>
    </div>

    <!-- Profile Content -->
    <div v-else class="profile-content">
      <!-- Profile Header -->
      <div class="profile-header">
        <div class="avatar-section">
          <div class="avatar-container">
            <img :src="profile.avatar || '/default-avatar.jpg'" :alt="profile.name" class="profile-avatar" />
            <button @click="uploadAvatar" class="avatar-upload-btn">
              <span class="upload-icon">📷</span>
            </button>
          </div>
          <input type="file" ref="avatarInput" @change="handleAvatarUpload" accept="image/*" style="display: none;">
        </div>
        
        <div class="profile-info">
          <h2>{{ profile.name }}</h2>
          <p class="profile-email">{{ profile.email }}</p>
          <div class="profile-badges">
            <span class="badge verified" v-if="profile.isVerified">✓ Verified Teacher</span>
            <span class="badge approved" v-if="profile.isApproved">✓ Approved</span>
            <span class="badge pending" v-else>⏳ Pending Approval</span>
          </div>
        </div>
        
        <div class="profile-stats">
          <div class="stat">
            <span class="stat-number">{{ profile.totalStudents || 0 }}</span>
            <span class="stat-label">Students</span>
          </div>
          <div class="stat">
            <span class="stat-number">{{ profile.totalCourses || 0 }}</span>
            <span class="stat-label">Courses</span>
          </div>
          <div class="stat">
            <span class="stat-number">{{ profile.averageRating || 0 }}</span>
            <span class="stat-label">Rating</span>
          </div>
        </div>
      </div>

      <!-- Profile Form -->
      <div class="profile-form">
        <form @submit.prevent="saveProfile">
          <!-- Basic Information -->
          <div class="form-section">
            <h3>Basic Information</h3>
            <div class="form-grid">
              <div class="form-group">
                <label for="firstName">First Name</label>
                <input type="text" id="firstName" v-model="form.firstName" required>
              </div>
              <div class="form-group">
                <label for="lastName">Last Name</label>
                <input type="text" id="lastName" v-model="form.lastName" required>
              </div>
              <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" v-model="form.email" required readonly>
              </div>
              <div class="form-group">
                <label for="phone">Phone Number</label>
                <input type="tel" id="phone" v-model="form.phone">
              </div>
            </div>
          </div>

          <!-- Professional Information -->
          <div class="form-section">
            <h3>Professional Information</h3>
            <div class="form-group">
              <label for="title">Professional Title</label>
              <input type="text" id="title" v-model="form.title" placeholder="e.g., Senior Software Engineer">
            </div>
            <div class="form-group">
              <label for="bio">Bio</label>
              <textarea id="bio" v-model="form.bio" rows="4" placeholder="Tell students about yourself..."></textarea>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label for="experience">Years of Experience</label>
                <select id="experience" v-model="form.experience">
                  <option value="">Select experience</option>
                  <option value="1-2">1-2 years</option>
                  <option value="3-5">3-5 years</option>
                  <option value="6-10">6-10 years</option>
                  <option value="10+">10+ years</option>
                </select>
              </div>
              <div class="form-group">
                <label for="expertise">Primary Expertise</label>
                <select id="expertise" v-model="form.expertise">
                  <option value="">Select expertise</option>
                  <option value="programming">Programming</option>
                  <option value="design">Design</option>
                  <option value="marketing">Marketing</option>
                  <option value="business">Business</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Education & Certifications -->
          <div class="form-section">
            <h3>Education & Certifications</h3>
            <div class="education-list">
              <div v-for="(edu, index) in form.education" :key="index" class="education-item">
                <div class="form-grid">
                  <div class="form-group">
                    <label>Institution</label>
                    <input type="text" v-model="edu.institution" placeholder="University/Institution">
                  </div>
                  <div class="form-group">
                    <label>Degree</label>
                    <input type="text" v-model="edu.degree" placeholder="Degree/Certification">
                  </div>
                  <div class="form-group">
                    <label>Year</label>
                    <input type="number" v-model="edu.year" placeholder="2020">
                  </div>
                  <div class="form-group">
                    <button type="button" @click="removeEducation(index)" class="remove-btn">Remove</button>
                  </div>
                </div>
              </div>
            </div>
            <button type="button" @click="addEducation" class="add-btn">Add Education</button>
          </div>

          <!-- Social Links -->
          <div class="form-section">
            <h3>Social Links</h3>
            <div class="form-grid">
              <div class="form-group">
                <label for="website">Website</label>
                <input type="url" id="website" v-model="form.website" placeholder="https://yourwebsite.com">
              </div>
              <div class="form-group">
                <label for="linkedin">LinkedIn</label>
                <input type="url" id="linkedin" v-model="form.linkedin" placeholder="https://linkedin.com/in/yourprofile">
              </div>
              <div class="form-group">
                <label for="twitter">Twitter</label>
                <input type="url" id="twitter" v-model="form.twitter" placeholder="https://twitter.com/yourusername">
              </div>
              <div class="form-group">
                <label for="github">GitHub</label>
                <input type="url" id="github" v-model="form.github" placeholder="https://github.com/yourusername">
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="form-actions">
            <button type="button" @click="resetForm" class="cancel-btn">Reset</button>
            <button type="submit" class="save-btn" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save Profile' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import type { APIError } from '@/services/api'
import { useApiData } from '@/composables/useApiData'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { api } from '@/services/api'

const { user } = useAuth()
const { handleApiError } = useErrorHandler()

// Reactive state
const saving = ref(false)
const avatarInput = ref<HTMLInputElement | null>(null)

// API data
const { 
  data: profileData, 
  loading, 
  // error, // Unused
  refresh 
} = useApiData<any>('/user-profiles/me/', {
  immediate: true
})

// Profile computed
const profile = computed(() => ({
  name: `${user.value?.first_name || ''} ${user.value?.last_name || ''}`.trim() || 'Teacher',
  email: user.value?.email || '',
  avatar: profileData.value?.avatar,
  isVerified: user.value?.is_verified || false,
  isApproved: user.value?.is_approved_teacher || false,
  totalStudents: profileData.value?.total_students || 0,
  totalCourses: profileData.value?.total_courses || 0,
  averageRating: profileData.value?.average_rating || 0
}))

// Form data
const form = reactive({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  title: '',
  bio: '',
  experience: '',
  expertise: '',
  education: [
    { institution: '', degree: '', year: '' }
  ],
  website: '',
  linkedin: '',
  twitter: '',
  github: ''
})

// Methods
const uploadAvatar = () => {
  avatarInput.value?.click()
}

const handleAvatarUpload = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  try {
    const formData = new FormData()
    formData.append('avatar', file)

    await api.post('/user-profiles/upload_avatar/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    await refresh()
  } catch (error) {
    handleApiError(error as APIError, { context: { action: 'upload_avatar' } })
  }
}

const addEducation = () => {
  form.education.push({ institution: '', degree: '', year: '' })
}

const removeEducation = (index: number) => {
  if (form.education.length > 1) {
    form.education.splice(index, 1)
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    const profileData = {
      first_name: form.firstName,
      last_name: form.lastName,
      phone: form.phone,
      title: form.title,
      bio: form.bio,
      experience: form.experience,
      expertise: form.expertise,
      education: form.education.filter((edu: any) => edu.institution || edu.degree),
      social_links: {
        website: form.website,
        linkedin: form.linkedin,
        twitter: form.twitter,
        github: form.github
      }
    }

    await api.patch('/user-profiles/me/', profileData)
    await refresh()
    
    // Show success message
    alert('Profile updated successfully!')
  } catch (error) {
    handleApiError(error as APIError, { context: { action: 'save_profile' } })
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  loadFormData()
}

const loadFormData = () => {
  if (profileData.value) {
    form.firstName = user.value?.first_name || ''
    form.lastName = user.value?.last_name || ''
    form.email = user.value?.email || ''
    form.phone = (profileData.value as any).phone || ''
    form.title = (profileData.value as any).title || ''
    form.bio = (profileData.value as any).bio || ''
    form.experience = (profileData.value as any).experience || ''
    form.expertise = (profileData.value as any).expertise || ''
    form.education = (profileData.value as any).education?.length > 0 
      ? (profileData.value as any).education 
      : [{ institution: '', degree: '', year: '' }]
    form.website = (profileData.value as any).social_links?.website || ''
    form.linkedin = (profileData.value as any).social_links?.linkedin || ''
    form.twitter = (profileData.value as any).social_links?.twitter || ''
    form.github = (profileData.value as any).social_links?.github || ''
  }
}

onMounted(() => {
  loadFormData()
})

// Watch for profile data changes
watch(profileData, () => {
  loadFormData()
})
</script>

<style scoped>
.profile-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: #6b7280;
  font-size: 1.125rem;
}

.profile-header {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.avatar-section {
  position: relative;
}

.avatar-container {
  position: relative;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.avatar-upload-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-upload-btn:hover {
  background: #d97706;
  transform: scale(1.1);
}

.profile-info {
  flex: 1;
}

.profile-info h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.profile-email {
  color: #6b7280;
  margin-bottom: 1rem;
}

.profile-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge.verified {
  background: #dcfce7;
  color: #166534;
}

.badge.approved {
  background: #dbeafe;
  color: #1e40af;
}

.badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.profile-stats {
  display: flex;
  gap: 2rem;
}

.stat {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #f59e0b;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.profile-form {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.form-section {
  margin-bottom: 2rem;
}

.form-section h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f59e0b;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.form-group input[readonly] {
  background: #f9fafb;
  color: #6b7280;
}

.education-list {
  margin-bottom: 1rem;
}

.education-item {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  margin-bottom: 1rem;
}

.add-btn, .remove-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.add-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.remove-btn {
  background: #ef4444;
  color: white;
}

.remove-btn:hover {
  background: #dc2626;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn, .save-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.save-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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

/* Responsive */
@media (max-width: 768px) {
  .profile-view {
    padding: 1rem;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .profile-stats {
    justify-content: center;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>