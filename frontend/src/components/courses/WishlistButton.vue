<template>
  <button
    @click="handleToggleWishlist"
    :disabled="loading"
    :class="[
      'wishlist-btn',
      {
        'in-wishlist': isInWishlist,
        'loading': loading,
        'compact': compact
      }
    ]"
    :title="isInWishlist ? 'Remove from wishlist' : 'Add to wishlist'"
  >
    <span class="wishlist-icon">
      <span v-if="loading" class="loading-spinner"></span>
      <span v-else-if="isInWishlist" class="heart-filled">❤️</span>
      <span v-else class="heart-empty">🤍</span>
    </span>
    <span v-if="!compact" class="wishlist-text">
      {{ isInWishlist ? 'In Wishlist' : 'Add to Wishlist' }}
    </span>
  </button>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useGlobalWishlist } from '@/composables/useWishlist'

interface Props {
  courseId: string
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  compact: false
})

const { isInWishlist: checkIsInWishlist, toggleGlobalWishlist, loadGlobalWishlistState } = useGlobalWishlist()
const loading = ref(false)

const isInWishlist = computed(() => checkIsInWishlist(props.courseId))

const handleToggleWishlist = async () => {
  if (loading.value) return
  
  loading.value = true
  try {
    await toggleGlobalWishlist(props.courseId)
  } catch (error) {
    console.error('Failed to toggle wishlist:', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // Load global wishlist state if not already loaded
  await loadGlobalWishlistState()
})
</script>

<style scoped>
.wishlist-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.wishlist-btn:hover:not(:disabled) {
  border-color: #f59e0b;
  background: #fef3e2;
  transform: translateY(-1px);
}

.wishlist-btn.in-wishlist {
  border-color: #ef4444;
  background: #fef2f2;
  color: #dc2626;
}

.wishlist-btn.in-wishlist:hover:not(:disabled) {
  border-color: #dc2626;
  background: #fee2e2;
}

.wishlist-btn.compact {
  padding: 0.5rem;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  justify-content: center;
}

.wishlist-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.wishlist-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #f3f4f6;
  border-top: 2px solid #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.heart-filled, .heart-empty {
  transition: all 0.3s ease;
}

.wishlist-btn:hover .heart-empty {
  transform: scale(1.1);
}

.wishlist-btn:hover .heart-filled {
  transform: scale(1.1);
}

.wishlist-text {
  white-space: nowrap;
}

/* Animation for adding to wishlist */
.wishlist-btn.in-wishlist .heart-filled {
  animation: heartBeat 0.6s ease-in-out;
}

@keyframes heartBeat {
  0% { transform: scale(1); }
  25% { transform: scale(1.2); }
  50% { transform: scale(1); }
  75% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

/* Responsive */
@media (max-width: 640px) {
  .wishlist-btn:not(.compact) {
    padding: 0.5rem;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    justify-content: center;
  }
  
  .wishlist-text {
    display: none;
  }
}
</style>