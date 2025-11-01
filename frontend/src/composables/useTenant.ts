import { ref, computed, readonly } from 'vue'
import { api } from '@/services/api'
import type { Organization } from '@/types/api'

const currentTenant = ref<Organization | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

export const useTenant = () => {
  // Computed properties
  const branding = computed(() => ({
    primaryColor: currentTenant.value?.primary_color || '#3B82F6',
    secondaryColor: currentTenant.value?.secondary_color || '#1E40AF',
    logo: currentTenant.value?.logo || null,
    name: currentTenant.value?.name || 'Edurise'
  }))

  const subscriptionPlan = computed(() => currentTenant.value?.subscription?.plan_name || 'basic')

  // Methods
  const detectTenantFromSubdomain = (): string | null => {
    if (typeof window === 'undefined') return null
    
    const hostname = window.location.hostname
    const parts = hostname.split('.')
    
    // Check if it's a subdomain (more than 2 parts for domain.com)
    // or more than 3 parts for domain.co.uk etc.
    if (parts.length >= 3 && parts[0] !== 'www') {
      return parts[0]
    }
    
    return null
  }

  const loadTenantBySubdomain = async (subdomain: string): Promise<Organization | null> => {
    try {
      isLoading.value = true
      error.value = null

      const response = await api.get<Organization>(`/accounts/organizations/by_subdomain/?subdomain=${subdomain}`)
      currentTenant.value = response.data.data
      
      return response.data.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to load tenant information'
      currentTenant.value = null
      return null
    } finally {
      isLoading.value = false
    }
  }

  const initializeTenant = async (): Promise<void> => {
    const subdomain = detectTenantFromSubdomain()
    
    if (subdomain) {
      await loadTenantBySubdomain(subdomain)
    } else {
      // Default to public marketplace
      currentTenant.value = null
    }
  }

  const setTenant = (tenant: Organization | null): void => {
    currentTenant.value = tenant
  }

  const clearTenant = (): void => {
    currentTenant.value = null
    error.value = null
  }

  const applyBranding = (): void => {
    if (typeof document === 'undefined') return

    const root = document.documentElement
    
    if (currentTenant.value) {
      root.style.setProperty('--primary-color', currentTenant.value.primary_color)
      root.style.setProperty('--secondary-color', currentTenant.value.secondary_color)
      
      // Update page title if needed
      if (currentTenant.value.name) {
        const titleSuffix = ` - ${currentTenant.value.name}`
        if (!document.title.includes(titleSuffix)) {
          document.title = document.title.replace(' - Edurise', titleSuffix)
        }
      }
    } else {
      // Reset to default branding
      root.style.setProperty('--primary-color', '#3B82F6')
      root.style.setProperty('--secondary-color', '#1E40AF')
    }
  }

  const isFeatureEnabled = (feature: string): boolean => {
    if (!currentTenant.value) return true // Public marketplace has all features
    
    const plan = currentTenant.value.subscription?.plan_name || 'basic'
    
    // Define feature availability by plan
    const featureMatrix: Record<string, string[]> = {
      'ai_tutor': ['pro', 'enterprise'],
      'live_classes': ['basic', 'pro', 'enterprise'],
      'custom_branding': ['pro', 'enterprise'],
      'analytics': ['pro', 'enterprise'],
      'api_access': ['enterprise'],
      'sso': ['enterprise'],
      'white_label': ['enterprise']
    }
    
    const allowedPlans = featureMatrix[feature]
    return allowedPlans ? allowedPlans.includes(plan) : true
  }

  return {
    // State
    currentTenant: readonly(currentTenant),
    isLoading: readonly(isLoading),
    error: readonly(error),
    
    // Computed
    branding,
    subscriptionPlan,
    
    // Methods
    detectTenantFromSubdomain,
    loadTenantBySubdomain,
    initializeTenant,
    setTenant,
    clearTenant,
    applyBranding,
    isFeatureEnabled
  }
}