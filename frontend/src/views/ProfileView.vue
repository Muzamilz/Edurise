<template>
  <div class="profile-view">
    <UserProfile />
  </div>
</template>

<script setup lang="ts">
import UserProfile from '@/components/profile/UserProfile.vue'
</script>

<style scoped>
.profile-view {
  min-height: 100vh;
  background: #f9fafb;
}
</style>