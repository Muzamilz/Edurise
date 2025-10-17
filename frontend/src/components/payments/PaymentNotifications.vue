<template>
  <div class="payment-notifications">
    <!-- Notifications Header -->
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-lg font-semibold text-gray-900">Payment Notifications</h3>
      <div class="flex items-center space-x-2">
        <button
          @click="markAllAsRead"
          :disabled="unreadCount === 0"
          class="text-sm text-blue-600 hover:text-blue-800 disabled:text-gray-400 disabled:cursor-not-allowed"
        >
          Mark all as read
        </button>
        <span class="text-sm text-gray-500">
          {{ unreadCount }} unread
        </span>
      </div>
    </div>

    <!-- Notifications List -->
    <div class="notifications-list space-y-3">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="[
          'notification-item p-4 rounded-lg border transition-all duration-200 cursor-pointer',
          notification.is_read
            ? 'bg-white border-gray-200 hover:border-gray-300'
            : 'bg-blue-50 border-blue-200 hover:border-blue-300'
        ]"
        @click="handleNotificationClick(notification)"
      >
        <div class="flex items-start space-x-3">
          <!-- Notification Icon -->
          <div
            :class="[
              'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
              getNotificationIconColor(notification.type)
            ]"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path v-if="notification.type === 'payment_success'" fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              <path v-else-if="notification.type === 'payment_failed'" fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              <path v-else-if="notification.type === 'subscription_renewed'" fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
              <path v-else-if="notification.type === 'invoice_sent'" fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
              <path v-else fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>

          <!-- Notification Content -->
          <div class="flex-1 min-w-0">
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h4
                  :class="[
                    'text-sm font-medium',
                    notification.is_read ? 'text-gray-900' : 'text-gray-900 font-semibold'
                  ]"
                >
                  {{ notification.title }}
                </h4>
                <p
                  :class="[
                    'text-sm mt-1',
                    notification.is_read ? 'text-gray-600' : 'text-gray-700'
                  ]"
                >
                  {{ notification.message }}
                </p>
              </div>
              
              <!-- Unread Indicator -->
              <div
                v-if="!notification.is_read"
                class="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full ml-2"
              ></div>
            </div>

            <!-- Notification Meta -->
            <div class="flex justify-between items-center mt-2">
              <span class="text-xs text-gray-500">
                {{ formatRelativeTime(notification.created_at) }}
              </span>
              
              <!-- Action Buttons -->
              <div class="flex space-x-2">
                <button
                  v-if="notification.payment_id"
                  @click.stop="viewPayment(notification.payment_id)"
                  class="text-xs text-blue-600 hover:text-blue-800"
                >
                  View Payment
                </button>
                <button
                  v-if="notification.invoice_id"
                  @click.stop="viewInvoice(notification.invoice_id)"
                  class="text-xs text-blue-600 hover:text-blue-800"
                >
                  View Invoice
                </button>
                <button
                  v-if="notification.subscription_id"
                  @click.stop="viewSubscription(notification.subscription_id)"
                  class="text-xs text-blue-600 hover:text-blue-800"
                >
                  View Subscription
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="notifications.length === 0" class="empty-state text-center py-12">
      <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM4 19h6v-2H4v2zM4 15h8v-2H4v2zM4 11h8V9H4v2zM4 7h8V5H4v2z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No notifications</h3>
      <p class="text-gray-600">You're all caught up! Payment notifications will appear here.</p>
    </div>

    <!-- Load More Button -->
    <div v-if="hasMore" class="text-center mt-6">
      <button
        @click="loadMore"
        :disabled="loading"
        class="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
      >
        <div v-if="loading" class="flex items-center">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
          Loading...
        </div>
        <span v-else>Load More</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { PaymentNotification } from '../../types/payments'

interface Props {
  limit?: number
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  limit: 10,
  showActions: true
})

const emit = defineEmits<{
  notificationClick: [notification: PaymentNotification]
  viewPayment: [paymentId: string]
  viewInvoice: [invoiceId: string]
  viewSubscription: [subscriptionId: string]
}>()

const router = useRouter()

// Mock data - in real app, this would come from API
const notifications = ref<PaymentNotification[]>([
  {
    id: '1',
    type: 'payment_success',
    title: 'Payment Successful',
    message: 'Your payment of $79.00 for Professional Plan has been processed successfully.',
    payment_id: 'pay_123',
    created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
    is_read: false
  },
  {
    id: '2',
    type: 'invoice_sent',
    title: 'Invoice Generated',
    message: 'Invoice #INV-202412-0001 has been generated and sent to your email.',
    invoice_id: 'inv_123',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
    is_read: false
  },
  {
    id: '3',
    type: 'subscription_renewed',
    title: 'Subscription Renewed',
    message: 'Your Professional Plan subscription has been automatically renewed.',
    subscription_id: 'sub_123',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // 1 day ago
    is_read: true
  },
  {
    id: '4',
    type: 'payment_failed',
    title: 'Payment Failed',
    message: 'Your payment attempt failed. Please update your payment method.',
    payment_id: 'pay_124',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(), // 2 days ago
    is_read: true
  },
  {
    id: '5',
    type: 'payment_overdue',
    title: 'Payment Overdue',
    message: 'Invoice #INV-202411-0045 is now overdue. Please make payment to avoid service interruption.',
    invoice_id: 'inv_124',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(), // 3 days ago
    is_read: true
  }
])

const loading = ref(false)
const hasMore = ref(false)

const unreadCount = computed(() => 
  notifications.value.filter(n => !n.is_read).length
)

const getNotificationIconColor = (type: string) => {
  const colors = {
    payment_success: 'bg-green-100 text-green-600',
    payment_failed: 'bg-red-100 text-red-600',
    subscription_renewed: 'bg-blue-100 text-blue-600',
    subscription_cancelled: 'bg-orange-100 text-orange-600',
    invoice_sent: 'bg-purple-100 text-purple-600',
    payment_overdue: 'bg-red-100 text-red-600'
  }
  return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-600'
}

const formatRelativeTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (diffInSeconds < 60) {
    return 'Just now'
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60)
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600)
    return `${hours} hour${hours > 1 ? 's' : ''} ago`
  } else if (diffInSeconds < 604800) {
    const days = Math.floor(diffInSeconds / 86400)
    return `${days} day${days > 1 ? 's' : ''} ago`
  } else {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    })
  }
}

const handleNotificationClick = (notification: PaymentNotification) => {
  if (!notification.is_read) {
    markAsRead(notification.id)
  }
  emit('notificationClick', notification)
}

const markAsRead = (notificationId: string) => {
  const notification = notifications.value.find(n => n.id === notificationId)
  if (notification) {
    notification.is_read = true
  }
}

const markAllAsRead = () => {
  notifications.value.forEach(notification => {
    notification.is_read = true
  })
}

const viewPayment = (paymentId: string) => {
  emit('viewPayment', paymentId)
  if (props.showActions) {
    router.push(`/payments/${paymentId}`)
  }
}

const viewInvoice = (invoiceId: string) => {
  emit('viewInvoice', invoiceId)
  if (props.showActions) {
    router.push(`/invoices/${invoiceId}`)
  }
}

const viewSubscription = (subscriptionId: string) => {
  emit('viewSubscription', subscriptionId)
  if (props.showActions) {
    router.push(`/subscriptions/${subscriptionId}`)
  }
}

const loadMore = () => {
  loading.value = true
  // Simulate API call
  setTimeout(() => {
    loading.value = false
    hasMore.value = false
  }, 1000)
}

onMounted(() => {
  // In real app, fetch notifications from API
})
</script>

<style scoped>
.notification-item {
  animation: slideInRight 0.3s ease-out;
}

.notification-item:hover {
  transform: translateX(2px);
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>