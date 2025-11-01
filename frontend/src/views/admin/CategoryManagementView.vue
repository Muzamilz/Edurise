<template>
  <div class="category-management">
    <div class="page-header">
      <h1>Category Management</h1>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <i class="fas fa-plus"></i>
        Add Category
      </button>
    </div>

    <!-- Category Tree View -->
    <div class="category-tree-container">
      <div class="tree-header">
        <h2>Category Hierarchy</h2>
        <div class="tree-actions">
          <button @click="expandAll" class="btn btn-outline btn-sm">
            <i class="fas fa-expand-arrows-alt"></i>
            Expand All
          </button>
          <button @click="collapseAll" class="btn btn-outline btn-sm">
            <i class="fas fa-compress-arrows-alt"></i>
            Collapse All
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading categories...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <i class="fas fa-exclamation-triangle"></i>
        <p>{{ error }}</p>
        <button @click="fetchCategories" class="btn btn-primary">Retry</button>
      </div>

      <div v-else class="category-tree">
        <CategoryTreeNode
          v-for="category in rootCategories"
          :key="category.id"
          :category="category"
          :expanded-nodes="expandedNodes"
          @toggle-expand="toggleExpand"
          @edit="editCategory"
          @delete="deleteCategory"
          @add-subcategory="addSubcategory"
        />
      </div>
    </div>

    <!-- Category Statistics -->
    <div class="category-stats">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-layer-group"></i>
          </div>
          <div class="stat-content">
            <h3>{{ totalCategories }}</h3>
            <p>Total Categories</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-sitemap"></i>
          </div>
          <div class="stat-content">
            <h3>{{ rootCategories.length }}</h3>
            <p>Root Categories</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-book"></i>
          </div>
          <div class="stat-content">
            <h3>{{ categoriesWithCourses }}</h3>
            <p>Categories with Courses</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-eye-slash"></i>
          </div>
          <div class="stat-content">
            <h3>{{ inactiveCategories }}</h3>
            <p>Inactive Categories</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Category Modal -->
    <CategoryModal
      v-if="showCreateModal || showEditModal"
      :category="selectedCategory"
      :parent-options="categoryOptions"
      :is-editing="showEditModal"
      @save="saveCategory"
      @cancel="closeModals"
    />

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      v-if="showDeleteModal"
      title="Delete Category"
      :message="`Are you sure you want to delete '${selectedCategory?.name}'? This action cannot be undone.`"
      confirm-text="Delete"
      confirm-class="btn-danger"
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCategoriesGlobal } from '@/composables/useCategories'
import type { CourseCategory } from '@/types/api'
import CategoryTreeNode from '@/components/admin/CategoryTreeNode.vue'
import CategoryModal from '@/components/admin/CategoryModal.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

// Composables
const { 
  categories, 
  rootCategories, 
  categoryOptions, 
  loading, 
  error, 
  fetchCategories,
  createCategory,
  updateCategory,
  deleteCategory: deleteCategoryAPI
} = useCategoriesGlobal()

// State
const expandedNodes = ref<Set<string>>(new Set())
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const selectedCategory = ref<CourseCategory | null>(null)

// Computed
const totalCategories = computed(() => {
  const countCategories = (cats: CourseCategory[]): number => {
    return cats.reduce((count, cat) => {
      return count + 1 + (cat.subcategories ? countCategories(cat.subcategories) : 0)
    }, 0)
  }
  return countCategories(categories.value)
})

const categoriesWithCourses = computed(() => {
  // This would need to be fetched from the API with course counts
  return 0 // Placeholder
})

const inactiveCategories = computed(() => {
  const countInactive = (cats: CourseCategory[]): number => {
    return cats.reduce((count, cat) => {
      const inactive = !cat.is_active ? 1 : 0
      const subInactive = cat.subcategories ? countInactive(cat.subcategories) : 0
      return count + inactive + subInactive
    }, 0)
  }
  return countInactive(categories.value)
})

// Methods
const toggleExpand = (categoryId: string) => {
  if (expandedNodes.value.has(categoryId)) {
    expandedNodes.value.delete(categoryId)
  } else {
    expandedNodes.value.add(categoryId)
  }
}

const expandAll = () => {
  const addAllIds = (cats: CourseCategory[]) => {
    cats.forEach(cat => {
      expandedNodes.value.add(cat.id)
      if (cat.subcategories) {
        addAllIds(cat.subcategories)
      }
    })
  }
  addAllIds(categories.value)
}

const collapseAll = () => {
  expandedNodes.value.clear()
}

const editCategory = (category: CourseCategory) => {
  selectedCategory.value = category
  showEditModal.value = true
}

const addSubcategory = (parentCategory: CourseCategory) => {
  selectedCategory.value = { parent: parentCategory.id } as CourseCategory
  showCreateModal.value = true
}

const deleteCategory = (category: CourseCategory) => {
  selectedCategory.value = category
  showDeleteModal.value = true
}

const saveCategory = async (categoryData: Partial<CourseCategory>) => {
  try {
    if (showEditModal.value && selectedCategory.value) {
      await updateCategory(selectedCategory.value.id, categoryData)
    } else {
      await createCategory(categoryData)
    }
    closeModals()
  } catch (error) {
    console.error('Error saving category:', error)
  }
}

const confirmDelete = async () => {
  if (selectedCategory.value) {
    try {
      await deleteCategoryAPI(selectedCategory.value.id)
      showDeleteModal.value = false
      selectedCategory.value = null
    } catch (error) {
      console.error('Error deleting category:', error)
    }
  }
}

const closeModals = () => {
  showCreateModal.value = false
  showEditModal.value = false
  selectedCategory.value = null
}

// Lifecycle
onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.category-management {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.page-header h1 {
  margin: 0;
  color: #1f2937;
  font-size: 2rem;
  font-weight: 600;
}

.category-tree-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  overflow: hidden;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.tree-header h2 {
  margin: 0;
  color: #374151;
  font-size: 1.25rem;
  font-weight: 600;
}

.tree-actions {
  display: flex;
  gap: 0.5rem;
}

.category-tree {
  padding: 1rem;
  min-height: 300px;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #6b7280;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.category-stats {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3b82f6;
  color: white;
  border-radius: 8px;
  margin-right: 1rem;
  font-size: 1.25rem;
}

.stat-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

.stat-content p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-outline {
  background: transparent;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-outline:hover {
  background: #f9fafb;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}
</style>