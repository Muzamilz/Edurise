<template>
  <div class="security-view">
    <div class="page-header">
      <h1>Security Center</h1>
      <p>Monitor platform security, audit logs, and manage security policies</p>
    </div>

    <!-- Security Overview Cards -->
    <div class="security-cards">
      <div class="security-card threats">
        <div class="card-icon">🛡️</div>
        <div class="card-content">
          <h3>Security Threats</h3>
          <p class="count">{{ securityData?.active_threats || 0 }}</p>
          <span class="status" :class="{ critical: securityData?.active_threats > 0 }">
            {{ securityData?.active_threats > 0 ? 'Requires Attention' : 'All Clear' }}
          </span>
        </div>
      </div>
      
      <div class="security-card logins">
        <div class="card-icon">🔐</div>
        <div class="card-content">
          <h3>Failed Login Attempts</h3>
          <p class="count">{{ securityData?.failed_logins_24h || 0 }}</p>
          <span class="period">Last 24 hours</span>
        </div>
      </div>
      
      <div class="security-card sessions">
        <div class="card-icon">👥</div>
        <div class="card-content">
          <h3>Active Sessions</h3>
          <p class="count">{{ securityData?.active_sessions || 0 }}</p>
          <span class="period">Currently online</span>
        </div>
      </div>
      
      <div class="security-card compliance">
        <div class="card-icon">✅</div>
        <div class="card-content">
          <h3>Compliance Score</h3>
          <p class="count">{{ securityData?.compliance_score || 0 }}%</p>
          <span class="status" :class="getComplianceClass(securityData?.compliance_score)">
            {{ getComplianceStatus(securityData?.compliance_score) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Security Alerts -->
    <div class="alerts-section">
      <div class="section-header">
        <h2>Security Alerts</h2>
        <div class="alert-filters">
          <select v-model="alertFilter">
            <option value="">All Alerts</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <button @click="markAllAsRead" class="mark-read-btn">
            Mark All as Read
          </button>
        </div>
      </div>

      <div class="alerts-list">
        <div v-if="filteredAlerts.length === 0" class="no-alerts">
          <div class="no-alerts-icon">🎉</div>
          <h3>No Security Alerts</h3>
          <p>Your platform is secure with no active security alerts.</p>
        </div>
        
        <div v-else>
          <div v-for="alert in filteredAlerts" :key="alert.id" class="alert-item" :class="[alert.severity, { unread: !alert.read }]">
            <div class="alert-icon">
              <span v-if="alert.severity === 'critical'">🚨</span>
              <span v-else-if="alert.severity === 'high'">⚠️</span>
              <span v-else-if="alert.severity === 'medium'">🔶</span>
              <span v-else>ℹ️</span>
            </div>
            <div class="alert-content">
              <h4>{{ alert.title }}</h4>
              <p>{{ alert.description }}</p>
              <div class="alert-meta">
                <span class="timestamp">{{ formatDate(alert.created_at) }}</span>
                <span class="source">{{ alert.source }}</span>
              </div>
            </div>
            <div class="alert-actions">
              <button @click="viewAlert(alert)" class="action-btn view">
                View Details
              </button>
              <button @click="resolveAlert(alert)" class="action-btn resolve">
                Resolve
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Audit Logs -->
    <div class="audit-section">
      <div class="section-header">
        <h2>Audit Logs</h2>
        <div class="audit-filters">
          <select v-model="auditFilter">
            <option value="">All Actions</option>
            <option value="login">Login Events</option>
            <option value="admin">Admin Actions</option>
            <option value="data">Data Changes</option>
            <option value="security">Security Events</option>
          </select>
          <select v-model="auditPeriod">
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading audit logs...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>Failed to load audit logs</h3>
        <p>{{ error.message }}</p>
        <button @click="handleRetry" class="retry-btn">Try Again</button>
      </div>

      <!-- Audit Logs Table -->
      <div v-else class="audit-table">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>User</th>
              <th>Action</th>
              <th>Resource</th>
              <th>IP Address</th>
              <th>User Agent</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in filteredAuditLogs" :key="log.id" class="audit-row">
              <td class="timestamp">{{ formatDateTime(log.timestamp) }}</td>
              <td class="user">
                <div class="user-info">
                  <img :src="log.user?.avatar || '/default-avatar.jpg'" :alt="log.user?.name" />
                  <span>{{ log.user?.first_name }} {{ log.user?.last_name }}</span>
                </div>
              </td>
              <td class="action">
                <span class="action-badge" :class="getActionClass(log.action)">
                  {{ formatAction(log.action) }}
                </span>
              </td>
              <td class="resource">{{ log.resource_type }}: {{ log.resource_id }}</td>
              <td class="ip">{{ log.ip_address }}</td>
              <td class="user-agent">{{ truncateUserAgent(log.user_agent) }}</td>
              <td class="status">
                <span class="status-badge" :class="log.status">
                  {{ formatStatus(log.status) }}
                </span>
              </td>
              <td class="actions">
                <button @click="viewLogDetails(log)" class="action-btn view">
                  Details
                </button>
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

    <!-- Security Policies -->
    <div class="policies-section">
      <div class="section-header">
        <h2>Security Policies</h2>
        <button @click="showPolicyModal = true" class="create-btn">
          <span class="btn-icon">➕</span>
          Add Policy
        </button>
      </div>

      <div class="policies-grid">
        <div v-for="policy in securityPolicies" :key="policy.id" class="policy-card">
          <div class="policy-header">
            <h3>{{ policy.name }}</h3>
            <div class="policy-status" :class="{ active: policy.enabled }">
              {{ policy.enabled ? 'Active' : 'Inactive' }}
            </div>
          </div>
          <p class="policy-description">{{ policy.description }}</p>
          <div class="policy-meta">
            <span class="policy-type">{{ formatPolicyType(policy.type) }}</span>
            <span class="policy-updated">Updated {{ formatDate(policy.updated_at) }}</span>
          </div>
          <div class="policy-actions">
            <button @click="editPolicy(policy)" class="action-btn edit">
              Edit
            </button>
            <button @click="togglePolicy(policy)" :class="policy.enabled ? 'disable' : 'enable'" class="action-btn">
              {{ policy.enabled ? 'Disable' : 'Enable' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Alert Details Modal -->
    <div v-if="selectedAlert" class="modal-overlay" @click="closeAlertModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Security Alert Details</h3>
          <button @click="closeAlertModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="alert-details">
            <div class="detail-row">
              <span class="label">Severity:</span>
              <span class="value" :class="selectedAlert.severity">{{ selectedAlert.severity.toUpperCase() }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Title:</span>
              <span class="value">{{ selectedAlert.title }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Description:</span>
              <span class="value">{{ selectedAlert.description }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Source:</span>
              <span class="value">{{ selectedAlert.source }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Detected:</span>
              <span class="value">{{ formatDateTime(selectedAlert.created_at) }}</span>
            </div>
            <div v-if="selectedAlert.details" class="detail-row">
              <span class="label">Additional Details:</span>
              <pre class="value">{{ JSON.stringify(selectedAlert.details, null, 2) }}</pre>
            </div>
          </div>
          <div class="modal-actions">
            <button @click="closeAlertModal" class="cancel-btn">Close</button>
            <button @click="resolveAlert(selectedAlert)" class="resolve-btn">
              Resolve Alert
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Policy Modal -->
    <div v-if="showPolicyModal || editingPolicy" class="modal-overlay" @click="closePolicyModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingPolicy ? 'Edit Policy' : 'Create Security Policy' }}</h3>
          <button @click="closePolicyModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="savePolicy">
            <div class="form-group">
              <label>Policy Name</label>
              <input v-model="policyForm.name" type="text" required />
            </div>
            <div class="form-group">
              <label>Policy Type</label>
              <select v-model="policyForm.type" required>
                <option value="password">Password Policy</option>
                <option value="session">Session Policy</option>
                <option value="access">Access Control</option>
                <option value="audit">Audit Policy</option>
              </select>
            </div>
            <div class="form-group">
              <label>Description</label>
              <textarea v-model="policyForm.description" rows="3" required></textarea>
            </div>
            <div class="form-group">
              <label>Policy Rules (JSON)</label>
              <textarea v-model="policyForm.rules" rows="6" placeholder='{"min_length": 8, "require_special": true}'></textarea>
            </div>
            <div class="form-group">
              <label>
                <input v-model="policyForm.enabled" type="checkbox" />
                Enable Policy
              </label>
            </div>
            <div class="form-actions">
              <button type="button" @click="closePolicyModal" class="cancel-btn">Cancel</button>
              <button type="submit" class="save-btn">
                {{ editingPolicy ? 'Update' : 'Create' }} Policy
              </button>
            </div>
          </form>
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
const { data: securityData, loading, error, refresh } = useApiData('/api/v1/security/', {
  immediate: true,
  transform: (data) => ({
    active_threats: data.active_threats || 0,
    failed_logins_24h: data.failed_logins_24h || 0,
    active_sessions: data.active_sessions || 0,
    compliance_score: data.compliance_score || 0
  }),
  retryAttempts: 3,
  onError: (error) => {
    console.error('Failed to load security data:', error)
  }
})

const { data: securityAlerts } = useApiData('/api/v1/security/alerts/', {
  immediate: true,
  transform: (data) => {
    if (data.results) {
      return data.results.map((alert: any) => ({
        id: alert.id,
        title: alert.title,
        description: alert.description,
        severity: alert.severity || 'medium',
        source: alert.source || 'System',
        created_at: alert.created_at,
        read: alert.read || false,
        resolved: alert.resolved || false,
        details: alert.details
      }))
    }
    return []
  }
})

const { data: auditLogs } = useApiData('/api/v1/audit-logs/', {
  immediate: true,
  transform: (data) => {
    if (data.results) {
      return data.results.map((log: any) => ({
        id: log.id,
        timestamp: log.timestamp || log.created_at,
        user: log.user,
        action: log.action,
        resource_type: log.resource_type,
        resource_id: log.resource_id,
        ip_address: log.ip_address,
        user_agent: log.user_agent,
        status: log.status || 'success'
      }))
    }
    return []
  }
})

const { data: securityPolicies } = useApiData('/api/v1/security/policies/', {
  immediate: true,
  transform: (data) => {
    if (data.results) {
      return data.results.map((policy: any) => ({
        id: policy.id,
        name: policy.name,
        type: policy.type,
        description: policy.description,
        rules: policy.rules || {},
        enabled: policy.enabled !== false,
        updated_at: policy.updated_at
      }))
    }
    return []
  }
})

// Filters and pagination
const alertFilter = ref('')
const auditFilter = ref('')
const auditPeriod = ref('24h')
const currentPage = ref(1)
const itemsPerPage = 20

// Modal state
const selectedAlert = ref(null)
const showPolicyModal = ref(false)
const editingPolicy = ref(null)
const policyForm = ref({
  name: '',
  type: 'password',
  description: '',
  rules: '',
  enabled: true
})

// Mutations
const { mutate: resolveAlertMutation } = useApiMutation(
  (alertId) => api.patch(`/api/v1/security/alerts/${alertId}/`, { resolved: true }),
  {
    onSuccess: () => refresh(),
    onError: (error) => handleApiError(error, { context: { action: 'resolve_alert' } })
  }
)

const { mutate: createPolicy } = useApiMutation(
  (policyData) => api.post('/api/v1/security/policies/', policyData),
  {
    onSuccess: () => {
      closePolicyModal()
      refresh()
    },
    onError: (error) => handleApiError(error, { context: { action: 'create_policy' } })
  }
)

const { mutate: updatePolicy } = useApiMutation(
  ({ id, ...policyData }) => api.patch(`/api/v1/security/policies/${id}/`, policyData),
  {
    onSuccess: () => {
      closePolicyModal()
      refresh()
    },
    onError: (error) => handleApiError(error, { context: { action: 'update_policy' } })
  }
)

// Computed properties
const filteredAlerts = computed(() => {
  if (!securityAlerts.value) return []
  
  return securityAlerts.value.filter(alert => {
    return !alertFilter.value || alert.severity === alertFilter.value
  })
})

const filteredAuditLogs = computed(() => {
  if (!auditLogs.value) return []
  
  return auditLogs.value.filter(log => {
    const matchesFilter = !auditFilter.value || log.action.includes(auditFilter.value)
    // Add period filtering logic here
    return matchesFilter
  })
})

const totalPages = computed(() => Math.ceil(filteredAuditLogs.value.length / itemsPerPage))

// Methods
const getComplianceClass = (score) => {
  if (score >= 90) return 'excellent'
  if (score >= 70) return 'good'
  if (score >= 50) return 'fair'
  return 'poor'
}

const getComplianceStatus = (score) => {
  if (score >= 90) return 'Excellent'
  if (score >= 70) return 'Good'
  if (score >= 50) return 'Fair'
  return 'Needs Improvement'
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const formatAction = (action) => {
  return action.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatStatus = (status) => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatPolicyType = (type) => {
  return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getActionClass = (action) => {
  if (action.includes('login')) return 'login'
  if (action.includes('admin')) return 'admin'
  if (action.includes('delete')) return 'delete'
  return 'default'
}

const truncateUserAgent = (userAgent) => {
  if (!userAgent) return 'N/A'
  return userAgent.length > 50 ? userAgent.substring(0, 50) + '...' : userAgent
}

const viewAlert = (alert) => {
  selectedAlert.value = alert
}

const closeAlertModal = () => {
  selectedAlert.value = null
}

const resolveAlert = async (alert) => {
  await resolveAlertMutation(alert.id)
  closeAlertModal()
}

const markAllAsRead = async () => {
  // Implement mark all as read functionality
  console.log('Mark all alerts as read')
}

const viewLogDetails = (log) => {
  // Implement log details view
  console.log('View log details:', log)
}

const editPolicy = (policy) => {
  editingPolicy.value = policy
  policyForm.value = {
    name: policy.name,
    type: policy.type,
    description: policy.description,
    rules: JSON.stringify(policy.rules, null, 2),
    enabled: policy.enabled
  }
}

const closePolicyModal = () => {
  showPolicyModal.value = false
  editingPolicy.value = null
  policyForm.value = {
    name: '',
    type: 'password',
    description: '',
    rules: '',
    enabled: true
  }
}

const savePolicy = async () => {
  const policyData = {
    ...policyForm.value,
    rules: JSON.parse(policyForm.value.rules || '{}')
  }
  
  if (editingPolicy.value) {
    await updatePolicy({ id: editingPolicy.value.id, ...policyData })
  } else {
    await createPolicy(policyData)
  }
}

const togglePolicy = async (policy) => {
  await updatePolicy({ id: policy.id, enabled: !policy.enabled })
}

const handleRetry = async () => {
  try {
    await refresh()
  } catch (err) {
    handleApiError(err, { context: { action: 'retry_security_load' } })
  }
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.security-view {
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

.card-content .status.critical {
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

.alerts-section,
.audit-section,
.policies-section {
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

.alert-filters,
.audit-filters {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.alert-filters select,
.audit-filters select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.mark-read-btn,
.create-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.mark-read-btn:hover,
.create-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.alerts-list {
  padding: 1.5rem;
}

.no-alerts {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.no-alerts-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
}

.alert-item.unread {
  border-left: 4px solid #f59e0b;
  background: #fffbeb;
}

.alert-item.critical {
  border-left-color: #dc2626;
}

.alert-item.high {
  border-left-color: #ea580c;
}

.alert-item.medium {
  border-left-color: #d97706;
}

.alert-item.low {
  border-left-color: #0891b2;
}

.alert-icon {
  font-size: 1.5rem;
  width: 40px;
  text-align: center;
}

.alert-content {
  flex: 1;
}

.alert-content h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.alert-content p {
  color: #6b7280;
  margin: 0 0 0.5rem 0;
  line-height: 1.5;
}

.alert-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #9ca3af;
}

.alert-actions {
  display: flex;
  gap: 0.5rem;
}

.audit-table {
  overflow-x: auto;
}

.audit-table table {
  width: 100%;
  border-collapse: collapse;
}

.audit-table th {
  background: #f9fafb;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.audit-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.audit-row:hover {
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

.action-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.action-badge.login {
  background: #dbeafe;
  color: #1e40af;
}

.action-badge.admin {
  background: #f3e8ff;
  color: #5b21b6;
}

.action-badge.delete {
  background: #fee2e2;
  color: #dc2626;
}

.action-badge.default {
  background: #f3f4f6;
  color: #374151;
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

.policies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.policy-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.policy-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.policy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.policy-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.policy-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  background: #fee2e2;
  color: #dc2626;
}

.policy-status.active {
  background: #dcfce7;
  color: #166534;
}

.policy-description {
  color: #6b7280;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.policy-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.policy-actions {
  display: flex;
  gap: 0.5rem;
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

.action-btn.view {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.view:hover {
  background: #bfdbfe;
}

.action-btn.resolve {
  background: #dcfce7;
  color: #166534;
}

.action-btn.resolve:hover {
  background: #bbf7d0;
}

.action-btn.edit {
  background: #fef3c7;
  color: #92400e;
}

.action-btn.edit:hover {
  background: #fde68a;
}

.action-btn.enable {
  background: #dcfce7;
  color: #166534;
}

.action-btn.enable:hover {
  background: #bbf7d0;
}

.action-btn.disable {
  background: #fee2e2;
  color: #dc2626;
}

.action-btn.disable:hover {
  background: #fecaca;
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
}

.close-btn:hover {
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.alert-details {
  margin-bottom: 1.5rem;
}

.detail-row {
  display: flex;
  margin-bottom: 1rem;
  align-items: flex-start;
}

.detail-row .label {
  font-weight: 500;
  color: #374151;
  min-width: 120px;
  margin-right: 1rem;
}

.detail-row .value {
  color: #1f2937;
  flex: 1;
}

.detail-row .value.critical {
  color: #dc2626;
  font-weight: 600;
}

.detail-row .value.high {
  color: #ea580c;
  font-weight: 600;
}

.detail-row .value.medium {
  color: #d97706;
  font-weight: 600;
}

.detail-row .value.low {
  color: #0891b2;
  font-weight: 600;
}

.detail-row pre {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  overflow-x: auto;
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

.form-actions,
.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  font-weight: 500;
}

.cancel-btn:hover {
  background: #f9fafb;
}

.save-btn,
.resolve-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.save-btn:hover,
.resolve-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
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