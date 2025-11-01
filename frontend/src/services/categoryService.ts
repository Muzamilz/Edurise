import { api } from './api'
import type { CourseCategory } from '@/types/api'

export class CategoryService {
  /**
   * Get all course categories
   */
  static async getCategories(): Promise<CourseCategory[]> {
    const response = await api.get('/course-categories/')
    return response.data.data
  }

  /**
   * Get root categories (no parent)
   */
  static async getRootCategories(): Promise<CourseCategory[]> {
    const response = await api.get('/course-categories/root_categories/')
    return response.data.data
  }

  /**
   * Get category hierarchy
   */
  static async getCategoryHierarchy(): Promise<CourseCategory[]> {
    const response = await api.get('/course-categories/hierarchy/')
    return response.data.data
  }

  /**
   * Get subcategories for a specific category
   */
  static async getSubcategories(categoryId: string): Promise<CourseCategory[]> {
    const response = await api.get(`/course-categories/${categoryId}/subcategories/`)
    return response.data.data
  }

  /**
   * Get a specific category by ID
   */
  static async getCategory(id: string): Promise<CourseCategory> {
    const response = await api.get(`/course-categories/${id}/`)
    return response.data.data
  }

  /**
   * Create a new category
   */
  static async createCategory(categoryData: Partial<CourseCategory>): Promise<CourseCategory> {
    const response = await api.post('/course-categories/', categoryData)
    return response.data.data
  }

  /**
   * Update a category
   */
  static async updateCategory(id: string, categoryData: Partial<CourseCategory>): Promise<CourseCategory> {
    const response = await api.put(`/course-categories/${id}/`, categoryData)
    return response.data.data
  }

  /**
   * Delete a category
   */
  static async deleteCategory(id: string): Promise<void> {
    await api.delete(`/course-categories/${id}/`)
  }

  /**
   * Get categories formatted for select options
   */
  static async getCategoryOptions(): Promise<Array<{ value: string; label: string; icon?: string; color?: string }>> {
    const categories = await this.getRootCategories()
    
    const options: Array<{ value: string; label: string; icon?: string; color?: string }> = []
    
    const addCategoryOptions = (cats: CourseCategory[], prefix = '') => {
      cats.forEach(category => {
        options.push({
          value: category.id,
          label: prefix + category.name,
          icon: category.icon,
          color: category.color
        })
        
        // Add subcategories with indentation
        if (category.subcategories && category.subcategories.length > 0) {
          addCategoryOptions(category.subcategories, prefix + '  ')
        }
      })
    }
    
    addCategoryOptions(categories)
    return options
  }

  /**
   * Search categories by name
   */
  static async searchCategories(query: string): Promise<CourseCategory[]> {
    const response = await api.get('/course-categories/', {
      params: { search: query }
    })
    return response.data.data
  }
}