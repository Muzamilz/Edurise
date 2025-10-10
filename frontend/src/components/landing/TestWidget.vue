<template>
  <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999; width: 70px; height: 70px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.3);" @click="showAlert">
    AI
  </div>
</template>

<script setup lang="ts">
const showAlert = () => {
  alert('AI Widget is working!')
}
</script>