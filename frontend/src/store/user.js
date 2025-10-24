import { reactive } from 'vue'
import { getProfile, me } from '../services/api'

export const userStore = reactive({
  profile: null,
  loading: false,
  
  async fetchProfile() {
    if (this.profile) return this.profile // Return cached data

    this.loading = true
    try {
      const profile = await getProfile()
      // Fallback: ensure username present even if profile lacks it
      if (!profile.username) {
        try {
          const who = await me()
          profile.username = who.username
          profile.email = profile.email || who.email
        } catch (_) {
          // ignore fallback errors
        }
      }
      this.profile = profile
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
