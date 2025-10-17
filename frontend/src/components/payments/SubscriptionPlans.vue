<template>
  <div class="subscription-plans p-6">
    <!-- Header -->
    <div class="text-center mb-8">
      <h2 class="text-3xl font-bold text-gray-900 mb-2">Choose Your Plan</h2>
      <p class="text-gray-600">Select the perfect plan for your organization's needs</p>
    </div>

    <!-- Billing Toggle -->
    <div class="flex justify-center mb-8">
      <div class="bg-gray-100 p-1 rounded-lg">
        <button
          @click="billingCycle = 'monthly'"
          :class="[
            'px-4 py-2 rounded-md text-sm font-medium transition-all',
            billingCycle === 'monthly'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          ]"
        >
          Monthly
        </button>
        <button
          @click="billingCycle = 'yearly'"
          :class="[
            'px-4 py-2 rounded-md text-sm font-medium transition-all',
            billingCycle === 'yearly'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          ]"
        >
          Yearly
          <span class="ml-1 text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full">
            Save 20%
          </span>
        </button>
      </div>
    </div>

    <!-- Plans Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div
        v-for="plan in plans"
        :key="plan.id"
        :class="[
          'plan-card relative bg-white rounded-lg shadow-lg border-2 transition-all duration-200 hover:shadow-xl',
          plan.is_popular ? 'border-blue-500 transform scale-105' : 'border-gray-200',
          currentPlan === plan.id ? 'ring-2 ring-blue-500' : ''
        ]"
      >
        <!-- Popular Badge -->
        <div
          v-if="plan.is_popular"
          class="absolute -top-3 left-1/2 transform -translate-x-1/2"
        >
          <span class="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
            Most Popular
          </span>
        </div>

        <div class="p-6">
          <!-- Plan Header -->
          <div class="text-center mb-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ plan.name }}</h3>
            <p class="text-gray-600 text-sm mb-4">{{ plan.description }}</p>
            
            <!-- Price -->
            <div class="mb-4">
              <span class="text-4xl font-bold text-gray-900">
                ${{ billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly }}
              </span>
              <span class="text-gray-600 ml-1">
                /{{ billingCycle === 'monthly' ? 'month' : 'year' }}
              </span>
            </div>

            <!-- Savings Badge -->
            <div v-if="billingCycle === 'yearly'" class="text-sm text-green-600 font-medium">
              Save ${{ (plan.price_monthly * 12 - plan.price_yearly).toFixed(0) }} per year
            </div>
          </div>

          <!-- Features List -->
          <ul class="space-y-3 mb-6">
            <li
              v-for="feature in plan.features"
              :key="feature"
              class="flex items-start"
            >
              <svg class="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <span class="text-gray-700 text-sm">{{ feature }}</span>
            </li>
          </ul>

          <!-- Plan Specs -->
          <div class="border-t pt-4 mb-6">
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-600">Max Users:</span>
                <span class="font-medium ml-1">
                  {{ plan.max_users === -1 ? 'Unlimited' : plan.max_users }}
                </span>
              </div>
              <div>
                <span class="text-gray-600">Max Courses:</span>
                <span class="font-medium ml-1">
                  {{ plan.max_courses === -1 ? 'Unlimited' : plan.max_courses }}
                </span>
              </div>
              <div>
                <span class="text-gray-600">AI Quota:</span>
                <span class="font-medium ml-1">{{ plan.ai_quota_monthly }}/month</span>
              </div>
              <div>
                <span class="text-gray-600">Storage:</span>
                <span class="font-medium ml-1">{{ plan.storage_gb }}GB</span>
              </div>
            </div>
          </div>

          <!-- Action Button -->
          <button
            @click="selectPlan(plan)"
            :disabled="loading || currentPlan === plan.id"
            :class="[
              'w-full py-3 px-4 rounded-lg font-medium transition-all duration-200',
              currentPlan === plan.id
                ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                : plan.is_popular
                ? 'bg-blue-600 text-white hover:bg-blue-700 transform hover:scale-105'
                : 'bg-gray-900 text-white hover:bg-gray-800 transform hover:scale-105'
            ]"
          >
            <div v-if="loading && selectedPlanId === plan.id" class="flex items-center justify-center">
              <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Processing...
            </div>
            <div v-else>
              {{ currentPlan === plan.id ? 'Current Plan' : 'Select Plan' }}
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- Support Comparison -->
    <div class="bg-gray-50 rounded-lg p-6 mb-6">
      <h4 class="text-lg font-semibold text-gray-900 mb-4 text-center">Support Levels</h4>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="text-center">
          <div class="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-2">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h5 class="font-medium text-gray-900">Basic Support</h5>
          <p class="text-sm text-gray-600">Email support within 48 hours</p>
        </div>
        <div class="text-center">
          <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h5 class="font-medium text-gray-900">Priority Support</h5>
          <p class="text-sm text-gray-600">Email & chat support within 24 hours</p>
        </div>
        <div class="text-center">
          <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h5 class="font-medium text-gray-900">Dedicated Support</h5>
          <p class="text-sm text-gray-600">Dedicated account manager & phone support</p>
        </div>
      </div>
    </div>

    <!-- Close Button -->
    <div class="text-center">
      <button
        @click="$emit('close')"
        class="text-gray-600 hover:text-gray-900 transition-colors"
      >
        Close
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usePayments } from '../../composables/usePayments'

interface Props {
  currentPlan?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  planSelected: [planData: any]
  close: []
}>()

const { createSubscription, loading } = usePayments()

const billingCycle = ref<'monthly' | 'yearly'>('monthly')
const selectedPlanId = ref<string | null>(null)

const plans = ref([
  {
    id: 'basic',
    name: 'Basic',
    description: 'Perfect for small teams getting started',
    price_monthly: 29,
    price_yearly: 290,
    features: [
      'Up to 50 users',
      'Up to 10 courses',
      'Basic AI features (100 queries/month)',
      '10GB storage',
      'Email support',
      'Basic analytics'
    ],
    max_users: 50,
    max_courses: 10,
    ai_quota_monthly: 100,
    storage_gb: 10,
    support_level: 'basic',
    is_popular: false
  },
  {
    id: 'pro',
    name: 'Professional',
    description: 'Ideal for growing organizations',
    price_monthly: 79,
    price_yearly: 790,
    features: [
      'Up to 200 users',
      'Up to 50 courses',
      'Advanced AI features (500 queries/month)',
      '100GB storage',
      'Priority support',
      'Advanced analytics',
      'Custom branding',
      'API access'
    ],
    max_users: 200,
    max_courses: 50,
    ai_quota_monthly: 500,
    storage_gb: 100,
    support_level: 'priority',
    is_popular: true
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    description: 'For large organizations with advanced needs',
    price_monthly: 199,
    price_yearly: 1990,
    features: [
      'Unlimited users',
      'Unlimited courses',
      'Premium AI features (2000 queries/month)',
      '1TB storage',
      'Dedicated support',
      'Custom integrations',
      'White-label solution',
      'Advanced security',
      'SLA guarantee'
    ],
    max_users: -1,
    max_courses: -1,
    ai_quota_monthly: 2000,
    storage_gb: 1000,
    support_level: 'dedicated',
    is_popular: false
  }
])

const selectPlan = async (plan: any) => {
  if (loading.value || props.currentPlan === plan.id) return

  selectedPlanId.value = plan.id

  try {
    const subscriptionData = await createSubscription({
      plan: plan.id,
      billing_cycle: billingCycle.value,
      payment_method: 'stripe'
    })

    emit('planSelected', {
      plan: plan,
      billing_cycle: billingCycle.value,
      subscription: subscriptionData
    })

  } catch (error) {
    console.error('Failed to create subscription:', error)
  } finally {
    selectedPlanId.value = null
  }
}

onMounted(() => {
  // Set default billing cycle based on current plan if available
  if (props.currentPlan) {
    billingCycle.value = 'monthly' // Could be determined from current subscription
  }
})
</script>

<style scoped>
.plan-card {
  transition: all 0.3s ease;
}

.plan-card:hover {
  transform: translateY(-4px);
}

.plan-card.scale-105 {
  transform: scale(1.05);
}

.plan-card.scale-105:hover {
  transform: scale(1.05) translateY(-4px);
}
</style>