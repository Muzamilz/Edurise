<template>
  <div class="global-category-node">
    <div class="category-item" :class="{ inactive: !category.is_active }">
      <div class="category-main">
        <button
          v-if="hasSubcategories"
          @click="$emit('toggleExpand', category.id)"
          class="expand-btn"
          :class="{ expanded: isExpanded }"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
        <div v-else class="expand-spacer"></div>

        <div class="category-icon" :style="{ backgroundColor: category.color || '#6b7280' }">
          <i :class="category.icon || 'fas fa-folder'" class="icon"></i>
        </div>

        <div class="category-info">
          <div class="category-name">
            {{ category.name }}
            <span v-if="!category.is_active" class="inactive-badge">Inactive</span>
            <span v-if="!category.tenant" class="global-badge">Global</span>
          </div>
          <div class="category-meta">
            <span class="category-slug">{{ category.slug }}</span>
            <span v-if="category.description" class="category-description">
              {{ category.description }}
            </span>
          </div>
        </div>
      </div>

      <div class="category-stats">
        <div class="stat-item">
          <i class="fas fa-book"></i>
          <span>{{ getCourseCount(category) }} courses</span>
        </div>
        <div class="stat-item">
          <i class="fas fa-building"></i>
          <span>{{ getOrganizationCount(category) }} orgs</span>
        </div>
      </div>

      <div class="category-actions">
        <button
          @click="$emit('viewUsage', category)"
          class="action-btn"
          title="View Usage Analytics"
        >
          <i class="fas fa-chart-bar"></i>
        </button>
        <button
          @click="$emit('addSubcategory', category)"
          class="action-btn"
          title="Add Subcategory"
        >
          <i class="fas fa-plus"></i>
        </button>
        <button
          @click="$emit('edit', category)"
          class="action-btn"
          title="Edit Category"
        >
          <i class="fas fa-edit"></i>
        </button>
        <button
          @click="$emit('delete', category)"
          class="action-btn delete-btn"
          title="Delete Category"
        >
          <i class="fas fa-trash"></i>
        </button>
      </div>
    </div>

    <!-- Subcategories -->
    <div v-if="hasSubcategories && isExpanded" class="subcategories">
      <GlobalCategoryTreeNode
        v-for="subcategory in category.subcategories"
        :key="subcategory.id"
        :category="subcategory"
        :expanded-nodes="expandedNodes"
        @toggle-expand="$emit('toggleExpand', $event)"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
        @add-subcategory="$emit('addSubcategory', $event)"
        @view-usage="$emit('viewUsage', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CourseCategory } from '@/types/api'

interface Props {
  category: CourseCategory
  expandedNodes: Set<string>
}

interface Emits {
  (e: 'toggleExpand', categoryId: string): void
  (e: 'edit', category: CourseCategory): void
  (e: 'delete', category: CourseCategory): void
  (e: 'addSubcategory', category: CourseCategory): void
  (e: 'viewUsage', category: CourseCategory): void
}

const props = defineProps<Props>()
defineEmits<Emits>()

const hasSubcategories = computed(() => 
  props.category.subcategories && props.category.subcategories.length > 0
)

const isExpanded = computed(() => 
  props.expandedNodes.has(props.category.id)
)

const getCourseCount = (category: CourseCategory): number => {
  // This would come from API with course counts
  return 0 // Placeholder
}

const getOrganizationCount = (category: CourseCategory): number => {
  // This would come from API with organization usage counts
  return 0 // Placeholder
}
</script>

<style scoped>
/* Similar styles to CategoryTreeNode but with additional global-specific styling */
.global-category-node {
  margin-bottom: 0.5rem;
}

.category-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
}

.category-item:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.category-item.inactive {
  opacity: 0.6;
  background: #f3f4f6;
}

.category-main {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 0.75rem;
}

.expand-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s;
}

.expand-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.expand-btn.expanded {
  transform: rotate(90deg);
}

.expand-spacer {
  width: 24px;
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

.category-info {
  flex: 1;
}

.category-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.global-badge {
  padding: 0.125rem 0.5rem;
  background: #3b82f6;
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.inactive-badge {
  padding: 0.125rem 0.5rem;
  background: #fef3c7;
  color: #92400e;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.category-meta {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.category-slug {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.75rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
}

.category-description {
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.4;
}

.category-stats {
  display: flex;
  gap: 1rem;
  margin-right: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.stat-item i {
  width: 14px;
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

.subcategories {
  margin-left: 2rem;
  margin-top: 0.5rem;
  padding-left: 1rem;
  border-left: 2px solid #e5e7eb;
}
</style>