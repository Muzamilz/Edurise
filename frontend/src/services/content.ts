import { api } from './api'
import type { PaginatedResponse } from '../types/api'

// ===== Type Definitions =====

export interface Testimonial {
  id: number
  user_name: string
  user?: number
  content: string
  rating: number
  position: string
  company: string
  course?: number
  course_title?: string
  status: 'pending' | 'published' | 'rejected'
  featured: boolean
  approved_by?: number
  approved_at?: string
  created_at: string
  updated_at: string
}

export interface TestimonialCreate {
  content: string
  rating: number
  position?: string
  company?: string
  course?: number
}

export interface TeamMember {
  id: number
  name: string
  role: string
  department: 'leadership' | 'engineering' | 'design' | 'marketing' | 'support' | 'other'
  bio: string
  profile_image?: string
  linkedin_url?: string
  twitter_url?: string
  github_url?: string
  website_url?: string
  display_order: number
  status: 'draft' | 'published'
  featured: boolean
  created_at: string
  updated_at: string
}

export interface Announcement {
  id: number
  title: string
  content: string
  category: 'general' | 'maintenance' | 'feature' | 'event' | 'urgent'
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: 'draft' | 'published' | 'archived'
  publish_at: string
  expire_at?: string
  featured: boolean
  show_on_homepage: boolean
  author: number
  author_name: string
  tags: string
  created_at: string
  updated_at: string
}

export interface FAQ {
  id: number
  question: string
  answer: string
  category: 'general' | 'account' | 'courses' | 'payments' | 'technical' | 'other'
  keywords: string
  status: 'draft' | 'published'
  featured: boolean
  display_order: number
  view_count: number
  helpful_count: number
  not_helpful_count: number
  helpfulness_ratio: number
  created_at: string
  updated_at: string
}

export interface ContactInfo {
  id: number
  company_name: string
  tagline: string
  description: string
  email: string
  phone: string
  address: string
  city: string
  state: string
  country: string
  postal_code: string
  business_hours: string
  facebook_url?: string
  twitter_url?: string
  linkedin_url?: string
  instagram_url?: string
  youtube_url?: string
  blog_url?: string
  support_url?: string
  privacy_policy_url?: string
  terms_of_service_url?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface FAQFeedback {
  helpful: boolean
  comment?: string
}

// ===== Content Service =====

export class ContentService {
  // ===== Testimonials =====
  
  /**
   * Get all testimonials
   * @param params - Filter parameters
   * @returns Paginated list of testimonials
   */
  static async getTestimonials(params?: {
    featured?: boolean
    status?: string
    rating?: number
    search?: string
    page?: number
  }): Promise<PaginatedResponse<Testimonial>> {
    const response = await api.get<PaginatedResponse<Testimonial>>('/testimonials/', { params })
    return response.data.data
  }

  /**
   * Get a single testimonial
   * @param id - Testimonial ID
   * @returns Testimonial details
   */
  static async getTestimonial(id: number): Promise<Testimonial> {
    const response = await api.get<Testimonial>(`/testimonials/${id}/`)
    return response.data.data
  }

  /**
   * Get featured testimonials
   * @returns List of featured testimonials
   */
  static async getFeaturedTestimonials(): Promise<Testimonial[]> {
    const response = await api.get<Testimonial[]>('/testimonials/featured/')
    return response.data.data
  }

  /**
   * Create a new testimonial
   * @param data - Testimonial data
   * @returns Created testimonial
   */
  static async createTestimonial(data: TestimonialCreate): Promise<Testimonial> {
    const response = await api.post<Testimonial>('/testimonials/', data)
    return response.data.data
  }

  /**
   * Update a testimonial
   * @param id - Testimonial ID
   * @param data - Updated testimonial data
   * @returns Updated testimonial
   */
  static async updateTestimonial(id: number, data: Partial<Testimonial>): Promise<Testimonial> {
    const response = await api.patch<Testimonial>(`/testimonials/${id}/`, data)
    return response.data.data
  }

  /**
   * Delete a testimonial
   * @param id - Testimonial ID
   */
  static async deleteTestimonial(id: number): Promise<void> {
    await api.delete(`/testimonials/${id}/`)
  }

  /**
   * Approve a testimonial (admin only)
   * @param id - Testimonial ID
   * @returns Approved testimonial
   */
  static async approveTestimonial(id: number): Promise<Testimonial> {
    const response = await api.post<Testimonial>(`/testimonials/${id}/approve/`)
    return response.data.data
  }

  /**
   * Reject a testimonial (admin only)
   * @param id - Testimonial ID
   * @returns Rejected testimonial
   */
  static async rejectTestimonial(id: number): Promise<Testimonial> {
    const response = await api.post<Testimonial>(`/testimonials/${id}/reject/`)
    return response.data.data
  }

  // ===== Team Members =====
  
  /**
   * Get all team members
   * @param params - Filter parameters
   * @returns Paginated list of team members
   */
  static async getTeamMembers(params?: {
    department?: string
    status?: string
    featured?: boolean
    search?: string
    page?: number
  }): Promise<PaginatedResponse<TeamMember>> {
    const response = await api.get<PaginatedResponse<TeamMember>>('/team-members/', { params })
    return response.data.data
  }

  /**
   * Get a single team member
   * @param id - Team member ID
   * @returns Team member details
   */
  static async getTeamMember(id: number): Promise<TeamMember> {
    const response = await api.get<TeamMember>(`/team-members/${id}/`)
    return response.data.data
  }

  /**
   * Get team members grouped by department
   * @returns Team members organized by department
   */
  static async getTeamMembersByDepartment(): Promise<Record<string, TeamMember[]>> {
    const response = await api.get<Record<string, TeamMember[]>>('/team-members/by_department/')
    return response.data.data
  }

  /**
   * Create a new team member (admin only)
   * @param data - Team member data
   * @returns Created team member
   */
  static async createTeamMember(data: Partial<TeamMember>): Promise<TeamMember> {
    const response = await api.post<TeamMember>('/team-members/', data)
    return response.data.data
  }

  /**
   * Update a team member (admin only)
   * @param id - Team member ID
   * @param data - Updated team member data
   * @returns Updated team member
   */
  static async updateTeamMember(id: number, data: Partial<TeamMember>): Promise<TeamMember> {
    const response = await api.patch<TeamMember>(`/team-members/${id}/`, data)
    return response.data.data
  }

  /**
   * Delete a team member (admin only)
   * @param id - Team member ID
   */
  static async deleteTeamMember(id: number): Promise<void> {
    await api.delete(`/team-members/${id}/`)
  }

  // ===== Announcements =====
  
  /**
   * Get all announcements
   * @param params - Filter parameters
   * @returns Paginated list of announcements
   */
  static async getAnnouncements(params?: {
    category?: string
    priority?: string
    status?: string
    featured?: boolean
    search?: string
    page?: number
  }): Promise<PaginatedResponse<Announcement>> {
    const response = await api.get<PaginatedResponse<Announcement>>('/announcements/', { params })
    return response.data.data
  }

  /**
   * Get a single announcement
   * @param id - Announcement ID
   * @returns Announcement details
   */
  static async getAnnouncement(id: number): Promise<Announcement> {
    const response = await api.get<Announcement>(`/announcements/${id}/`)
    return response.data.data
  }

  /**
   * Get featured announcements
   * @returns List of featured announcements
   */
  static async getFeaturedAnnouncements(): Promise<Announcement[]> {
    const response = await api.get<Announcement[]>('/announcements/featured/')
    return response.data.data
  }

  /**
   * Get homepage announcements
   * @returns List of announcements for homepage
   */
  static async getHomepageAnnouncements(): Promise<Announcement[]> {
    const response = await api.get<Announcement[]>('/announcements/homepage/')
    return response.data.data
  }

  /**
   * Create a new announcement (admin only)
   * @param data - Announcement data
   * @returns Created announcement
   */
  static async createAnnouncement(data: Partial<Announcement>): Promise<Announcement> {
    const response = await api.post<Announcement>('/announcements/', data)
    return response.data.data
  }

  /**
   * Update an announcement (admin only)
   * @param id - Announcement ID
   * @param data - Updated announcement data
   * @returns Updated announcement
   */
  static async updateAnnouncement(id: number, data: Partial<Announcement>): Promise<Announcement> {
    const response = await api.patch<Announcement>(`/announcements/${id}/`, data)
    return response.data.data
  }

  /**
   * Delete an announcement (admin only)
   * @param id - Announcement ID
   */
  static async deleteAnnouncement(id: number): Promise<void> {
    await api.delete(`/announcements/${id}/`)
  }

  // ===== FAQs =====
  
  /**
   * Get all FAQs
   * @param params - Filter parameters
   * @returns Paginated list of FAQs
   */
  static async getFAQs(params?: {
    category?: string
    status?: string
    featured?: boolean
    search?: string
    page?: number
  }): Promise<PaginatedResponse<FAQ>> {
    const response = await api.get<PaginatedResponse<FAQ>>('/faqs/', { params })
    return response.data.data
  }

  /**
   * Get a single FAQ
   * @param id - FAQ ID
   * @returns FAQ details
   */
  static async getFAQ(id: number): Promise<FAQ> {
    const response = await api.get<FAQ>(`/faqs/${id}/`)
    return response.data.data
  }

  /**
   * Get featured FAQs
   * @returns List of featured FAQs
   */
  static async getFeaturedFAQs(): Promise<FAQ[]> {
    const response = await api.get<FAQ[]>('/faqs/featured/')
    return response.data.data
  }

  /**
   * Get FAQs grouped by category
   * @returns FAQs organized by category
   */
  static async getFAQsByCategory(): Promise<Record<string, FAQ[]>> {
    const response = await api.get<Record<string, FAQ[]>>('/faqs/by_category/')
    return response.data.data
  }

  /**
   * Submit feedback for an FAQ
   * @param id - FAQ ID
   * @param helpful - Whether the FAQ was helpful
   * @param comment - Optional feedback comment
   * @returns Success message
   */
  static async submitFAQFeedback(id: number, helpful: boolean, comment?: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>(`/faqs/${id}/feedback/`, {
      helpful,
      comment
    })
    return response.data.data
  }

  /**
   * Create a new FAQ (admin only)
   * @param data - FAQ data
   * @returns Created FAQ
   */
  static async createFAQ(data: Partial<FAQ>): Promise<FAQ> {
    const response = await api.post<FAQ>('/faqs/', data)
    return response.data.data
  }

  /**
   * Update an FAQ (admin only)
   * @param id - FAQ ID
   * @param data - Updated FAQ data
   * @returns Updated FAQ
   */
  static async updateFAQ(id: number, data: Partial<FAQ>): Promise<FAQ> {
    const response = await api.patch<FAQ>(`/faqs/${id}/`, data)
    return response.data.data
  }

  /**
   * Delete an FAQ (admin only)
   * @param id - FAQ ID
   */
  static async deleteFAQ(id: number): Promise<void> {
    await api.delete(`/faqs/${id}/`)
  }

  // ===== Contact Info =====
  
  /**
   * Get all contact information entries
   * @returns Paginated list of contact info
   */
  static async getContactInfoList(): Promise<PaginatedResponse<ContactInfo>> {
    const response = await api.get<PaginatedResponse<ContactInfo>>('/contact-info/')
    return response.data.data
  }

  /**
   * Get a single contact info entry
   * @param id - Contact info ID
   * @returns Contact info details
   */
  static async getContactInfoById(id: number): Promise<ContactInfo> {
    const response = await api.get<ContactInfo>(`/contact-info/${id}/`)
    return response.data.data
  }

  /**
   * Get the active contact information
   * @returns Active contact info
   */
  static async getActiveContactInfo(): Promise<ContactInfo> {
    const response = await api.get<ContactInfo>('/contact-info/active/')
    return response.data.data
  }

  /**
   * Create new contact information (admin only)
   * @param data - Contact info data
   * @returns Created contact info
   */
  static async createContactInfo(data: Partial<ContactInfo>): Promise<ContactInfo> {
    const response = await api.post<ContactInfo>('/contact-info/', data)
    return response.data.data
  }

  /**
   * Update contact information (admin only)
   * @param id - Contact info ID
   * @param data - Updated contact info data
   * @returns Updated contact info
   */
  static async updateContactInfo(id: number, data: Partial<ContactInfo>): Promise<ContactInfo> {
    const response = await api.patch<ContactInfo>(`/contact-info/${id}/`, data)
    return response.data.data
  }

  /**
   * Delete contact information (admin only)
   * @param id - Contact info ID
   */
  static async deleteContactInfo(id: number): Promise<void> {
    await api.delete(`/contact-info/${id}/`)
  }
}

// Export legacy object for backward compatibility
export const contentService = {
  getTestimonials: ContentService.getTestimonials,
  getFeaturedTestimonials: ContentService.getFeaturedTestimonials,
  createTestimonial: ContentService.createTestimonial,
  getTeamMembers: ContentService.getTeamMembers,
  getTeamMembersByDepartment: ContentService.getTeamMembersByDepartment,
  getAnnouncements: ContentService.getAnnouncements,
  getFeaturedAnnouncements: ContentService.getFeaturedAnnouncements,
  getHomepageAnnouncements: ContentService.getHomepageAnnouncements,
  getFAQs: ContentService.getFAQs,
  getFeaturedFAQs: ContentService.getFeaturedFAQs,
  getFAQsByCategory: ContentService.getFAQsByCategory,
  submitFAQFeedback: ContentService.submitFAQFeedback,
  getContactInfo: ContentService.getActiveContactInfo,
}