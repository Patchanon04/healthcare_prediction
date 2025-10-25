<template>
  <div class="min-h-screen bg-gradient-to-br from-[#00838F] via-[#4DD0E1] to-white flex items-center justify-center p-6">
    <div class="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
      <!-- Login Form -->
      <div class="p-8 max-w-md w-full mx-auto md:mx-0">
        <div class="mb-8">
          <h2 class="text-3xl font-bold text-white mb-2">OPEN BRAIN Health System</h2>
          <p class="text-white/80">Sign in to access your medical diagnosis</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Username Field -->
          <div>
            <label class="block text-sm font-medium text-white mb-2">Username</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
              <input 
                v-model="username" 
                class="w-full pl-12 pr-4 py-3 bg-white/20 backdrop-blur-sm border-2 border-white/30 rounded-xl focus:outline-none focus:border-white/60 text-white placeholder-white/60 transition" 
                placeholder="Enter your username" 
              />
            </div>
          </div>

          <!-- Password Field -->
          <div>
            <label class="block text-sm font-medium text-white mb-2">Password</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
                </svg>
              </div>
              <input 
                type="password" 
                v-model="password" 
                class="w-full pl-12 pr-4 py-3 bg-white/20 backdrop-blur-sm border-2 border-white/30 rounded-xl focus:outline-none focus:border-white/60 text-white placeholder-white/60 transition" 
                placeholder="Enter your password" 
              />
            </div>
          </div>

          <!-- Login Button -->
          <button 
            :disabled="loading" 
            class="w-full bg-white text-[#00BCD4] rounded-xl py-3 font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Signing in...' : 'Login' }}
          </button>

          <!-- Register Link -->
          <div class="text-center">
            <span class="text-white/80 text-sm">Don't have an account? </span>
            <router-link to="/register" class="text-white text-sm font-semibold hover:underline">Register</router-link>
          </div>
        </form>
      </div>

      <!-- Right Illustration (semi-transparent over gradient) -->
      <div class="hidden md:flex items-center justify-center">
        <img :src="Brain" alt="OPEN BRAIN" class="w-[460px] h-auto object-contain opacity-90 md:opacity-95 drop-shadow-2xl filter saturate-150 contrast-110" />
      </div>

    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { login } from '../services/api'
import Brain from '../assets/brain.png'

export default {
  name: 'LoginView',
  setup() {
    const toast = useToast()
    const username = ref('')
    const password = ref('')
    const loading = ref(false)

    const handleLogin = async () => {
      if (!username.value || !password.value) return
      loading.value = true
      try {
        const data = await login({ username: username.value, password: password.value })
        localStorage.setItem('token', data.token)
        toast.success('Welcome!')
        window.location.href = '/patients'
      } catch (e) {
        toast.error(e.message)
      } finally {
        loading.value = false
      }
    }

    return { username, password, loading, handleLogin, Brain }
  }
}
</script>
