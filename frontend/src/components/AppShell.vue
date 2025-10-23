<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex">
    <!-- Sidebar -->
    <aside class="w-60 bg-white/80 backdrop-blur shadow-md p-4 hidden md:block">
      <div class="flex items-center space-x-2 mb-6">
        <span class="font-bold text-gray-700">MedAI</span>
      </div>
      <nav class="space-y-2">
        <router-link to="/home" class="block px-3 py-2 rounded hover:bg-blue-100" active-class="bg-blue-200 font-semibold">Home</router-link>
        <router-link to="/predict" class="block px-3 py-2 rounded hover:bg-blue-100" active-class="bg-blue-200 font-semibold">Predict</router-link>
      </nav>
    </aside>

    <!-- Content -->
    <div class="flex-1 flex flex-col">
      <!-- Top bar -->
      <header class="bg-white shadow-sm">
        <div class="container mx-auto px-4 py-3 flex items-center justify-between">
          <div class="font-semibold text-gray-700">{{ title }}</div>
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded-full bg-blue-200 flex items-center justify-center">👤</div>
            <div class="text-sm">
              <div class="font-semibold">{{ user?.username || 'Doctor' }}</div>
              <div class="text-gray-500 text-xs">Logged in</div>
            </div>
            <button @click="logout" class="ml-4 text-sm text-red-600 hover:underline">Logout</button>
          </div>
        </div>
      </header>

      <!-- Main -->
      <main class="container mx-auto px-4 py-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { me } from '../services/api'

export default {
  name: 'AppShell',
  props: { title: { type: String, default: '' } },
  setup() {
    const user = ref(null)

    const fetchMe = async () => {
      try {
        user.value = await me()
      } catch (e) {
        // token invalid, redirect to login
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    }

    const logout = () => {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }

    onMounted(fetchMe)

    return { user, logout }
  }
}
</script>
