import { api } from './api'
import type { Payment, PaginatedResponse } from '../types/api'

export class PaymentService {
  // Payment operations
  static async getPayments(): Promise<PaginatedResponse<Payment>> {
    const response = await api.get<PaginatedResponse<Payment>>('/payments/payments/')
    return response.data
  }

  static async getPayment(id: string): Promise<Payment> {
    const response = await api.get<Payment>(`/payments/payments/${id}/`)
    return response.data
  }

  // Course purchase
  static async purchaseCourse(courseId: string, paymentMethod: 'stripe' | 'paypal'): Promise<{
    payment_id: string
    client_secret?: string // For Stripe
    approval_url?: string // For PayPal
  }> {
    const response = await api.post('/payments/payments/purchase_course/', {
      course_id: courseId,
      payment_method: paymentMethod
    })
    return response.data
  }

  // Stripe integration
  static async createStripePaymentIntent(amount: number, currency: string = 'usd'): Promise<{
    client_secret: string
    payment_intent_id: string
  }> {
    const response = await api.post('/payments/payments/create_stripe_intent/', {
      amount,
      currency
    })
    return response.data
  }

  static async confirmStripePayment(paymentIntentId: string): Promise<Payment> {
    const response = await api.post<Payment>('/payments/payments/confirm_stripe_payment/', {
      payment_intent_id: paymentIntentId
    })
    return response.data
  }

  // PayPal integration
  static async createPayPalOrder(amount: number, currency: string = 'USD'): Promise<{
    order_id: string
    approval_url: string
  }> {
    const response = await api.post('/payments/payments/create_paypal_order/', {
      amount,
      currency
    })
    return response.data
  }

  static async capturePayPalOrder(orderId: string): Promise<Payment> {
    const response = await api.post<Payment>('/payments/payments/capture_paypal_order/', {
      order_id: orderId
    })
    return response.data
  }

  // Refunds
  static async requestRefund(paymentId: string, reason?: string): Promise<Payment> {
    const response = await api.post<Payment>(`/payments/payments/${paymentId}/refund/`, {
      reason
    })
    return response.data
  }

  // Payment history
  static async getUserPaymentHistory(): Promise<PaginatedResponse<Payment>> {
    const response = await api.get<PaginatedResponse<Payment>>('/payments/payments/my_payments/')
    return response.data
  }

  // Revenue analytics (for admins/teachers)
  static async getRevenueStats(timeframe: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<{
    total_revenue: number
    total_transactions: number
    successful_payments: number
    failed_payments: number
    refunded_amount: number
    revenue_by_period: Array<{
      period: string
      revenue: number
      transactions: number
    }>
  }> {
    const response = await api.get('/payments/payments/revenue_stats/', {
      params: { timeframe }
    })
    return response.data
  }

  // Subscription management (if applicable)
  static async getSubscriptions(): Promise<PaginatedResponse<any>> {
    const response = await api.get<PaginatedResponse<any>>('/payments/subscriptions/')
    return response.data
  }

  static async createSubscription(planId: string): Promise<any> {
    const response = await api.post('/payments/subscriptions/', {
      plan_id: planId
    })
    return response.data
  }

  static async cancelSubscription(subscriptionId: string): Promise<any> {
    const response = await api.post(`/payments/subscriptions/${subscriptionId}/cancel/`)
    return response.data
  }

  // Payment methods management
  static async getPaymentMethods(): Promise<any[]> {
    const response = await api.get('/payments/payment_methods/')
    return response.data
  }

  static async addPaymentMethod(paymentMethodData: any): Promise<any> {
    const response = await api.post('/payments/payment_methods/', paymentMethodData)
    return response.data
  }

  static async removePaymentMethod(paymentMethodId: string): Promise<void> {
    await api.delete(`/payments/payment_methods/${paymentMethodId}/`)
  }

  // Invoices
  static async getInvoices(): Promise<PaginatedResponse<any>> {
    const response = await api.get<PaginatedResponse<any>>('/payments/invoices/')
    return response.data
  }

  static async downloadInvoice(invoiceId: string): Promise<Blob> {
    const response = await api.get(`/payments/invoices/${invoiceId}/download/`, {
      responseType: 'blob'
    })
    return response.data
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