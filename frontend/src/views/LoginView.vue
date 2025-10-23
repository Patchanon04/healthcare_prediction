<template>
  <div class="min-h-screen bg-gradient-to-br from-[#00BCD4] via-[#4DD0E1] to-[#80DEEA] flex items-center justify-center p-6">
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
      <div class="hidden md:flex md:w-1/2 bg-gradient-to-br from-[#00BCD4] to-[#26C6DA] items-center justify-center p-12 relative overflow-hidden">
        <!-- Background decorative elements -->
        <div class="absolute inset-0 opacity-10">
          <div class="absolute top-20 right-20 w-64 h-64 bg-white rounded-full"></div>
          <div class="absolute bottom-10 left-10 w-48 h-48 bg-white rounded-full"></div>
        </div>
        
        <div class="relative z-10 text-center">
          <!-- Colorful Brain & Doctors Illustration -->
          <div class="mb-6">
            <svg class="w-80 h-80 mx-auto" viewBox="0 0 300 300" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Colorful Brain -->
              <g transform="translate(180, 40)">
                <!-- Brain outline -->
                <path d="M 50 20 Q 80 10 90 30 Q 100 20 110 35 Q 115 25 120 40 Q 120 60 115 75 Q 110 85 100 90 Q 85 95 70 90 Q 55 85 45 75 Q 35 60 40 40 Q 42 28 50 20 Z" fill="#FFA726" opacity="0.9"/>
                <path d="M 55 25 Q 70 20 80 30 Q 88 25 95 35 Q 100 45 98 60 Q 95 70 85 75 Q 75 78 65 75 Q 55 70 50 60 Q 48 45 55 25 Z" fill="#FF6B9D" opacity="0.8"/>
                <path d="M 70 30 Q 80 28 88 38 Q 92 48 90 58 Q 87 65 78 68 Q 70 70 63 65 Q 58 58 60 48 Q 62 38 70 30 Z" fill="#AB47BC" opacity="0.8"/>
                <path d="M 75 40 Q 82 38 87 45 Q 90 52 87 58 Q 83 62 76 62 Q 70 60 68 53 Q 67 46 75 40 Z" fill="#5C6BC0" opacity="0.9"/>
                <path d="M 65 45 Q 70 43 74 48 Q 76 53 73 57 Q 70 59 66 57 Q 63 54 64 49 Q 64 46 65 45 Z" fill="#26C6DA" opacity="0.9"/>
                <path d="M 80 48 Q 84 47 87 51 Q 88 55 85 58 Q 82 59 79 57 Q 77 54 78 51 Q 78 49 80 48 Z" fill="#66BB6A" opacity="0.9"/>
                
                <!-- Brain connection lines -->
                <path d="M 80 70 Q 85 75 90 80" stroke="#00BCD4" stroke-width="3" fill="none" opacity="0.6"/>
                <path d="M 75 72 Q 78 78 80 85" stroke="#00BCD4" stroke-width="2.5" fill="none" opacity="0.6"/>
              </g>
              
              <!-- Doctor 1 (Male) -->
              <g transform="translate(30, 120)">
                <!-- Head -->
                <circle cx="35" cy="30" r="18" fill="#8D6E63"/>
                <!-- Hair -->
                <path d="M 20 25 Q 25 15 35 15 Q 45 15 50 25" fill="#5D4037"/>
                <!-- Body (white coat) -->
                <rect x="15" y="50" width="40" height="70" rx="8" fill="white"/>
                <!-- Shirt -->
                <rect x="20" y="55" width="30" height="20" fill="#00897B"/>
                <!-- Coat details -->
                <line x1="35" y1="55" x2="35" y2="115" stroke="#00BCD4" stroke-width="2"/>
                <circle cx="30" cy="65" r="2" fill="#00BCD4"/>
                <circle cx="40" cy="65" r="2" fill="#00BCD4"/>
                <!-- Arms -->
                <rect x="10" y="60" width="8" height="40" rx="4" fill="#8D6E63"/>
                <rect x="52" y="60" width="8" height="40" rx="4" fill="#8D6E63"/>
                <!-- Pants -->
                <rect x="18" y="115" width="15" height="35" fill="#00897B"/>
                <rect x="37" y="115" width="15" height="35" fill="#00897B"/>
                <!-- Shoes -->
                <ellipse cx="25" cy="152" rx="8" ry="4" fill="white"/>
                <ellipse cx="45" cy="152" rx="8" ry="4" fill="white"/>
              </g>
              
              <!-- Doctor 2 (Female) -->
              <g transform="translate(110, 130)">
                <!-- Head -->
                <circle cx="30" cy="25" r="16" fill="#D4A574"/>
                <!-- Hair -->
                <path d="M 15 20 Q 20 10 30 10 Q 40 10 45 20 L 45 35 Q 42 40 38 42 L 35 45 Q 33 48 30 48 Q 27 48 25 45 L 22 42 Q 18 40 15 35 Z" fill="#6D4C41"/>
                <!-- Body (white coat) -->
                <rect x="12" y="42" width="36" height="60" rx="8" fill="white"/>
                <!-- Dress/Shirt -->
                <rect x="15" y="47" width="30" height="25" fill="#1976D2"/>
                <!-- Coat details -->
                <line x1="30" y1="47" x2="30" y2="98" stroke="#00BCD4" stroke-width="2"/>
                <circle cx="24" cy="55" r="2" fill="#00BCD4"/>
                <circle cx="36" cy="55" r="2" fill="#00BCD4"/>
                <!-- Arms -->
                <rect x="7" y="50" width="7" height="35" rx="3" fill="#D4A574"/>
                <rect x="46" y="50" width="7" height="35" rx="3" fill="#D4A574"/>
                <!-- Holding tablet -->
                <rect x="45" y="70" width="15" height="20" rx="2" fill="#455A64"/>
                <rect x="47" y="72" width="11" height="16" fill="#B3E5FC"/>
                <!-- Skirt -->
                <path d="M 15 98 L 12 120 L 48 120 L 45 98 Z" fill="#1976D2"/>
                <!-- Legs -->
                <rect x="18" y="118" width="8" height="25" fill="#D4A574"/>
                <rect x="34" y="118" width="8" height="25" fill="#D4A574"/>
                <!-- Shoes -->
                <ellipse cx="22" cy="145" rx="6" ry="3" fill="#5E35B1"/>
                <ellipse cx="38" cy="145" rx="6" ry="3" fill="#5E35B1"/>
              </g>
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-white mb-2">Welcome Back!</h3>
          <p class="text-white/90">AI-Powered Medical Diagnosis System</p>
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
