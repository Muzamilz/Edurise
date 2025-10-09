<template>
  <div class="course-form">
    <div class="form-header">
      <h2>{{ isEditing ? 'Edit Course' : 'Create New Course' }}</h2>
      <p>{{ isEditing ? 'Update your course details' : 'Fill in the details to create your course' }}</p>
    </div>

    <form @submit.prevent="handleSubmit" class="form">
      <!-- Basic Information -->
      <div class="form-section">
        <h3>Basic Information</h3>
        
        <div class="form-group">
          <label for="title" class="form-label">Course Title *</label>
          <input
            id="title"
            v-model="formData.title"
            type="text"
            class="form-input"
            :class="{ error: errors.title }"
            placeholder="Enter course title"
            required
          />
          <span v-if="errors.title" class="error-message">{{ errors.title }}</span>
        </div>

        <div class="form-group">
          <label for="description" class="form-label">Description *</label>
          <textarea
            id="description"
            v-model="formData.description"
            class="form-textarea"
            :class="{ error: errors.description }"
            placeholder="Describe what students will learn in this course"
            rows="4"
            required
          ></textarea>
          <span v-if="errors.description" class="error-message">{{ errors.description }}</span>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="category" class="form-label">Category *</label>
            <select
              id="category"
              v-model="formData.category"
              class="form-select"
              :class="{ error: errors.category }"
              required
            >
              <option value="">Select a category</option>
              <option value="technology">Technology</option>
              <option value="business">Business</option>
              <option value="design">Design</option>
              <option value="marketing">Marketing</option>
              <option value="language">Language</option>
              <option value="science">Science</option>
              <option value="other">Other</option>
            </select>
            <span v-if="errors.category" class="error-message">{{ errors.category }}</span>
          </div>

          <div class="form-group">
            <label for="difficulty_level" class="form-label">Difficulty Level *</label>
            <select
              id="difficulty_level"
              v-model="formData.difficulty_level"
              class="form-select"
              :class="{ error: errors.difficulty_level }"
              required
            >
              <option value="">Select difficulty</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
            <span v-if="errors.difficulty_level" class="error-message">{{ errors.difficulty_level }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="tags" class="form-label">Tags</label>
          <div class="tags-input">
            <div class="tags-list">
              <span
                v-for="(tag, index) in formData.tags"
                :key="index"
                class="tag"
              >
                {{ tag }}
                <button
                  type="button"
                  @click="removeTag(index)"
                  class="tag-remove"
                >
                  ×
                </button>
              </span>
            </div>
            <input
              v-model="newTag"
              @keydown.enter.prevent="addTag"
              @keydown.comma.prevent="addTag"
              type="text"
              class="tag-input"
              placeholder="Add tags (press Enter or comma to add)"
            />
          </div>
          <small class="form-help">Add relevant tags to help students find your course</small>
        </div>
      </div>

      <!-- Course Settings -->
      <div class="form-section">
        <h3>Course Settings</h3>
        
        <div class="form-row">
          <div class="form-group">
            <label for="price" class="form-label">Price ($)</label>
            <input
              id="price"
              v-model.number="formData.price"
              type="number"
              step="0.01"
              min="0"
              class="form-input"
              :class="{ error: errors.price }"
              placeholder="0.00"
            />
            <span v-if="errors.price" class="error-message">{{ errors.price }}</span>
            <small class="form-help">Leave empty or set to 0 for free courses</small>
          </div>

          <div class="form-group">
            <label for="duration_weeks" class="form-label">Duration (weeks) *</label>
            <input
              id="duration_weeks"
              v-model.number="formData.duration_weeks"
              type="number"
              min="1"
              max="52"
              class="form-input"
              :class="{ error: errors.duration_weeks }"
              placeholder="8"
              required
            />
            <span v-if="errors.duration_weeks" class="error-message">{{ errors.duration_weeks }}</span>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="max_students" class="form-label">Maximum Students</label>
            <input
              id="max_students"
              v-model.number="formData.max_students"
              type="number"
              min="1"
              class="form-input"
              :class="{ error: errors.max_students }"
              placeholder="Unlimited"
            />
            <span v-if="errors.max_students" class="error-message">{{ errors.max_students }}</span>
            <small class="form-help">Leave empty for unlimited enrollment</small>
          </div>

          <div class="form-group">
            <div class="checkbox-group">
              <input
                id="is_public"
                v-model="formData.is_public"
                type="checkbox"
                class="form-checkbox"
              />
              <label for="is_public" class="checkbox-label">
                Make this course public
              </label>
            </div>
            <small class="form-help">Public courses appear in the marketplace</small>
          </div>
        </div>
      </div>

      <!-- Course Image -->
      <div class="form-section">
        <h3>Course Image</h3>
        
        <div class="form-group">
          <label class="form-label">Thumbnail Image</label>
          <div class="image-upload">
            <div v-if="imagePreview" class="image-preview">
              <img :src="imagePreview" alt="Course thumbnail" />
              <button
                type="button"
                @click="removeImage"
                class="image-remove"
              >
                Remove
              </button>
            </div>
            <div v-else class="image-placeholder">
              <div class="placeholder-icon">📷</div>
              <p>Upload course thumbnail</p>
              <small>Recommended size: 800x450px</small>
            </div>
            <input
              ref="imageInput"
              type="file"
              accept="image/*"
              @change="handleImageUpload"
              class="image-input"
            />
            <button
              type="button"
              @click="($refs.imageInput as HTMLInputElement)?.click()"
              class="upload-btn"
            >
              {{ imagePreview ? 'Change Image' : 'Upload Image' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
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
          class="btn btn-primary"
          :disabled="loading || !isFormValid"
        >
          {{ loading ? 'Saving...' : (isEditing ? 'Update Course' : 'Create Course') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { Course } from '../../types/api'

interface Props {
  course?: Course | null
  loading?: boolean
}

interface Emits {
  (e: 'submit', courseData: Partial<Course>): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  course: null,
  loading: false
})

const emit = defineEmits<Emits>()

// Form data
const formData = ref({
  title: '',
  description: '',
  category: '',
  difficulty_level: '',
  tags: [] as string[],
  price: null as number | null,
  duration_weeks: 8,
  max_students: null as number | null,
  is_public: false,
  thumbnail: null as File | null
})

// Form state
const newTag = ref('')
const imagePreview = ref<string | null>(null)
const errors = ref<Record<string, string>>({})

// Computed
const isEditing = computed(() => !!props.course)

const isFormValid = computed(() => {
  return formData.value.title.trim() !== '' &&
         formData.value.description.trim() !== '' &&
         formData.value.category !== '' &&
         formData.value.difficulty_level !== '' &&
         formData.value.duration_weeks > 0
})

// Methods
const validateForm = () => {
  errors.value = {}

  if (!formData.value.title.trim()) {
    errors.value.title = 'Course title is required'
  }

  if (!formData.value.description.trim()) {
    errors.value.description = 'Course description is required'
  }

  if (!formData.value.category) {
    errors.value.category = 'Please select a category'
  }

  if (!formData.value.difficulty_level) {
    errors.value.difficulty_level = 'Please select a difficulty level'
  }

  if (formData.value.duration_weeks <= 0) {
    errors.value.duration_weeks = 'Duration must be at least 1 week'
  }

  if (formData.value.price !== null && formData.value.price < 0) {
    errors.value.price = 'Price cannot be negative'
  }

  if (formData.value.max_students !== null && formData.value.max_students <= 0) {
    errors.value.max_students = 'Maximum students must be greater than 0'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = () => {
  if (!validateForm()) {
    return
  }

  const courseData: Partial<Course> = {
    title: formData.value.title.trim(),
    description: formData.value.description.trim(),
    category: formData.value.category,
    difficulty_level: formData.value.difficulty_level as 'beginner' | 'intermediate' | 'advanced',
    tags: formData.value.tags,
    price: formData.value.price || undefined,
    duration_weeks: formData.value.duration_weeks,
    max_students: formData.value.max_students || undefined,
    is_public: formData.value.is_public
  }

  // Include thumbnail if uploaded
  if (formData.value.thumbnail) {
    // In a real implementation, you'd upload the image first
    // and get a URL back, then include it in the course data
    // courseData.thumbnail = uploadedImageUrl
  }

  emit('submit', courseData)
}

const addTag = () => {
  const tag = newTag.value.trim().toLowerCase()
  if (tag && !formData.value.tags.includes(tag)) {
    formData.value.tags.push(tag)
    newTag.value = ''
  }
}

const removeTag = (index: number) => {
  formData.value.tags.splice(index, 1)
}

const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    formData.value.thumbnail = file
    
    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const removeImage = () => {
  formData.value.thumbnail = null
  imagePreview.value = null
  
  // Clear file input
  const input = document.querySelector('.image-input') as HTMLInputElement
  if (input) {
    input.value = ''
  }
}

const loadCourseData = () => {
  if (props.course) {
    formData.value = {
      title: props.course.title,
      description: props.course.description,
      category: props.course.category,
      difficulty_level: props.course.difficulty_level,
      tags: [...props.course.tags],
      price: props.course.price || null,
      duration_weeks: props.course.duration_weeks,
      max_students: props.course.max_students || null,
      is_public: props.course.is_public,
      thumbnail: null
    }
    
    // Set image preview if course has thumbnail
    if (props.course.thumbnail) {
      imagePreview.value = props.course.thumbnail
    }
  }
}

// Lifecycle
onMounted(() => {
  loadCourseData()
})

// Watch for course changes
watch(() => props.course, () => {
  loadCourseData()
}, { deep: true })
</script>

<style scoped>
.course-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.form-header h2 {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.form-header p {
  color: #6B7280;
  font-size: 1.125rem;
}

.form {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.form-section {
  padding: 32px;
  border-bottom: 1px solid #E5E7EB;
}

.form-section:last-child {
  border-bottom: none;
}

.form-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.error,
.form-textarea.error,
.form-select.error {
  border-color: #EF4444;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.form-help {
  display: block;
  margin-top: 4px;
  font-size: 0.75rem;
  color: #6B7280;
}

.error-message {
  display: block;
  margin-top: 4px;
  font-size: 0.75rem;
  color: #EF4444;
}

.tags-input {
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  padding: 8px;
  min-height: 48px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.tags-input:focus-within {
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  background: #3B82F6;
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tag-remove {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.tag-remove:hover {
  background: rgba(255, 255, 255, 0.2);
}

.tag-input {
  border: none;
  outline: none;
  flex: 1;
  min-width: 120px;
  padding: 4px;
  font-size: 0.875rem;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-checkbox {
  width: 16px;
  height: 16px;
  accent-color: #3B82F6;
}

.checkbox-label {
  font-size: 0.875rem;
  color: #374151;
  cursor: pointer;
  margin: 0;
}

.image-upload {
  text-align: center;
}

.image-preview {
  position: relative;
  display: inline-block;
  margin-bottom: 16px;
}

.image-preview img {
  width: 300px;
  height: 169px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #E5E7EB;
}

.image-remove {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.image-remove:hover {
  background: rgba(0, 0, 0, 0.9);
}

.image-placeholder {
  border: 2px dashed #D1D5DB;
  border-radius: 8px;
  padding: 40px 20px;
  margin-bottom: 16px;
  color: #6B7280;
}

.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 8px;
}

.image-placeholder p {
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 4px;
}

.image-placeholder small {
  font-size: 0.75rem;
}

.image-input {
  display: none;
}

.upload-btn {
  background: #3B82F6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.upload-btn:hover {
  background: #2563EB;
}

.form-actions {
  padding: 24px 32px;
  background: #F9FAFB;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3B82F6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563EB;
}

.btn-outline {
  background: transparent;
  color: #6B7280;
  border: 1px solid #D1D5DB;
}

.btn-outline:hover:not(:disabled) {
  background: #F9FAFB;
  border-color: #9CA3AF;
}

/* Responsive */
@media (max-width: 768px) {
  .course-form {
    padding: 16px;
  }
  
  .form-section {
    padding: 24px 20px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .form-actions {
    padding: 20px;
    flex-direction: column;
  }
  
  .image-preview img {
    width: 100%;
    max-width: 300px;
    height: auto;
  }
}
</style>