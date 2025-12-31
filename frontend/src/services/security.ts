import { api } from './api'
import type {
  SecurityOverview,
  SecurityAlert,
  SecurityAlertFilters,
  SecurityEvent,
  SecurityPolicy,
  SecuritySettings,
  ComplianceReport
} from '../types/security'
import type { PaginatedResponse, SecurityEventFilters } from '../types/api'

/**
 * SecurityService
 * 
 * Centralized service for all security-related API operations.
 * Handles security alerts, policies, settings, and compliance.
 */
export class SecurityService {
  // ===== Overview and Monitoring =====

  /**
   * Get security dashboard overview data
   * @returns Security overview with threats, alerts, and compliance score
   */
  static async getSecurityOverview(): Promise<SecurityOverview> {
    try {
      const response = await api.get<SecurityOverview>('/security/')
      return response.data.data
    } catch (error) {
      console.error('Failed to fetch security overview:', error)
      throw error
    }
  }

  /**
   * Get security alerts with optional filtering
   * @param filters - Optional filters for severity, type, resolved status, etc.
   * @returns Paginated list of security alerts
   */
  static async getSecurityAlerts(filters?: SecurityAlertFilters): Promise<PaginatedResponse<SecurityAlert>> {
    try {
      const response = await api.get<PaginatedResponse<SecurityAlert>>('/security/alerts/', {
        params: filters
      })
      return response.data.data
    } catch (error) {
      console.error('Failed to fetch security alerts:', error)
      throw error
    }
  }

  /**
   * Get security events with optional filtering
   * @param filters - Optional filters for events
   * @returns Paginated list of security events
   */
  static async getSecurityEvents(filters?: SecurityEventFilters): Promise<PaginatedResponse<SecurityEvent>> {
    try {
      const response = await api.get<PaginatedResponse<SecurityEvent>>('/security/events/', {
        params: filters
      })
      return response.data.data
    } catch (error) {
      console.error('Failed to fetch security events:', error)
      throw error
    }
  }

  // ===== Alert Management =====

  /**
   * Mark a security alert as resolved
   * @param alertId - ID of the alert to resolve
   * @returns Updated alert
   */
  static async resolveAlert(alertId: string): Promise<SecurityAlert> {
    try {
      const response = await api.patch<SecurityAlert>(`/security/alerts/${alertId}/`, {
        resolved: true
      })
      return response.data.data
    } catch (error) {
      console.error(`Failed to resolve alert ${alertId}:`, error)
      throw error
    }
  }

  /**
   * Dismiss a security alert
   * @param alertId - ID of the alert to dismiss
   */
  static async dismissAlert(alertId: string): Promise<void> {
    try {
      await api.delete(`/security/alerts/${alertId}/`)
    } catch (error) {
      console.error(`Failed to dismiss alert ${alertId}:`, error)
      throw error
    }
  }

  /**
   * Get detailed information about a specific alert
   * @param alertId - ID of the alert
   * @returns Alert details
   */
  static async getAlertDetails(alertId: string): Promise<SecurityAlert> {
    try {
      const response = await api.get<SecurityAlert>(`/security/alerts/${alertId}/`)
      return response.data.data
    } catch (error) {
      console.error(`Failed to fetch alert details for ${alertId}:`, error)
      throw error
    }
  }

  // ===== Policy Management =====

  /**
   * Get all security policies
   * @returns List of security policies
   */
  static async getSecurityPolicies(): Promise<SecurityPolicy[]> {
    try {
      const response = await api.get<SecurityPolicy[]>('/security/policies/')
      return response.data.data
    } catch (error) {
      console.error('Failed to fetch security policies:', error)
      throw error
    }
  }

  /**
   * Create a new security policy
   * @param policyData - Policy data to create
   * @returns Created policy
   */
  static async createPolicy(policyData: Partial<SecurityPolicy>): Promise<SecurityPolicy> {
    try {
      const response = await api.post<SecurityPolicy>('/security/policies/', policyData)
      return response.data.data
    } catch (error) {
      console.error('Failed to create security policy:', error)
      throw error
    }
  }

  /**
   * Update an existing security policy
   * @param id - Policy ID
   * @param policyData - Updated policy data
   * @returns Updated policy
   */
  static async updatePolicy(id: string, policyData: Partial<SecurityPolicy>): Promise<SecurityPolicy> {
    try {
      const response = await api.patch<SecurityPolicy>(`/security/policies/${id}/`, policyData)
      return response.data.data
    } catch (error) {
      console.error(`Failed to update policy ${id}:`, error)
      throw error
    }
  }

  /**
   * Delete a security policy
   * @param id - Policy ID to delete
   */
  static async deletePolicy(id: string): Promise<void> {
    try {
      await api.delete(`/security/policies/${id}/`)
    } catch (error) {
      console.error(`Failed to delete policy ${id}:`, error)
      throw error
    }
  }

  /**
   * Enable or disable a security policy
   * @param id - Policy ID
   * @param enabled - Whether to enable or disable the policy
   * @returns Updated policy
   */
  static async togglePolicy(id: string, enabled: boolean): Promise<SecurityPolicy> {
    try {
      const response = await api.patch<SecurityPolicy>(`/security/policies/${id}/`, { enabled })
      return response.data.data
    } catch (error) {
      console.error(`Failed to toggle policy ${id}:`, error)
      throw error
    }
  }

  // ===== Settings =====

  /**
   * Get security settings configuration
   * @returns Security settings
   */
  static async getSecuritySettings(): Promise<SecuritySettings> {
    try {
      const response = await api.get<SecuritySettings>('/security/settings/')
      return response.data.data
    } catch (error) {
      console.error('Failed to fetch security settings:', error)
      throw error
    }
  }

  /**
   * Update security settings
   * @param settings - Updated security settings
   * @returns Updated settings
   */
  static async updateSecuritySettings(settings: Partial<SecuritySettings>): Promise<SecuritySettings> {
    try {
      const response = await api.patch<SecuritySettings>('/security/settings/', settings)
      return response.data.data
    } catch (error) {
      console.error('Failed to update security settings:', error)
      throw error
    }
  }

  /**
   * Reset security settings to defaults
   * @returns Default security settings
   */
  static async resetSecuritySettings(): Promise<SecuritySettings> {
    try {
      const response = await api.post<SecuritySettings>('/security/settings/reset/')
      return response.data.data
    } catch (error) {
      console.error('Failed to reset security settings:', error)
      throw error
    }
  }

  // ===== Compliance =====

  /**
   * Export user data for GDPR compliance
   * @param userId - ID of the user whose data to export
   * @returns Blob containing user data
   */
  static async exportUserData(userId: string): Promise<Blob> {
    try {
      const response = await api.get(`/security/compliance/export-user-data/${userId}/`, {
        responseType: 'blob'
      })
      return response.data as unknown as Blob
    } catch (error) {
      console.error(`Failed to export user data for ${userId}:`, error)
      throw error
    }
  }

  /**
   * Delete user data for GDPR compliance
   * @param userId - ID of the user whose data to delete
   * @param reason - Reason for deletion
   */
  static async deleteUserData(userId: string, reason: string): Promise<void> {
    try {
      await api.post(`/security/compliance/delete-user-data/${userId}/`, { reason })
    } catch (error) {
      console.error(`Failed to delete user data for ${userId}:`, error)
      throw error
    }
  }

  /**
   * Get compliance report
   * @returns Compliance status and report
   */
  static async getComplianceReport(): Promise<ComplianceReport> {
    try {
      const response = await api.get<ComplianceReport>('/security/compliance/report/')
      return response.data.data
    } catch (error) {
      console.error('Failed to fetch compliance report:', error)
      throw error
    }
  }
}
