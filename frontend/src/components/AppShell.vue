<template>
  <div class="min-h-screen bg-gradient-to-br from-[#00838F] via-[#4DD0E1] to-white flex">
    <!-- Sidebar -->
    <aside class="w-64 bg-gradient-to-b from-[#006064] to-[#00838F] shadow-lg flex flex-col hidden md:flex">
      <!-- Logo/Brand -->
      <div class="p-6 border-b border-white/20">
        <h1 class="text-2xl font-bold text-white">MedML</h1>
        <p class="text-xs text-white/80 mt-1">Medical Diagnosis System</p>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 space-y-3">
        <router-link 
          to="/dashboard" 
          class="block px-6 py-3 rounded-r-full hover:bg-white/10 transition text-[#00BCD4] bg-white border-2 border-transparent max-w-[200px]"
          active-class="!text-orange-500 !border-orange-500"
        >
          <span class="font-semibold text-lg">Dashboard</span>
        </router-link>

        <router-link 
          to="/patients" 
          class="block px-6 py-3 rounded-r-full hover:bg-white/10 transition text-[#00BCD4] bg-white border-2 border-transparent max-w-[200px]"
          active-class="!text-orange-500 !border-orange-500"
        >
          <span class="font-semibold text-lg">Patient</span>
        </router-link>

        <button 
          type="button"
          @click="confirmLogout"
          class="block text-left px-6 py-3 rounded-r-full hover:bg-white/10 transition text-[#00BCD4] bg-white border-2 border-transparent max-w-[200px]"
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
            <router-link to="/profile" class="flex items-center space-x-3 hover:bg-gray-50 px-3 py-2 rounded-lg transition group">
              <div v-if="!profile?.avatar" class="w-10 h-10 rounded-full bg-gradient-to-br from-[#00BCD4] to-[#00ACC1] flex items-center justify-center text-white font-semibold">
                {{ (profile?.full_name || profile?.username || 'U').charAt(0).toUpperCase() }}
              </div>
              <img v-else :src="profile.avatar" class="w-10 h-10 rounded-full object-cover" alt="Profile" />
              <div class="text-sm">
                <div class="font-semibold text-[#2C597D] group-hover:text-[#00BCD4] transition">{{ profile?.full_name || profile?.username || 'User' }}</div>
                <div class="text-gray-500 text-xs capitalize">{{ profile?.role || 'Medical Professional' }}</div>
              </div>
              <svg class="w-5 h-5 text-gray-400 group-hover:text-[#00BCD4] transition" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </router-link>
          </div>
        </div>
      </header>

      <!-- Main -->
      <main class="flex-1 p-6 overflow-auto">
        <slot />
      </main>
    </div>

    <!-- Logout Confirmation Modal -->
    <div v-if="showLogoutModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click="showLogoutModal = false">
      <div class="bg-white rounded-xl shadow-2xl p-6 max-w-sm w-full mx-4" @click.stop>
        <div class="text-center mb-6">
          <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">Confirm Logout</h3>
          <p class="text-gray-600">Are you sure you want to logout?</p>
        </div>
        <div class="flex gap-3">
          <button 
            @click="showLogoutModal = false"
            class="flex-1 px-4 py-2 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-semibold"
          >
            Cancel
          </button>
          <button 
            @click="logout"
            class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-semibold"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { userStore } from '../store/user'

export default {
  name: 'AppShell',
  props: { title: { type: String, default: '' } },
  setup() {
    const showLogoutModal = ref(false)

    const fetchProfile = async () => {
      try {
        await userStore.fetchProfile()
      } catch (e) {
        // token invalid, redirect to login
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    }

    const confirmLogout = () => {
      showLogoutModal.value = true
    }

    const logout = () => {
      userStore.clearProfile()
      localStorage.removeItem('token')
      window.location.href = '/login'
    }

    onMounted(fetchProfile)

    return { profile: userStore.profile, showLogoutModal, confirmLogout, logout }
  }
}
</script>
