import { reactive } from 'vue'
import { getProfile } from '../services/api'

export const userStore = reactive({
  profile: null,
  loading: false,
  
  async fetchProfile() {
    if (this.profile) return this.profile // Return cached data
    
    this.loading = true
    try {
      this.profile = await getProfile()
      return this.profile
    } catch (error) {
      console.error('Failed to fetch profile:', error)
      throw error
    } finally {
      this.loading = false
    }
  },
  
  clearProfile() {
    this.profile = null
  }
})
