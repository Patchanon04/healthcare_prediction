<template>
  <div class="min-h-screen bg-gradient-to-br from-[#B2EBF2] to-[#E0F7FA] flex">
    <!-- Sidebar -->
    <aside class="w-64 bg-[#00BCD4] shadow-lg flex flex-col hidden md:flex">
      <!-- Logo/Brand -->
      <div class="p-6 border-b border-white/20">
        <h1 class="text-2xl font-bold text-white">MedML</h1>
        <p class="text-xs text-white/80 mt-1">Medical Diagnosis System</p>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 space-y-3">
        <router-link 
          to="/home" 
          class="flex items-center space-x-3 px-6 py-3 rounded-r-full hover:bg-white/10 transition group text-[#00BCD4] bg-white mr-4"
          active-class="!bg-white !text-[#00BCD4] shadow-md"
        >
          <span class="font-semibold text-lg">Home</span>
        </router-link>

        <router-link 
          to="/predict" 
          class="flex items-center space-x-3 px-6 py-3 rounded-r-full hover:bg-white/10 transition group text-[#00BCD4] bg-white mr-4"
          active-class="!bg-white !text-[#00BCD4] shadow-md"
        >
          <span class="font-semibold text-lg">Predict</span>
        </router-link>

        <button 
          @click="logout"
          class="flex items-center space-x-3 px-6 py-3 rounded-r-full hover:bg-white/10 transition group text-[#00BCD4] bg-white mr-4 w-full text-left"
        >
          <span class="font-semibold text-lg">Logout</span>
        </button>
      </nav>

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
              <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#00BCD4] to-[#00ACC1] flex items-center justify-center text-white font-semibold">
                {{ (profile?.full_name || profile?.username || 'U').charAt(0).toUpperCase() }}
              </div>
              <div class="text-sm">
                <div class="font-semibold text-[#2C597D]">{{ profile?.full_name || profile?.username || 'User' }}</div>
                <div class="text-gray-500 text-xs capitalize">{{ profile?.role || 'Medical Professional' }}</div>
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
import { onMounted } from 'vue'
import { userStore } from '../store/user'

export default {
  name: 'AppShell',
  props: { title: { type: String, default: '' } },
  setup() {
    const fetchProfile = async () => {
      try {
        await userStore.fetchProfile()
      } catch (e) {
        // token invalid, redirect to login
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    }

    const logout = () => {
      userStore.clearProfile()
      localStorage.removeItem('token')
      window.location.href = '/login'
    }

    onMounted(fetchProfile)

    return { profile: userStore.profile, logout }
  }
}
</script>
