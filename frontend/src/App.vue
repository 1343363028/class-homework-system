<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSubjectStore } from '@/stores/subject'

const auth = useAuthStore()
const subjectStore = useSubjectStore()

onMounted(async () => {
  if (auth.isLoggedIn) {
    await auth.fetchMe()
    if (auth.isLoggedIn) await subjectStore.load()
  }
})
</script>

<template>
  <div class="app-root">
    <div class="grid-bg"></div>
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<style scoped>
.app-root { position: relative; min-height: 100vh; z-index: 1; }
</style>
