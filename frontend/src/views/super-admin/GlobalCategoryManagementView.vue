<template>
  <div class="global-category-management">
    <div class="page-header">
      <div class="header-content">
        <h1>Global Category Management</h1>
        <p class="header-description">
          Manage global course categories that are available to all organizations
        </p>
      </div>
      <div class="header-actions">
        <button @click="showCreateModal = true" class="btn btn-primary">
          <i class="fas fa-plus"></i>
          Add Global Category
        </button>
        <button @click="exportCategories" class="btn btn-outline">
          <i class="fas fa-download"></i>
          Export
        </button>
      </div>
    </div>

    <!-- Global Stats -->
    <div class="global-stats">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon global">
            <i class="fas fa-globe"></i>
          </div>
          <div class="stat-content">
            <h3>{{ globalCategories.length }}</h3>
            <p>Global Categories</p>
            <small>Available to all organizations</small>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon tenant">
            <i class="fas fa-building"></i>
          </div>
          <div class="stat-content">
            <h3>{{ tenantCategories.length }}</h3>
            <p>Tenant Categories</p>
            <small>Organization-specific</small>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon courses">
            <i class="fas fa-book"></i>
          </div>
          <div class="stat-content">
            <h3>{{ totalCourses }}</h3>
            <p>Total Courses</p>
            <small>Across all categories</small>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon usage">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="stat-content">
            <h3>{{ categoryUsageRate }}%</h3>
            <p>Usage Rate</p>
            <small>Categories with courses</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Category Filters -->
    <div class="category-filters">
      <div class="filter-group">
        <label>Filter by Type:</label>
        <select v-model="filterType" class="filter-select">
          <option value="all">All Categories</option>
          <option value="global">Global Only</option>
          <option value="tenant">Tenant-Specific</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Filter by Status:</label>
        <select v-model="filterStatus" class="filter-select">
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Search:</label>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search categories..."
          class="search-input"
        />
      </div>
    </div>

    <!-- Category Management Tabs -->
    <div class="management-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
      >
        <i :class="tab.icon"></i>
        {{ tab.label }}
        <span v-if="tab.count !== undefined" class="tab-count">{{ tab.count }}</span>
      </button>
    </div>

    <!-- Global Categories Tab -->
    <div v-show="activeTab === 'global'" class="tab-content">
      <div class="section-header">
        <h2>Global Categories</h2>
        <p>These categories are available to all organizations and cannot be modified by tenants.</p>
      </div>
      
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading global categories...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <i class="fas fa-exclamation-triangle"></i>
        <p>{{ error }}</p>
        <button @click="fetchCategories" class="btn btn-primary">Retry</button>
      </div>

      <div v-else class="category-tree">
        <GlobalCategoryTreeNode
          v-for="category in filteredGlobalCategories"
          :key="category.id"
          :category="category"
          :expanded-nodes="expandedNodes"
          @toggle-expand="toggleExpand"
          @edit="editCategory"
          @delete="deleteCategory"
          @add-subcategory="addSubcategory"
          @view-usage="viewCategoryUsage"
        />
      </div>
    </div>

    <!-- Tenant Categories Tab -->
    <div v-show="activeTab === 'tenant'" class="tab-content">
      <div class="section-header">
        <h2>Tenant-Specific Categories</h2>
        <p>Categories created by individual organizations for their specific needs.</p>
      </div>

      <div class="tenant-categories-list">
        <div
          v-for="category in filteredTenantCategories"
          :key="category.id"
          class="tenant-category-item"
        >
          <div class="category-info">
            <div class="category-icon" :style="{ backgroundColor: category.color || '#6b7280' }">
              <i :class="category.icon || 'fas fa-folder'"></i>
            </div>
            <div class="category-details">
              <div class="category-name">{{ category.name }}</div>
              <div class="category-meta">
                <span class="organization">{{ getOrganizationName(category.tenant) }}</span>
                <span class="separator">•</span>
                <span class="slug">{{ category.slug }}</span>
                <span v-if="!category.is_active" class="inactive-badge">Inactive</span>
              </div>
            </div>
          </div>
          <div class="category-actions">
            <button @click="viewCategoryUsage(category)" class="action-btn" title="View Usage">
              <i class="fas fa-chart-bar"></i>
            </button>
            <button @click="editCategory(category)" class="action-btn" title="Edit">
              <i class="fas fa-edit"></i>
            </button>
            <button @click="deleteCategory(category)" class="action-btn delete-btn" title="Delete">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Analytics Tab -->
    <div v-show="activeTab === 'analytics'" class="tab-content">
      <div class="section-header">
        <h2>Category Analytics</h2>
        <p>Usage statistics and insights across all categories.</p>
      </div>

      <div class="analytics-grid">
        <div class="analytics-card">
          <h3>Most Popular Categories</h3>
          <div class="popular-categories">
            <div
              v-for="category in popularCategories"
              :key="category.id"
              class="popular-item"
            >
              <div class="category-icon" :style="{ backgroundColor: category.color }">
                <i :class="category.icon"></i>
              </div>
              <div class="category-info">
                <div class="name">{{ category.name }}</div>
                <div class="stats">{{ category.course_count }} courses</div>
              </div>
            </div>
          </div>
        </div>

        <div class="analytics-card">
          <h3>Category Distribution</h3>
          <div class="distribution-chart">
            <!-- Chart would go here -->
            <div class="chart-placeholder">
              <i class="fas fa-chart-pie"></i>
              <p>Category distribution chart</p>
            </div>
          </div>
        </div>

        <div class="analytics-card">
          <h3>Usage Trends</h3>
          <div class="trends-chart">
            <!-- Chart would go here -->
            <div class="chart-placeholder">
              <i class="fas fa-chart-line"></i>
              <p>Usage trends over time</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Category Modal -->
    <GlobalCategoryModal
      :show="showCreateModal || showEditModal"
      :category="selectedCategory"
      :categories="categories as any"
      :loading="loading"
      @submit="saveCategory"
      @close="closeModals"
    />

    <!-- Category Usage Modal -->
    <CategoryUsageModal
      :show="showUsageModal"
      :category="selectedCategory"
      @close="showUsageModal = false"
    />

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      v-if="showDeleteModal"
      title="Delete Category"
      :message="`Are you sure you want to delete '${selectedCategory?.name}'? This will affect all organizations using this category.`"
      confirm-text="Delete"
      confirm-class="btn-danger"
      type="danger"
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCategoriesGlobal } from '@/composables/useCategories'
import type { CourseCategory } from '@/types/api'
import GlobalCategoryTreeNode from '@/components/super-admin/GlobalCategoryTreeNode.vue'
import GlobalCategoryModal from '@/components/super-admin/GlobalCategoryModal.vue'
import CategoryUsageModal from '@/components/super-admin/CategoryUsageModal.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

// Composables
const { 
  categories, 
  loading, 
  error, 
  fetchCategories,
  createCategory,
  updateCategory,
  deleteCategory: deleteCategoryAPI
} = useCategoriesGlobal()

// State
const activeTab = ref('global')
const expandedNodes = ref<Set<string>>(new Set())
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const showUsageModal = ref(false)
const selectedCategory = ref<CourseCategory | null>(null)
const filterType = ref('all')
const filterStatus = ref('all')
const searchQuery = ref('')

// Tabs configuration
const tabs = computed(() => [
  { 
    id: 'global', 
    label: 'Global Categories', 
    icon: 'fas fa-globe',
    count: globalCategories.value.length
  },
  { 
    id: 'tenant', 
    label: 'Tenant Categories', 
    icon: 'fas fa-building',
    count: tenantCategories.value.length
  },
  { 
    id: 'analytics', 
    label: 'Analytics', 
    icon: 'fas fa-chart-bar'
  }
])

// Computed
const globalCategories = computed(() => 
  categories.value.filter(cat => !cat.tenant) as CourseCategory[]
)

const tenantCategories = computed(() => 
  categories.value.filter(cat => cat.tenant) as CourseCategory[]
)

// Unused - categories are passed directly to modal
// const globalCategoryOptions = computed(() => {
//   const options: Array<{ value: string; label: string }> = []
//   
//   const addOptions = (cats: CourseCategory[], prefix = '') => {
//     cats.forEach(category => {
//       if (!category.tenant) { // Only global categories as parent options
//         options.push({
//           value: category.id,
//           label: prefix + category.name
//         })
//         
//         if (category.subcategories && category.subcategories.length > 0) {
//           addOptions(category.subcategories, prefix + '  ')
//         }
//       }
//     })
//   }
//   
//   addOptions(globalCategories.value)
//   return options
// })

const filteredGlobalCategories = computed(() => {
  let filtered = globalCategories.value.filter(cat => !cat.parent)
  
  if (filterStatus.value !== 'all') {
    const isActive = filterStatus.value === 'active'
    filtered = filtered.filter(cat => cat.is_active === isActive)
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(cat => 
      cat.name.toLowerCase().includes(query) ||
      cat.description.toLowerCase().includes(query) ||
      cat.slug.toLowerCase().includes(query)
    )
  }
  
  return filtered
})

const filteredTenantCategories = computed(() => {
  let filtered = tenantCategories.value
  
  if (filterStatus.value !== 'all') {
    const isActive = filterStatus.value === 'active'
    filtered = filtered.filter(cat => cat.is_active === isActive)
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(cat => 
      cat.name.toLowerCase().includes(query) ||
      cat.description.toLowerCase().includes(query) ||
      cat.slug.toLowerCase().includes(query)
    )
  }
  
  return filtered
})

const totalCourses = computed(() => {
  // This would come from API with course counts
  return 0 // Placeholder
})

const categoryUsageRate = computed(() => {
  const totalCategories = categories.value.length
  if (totalCategories === 0) return 0
  
  // This would come from API with usage data
  const usedCategories = 0 // Placeholder
  return Math.round((usedCategories / totalCategories) * 100)
})

const popularCategories = computed(() => {
  // This would come from API with course counts
  return globalCategories.value.slice(0, 5).map(cat => ({
    ...cat,
    course_count: 0 // Placeholder
  }))
})

// Methods
const toggleExpand = (categoryId: string) => {
  if (expandedNodes.value.has(categoryId)) {
    expandedNodes.value.delete(categoryId)
  } else {
    expandedNodes.value.add(categoryId)
  }
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

const viewCategoryUsage = (category: CourseCategory) => {
  selectedCategory.value = category
  showUsageModal.value = true
}

const saveCategory = async (categoryData: Partial<CourseCategory>) => {
  try {
    // Ensure global categories have no tenant
    if (!showEditModal.value) {
      categoryData.tenant = null
    }
    
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

const exportCategories = () => {
  // Export functionality
  console.log('Exporting categories...')
}

const getOrganizationName = (tenantId: string | null) => {
  // This would come from organization data
  return tenantId ? 'Organization Name' : 'Global'
}

// Lifecycle
onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.global-category-management {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.header-content h1 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 2rem;
  font-weight: 600;
}

.header-description {
  margin: 0;
  color: #6b7280;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.global-stats {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.stat-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  margin-right: 1rem;
  font-size: 1.5rem;
  color: white;
}

.stat-icon.global {
  background: #3b82f6;
}

.stat-icon.tenant {
  background: #10b981;
}

.stat-icon.courses {
  background: #f59e0b;
}

.stat-icon.usage {
  background: #8b5cf6;
}

.stat-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.75rem;
  font-weight: 700;
  color: #1f2937;
}

.stat-content p {
  margin: 0 0 0.25rem 0;
  color: #374151;
  font-weight: 500;
}

.stat-content small {
  color: #6b7280;
  font-size: 0.875rem;
}

.category-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.filter-select,
.search-input {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.management-tabs {
  display: flex;
  background: white;
  border-radius: 8px 8px 0 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 0;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  background: none;
  border: none;
  color: #6b7280;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
}

.tab-btn:hover {
  color: #374151;
  background: #f9fafb;
}

.tab-btn.active {
  color: #3b82f6;
  background: white;
  border-bottom-color: #3b82f6;
}

.tab-count {
  padding: 0.125rem 0.5rem;
  background: #e5e7eb;
  color: #374151;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.tab-btn.active .tab-count {
  background: #dbeafe;
  color: #3b82f6;
}

.tab-content {
  background: white;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  min-height: 400px;
}

.section-header {
  margin-bottom: 2rem;
}

.section-header h2 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.section-header p {
  margin: 0;
  color: #6b7280;
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

.tenant-categories-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.tenant-category-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
}

.tenant-category-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.category-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: white;
  font-size: 1.125rem;
}

.category-details {
  flex: 1;
}

.category-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.category-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.separator {
  color: #d1d5db;
}

.slug {
  font-family: 'Monaco', 'Menlo', monospace;
  background: #e5e7eb;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
}

.inactive-badge {
  padding: 0.125rem 0.5rem;
  background: #fef3c7;
  color: #92400e;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.category-actions {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.delete-btn:hover {
  background: #fef2f2;
  color: #dc2626;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.analytics-card {
  padding: 1.5rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.analytics-card h3 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1.125rem;
  font-weight: 600;
}

.popular-categories {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.popular-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.popular-item .category-icon {
  width: 32px;
  height: 32px;
  font-size: 0.875rem;
}

.popular-item .category-info .name {
  font-weight: 500;
  color: #374151;
}

.popular-item .category-info .stats {
  font-size: 0.875rem;
  color: #6b7280;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #9ca3af;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
}

.chart-placeholder i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
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
</style>