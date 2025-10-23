<template>
  <div class="min-h-screen bg-gradient-to-br from-[#E9F7FB] via-[#D4EEF5] to-[#7CC6D2] flex items-center justify-center p-6">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-5xl overflow-hidden flex">
      <!-- Left Side - Login Form -->
      <div class="w-full md:w-1/2 p-12">
        <div class="mb-8">
          <h2 class="text-3xl font-bold text-[#2C597D] mb-2">Your Health System</h2>
          <p class="text-gray-500">Sign in to access your medical dashboard</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Username Field -->
          <div>
            <label class="block text-sm font-medium text-[#2C597D] mb-2">Username</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-[#7CC6D2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
              <input 
                v-model="username" 
                class="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition" 
                placeholder="Enter your username" 
              />
            </div>
          </div>

          <!-- Password Field -->
          <div>
            <label class="block text-sm font-medium text-[#2C597D] mb-2">Password</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-[#7CC6D2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
                </svg>
              </div>
              <input 
                type="password" 
                v-model="password" 
                class="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition" 
                placeholder="Enter your password" 
              />
            </div>
          </div>

          <!-- Login Button -->
          <button 
            :disabled="loading" 
            class="w-full bg-gradient-to-r from-[#7CC6D2] to-[#5AB4C4] text-white rounded-xl py-3 font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Signing in...' : 'Login' }}
          </button>

          <!-- Register Link -->
          <div class="text-center">
            <span class="text-gray-600 text-sm">Don't have an account? </span>
            <router-link to="/register" class="text-[#7CC6D2] text-sm font-semibold hover:underline">Register</router-link>
          </div>
        </form>
      </div>

      <!-- Right Side - Medical Illustration -->
      <div class="hidden md:flex md:w-1/2 bg-gradient-to-br from-[#7CC6D2] to-[#5AB4C4] items-center justify-center p-12">
        <div class="text-center">
          <!-- Doctor Illustration (SVG) -->
          <div class="mb-6">
            <svg class="w-64 h-64 mx-auto" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Doctor 1 -->
              <circle cx="70" cy="60" r="20" fill="#2C597D"/>
              <rect x="50" y="85" width="40" height="60" rx="8" fill="white"/>
              <rect x="55" y="90" width="30" height="3" fill="#7CC6D2"/>
              <circle cx="65" cy="100" r="2" fill="#E74C3C"/>
              
              <!-- Doctor 2 -->
              <circle cx="130" cy="70" r="18" fill="#2C597D"/>
              <rect x="112" y="92" width="36" height="55" rx="8" fill="white"/>
              <rect x="117" y="97" width="26" height="3" fill="#7CC6D2"/>
              
              <!-- Medical Cross -->
              <rect x="95" y="150" width="10" height="30" rx="2" fill="white"/>
              <rect x="85" y="160" width="30" height="10" rx="2" fill="white"/>
              
              <!-- Stethoscope -->
              <path d="M 60 120 Q 65 130 70 120" stroke="white" stroke-width="3" fill="none"/>
              <circle cx="60" cy="120" r="4" fill="white"/>
              <circle cx="70" cy="120" r="4" fill="white"/>
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-white mb-2">Welcome Back!</h3>
          <p class="text-white/90">Access your medical diagnosis system</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { login } from '../services/api'

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
        window.location.href = '/home'
      } catch (e) {
        toast.error(e.message)
      } finally {
        loading.value = false
      }
    }

    return { username, password, loading, handleLogin }
  }
}
</script>
