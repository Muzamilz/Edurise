/**
 * JWT Token Management Utilities
 */

export interface JWTPayload {
  user_id: string
  email: string
  tenant_id?: string
  exp: number
  iat: number
}

/**
 * Decode JWT token payload without verification
 */
export const decodeJWT = (token: string): JWTPayload | null => {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) {
      return null
    }

    const payload = parts[1]
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(decoded)
  } catch (error) {
    console.error('Failed to decode JWT:', error)
    return null
  }
}

/**
 * Check if JWT token is expired
 */
export const isTokenExpired = (token: string): boolean => {
  const payload = decodeJWT(token)
  if (!payload) {
    return true
  }

  const currentTime = Math.floor(Date.now() / 1000)
  return payload.exp < currentTime
}

/**
 * Check if JWT token will expire soon (within 5 minutes)
 */
export const isTokenExpiringSoon = (token: string): boolean => {
  const payload = decodeJWT(token)
  if (!payload) {
    return true
  }

  const currentTime = Math.floor(Date.now() / 1000)
  const fiveMinutesFromNow = currentTime + (5 * 60) // 5 minutes in seconds
  
  return payload.exp < fiveMinutesFromNow
}

/**
 * Get token expiration time as Date object
 */
export const getTokenExpiration = (token: string): Date | null => {
  const payload = decodeJWT(token)
  if (!payload) {
    return null
  }

  return new Date(payload.exp * 1000)
}

/**
 * Extract user information from JWT token
 */
export const getUserFromToken = (token: string): { userId: string; email: string; tenantId?: string } | null => {
  const payload = decodeJWT(token)
  if (!payload) {
    return null
  }

  return {
    userId: payload.user_id,
    email: payload.email,
    tenantId: payload.tenant_id
  }
}