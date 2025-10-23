<template>
  <router-view />
  <footer class="bg-white shadow-inner mt-16">
    <div class="container mx-auto px-4 py-6 text-center text-[#2C597D]">
      <p class="text-sm">© 2024 Medical Diagnosis System | Built with Vue.js, Django, FastAPI</p>
      <p class="text-xs text-gray-500 mt-1">Powered by AI · Trusted by Healthcare Professionals</p>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'App'
}
</script>

