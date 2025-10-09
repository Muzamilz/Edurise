import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authGuard, guestGuard, teacherGuard } from '@/middleware/auth'

const routes: RouteRecordRaw[] = [
  // Public routes
  {
    path: '/',
    name: 'home',
    component: () => import('../views/LandingView.vue'),
    meta: { title: 'Edurise - Learning Management System' }
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
      }
    ]
  },

  // Teacher routes
  {
    path: '/teacher',
    beforeEnter: teacherGuard,
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
        meta: { title: 'Create Course - Edurise', requiresAuth: true, requiresTeacher: true }
      },
      {
        path: 'courses/:id/edit',
        name: 'teacher-course-edit',
        component: () => import('../views/teacher/CourseEditView.vue'),
        meta: { title: 'Edit Course - Edurise', requiresAuth: true, requiresTeacher: true }
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