<template>
  <div class="notification-settings">
    <div class="settings-header">
      <h3 class="text-lg font-semibold text-gray-900">Notification Settings</h3>
      <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
        <XMarkIcon class="w-5 h-5" />
      </button>
    </div>

    <div class="settings-content">
      <!-- General Settings -->
      <div class="settings-section">
        <h4 class="section-title">General</h4>
        
        <div class="setting-item">
          <div class="setting-info">
            <label class="setting-label">Sound Notifications</label>
            <p class="setting-description">Play sound when new notifications arrive</p>
          </div>
          <ToggleSwitch 
            v-model="localPreferences.sound_enabled"
            @update:modelValue="updateSetting('sound_enabled', $event)"
          />
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <label class="setting-label">Browser Notifications</label>
            <p class="setting-description">Show desktop notifications</p>
          </div>
          <ToggleSwitch 
            v-model="localPreferences.browser_notifications"
            @update:modelValue="updateSetting('browser_notifications', $event)"
          />
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <label class="setting-label">Email Notifications</label>
            <p class="setting-description">Receive notifications via email</p>
          </div>
          <ToggleSwitch 
            v-model="localPreferences.email_notifications"
            @update:modelValue="updateSetting('email_notifications', $event)"
          />
        </div>
      </div>

      <!-- Category Settings -->
      <div class="settings-section">
        <h4 class="section-title">Categories</h4>
        <p class="section-description">Choose which types of notifications you want to receive</p>
        
        <div class="category-list">
          <div 
            v-for="category in notificationCategories"
            :key="category.key"
            class="category-item"
          >
            <div class="category-info">
              <div class="category-icon" :class="category.iconClass">
                <component :is="category.icon" class="w-5 h-5" />
              </div>
              <div>
                <label class="category-label">{{ category.label }}</label>
                <p class="category-description">{{ category.description }}</p>
              </div>
            </div>
            <ToggleSwitch 
              v-model="localPreferences.categories[category.key]"
              @update:modelValue="updateCategorySetting(category.key, $event)"
            />
          </div>
        </div>
      </div>

      <!-- Quiet Hours -->
      <div class="settings-section">
        <h4 class="section-title">Quiet Hours</h4>
        <p class="section-description">Disable notifications during specific hours</p>
        
        <div class="setting-item">
          <div class="setting-info">
            <label class="setting-label">Enable Quiet Hours</label>
            <p class="setting-description">Mute notifications during specified time range</p>
          </div>
          <ToggleSwitch 
            v-model="localPreferences.quiet_hours_enabled"
            @update:modelValue="updateSetting('quiet_hours_enabled', $event)"
          />
        </div>

        <div v-if="localPreferences.quiet_hours_enabled" class="quiet-hours-config">
          <div class="time-inputs">
            <div class="time-input">
              <label class="time-label">From</label>
              <input 
                v-model="localPreferences.quiet_hours_start"
                type="time"
                class="time-field"
                @change="updateSetting('quiet_hours_start', ($event.target as HTMLInputElement)?.value)"
              />
            </div>
            <div class="time-input">
              <label class="time-label">To</label>
              <input 
                v-model="localPreferences.quiet_hours_end"
                type="time"
                class="time-field"
                @change="updateSetting('quiet_hours_end', ($event.target as HTMLInputElement)?.value)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="settings-footer">
      <button @click="resetToDefaults" class="reset-btn">
        Reset to Defaults
      </button>
      <div class="footer-actions">
        <button @click="$emit('close')" class="cancel-btn">
          Cancel
        </button>
        <button @click="saveSettings" class="save-btn">
          Save Changes
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
// Removed unused heroicons imports - using emoji icons instead
import ToggleSwitch from '@/components/common/ToggleSwitch.vue'

interface NotificationPreferences {
  sound_enabled: boolean
  browser_notifications: boolean
  email_notifications: boolean
  quiet_hours_enabled: boolean
  quiet_hours_start: string
  quiet_hours_end: string
  categories: Record<string, boolean>
}

interface Props {
  preferences: NotificationPreferences
}

const props = defineProps<Props>()

const emit = defineEmits<{
  update: [preferences: NotificationPreferences]
  close: []
}>()

const localPreferences = reactive<NotificationPreferences>({
  sound_enabled: true,
  browser_notifications: true,
  email_notifications: true,
  quiet_hours_enabled: false,
  quiet_hours_start: '22:00',
  quiet_hours_end: '08:00',
  categories: {
    assignment: true,
    grade: true,
    live_class: true,
    course: true,
    system: true,
    announcement: true,
    reminder: true
  }
})

const notificationCategories = [
  {
    key: 'assignment',
    label: 'Assignments',
    description: 'New assignments, due date reminders, and submissions',
    icon: '📝',
    iconClass: 'bg-blue-100 text-blue-600'
  },
  {
    key: 'grade',
    label: 'Grades',
    description: 'Grade updates and feedback on your work',
    icon: '🎓',
    iconClass: 'bg-green-100 text-green-600'
  },
  {
    key: 'live_class',
    label: 'Live Classes',
    description: 'Class reminders, recordings, and attendance updates',
    icon: '📹',
    iconClass: 'bg-purple-100 text-purple-600'
  },
  {
    key: 'course',
    label: 'Courses',
    description: 'Enrollment updates and course announcements',
    icon: '📚',
    iconClass: 'bg-indigo-100 text-indigo-600'
  },
  {
    key: 'system',
    label: 'System',
    description: 'Platform updates and maintenance notifications',
    icon: 'ℹ️',
    iconClass: 'bg-gray-100 text-gray-600'
  },
  {
    key: 'announcement',
    label: 'Announcements',
    description: 'Important announcements from instructors and admin',
    icon: '📢',
    iconClass: 'bg-yellow-100 text-yellow-600'
  },
  {
    key: 'reminder',
    label: 'Reminders',
    description: 'General reminders and upcoming events',
    icon: '⏰',
    iconClass: 'bg-orange-100 text-orange-600'
  }
]

const updateSetting = (key: keyof NotificationPreferences, value: boolean | string) => {
  (localPreferences as any)[key] = value
}

const updateCategorySetting = (category: string, enabled: boolean) => {
  localPreferences.categories[category] = enabled
}

const saveSettings = () => {
  emit('update', { ...localPreferences })
  emit('close')
}

const resetToDefaults = () => {
  Object.assign(localPreferences, {
    sound_enabled: true,
    browser_notifications: true,
    email_notifications: true,
    quiet_hours_enabled: false,
    quiet_hours_start: '22:00',
    quiet_hours_end: '08:00',
    categories: {
      assignment: true,
      grade: true,
      live_class: true,
      course: true,
      system: true,
      announcement: true,
      reminder: true
    }
  })
}

onMounted(() => {
  // Initialize with current preferences
  Object.assign(localPreferences, props.preferences)
})
</script>

<style scoped>
.notification-settings {
  @apply absolute inset-0 bg-white rounded-lg flex flex-col;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.98);
  animation: slideInFromRight 0.3s ease-out;
}

@keyframes slideInFromRight {
  0% {
    transform: translateX(100%);
    opacity: 0;
  }
  100% {
    transform: translateX(0);
    opacity: 1;
  }
}

.settings-header {
  @apply flex items-center justify-between p-4 border-b border-gray-200;
}

.settings-content {
  @apply flex-1 overflow-y-auto p-4 space-y-6;
}

.settings-section {
  @apply space-y-4;
}

.section-title {
  @apply text-base font-semibold text-gray-900;
}

.section-description {
  @apply text-sm text-gray-600 -mt-1;
}

.setting-item {
  @apply flex items-center justify-between gap-4;
}

.setting-info {
  @apply flex-1;
}

.setting-label {
  @apply block text-sm font-medium text-gray-900;
}

.setting-description {
  @apply text-xs text-gray-500 mt-0.5;
}

.category-list {
  @apply space-y-3;
}

.category-item {
  @apply flex items-center justify-between gap-4 p-3 rounded-lg border border-gray-200 transition-all duration-200 hover:border-gray-300 hover:shadow-sm;
}

.category-info {
  @apply flex items-center gap-3 flex-1;
}

.category-icon {
  @apply w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0;
}

.category-label {
  @apply block text-sm font-medium text-gray-900;
}

.category-description {
  @apply text-xs text-gray-500 mt-0.5;
}

.quiet-hours-config {
  @apply mt-3 p-3 bg-gray-50 rounded-lg;
}

.time-inputs {
  @apply flex gap-4;
}

.time-input {
  @apply flex-1;
}

.time-label {
  @apply block text-xs font-medium text-gray-700 mb-1;
}

.time-field {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

.settings-footer {
  @apply flex items-center justify-between p-4 border-t border-gray-200;
}

.reset-btn {
  @apply text-sm text-gray-600 hover:text-gray-800 underline;
}

.footer-actions {
  @apply flex gap-2;
}

.cancel-btn {
  @apply px-4 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50;
}

.save-btn {
  @apply px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700;
}
</style>