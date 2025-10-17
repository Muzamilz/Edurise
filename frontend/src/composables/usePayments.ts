import { ref, computed } from 'vue'
import { api } from '../services/api'
import type { 
  Payment, 
  Subscription, 
  Invoice, 
  PaymentCreateRequest, 
  SubscriptionCreateRequest,
  PaymentIntent,
  PayPalOrder,
  PaymentStats,
  SubscriptionPlan,
  BankTransferDetails,
  PaymentNotification
} from '../types/payments'

interface PaginatedResponse<T> {
  results: T[]
  count: number
  next: string | null
  previous: string | null
}

export const usePayments = () => {
  
  // State
  const payments = ref<Payment[]>([])
  const subscriptions = ref<Subscription[]>([])
  const invoices = ref<Invoice[]>([])
  const currentPayment = ref<Payment | null>(null)
  const currentSubscription = ref<Subscription | null>(null)
  const currentInvoice = ref<Invoice | null>(null)
  const paymentStats = ref<PaymentStats | null>(null)
  const subscriptionPlans = ref<SubscriptionPlan[]>([])
  const notifications = ref<PaymentNotification[]>([])
  
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Payment processing state
  const processingPayment = ref(false)
  const paymentIntent = ref<PaymentIntent | null>(null)
  const paypalOrder = ref<PayPalOrder | null>(null)
  const bankTransferDetails = ref<BankTransferDetails | null>(null)
  
  // Computed
  const totalRevenue = computed(() => 
    payments.value
      .filter(p => p.status === 'completed')
      .reduce((sum, p) => sum + p.amount, 0)
  )
  
  const pendingPayments = computed(() => 
    payments.value.filter(p => p.status === 'pending')
  )
  
  const failedPayments = computed(() => 
    payments.value.filter(p => p.status === 'failed')
  )
  
  const activeSubscription = computed(() => 
    subscriptions.value.find(s => s.is_active_status)
  )
  
  const overdueInvoices = computed(() => 
    invoices.value.filter(i => i.status === 'overdue')
  )
  
  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.is_read)
  )
  
  // Payment Methods
  const fetchPayments = async (filters?: any) => {
    loading.value = true
    error.value = null
    
    try {
      const params = new URLSearchParams()
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== null && value !== undefined) {
            params.append(key, String(value))
          }
        })
      }
      
      const response = await api.get<PaginatedResponse<Payment>>(`/v1/payments/?${params}`)
      payments.value = response.data.data.results
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch payments'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const fetchPayment = async (id: string) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get<Payment>(`/v1/payments/${id}/`)
      currentPayment.value = response.data.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch payment'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const createCoursePayment = async (request: PaymentCreateRequest) => {
    processingPayment.value = true
    error.value = null
    
    try {
      const response = await api.post('/v1/payments/create_course_payment/', request)
      
      if (request.payment_method === 'stripe') {
        paymentIntent.value = {
          id: response.data.data.payment_intent_id,
          client_secret: response.data.data.client_secret,
          amount: request.amount,
          currency: request.currency || 'USD',
          status: 'requires_payment_method'
        }
      } else if (request.payment_method === 'paypal') {
        paypalOrder.value = {
          id: response.data.data.order_id,
          approval_url: response.data.data.approval_url,
          amount: request.amount,
          currency: request.currency || 'USD',
          status: 'created'
        }
      } else if (request.payment_method === 'bank_transfer') {
        bankTransferDetails.value = response.data.data.bank_transfer_details
      }
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create payment'
      throw err
    } finally {
      processingPayment.value = false
    }
  }
  
  const confirmPayment = async (paymentId: string) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post(`/v1/payments/${paymentId}/confirm_payment/`)
      
      // Update payment in list
      const index = payments.value.findIndex(p => p.id === paymentId)
      if (index !== -1) {
        payments.value[index] = { ...payments.value[index], status: 'completed' }
      }
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to confirm payment'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Subscription Methods
  const fetchSubscriptions = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get<PaginatedResponse<Subscription>>('/v1/subscriptions/')
      subscriptions.value = response.data.data.results
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch subscriptions'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const createSubscription = async (request: SubscriptionCreateRequest) => {
    processingPayment.value = true
    error.value = null
    
    try {
      const response = await api.post('/v1/subscriptions/create_subscription/', request)
      
      // Add to subscriptions list
      subscriptions.value.push(response.data.data.subscription)
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create subscription'
      throw err
    } finally {
      processingPayment.value = false
    }
  }
  
  const cancelSubscription = async (subscriptionId: string) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post(`/v1/subscriptions/${subscriptionId}/cancel_subscription/`)
      
      // Update subscription in list
      const index = subscriptions.value.findIndex(s => s.id === subscriptionId)
      if (index !== -1) {
        subscriptions.value[index] = { ...subscriptions.value[index], status: 'cancelled' }
      }
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to cancel subscription'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const renewSubscription = async (subscriptionId: string) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post(`/v1/subscriptions/${subscriptionId}/renew_subscription/`)
      
      // Update subscription in list
      const index = subscriptions.value.findIndex(s => s.id === subscriptionId)
      if (index !== -1) {
        subscriptions.value[index] = { ...subscriptions.value[index], status: 'active' }
      }
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to renew subscription'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Subscription Plan Methods
  const fetchSubscriptionPlans = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/v1/subscription-plans/')
      subscriptionPlans.value = response.data.data.results
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch subscription plans'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const fetchSubscriptionPlansComparison = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/v1/subscription-plans/compare/')
      return response.data.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch subscription plans comparison'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const fetchBillingAutomation = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/v1/subscriptions/billing_automation/')
      return response.data.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch billing automation data'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Analytics Methods
  const fetchPaymentAnalytics = async (timeframe: 'day' | 'week' | 'month' | 'year' = 'month') => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/v1/payments/payment_analytics/', {
        params: { timeframe }
      })
      return response.data.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch payment analytics'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const fetchInvoiceAnalytics = async (timeframe: 'day' | 'week' | 'month' | 'year' = 'month') => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/v1/invoices/invoice_analytics/', {
        params: { timeframe }
      })
      return response.data.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch invoice analytics'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Invoice Methods
  const fetchInvoices = async (filters?: any) => {
    loading.value = true
    error.value = null
    
    try {
      const params = new URLSearchParams()
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== null && value !== undefined) {
            params.append(key, String(value))
          }
        })
      }
      
      const response = await api.get<PaginatedResponse<Invoice>>(`/v1/invoices/?${params}`)
      invoices.value = response.data.data.results
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch invoices'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const fetchInvoice = async (id: string) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get<Invoice>(`/v1/invoices/${id}/`)
      currentInvoice.value = response.data.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch invoice'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const downloadInvoice = async (invoiceId: string) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get(`/v1/invoices/${invoiceId}/download/`, {
        responseType: 'blob'
      })
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `invoice-${invoiceId}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to download invoice'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Analytics Methods
  const fetchPaymentStats = async (timeframe: 'day' | 'week' | 'month' | 'year' = 'month') => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get<PaymentStats>('/v1/payments/revenue_stats/', {
        params: { timeframe }
      })
      paymentStats.value = response.data.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch payment stats'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Utility Methods
  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount)
  }
  
  const getPaymentStatusColor = (status: string) => {
    const colors = {
      pending: 'text-yellow-600 bg-yellow-100',
      processing: 'text-blue-600 bg-blue-100',
      completed: 'text-green-600 bg-green-100',
      failed: 'text-red-600 bg-red-100',
      cancelled: 'text-gray-600 bg-gray-100',
      refunded: 'text-purple-600 bg-purple-100'
    }
    return colors[status as keyof typeof colors] || 'text-gray-600 bg-gray-100'
  }
  
  const getPaymentMethodIcon = (method: string) => {
    const icons = {
      stripe: '💳',
      paypal: '🅿️',
      bank_transfer: '🏦'
    }
    return icons[method as keyof typeof icons] || '💳'
  }
  
  const getSubscriptionStatusColor = (status: string) => {
    const colors = {
      active: 'text-green-600 bg-green-100',
      cancelled: 'text-red-600 bg-red-100',
      past_due: 'text-orange-600 bg-orange-100',
      unpaid: 'text-red-600 bg-red-100',
      trialing: 'text-blue-600 bg-blue-100'
    }
    return colors[status as keyof typeof colors] || 'text-gray-600 bg-gray-100'
  }
  
  const clearError = () => {
    error.value = null
  }
  
  const resetPaymentState = () => {
    paymentIntent.value = null
    paypalOrder.value = null
    bankTransferDetails.value = null
    processingPayment.value = false
    error.value = null
  }
  
  return {
    // State
    payments,
    subscriptions,
    invoices,
    currentPayment,
    currentSubscription,
    currentInvoice,
    paymentStats,
    subscriptionPlans,
    notifications,
    loading,
    error,
    processingPayment,
    paymentIntent,
    paypalOrder,
    bankTransferDetails,
    
    // Computed
    totalRevenue,
    pendingPayments,
    failedPayments,
    activeSubscription,
    overdueInvoices,
    unreadNotifications,
    
    // Methods
    fetchPayments,
    fetchPayment,
    createCoursePayment,
    confirmPayment,
    fetchSubscriptions,
    createSubscription,
    cancelSubscription,
    renewSubscription,
    fetchSubscriptionPlans,
    fetchSubscriptionPlansComparison,
    fetchBillingAutomation,
    fetchInvoices,
    fetchInvoice,
    downloadInvoice,
    fetchPaymentStats,
    fetchPaymentAnalytics,
    fetchInvoiceAnalytics,
    
    // Utilities
    formatCurrency,
    getPaymentStatusColor,
    getPaymentMethodIcon,
    getSubscriptionStatusColor,
    clearError,
    resetPaymentState
  }
}