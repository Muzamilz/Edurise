import type { User } from './api'

/**
 * Security Overview Dashboard Data
 */
export interface SecurityOverview {
  active_threats: number
  failed_logins_24h: number
  active_sessions: number
  compliance_score: number
  total_alerts: number
  critical_alerts: number
  resolved_alerts: number
  active_policies: number
  recent_events: SecurityEvent[]
  security_score: number
  last_scan: string
}

/**
 * Security Alert
 */
export interface SecurityAlert {
  id: string
  type: 'login_attempt' | 'password_change' | 'suspicious_activity' | 'policy_violation'
  severity: 'low' | 'medium' | 'high' | 'critical'
  title: string
  message: string
  description: string
  details?: string
  source?: string
  user?: User
  ip_address?: string
  created_at: string
  resolved: boolean
  resolved_at?: string
  resolved_by?: User
  read?: boolean
}

/**
 * Security Alert Filters
 */
export interface SecurityAlertFilters {
  severity?: 'low' | 'medium' | 'high' | 'critical'
  type?: string
  resolved?: boolean
  date_from?: string
  date_to?: string
  user_id?: string
  page?: number
  page_size?: number
}

/**
 * Security Event
 */
export interface SecurityEvent {
  id: string
  type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  description: string
  timestamp: string
  user?: User
  ip_address?: string
  user_agent?: string
  metadata?: Record<string, any>
}

/**
 * Security Policy
 */
export interface SecurityPolicy {
  id: string
  name: string
  description: string
  enabled: boolean
  policy_type: 'password' | 'session' | 'access' | 'data' | 'audit'
  type?: string // Alias for policy_type
  settings?: Record<string, any>
  rules?: Record<string, any>
  created_at: string
  updated_at: string
  created_by?: User
}

/**
 * Security Settings
 */
export interface SecuritySettings {
  password_min_length: number
  password_require_uppercase: boolean
  password_require_lowercase: boolean
  password_require_numbers: boolean
  password_require_special: boolean
  password_expiry_days: number
  session_timeout_minutes: number
  max_login_attempts: number
  lockout_duration_minutes: number
  two_factor_required: boolean
  ip_whitelist_enabled: boolean
  ip_whitelist: string[]
  audit_log_retention_days: number
}

/**
 * Compliance Report
 */
export interface ComplianceReport {
  gdpr_compliant: boolean
  data_retention_policy: string
  user_data_exports: number
  user_data_deletions: number
  last_audit_date: string
  issues: Array<{
    type: string
    severity: string
    description: string
  }>
}
