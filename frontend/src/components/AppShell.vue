<template>
  <div class="min-h-screen bg-gradient-to-br from-[#E9F7FB] to-[#D4EEF5] flex">
    <!-- Sidebar -->
    <aside class="w-64 bg-white shadow-lg flex flex-col hidden md:flex">
      <!-- Logo/Brand -->
      <div class="p-6 border-b border-gray-100">
        <h1 class="text-2xl font-bold text-[#2C597D]">MedML</h1>
        <p class="text-xs text-gray-500 mt-1">Medical Diagnosis System</p>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 space-y-2">
        <router-link 
          to="/home" 
          class="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-[#E9F7FB] transition group"
          active-class="bg-gradient-to-r from-[#7CC6D2] to-[#5AB4C4] text-white hover:bg-gradient-to-r"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
          </svg>
          <span class="font-medium">Home</span>
        </router-link>

        <router-link 
          to="/predict" 
          class="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-[#E9F7FB] transition group"
          active-class="bg-gradient-to-r from-[#7CC6D2] to-[#5AB4C4] text-white hover:bg-gradient-to-r"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
          </svg>
          <span class="font-medium">Predict</span>
        </router-link>

        <router-link 
          to="/profile" 
          class="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-[#E9F7FB] transition group"
          active-class="bg-gradient-to-r from-[#7CC6D2] to-[#5AB4C4] text-white hover:bg-gradient-to-r"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
          </svg>
          <span class="font-medium">Profile</span>
        </router-link>
      </nav>

      <!-- Logout Button -->
      <div class="p-4 border-t border-gray-100">
        <button 
          @click="logout" 
          class="w-full flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-red-50 text-red-600 transition"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
          </svg>
          <span class="font-medium">Logout</span>
        </button>
      </div>
    </aside>

    <!-- Content -->
    <div class="flex-1 flex flex-col">
      <!-- Top bar -->
      <header class="bg-white shadow-sm">
        <div class="px-6 py-4 flex items-center justify-between">
          <h2 class="text-xl font-semibold text-[#2C597D]">{{ title }}</h2>
          
          <!-- User Profile -->
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#7CC6D2] to-[#5AB4C4] flex items-center justify-center text-white font-semibold">
                {{ (user?.username || 'D').charAt(0).toUpperCase() }}
              </div>
              <div class="text-sm">
                <div class="font-semibold text-[#2C597D]">Dr. {{ user?.username || 'User' }}</div>
                <div class="text-gray-500 text-xs">Medical Professional</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Main -->
      <main class="flex-1 p-6 overflow-auto">
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
