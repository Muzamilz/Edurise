<template>
  <div class="system-view">
    <div class="page-header">
      <h1>System Administration</h1>
      <p>Monitor system health and manage platform settings</p>
    </div>

    <!-- System Health -->
    <div class="health-section">
      <h3>System Health</h3>
      <div class="health-grid">
        <div class="health-card">
          <div class="health-header">
            <h4>Database</h4>
            <div class="health-status online">Online</div>
          </div>
          <div class="health-metrics">
            <div class="metric">
              <span>Connections:</span>
              <span>25/100</span>
            </div>
            <div class="metric">
              <span>Response Time:</span>
              <span>12ms</span>
            </div>
          </div>
        </div>

        <div class="health-card">
          <div class="health-header">
            <h4>API Services</h4>
            <div class="health-status online">Online</div>
          </div>
          <div class="health-metrics">
            <div class="metric">
              <span>Uptime:</span>
              <span>99.9%</span>
            </div>
            <div class="metric">
              <span>Requests/min:</span>
              <span>1,250</span>
            </div>
          </div>
        </div>

        <div class="health-card">
          <div class="health-header">
            <h4>Storage</h4>
            <div class="health-status warning">Warning</div>
          </div>
          <div class="health-metrics">
            <div class="metric">
              <span>Used:</span>
              <span>75GB/100GB</span>
            </div>
            <div class="metric">
              <span>Available:</span>
              <span>25GB</span>
            </div>
          </div>
        </div>

        <div class="health-card">
          <div class="health-header">
            <h4>Cache</h4>
            <div class="health-status online">Online</div>
          </div>
          <div class="health-metrics">
            <div class="metric">
              <span>Hit Rate:</span>
              <span>94%</span>
            </div>
            <div class="metric">
              <span>Memory:</span>
              <span>2.1GB/4GB</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- System Logs -->
    <div class="logs-section">
      <div class="logs-header">
        <h3>Recent System Logs</h3>
        <div class="log-controls">
          <select v-model="logLevel" class="log-filter">
            <option value="">All Levels</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
          </select>
          <button @click="refreshLogs" class="refresh-btn">Refresh</button>
        </div>
      </div>
      
      <div class="logs-container">
        <div v-for="log in filteredLogs" :key="log.id" :class="['log-entry', log.level]">
          <div class="log-timestamp">{{ formatTimestamp(log.timestamp) }}</div>
          <div class="log-level">{{ log.level.toUpperCase() }}</div>
          <div class="log-message">{{ log.message }}</div>
        </div>
      </div>
    </div>

    <!-- System Actions -->
    <div class="actions-section">
      <h3>System Actions</h3>
      <div class="actions-grid">
        <button @click="clearCache" class="action-btn">
          <span class="btn-icon">🗑️</span>
          Clear Cache
        </button>
        
        <button @click="runMaintenance" class="action-btn">
          <span class="btn-icon">🔧</span>
          Run Maintenance
        </button>
        
        <button @click="backupDatabase" class="action-btn">
          <span class="btn-icon">💾</span>
          Backup Database
        </button>
        
        <button @click="exportLogs" class="action-btn">
          <span class="btn-icon">📄</span>
          Export Logs
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const logLevel = ref('')

// Mock system logs
const systemLogs = ref([
  {
    id: 1,
    timestamp: new Date(),
    level: 'info',
    message: 'User authentication successful for user@example.com'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 60000),
    level: 'warning',
    message: 'Storage usage is above 75% threshold'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 120000),
    level: 'error',
    message: 'Failed to send email notification to user@example.com'
  }
])

const filteredLogs = computed(() => {
  if (!logLevel.value) return systemLogs.value
  return systemLogs.value.filter(log => log.level === logLevel.value)
})

const formatTimestamp = (timestamp) => {
  return timestamp.toLocaleString()
}

const refreshLogs = () => {
  // Refresh system logs
  console.log('Refreshing logs...')
}

const clearCache = () => {
  if (confirm('Are you sure you want to clear the cache?')) {
    console.log('Clearing cache...')
  }
}

const runMaintenance = () => {
  if (confirm('Are you sure you want to run system maintenance?')) {
    console.log('Running maintenance...')
  }
}

const backupDatabase = () => {
  if (confirm('Are you sure you want to backup the database?')) {
    console.log('Starting database backup...')
  }
}

const exportLogs = () => {
  console.log('Exporting logs...')
}

onMounted(() => {
  // Load system data
})
</script>

<style scoped>
.system-view {
  max-width: 1400px;
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

.health-section,
.logs-section,
.actions-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.health-section h3,
.logs-section h3,
.actions-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.health-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
}

.health-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.health-header h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.health-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.health-status.online {
  background: #dcfce7;
  color: #166534;
}

.health-status.warning {
  background: #fef3c7;
  color: #92400e;
}

.health-status.error {
  background: #fee2e2;
  color: #dc2626;
}

.health-metrics {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metric {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.metric span:first-child {
  color: #6b7280;
}

.metric span:last-child {
  color: #1f2937;
  font-weight: 500;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.log-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.log-filter {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.refresh-btn {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: #bfdbfe;
}

.logs-container {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.log-entry {
  display: grid;
  grid-template-columns: 150px 80px 1fr;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.875rem;
}

.log-entry:last-child {
  border-bottom: none;
}

.log-entry.error {
  background: #fef2f2;
}

.log-entry.warning {
  background: #fffbeb;
}

.log-entry.info {
  background: #f0f9ff;
}

.log-timestamp {
  color: #6b7280;
}

.log-level {
  font-weight: 600;
}

.log-level.ERROR {
  color: #dc2626;
}

.log-level.WARNING {
  color: #d97706;
}

.log-level.INFO {
  color: #2563eb;
}

.log-message {
  color: #1f2937;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-btn {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  color: #374151;
}

.action-btn:hover {
  background: #f9fafb;
  border-color: #f59e0b;
  transform: translateY(-1px);
}

.btn-icon {
  font-size: 1.25rem;
}
</style>