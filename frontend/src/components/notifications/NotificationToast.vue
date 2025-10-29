<template>
  <Teleport to="body">
    <div class="toast-container">
      <Transition
        v-for="toast in toasts"
        :key="toast.id"
        name="toast"
        appear
      >
        <div
          class="toast"
          :class="[
            `toast--${toast.type}`,
            { 'toast--dismissible': toast.dismissible }
          ]"
        >
          <div class="toast-icon">
            <span v-if="toast.type === 'success'">✅</span>
            <span v-else-if="toast.type === 'error'">❌</span>
            <span v-else-if="toast.type === 'warning'">⚠️</span>
            <span v-else>ℹ️</span>
          </div>
          
          <div class="toast-content">
            <div v-if="toast.title" class="toast-title">{{ toast.title }}</div>
            <div class="toast-message">{{ toast.message }}</div>
          </div>
          
          <button
            v-if="toast.dismissible"
            @click="removeToast(toast.id)"
            class="toast-close"
          >
            ✕
          </button>
          
          <div
            v-if="toast.duration"
            class="toast-progress"
            :style="{ animationDuration: `${toast.duration}ms` }"
          ></div>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Toast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  duration?: number
  dismissible?: boolean
}

const toasts = ref<Toast[]>([])

const addToast = (toast: Omit<Toast, 'id'>) => {
  const id = Date.now().toString()
  const newToast: Toast = {
    id,
    dismissible: true,
    duration: 5000,
    ...toast
  }
  
  toasts.value.push(newToast)
  
  if (newToast.duration) {
    setTimeout(() => {
      removeToast(id)
    }, newToast.duration)
  }
}

const removeToast = (id: string) => {
  const index = toasts.value.findIndex(toast => toast.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

// Listen for custom toast events
onMounted(() => {
  window.addEventListener('show-toast', ((event: CustomEvent) => {
    addToast(event.detail)
  }) as EventListener)
})

defineExpose({
  addToast,
  removeToast
})
</script>

<style scoped>
.toast-container {
  @apply fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none;
  max-width: 400px;
}

.toast {
  @apply relative flex items-start gap-3 p-4 rounded-lg shadow-lg border pointer-events-auto;
  backdrop-filter: blur(10px);
  min-width: 300px;
}

.toast--success {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #065f46;
}

.toast--error {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05));
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #991b1b;
}

.toast--warning {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.05));
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #92400e;
}

.toast--info {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.05));
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #92400e;
}

.toast-icon {
  @apply flex-shrink-0 text-lg;
}

.toast-content {
  @apply flex-1 min-w-0;
}

.toast-title {
  @apply font-semibold text-sm mb-1;
}

.toast-message {
  @apply text-sm leading-relaxed;
}

.toast-close {
  @apply flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors cursor-pointer bg-none border-none text-sm;
}

.toast-progress {
  @apply absolute bottom-0 left-0 h-1 bg-current opacity-30 rounded-b-lg;
  animation: progress linear;
  transform-origin: left;
}

@keyframes progress {
  0% { width: 100%; }
  100% { width: 0%; }
}

/* Toast transitions */
.toast-enter-active {
  @apply transition-all duration-300 ease-out;
}

.toast-leave-active {
  @apply transition-all duration-200 ease-in;
}

.toast-enter-from {
  @apply opacity-0;
  transform: translateX(100%) scale(0.95);
}

.toast-leave-to {
  @apply opacity-0;
  transform: translateX(100%) scale(0.95);
}

.toast-enter-to,
.toast-leave-from {
  @apply opacity-100;
  transform: translateX(0) scale(1);
}
</style>