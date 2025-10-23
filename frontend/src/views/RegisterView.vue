<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-6">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-8">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center space-x-2">
          <span class="text-3xl">💙</span>
          <h1 class="text-2xl font-bold text-gray-800">Register</h1>
        </div>
        <router-link to="/login" class="text-blue-600 text-sm hover:underline">Login</router-link>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-sm text-gray-600 mb-1">Username</label>
          <input v-model="username" class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring" placeholder="username" />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">Email</label>
          <input v-model="email" class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring" placeholder="you@example.com" />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">Password</label>
          <input type="password" v-model="password" class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring" placeholder="••••••" />
        </div>
        <button :disabled="loading" class="w-full bg-blue-600 text-white rounded-lg py-2 font-semibold hover:bg-blue-700 disabled:bg-gray-300">Create Account</button>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import { register } from '../services/api'

export default {
  name: 'RegisterView',
  setup() {
    const toast = useToast()
    const username = ref('')
    const email = ref('')
    const password = ref('')
    const loading = ref(false)

    const handleRegister = async () => {
      if (!username.value || !password.value) return
      loading.value = true
      try {
        const data = await register({ username: username.value, email: email.value, password: password.value })
        localStorage.setItem('token', data.token)
        toast.success('Account created!')
        window.location.href = '/home'
      } catch (e) {
        toast.error(e.message)
      } finally {
        loading.value = false
      }
    }

    return { username, email, password, loading, handleRegister }
  }
}
</script>
