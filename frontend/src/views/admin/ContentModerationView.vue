<template>
  <div class="content-moderation-view">
    <div class="page-header">
      <h1>Content Moderation</h1>
      <p>Review and moderate user-generated content</p>
    </div>

    <!-- Moderation Queue -->
    <div class="moderation-container">
      <div class="queue-header">
        <h2>Pending Reviews</h2>
        <div class="queue-stats">
          <span class="stat">{{ pendingCount }} pending</span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading content for review...</p>
      </div>

      <!-- Content Items -->
      <div v-else class="content-items">
        <div v-for="item in contentItems" :key="item.id" class="content-item">
          <div class="item-header">
            <h3>{{ item.title }}</h3>
            <span class="content-type">{{ item.type }}</span>
          </div>
          <div class="item-content">
            <p>{{ item.content }}</p>
          </div>
          <div class="item-actions">
            <button @click="approveContent(item)" class="action-btn approve">Approve</button>
            <button @click="rejectContent(item)" class="action-btn reject">Reject</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
// Removed unused imports

// Mock data for now
const contentItems = ref([
  {
    id: 1,
    title: 'Course Review',
    type: 'Review',
    content: 'This course was amazing! I learned so much about web development.',
    status: 'pending'
  }
])

const loading = ref(false)
const pendingCount = computed(() => contentItems.value.filter((item: any) => item.status === 'pending').length)

const approveContent = (item: any) => {
  item.status = 'approved'
}

const rejectContent = (item: any) => {
  item.status = 'rejected'
}

onMounted(() => {
  // Load content items
})
</script>

<style scoped>
.content-moderation-view {
  max-width: 1200px;
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

.moderation-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.queue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.queue-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.stat {
  background: #fef3c7;
  color: #92400e;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.content-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.content-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.item-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.content-type {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.item-content p {
  color: #6b7280;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.item-actions {
  display: flex;
  gap: 1rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.approve {
  background: #dcfce7;
  color: #166534;
}

.action-btn.approve:hover {
  background: #bbf7d0;
}

.action-btn.reject {
  background: #fee2e2;
  color: #dc2626;
}

.action-btn.reject:hover {
  background: #fecaca;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
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
</style>