<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>Manage Subscription Plan</h2>
        <button @click="closeModal" class="close-btn">×</button>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading subscription information...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <p>{{ error }}</p>
        <button @click="loadSubscriptionInfo" class="retry-btn">Try Again</button>
      </div>

      <div v-else class="modal-body">
        <!-- Current Plan Info -->
        <div v-if="subscriptionInfo?.has_subscription" class="current-plan-section">
          <h3>Current Plan</h3>
          <div class="current-plan-card">
            <div class="plan-header">
              <h4>{{ subscriptionInfo.current_plan.display_name }}</h4>
              <span class="plan-price">${{ subscriptionInfo.current_plan.price_monthly }}/month</span>
            </div>
            <div class="plan-features">
              <div class="feature-item">
                <span class="feature-label">Users:</span>
                <span class="feature-value">{{ subscriptionInfo.current_plan.max_users }}</span>
              </div>
              <div class="feature-item">
                <span class="feature-label">Courses:</span>
                <span class="feature-value">{{ subscriptionInfo.current_plan.max_courses }}</span>
              </div>
              <div class="feature-item">
                <span class="feature-label">Storage:</span>
                <span class="feature-value">{{ subscriptionInfo.current_plan.max_storage_gb }}GB</span>
              </div>
              <div class="feature-item">
                <span class="feature-label">AI Requests:</span>
                <span class="feature-value">{{ subscriptionInfo.current_plan.ai_quota_monthly }}/month</span>
              </div>
            </div>
            <div class="plan-status">
              <span class="status-badge" :class="subscriptionInfo.status">
                {{ formatStatus(subscriptionInfo.status) }}
              </span>
              <span class="billing-cycle">{{ formatBillingCycle(subscriptionInfo.billing_cycle) }}</span>
            </div>
          </div>
        </div>

        <div v-else class="no-subscription-section">
          <div class="no-subscription-card">
            <h3>No Active Subscription</h3>
            <p>This organization doesn't have an active subscription plan. Select a plan below to get started.</p>
          </div>
        </div>

        <!-- Available Plans -->
        <div class="available-plans-section">
          <h3>{{ subscriptionInfo?.has_subscription ? 'Change to Different Plan' : 'Select a Plan' }}</h3>
          <div class="plans-grid">
            <div 
              v-for="plan in subscriptionInfo?.available_plans || []" 
              :key="plan.id"
              class="plan-card"
              :class="{ 
                'current': subscriptionInfo?.current_plan?.id === plan.id,
                'selected': selectedPlanId === plan.id,
                'popular': plan.is_popular
              }"
              @click="selectPlan(plan)"
            >
              <div v-if="plan.is_popular" class="popular-badge">Most Popular</div>
              <div v-if="subscriptionInfo?.current_plan?.id === plan.id" class="current-badge">Current Plan</div>
              
              <div class="plan-header">
                <h4>{{ plan.display_name }}</h4>
                <div class="plan-pricing">
                  <span class="price-monthly">${{ plan.price_monthly }}/month</span>
                  <span class="price-yearly">${{ plan.price_yearly }}/year</span>
                </div>
              </div>

              <p class="plan-description">{{ plan.description }}</p>

              <div class="plan-features">
                <div class="feature-grid">
                  <div class="feature-item">
                    <span class="feature-icon">👥</span>
                    <span class="feature-text">{{ plan.max_users }} Users</span>
                  </div>
                  <div class="feature-item">
                    <span class="feature-icon">📚</span>
                    <span class="feature-text">{{ plan.max_courses }} Courses</span>
                  </div>
                  <div class="feature-item">
                    <span class="feature-icon">💾</span>
                    <span class="feature-text">{{ plan.max_storage_gb }}GB Storage</span>
                  </div>
                  <div class="feature-item">
                    <span class="feature-icon">🤖</span>
                    <span class="feature-text">{{ plan.ai_quota_monthly }} AI Requests</span>
                  </div>
                </div>

                <div class="premium-features">
                  <div v-if="plan.has_analytics" class="premium-feature">
                    <span class="feature-icon">📊</span>
                    <span>Advanced Analytics</span>
                  </div>
                  <div v-if="plan.has_api_access" class="premium-feature">
                    <span class="feature-icon">🔌</span>
                    <span>API Access</span>
                  </div>
                  <div v-if="plan.has_white_labeling" class="premium-feature">
                    <span class="feature-icon">🎨</span>
                    <span>White Labeling</span>
                  </div>
                  <div v-if="plan.has_priority_support" class="premium-feature">
                    <span class="feature-icon">🚀</span>
                    <span>Priority Support</span>
                  </div>
                  <div v-if="plan.has_custom_integrations" class="premium-feature">
                    <span class="feature-icon">🔗</span>
                    <span>Custom Integrations</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="closeModal" class="btn-secondary">Cancel</button>
        <button 
          @click="changePlan" 
          :disabled="!selectedPlanId || selectedPlanId === subscriptionInfo?.current_plan?.id || changingPlan"
          class="btn-primary"
        >
          {{ changingPlan ? 'Changing Plan...' : 'Change Plan' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { OrganizationService } from '@/services/organizationService'
import { useErrorHandler } from '@/composables/useErrorHandler'

interface Props {
  isOpen: boolean
  organizationId: string | null
  organizationName: string
}

interface Emits {
  (e: 'close'): void
  (e: 'planChanged', data: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { handleApiError } = useErrorHandler()

const subscriptionInfo = ref<any>(null)
const selectedPlanId = ref<string | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const changingPlan = ref(false)

const loadSubscriptionInfo = async () => {
  if (!props.organizationId) return

  try {
    loading.value = true
    error.value = null
    
    const info = await OrganizationService.getOrganizationSubscription(props.organizationId)
    subscriptionInfo.value = info
    
    // Pre-select current plan if exists
    if (info.has_subscription && info.current_plan) {
      selectedPlanId.value = info.current_plan.id
    }
  } catch (err: any) {
    error.value = err.response?.data?.message || 'Failed to load subscription information'
    handleApiError(err)
  } finally {
    loading.value = false
  }
}

const selectPlan = (plan: any) => {
  selectedPlanId.value = plan.id
}

const changePlan = async () => {
  if (!props.organizationId || !selectedPlanId.value) return

  try {
    changingPlan.value = true
    
    const result = await OrganizationService.changeOrganizationSubscriptionPlan(
      props.organizationId,
      selectedPlanId.value
    )
    
    emit('planChanged', result)
    closeModal()
  } catch (err: any) {
    error.value = err.response?.data?.message || 'Failed to change subscription plan'
    handleApiError(err)
  } finally {
    changingPlan.value = false
  }
}

const closeModal = () => {
  emit('close')
  // Reset state
  subscriptionInfo.value = null
  selectedPlanId.value = null
  error.value = null
}

const formatStatus = (status: string) => {
  return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')
}

const formatBillingCycle = (cycle: string) => {
  return cycle === 'yearly' ? 'Billed Yearly' : 'Billed Monthly'
}

// Watch for modal open to load data
watch(() => props.isOpen, (isOpen) => {
  if (isOpen && props.organizationId) {
    loadSubscriptionInfo()
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 1200px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 2rem;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #7c3aed;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.current-plan-section, .no-subscription-section, .available-plans-section {
  margin-bottom: 2rem;
}

.current-plan-section h3, .available-plans-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.current-plan-card, .no-subscription-card {
  background: linear-gradient(135deg, #f3e8ff, #e9d5ff);
  border: 1px solid #7c3aed;
  border-radius: 8px;
  padding: 1.5rem;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.plan-header h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #5b21b6;
  margin: 0;
}

.plan-price {
  font-size: 1.25rem;
  font-weight: 700;
  color: #7c3aed;
}

.plan-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.feature-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.feature-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.feature-value {
  font-weight: 600;
  color: #1f2937;
}

.plan-status {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.active {
  background: #dcfce7;
  color: #166534;
}

.status-badge.cancelled {
  background: #fef2f2;
  color: #dc2626;
}

.billing-cycle {
  font-size: 0.875rem;
  color: #6b7280;
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.plan-card {
  position: relative;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.plan-card:hover {
  border-color: #7c3aed;
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.15);
  transform: translateY(-2px);
}

.plan-card.selected {
  border-color: #7c3aed;
  background: linear-gradient(135deg, #faf5ff, #f3e8ff);
}

.plan-card.current {
  border-color: #10b981;
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
}

.plan-card.popular {
  border-color: #f59e0b;
}

.popular-badge, .current-badge {
  position: absolute;
  top: -8px;
  right: 1rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.popular-badge {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.current-badge {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.plan-card .plan-header h4 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.plan-pricing {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.price-monthly {
  font-size: 1.5rem;
  font-weight: 700;
  color: #7c3aed;
}

.price-yearly {
  font-size: 0.875rem;
  color: #6b7280;
}

.plan-description {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.plan-card .feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.feature-icon {
  font-size: 1rem;
}

.feature-text {
  font-size: 0.875rem;
  color: #374151;
}

.premium-features {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.premium-feature {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #059669;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
}

.btn-secondary, .btn-primary {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.retry-btn {
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
}
</style>