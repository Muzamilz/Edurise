<template>
  <div class="subscription-management">
    <div class="page-header">
      <h1>Subscription Plan Management</h1>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <i class="fas fa-plus"></i>
        Add Plan
      </button>
    </div>

    <!-- Plans Overview -->
    <div class="plans-grid">
      <div
        v-for="plan in subscriptionPlans"
        :key="plan.id"
        class="plan-card"
        :class="{ 
          popular: plan.is_popular,
          inactive: !plan.is_active
        }"
      >
        <div class="plan-header">
          <div class="plan-name">
            {{ plan.display_name }}
            <span v-if="plan.is_popular" class="popular-badge">Popular</span>
            <span v-if="!plan.is_active" class="inactive-badge">Inactive</span>
          </div>
          <div class="plan-actions">
            <button @click="editPlan(plan)" class="action-btn" title="Edit Plan">
              <i class="fas fa-edit"></i>
            </button>
            <button @click="togglePlanStatus(plan)" class="action-btn" :title="plan.is_active ? 'Deactivate' : 'Activate'">
              <i :class="plan.is_active ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
            <button @click="deletePlan(plan)" class="action-btn delete-btn" title="Delete Plan">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>

        <div class="plan-pricing">
          <div class="price-monthly">
            <span class="currency">$</span>
            <span class="amount">{{ plan.price_monthly }}</span>
            <span class="period">/month</span>
          </div>
          <div class="price-yearly">
            <span class="yearly-label">Yearly:</span>
            <span class="yearly-price">${{ plan.price_yearly }}/year</span>
            <span class="yearly-savings">(Save {{ calculateYearlySavings(plan) }}%)</span>
          </div>
        </div>

        <div class="plan-description">
          {{ plan.description }}
        </div>

        <div class="plan-limits">
          <div class="limit-item">
            <i class="fas fa-users"></i>
            <span>{{ plan.max_users }} Users</span>
          </div>
          <div class="limit-item">
            <i class="fas fa-book"></i>
            <span>{{ plan.max_courses }} Courses</span>
          </div>
          <div class="limit-item">
            <i class="fas fa-hdd"></i>
            <span>{{ plan.max_storage_gb }}GB Storage</span>
          </div>
          <div class="limit-item">
            <i class="fas fa-robot"></i>
            <span>{{ plan.ai_quota_monthly }} AI Requests/month</span>
          </div>
        </div>

        <div class="plan-features">
          <div class="feature-item" :class="{ enabled: plan.has_analytics }">
            <i :class="plan.has_analytics ? 'fas fa-check' : 'fas fa-times'"></i>
            <span>Advanced Analytics</span>
          </div>
          <div class="feature-item" :class="{ enabled: plan.has_api_access }">
            <i :class="plan.has_api_access ? 'fas fa-check' : 'fas fa-times'"></i>
            <span>API Access</span>
          </div>
          <div class="feature-item" :class="{ enabled: plan.has_white_labeling }">
            <i :class="plan.has_white_labeling ? 'fas fa-check' : 'fas fa-times'"></i>
            <span>White Labeling</span>
          </div>
          <div class="feature-item" :class="{ enabled: plan.has_priority_support }">
            <i :class="plan.has_priority_support ? 'fas fa-check' : 'fas fa-times'"></i>
            <span>Priority Support</span>
          </div>
        </div>

        <div class="plan-stats">
          <div class="stat">
            <span class="stat-label">Active Subscriptions:</span>
            <span class="stat-value">{{ getActiveSubscriptions(plan) }}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Monthly Revenue:</span>
            <span class="stat-value">${{ getMonthlyRevenue(plan) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Plan Statistics -->
    <div class="stats-section">
      <h2>Plan Statistics</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-layer-group"></i>
          </div>
          <div class="stat-content">
            <h3>{{ subscriptionPlans.length }}</h3>
            <p>Total Plans</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-eye"></i>
          </div>
          <div class="stat-content">
            <h3>{{ activePlans }}</h3>
            <p>Active Plans</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-star"></i>
          </div>
          <div class="stat-content">
            <h3>{{ popularPlans }}</h3>
            <p>Popular Plans</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-dollar-sign"></i>
          </div>
          <div class="stat-content">
            <h3>${{ totalMonthlyRevenue }}</h3>
            <p>Monthly Revenue</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Plan Modal -->
    <SubscriptionPlanModal
      v-if="showCreateModal || showEditModal"
      :plan="selectedPlan"
      :is-editing="showEditModal"
      @save="savePlan"
      @cancel="closeModals"
    />

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      v-if="showDeleteModal"
      title="Delete Subscription Plan"
      :message="`Are you sure you want to delete '${selectedPlan?.display_name}'? This action cannot be undone and will affect existing subscriptions.`"
      confirm-text="Delete"
      confirm-class="btn-danger"
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { SubscriptionPlan } from '@/types/api'
import SubscriptionPlanModal from '@/components/admin/SubscriptionPlanModal.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import { SubscriptionService } from '@/services/subscriptionService'

// State
const subscriptionPlans = ref<SubscriptionPlan[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const selectedPlan = ref<SubscriptionPlan | null>(null)

// Computed
const activePlans = computed(() => 
  subscriptionPlans.value.filter(plan => plan.is_active).length
)

const popularPlans = computed(() => 
  subscriptionPlans.value.filter(plan => plan.is_popular).length
)

const totalMonthlyRevenue = computed(() => {
  return subscriptionPlans.value.reduce((total, plan) => {
    return total + (getMonthlyRevenue(plan) || 0)
  }, 0).toFixed(2)
})

// Methods
const fetchPlans = async () => {
  loading.value = true
  error.value = null
  
  try {
    subscriptionPlans.value = await SubscriptionService.getPlans()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to fetch plans'
    console.error('Error fetching plans:', err)
  } finally {
    loading.value = false
  }
}

const calculateYearlySavings = (plan: SubscriptionPlan): number => {
  const monthlyTotal = plan.price_monthly * 12
  const yearlySavings = ((monthlyTotal - plan.price_yearly) / monthlyTotal) * 100
  return Math.round(yearlySavings)
}

const getActiveSubscriptions = (plan: SubscriptionPlan): number => {
  // This would come from the API with subscription counts
  return 0 // Placeholder
}

const getMonthlyRevenue = (plan: SubscriptionPlan): number => {
  // This would come from the API with revenue data
  return 0 // Placeholder
}

const editPlan = (plan: SubscriptionPlan) => {
  selectedPlan.value = plan
  showEditModal.value = true
}

const deletePlan = (plan: SubscriptionPlan) => {
  selectedPlan.value = plan
  showDeleteModal.value = true
}

const togglePlanStatus = async (plan: SubscriptionPlan) => {
  try {
    await SubscriptionService.updatePlan(plan.id, {
      is_active: !plan.is_active
    })
    await fetchPlans()
  } catch (error) {
    console.error('Error toggling plan status:', error)
  }
}

const savePlan = async (planData: Partial<SubscriptionPlan>) => {
  try {
    if (showEditModal.value && selectedPlan.value) {
      await SubscriptionService.updatePlan(selectedPlan.value.id, planData)
    } else {
      await SubscriptionService.createPlan(planData)
    }
    await fetchPlans()
    closeModals()
  } catch (error) {
    console.error('Error saving plan:', error)
  }
}

const confirmDelete = async () => {
  if (selectedPlan.value) {
    try {
      await SubscriptionService.deletePlan(selectedPlan.value.id)
      await fetchPlans()
      showDeleteModal.value = false
      selectedPlan.value = null
    } catch (error) {
      console.error('Error deleting plan:', error)
    }
  }
}

const closeModals = () => {
  showCreateModal.value = false
  showEditModal.value = false
  selectedPlan.value = null
}

// Lifecycle
onMounted(() => {
  fetchPlans()
})
</script>

<style scoped>
.subscription-management {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.page-header h1 {
  margin: 0;
  color: #1f2937;
  font-size: 2rem;
  font-weight: 600;
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.plan-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.2s;
  position: relative;
}

.plan-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.plan-card.popular {
  border-color: #3b82f6;
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1);
}

.plan-card.inactive {
  opacity: 0.6;
  background: #f9fafb;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.plan-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.popular-badge {
  padding: 0.125rem 0.5rem;
  background: #3b82f6;
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.inactive-badge {
  padding: 0.125rem 0.5rem;
  background: #6b7280;
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.plan-actions {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.delete-btn:hover {
  background: #fef2f2;
  color: #dc2626;
}

.plan-pricing {
  margin-bottom: 1rem;
}

.price-monthly {
  display: flex;
  align-items: baseline;
  margin-bottom: 0.5rem;
}

.currency {
  font-size: 1.25rem;
  color: #6b7280;
  margin-right: 0.25rem;
}

.amount {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
}

.period {
  font-size: 1rem;
  color: #6b7280;
  margin-left: 0.25rem;
}

.price-yearly {
  font-size: 0.875rem;
  color: #6b7280;
}

.yearly-savings {
  color: #059669;
  font-weight: 500;
}

.plan-description {
  color: #6b7280;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

.plan-limits {
  margin-bottom: 1.5rem;
}

.limit-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #374151;
}

.limit-item i {
  width: 16px;
  color: #6b7280;
}

.plan-features {
  margin-bottom: 1.5rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.feature-item.enabled {
  color: #059669;
}

.feature-item:not(.enabled) {
  color: #6b7280;
}

.feature-item i {
  width: 16px;
}

.plan-stats {
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.stat {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.stat-label {
  color: #6b7280;
}

.stat-value {
  color: #1f2937;
  font-weight: 500;
}

.stats-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.stats-section h2 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3b82f6;
  color: white;
  border-radius: 8px;
  margin-right: 1rem;
  font-size: 1.25rem;
}

.stat-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

.stat-content p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}
</style>