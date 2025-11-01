<template>
  <div class="modal-overlay" @click="$emit('cancel')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ isEditing ? 'Edit Subscription Plan' : 'Create Subscription Plan' }}</h2>
        <button @click="$emit('cancel')" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <div class="form-tabs">
          <button
            type="button"
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            class="tab-btn"
            :class="{ active: activeTab === tab.id }"
          >
            <i :class="tab.icon"></i>
            {{ tab.label }}
          </button>
        </div>

        <!-- Basic Information Tab -->
        <div v-show="activeTab === 'basic'" class="tab-content">
          <div class="form-grid">
            <div class="form-group">
              <label for="name" class="form-label">Plan Name *</label>
              <select
                id="name"
                v-model="formData.name"
                class="form-select"
                :class="{ error: errors.name }"
                required
              >
                <option value="">Select plan type</option>
                <option value="basic">Basic</option>
                <option value="pro">Pro</option>
                <option value="enterprise">Enterprise</option>
              </select>
              <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
            </div>

            <div class="form-group">
              <label for="display_name" class="form-label">Display Name *</label>
              <input
                id="display_name"
                v-model="formData.display_name"
                type="text"
                class="form-input"
                :class="{ error: errors.display_name }"
                placeholder="e.g., Professional Plan"
                required
              />
              <span v-if="errors.display_name" class="error-message">{{ errors.display_name }}</span>
            </div>
          </div>

          <div class="form-group">
            <label for="description" class="form-label">Description *</label>
            <textarea
              id="description"
              v-model="formData.description"
              class="form-textarea"
              rows="3"
              placeholder="Describe what this plan offers"
              required
            ></textarea>
            <span v-if="errors.description" class="error-message">{{ errors.description }}</span>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label for="sort_order" class="form-label">Sort Order</label>
              <input
                id="sort_order"
                v-model.number="formData.sort_order"
                type="number"
                class="form-input"
                min="0"
                placeholder="0"
              />
              <small class="form-help">Lower numbers appear first</small>
            </div>

            <div class="form-group">
              <div class="checkbox-group">
                <label class="checkbox-label">
                  <input
                    v-model="formData.is_popular"
                    type="checkbox"
                    class="checkbox"
                  />
                  <span class="checkbox-text">Mark as Popular</span>
                </label>
                <label class="checkbox-label">
                  <input
                    v-model="formData.is_active"
                    type="checkbox"
                    class="checkbox"
                  />
                  <span class="checkbox-text">Active</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Pricing Tab -->
        <div v-show="activeTab === 'pricing'" class="tab-content">
          <div class="form-grid">
            <div class="form-group">
              <label for="price_monthly" class="form-label">Monthly Price *</label>
              <div class="price-input-group">
                <span class="currency-symbol">$</span>
                <input
                  id="price_monthly"
                  v-model.number="formData.price_monthly"
                  type="number"
                  step="0.01"
                  min="0"
                  class="form-input"
                  :class="{ error: errors.price_monthly }"
                  placeholder="29.99"
                  required
                />
              </div>
              <span v-if="errors.price_monthly" class="error-message">{{ errors.price_monthly }}</span>
            </div>

            <div class="form-group">
              <label for="price_yearly" class="form-label">Yearly Price *</label>
              <div class="price-input-group">
                <span class="currency-symbol">$</span>
                <input
                  id="price_yearly"
                  v-model.number="formData.price_yearly"
                  type="number"
                  step="0.01"
                  min="0"
                  class="form-input"
                  :class="{ error: errors.price_yearly }"
                  placeholder="299.99"
                  required
                />
              </div>
              <span v-if="errors.price_yearly" class="error-message">{{ errors.price_yearly }}</span>
            </div>
          </div>

          <div class="savings-display" v-if="formData.price_monthly && formData.price_yearly">
            <div class="savings-info">
              <i class="fas fa-info-circle"></i>
              <span>
                Yearly plan saves {{ yearlySavingsPercentage }}% 
                ({{ yearlySavingsAmount }} per year)
              </span>
            </div>
          </div>
        </div>

        <!-- Limits Tab -->
        <div v-show="activeTab === 'limits'" class="tab-content">
          <div class="form-grid">
            <div class="form-group">
              <label for="max_users" class="form-label">Max Users *</label>
              <input
                id="max_users"
                v-model.number="formData.max_users"
                type="number"
                min="1"
                class="form-input"
                :class="{ error: errors.max_users }"
                placeholder="10"
                required
              />
              <span v-if="errors.max_users" class="error-message">{{ errors.max_users }}</span>
            </div>

            <div class="form-group">
              <label for="max_courses" class="form-label">Max Courses *</label>
              <input
                id="max_courses"
                v-model.number="formData.max_courses"
                type="number"
                min="1"
                class="form-input"
                :class="{ error: errors.max_courses }"
                placeholder="5"
                required
              />
              <span v-if="errors.max_courses" class="error-message">{{ errors.max_courses }}</span>
            </div>

            <div class="form-group">
              <label for="max_storage_gb" class="form-label">Max Storage (GB) *</label>
              <input
                id="max_storage_gb"
                v-model.number="formData.max_storage_gb"
                type="number"
                min="1"
                class="form-input"
                :class="{ error: errors.max_storage_gb }"
                placeholder="10"
                required
              />
              <span v-if="errors.max_storage_gb" class="error-message">{{ errors.max_storage_gb }}</span>
            </div>

            <div class="form-group">
              <label for="ai_quota_monthly" class="form-label">AI Quota (Monthly) *</label>
              <input
                id="ai_quota_monthly"
                v-model.number="formData.ai_quota_monthly"
                type="number"
                min="0"
                class="form-input"
                :class="{ error: errors.ai_quota_monthly }"
                placeholder="100"
                required
              />
              <span v-if="errors.ai_quota_monthly" class="error-message">{{ errors.ai_quota_monthly }}</span>
            </div>

            <div class="form-group">
              <label for="max_file_size_mb" class="form-label">Max File Size (MB)</label>
              <input
                id="max_file_size_mb"
                v-model.number="formData.max_file_size_mb"
                type="number"
                min="1"
                class="form-input"
                placeholder="10"
              />
            </div>

            <div class="form-group">
              <label for="monthly_download_limit" class="form-label">Monthly Download Limit</label>
              <input
                id="monthly_download_limit"
                v-model.number="formData.monthly_download_limit"
                type="number"
                min="0"
                class="form-input"
                placeholder="Leave empty for unlimited"
              />
              <small class="form-help">Leave empty for unlimited downloads</small>
            </div>
          </div>
        </div>

        <!-- Features Tab -->
        <div v-show="activeTab === 'features'" class="tab-content">
          <div class="features-grid">
            <div class="feature-group">
              <h3>Core Features</h3>
              <label class="feature-checkbox">
                <input
                  v-model="formData.has_analytics"
                  type="checkbox"
                  class="checkbox"
                />
                <div class="feature-info">
                  <span class="feature-name">Advanced Analytics</span>
                  <span class="feature-description">Detailed reports and insights</span>
                </div>
              </label>

              <label class="feature-checkbox">
                <input
                  v-model="formData.has_api_access"
                  type="checkbox"
                  class="checkbox"
                />
                <div class="feature-info">
                  <span class="feature-name">API Access</span>
                  <span class="feature-description">Programmatic access to platform</span>
                </div>
              </label>

              <label class="feature-checkbox">
                <input
                  v-model="formData.has_priority_support"
                  type="checkbox"
                  class="checkbox"
                />
                <div class="feature-info">
                  <span class="feature-name">Priority Support</span>
                  <span class="feature-description">Faster response times</span>
                </div>
              </label>
            </div>

            <div class="feature-group">
              <h3>Advanced Features</h3>
              <label class="feature-checkbox">
                <input
                  v-model="formData.has_white_labeling"
                  type="checkbox"
                  class="checkbox"
                />
                <div class="feature-info">
                  <span class="feature-name">White Labeling</span>
                  <span class="feature-description">Custom branding options</span>
                </div>
              </label>

              <label class="feature-checkbox">
                <input
                  v-model="formData.has_custom_integrations"
                  type="checkbox"
                  class="checkbox"
                />
                <div class="feature-info">
                  <span class="feature-name">Custom Integrations</span>
                  <span class="feature-description">Third-party integrations</span>
                </div>
              </label>

              <label class="feature-checkbox">
                <input
                  v-model="formData.recording_access"
                  type="checkbox"
                  class="checkbox"
                />
                <div class="feature-info">
                  <span class="feature-name">Recording Access</span>
                  <span class="feature-description">Access to class recordings</span>
                </div>
              </label>

              <label class="feature-checkbox">
                <input
                  v-model="formData.premium_content_access"
                  type="checkbox"
                  class="checkbox"
                />
                <div class="feature-info">
                  <span class="feature-name">Premium Content</span>
                  <span class="feature-description">Access to premium materials</span>
                </div>
              </label>
            </div>
          </div>
        </div>

        <!-- Preview Tab -->
        <div v-show="activeTab === 'preview'" class="tab-content">
          <div class="plan-preview">
            <div class="preview-card" :class="{ popular: formData.is_popular }">
              <div class="preview-header">
                <h3>{{ formData.display_name || 'Plan Name' }}</h3>
                <span v-if="formData.is_popular" class="popular-badge">Popular</span>
              </div>
              
              <div class="preview-pricing">
                <div class="price-display">
                  <span class="currency">$</span>
                  <span class="amount">{{ formData.price_monthly || 0 }}</span>
                  <span class="period">/month</span>
                </div>
                <div class="yearly-price">
                  ${{ formData.price_yearly || 0 }}/year
                  <span v-if="yearlySavingsPercentage > 0" class="savings">
                    (Save {{ yearlySavingsPercentage }}%)
                  </span>
                </div>
              </div>

              <div class="preview-description">
                {{ formData.description || 'Plan description will appear here' }}
              </div>

              <div class="preview-limits">
                <div class="limit-item">
                  <i class="fas fa-users"></i>
                  <span>{{ formData.max_users || 0 }} Users</span>
                </div>
                <div class="limit-item">
                  <i class="fas fa-book"></i>
                  <span>{{ formData.max_courses || 0 }} Courses</span>
                </div>
                <div class="limit-item">
                  <i class="fas fa-hdd"></i>
                  <span>{{ formData.max_storage_gb || 0 }}GB Storage</span>
                </div>
                <div class="limit-item">
                  <i class="fas fa-robot"></i>
                  <span>{{ formData.ai_quota_monthly || 0 }} AI Requests</span>
                </div>
              </div>

              <div class="preview-features">
                <div class="feature-item" :class="{ enabled: formData.has_analytics }">
                  <i :class="formData.has_analytics ? 'fas fa-check' : 'fas fa-times'"></i>
                  <span>Advanced Analytics</span>
                </div>
                <div class="feature-item" :class="{ enabled: formData.has_api_access }">
                  <i :class="formData.has_api_access ? 'fas fa-check' : 'fas fa-times'"></i>
                  <span>API Access</span>
                </div>
                <div class="feature-item" :class="{ enabled: formData.has_white_labeling }">
                  <i :class="formData.has_white_labeling ? 'fas fa-check' : 'fas fa-times'"></i>
                  <span>White Labeling</span>
                </div>
                <div class="feature-item" :class="{ enabled: formData.has_priority_support }">
                  <i :class="formData.has_priority_support ? 'fas fa-check' : 'fas fa-times'"></i>
                  <span>Priority Support</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </form>

      <div class="modal-footer">
        <button
          type="button"
          @click="$emit('cancel')"
          class="btn btn-outline"
          :disabled="loading"
        >
          Cancel
        </button>
        <button
          type="submit"
          @click="handleSubmit"
          class="btn btn-primary"
          :disabled="loading || !isFormValid"
        >
          {{ loading ? 'Saving...' : (isEditing ? 'Update Plan' : 'Create Plan') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { SubscriptionPlan } from '@/types/api'

interface Props {
  plan?: SubscriptionPlan | null
  isEditing: boolean
}

interface Emits {
  (e: 'save', planData: Partial<SubscriptionPlan>): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  plan: null,
  isEditing: false
})

const emit = defineEmits<Emits>()

// Form data
const formData = ref({
  name: 'basic' as 'basic' | 'pro' | 'enterprise',
  display_name: '',
  description: '',
  price_monthly: 0,
  price_yearly: 0,
  max_users: 10,
  max_courses: 5,
  max_storage_gb: 10,
  ai_quota_monthly: 100,
  max_file_size_mb: 10,
  monthly_download_limit: null as number | null,
  has_analytics: false,
  has_api_access: false,
  has_white_labeling: false,
  has_priority_support: false,
  has_custom_integrations: false,
  recording_access: false,
  premium_content_access: false,
  is_popular: false,
  is_active: true,
  sort_order: 0
})

// Form state
const activeTab = ref('basic')
const loading = ref(false)
const errors = ref<Record<string, string>>({})

// Tabs configuration
const tabs = [
  { id: 'basic', label: 'Basic Info', icon: 'fas fa-info-circle' },
  { id: 'pricing', label: 'Pricing', icon: 'fas fa-dollar-sign' },
  { id: 'limits', label: 'Limits', icon: 'fas fa-sliders-h' },
  { id: 'features', label: 'Features', icon: 'fas fa-star' },
  { id: 'preview', label: 'Preview', icon: 'fas fa-eye' }
]

// Computed
const isFormValid = computed(() => {
  return formData.value.display_name.trim() && 
         formData.value.description.trim() &&
         formData.value.price_monthly > 0 &&
         formData.value.price_yearly > 0 &&
         formData.value.max_users > 0 &&
         formData.value.max_courses > 0 &&
         !Object.keys(errors.value).length
})

const yearlySavingsAmount = computed(() => {
  const monthlyTotal = formData.value.price_monthly * 12
  const savings = monthlyTotal - formData.value.price_yearly
  return savings > 0 ? `$${savings.toFixed(2)}` : '$0.00'
})

const yearlySavingsPercentage = computed(() => {
  const monthlyTotal = formData.value.price_monthly * 12
  const savings = ((monthlyTotal - formData.value.price_yearly) / monthlyTotal) * 100
  return savings > 0 ? Math.round(savings) : 0
})

// Methods
const validateForm = () => {
  errors.value = {}

  if (!formData.value.display_name.trim()) {
    errors.value.display_name = 'Display name is required'
  }

  if (!formData.value.description.trim()) {
    errors.value.description = 'Description is required'
  }

  if (formData.value.price_monthly <= 0) {
    errors.value.price_monthly = 'Monthly price must be greater than 0'
  }

  if (formData.value.price_yearly <= 0) {
    errors.value.price_yearly = 'Yearly price must be greater than 0'
  }

  if (formData.value.max_users <= 0) {
    errors.value.max_users = 'Max users must be greater than 0'
  }

  if (formData.value.max_courses <= 0) {
    errors.value.max_courses = 'Max courses must be greater than 0'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return

  loading.value = true
  
  try {
    const planData: Partial<SubscriptionPlan> = {
      name: formData.value.name,
      display_name: formData.value.display_name.trim(),
      description: formData.value.description.trim(),
      price_monthly: formData.value.price_monthly,
      price_yearly: formData.value.price_yearly,
      max_users: formData.value.max_users,
      max_courses: formData.value.max_courses,
      max_storage_gb: formData.value.max_storage_gb,
      ai_quota_monthly: formData.value.ai_quota_monthly,
      max_file_size_mb: formData.value.max_file_size_mb,
      monthly_download_limit: formData.value.monthly_download_limit,
      has_analytics: formData.value.has_analytics,
      has_api_access: formData.value.has_api_access,
      has_white_labeling: formData.value.has_white_labeling,
      has_priority_support: formData.value.has_priority_support,
      has_custom_integrations: formData.value.has_custom_integrations,
      recording_access: formData.value.recording_access,
      premium_content_access: formData.value.premium_content_access,
      is_popular: formData.value.is_popular,
      is_active: formData.value.is_active,
      sort_order: formData.value.sort_order
    }

    emit('save', planData)
  } catch (error) {
    console.error('Error saving plan:', error)
  } finally {
    loading.value = false
  }
}

const loadPlanData = () => {
  if (props.plan) {
    formData.value = {
      name: props.plan.name || 'basic',
      display_name: props.plan.display_name || '',
      description: props.plan.description || '',
      price_monthly: props.plan.price_monthly || 0,
      price_yearly: props.plan.price_yearly || 0,
      max_users: props.plan.max_users || 10,
      max_courses: props.plan.max_courses || 5,
      max_storage_gb: props.plan.max_storage_gb || 10,
      ai_quota_monthly: props.plan.ai_quota_monthly || 100,
      max_file_size_mb: props.plan.max_file_size_mb || 10,
      monthly_download_limit: props.plan.monthly_download_limit,
      has_analytics: props.plan.has_analytics || false,
      has_api_access: props.plan.has_api_access || false,
      has_white_labeling: props.plan.has_white_labeling || false,
      has_priority_support: props.plan.has_priority_support || false,
      has_custom_integrations: props.plan.has_custom_integrations || false,
      recording_access: props.plan.recording_access || false,
      premium_content_access: props.plan.premium_content_access || false,
      is_popular: props.plan.is_popular || false,
      is_active: props.plan.is_active !== false,
      sort_order: props.plan.sort_order || 0
    }
  }
}

// Watchers
watch(() => props.plan, loadPlanData, { immediate: true })

// Lifecycle
onMounted(() => {
  loadPlanData()
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
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
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

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.form-tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  background: none;
  border: none;
  color: #6b7280;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
}

.tab-btn:hover {
  color: #374151;
  background: #f3f4f6;
}

.tab-btn.active {
  color: #3b82f6;
  background: white;
  border-bottom-color: #3b82f6;
}

.tab-content {
  padding: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #374151;
  font-weight: 500;
  font-size: 0.875rem;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.error,
.form-textarea.error,
.form-select.error {
  border-color: #ef4444;
}

.form-help {
  display: block;
  margin-top: 0.25rem;
  color: #6b7280;
  font-size: 0.75rem;
}

.error-message {
  display: block;
  margin-top: 0.25rem;
  color: #ef4444;
  font-size: 0.75rem;
}

.price-input-group {
  display: flex;
  align-items: center;
}

.currency-symbol {
  padding: 0.75rem;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-right: none;
  border-radius: 6px 0 0 6px;
  color: #6b7280;
  font-weight: 500;
}

.price-input-group .form-input {
  border-radius: 0 6px 6px 0;
}

.savings-display {
  margin-top: 1rem;
  padding: 1rem;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
}

.savings-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #0369a1;
  font-size: 0.875rem;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox {
  width: 16px;
  height: 16px;
}

.checkbox-text {
  color: #374151;
  font-weight: 500;
}

.features-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.feature-group h3 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1rem;
  font-weight: 600;
}

.feature-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.feature-checkbox:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.feature-info {
  flex: 1;
}

.feature-name {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.25rem;
}

.feature-description {
  display: block;
  font-size: 0.875rem;
  color: #6b7280;
}

.plan-preview {
  display: flex;
  justify-content: center;
}

.preview-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
}

.preview-card.popular {
  border-color: #3b82f6;
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.preview-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.popular-badge {
  padding: 0.125rem 0.5rem;
  background: #3b82f6;
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.preview-pricing {
  margin-bottom: 1rem;
}

.price-display {
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
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
}

.period {
  font-size: 1rem;
  color: #6b7280;
  margin-left: 0.25rem;
}

.yearly-price {
  font-size: 0.875rem;
  color: #6b7280;
}

.savings {
  color: #059669;
  font-weight: 500;
}

.preview-description {
  color: #6b7280;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

.preview-limits {
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

.preview-features {
  margin-bottom: 1rem;
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

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-outline {
  background: transparent;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background: #f9fafb;
}

@media (max-width: 768px) {
  .form-grid,
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .form-tabs {
    flex-wrap: wrap;
  }
  
  .tab-btn {
    flex: none;
    min-width: 120px;
  }
}
</style>