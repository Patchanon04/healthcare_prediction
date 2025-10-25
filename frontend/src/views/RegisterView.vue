<template>
  <div class="min-h-screen bg-gradient-to-br from-[#00838F] via-[#4DD0E1] to-white flex items-center justify-center p-6">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
      <div class="mb-8">
        <h2 class="text-3xl font-bold text-[#2C597D] mb-2">Create Account</h2>
        <p class="text-gray-500">Join our medical diagnosis system</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-5">
        <!-- Username -->
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
              required
              class="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition" 
              placeholder="Enter username" 
            />
          </div>
        </div>

        <!-- Full Name -->
        <div>
          <label class="block text-sm font-medium text-[#2C597D] mb-2">Full Name</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="w-5 h-5 text-[#7CC6D2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <input 
              v-model="fullName" 
              required
              class="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition" 
              placeholder="Enter your full name" 
            />
          </div>
        </div>

        <!-- Email -->
        <div>
          <label class="block text-sm font-medium text-[#2C597D] mb-2">Email Address</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="w-5 h-5 text-[#7CC6D2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
              </svg>
            </div>
            <input 
              v-model="email" 
              type="email"
              required
              class="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition" 
              placeholder="your.email@example.com" 
            />
          </div>
        </div>

        <!-- Contact (Optional) -->
        <div>
          <label class="block text-sm font-medium text-[#2C597D] mb-2">
            Contact Number <span class="text-gray-400 text-xs">(Optional)</span>
          </label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="w-5 h-5 text-[#7CC6D2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
              </svg>
            </div>
            <input 
              v-model="contact" 
              class="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition" 
              placeholder="081-234-5678" 
            />
          </div>
        </div>

        <!-- Role -->
        <div>
          <label class="block text-sm font-medium text-[#2C597D] mb-2">Role</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="w-5 h-5 text-[#7CC6D2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
              </svg>
            </div>
            <select 
              v-model="role" 
              class="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition appearance-none bg-white"
            >
              <option value="doctor">Doctor</option>
              <option value="nurse">Nurse</option>
              <option value="specialist">Specialist</option>
              <option value="researcher">Researcher</option>
            </select>
          </div>
        </div>

        <!-- Password -->
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
              required
              minlength="6"
              class="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition" 
              placeholder="Enter password (min 6 characters)" 
          </div>
        </div>

        <!-- Submit Button -->
        <button 
          :disabled="loading" 
          class="w-full bg-gradient-to-r from-[#00BCD4] to-[#00ACC1] text-white rounded-xl py-3 font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>

        <!-- Login Link -->
        <div class="text-center pt-2">
          <span class="text-gray-600 text-sm">Already have an account? </span>
          <router-link to="/login" class="text-[#00BCD4] text-sm font-semibold hover:underline">Login</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { register, updateProfile } from '../services/api'

export default {
  name: 'RegisterView',
  setup() {
    const router = useRouter()
    const toast = useToast()
    const username = ref('')
    const fullName = ref('')
    const email = ref('')
    const contact = ref('')
    const role = ref('doctor')
    const password = ref('')
    const loading = ref(false)

    const handleRegister = async () => {
      if (!username.value || !password.value || !fullName.value || !email.value) {
        toast.error('Please fill in all required fields')
        return
      }
      loading.value = true
      try {
        // Register user
        const data = await register({ 
          username: username.value, 
          email: email.value, 
          password: password.value 
        })
        localStorage.setItem('token', data.token)
        
        // Update profile with additional info
        await updateProfile({
          full_name: fullName.value,
          email: email.value,
          contact: contact.value,
          role: role.value
        })
        
        toast.success('Account created successfully!')
        router.push('/patients')
      } catch (e) {
        toast.error(e.message)
      } finally {
        loading.value = false
      }
    }

    return { username, fullName, email, contact, role, password, loading, handleRegister }
  }
}
</script>
