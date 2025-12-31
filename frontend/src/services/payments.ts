import { api } from './api'
import type { Payment, PaginatedResponse, PaymentCapture, PayPalOrder } from '../types/api'

export class PaymentService {
  // ===== PayPal Payment Methods =====
  
  /**
   * Create a PayPal order for course purchase
   * @param amount - Payment amount
   * @param courseId - Course ID to purchase
   * @param currency - Currency code (default: USD)
   * @returns PayPal order with approval URL
   */
  static async createPayPalOrder(amount: number, courseId: string, currency: string = 'USD'): Promise<PayPalOrder> {
    try {
      const response = await api.post<PayPalOrder>('/payments/paypal/create-order/', {
        amount,
        course_id: courseId,
        currency
      })
      return response.data.data
    } catch (error) {
      console.error('Failed to create PayPal order:', error)
      throw error
    }
  }
  
  /**
   * Capture a PayPal payment after user approval
   * @param orderId - PayPal order ID
   * @param payerId - PayPal payer ID (optional, may be included in order)
   * @returns Payment capture confirmation
   */
  static async capturePayPalPayment(orderId: string, payerId?: string): Promise<PaymentCapture> {
    try {
      const response = await api.post<PaymentCapture>('/payments/paypal/capture-order/', {
        order_id: orderId,
        payer_id: payerId
      })
      return response.data.data
    } catch (error) {
      console.error('Failed to capture PayPal payment:', error)
      throw error
    }
  }
  // Payment operations - using centralized API endpoints
  static async getPayments(): Promise<PaginatedResponse<Payment>> {
    const response = await api.get<PaginatedResponse<Payment>>('/payments/')
    return response.data.data
  }

  static async getPayment(id: string): Promise<Payment> {
    const response = await api.get<Payment>(`/payments/${id}/`)
    return response.data.data
  }

  // Course purchase - using centralized API
  static async purchaseCourse(courseId: string, amount: number, paymentMethod: 'stripe' | 'paypal' | 'bank_transfer'): Promise<{
    payment_id: string
    client_secret?: string // For Stripe
    approval_url?: string // For PayPal
    order_id?: string // For PayPal
    bank_transfer_details?: any // For Bank Transfer
  }> {
    const response = await api.post('/payments/create_course_payment/', {
      course_id: courseId,
      amount: amount,
      payment_method: paymentMethod
    })
    return response.data.data
  }

  // Payment confirmation - using centralized API
  static async confirmPayment(paymentId: string): Promise<Payment> {
    const response = await api.post<Payment>(`/payments/${paymentId}/confirm_payment/`)
    return response.data.data
  }

  // Bank transfer approval (admin only) - using centralized API
  static async approveBankTransfer(paymentId: string): Promise<{ message: string }> {
    const response = await api.post(`/payments/${paymentId}/approve_bank_transfer/`)
    return response.data.data
  }

  static async rejectBankTransfer(paymentId: string, reason?: string): Promise<{ message: string }> {
    const response = await api.post(`/payments/${paymentId}/reject_bank_transfer/`, {
      reason: reason || ''
    })
    return response.data.data
  }

  // Payment history - using centralized API
  static async getUserPaymentHistory(): Promise<PaginatedResponse<Payment>> {
    const response = await api.get<PaginatedResponse<Payment>>('/payments/')
    return response.data.data
  }

  // Payment status updates and notifications - using centralized API
  static async getPaymentNotifications(): Promise<any[]> {
    const response = await api.get('/notifications/')
    return response.data.data.results.filter((n: any) => 
      ['payment_success', 'payment_failed', 'payment_overdue'].includes(n.type)
    )
  }

  // Subscription management - using centralized API
  static async getSubscriptions(): Promise<PaginatedResponse<any>> {
    const response = await api.get<PaginatedResponse<any>>('/subscriptions/')
    return response.data.data
  }

  static async createSubscription(plan: string, billingCycle: 'monthly' | 'yearly' = 'monthly', paymentMethod: 'stripe' | 'paypal' | 'bank_transfer' = 'stripe'): Promise<any> {
    const response = await api.post('/subscriptions/create_subscription/', {
      plan,
      billing_cycle: billingCycle,
      payment_method: paymentMethod
    })
    return response.data.data
  }

  static async cancelSubscription(subscriptionId: string): Promise<any> {
    const response = await api.post(`/subscriptions/${subscriptionId}/cancel_subscription/`)
    return response.data.data
  }

  static async renewSubscription(subscriptionId: string): Promise<any> {
    const response = await api.post(`/subscriptions/${subscriptionId}/renew_subscription/`)
    return response.data.data
  }

  // Subscription plans - using centralized API
  static async getSubscriptionPlans(): Promise<any[]> {
    const response = await api.get('/subscription-plans/')
    return response.data.data.results
  }

  static async getSubscriptionPlansComparison(): Promise<any> {
    const response = await api.get('/subscription-plans/compare/')
    return response.data.data
  }

  // Billing automation - using centralized API
  static async getBillingAutomation(): Promise<any> {
    const response = await api.get('/subscriptions/billing_automation/')
    return response.data.data
  }

  // Payment analytics - using centralized API
  static async getPaymentAnalytics(timeframe: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<any> {
    const response = await api.get('/payments/payment_analytics/', {
      params: { timeframe }
    })
    return response.data.data
  }

  // Invoice analytics - using centralized API
  static async getInvoiceAnalytics(timeframe: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<any> {
    const response = await api.get('/invoices/invoice_analytics/', {
      params: { timeframe }
    })
    return response.data.data
  }

  // Invoices - using centralized API
  static async getInvoices(): Promise<PaginatedResponse<any>> {
    const response = await api.get<PaginatedResponse<any>>('/invoices/')
    return response.data.data
  }

  static async getInvoice(invoiceId: string): Promise<any> {
    const response = await api.get(`/invoices/${invoiceId}/`)
    return response.data.data
  }

  static async sendInvoice(invoiceId: string): Promise<{ message: string }> {
    const response = await api.post(`/invoices/${invoiceId}/send_invoice/`)
    return response.data.data
  }

  static async markInvoicePaid(invoiceId: string): Promise<{ message: string }> {
    const response = await api.post(`/invoices/${invoiceId}/mark_paid/`)
    return response.data.data
  }

  static async getOverdueInvoices(): Promise<any[]> {
    const response = await api.get('/invoices/overdue_invoices/')
    return response.data.data
  }

  static async downloadInvoice(invoiceId: string): Promise<Blob> {
    const response = await api.get(`/invoices/${invoiceId}/download/`, {
      responseType: 'blob'
    })
    return response.data.data
  }

  // Utility methods
  static formatCurrency(amount: number, currency: string = 'USD'): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount / 100) // Assuming amounts are in cents
  }

  static getPaymentStatusColor(status: string): string {
    const colors = {
      pending: 'text-yellow-600 bg-yellow-100',
      completed: 'text-green-600 bg-green-100',
      failed: 'text-red-600 bg-red-100',
      refunded: 'text-gray-600 bg-gray-100'
    }
    return colors[status as keyof typeof colors] || 'text-gray-600 bg-gray-100'
  }

  static getPaymentMethodIcon(method: string): string {
    const icons = {
      stripe: '💳',
      paypal: '🅿️',
      bank_transfer: '🏦',
      crypto: '₿'
    }
    return icons[method as keyof typeof icons] || '💳'
  }
}