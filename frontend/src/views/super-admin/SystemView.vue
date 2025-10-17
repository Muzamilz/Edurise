<template>
  <div class="system-view">
    <div class="page-header">
      <h1>System Administration</h1>
      <p>Manage platform-wide system settings and configurations</p>
    </div>

    <!-- System Status Cards -->
    <div class="status-cards">
      <div class="status-card server">
        <div class="card-icon">🖥️</div>
        <div class="card-content">
          <h3>Server Status</h3>
          <p class="status" :class="systemStatus?.server_status">
            {{ formatStatus(systemStatus?.server_status) }}
          </p>
          <span class="uptime">Uptime: {{ systemStatus?.uptime || 'N/A' }}</span>
        </div>
      </div>
      
      <div class="status-card database">
        <div class="card-icon">🗄️</div>
        <div class="card-content">
          <h3>Database</h3>
          <p class="status" :class="systemStatus?.database_status">
            {{ formatStatus(systemStatus?.database_status) }}
          </p>
          <span class="connections">{{ systemStatus?.db_connections || 0 }} connections</span>
        </div>
      </div>
      
      <div class="status-card storage">
        <div class="card-icon">💾</div>
        <div class="card-content">
          <h3>Storage</h3>
          <p class="usage">{{ systemStatus?.storage_used || 0 }}GB / {{ systemStatus?.storage_total || 0 }}GB</p>
          <span class="percentage">{{ calculateStoragePercentage() }}% used</span>
        </div>
      </div>
      
      <div class="status-card memory">
        <div class="card-icon">🧠</div>
        <div class="card-content">
          <h3>Memory</h3>
          <p class="usage">{{ systemStatus?.memory_used || 0 }}GB / {{ systemStatus?.memory_total || 0 }}GB</p>
          <span class="percentage">{{ calculateMemoryPercentage() }}% used</span>
        </div>
      </div>
    </div>

    <!-- System Configuration -->
    <div class="config-section">
      <div class="section-header">
        <h2>System Configuration</h2>
        <button @click="saveConfiguration" :disabled="!hasConfigChanges" class="save-btn">
          Save Changes
        </button>
      </div>

      <div class="config-tabs">
        <button 
          v-for="tab in configTabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="{ active: activeTab === tab.id }"
          class="tab-btn"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="config-content">
        <!-- General Settings -->
        <div v-if="activeTab === 'general'" class="config-panel">
          <div class="form-group">
            <label>Platform Name</label>
            <input 
              v-model="config.general.platform_name" 
              type="text" 
              @input="markConfigChanged"
            />
          </div>
          <div class="form-group">
            <label>Platform URL</label>
            <input 
              v-model="config.general.platform_url" 
              type="url" 
              @input="markConfigChanged"
            />
          </div>
          <div class="form-group">
            <label>Support Email</label>
            <input 
              v-model="config.general.support_email" 
              type="email" 
              @input="markConfigChanged"
            />
          </div>
          <div class="form-group">
            <label>Default Language</label>
            <select v-model="config.general.default_language" @change="markConfigChanged">
              <option value="en">English</option>
              <option value="ar">Arabic</option>
              <option value="so">Somali</option>
            </select>
          </div>
          <div class="form-group">
            <label>
              <input 
                v-model="config.general.maintenance_mode" 
                type="checkbox" 
                @change="markConfigChanged"
              />
              Maintenance Mode
            </label>
          </div>
        </div>

        <!-- Email Settings -->
        <div v-if="activeTab === 'email'" class="config-panel">
          <div class="form-group">
            <label>SMTP Host</label>
            <input 
              v-model="config.email.smtp_host" 
              type="text" 
              @input="markConfigChanged"
            />
          </div>
          <div class="form-group">
            <label>SMTP Port</label>
            <input 
              v-model="config.email.smtp_port" 
              type="number" 
              @input="markConfigChanged"
            />
          </div>
          <div class="form-group">
            <label>SMTP Username</label>
            <input 
              v-model="config.email.smtp_username" 
              type="text" 
              @input="markConfigChanged"
            />
          </div>
          <div class="form-group">
            <label>SMTP Password</label>
            <input 
              v-model="config.email.smtp_password" 
              type="password" 
              @input="markConfigChanged"
            />
          </div>
          <div class="form-group">
            <label>
              <input 
                v-model="config.email.use_tls" 
                type="checkbox" 
                @change="markConfigChanged"
              />
              Use TLS
            </label>
          </div>
          <div class="form-group">
            <label>From Email</label>
            <input 
              v-model="config.email.from_email" 
              type="email" 
              @input="markConfigChanged"
            />
          </div>
        </div>

        <!-- Storage Settings -->
        <div v-if="activeTab === 'storage'" class="config-panel">
          <div class="form-group">
            <label>Storage Provider</label>
            <select v-model="config.storage.provider" @change="markConfigChanged">
              <option value="local">Local Storage</option>
              <option value="aws_s3">AWS S3</option>
              <option value="azure">Azure Blob</option>
              <option value="gcp">Google Cloud Storage</option>
            </select>
          </div>
          <div v-if="config.storage.provider === 'aws_s3'" class="storage-config">
            <div class="form-group">
              <label>AWS Access Key ID</label>
              <input 
                v-model="config.storage.aws_access_key" 
                type="text" 
                @input="markConfigChanged"
              />
            </div>
            <div class="form-group">
              <label>AWS Secret Access Key</label>
              <input 
                v-model="config.storage.aws_secret_key" 
                type="password" 
                @input="markConfigChanged"
              />
            </div>
            <div class="form-group">
              <label>S3 Bucket Name</label>
              <input 
                v-model="config.storage.s3_bucket" 
                type="text" 
                @input="markConfigChanged"
              />
            </div>
            <div class="form-group">
              <label>AWS Region</label>
              <input 
                v-model="config.storage.aws_region" 
                type="text" 
                @input="markConfigChanged"
              />
            </div>
          </div>
          <div class="form-group">
            <label>Max File Size (MB)</label>
            <input 
              v-model="config.storage.max_file_size" 
              type="number" 
              @input="markConfigChanged"
            />
          </div>
          <div class="form-group">
            <label>Allowed File Types</label>
            <textarea 
              v-model="config.storage.allowed_types" 
              rows="3"
              placeholder="jpg,png,pdf,mp4,mp3"
              @input="markConfigChanged"
            ></textarea>
          </div>
        </div>

        <!-- Payment Settings -->
        <div v-if="activeTab === 'payment'" class="config-panel">
          <div class="form-group">
            <label>Payment Provider</label>
            <select v-model="config.payment.provider" @change="markConfigChanged">
              <option value="stripe">Stripe</option>
              <option value="paypal">PayPal</option>
              <option value="razorpay">Razorpay</option>
            </select>
          </div>
          <div class="form-group">
            <label>API Key</label>
            <input 
              v-model="config.payment.api_key" 
              type="password" 
              @input="markConfigChanged"
            />
          </div>
          <div class="form-group">
            <label>Webhook Secret</label>
            <input 
              v-model="config.payment.webhook_secret" 
              type="password" 
              @input="markConfigChanged"
            />
          </div>
          <div class="form-group">
            <label>Platform Commission (%)</label>
            <input 
              v-model="config.payment.commission_rate" 
              type="number" 
              min="0" 
              max="100" 
              step="0.1"
              @input="markConfigChanged"
            />
          </div>
          <div class="form-group">
            <label>Currency</label>
            <select v-model="config.payment.currency" @change="markConfigChanged">
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
              <option value="SAR">SAR</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- System Logs -->
    <div class="logs-section">
      <div class="section-header">
        <h2>System Logs</h2>
        <div class="log-controls">
          <select v-model="logLevel">
            <option value="">All Levels</option>
            <option value="error">Error</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
            <option value="debug">Debug</option>
          </select>
          <button @click="refreshLogs" class="refresh-btn">
            Refresh
          </button>
          <button @click="downloadLogs" class="download-btn">
            Download
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading system logs...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>Failed to load system logs</h3>
        <p>{{ error.message }}</p>
        <button @click="handleRetry" class="retry-btn">Try Again</button>
      </div>

      <!-- Logs Display -->
      <div v-else class="logs-display">
        <div class="log-entry" v-for="log in filteredLogs" :key="log.id" :class="log.level">
          <div class="log-timestamp">{{ formatDateTime(log.timestamp) }}</div>
          <div class="log-level">{{ log.level.toUpperCase() }}</div>
          <div class="log-message">{{ log.message }}</div>
          <div class="log-source">{{ log.source }}</div>
        </div>
      </div>
    </div>

    <!-- Backup & Maintenance -->
    <div class="maintenance-section">
      <div class="section-header">
        <h2>Backup & Maintenance</h2>
      </div>

      <div class="maintenance-grid">
        <div class="maintenance-card">
          <h3>Database Backup</h3>
          <p>Last backup: {{ lastBackup || 'Never' }}</p>
          <div class="maintenance-actions">
            <button @click="createBackup" :disabled="backupInProgress" class="action-btn primary">
              {{ backupInProgress ? 'Creating...' : 'Create Backup' }}
            </button>
            <button @click="scheduleBackup" class="action-btn secondary">
              Schedule Backup
            </button>
          </div>
        </div>

        <div class="maintenance-card">
          <h3>System Cleanup</h3>
          <p>Clean temporary files and optimize database</p>
          <div class="maintenance-actions">
            <button @click="runCleanup" :disabled="cleanupInProgress" class="action-btn primary">
              {{ cleanupInProgress ? 'Cleaning...' : 'Run Cleanup' }}
            </button>
          </div>
        </div>

        <div class="maintenance-card">
          <h3>Cache Management</h3>
          <p>Clear application and system caches</p>
          <div class="maintenance-actions">
            <button @click="clearCache" class="action-btn primary">
              Clear Cache
            </button>
            <button @click="warmupCache" class="action-btn secondary">
              Warmup Cache
            </button>
          </div>
        </div>

        <div class="maintenance-card">
          <h3>System Updates</h3>
          <p>Check for and install system updates</p>
          <div class="maintenance-actions">
            <button @click="checkUpdates" class="action-btn primary">
              Check Updates
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useApiData, useApiMutation } from '@/composables/useApiData'
import { useErrorHandler } from '@/composables/useErrorHandler'

const { handleApiError } = useErrorHandler()

// Data fetching
const { data: systemStatus, loading, error, refresh } = useApiData('/system/status/')
const { data: systemLogs } = useApiData('/system/logs/')
const { data: systemConfig } = useApiData('/system/config/')

// State
const activeTab = ref('general')
const logLevel = ref('')
const hasConfigChanges = ref(false)
const backupInProgress = ref(false)
const cleanupInProgress = ref(false)
const lastBackup = ref(null)

// Configuration tabs
const configTabs = [
  { id: 'general', label: 'General' },
  { id: 'email', label: 'Email' },
  { id: 'storage', label: 'Storage' },
  { id: 'payment', label: 'Payment' }
]

// Configuration state
const config = ref({
  general: {
    platform_name: '',
    platform_url: '',
    support_email: '',
    default_language: 'en',
    maintenance_mode: false
  },
  email: {
    smtp_host: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    use_tls: true,
    from_email: ''
  },
  storage: {
    provider: 'local',
    aws_access_key: '',
    aws_secret_key: '',
    s3_bucket: '',
    aws_region: '',
    max_file_size: 100,
    allowed_types: 'jpg,png,pdf,mp4,mp3'
  },
  payment: {
    provider: 'stripe',
    api_key: '',
    webhook_secret: '',
    commission_rate: 10,
    currency: 'USD'
  }
})

// Mutations
const { mutate: updateConfig } = useApiMutation(
  (configData) => ({ method: 'PATCH', url: '/system/config/', data: configData }),
  {
    onSuccess: () => {
      hasConfigChanges.value = false
      refresh()
    },
    onError: (error) => handleApiError(error, { context: { action: 'update_system_config' } })
  }
)

const { mutate: performMaintenance } = useApiMutation(
  (action) => ({ method: 'POST', url: `/system/maintenance/${action}/` }),
  {
    onSuccess: () => refresh(),
    onError: (error) => handleApiError(error, { context: { action: 'system_maintenance' } })
  }
)

// Computed properties
const filteredLogs = computed(() => {
  if (!systemLogs.value) return []
  
  return systemLogs.value.filter(log => {
    return !logLevel.value || log.level === logLevel.value
  })
})

// Methods
const formatStatus = (status) => {
  return status?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Unknown'
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const calculateStoragePercentage = () => {
  const used = systemStatus.value?.storage_used || 0
  const total = systemStatus.value?.storage_total || 1
  return Math.round((used / total) * 100)
}

const calculateMemoryPercentage = () => {
  const used = systemStatus.value?.memory_used || 0
  const total = systemStatus.value?.memory_total || 1
  return Math.round((used / total) * 100)
}

const markConfigChanged = () => {
  hasConfigChanges.value = true
}

const saveConfiguration = async () => {
  await updateConfig(config.value)
}

const refreshLogs = async () => {
  await refresh()
}

const downloadLogs = () => {
  // Implement log download functionality
  console.log('Download logs')
}

const createBackup = async () => {
  backupInProgress.value = true
  try {
    await performMaintenance('backup')
    lastBackup.value = new Date().toISOString()
  } finally {
    backupInProgress.value = false
  }
}

const scheduleBackup = () => {
  // Implement backup scheduling
  console.log('Schedule backup')
}

const runCleanup = async () => {
  cleanupInProgress.value = true
  try {
    await performMaintenance('cleanup')
  } finally {
    cleanupInProgress.value = false
  }
}

const clearCache = async () => {
  await performMaintenance('clear-cache')
}

const warmupCache = async () => {
  await performMaintenance('warmup-cache')
}

const checkUpdates = async () => {
  await performMaintenance('check-updates')
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err, { context: { action: 'retry_system_load' } })
  }
}

onMounted(() => {
  refresh()
  // Load configuration when component mounts
  if (systemConfig.value) {
    config.value = { ...systemConfig.value }
  }
})
</script>

<style scoped>
.system-view {
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

.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.status-card {
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

.card-content .status,
.card-content .usage {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.card-content .status.healthy {
  color: #059669;
}

.card-content .status.warning {
  color: #d97706;
}

.card-content .status.critical {
  color: #dc2626;
}

.card-content .uptime,
.card-content .connections,
.card-content .percentage {
  font-size: 0.875rem;
  color: #6b7280;
}

.config-section,
.logs-section,
.maintenance-section {
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

.config-tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
}

.tab-btn {
  padding: 1rem 1.5rem;
  border: none;
  background: none;
  color: #6b7280;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab-btn.active {
  color: #f59e0b;
  border-bottom-color: #f59e0b;
}

.tab-btn:hover {
  color: #374151;
}

.config-content {
  padding: 1.5rem;
}

.config-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
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

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.log-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.log-controls select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.refresh-btn,
.download-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.refresh-btn:hover,
.download-btn:hover {
  background: #f9fafb;
  border-color: #f59e0b;
}

.logs-display {
  max-height: 400px;
  overflow-y: auto;
  padding: 1rem;
  background: #1f2937;
  color: #f9fafb;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}

.log-entry {
  display: grid;
  grid-template-columns: 180px 80px 1fr 120px;
  gap: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #374151;
}

.log-entry.error {
  color: #fca5a5;
}

.log-entry.warning {
  color: #fcd34d;
}

.log-entry.info {
  color: #93c5fd;
}

.log-entry.debug {
  color: #d1d5db;
}

.log-timestamp {
  color: #9ca3af;
}

.log-level {
  font-weight: 600;
}

.log-message {
  word-break: break-word;
}

.log-source {
  color: #9ca3af;
  font-size: 0.75rem;
}

.maintenance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.maintenance-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
}

.maintenance-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.maintenance-card p {
  color: #6b7280;
  margin-bottom: 1rem;
}

.maintenance-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.action-btn.primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.action-btn.secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.action-btn.secondary:hover {
  background: #e5e7eb;
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