import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authGuard, guestGuard, teacherGuard, adminGuard, superAdminGuard } from '@/middleware/auth'

const routes: RouteRecordRaw[] = [
  // Public routes
  {
    path: '/',
    name: 'home',
    component: () => import('../views/LandingView.vue'),
    meta: { title: 'Edurise - Learning Management System' }
  },

  // About Us routes
  {
    path: '/about',
    name: 'about',
    component: () => import('../views/AboutView.vue'),
    meta: { title: 'About Us - Edurise' }
  },
  {
    path: '/vision-mission',
    name: 'vision-mission',
    component: () => import('../views/VisionMissionView.vue'),
    meta: { title: 'Vision Mission Goals Values - Edurise' }
  },
  {
    path: '/our-team',
    name: 'our-team',
    component: () => import('../views/OurTeamView.vue'),
    meta: { title: 'Our Team - Edurise' }
  },
  {
    path: '/testimonies',
    name: 'testimonies',
    component: () => import('../views/TestimoniesView.vue'),
    meta: { title: 'Testimonies - Edurise' }
  },

  // Announcements
  {
    path: '/announcements',
    name: 'announcements',
    component: () => import('../views/AnnouncementsView.vue'),
    meta: { title: 'Announcements - Edurise' }
  },

  // Join Us routes
  {
    path: '/become-teacher',
    name: 'become-teacher',
    component: () => import('../views/BecomeTeacherView.vue'),
    meta: { title: 'Become a Teacher - Edurise' }
  },
  {
    path: '/become-student',
    name: 'become-student',
    component: () => import('../views/BecomeStudentView.vue'),
    meta: { title: 'Become a Student - Edurise' }
  },

  // Guidelines routes
  {
    path: '/payment-methodologies',
    name: 'payment-methodologies',
    component: () => import('../views/PaymentMethodologiesView.vue'),
    meta: { title: 'Payment Methodologies - Edurise' }
  },
  {
    path: '/student-guidelines',
    name: 'student-guidelines',
    component: () => import('../views/StudentGuidelinesView.vue'),
    meta: { title: 'Student Guidelines - Edurise' }
  },

  // FAQs and Contact
  {
    path: '/faqs',
    name: 'faqs',
    component: () => import('../views/FAQsView.vue'),
    meta: { title: 'FAQs - Edurise' }
  },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('../views/ContactView.vue'),
    meta: { title: 'Contact Us - Edurise' }
  },

  // Authentication routes
  {
    path: '/auth',
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import('../views/auth/LoginView.vue'),
        beforeEnter: guestGuard,
        meta: { title: 'Sign In - Edurise' }
      },
      {
        path: 'register',
        name: 'register',
        component: () => import('../views/auth/RegisterView.vue'),
        beforeEnter: guestGuard,
        meta: { title: 'Sign Up - Edurise' }
      },
      {
        path: 'forgot-password',
        name: 'forgot-password',
        component: () => import('../views/auth/ForgotPasswordView.vue'),
        beforeEnter: guestGuard,
        meta: { title: 'Forgot Password - Edurise' }
      },
      {
        path: 'reset-password',
        name: 'reset-password',
        component: () => import('../views/auth/ResetPasswordView.vue'),
        beforeEnter: guestGuard,
        meta: { title: 'Reset Password - Edurise' }
      }
    ]
  },

  // Protected routes
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue'),
    beforeEnter: authGuard,
    meta: { title: 'Dashboard - Edurise', requiresAuth: true }
  },

  // Profile route
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue'),
    beforeEnter: authGuard,
    meta: { title: 'Profile - Edurise', requiresAuth: true }
  },

  // Course routes
  {
    path: '/courses',
    children: [
      {
        path: '',
        name: 'courses',
        component: () => import('../views/courses/CoursesView.vue'),
        meta: { title: 'Courses - Edurise' }
      },
      {
        path: ':id',
        name: 'course-detail',
        component: () => import('../views/courses/CourseDetailView.vue'),
        meta: { title: 'Course Details - Edurise' }
      },
      {
        path: ':id/learn',
        name: 'course-learn',
        component: () => import('../views/courses/CourseLearningView.vue'),
        beforeEnter: authGuard,
        meta: { title: 'Learning - Edurise', requiresAuth: true }
      }
    ]
  },

  // Student routes
  {
    path: '/student',
    beforeEnter: authGuard,
    children: [
      {
        path: 'my-courses',
        name: 'student-my-courses',
        component: () => import('../views/student/MyCoursesView.vue'),
        meta: { title: 'My Courses - Edurise', requiresAuth: true }
      },
      {
        path: 'live-classes',
        name: 'student-live-classes',
        component: () => import('../views/student/LiveClassesView.vue'),
        meta: { title: 'My Live Classes - Edurise', requiresAuth: true }
      },
      {
        path: 'certificates',
        name: 'student-certificates',
        component: () => import('../views/student/CertificatesView.vue'),
        meta: { title: 'My Certificates - Edurise', requiresAuth: true }
      },
      {
        path: 'progress',
        name: 'student-progress',
        component: () => import('../views/student/ProgressView.vue'),
        meta: { title: 'Learning Progress - Edurise', requiresAuth: true }
      },
      {
        path: 'wishlist',
        name: 'student-wishlist',
        component: () => import('../views/student/WishlistView.vue'),
        meta: { title: 'Wishlist - Edurise', requiresAuth: true }
      }
    ]
  },

  // Dashboard sub-routes (for student dashboard links)
  {
    path: '/dashboard',
    beforeEnter: authGuard,
    children: [
      {
        path: 'my-courses',
        name: 'dashboard-my-courses',
        component: () => import('../views/student/MyCoursesView.vue'),
        meta: { title: 'My Courses - Edurise', requiresAuth: true }
      }
    ]
  },

  // Teacher routes
  {
    path: '/teacher',
    beforeEnter: authGuard, // Allow all authenticated users to access teacher routes (approval check is in components)
    children: [
      {
        path: 'courses',
        name: 'teacher-courses',
        component: () => import('../views/teacher/CoursesView.vue'),
        meta: { title: 'My Courses - Edurise', requiresAuth: true, requiresTeacher: true }
      },
      {
        path: 'courses/create',
        name: 'teacher-course-create',
        component: () => import('../views/teacher/CourseCreateView.vue'),
        beforeEnter: teacherGuard, // Only approved teachers can create courses
        meta: { title: 'Create Course - Edurise', requiresAuth: true, requiresTeacher: true }
      },
      {
        path: 'courses/:id/edit',
        name: 'teacher-course-edit',
        component: () => import('../views/teacher/CourseEditView.vue'),
        beforeEnter: teacherGuard, // Only approved teachers can edit courses
        meta: { title: 'Edit Course - Edurise', requiresAuth: true, requiresTeacher: true }
      },
      {
        path: 'application-status',
        name: 'teacher-application-status',
        component: () => import('../views/teacher/ApplicationStatusView.vue'),
        meta: { title: 'Application Status - Edurise', requiresAuth: true }
      },
      {
        path: 'live-classes',
        name: 'teacher-live-classes',
        component: () => import('../views/teacher/LiveClassesView.vue'),
        beforeEnter: teacherGuard,
        meta: { title: 'My Live Classes - Edurise', requiresAuth: true, requiresTeacher: true }
      },
      {
        path: 'students',
        name: 'teacher-students',
        component: () => import('../views/teacher/StudentsView.vue'),
        beforeEnter: teacherGuard,
        meta: { title: 'My Students - Edurise', requiresAuth: true, requiresTeacher: true }
      },
      {
        path: 'analytics',
        name: 'teacher-analytics',
        component: () => import('../views/teacher/AnalyticsView.vue'),
        beforeEnter: teacherGuard,
        meta: { title: 'Teaching Analytics - Edurise', requiresAuth: true, requiresTeacher: true }
      },
      {
        path: 'earnings',
        name: 'teacher-earnings',
        component: () => import('../views/teacher/EarningsView.vue'),
        beforeEnter: teacherGuard,
        meta: { title: 'Earnings - Edurise', requiresAuth: true, requiresTeacher: true }
      },
      {
        path: 'profile',
        name: 'teacher-profile',
        component: () => import('../views/teacher/ProfileView.vue'),
        meta: { title: 'Teacher Profile - Edurise', requiresAuth: true }
      },
      {
        path: 'resources',
        name: 'teacher-resources',
        component: () => import('../views/teacher/ResourcesView.vue'),
        meta: { title: 'Teaching Resources - Edurise', requiresAuth: true }
      }
    ]
  },

  // Live Classes routes
  {
    path: '/live-classes',
    beforeEnter: authGuard,
    children: [
      {
        path: '',
        name: 'live-classes',
        component: () => import('../views/live-classes/LiveClassesView.vue'),
        meta: { title: 'Live Classes - Edurise', requiresAuth: true }
      },
      {
        path: ':id',
        name: 'live-class-detail',
        component: () => import('../components/live-classes/LiveClassJoinInterface.vue'),
        meta: { title: 'Join Class - Edurise', requiresAuth: true }
      },
      {
        path: ':id/attendance',
        name: 'live-class-attendance',
        component: () => import('../components/live-classes/AttendanceTrackingDashboard.vue'),
        beforeEnter: teacherGuard,
        meta: { title: 'Class Attendance - Edurise', requiresAuth: true, requiresTeacher: true }
      }
    ]
  },

  // Admin routes
  {
    path: '/admin',
    beforeEnter: adminGuard,
    children: [
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('../views/admin/UsersView.vue'),
        meta: { title: 'User Management - Edurise', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'teachers/pending',
        name: 'admin-teachers-pending',
        component: () => import('../views/admin/TeacherApprovalsView.vue'),
        meta: { title: 'Teacher Approvals - Edurise', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'teachers/:id',
        name: 'admin-teacher-detail',
        component: () => import('../views/admin/TeacherDetailView.vue'),
        meta: { title: 'Teacher Details - Edurise', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'courses',
        name: 'admin-courses',
        component: () => import('../views/admin/CoursesView.vue'),
        meta: { title: 'Course Management - Edurise', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'content-moderation',
        name: 'admin-content-moderation',
        component: () => import('../views/admin/ContentModerationView.vue'),
        meta: { title: 'Content Moderation - Edurise', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'analytics',
        name: 'admin-analytics',
        component: () => import('../views/admin/AnalyticsView.vue'),
        meta: { title: 'Platform Analytics - Edurise', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'financial',
        name: 'admin-financial',
        component: () => import('../views/admin/FinancialView.vue'),
        meta: { title: 'Financial Reports - Edurise', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'organization',
        name: 'admin-organization',
        component: () => import('../views/admin/OrganizationView.vue'),
        meta: { title: 'Organization Settings - Edurise', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'system',
        name: 'admin-system',
        component: () => import('../views/admin/SystemView.vue'),
        meta: { title: 'System Settings - Edurise', requiresAuth: true, requiresAdmin: true }
      }
    ]
  },

  // Super Admin routes
  {
    path: '/super-admin',
    beforeEnter: superAdminGuard,
    children: [
      {
        path: 'organizations',
        name: 'super-admin-organizations',
        component: () => import('../views/super-admin/OrganizationsView.vue'),
        meta: { title: 'Manage Organizations - Edurise', requiresAuth: true, requiresSuperAdmin: true }
      },
      {
        path: 'organizations/:id',
        name: 'super-admin-organization-detail',
        component: () => import('../views/super-admin/OrganizationDetailView.vue'),
        meta: { title: 'Organization Details - Edurise', requiresAuth: true, requiresSuperAdmin: true }
      },
      {
        path: 'teachers/global',
        name: 'super-admin-teachers-global',
        component: () => import('../views/super-admin/GlobalTeachersView.vue'),
        meta: { title: 'Global Teacher Approvals - Edurise', requiresAuth: true, requiresSuperAdmin: true }
      },
      {
        path: 'teachers/:id',
        name: 'super-admin-teacher-detail',
        component: () => import('../views/super-admin/TeacherDetailView.vue'),
        meta: { title: 'Teacher Details - Edurise', requiresAuth: true, requiresSuperAdmin: true }
      },
      {
        path: 'users',
        name: 'super-admin-users',
        component: () => import('../views/super-admin/UsersView.vue'),
        meta: { title: 'All Users - Edurise', requiresAuth: true, requiresSuperAdmin: true }
      },
      {
        path: 'courses/global',
        name: 'super-admin-courses-global',
        component: () => import('../views/super-admin/GlobalCoursesView.vue'),
        meta: { title: 'All Courses - Edurise', requiresAuth: true, requiresSuperAdmin: true }
      },
      {
        path: 'analytics/platform',
        name: 'super-admin-analytics-platform',
        component: () => import('../views/super-admin/PlatformAnalyticsView.vue'),
        meta: { title: 'Platform Analytics - Edurise', requiresAuth: true, requiresSuperAdmin: true }
      },
      {
        path: 'financial/global',
        name: 'super-admin-financial-global',
        component: () => import('../views/super-admin/GlobalFinancialView.vue'),
        meta: { title: 'Global Financials - Edurise', requiresAuth: true, requiresSuperAdmin: true }
      },
      {
        path: 'security',
        name: 'super-admin-security',
        component: () => import('../views/super-admin/SecurityView.vue'),
        meta: { title: 'Security Center - Edurise', requiresAuth: true, requiresSuperAdmin: true }
      },
      {
        path: 'system',
        name: 'super-admin-system',
        component: () => import('../views/super-admin/SystemView.vue'),
        meta: { title: 'System Administration - Edurise', requiresAuth: true, requiresSuperAdmin: true }
      }
    ]
  },



  // Error routes
  {
    path: '/unauthorized',
    name: 'unauthorized',
    component: () => import('../views/UnauthorizedView.vue'),
    meta: { title: 'Unauthorized - Edurise' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFoundView.vue'),
    meta: { title: 'Page Not Found - Edurise' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Global navigation guard for authentication and page titles
router.beforeEach((to, _from, next) => {
  // Initialize auth store if not already done
  const authStore = useAuthStore()
  if (!authStore.user && localStorage.getItem('access_token')) {
    authStore.initializeAuth()
  }

  // Set page title
  if (to.meta.title) {
    document.title = to.meta.title as string
  }
  
  next()
})

export default router