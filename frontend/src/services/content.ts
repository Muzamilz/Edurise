import { api } from './api'

export interface Testimonial {
  id: number
  user_name: string
  content: string
  rating: number
  position: string
  company: string
  course_title?: string
  created_at: string
}

export interface TeamMember {
  id: number
  name: string
  role: string
  department: string
  bio: string
  profile_image?: string
  linkedin_url?: string
  twitter_url?: string
}

export interface Announcement {
  id: number
  title: string
  content: string
  category: string
  priority: string
  publish_at: string
  expire_at?: string
  featured: boolean
  author_name: string
  tags: string
  created_at: string
}

export interface FAQ {
  id: number
  question: string
  answer: string
  category: string
  view_count: number
  helpful_count: number
  not_helpful_count: number
  helpfulness_ratio: number
}

export interface ContactInfo {
  company_name: string
  tagline: string
  description: string
  email: string
  phone: string
  address: string
  business_hours: string
  facebook_url: string
  twitter_url: string
  linkedin_url: string
  instagram_url: string
  youtube_url: string
  blog_url: string
  support_url: string
  privacy_policy_url: string
  terms_of_service_url: string
}

export const contentService = {
  // Testimonials
  async getTestimonials(params?: { featured?: boolean }) {
    const response = await api.get('/content/testimonials/', { params })
    return response.data
  },

  async getFeaturedTestimonials() {
    const response = await api.get('/content/testimonials/featured/')
    return response.data
  },

  async createTestimonial(data: {
    content: string
    rating: number
    position?: string
    company?: string
    course?: number
  }) {
    const response = await api.post('/content/testimonials/', data)
    return response.data
  },

  // Team Members
  async getTeamMembers(params?: { department?: string }) {
    const response = await api.get('/content/team-members/', { params })
    return response.data
  },

  async getTeamMembersByDepartment() {
    const response = await api.get('/content/team-members/by_department/')
    return response.data
  },

  // Announcements
  async getAnnouncements(params?: { 
    category?: string
    featured?: boolean 
  }) {
    const response = await api.get('/content/announcements/', { params })
    return response.data
  },

  async getFeaturedAnnouncements() {
    const response = await api.get('/content/announcements/featured/')
    return response.data
  },

  async getHomepageAnnouncements() {
    const response = await api.get('/content/announcements/homepage/')
    return response.data
  },

  // FAQs
  async getFAQs(params?: { 
    category?: string
    search?: string 
  }) {
    const response = await api.get('/content/faqs/', { params })
    return response.data
  },

  async getFeaturedFAQs() {
    const response = await api.get('/content/faqs/featured/')
    return response.data
  },

  async getFAQsByCategory() {
    const response = await api.get('/content/faqs/by_category/')
    return response.data
  },

  async submitFAQFeedback(faqId: number, helpful: boolean) {
    const response = await api.post(`/content/faqs/${faqId}/feedback/`, { helpful })
    return response.data
  },

  // Contact Info
  async getContactInfo() {
    const response = await api.get('/content/contact-info/active/')
    return response.data
  }
}