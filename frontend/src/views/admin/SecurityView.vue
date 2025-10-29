<template>
  <div class="admin-security-view">
    <div class="page-header">
      <h1>Organization Security</h1>
      <p>Monitor and manage security settings for your organization</p>
    </div>

    <!-- Security Overview Cards -->
    <div class="security-cards">
      <div class="security-card threats">
        <div class="card-icon">🛡️</div>
        <div class="card-content">
          <h3>Security Alerts</h3>
          <p class="count">{{ securityData?.active_alerts || 0 }}</p>
          <span class="status" :class="{ warning: securityData?.active_alerts > 0 }">
            {{ securityData?.active_alerts > 0 ? 'Needs Attention' : 'All Clear' }}
          </span>
        </div>
      </div>
      
      <div class="security-card logins">
        <div class="card-icon">🔐</div>
        <div class="card-content">
          <h3>Failed Logins</h3>
          <p class="count">{{ securityData?.failed_logins_today || 0 }}</p>
          <span class="period">Today</span>
        </div>
      </div>
      
      <div class="security-card sessions">
        <div class="card-icon">👥</div>
        <div class="card-content">
          <h3>Active Users</h3>
          <p class="count">{{ securityData?.active_users || 0 }}</p>
          <span class="period">Currently online</span>
        </div>
      </div>
      
      <div class="security-card compliance">
        <div class="card-icon">✅</div>
        <div class="card-content">
          <h3>Security Score</h3>
          <p class="count">{{ securityData?.security_score || 0 }}%</p>
          <span class="status" :class="getSecurityScoreClass(securityData?.security_score)">
            {{ getSecurityScoreStatus(securityData?.security_score) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Security Settings -->
    <div class="settings-section">
      <div class="section-header">
        <h2>Security Settings</h2>
        <button @click="saveSettings" :disabled="!hasChanges" class="save-btn">
          Save Changes
        </button>
      </div>

      <div class="settings-grid">
        <!-- Password Policy -->
        <div class="setting-card">
          <div class="setting-header">
            <h3>Password Policy</h3>
            <div class="setting-toggle">
              <input 
                v-model="settings.password_policy.enabled" 
                type="checkbox" 
                id="password-policy"
                @change="markChanged"
              />
              <label for="password-policy"></label>
            </div>
          </div>
          <div v-if="settings.password_policy.enabled" class="setting-content">
            <div class="form-group">
              <label>Minimum Length</label>
              <input 
                v-model.number="settings.password_policy.min_length" 
                type="number" 
                min="6" 
                max="32"
                @change="markChanged"
              />
            </div>
            <div class="form-group">
              <label>
                <input 
                  v-model="settings.password_policy.require_uppercase" 
                  type="checkbox"
                  @change="markChanged"
                />
                Require uppercase letters
              </label>
            </div>
            <div class="form-group">
              <label>
                <input 
                  v-model="settings.password_policy.require_lowercase" 
                  type="checkbox"
                  @change="markChanged"
                />
                Require lowercase letters
              </label>
            </div>
            <div class="form-group">
              <label>
                <input 
                  v-model="settings.password_policy.require_numbers" 
                  type="checkbox"
                  @change="markChanged"
                />
                Require numbers
              </label>
            </div>
            <div class="form-group">
              <label>
                <input 
                  v-model="settings.password_policy.require_special" 
                  type="checkbox"
                  @change="markChanged"
                />
                Require special characters
              </label>
            </div>
          </div>
        </div>

        <!-- Session Management -->
        <div class="setting-card">
          <div class="setting-header">
            <h3>Session Management</h3>
            <div class="setting-toggle">
              <input 
                v-model="settings.session_management.enabled" 
                type="checkbox" 
                id="session-management"
                @change="markChanged"
              />
              <label for="session-management"></label>
            </div>
          </div>
          <div v-if="settings.session_management.enabled" class="setting-content">
            <div class="form-group">
              <label>Session Timeout (minutes)</label>
              <input 
                v-model.number="settings.session_management.timeout_minutes" 
                type="number" 
                min="5" 
                max="1440"
                @change="markChanged"
              />
            </div>
            <div class="form-group">
              <label>
                <input 
                  v-model="settings.session_management.concurrent_sessions" 
                  type="checkbox"
                  @change="markChanged"
                />
                Allow concurrent sessions
              </label>
            </div>
            <div class="form-group">
              <label>Max Sessions per User</label>
              <input 
                v-model.number="settings.session_management.max_sessions" 
                type="number" 
                min="1" 
                max="10"
                :disabled="!settings.session_management.concurrent_sessions"
                @change="markChanged"
              />
            </div>
          </div>
        </div>

        <!-- Two-Factor Authentication -->
        <div class="setting-card">
          <div class="setting-header">
            <h3>Two-Factor Authentication</h3>
            <div class="setting-toggle">
              <input 
                v-model="settings.two_factor.enabled" 
                type="checkbox" 
                id="two-factor"
                @change="markChanged"
              />
              <label for="two-factor"></label>
            </div>
          </div>
          <div v-if="settings.two_factor.enabled" class="setting-content">
            <div class="form-group">
              <label>
                <input 
                  v-model="settings.two_factor.required_for_admins" 
                  type="checkbox"
                  @change="markChanged"
                />
                Required for administrators
              </label>
            </div>
            <div class="form-group">
              <label>
                <input 
                  v-model="settings.two_factor.required_for_teachers" 
                  type="checkbox"
                  @change="markChanged"
                />
                Required for teachers
              </label>
            </div>
            <div class="form-group">
              <label>Backup Codes</label>
              <input 
                v-model.number="settings.two_factor.backup_codes_count" 
                type="number" 
                min="5" 
                max="20"
                @change="markChanged"
              />
            </div>
          </div>
        </div>

        <!-- Login Restrictions -->
        <div class="setting-card">
          <div class="setting-header">
            <h3>Login Restrictions</h3>
            <div class="setting-toggle">
              <input 
                v-model="settings.login_restrictions.enabled" 
                type="checkbox" 
                id="login-restrictions"
                @change="markChanged"
              />
              <label for="login-restrictions"></label>
            </div>
          </div>
          <div v-if="settings.login_restrictions.enabled" class="setting-content">
            <div class="form-group">
              <label>Max Failed Attempts</label>
              <input 
                v-model.number="settings.login_restrictions.max_attempts" 
                type="number" 
                min="3" 
                max="10"
                @change="markChanged"
              />
            </div>
            <div class="form-group">
              <label>Lockout Duration (minutes)</label>
              <input 
                v-model.number="settings.login_restrictions.lockout_duration" 
                type="number" 
                min="5" 
                max="1440"
                @change="markChanged"
              />
            </div>
            <div class="form-group">
              <label>IP Whitelist (one per line)</label>
              <textarea 
                v-model="settings.login_restrictions.ip_whitelist" 
                rows="4"
                placeholder="192.168.1.0/24&#10;10.0.0.0/8"
                @change="markChanged"
              ></textarea>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Security Events -->
    <div class="events-section">
      <div class="section-header">
        <h2>Recent Security Events</h2>
        <div class="event-filters">
          <select v-model="eventFilter">
            <option value="">All Events</option>
            <option value="login_failed">Failed Logins</option>
            <option value="login_success">Successful Logins</option>
            <option value="password_changed">Password Changes</option>
            <option value="account_locked">Account Lockouts</option>
          </select>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading security events...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>Failed to load security events</h3>
        <p>{{ error.message }}</p>
        <button @click="handleRetry" class="retry-btn">Try Again</button>
      </div>

      <!-- Events Table -->
      <div v-else class="events-table">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Event Type</th>
              <th>User</th>
              <th>IP Address</th>
              <th>Details</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="event in filteredEvents" :key="event.id" class="event-row">
              <td class="timestamp">{{ formatDateTime(event.timestamp) }}</td>
              <td class="event-type">
                <span class="event-badge" :class="getEventClass(event.type)">
                  {{ formatEventType(event.type) }}
                </span>
              </td>
              <td class="user">
                <div class="user-info">
                  <img :src="event.user?.avatar || '/default-avatar.jpg'" :alt="event.user?.name" />
                  <span>{{ event.user?.first_name }} {{ event.user?.last_name }}</span>
                </div>
              </td>
              <td class="ip">{{ event.ip_address }}</td>
              <td class="details">{{ event.details || 'N/A' }}</td>
              <td class="status">
                <span class="status-badge" :class="event.status">
                  {{ formatStatus(event.status) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pagination">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="pagination-btn"
        >
          Previous
        </button>
        <span class="pagination-info">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="pagination-btn"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useApiData, useApiMutation } from '@/composables/useApiData'
import type { APIError } from '@/services/api'
import { useErrorHandler } from '@/composables/useErrorHandler'

const { handleApiError } = useErrorHandler()

// Data fetching
const { data: securityData, loading, error, refresh } = useApiData<any>('/security/overview/')
const { data: securityEvents } = useApiData<any[]>('/security/events/')
const { data: securitySettings } = useApiData<any>('/security/settings/')

// Filters and pagination
const eventFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 20

// Settings state
const hasChanges = ref(false)
const settings = ref({
  password_policy: {
    enabled: false,
    min_length: 8,
    require_uppercase: true,
    require_lowercase: true,
    require_numbers: true,
    require_special: false
  },
  session_management: {
    enabled: false,
    timeout_minutes: 30,
    concurrent_sessions: true,
    max_sessions: 3
  },
  two_factor: {
    enabled: false,
    required_for_admins: false,
    required_for_teachers: false,
    backup_codes_count: 10
  },
  login_restrictions: {
    enabled: false,
    max_attempts: 5,
    lockout_duration: 15,
    ip_whitelist: ''
  }
})

// Settings mutation
const { mutate: updateSettings } = useApiMutation(
  (settingsData) => ({ method: 'PATCH', url: '/security/settings/', data: settingsData }),
  {
    onSuccess: () => {
      hasChanges.value = false
      refresh()
    },
    onError: (error) => handleApiError(error as APIError, { context: { action: 'update_security_settings' } })
  }
)

// Watch for settings changes from API
watch(securitySettings, (newSettings) => {
  if (newSettings) {
    settings.value = { ...newSettings }
    hasChanges.value = false
  }
}, { immediate: true })

// Computed properties
const filteredEvents = computed(() => {
  if (!securityEvents.value) return []
  
  return securityEvents.value.filter((event: any) => {
    return !eventFilter.value || event.type === eventFilter.value
  })
})

const totalPages = computed(() => Math.ceil(filteredEvents.value.length / itemsPerPage))

// Methods
const getSecurityScoreClass = (score: number) => {
  if (score >= 90) return 'excellent'
  if (score >= 70) return 'good'
  if (score >= 50) return 'fair'
  return 'poor'
}

const getSecurityScoreStatus = (score: number) => {
  if (score >= 90) return 'Excellent'
  if (score >= 70) return 'Good'
  if (score >= 50) return 'Fair'
  return 'Needs Improvement'
}

const formatDateTime = (date: any) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const formatEventType = (type: string) => {
  return type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())
}

const formatStatus = (status: string) => {
  return status.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())
}

const getEventClass = (type: string) => {
  if (type.includes('failed') || type.includes('locked')) return 'danger'
  if (type.includes('success') || type.includes('login')) return 'success'
  if (type.includes('changed') || type.includes('updated')) return 'warning'
  return 'info'
}

const markChanged = () => {
  hasChanges.value = true
}

const saveSettings = async () => {
  await updateSettings(settings.value)
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err as APIError, { context: { action: 'retry_security_load' } })
  }
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.admin-security-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
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

.security-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.security-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.card-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.card-content h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-content .count {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.card-content .status,
.card-content .period {
  font-size: 0.875rem;
  color: #6b7280;
}

.card-content .status.warning {
  color: #dc2626;
  font-weight: 600;
}

.card-content .status.excellent {
  color: #059669;
}

.card-content .status.good {
  color: #0891b2;
}

.card-content .status.fair {
  color: #d97706;
}

.card-content .status.poor {
  color: #dc2626;
}

.settings-section,
.events-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.section-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
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

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.setting-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
}

.setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.setting-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.setting-toggle {
  position: relative;
}

.setting-toggle input[type="checkbox"] {
  opacity: 0;
  width: 0;
  height: 0;
}

.setting-toggle label {
  display: block;
  width: 50px;
  height: 28px;
  background: #d1d5db;
  border-radius: 14px;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.setting-toggle label::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 24px;
  height: 24px;
  background: white;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.setting-toggle input:checked + label {
  background: #f59e0b;
}

.setting-toggle input:checked + label::after {
  transform: translateX(22px);
}

.setting-content {
  margin-top: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-group input[type="checkbox"] {
  margin-right: 0.5rem;
}

.form-group input[type="number"],
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group input:disabled {
  background: #f9fafb;
  color: #9ca3af;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.event-filters select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.events-table {
  overflow-x: auto;
}

.events-table table {
  width: 100%;
  border-collapse: collapse;
}

.events-table th {
  background: #f9fafb;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.events-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.event-row:hover {
  background: #f9fafb;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-info img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.event-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.event-badge.success {
  background: #dcfce7;
  color: #166534;
}

.event-badge.danger {
  background: #fee2e2;
  color: #dc2626;
}

.event-badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.event-badge.info {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.success {
  background: #dcfce7;
  color: #166534;
}

.status-badge.failed {
  background: #fee2e2;
  color: #dc2626;
}

.status-badge.blocked {
  background: #f3e8ff;
  color: #5b21b6;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #f59e0b;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Loading and Error States */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
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

.loading-state p {
  color: #6b7280;
  font-size: 1rem;
  margin: 0;
}

.error-state .error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 0.5rem;
}

.error-state p {
  color: #6b7280;
  margin-bottom: 1.5rem;
  max-width: 400px;
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
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}
</style>