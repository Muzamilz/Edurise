<template>
  <div class="course-card" @click="$emit('click', course)">
    <div class="course-image">
      <img 
        :src="course.thumbnail || '/placeholder-course.jpg'" 
        :alt="course.title"
        class="course-thumbnail"
      />
      <div class="course-badge" v-if="course.difficulty_level">
        {{ course.difficulty_level }}
      </div>
      <div class="course-price" v-if="course.price">
        ${{ course.price }}
      </div>
      <div class="course-price free" v-else>
        Free
      </div>
    </div>
    
    <div class="course-content">
      <div class="course-category">
        {{ formatCategory(course.category) }}
      </div>
      
      <h3 class="course-title">{{ course.title }}</h3>
      
      <p class="course-description">
        {{ truncateText(course.description, 100) }}
      </p>
      
      <div class="course-instructor">
        <span class="instructor-name">
          {{ course.instructor.first_name }} {{ course.instructor.last_name }}
        </span>
      </div>
      
      <div class="course-meta">
        <div class="course-rating" v-if="course.average_rating > 0">
          <div class="stars">
            <span 
              v-for="star in 5" 
              :key="star"
              class="star"
              :class="{ filled: star <= Math.round(course.average_rating) }"
            >
              ★
            </span>
          </div>
          <span class="rating-text">{{ course.average_rating.toFixed(1) }}</span>
        </div>
        
        <div class="course-stats">
          <span class="stat">
            <i class="icon-users"></i>
            {{ course.total_enrollments }} students
          </span>
          <span class="stat">
            <i class="icon-clock"></i>
            {{ course.duration_weeks }} weeks
          </span>
        </div>
      </div>
      
      <div class="course-tags" v-if="course.tags && course.tags.length > 0">
        <span 
          v-for="tag in course.tags.slice(0, 3)" 
          :key="tag"
          class="tag"
        >
          {{ tag }}
        </span>
      </div>
    </div>
    
    <div class="course-actions">
      <button 
        v-if="showEnrollButton && !isEnrolled"
        @click.stop="$emit('enroll', course)"
        class="btn btn-primary"
        :disabled="loading"
      >
        {{ loading ? 'Enrolling...' : 'Enroll Now' }}
      </button>
      
      <button 
        v-else-if="isEnrolled"
        @click.stop="$emit('continue', course)"
        class="btn btn-secondary"
      >
        Continue Learning
      </button>
      
      <button 
        v-if="showEditButton"
        @click.stop="$emit('edit', course)"
        class="btn btn-outline"
      >
        Edit
      </button>
      
      <button 
        v-if="showDeleteButton"
        @click.stop="$emit('delete', course)"
        class="btn btn-danger"
      >
        Delete
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Course } from '../../types/api'

interface Props {
  course: Course
  isEnrolled?: boolean
  showEnrollButton?: boolean
  showEditButton?: boolean
  showDeleteButton?: boolean
  loading?: boolean
}

interface Emits {
  (e: 'click', course: Course): void
  (e: 'enroll', course: Course): void
  (e: 'continue', course: Course): void
  (e: 'edit', course: Course): void
  (e: 'delete', course: Course): void
}

withDefaults(defineProps<Props>(), {
  isEnrolled: false,
  showEnrollButton: true,
  showEditButton: false,
  showDeleteButton: false,
  loading: false
})

defineEmits<Emits>()

const formatCategory = (category: string | null | undefined) => {
  if (!category || typeof category !== 'string') return 'General'
  return category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')
}

const truncateText = (text: string, maxLength: number) => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
</script>

<style scoped>
.course-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 243, 226, 0.3));
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.course-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 35px rgba(245, 158, 11, 0.2);
}

.course-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.course-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.course-card:hover .course-thumbnail {
  transform: scale(1.05);
}

.course-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.course-price {
  position: absolute;
  top: 12px;
  right: 12px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.course-price.free {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.3);
}

.course-content {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.course-category {
  color: #6B7280;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.course-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 12px;
  line-height: 1.4;
}

.course-description {
  color: #6B7280;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 16px;
  flex: 1;
}

.course-instructor {
  margin-bottom: 16px;
}

.instructor-name {
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
}

.course-meta {
  margin-bottom: 16px;
}

.course-rating {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.stars {
  display: flex;
  gap: 2px;
}

.star {
  color: #D1D5DB;
  font-size: 1rem;
}

.star.filled {
  color: #F59E0B;
}

.rating-text {
  color: #6B7280;
  font-size: 0.875rem;
  font-weight: 500;
}

.course-stats {
  display: flex;
  gap: 16px;
}

.stat {
  color: #6B7280;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 4px;
}

.course-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.tag {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  color: #92400e;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.course-actions {
  padding: 20px;
  border-top: 1px solid rgba(245, 158, 11, 0.1);
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  flex: 1;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  color: #92400e;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #fed7aa, #fdba74);
  border-color: #f59e0b;
}

.btn-outline {
  background: transparent;
  color: #6B7280;
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.btn-outline:hover {
  background: linear-gradient(135deg, #fef3e2, #fed7aa);
  border-color: #f59e0b;
  color: #374151;
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.btn-danger:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
}

/* Responsive */
@media (max-width: 768px) {
  .course-content {
    padding: 16px;
  }
  
  .course-actions {
    padding: 16px;
    flex-direction: column;
  }
  
  .course-stats {
    flex-direction: column;
    gap: 8px;
  }
}
</style>