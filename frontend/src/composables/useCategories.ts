import { ref, computed, readonly } from 'vue'
import { CategoryService } from '@/services/categoryService'
import type { CourseCategory } from '@/types/api'

const categories = ref<CourseCategory[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

export function useCategories() {
  const rootCategories = computed(() => 
    categories.value.filter(cat => !cat.parent)
  )

  const categoryOptions = computed(() => {
    const options: Array<{ value: string; label: string; icon?: string; color?: string }> = []
    
    const addOptions = (cats: CourseCategory[], prefix = '') => {
      cats.forEach(category => {
        options.push({
          value: category.id,
          label: prefix + category.name,
          icon: category.icon,
          color: category.color
        })
        
        if (category.subcategories && category.subcategories.length > 0) {
          addOptions(category.subcategories, prefix + '  ')
        }
      })
    }
    
    addOptions(rootCategories.value)
    return options
  })

  const fetchCategories = async () => {
    loading.value = true
    error.value = null
    
    try {
      categories.value = await CategoryService.getCategoryHierarchy()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch categories'
      console.error('Error fetching categories:', err)
    } finally {
      loading.value = false
    }
  }

  const getCategoryById = (id: string): CourseCategory | undefined => {
    const findCategory = (cats: CourseCategory[]): CourseCategory | undefined => {
      for (const cat of cats) {
        if (cat.id === id) return cat
        if (cat.subcategories) {
          const found = findCategory(cat.subcategories)
          if (found) return found
        }
      }
      return undefined
    }
    
    return findCategory(categories.value)
  }

  const getCategoryPath = (id: string): string => {
    const category = getCategoryById(id)
    return category?.full_path || ''
  }

  const getSubcategories = (parentId: string): CourseCategory[] => {
    const parent = getCategoryById(parentId)
    return parent?.subcategories || []
  }

  const createCategory = async (categoryData: Partial<CourseCategory>) => {
    try {
      const newCategory = await CategoryService.createCategory(categoryData)
      await fetchCategories() // Refresh the list
      return newCategory
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create category'
      throw err
    }
  }

  const updateCategory = async (id: string, categoryData: Partial<CourseCategory>) => {
    try {
      const updatedCategory = await CategoryService.updateCategory(id, categoryData)
      await fetchCategories() // Refresh the list
      return updatedCategory
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update category'
      throw err
    }
  }

  const deleteCategory = async (id: string) => {
    try {
      await CategoryService.deleteCategory(id)
      await fetchCategories() // Refresh the list
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete category'
      throw err
    }
  }

  return {
    categories: readonly(categories),
    rootCategories,
    categoryOptions,
    loading: readonly(loading),
    error: readonly(error),
    fetchCategories,
    getCategoryById,
    getCategoryPath,
    getSubcategories,
    createCategory,
    updateCategory,
    deleteCategory
  }
}

// Global state - categories are shared across components
const globalCategoriesState = useCategories()

export function useCategoriesGlobal() {
  return globalCategoriesState
}