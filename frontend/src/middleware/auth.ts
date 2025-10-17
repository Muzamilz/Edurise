import { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export const authGuard = (
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    // Store the intended destination
    const redirectPath = to.fullPath !== '/auth/login' ? to.fullPath : undefined
    next({
      path: '/auth/login',
      query: redirectPath ? { redirect: redirectPath } : undefined
    })
  } else {
    next()
  }
}

export const guestGuard = (
  _to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const authStore = useAuthStore()
  
  if (authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
}

export const teacherGuard = (
  _to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    next('/auth/login')
  } else if (!authStore.isApprovedTeacher) {
    next('/unauthorized')
  } else {
    next()
  }
}

export const adminGuard = (
  _to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    next('/auth/login')
  } else if (!authStore.isStaff) {
    next('/unauthorized')
  } else {
    next()
  }
}

export const superAdminGuard = (
  _to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated) {
    next('/auth/login')
  } else if (!authStore.isSuperuser) {
    next('/unauthorized')
  } else {
    next()
  }
}