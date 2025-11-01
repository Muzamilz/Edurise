<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ isEditing ? 'Edit Category' : 'Create Category' }}</h3>
        <button @click="$emit('close')" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <div class="form-group">
          <label for="name">Category Name *</label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            required
            placeholder="Enter category name"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea
            id="description"
            v-model="formData.description"
            placeholder="Enter category description"
            class="form-textarea"
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="parent">Parent Category</label>
          <select id="parent" v-model="formData.parent_id" class="form-select">
            <option value="">No Parent (Root Category)</option>
            <option
              v-for="category in availableParents"
              :key="category.id"
              :value="category.id"
            >
              {{ category.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input
              v-model="formData.is_active"
              type="checkbox"
              class="form-checkbox"
            />
            <span class="checkbox-text">Active</span>
          </label>
        </div>

        <div class="modal-actions">
          <button type="button" @click="$emit('close')" class="btn btn-outline">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            <i v-if="loading" class="fas fa-spinner fa-spin"></i>
            {{ isEditing ? 'Update' : 'Create' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Category } from '@/types'

interface Props {
  show: boolean
  category?: Category | null
  categories: Category[]
  loading?: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'submit', data: Partial<Category>): void
}

const props = withDefaults(defineProps<Props>(), {
  category: null,
  loading: false
})

const emit = defineEmits<Emits>()

const formData = ref({
  name: '',
  description: '',
  parent_id: '',
  is_active: true
})

const isEditing = computed(() => !!props.category)

const availableParents = computed(() => {
  if (!props.category) return props.categories
  
  // Exclude the current category and its descendants to prevent circular references
  return props.categories.filter(cat => 
    cat.id !== props.category?.id && 
    !isDescendant(cat, props.category)
  )
})

const isDescendant = (category: Category, potentialAncestor: Category): boolean => {
  if (category.parent_id === potentialAncestor.id) return true
  
  const parent = props.categories.find(c => c.id === category.parent_id)
  if (!parent) return false
  
  return isDescendant(parent, potentialAncestor)
}

const handleOverlayClick = () => {
  emit('close')
}

const handleSubmit = () => {
  const submitData: Partial<Category> = {
    name: formData.value.name,
    description: formData.value.description,
    parent_id: formData.value.parent_id || null,
    is_active: formData.value.is_active
  }
  
  emit('submit', submitData)
}

// Watch for category changes to populate form
watch(() => props.category, (newCategory) => {
  if (newCategory) {
    formData.value = {
      name: newCategory.name,
      description: newCategory.description || '',
      parent_id: newCategory.parent_id || '',
      is_active: newCategory.is_active
    }
  } else {
    formData.value = {
      name: '',
      description: '',
      parent_id: '',
      is_active: true
    }
  }
}, { immediate: true })

// Reset form when modal is closed
watch(() => props.show, (show) => {
  if (!show) {
    formData.value = {
      name: '',
      description: '',
      parent_id: '',
      is_active: true
    }
  }
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
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
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

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.form-checkbox {
  width: auto;
  margin: 0;
}

.checkbox-text {
  color: #374151;
  font-weight: 500;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
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
  opacity: 0.6;
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

.btn-outline:hover {
  background: #f9fafb;
}
</style>