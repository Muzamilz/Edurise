import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

/**
 * Composable for role-based routing and navigation
 */
export function useRoleBasedRouting() {
  const router = useRouter()
  const authStore = useAuthStore()

  /**
   * Get the appropriate dashboard route based on user role
   */
  const getDashboardRoute = computed(() => {
    return authStore.dashboardRoute
  })

  /**
   * Navigate to the user's role-specific dashboard
   */
  const goToDashboard = async () => {
    await router.push(getDashboardRoute.value)
  }

  /**
   * Check if user has access to a specific role
   */
  const hasRole = (role: 'student' | 'teacher' | 'admin' | 'superuser'): boolean => {
    switch (role) {
      case 'superuser':
        return authStore.isSuperuser
      case 'admin':
        return authStore.isStaff || authStore.isSuperuser
      case 'teacher':
        return authStore.isApprovedTeacher || authStore.isStaff || authStore.isSuperuser
      case 'student':
        return authStore.isAuthenticated
      default:
        return false
    }
  }

  /**
   * Check if user can access a specific route based on role requirements
   */
  const canAccessRoute = (routeMeta: any): boolean => {
    if (!routeMeta) return true

    if (routeMeta.requiresSuperAdmin && !authStore.isSuperuser) {
      return false
    }

    if (routeMeta.requiresAdmin && !authStore.isStaff && !authStore.isSuperuser) {
      return false
    }

    if (routeMeta.requiresTeacher && !authStore.isApprovedTeacher && !authStore.isStaff && !authStore.isSuperuser) {
      return false
    }

    if (routeMeta.requiresAuth && !authStore.isAuthenticated) {
      return false
    }

    return true
  }

  /**
   * Get user-friendly role name
   */
  const getRoleName = computed(() => {
    if (authStore.isSuperuser) return 'Super Administrator'
    if (authStore.isStaff) return 'Administrator'
    if (authStore.isApprovedTeacher) return 'Teacher'
    if (authStore.isTeacher) return 'Teacher (Pending Approval)'
    return 'Student'
  })

  /**
   * Get available navigation items based on user role
   */
  const getNavigationItems = computed(() => {
    const items = []

    // Common items for all authenticated users
    if (authStore.isAuthenticated) {
      items.push({
        name: 'Dashboard',
        route: getDashboardRoute.value,
        icon: 'dashboard'
      })
    }

    // Student items
    if (authStore.isAuthenticated) {
      items.push(
        { name: 'My Courses', route: '/student/my-courses', icon: 'book' },
        { name: 'Live Classes', route: '/student/live-classes', icon: 'video' },
        { name: 'Certificates', route: '/student/certificates', icon: 'certificate' }
      )
    }

    // Teacher items
    if (authStore.isApprovedTeacher || authStore.isStaff || authStore.isSuperuser) {
      items.push(
        { name: 'My Teaching', route: '/teacher/courses', icon: 'teach' },
        { name: 'Create Course', route: '/teacher/courses/create', icon: 'plus' },
        { name: 'My Students', route: '/teacher/students', icon: 'users' },
        { name: 'Analytics', route: '/teacher/analytics', icon: 'chart' }
      )
    }

    // Admin items
    if (authStore.isStaff || authStore.isSuperuser) {
      items.push(
        { name: 'User Management', route: '/admin/users', icon: 'users-cog' },
        { name: 'Course Management', route: '/admin/courses', icon: 'book-cog' },
        { name: 'Teacher Approvals', route: '/admin/teachers/pending', icon: 'user-check' },
        { name: 'Analytics', route: '/admin/analytics', icon: 'chart-line' }
      )
    }

    // Super Admin items
    if (authStore.isSuperuser) {
      items.push(
        { name: 'Organizations', route: '/super-admin/organizations', icon: 'building' },
        { name: 'Global Users', route: '/super-admin/users', icon: 'users-globe' },
        { name: 'Platform Analytics', route: '/super-admin/analytics/platform', icon: 'chart-network' },
        { name: 'System Settings', route: '/super-admin/system', icon: 'cog' }
      )
    }

    return items
  })

  return {
    getDashboardRoute,
    goToDashboard,
    hasRole,
    canAccessRoute,
    getRoleName,
    getNavigationItems
  }
}
