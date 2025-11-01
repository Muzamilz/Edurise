import { computed } from 'vue'
import { useApiData } from './useApiData'
import { useAuth } from './useAuth'

// Dashboard data types
export interface StudentDashboardData {
  enrolledCourses: Course[]
  completedCourses: Course[]
  hoursLearned: number
  certificates: Certificate[]
  currentCourses: Course[]
  recommendations: Course[]
  progressStats: {
    totalEnrollments: number
    completedCourses: number
    inProgressCourses: number
    averageProgress: number
  }
  upcomingClasses: LiveClass[]
  recentActivity: Activity[]
}

export interface TeacherDashboardData {
  totalCourses: number
  totalStudents: number
  totalRevenue: number
  courseStats: {
    published: number
    draft: number
    totalEnrollments: number
    averageRating: number
  }
  recentEnrollments: Enrollment[]
  upcomingClasses: LiveClass[]
  revenueStats: {
    thisMonth: number
    lastMonth: number
    growth: number
  }
  topCourses: Course[]
  studentEngagement: {
    activeStudents: number
    completionRate: number
    averageProgress: number
  }
}

export interface AdminDashboardData {
  userStats: {
    totalUsers: number
    activeUsers: number
    newUsersThisMonth: number
    teacherCount: number
    studentCount: number
  }
  courseStats: {
    totalCourses: number
    publishedCourses: number
    totalEnrollments: number
    completionRate: number
  }
  revenueStats: {
    totalRevenue: number
    monthlyRevenue: number
    revenueGrowth: number
    subscriptionRevenue: number
  }
  systemHealth: {
    serverStatus: string
    databaseStatus: string
    cacheStatus: string
    apiResponseTime: number
  }
  recentActivity: Activity[]
  topPerformingCourses: Course[]
}

export interface SuperAdminDashboardData {
  platformStats: {
    totalTenants: number
    activeTenants: number
    totalUsers: number
    totalCourses: number
    totalRevenue: number
    totalEnrollments: number
    totalTeachers: number
    approvedTeachers: number
    publishedCourses: number
    activeEnrollments: number
    completedEnrollments: number
  }
  tenantStats: Tenant[]
  systemMetrics: {
    serverLoad: number
    memoryUsage: number
    diskUsage: number
    apiCalls: number
  }
  revenueByTenant: {
    tenantId: string
    tenantName: string
    revenue: number
    growth: number
  }[]
  globalActivity: Activity[]
  subscriptionStats: {
    basic: number
    pro: number
    enterprise: number
  }
}

// Supporting types
interface Course {
  id: string
  title: string
  description: string
  instructor: string
  enrollmentCount: number
  rating: number
  progress?: number
  thumbnail?: string
}

interface Certificate {
  id: string
  courseTitle: string
  issuedDate: string
  certificateUrl: string
}

interface LiveClass {
  id: string
  title: string
  courseTitle: string
  scheduledAt: string
  duration: number
  joinUrl?: string
}

interface Activity {
  id: string
  type: string
  description: string
  timestamp: string
  user?: string
}

interface Enrollment {
  id: string
  studentName: string
  courseTitle: string
  enrolledAt: string
  progress: number
}

interface Tenant {
  id: string
  name: string
  subdomain: string
  subscriptionPlan: string
  userCount: number
  courseCount: number
  revenue: number
}

export const useDashboardData = () => {
  const { user } = useAuth()

  // Student Dashboard Data
  const studentData = useApiData<StudentDashboardData>('/dashboard/student/', {
    immediate: !!(user.value && !user.value.is_teacher && !user.value.is_staff),
    transform: (data) => ({
      enrolledCourses: data.recent_enrollments || [],
      completedCourses: [], // Will be calculated from enrollment stats
      hoursLearned: data.enrollment_stats?.total_learning_hours || 0,
      certificates: [], // Will be calculated from enrollment stats
      currentCourses: data.courses_in_progress || [],
      recommendations: data.recommendations || [],
      progressStats: {
        totalEnrollments: data.enrollment_stats?.total_enrollments || 0,
        completedCourses: data.enrollment_stats?.completed_courses || 0,
        inProgressCourses: data.enrollment_stats?.active_courses || 0,
        averageProgress: data.enrollment_stats?.average_progress || 0
      },
      upcomingClasses: data.upcoming_classes || [],
      recentActivity: data.recent_notifications || []
    }),
    cacheKey: 'student-dashboard',
    // Cache for 5 minutes
  })

  // Teacher Dashboard Data
  const teacherData = useApiData<TeacherDashboardData>('/dashboard/teacher/', {
    immediate: !!(user.value?.is_teacher && !user.value.is_staff),
    transform: (data) => ({
      totalCourses: data.overview_stats?.total_courses || 0,
      totalStudents: data.overview_stats?.total_students || 0,
      totalRevenue: data.overview_stats?.total_revenue || 0,
      courseStats: {
        published: data.overview_stats?.published_courses || 0,
        draft: (data.overview_stats?.total_courses || 0) - (data.overview_stats?.published_courses || 0),
        totalEnrollments: data.overview_stats?.total_enrollments || 0,
        averageRating: data.overview_stats?.average_rating || 0
      },
      recentEnrollments: data.recent_enrollments || [],
      upcomingClasses: data.upcoming_classes || [],
      revenueStats: {
        thisMonth: data.overview_stats?.total_revenue || 0, // Backend doesn't separate monthly yet
        lastMonth: 0,
        growth: 0
      },
      topCourses: data.course_performance || [],
      studentEngagement: {
        activeStudents: data.overview_stats?.total_students || 0,
        completionRate: 0, // Will be calculated from course performance
        averageProgress: 0
      }
    }),
    cacheKey: 'teacher-dashboard',
    // Cache for 5 minutes
  })

  // Admin Dashboard Data
  const adminData = useApiData<AdminDashboardData>('/dashboard/admin/', {
    immediate: !!(user.value?.is_staff && !user.value.is_superuser),
    transform: (data) => ({
      userStats: {
        totalUsers: data.user_stats?.total_users || 0,
        activeUsers: data.user_stats?.active_users || 0,
        newUsersThisMonth: data.user_stats?.new_users_this_month || 0,
        teacherCount: data.user_stats?.total_teachers || 0,
        studentCount: (data.user_stats?.total_users || 0) - (data.user_stats?.total_teachers || 0)
      },
      courseStats: {
        totalCourses: data.course_stats?.total_courses || 0,
        publishedCourses: data.course_stats?.published_courses || 0,
        totalEnrollments: data.enrollment_stats?.total_enrollments || 0,
        completionRate: data.enrollment_stats?.completion_rate || 0
      },
      revenueStats: {
        totalRevenue: data.revenue_stats?.total_revenue || 0,
        monthlyRevenue: data.revenue_stats?.revenue_this_month || 0,
        revenueGrowth: data.revenue_stats?.revenue_growth_rate || 0,
        subscriptionRevenue: data.revenue_stats?.total_revenue || 0 // Backend doesn't separate subscription revenue yet
      },
      systemHealth: {
        serverStatus: data.system_health?.database_status || 'healthy',
        databaseStatus: data.system_health?.database_status || 'healthy',
        cacheStatus: data.system_health?.cache_status || 'healthy',
        apiResponseTime: 0 // Backend doesn't provide this yet
      },
      recentActivity: data.recent_activity || [],
      topPerformingCourses: data.popular_courses || []
    }),
    cacheKey: 'admin-dashboard',
    // Cache for 3 minutes for admin data
  })

  // Super Admin Dashboard Data
  const superAdminData = useApiData<SuperAdminDashboardData>('/dashboard/superadmin/', {
    immediate: !!(user.value?.is_superuser),
    transform: (data) => ({
      platformStats: {
        totalTenants: data.platform_stats?.total_organizations || 0,
        activeTenants: data.platform_stats?.active_organizations || 0,
        totalUsers: data.platform_stats?.total_users || 0,
        totalCourses: data.platform_stats?.total_courses || 0,
        totalRevenue: data.platform_stats?.total_revenue || 0,
        totalEnrollments: data.platform_stats?.total_enrollments || 0,
        totalTeachers: data.platform_stats?.total_teachers || 0,
        approvedTeachers: data.platform_stats?.approved_teachers || 0,
        publishedCourses: data.platform_stats?.published_courses || 0,
        activeEnrollments: data.platform_stats?.active_enrollments || 0,
        completedEnrollments: data.platform_stats?.completed_enrollments || 0
      },
      tenantStats: (data.organization_performance || []).map((org: any) => ({
        id: org.id,
        name: org.name,
        subdomain: org.subdomain,
        subscriptionPlan: org.subscription_plan,
        userCount: org.total_users,
        courseCount: org.total_courses,
        revenue: org.total_revenue
      })),
      systemMetrics: {
        serverLoad: 0, // Backend doesn't provide this yet
        memoryUsage: 0,
        diskUsage: 0,
        apiCalls: 0
      },
      revenueByTenant: (data.organization_performance || []).map((org: any) => ({
        tenantId: org.id,
        tenantName: org.name,
        revenue: org.total_revenue,
        growth: 0 // Backend doesn't provide growth calculation yet
      })),
      globalActivity: [], // Backend doesn't provide this yet
      subscriptionStats: data.subscription_breakdown || {
        basic: 0,
        pro: 0,
        enterprise: 0
      }
    }),
    cacheKey: 'superadmin-dashboard',
    // Cache for 2 minutes for super admin data
  })

  // Computed properties for current user's dashboard
  const currentDashboardData = computed(() => {
    if (user.value?.is_superuser) {
      return superAdminData.data.value
    } else if (user.value?.is_staff) {
      return adminData.data.value
    } else if (user.value?.is_teacher) {
      return teacherData.data.value
    } else {
      return studentData.data.value
    }
  })

  const currentDashboardLoading = computed(() => {
    if (user.value?.is_superuser) {
      return superAdminData.loading.value
    } else if (user.value?.is_staff) {
      return adminData.loading.value
    } else if (user.value?.is_teacher) {
      return teacherData.loading.value
    } else {
      return studentData.loading.value
    }
  })

  const currentDashboardError = computed(() => {
    if (user.value?.is_superuser) {
      return superAdminData.error.value
    } else if (user.value?.is_staff) {
      return adminData.error.value
    } else if (user.value?.is_teacher) {
      return teacherData.error.value
    } else {
      return studentData.error.value
    }
  })

  const refreshCurrentDashboard = async () => {
    if (user.value?.is_superuser) {
      await superAdminData.refresh()
    } else if (user.value?.is_staff) {
      await adminData.refresh()
    } else if (user.value?.is_teacher) {
      await teacherData.refresh()
    } else {
      await studentData.refresh()
    }
  }

  return {
    // Individual dashboard data
    studentData,
    teacherData,
    adminData,
    superAdminData,
    
    // Current user's dashboard
    currentDashboardData,
    currentDashboardLoading,
    currentDashboardError,
    refreshCurrentDashboard,
    
    // Utility methods
    refreshAll: async () => {
      await Promise.all([
        studentData.refresh(),
        teacherData.refresh(),
        adminData.refresh(),
        superAdminData.refresh()
      ])
    }
  }
}