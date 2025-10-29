<template>
  <button
    type="button"
    class="toggle-switch"
    :class="{ 'toggle-switch--enabled': modelValue }"
    @click="toggle"
    :disabled="disabled"
  >
    <span class="toggle-slider" :class="{ 'toggle-slider--enabled': modelValue }">
      <span class="toggle-thumb" :class="{ 'toggle-thumb--enabled': modelValue }"></span>
    </span>
    <span class="sr-only">{{ modelValue ? 'Enabled' : 'Disabled' }}</span>
  </button>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const toggle = () => {
  if (!props.disabled) {
    emit('update:modelValue', !props.modelValue)
  }
}
</script>

<style scoped>
.toggle-switch {
  @apply relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed;
  @apply bg-gray-200;
}

.toggle-switch--enabled {
  @apply bg-blue-600;
}

.toggle-slider {
  @apply inline-block h-4 w-4 transform rounded-full bg-white transition-transform;
}

.toggle-thumb {
  @apply absolute left-1 top-1 h-4 w-4 rounded-full bg-white transition-transform;
}

.toggle-thumb--enabled {
  @apply translate-x-5;
}
</style>