<template>
  <div class="notification-badge-wrapper">
    <slot />
    <Transition name="badge-bounce">
      <div 
        v-if="count > 0" 
        class="notification-badge"
        :class="badgeClasses"
      >
        {{ displayCount }}
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  count: number
  maxCount?: number
  variant?: 'default' | 'urgent' | 'success' | 'warning'
  size?: 'sm' | 'md' | 'lg'
  pulse?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  maxCount: 99,
  variant: 'default',
  size: 'md',
  pulse: false
})

const displayCount = computed(() => {
  return props.count > props.maxCount ? `${props.maxCount}+` : props.count.toString()
})

const badgeClasses = computed(() => ({
  [`badge--${props.variant}`]: true,
  [`badge--${props.size}`]: true,
  'badge--pulse': props.pulse
}))
</script>

<style scoped>
.notification-badge-wrapper {
  @apply relative inline-block;
}

.notification-badge {
  position: absolute;
  top: -0.5rem;
  right: -0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  min-width: 1.25rem;
  height: 1.25rem;
  padding: 0 0.25rem;
  transform-origin: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  border: 2px solid white;
}

/* Variants */
.badge--default {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.badge--urgent {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  animation: urgentPulse 1.5s ease-in-out infinite;
}

.badge--success {
  background: linear-gradient(135deg, #10b981, #059669);
}

.badge--warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

/* Sizes */
.badge--sm {
  @apply text-xs;
  min-width: 16px;
  height: 16px;
  font-size: 10px;
}

.badge--md {
  @apply text-xs;
  min-width: 20px;
  height: 20px;
}

.badge--lg {
  @apply text-sm;
  min-width: 24px;
  height: 24px;
}

/* Pulse animation */
.badge--pulse {
  animation: badgePulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% { 
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
  }
  50% { 
    transform: scale(1.1);
    box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
  }
}

@keyframes urgentPulse {
  0%, 100% {
    background-color: #dc2626;
    transform: scale(1);
  }
  50% {
    background-color: #ef4444;
    transform: scale(1.1);
  }
}

/* Badge transitions */
.badge-bounce-enter-active {
  animation: badgeBounceIn 0.5s ease-out;
}

.badge-bounce-leave-active {
  animation: badgeBounceOut 0.3s ease-in;
}

@keyframes badgeBounceIn {
  0% {
    transform: scale(0) rotate(180deg);
    opacity: 0;
  }
  50% {
    transform: scale(1.3) rotate(90deg);
    opacity: 1;
  }
  100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}

@keyframes badgeBounceOut {
  0% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: scale(0) rotate(-180deg);
    opacity: 0;
  }
}
</style>