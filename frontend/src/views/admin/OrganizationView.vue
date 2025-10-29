<template>
  <div class="organization-view">
    <div class="page-header">
      <h1>Organization Settings</h1>
      <p>Manage your organization's profile and configuration</p>
    </div>

    <!-- Organization Profile -->
    <div class="settings-container">
      <div class="settings-section">
        <h3>Organization Profile</h3>
        <form @submit.prevent="saveOrganization" class="settings-form">
          <div class="form-group">
            <label>Organization Name</label>
            <input v-model="orgForm.name" type="text" required />
          </div>
          
          <div class="form-group">
            <label>Subdomain</label>
            <div class="subdomain-input">
              <input v-model="orgForm.subdomain" type="text" required />
              <span>.edurise.com</span>
            </div>
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="orgForm.description" rows="4"></textarea>
          </div>
          
          <div class="form-group">
            <label>Logo</label>
            <div class="logo-upload">
              <div class="current-logo">
                <img :src="orgForm.logo || '/default-org-logo.png'" alt="Organization Logo" />
              </div>
              <input type="file" @change="handleLogoUpload" accept="image/*" />
            </div>
          </div>
          
          <div class="form-actions">
            <button type="submit" class="save-btn">Save Changes</button>
          </div>
        </form>
      </div>

      <!-- Subscription Info -->
      <div class="settings-section">
        <h3>Subscription</h3>
        <div class="subscription-info">
          <div class="plan-card">
            <div class="plan-header">
              <h4>{{ subscription.plan_name }}</h4>
              <div class="plan-price">${{ subscription.price }}/month</div>
            </div>
            <div class="plan-features">
              <div class="feature">✓ {{ subscription.max_users }} users</div>
              <div class="feature">✓ {{ subscription.max_courses }} courses</div>
              <div class="feature">✓ {{ subscription.storage_gb }}GB storage</div>
            </div>
            <div class="plan-actions">
              <button class="upgrade-btn">Upgrade Plan</button>
            </div>
          </div>
        </div>
      </div>

      <!-- System Settings -->
      <div class="settings-section">
        <h3>System Settings</h3>
        <div class="settings-grid">
          <div class="setting-item">
            <label class="setting-label">
              <input type="checkbox" v-model="settings.allowSelfRegistration" />
              Allow self-registration
            </label>
            <p class="setting-description">Allow users to register without invitation</p>
          </div>
          
          <div class="setting-item">
            <label class="setting-label">
              <input type="checkbox" v-model="settings.requireEmailVerification" />
              Require email verification
            </label>
            <p class="setting-description">Users must verify their email before accessing the platform</p>
          </div>
          
          <div class="setting-item">
            <label class="setting-label">
              <input type="checkbox" v-model="settings.enableNotifications" />
              Enable notifications
            </label>
            <p class="setting-description">Send email notifications for important events</p>
          </div>
        </div>
        
        <div class="form-actions">
          <button @click="saveSettings" class="save-btn">Save Settings</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApiMutation } from '@/composables/useApiData'

// Form data
const orgForm = ref({
  name: 'My Organization',
  subdomain: 'myorg',
  description: 'A great learning organization',
  logo: null as string | null
})

const subscription = ref({
  plan_name: 'Professional',
  price: 99,
  max_users: 100,
  max_courses: 50,
  storage_gb: 100
})

const settings = ref({
  allowSelfRegistration: true,
  requireEmailVerification: true,
  enableNotifications: true
})

// Mutations
const { mutate: updateOrganization } = useApiMutation(
  (data) => ({ method: 'PATCH', url: '/organizations/current/', data })
)

const { mutate: updateSettings } = useApiMutation(
  (data) => ({ method: 'PATCH', url: '/organizations/settings/', data })
)

// Methods
const handleLogoUpload = (event: Event) => {
  const file = (event.target as HTMLInputElement)?.files?.[0]
  if (file) {
    // Handle file upload
    const reader = new FileReader()
    reader.onload = (e) => {
      orgForm.value.logo = (e.target as FileReader)?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const saveOrganization = async () => {
  await updateOrganization(orgForm.value)
}

const saveSettings = async () => {
  await updateSettings(settings.value)
}

onMounted(() => {
  // Load organization data
})
</script>

<style scoped>
.organization-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
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
  margin-bottom: 2rem;
}

.settings-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.settings-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.settings-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.subdomain-input {
  display: flex;
  align-items: center;
}

.subdomain-input input {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  border-right: none;
}

.subdomain-input span {
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-left: none;
  border-top-right-radius: 6px;
  border-bottom-right-radius: 6px;
  padding: 0.75rem;
  color: #6b7280;
}

.logo-upload {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.current-logo {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.current-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.plan-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.plan-header h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.plan-price {
  font-size: 1.25rem;
  font-weight: 700;
  color: #10b981;
}

.plan-features {
  margin-bottom: 1.5rem;
}

.feature {
  color: #374151;
  margin-bottom: 0.5rem;
}

.upgrade-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upgrade-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.settings-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.setting-item {
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.setting-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
}

.setting-label input[type="checkbox"] {
  width: 1.25rem;
  height: 1.25rem;
}

.setting-description {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0.5rem 0 0 2rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.save-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}
</style>