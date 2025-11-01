<template>
  <div class="modal-overlay" @click="$emit('cancel')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ isEditing ? 'Edit Category' : 'Create Category' }}</h2>
        <button @click="$emit('cancel')" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <div class="form-grid">
          <!-- Basic Information -->
          <div class="form-section">
            <h3>Basic Information</h3>
            
            <div class="form-group">
              <label for="name" class="form-label">Name *</label>
              <input
                id="name"
                v-model="formData.name"
                type="text"
                class="form-input"
                :class="{ error: errors.name }"
                placeholder="Enter category name"
                required
              />
              <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
            </div>

            <div class="form-group">
              <label for="slug" class="form-label">Slug *</label>
              <input
                id="slug"
                v-model="formData.slug"
                type="text"
                class="form-input"
                :class="{ error: errors.slug }"
                placeholder="category-slug"
                required
              />
              <small class="form-help">URL-friendly version of the name</small>
              <span v-if="errors.slug" class="error-message">{{ errors.slug }}</span>
            </div>

            <div class="form-group">
              <label for="description" class="form-label">Description</label>
              <textarea
                id="description"
                v-model="formData.description"
                class="form-textarea"
                rows="3"
                placeholder="Enter category description"
              ></textarea>
            </div>

            <div class="form-group">
              <label for="parent" class="form-label">Parent Category</label>
              <select
                id="parent"
                v-model="formData.parent"
                class="form-select"
              >
                <option value="">No Parent (Root Category)</option>
                <option
                  v-for="option in parentOptions"
                  :key="option.value"
                  :value="option.value"
                  :disabled="option.value === category?.id"
                >
                  {{ option.label }}
                </option>
              </select>
              <small class="form-help">Select a parent category to create a subcategory</small>
            </div>
          </div>

          <!-- Visual Settings -->
          <div class="form-section">
            <h3>Visual Settings</h3>
            
            <div class="form-group">
              <label for="icon" class="form-label">Icon</label>
              <div class="icon-input-group">
                <input
                  id="icon"
                  v-model="formData.icon"
                  type="text"
                  class="form-input"
                  placeholder="fas fa-laptop-code"
                />
                <div class="icon-preview" :style="{ backgroundColor: formData.color || '#6b7280' }">
                  <i :class="formData.icon || 'fas fa-folder'" class="preview-icon"></i>
                </div>
              </div>
              <small class="form-help">FontAwesome icon class (e.g., fas fa-laptop-code)</small>
            </div>

            <div class="form-group">
              <label for="color" class="form-label">Color</label>
              <div class="color-input-group">
                <input
                  id="color"
                  v-model="formData.color"
                  type="color"
                  class="color-picker"
                />
                <input
                  v-model="formData.color"
                  type="text"
                  class="form-input"
                  placeholder="#3B82F6"
                />
              </div>
              <small class="form-help">Hex color code for the category</small>
            </div>

            <div class="form-group">
              <label for="sort_order" class="form-label">Sort Order</label>
              <input
                id="sort_order"
                v-model.number="formData.sort_order"
                type="number"
                class="form-input"
                min="0"
                placeholder="0"
              />
              <small class="form-help">Lower numbers appear first</small>
            </div>
          </div>
        </div>

        <!-- Status -->
        <div class="form-section">
          <h3>Status</h3>
          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="formData.is_active"
                type="checkbox"
                class="checkbox"
              />
              <span class="checkbox-text">Active</span>
            </label>
            <small class="form-help">Inactive categories won't be shown in course creation</small>
          </div>
        </div>

        <!-- Preview -->
        <div class="form-section">
          <h3>Preview</h3>
          <div class="category-preview">
            <div class="preview-icon-container" :style="{ backgroundColor: formData.color || '#6b7280' }">
              <i :class="formData.icon || 'fas fa-folder'" class="preview-icon"></i>
            </div>
            <div class="preview-info">
              <div class="preview-name">{{ formData.name || 'Category Name' }}</div>
              <div class="preview-slug">{{ formData.slug || 'category-slug' }}</div>
              <div v-if="formData.description" class="preview-description">
                {{ formData.description }}
              </div>
            </div>
          </div>
        </div>
      </form>

      <div class="modal-footer">
        <button
          type="button"
          @click="$emit('cancel')"
          class="btn btn-outline"
          :disabled="loading"
        >
          Cancel
        </button>
        <button
          type="submit"
          @click="handleSubmit"
          class="btn btn-primary"
          :disabled="loading || !isFormValid"
        >
          {{ loading ? 'Saving...' : (isEditing ? 'Update Category' : 'Create Category') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { CourseCategory } from '@/types/api'

interface Props {
  category?: CourseCategory | null
  parentOptions: Array<{ value: string; label: string }>
  isEditing: boolean
}

interface Emits {
  (e: 'save', categoryData: Partial<CourseCategory>): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  category: null,
  isEditing: false
})

const emit = defineEmits<Emits>()

// Form data
const formData = ref({
  name: '',
  slug: '',
  description: '',
  icon: '',
  color: '#3B82F6',
  parent: '',
  sort_order: 0,
  is_active: true
})

// Form state
const loading = ref(false)
const errors = ref<Record<string, string>>({})

// Computed
const isFormValid = computed(() => {
  return formData.value.name.trim() && 
         formData.value.slug.trim() && 
         !Object.keys(errors.value).length
})

// Methods
const generateSlug = (name: string) => {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

const validateForm = () => {
  errors.value = {}

  if (!formData.value.name.trim()) {
    errors.value.name = 'Name is required'
  }

  if (!formData.value.slug.trim()) {
    errors.value.slug = 'Slug is required'
  } else if (!/^[a-z0-9-]+$/.test(formData.value.slug)) {
    errors.value.slug = 'Slug can only contain lowercase letters, numbers, and hyphens'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return

  loading.value = true
  
  try {
    const categoryData: Partial<CourseCategory> = {
      name: formData.value.name.trim(),
      slug: formData.value.slug.trim(),
      description: formData.value.description.trim(),
      icon: formData.value.icon.trim(),
      color: formData.value.color,
      parent: formData.value.parent || null,
      sort_order: formData.value.sort_order,
      is_active: formData.value.is_active
    }

    emit('save', categoryData)
  } catch (error) {
    console.error('Error saving category:', error)
  } finally {
    loading.value = false
  }
}

const loadCategoryData = () => {
  if (props.category) {
    formData.value = {
      name: props.category.name || '',
      slug: props.category.slug || '',
      description: props.category.description || '',
      icon: props.category.icon || '',
      color: props.category.color || '#3B82F6',
      parent: props.category.parent || '',
      sort_order: props.category.sort_order || 0,
      is_active: props.category.is_active !== false
    }
  }
}

// Watchers
watch(() => formData.value.name, (newName) => {
  if (!props.isEditing && newName) {
    formData.value.slug = generateSlug(newName)
  }
})

watch(() => props.category, loadCategoryData, { immediate: true })

// Lifecycle
onMounted(() => {
  loadCategoryData()
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
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

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.form-section {
  background: #f9fafb;
  border-radius: 8px;
  padding: 1.5rem;
}

.form-section h3 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1.125rem;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #374151;
  font-weight: 500;
  font-size: 0.875rem;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.error,
.form-textarea.error,
.form-select.error {
  border-color: #ef4444;
}

.form-help {
  display: block;
  margin-top: 0.25rem;
  color: #6b7280;
  font-size: 0.75rem;
}

.error-message {
  display: block;
  margin-top: 0.25rem;
  color: #ef4444;
  font-size: 0.75rem;
}

.icon-input-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.icon-input-group .form-input {
  flex: 1;
}

.icon-preview {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  color: white;
}

.preview-icon {
  font-size: 1.125rem;
}

.color-input-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.color-picker {
  width: 40px;
  height: 40px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
}

.color-input-group .form-input {
  flex: 1;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox {
  width: 16px;
  height: 16px;
}

.checkbox-text {
  color: #374151;
  font-weight: 500;
}

.category-preview {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.preview-icon-container {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: white;
}

.preview-info {
  flex: 1;
}

.preview-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.preview-slug {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.75rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  display: inline-block;
  margin-bottom: 0.25rem;
}

.preview-description {
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.4;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-outline {
  background: transparent;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background: #f9fafb;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .modal-content {
    margin: 0.5rem;
    max-width: none;
  }
}
</style>