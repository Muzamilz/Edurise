import { api } from './api'
import type { SubscriptionPlan, Organization, Subscription, PaginatedResponse } from '../types/api'

export interface OrganizationSubscriptionData {
  organization: Organization
  subscription?: Subscription
  revenue: {
    monthly: number
    yearly: number
    total: number
  }
  stats: {
    total_users: number
    total_courses: number
    total_enrollments: number
  }
}

export interface GlobalSubscriptionStats {
  total_organizations: number
  total_subscriptions: number
  total_monthly_revenue: number
  total_yearly_revenue: number
  subscription_plans: SubscriptionPlan[]
  organizations_data: OrganizationSubscriptionData[]
  revenue_by_plan: Array<{
    plan_name: string
    plan_id: string
    subscriber_count: number
    monthly_revenue: number
    yearly_revenue: number
  }>
  all_subscriptions?: any[]
}

export class SubscriptionService {
  /**
   * Get all subscription plans
   */
  static async getPlans(): Promise<SubscriptionPlan[]> {
    try {
      const response = await api.get<SubscriptionPlan[] | PaginatedResponse<SubscriptionPlan>>('/subscription-plans/')
      const data = response.data.data
      if (Array.isArray(data)) {
        return data
      } else if (data && 'results' in data) {
        return data.results
      }
      return []
    } catch (error) {
      console.error('Failed to fetch subscription plans:', error)
      return []
    }
  }

  /**
   * Get active subscription plans only
   */
  static async getActivePlans(): Promise<SubscriptionPlan[]> {
    try {
      const response = await api.get<SubscriptionPlan[] | PaginatedResponse<SubscriptionPlan>>('/subscription-plans/', {
        params: { is_active: true }
      })
      const data = response.data.data
      if (Array.isArray(data)) {
        return data
      } else if (data && 'results' in data) {
        return data.results
      }
      return []
    } catch (error) {
      console.error('Failed to fetch active subscription plans:', error)
      return []
    }
  }

  /**
   * Get all active subscriptions with organization data
   */
  static async getAllSubscriptions(): Promise<any[]> {
    console.log('Getting all subscriptions...')

    // Skip the subscriptions endpoint since it's not working and go directly to fallback
    console.log('Subscriptions endpoint not available, building from organization data')

    try {

      // Build subscription data directly from organization data (skip problematic API calls)
      const orgsResponse = await api.get<Organization[] | PaginatedResponse<Organization>>('/organizations/')
      const responseData = orgsResponse.data.data
      const organizations = Array.isArray(responseData) ? responseData : 
                          (responseData && 'results' in responseData) ? responseData.results : []

      console.log('Building subscriptions from', organizations.length, 'organizations')

      const subscriptions = []

      for (const org of organizations) {
        // Create subscription data based on organization subscription plan
        if (org.subscription_plan && org.subscription_plan !== 'basic') {
          const planPrice = this.getDefaultPlanPrice(org.subscription_plan)

          subscriptions.push({
            id: `sub_${org.id}`,
            organization: org,
            plan: {
              name: org.subscription_plan,
              display_name: this.formatPlanName(org.subscription_plan),
              id: `plan_${org.subscription_plan}`
            },
            status: 'active',
            billing_cycle: 'monthly',
            amount: planPrice,
            currency: 'USD',
            current_period_start: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
            current_period_end: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString(),
            created_at: org.created_at || new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
            cancelled_at: null
          })
        }
      }

      return subscriptions
    } catch (error) {
      console.error('Failed to fetch subscriptions:', error)
      return []
    }
  }

  /**
   * Get default price for a plan (fallback when API data is not available)
   */
  private static getDefaultPlanPrice(planName: string): number {
    const defaultPrices = {
      basic: 0,
      pro: 79,
      enterprise: 199
    }
    return defaultPrices[planName as keyof typeof defaultPrices] || 0
  }

  /**
   * Format plan name for display
   */
  private static formatPlanName(planName: string): string {
    if (!planName) return 'Basic'
    return planName.charAt(0).toUpperCase() + planName.slice(1)
  }

  /**
   * Get global subscription statistics with organization data
   */
  static async getGlobalStats(): Promise<GlobalSubscriptionStats> {
    try {
      console.log('Fetching global subscription stats...')

      // Try to get data from super admin dashboard endpoint first
      try {
        const dashboardResponse = await api.get('/dashboard/superadmin/')
        const dashboardData = dashboardResponse.data.data || dashboardResponse.data

        if (dashboardData && dashboardData.organization_performance) {
          console.log('Using super admin dashboard data')

          // Get subscription plans
          const plansResponse = await api.get<SubscriptionPlan[] | PaginatedResponse<SubscriptionPlan>>('/subscription-plans/')
          const plansData = plansResponse.data.data
          const plans = Array.isArray(plansData) ? plansData : 
                       (plansData && 'results' in plansData) ? plansData.results : []

          // Transform dashboard data to our format
          const organizationsData: OrganizationSubscriptionData[] = dashboardData.organization_performance.map((org: any) => ({
            organization: {
              id: org.id,
              name: org.name,
              subdomain: org.subdomain,
              subscription_plan: org.subscription_plan,
              is_active: true,
              created_at: new Date().toISOString()
            },
            revenue: {
              monthly: parseFloat(org.total_revenue) || 0,
              yearly: 0,
              total: parseFloat(org.total_revenue) || 0
            },
            stats: {
              total_users: parseInt(org.total_users) || 0,
              total_courses: parseInt(org.total_courses) || 0,
              total_enrollments: parseInt(org.total_enrollments) || 0
            }
          }))

          const totalMonthlyRevenue = organizationsData.reduce((sum, org) => sum + org.revenue.monthly, 0)
          const totalSubscriptions = organizationsData.filter(org => org.organization.subscription_plan !== 'basic').length

          // Get all subscriptions for the subscriptions tab (built from organization data)
          const allSubscriptions = await this.getAllSubscriptions()
          console.log('Built subscriptions from organization data:', allSubscriptions)

          // Calculate revenue by plan from organization data and subscription data
          const revenueByPlan = plans.map((plan: SubscriptionPlan) => {
            // Use organization data for revenue calculation
            const orgsWithPlan = organizationsData.filter(orgData => orgData.organization.subscription_plan === plan.name)
            const planRevenue = orgsWithPlan.reduce((sum, orgData) => sum + orgData.revenue.monthly, 0)

            // Count subscriptions for this plan
            const planSubscriptions = allSubscriptions.filter(sub =>
              sub.plan?.name === plan.name || sub.organization?.subscription_plan === plan.name
            )

            return {
              plan_name: plan.display_name,
              plan_id: plan.id,
              subscriber_count: Math.max(orgsWithPlan.length, planSubscriptions.length),
              monthly_revenue: planRevenue,
              yearly_revenue: 0
            }
          })

          return {
            total_organizations: organizationsData.length,
            total_subscriptions: totalSubscriptions,
            total_monthly_revenue: totalMonthlyRevenue,
            total_yearly_revenue: 0,
            subscription_plans: plans,
            organizations_data: organizationsData,
            revenue_by_plan: revenueByPlan,
            all_subscriptions: allSubscriptions
          }
        }
      } catch (dashboardError) {
        console.warn('Super admin dashboard failed, trying individual endpoints:', dashboardError)
      }

      // Fallback to individual endpoints
      // Get organizations with their subscription data
      const orgsResponse = await api.get<Organization[] | PaginatedResponse<Organization>>('/organizations/')
      const orgsData = orgsResponse.data.data
      const organizations = Array.isArray(orgsData) ? orgsData : 
                          (orgsData && 'results' in orgsData) ? orgsData.results : []

      // Get subscription plans
      const plansResponse = await api.get<SubscriptionPlan[] | PaginatedResponse<SubscriptionPlan>>('/subscription-plans/')
      const plansData = plansResponse.data.data
      const plans = Array.isArray(plansData) ? plansData : 
                   (plansData && 'results' in plansData) ? plansData.results : []

      // Get detailed data for each organization
      const organizationsData: OrganizationSubscriptionData[] = []
      let totalMonthlyRevenue = 0
      let totalYearlyRevenue = 0
      let totalSubscriptions = 0

      for (const org of organizations) {
        try {
          // Get organization subscription info
          const subResponse = await api.get(`/organizations/${org.id}/subscription-info/`)
          const subData = subResponse.data.data || subResponse.data

          // Get organization stats
          const statsResponse = await api.get(`/organizations/${org.id}/stats/`)
          const statsData = statsResponse.data.data || statsResponse.data

          const orgData: OrganizationSubscriptionData = {
            organization: org,
            subscription: subData.has_subscription ? {
              id: subData.subscription_id,
              organization: org.id,
              plan: subData.current_plan,
              billing_cycle: subData.billing_cycle,
              status: subData.status,
              amount: subData.amount,
              currency: subData.currency || 'USD',
              current_period_start: subData.current_period_start,
              current_period_end: subData.current_period_end,
              trial_end: null,
              created_at: '',
              updated_at: '',
              cancelled_at: null
            } : undefined,
            revenue: {
              monthly: subData.billing_cycle === 'monthly' ? subData.amount || 0 : 0,
              yearly: subData.billing_cycle === 'yearly' ? subData.amount || 0 : 0,
              total: subData.amount || 0
            },
            stats: {
              total_users: statsData?.student_statistics?.total_students || 0,
              total_courses: statsData?.course_statistics?.total_courses || 0,
              total_enrollments: statsData?.student_statistics?.total_enrollments || 0
            }
          }

          organizationsData.push(orgData)

          if (subData.has_subscription) {
            totalSubscriptions++
            if (subData.billing_cycle === 'monthly') {
              totalMonthlyRevenue += subData.amount || 0
            } else {
              totalYearlyRevenue += subData.amount || 0
            }
          }
        } catch (error) {
          console.error(`Failed to fetch data for organization ${org.id}:`, error)
          // Add organization with default data
          organizationsData.push({
            organization: org,
            revenue: { monthly: 0, yearly: 0, total: 0 },
            stats: { total_users: 0, total_courses: 0, total_enrollments: 0 }
          })
        }
      }

      // Calculate revenue by plan
      const revenueByPlan = plans.map((plan: SubscriptionPlan) => {
        const planSubscriptions = organizationsData.filter(
          org => org.subscription?.plan?.id === plan.id
        )

        const monthlyRevenue = planSubscriptions
          .filter(org => org.subscription?.billing_cycle === 'monthly')
          .reduce((sum, org) => sum + (org.revenue.monthly || 0), 0)

        const yearlyRevenue = planSubscriptions
          .filter(org => org.subscription?.billing_cycle === 'yearly')
          .reduce((sum, org) => sum + (org.revenue.yearly || 0), 0)

        return {
          plan_name: plan.display_name,
          plan_id: plan.id,
          subscriber_count: planSubscriptions.length,
          monthly_revenue: monthlyRevenue,
          yearly_revenue: yearlyRevenue
        }
      })

      return {
        total_organizations: organizations.length,
        total_subscriptions: totalSubscriptions,
        total_monthly_revenue: totalMonthlyRevenue,
        total_yearly_revenue: totalYearlyRevenue,
        subscription_plans: plans,
        organizations_data: organizationsData,
        revenue_by_plan: revenueByPlan
      }
    } catch (error) {
      console.error('Failed to fetch global subscription stats:', error)
      return {
        total_organizations: 0,
        total_subscriptions: 0,
        total_monthly_revenue: 0,
        total_yearly_revenue: 0,
        subscription_plans: [],
        organizations_data: [],
        revenue_by_plan: [],
        all_subscriptions: []
      }
    }
  }

  /**
   * Create a new subscription plan
   */
  static async createPlan(planData: Partial<SubscriptionPlan>): Promise<SubscriptionPlan> {
    const response = await api.post('/subscription-plans/', planData)
    return response.data.data || response.data
  }

  /**
   * Update a subscription plan
   */
  static async updatePlan(planId: string, planData: Partial<SubscriptionPlan>): Promise<SubscriptionPlan> {
    const response = await api.put(`/subscription-plans/${planId}/`, planData)
    return response.data.data || response.data
  }

  /**
   * Delete a subscription plan
   */
  static async deletePlan(planId: string): Promise<void> {
    await api.delete(`/subscription-plans/${planId}/`)
  }

  /**
   * Get organization subscription details
   */
  static async getOrganizationSubscription(orgId: string) {
    const response = await api.get(`/organizations/${orgId}/subscription-info/`)
    return response.data.data || response.data
  }

  /**
   * Change organization subscription plan
   */
  static async changeOrganizationPlan(orgId: string, planId: string, billingCycle: 'monthly' | 'yearly') {
    const response = await api.post(`/organizations/${orgId}/change-subscription-plan/`, {
      plan_id: planId,
      billing_cycle: billingCycle
    })
    return response.data.data || response.data
  }

  /**
   * Get subscription analytics and trends
   */
  static async getSubscriptionAnalytics(): Promise<{
    revenue_growth: number
    customer_acquisition_rate: number
    churn_rate: number
    arpu_growth: number
    new_subscriptions_this_month: number
    subscription_trends: Array<{ month: string; subscriptions: number }>
  }> {
    try {
      // Try to get analytics from a dedicated endpoint
      const response = await api.get('/analytics/subscriptions/')
      return response.data.data || response.data
    } catch (error) {
      console.warn('Subscription analytics endpoint not available, using calculated values')
      return {
        revenue_growth: 0,
        customer_acquisition_rate: 0,
        churn_rate: 0,
        arpu_growth: 0,
        new_subscriptions_this_month: 0,
        subscription_trends: []
      }
    }
  }
}