<template>
  <div class="modal-overlay" @click="$emit('cancel')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <div class="modal-icon" :class="iconClass">
          <i :class="icon"></i>
        </div>
        <h2>{{ title }}</h2>
      </div>

      <div class="modal-body">
        <p>{{ message }}</p>
        <div v-if="details" class="details">
          {{ details }}
        </div>
      </div>

      <div class="modal-footer">
        <button
          type="button"
          @click="$emit('cancel')"
          class="btn btn-outline"
          :disabled="loading"
        >
          {{ cancelText }}
        </button>
        <button
          type="button"
          @click="$emit('confirm')"
          class="btn"
          :class="confirmClass"
          :disabled="loading"
        >
          {{ loading ? 'Processing...' : confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  message: string
  details?: string
  confirmText?: string
  cancelText?: string
  confirmClass?: string
  type?: 'danger' | 'warning' | 'info' | 'success'
  loading?: boolean
}

interface Emits {
  (e: 'confirm'): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  confirmClass: 'btn-primary',
  type: 'danger',
  loading: false
})

defineEmits<Emits>()

const icon = computed(() => {
  switch (props.type) {
    case 'danger':
      return 'fas fa-exclamation-triangle'
    case 'warning':
      return 'fas fa-exclamation-circle'
    case 'info':
      return 'fas fa-info-circle'
    case 'success':
      return 'fas fa-check-circle'
    default:
      return 'fas fa-exclamation-triangle'
  }
})

const iconClass = computed(() => {
  switch (props.type) {
    case 'danger':
      return 'icon-danger'
    case 'warning':
      return 'icon-warning'
    case 'info':
      return 'icon-info'
    case 'success':
      return 'icon-success'
    default:
      return 'icon-danger'
  }
})
</script>

<style scoped>
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
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 1.5rem 1rem;
  text-align: center;
}

.modal-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.icon-danger {
  background: #fef2f2;
  color: #dc2626;
}

.icon-warning {
  background: #fffbeb;
  color: #d97706;
}

.icon-info {
  background: #eff6ff;
  color: #2563eb;
}

.icon-success {
  background: #f0fdf4;
  color: #16a34a;
}

.modal-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.modal-body {
  padding: 0 1.5rem 1.5rem;
  text-align: center;
}

.modal-body p {
  margin: 0 0 1rem 0;
  color: #6b7280;
  line-height: 1.5;
}

.details {
  padding: 0.75rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #374151;
  text-align: left;
}

.modal-footer {
  display: flex;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-danger {
  background: #dc2626;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #b91c1c;
}

.btn-warning {
  background: #d97706;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: #b45309;
}

.btn-outline {
  background: transparent;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background: #f9fafb;
}
</style>