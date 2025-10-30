<template>
  <AppShell title="Profile">
    <div class="max-w-4xl mx-auto">
      <div class="bg-white rounded-2xl shadow-lg p-8">
        <!-- Profile Header -->
        <div class="flex items-center space-x-6 mb-8 pb-6 border-b border-gray-200">
          <div class="relative group">
            <!-- Avatar -->
            <div v-if="!avatarPreview" class="w-24 h-24 rounded-full bg-gradient-to-br from-[#00BCD4] to-[#00ACC1] flex items-center justify-center text-white text-3xl font-bold">
              {{ (profile?.full_name || profile?.username || 'U').charAt(0).toUpperCase() }}
            </div>
            <img v-else :src="avatarPreview" class="w-24 h-24 rounded-full object-cover" alt="Profile" />
            
            <!-- Upload Overlay -->
            <label class="absolute inset-0 flex items-center justify-center bg-black/50 rounded-full opacity-0 group-hover:opacity-100 transition cursor-pointer">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
              <input type="file" @change="handleAvatarChange" accept="image/*" class="hidden" />
            </label>
          </div>
          <div>
            <h2 class="text-2xl font-bold text-[#2C597D]">{{ profile?.full_name || profile?.username || 'User' }}</h2>
            <p class="text-gray-500 capitalize">{{ profile?.role || 'Medical Professional' }}</p>
            <p class="text-sm text-gray-400 mt-1">Member since {{ new Date().getFullYear() }}</p>
          </div>
        </div>

        <!-- Profile Form -->
        <form @submit.prevent="handleSave" class="space-y-6">
          <!-- Name -->
          <div>
            <label class="block text-sm font-medium text-[#2C597D] mb-2">Full Name</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-[#7CC6D2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
              <input 
                v-model="form.full_name" 
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
                v-model="form.email" 
                type="email"
                class="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition" 
                placeholder="your.email@example.com" 
              />
            </div>
          </div>

          <!-- Contact -->
          <div>
            <label class="block text-sm font-medium text-[#2C597D] mb-2">Contact Number</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-[#7CC6D2]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                </svg>
              </div>
              <input 
                v-model="form.contact" 
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
                v-model="form.role" 
                class="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-[#7CC6D2] transition appearance-none"
              >
                <option value="doctor">Doctor</option>
                <option value="nurse">Nurse</option>
                <option value="specialist">Specialist</option>
                <option value="researcher">Researcher</option>
              </select>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex space-x-4 pt-4">
            <button 
              type="submit"
              :disabled="loading"
              class="flex-1 bg-gradient-to-r from-[#00BCD4] to-[#00ACC1] text-white rounded-xl py-3 font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ loading ? 'Saving...' : 'Save Changes' }}
            </button>
            <button 
              type="button"
              @click="handleCancel"
              class="flex-1 bg-gray-100 text-gray-700 rounded-xl py-3 font-semibold hover:bg-gray-200 transition"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </AppShell>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import AppShell from '../components/AppShell.vue'
import { updateProfile } from '../services/api'
import { userStore } from '../store/user'

export default {
  name: 'ProfileView',
  components: { AppShell },
  setup() {
    const toast = useToast()
    const loading = ref(false)
    const avatarPreview = ref(null)
    const avatarFile = ref(null)
    const form = ref({
      full_name: '',
      email: '',
      contact: '',
      role: 'doctor'
    })

    const fetchProfile = async () => {
      try {
        await userStore.fetchProfile()
        const profile = userStore.profile
        // Populate form with profile data
        form.value.full_name = profile.full_name || ''
        form.value.email = profile.email || ''
        form.value.contact = profile.contact || ''
        form.value.role = profile.role || 'doctor'
        avatarPreview.value = profile.avatar || null
      } catch (e) {
        toast.error('Failed to load profile')
      }
    }

    const handleAvatarChange = (event) => {
      const file = event.target.files[0]
      if (!file) return

      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast.error('Please select an image file')
        return
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast.error('Image size must be less than 5MB')
        return
      }

      avatarFile.value = file

      // Preview image
      const reader = new FileReader()
      reader.onload = (e) => {
        avatarPreview.value = e.target.result
      }
      reader.readAsDataURL(file)

      toast.success('Image selected! Click Save to upload.')
    }

    const handleSave = async () => {
      loading.value = true
      try {
        // If there's a new avatar, upload it first
        if (avatarFile.value) {
          const formData = new FormData()
          formData.append('avatar', avatarFile.value)
          formData.append('full_name', form.value.full_name)
          formData.append('contact', form.value.contact)
          formData.append('role', form.value.role)
          
          await updateProfile(formData)
          avatarFile.value = null
        } else {
          await updateProfile(form.value)
        }
        
        // Update store with new data
        await userStore.fetchProfile()
        toast.success('Profile updated successfully!')
      } catch (e) {
        toast.error('Failed to update profile')
      } finally {
        loading.value = false
      }
    }

    const handleCancel = () => {
      fetchProfile() // Reset form
      avatarFile.value = null
      toast.info('Changes cancelled')
    }

    onMounted(fetchProfile)

    return { 
      profile: userStore.profile, 
      form, 
      loading, 
      avatarPreview,
      handleAvatarChange,
      handleSave, 
      handleCancel 
    }
  }
}
</script>
