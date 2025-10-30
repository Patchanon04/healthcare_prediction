<template>
  <div v-if="isPublicRoute">
    <!-- Public routes (login) without AppShell -->
    <router-view />
  </div>
  <AppShell v-else :title="currentTitle">
    <!-- Protected routes with AppShell -->
    <router-view />
  </AppShell>
  
  <footer class="bg-white shadow-inner mt-16">
    <div class="container mx-auto px-4 py-6 text-center text-[#2C597D]">
      <p class="text-sm">© 2025 OPEN BRAIN Medical Diagnosis System | Built with Vue.js, Django, FastAPI</p>
      <p class="text-xs text-gray-500 mt-1">Powered by OPEN BRAIN · Trusted by Healthcare Professionals (Trust me bro)</p>
    </div>
  </footer>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from './components/AppShell.vue'

export default {
  name: 'App',
  components: { AppShell },
  setup() {
    const route = useRoute()
    
    const isPublicRoute = computed(() => {
      return route.meta?.public === true
    })
    
    const currentTitle = computed(() => {
      return route.meta?.title || ''
    })
    
    return {
      isPublicRoute,
      currentTitle
    }
  }
}
</script>

