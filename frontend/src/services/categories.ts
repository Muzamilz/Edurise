import { api } from './api'

export interface Category {
  id: string
  name: string
  slug: string
  description?: string
  icon?: string
  parent?: string
  course_count?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

/**
 * Category management service
 * Handles course category operations
 */
export class CategoryService {
  /**
   * Get all categories
   * @param filters - Optional filter parameters
   * @returns List of categories
   */
  static async getCategories(filters?: {
    is_active?: boolean
    parent?: string
    search?: string
  }): Promise<Category[]> {
    try {
      const response = await api.get<Category[]>('/categories/', {
        params: filters
      })
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error fetching categories:', error)
      throw error
    }
  }

  /**
   * Get a single category by ID
   * @param id - Category ID
   * @returns Category details
   */
  static async getCategory(id: string): Promise<Category> {
    try {
      const response = await api.get<Category>(`/categories/${id}/`)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error fetching category:', error)
      throw error
    }
  }

  /**
   * Create a new category
   * @param categoryData - Category data
   * @returns Created category
   */
  static async createCategory(categoryData: Partial<Category>): Promise<Category> {
    try {
      const response = await api.post<Category>('/categories/', categoryData)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error creating category:', error)
      throw error
    }
  }

  /**
   * Update an existing category
   * @param id - Category ID
   * @param categoryData - Updated category data
   * @returns Updated category
   */
  static async updateCategory(id: string, categoryData: Partial<Category>): Promise<Category> {
    try {
      const response = await api.patch<Category>(`/categories/${id}/`, categoryData)
      return (response.data as any).data || response.data
    } catch (error) {
      console.error('Error updating category:', error)
      throw error
    }
  }

  /**
   * Delete a category
   * @param id - Category ID
   */
  static async deleteCategory(id: string): Promise<void> {
    try {
      await api.delete(`/categories/${id}/`)
    } catch (error) {
      console.error('Error deleting category:', error)
      throw error
    }
  }
}
