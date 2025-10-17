// Fallback data service for when API endpoints don't exist yet
// This provides realistic sample data so components can display meaningful content

export const fallbackData = {
  // Platform Analytics
  '/analytics/platform-overview/': {
    totalUsers: 1247,
    totalOrganizations: 23,
    totalCourses: 156,
    totalRevenue: 45230,
    userGrowth: 12.5,
    orgGrowth: 8.3,
    courseGrowth: 15.7,
    revenueGrowth: 22.1,
    avgResponseTime: 145,
    uptime: 99.8,
    dailyActiveUsers: 892,
    avgSessionDuration: 24,
    userGrowthTrend: [
      { month: 'Jan', count: 120 },
      { month: 'Feb', count: 145 },
      { month: 'Mar', count: 180 },
      { month: 'Apr', count: 210 },
      { month: 'May', count: 250 },
      { month: 'Jun', count: 290 }
    ],
    revenueTrend: [
      { month: 'Jan', amount: 8500 },
      { month: 'Feb', amount: 9200 },
      { month: 'Mar', amount: 10800 },
      { month: 'Apr', amount: 12100 },
      { month: 'May', amount: 13500 },
      { month: 'Jun', amount: 15200 }
    ],
    topOrganizations: [
      { id: 1, name: 'Tech Academy', subdomain: 'tech-academy', userCount: 245, courseCount: 32, revenue: 12500, growth: 18.5 },
      { id: 2, name: 'Business School', subdomain: 'biz-school', userCount: 189, courseCount: 28, revenue: 9800, growth: 15.2 },
      { id: 3, name: 'Design Institute', subdomain: 'design-inst', userCount: 156, courseCount: 24, revenue: 8200, growth: 12.8 }
    ]
  },

  // Users
  '/users/': {
    results: [
      {
        id: 1,
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        role: 'student',
        is_active: true,
        date_joined: '2024-01-15T10:30:00Z',
        last_login: '2024-02-10T14:20:00Z',
        avatar: null
      },
      {
        id: 2,
        first_name: 'Jane',
        last_name: 'Smith',
        email: 'jane.smith@example.com',
        role: 'teacher',
        is_active: true,
        is_approved_teacher: true,
        date_joined: '2024-01-10T09:15:00Z',
        last_login: '2024-02-10T16:45:00Z',
        avatar: null
      },
      {
        id: 3,
        first_name: 'Admin',
        last_name: 'User',
        email: 'admin@example.com',
        role: 'admin',
        is_active: true,
        is_staff: true,
        date_joined: '2024-01-01T08:00:00Z',
        last_login: '2024-02-10T18:30:00Z',
        avatar: null
      }
    ],
    count: 3,
    next: null,
    previous: null
  },

  // Courses
  '/courses/': {
    results: [
      {
        id: 1,
        title: 'Introduction to Web Development',
        description: 'Learn the basics of HTML, CSS, and JavaScript',
        instructor: { id: 2, first_name: 'Jane', last_name: 'Smith' },
        thumbnail: null,
        price: 99.99,
        status: 'published',
        category: 'technology',
        difficulty_level: 'beginner',
        total_lessons: 24,
        total_duration: 1440,
        enrollment_count: 156,
        average_rating: 4.5,
        created_at: '2024-01-20T10:00:00Z'
      },
      {
        id: 2,
        title: 'Advanced React Development',
        description: 'Master React hooks, context, and advanced patterns',
        instructor: { id: 2, first_name: 'Jane', last_name: 'Smith' },
        thumbnail: null,
        price: 149.99,
        status: 'published',
        category: 'technology',
        difficulty_level: 'advanced',
        total_lessons: 32,
        total_duration: 1920,
        enrollment_count: 89,
        average_rating: 4.8,
        created_at: '2024-01-25T14:30:00Z'
      }
    ],
    count: 2,
    next: null,
    previous: null
  },

  // Enrollments
  '/enrollments/': {
    results: [
      {
        id: 1,
        title: 'Introduction to Web Development',
        instructor: { first_name: 'Jane', last_name: 'Smith' },
        thumbnail: null,
        progress_percentage: 65,
        enrollment_date: '2024-01-22T10:00:00Z',
        last_accessed: '2024-02-08T15:30:00Z',
        total_lessons: 24,
        total_duration: 1440,
        difficulty_level: 'beginner',
        certificate_earned: false
      },
      {
        id: 2,
        title: 'Advanced React Development',
        instructor: { first_name: 'Jane', last_name: 'Smith' },
        thumbnail: null,
        progress_percentage: 100,
        enrollment_date: '2024-01-28T09:15:00Z',
        last_accessed: '2024-02-05T12:00:00Z',
        total_lessons: 32,
        total_duration: 1920,
        difficulty_level: 'advanced',
        certificate_earned: true
      }
    ],
    count: 2,
    next: null,
    previous: null
  },

  // Live Classes
  '/live-classes/': {
    results: [
      {
        id: 1,
        title: 'React Hooks Deep Dive',
        course_title: 'Advanced React Development',
        instructor_name: 'Jane Smith',
        description: 'Comprehensive overview of React hooks and their use cases',
        scheduled_at: '2024-02-15T15:00:00Z',
        duration_minutes: 90,
        status: 'scheduled',
        join_url: 'https://zoom.us/j/123456789',
        recording_url: null,
        has_materials: true,
        attended: false
      },
      {
        id: 2,
        title: 'JavaScript Fundamentals',
        course_title: 'Introduction to Web Development',
        instructor_name: 'Jane Smith',
        description: 'Core JavaScript concepts and best practices',
        scheduled_at: '2024-02-08T14:00:00Z',
        duration_minutes: 60,
        status: 'completed',
        join_url: null,
        recording_url: 'https://zoom.us/rec/123456789',
        has_materials: true,
        attended: true,
        attendance_duration: 58
      }
    ],
    count: 2,
    next: null,
    previous: null
  },

  // Organizations
  '/organizations/': {
    results: [
      {
        id: 1,
        name: 'Tech Academy',
        domain: 'tech-academy.edurise.com',
        logo: null,
        created_at: '2024-01-01T00:00:00Z',
        is_active: true,
        user_count: 245,
        course_count: 32,
        subscription_plan: 'premium'
      },
      {
        id: 2,
        name: 'Business School',
        domain: 'biz-school.edurise.com',
        logo: null,
        created_at: '2024-01-05T00:00:00Z',
        is_active: true,
        user_count: 189,
        course_count: 28,
        subscription_plan: 'standard'
      }
    ],
    count: 2,
    next: null,
    previous: null
  },

  // Analytics
  '/analytics/': {
    total_students: 156,
    total_courses: 12,
    total_revenue: 15420,
    completion_rate: 78.5,
    monthly_growth: 12.3,
    popular_courses: [
      { name: 'Web Development', enrollments: 89 },
      { name: 'React Advanced', enrollments: 67 }
    ],
    revenue_trend: [
      { month: 'Jan', amount: 2500 },
      { month: 'Feb', amount: 3200 },
      { month: 'Mar', amount: 2800 },
      { month: 'Apr', amount: 3500 },
      { month: 'May', amount: 4200 },
      { month: 'Jun', amount: 3800 }
    ]
  },

  // Security Overview
  '/security/overview/': {
    active_threats: 0,
    failed_logins_24h: 3,
    active_sessions: 45,
    security_score: 92,
    active_alerts: 1,
    failed_logins_today: 3,
    active_users: 45
  },

  // System Status
  '/system/status/': {
    server_status: 'healthy',
    database_status: 'healthy',
    storage_used: 75,
    storage_total: 100,
    memory_used: 4.2,
    memory_total: 8.0,
    uptime: '15 days, 6 hours',
    db_connections: 25
  },

  // Teacher Approvals
  '/teacher-approvals/': {
    results: [
      {
        id: 1,
        user: {
          id: 4,
          first_name: 'Michael',
          last_name: 'Johnson',
          email: 'michael.j@example.com'
        },
        qualifications: 'PhD in Computer Science, 10 years teaching experience',
        experience: '10 years of university teaching and industry experience',
        motivation: 'Passionate about sharing knowledge and helping students succeed',
        status: 'pending',
        submitted_at: '2024-02-05T10:30:00Z',
        documents: []
      }
    ],
    count: 1,
    next: null,
    previous: null
  },

  // Payments
  '/payments/': {
    results: [
      {
        id: 1,
        amount: 99.99,
        currency: 'USD',
        status: 'completed',
        course: { title: 'Introduction to Web Development' },
        student: { first_name: 'John', last_name: 'Doe' },
        created_at: '2024-01-22T10:00:00Z',
        payment_method: 'credit_card'
      },
      {
        id: 2,
        amount: 149.99,
        currency: 'USD',
        status: 'completed',
        course: { title: 'Advanced React Development' },
        student: { first_name: 'John', last_name: 'Doe' },
        created_at: '2024-01-28T09:15:00Z',
        payment_method: 'paypal'
      }
    ],
    count: 2,
    next: null,
    previous: null
  }
}

// Helper function to get fallback data for an endpoint
export const getFallbackData = (endpoint: string) => {
  // Normalize endpoint (remove query parameters and trailing slashes)
  const normalizedEndpoint = endpoint.split('?')[0].replace(/\/$/, '') + '/'
  
  return fallbackData[normalizedEndpoint] || null
}

// Check if endpoint has fallback data available
export const hasFallbackData = (endpoint: string): boolean => {
  const normalizedEndpoint = endpoint.split('?')[0].replace(/\/$/, '') + '/'
  return normalizedEndpoint in fallbackData
}

export default fallbackData