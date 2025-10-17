// Payment Types
export interface Payment {
  id: string
  user: string
  user_email: string
  course?: string
  course_title?: string
  subscription?: string
  subscription_plan?: string
  payment_type: 'course' | 'subscription'
  amount: number
  currency: string
  payment_method: 'stripe' | 'paypal' | 'bank_transfer'
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled' | 'refunded'
  stripe_payment_intent_id?: string
  stripe_subscription_id?: string
  paypal_order_id?: string
  bank_transfer_reference?: string
  description: string
  created_at: string
  completed_at?: string
  failed_at?: string
}

export interface Subscription {
  id: string
  organization: string
  organization_name: string
  plan: 'basic' | 'pro' | 'enterprise'
  billing_cycle: 'monthly' | 'yearly'
  status: 'active' | 'cancelled' | 'past_due' | 'unpaid' | 'trialing'
  is_active_status: boolean
  amount: number
  currency: string
  stripe_subscription_id?: string
  stripe_customer_id?: string
  current_period_start: string
  current_period_end: string
  trial_end?: string
  created_at: string
  updated_at: string
  cancelled_at?: string
}

export interface Invoice {
  id: string
  invoice_number: string
  user?: string
  user_email?: string
  organization?: string
  organization_name?: string
  invoice_type: 'payment' | 'subscription'
  payment?: string
  payment_id?: string
  subscription?: string
  subtotal: number
  tax_rate: number
  tax_amount: number
  discount_amount: number
  total_amount: number
  currency: string
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled' | 'void'
  issue_date: string
  due_date: string
  description: string
  notes: string
  billing_name: string
  billing_email: string
  billing_address_line1: string
  billing_address_line2: string
  billing_city: string
  billing_state: string
  billing_postal_code: string
  billing_country: string
  pdf_file?: string
  line_items: InvoiceLineItem[]
  created_at: string
  updated_at: string
  sent_at?: string
  paid_at?: string
}

export interface InvoiceLineItem {
  id: string
  description: string
  quantity: number
  unit_price: number
  total_price: number
  course?: string
  course_title?: string
}

export interface PaymentMethod {
  id: string
  type: 'card' | 'bank_account'
  card?: {
    brand: string
    last4: string
    exp_month: number
    exp_year: number
  }
  bank_account?: {
    bank_name: string
    last4: string
    account_type: string
  }
  is_default: boolean
  created_at: string
}

export interface PaymentIntent {
  id: string
  client_secret: string
  amount: number
  currency: string
  status: string
}

export interface PayPalOrder {
  id: string
  approval_url: string
  amount: number
  currency: string
  status: string
}

export interface PaymentCreateRequest {
  course_id?: string
  amount: number
  payment_method: 'stripe' | 'paypal' | 'bank_transfer'
  currency?: string
}

export interface SubscriptionCreateRequest {
  plan: 'basic' | 'pro' | 'enterprise'
  billing_cycle: 'monthly' | 'yearly'
  payment_method: 'stripe' | 'paypal' | 'bank_transfer'
}

export interface PaymentStats {
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
}

export interface SubscriptionPlan {
  id: string
  name: string
  description: string
  price_monthly: number
  price_yearly: number
  features: string[]
  max_users: number
  max_courses: number
  ai_quota_monthly: number
  storage_gb: number
  support_level: 'basic' | 'priority' | 'dedicated'
  is_popular: boolean
}

export interface BankTransferDetails {
  bank_name: string
  account_name: string
  account_number: string
  routing_number: string
  swift_code?: string
  reference_number: string
  instructions: string
}

export interface PaymentNotification {
  id: string
  type: 'payment_success' | 'payment_failed' | 'subscription_renewed' | 'subscription_cancelled' | 'invoice_sent' | 'payment_overdue'
  title: string
  message: string
  payment_id?: string
  subscription_id?: string
  invoice_id?: string
  created_at: string
  is_read: boolean
}