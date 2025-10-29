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

        <router-link 
          to="/chat"
          class="block px-6 py-3 rounded-r-full hover:bg-white/10 transition text-[#00BCD4] bg-white border-2 border-transparent max-w-[200px]"
          active-class="!text-orange-500 !border-orange-500"
        >
          <span class="font-semibold text-lg">Chat</span>
        </router-link>

        <router-link 
          to="/diagnoses"
          class="block px-6 py-3 rounded-r-full hover:bg-white/10 transition text-[#00BCD4] bg-white border-2 border-transparent max-w-[200px]"
          active-class="!text-orange-500 !border-orange-500"
        >
          <span class="font-semibold text-lg">Diagnoses</span>
        </router-link>

        <button 
          type="button"
          @click="confirmLogout"
          class="block w-full text-left px-6 py-3 rounded-r-full hover:bg-white/10 transition text-[#00BCD4] bg-white border-2 border-transparent max-w-[200px]"
        >
          <span class="font-semibold text-lg">Logout</span>
        </button>
      </nav>

    </aside>

    <!-- Content -->
    <div class="flex-1 flex flex-col">
      <!-- Top bar -->
      <header class="bg-white shadow-sm">
        <div class="px-6 py-4 flex items-center justify-between gap-4">
          <h2 class="text-xl font-semibold text-[#2C597D] flex-shrink-0">{{ title }}</h2>
          
          <!-- Global Search -->
          <div class="flex-1 max-w-md relative">
            <input
              v-model="searchQuery"
              @input="handleSearchInput"
              @focus="showSearchResults = true"
              type="text"
              placeholder="Search patients, diagnoses, messages..."
              class="w-full px-4 py-2 pl-10 border rounded-lg focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent"
            />
            <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            
            <!-- Search Results Dropdown -->
            <div v-if="showSearchResults && (searchResults.total > 0 || searchLoading)" class="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-xl border max-h-96 overflow-y-auto z-50">
              <div v-if="searchLoading" class="p-4 text-center text-gray-500">
                Searching...
              </div>
              <div v-else>
                <!-- Patients -->
                <div v-if="searchResults.patients.length > 0" class="border-b">
                  <div class="px-4 py-2 bg-gray-50 text-xs font-semibold text-gray-600">PATIENTS ({{ searchResults.patients.length }})</div>
                  <router-link
                    v-for="patient in searchResults.patients"
                    :key="patient.id"
                    :to="`/patients/${patient.id}`"
                    @click="closeSearch"
                    class="block px-4 py-3 hover:bg-gray-50 transition"
                  >
                    <div class="font-semibold text-[#2C597D]">{{ patient.full_name }}</div>
                    <div class="text-sm text-gray-500">MRN: {{ patient.mrn }} • {{ patient.phone }}</div>
                  </router-link>
                </div>
                
                <!-- Diagnoses -->
                <div v-if="searchResults.diagnoses.length > 0" class="border-b">
                  <div class="px-4 py-2 bg-gray-50 text-xs font-semibold text-gray-600">DIAGNOSES ({{ searchResults.diagnoses.length }})</div>
                  <router-link
                    v-for="diagnosis in searchResults.diagnoses"
                    :key="diagnosis.id"
                    :to="`/patients/${diagnosis.patient_data?.id}`"
                    @click="closeSearch"
                    class="block px-4 py-3 hover:bg-gray-50 transition"
                  >
                    <div class="font-semibold text-[#2C597D]">{{ diagnosis.diagnosis }}</div>
                    <div class="text-sm text-gray-500">{{ diagnosis.patient_data?.full_name }} • Confidence: {{ (diagnosis.confidence * 100).toFixed(1) }}%</div>
                  </router-link>
                </div>
                
                <!-- Messages -->
                <div v-if="searchResults.messages.length > 0">
                  <div class="px-4 py-2 bg-gray-50 text-xs font-semibold text-gray-600">MESSAGES ({{ searchResults.messages.length }})</div>
                  <router-link
                    v-for="message in searchResults.messages"
                    :key="message.id"
                    :to="`/chat?room=${message.room_id}`"
                    @click="closeSearch"
                    class="block px-4 py-3 hover:bg-gray-50 transition"
                  >
                    <div class="font-semibold text-[#2C597D]">{{ message.sender.full_name || message.sender.username }}</div>
                    <div class="text-sm text-gray-700 line-clamp-2">{{ message.content }}</div>
                    <div class="text-xs text-gray-500 mt-1">{{ message.room_name }} • {{ formatSearchDate(message.created_at) }}</div>
                  </router-link>
                </div>
              </div>
            </div>
            
            <!-- No Results -->
            <div v-if="showSearchResults && searchResults.total === 0 && !searchLoading && searchQuery.length >= 2" class="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-xl border p-4 text-center text-gray-500 z-50">
              No results found for "{{ searchQuery }}"
            </div>
          </div>
          
          <!-- User Profile -->
          <div class="flex items-center space-x-4">
            <!-- Notification Dropdown -->
            <div class="relative">
              <button 
                @click="toggleNotifications" 
                class="relative p-2 hover:bg-gray-50 rounded-lg transition group"
              >
                <svg class="w-6 h-6 text-gray-600 group-hover:text-[#00BCD4] transition" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
                </svg>
                <span v-if="unreadCount > 0" class="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full min-w-[20px]">
                  {{ unreadCount > 99 ? '99+' : unreadCount }}
                </span>
              </button>

              <!-- Notification Dropdown Panel -->
              <transition name="dropdown">
                <div v-if="showNotifications" class="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border z-50 max-h-96 overflow-hidden flex flex-col">
                  <div class="px-4 py-3 border-b bg-gray-50">
                    <h3 class="font-semibold text-gray-800">Notifications</h3>
                  </div>
                  
                  <div v-if="loadingNotifications" class="p-4 text-center text-gray-500">
                    Loading...
                  </div>
                  
                  <div v-else-if="notifications.length === 0" class="p-8 text-center text-gray-500">
                    <svg class="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                    </svg>
                    <p class="text-sm">No new notifications</p>
                  </div>
                  
                  <div v-else class="overflow-y-auto flex-1">
                    <router-link
                      v-for="notif in notifications"
                      :key="notif.room_id"
                      :to="`/chat?room=${notif.room_id}`"
                      @click="closeNotifications"
                      class="block px-4 py-3 hover:bg-gray-50 transition border-b last:border-b-0"
                    >
                      <div class="flex items-start gap-3">
                        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#00BCD4] to-[#00ACC1] text-white flex items-center justify-center font-semibold flex-shrink-0">
                          {{ notif.room_name.charAt(0).toUpperCase() }}
                        </div>
                        <div class="flex-1 min-w-0">
                          <div class="font-semibold text-sm text-[#2C597D] truncate">{{ notif.room_name }}</div>
                          <div class="text-sm text-gray-700 line-clamp-2">{{ notif.last_message }}</div>
                          <div class="flex items-center gap-2 mt-1">
                            <span class="inline-flex items-center justify-center px-2 py-0.5 text-xs font-bold text-white bg-red-600 rounded-full">
                              {{ notif.unread_count }}
                            </span>
                            <span class="text-xs text-gray-500">{{ formatNotifTime(notif.last_message_time) }}</span>
                          </div>
                        </div>
                      </div>
                    </router-link>
                  </div>
                  
                  <div class="px-4 py-3 border-t bg-gray-50">
                    <router-link to="/chat" @click="closeNotifications" class="text-sm text-[#00BCD4] hover:text-[#00ACC1] font-semibold">
                      View all messages →
                    </router-link>
                  </div>
                </div>
              </transition>
            </div>

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

    <!-- Contacts panel on the right (collapsible) -->
    <ContactsPanel v-if="!contactsCollapsed" :current-user-id="currentUserId" @open-chat="openChatWithUser" />
    <!-- Collapse/expand button -->
    <button
      class="fixed right-2 top-1/2 -translate-y-1/2 z-30 bg-white border rounded-full w-8 h-8 flex items-center justify-center shadow hover:bg-gray-50"
      @click="contactsCollapsed = !contactsCollapsed"
      :title="contactsCollapsed ? 'Show contacts' : 'Hide contacts'"
    >
      <span v-if="contactsCollapsed">❮</span>
      <span v-else>❯</span>
    </button>

    <!-- Floating chat windows (like Facebook) -->
    <template v-for="(win, idx) in openRooms" :key="win.id">
      <ChatWindow
        :room="win"
        :current-user-id="currentUserId"
        :offset-right="(contactsCollapsed ? 16 : 304) + idx * 336"
        @close="closeWindow"
      />
    </template>

    <!-- Toast Notification -->
    <transition name="fade">
      <div v-if="showToast" class="fixed top-4 right-4 z-50 bg-white shadow-xl rounded-lg p-4 w-80 border cursor-pointer" @click="openChatFromToast">
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#00BCD4] to-[#00ACC1] text-white flex items-center justify-center font-semibold">
            💬
          </div>
          <div class="flex-1">
            <div class="text-xs text-gray-500">New message from</div>
            <div class="font-semibold text-[#2C597D]">{{ toastSender }}</div>
            <div class="text-sm text-gray-700 line-clamp-2 mt-1">{{ toastContent }}</div>
          </div>
        </div>
      </div>
    </transition>

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
import ContactsPanel from './ContactsPanel.vue'
import ChatWindow from './ChatWindow.vue'

export default {
  props: {
    title: { type: String, default: '' },
  },
  components: { ContactsPanel, ChatWindow },
  data() {
    return {
      showLogoutModal: false,
      // Notification WS
      notifWs: null,
      showToast: false,
      toastSender: '',
      toastContent: '',
      toastRoomId: null,
      toastRoomName: '',
      unreadCount: 0,
      searchQuery: '',
      searchResults: { patients: [], diagnoses: [], messages: [], total: 0 },
      searchLoading: false,
      showSearchResults: false,
      searchTimeout: null,
      // Notification dropdown
      showNotifications: false,
      notifications: [],
      loadingNotifications: false,
      notificationsSeen: false, // Track if user has seen notifications
      // Floating chat windows state
      openRooms: [],
      userId: (() => {
        try {
          const cached = localStorage.getItem('user')
          return cached ? JSON.parse(cached).id : null
        } catch {
          return null
        }
      })(),
      // Collapsible contacts panel
      contactsCollapsed: false,
    }
  },
  computed: {
    profile() {
      return userStore.profile
    },
    currentUserId() {
      // Try profile first, then userId from localStorage, then try to get from cached user
      let id = this.profile?.id || this.userId
      
      // If still null, try to read from localStorage directly
      if (!id) {
        try {
          const cached = localStorage.getItem('user')
          if (cached) {
            const user = JSON.parse(cached)
            id = user.id
            // Update userId for next time
            if (id && !this.userId) {
              this.userId = id
            }
          }
        } catch (e) {
          console.error('Failed to parse user from localStorage:', e)
        }
      }
      
      console.log(`🆔 currentUserId computed: profile.id=${this.profile?.id}, userId=${this.userId}, result=${id}`)
      return id
    }
  },
  async mounted() {
    await this.loadProfile()
    this.connectNotifyWebSocket()
    this.fetchUnreadCount()
    // Poll unread count every 30 seconds
    this.unreadInterval = setInterval(() => {
      this.fetchUnreadCount()
    }, 30000)
    // Listen for messages marked as read
    window.addEventListener('messages-marked-read', this.handleMessagesRead)
    // Listen for open chat room event from ChatView
    window.addEventListener('open-chat-room', this.handleOpenChatRoom)
    // Close search on click outside
    document.addEventListener('click', this.handleClickOutside)
    // Restore open chat windows
    try {
      const saved = JSON.parse(localStorage.getItem('open_rooms') || '[]')
      console.log(`🔄 Restoring open rooms from localStorage:`, saved)
      if (Array.isArray(saved) && saved.length) {
        import('../services/api').then(async ({ getChatRoom }) => {
          for (const id of saved) {
            try {
              console.log(`🔄 Fetching room details for ${id}`)
              const room = await getChatRoom(id)
              console.log(`🔄 Fetched room:`, room)
              if (!this.openRooms.find(r => String(r.id) === String(room.id))) {
                this.openRooms.push(room)
                console.log(`🔄 Added room ${room.id} to openRooms`)
              }
            } catch (error) {
              console.error(`❌ Failed to restore room ${id}:`, error)
            }
          }
        })
      }
    } catch (error) {
      console.error(`❌ Failed to restore rooms:`, error)
    }
  },
  beforeUnmount() {
    if (this.unreadInterval) {
      clearInterval(this.unreadInterval)
    }
    window.removeEventListener('messages-marked-read', this.handleMessagesRead)
    window.removeEventListener('open-chat-room', this.handleOpenChatRoom)
    document.removeEventListener('click', this.handleClickOutside)
  },
  methods: {
    async loadProfile() {
      try {
        await userStore.fetchProfile()
        console.log('✅ Profile loaded:', userStore.profile)
      } catch (e) {
        console.error('❌ Failed to load profile:', e)
        // token invalid, redirect to login
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    },
    async fetchUnreadCount() {
      try {
        const { getUnreadCount } = await import('../services/api')
        const data = await getUnreadCount()
        const newCount = data.unread_count || 0
        
        // Only update if notifications haven't been seen, or if count increased
        if (!this.notificationsSeen || newCount > this.unreadCount) {
          this.unreadCount = newCount
          if (newCount > this.unreadCount) {
            this.notificationsSeen = false // New messages arrived
          }
        }
      } catch (e) {
        // Silently fail
      }
    },
    handleMessagesRead(event) {
      // Decrement unread count when messages are marked as read
      const count = event.detail?.count || 0
      this.unreadCount = Math.max(0, this.unreadCount - count)
      // Reset seen flag so badge can show again if needed
      this.notificationsSeen = false
    },
    handleOpenChatRoom(event) {
      const room = event.detail?.room
      if (!room) return
      
      // Check if already open
      const idx = this.openRooms.findIndex(r => String(r.id) === String(room.id))
      if (idx !== -1) {
        // Bring to front
        const [existing] = this.openRooms.splice(idx, 1)
        this.openRooms.push(existing)
      } else {
        // Add new
        this.openRooms.push(room)
      }
    },
    handleSearchInput() {
      clearTimeout(this.searchTimeout)
      if (this.searchQuery.length < 2) {
        this.searchResults = { patients: [], diagnoses: [], messages: [], total: 0 }
        this.showSearchResults = false
        return
      }
      this.searchTimeout = setTimeout(() => {
        this.performSearch()
      }, 300)
    },
    async performSearch() {
      try {
        this.searchLoading = true
        console.log('🔍 Searching for:', this.searchQuery)
        const { globalSearch } = await import('../services/api')
        const results = await globalSearch(this.searchQuery)
        console.log('✅ Search results:', results)
        this.searchResults = results
        this.showSearchResults = true
      } catch (e) {
        console.error('❌ Search failed:', e)
        console.error('Error details:', e.response?.data || e.message)
        this.searchResults = { patients: [], diagnoses: [], messages: [], total: 0 }
      } finally {
        this.searchLoading = false
      }
    },
    closeSearch() {
      this.showSearchResults = false
      this.searchQuery = ''
      this.searchResults = { patients: [], diagnoses: [], messages: [], total: 0 }
    },
    formatSearchDate(timestamp) {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      if (days === 0) return 'Today'
      if (days === 1) return 'Yesterday'
      if (days < 7) return `${days} days ago`
      return date.toLocaleDateString()
    },
    handleClickOutside(event) {
      const searchContainer = event.target.closest('.flex-1.max-w-md')
      if (!searchContainer && this.showSearchResults) {
        this.showSearchResults = false
      }
    },
    connectNotifyWebSocket() {
      try {
        const token = localStorage.getItem('token')
        if (!token) return

        // Build WS URL properly (ws/wss) and backend host from Vite env or current hostname
        const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        let host = 'localhost:8000'
        try {
          if (import.meta && import.meta.env && import.meta.env.VITE_API_URL) {
            host = import.meta.env.VITE_API_URL.replace('http://', '').replace('https://', '')
          } else if (window.location.hostname !== 'localhost') {
            host = `${window.location.hostname}:8000`
          }
        } catch (e) {}

        const wsUrl = `${proto}//${host}/ws/notify/?token=${encodeURIComponent(token)}`
        this.notifWs = new WebSocket(wsUrl)

        this.notifWs.onmessage = event => {
          try {
            const data = JSON.parse(event.data)
            if (data.type === 'notification') {
              // Only show toast for receiver (not sender)
              this.showToastNotification(data.sender, data.content, data.room_id, data.room_name)
              window.dispatchEvent(new CustomEvent('chat-notification', { detail: data }))
              // Increment unread count
              this.unreadCount++
            }
          } catch (e) { /* ignore */ }
        }

        this.notifWs.onclose = () => {
          // retry later
          setTimeout(() => this.connectNotifyWebSocket(), 5000)
        }
        this.notifWs.onerror = () => {
          // avoid crashing the app
        }
      } catch (e) {
        // swallow to prevent white screen
      }
    },
    showToastNotification(sender, content, roomId, roomName) {
      this.showToast = true
      this.toastSender = sender
      this.toastContent = content
      this.toastRoomId = roomId
      this.toastRoomName = roomName || ''
      setTimeout(() => { this.showToast = false }, 5000)
    },
    openChatFromToast() {
      this.showToast = false
      if (!this.toastRoomId) {
        this.$router.push({ name: 'Chat' })
        return
      }
      // Navigate to chat and trigger room selection via query param
      this.$router.push({ name: 'Chat', query: { room: this.toastRoomId } })
    },
    async openChatWithUser(user) {
      try {
        const currentId = String(this.profile?.id || this.userId || '')
        if (!currentId) {
          console.warn('⚠️ Cannot open chat: current user id missing')
          return
        }

        const normalizeId = (value) => {
          if (value === null || value === undefined) return null
          if (typeof value === 'object') {
            if ('id' in value) return normalizeId(value.id)
            if ('value' in value) return normalizeId(value.value)
          }
          return String(value)
        }

        const targetId = String(user.id)
        const idx = this.openRooms.findIndex(room => {
          if (room.room_type !== 'direct') return false
          const members = room.members || []
          if (members.length !== 2) return false
          const ids = members.map(m => normalizeId(m.id)).filter(Boolean)
          return ids.includes(targetId) && ids.includes(currentId)
        })

        if (idx !== -1) {
          const [existing] = this.openRooms.splice(idx, 1)
          this.openRooms.push(existing)
          return
        }

        const { createChatRoom, getChatRoom } = await import('../services/api')
        const created = await createChatRoom({ room_type: 'direct', member_ids: [user.id], name: '' })
        const roomId = created?.id
        if (!roomId) return

        const detailed = await getChatRoom(roomId).catch(() => created)

        if (!this.openRooms.find(room => String(room.id) === String(roomId))) {
          this.openRooms.push(detailed)
        } else {
          this.openRooms = this.openRooms.map(room => String(room.id) === String(roomId) ? detailed : room)
        }
      } catch (e) {
        console.error(`❌ Error opening chat with user:`, e)
      }
    },
    closeWindow(roomId) {
      this.openRooms = this.openRooms.filter(r => String(r.id) !== String(roomId))
    },
    async toggleNotifications() {
      this.showNotifications = !this.showNotifications
      if (this.showNotifications) {
        await this.loadNotifications()
        this.notificationsSeen = true
      }
    },
    async loadNotifications() {
      try {
        this.loadingNotifications = true
        const { listChatRooms } = await import('../services/api')
        const data = await listChatRooms({ pageSize: 50 })
        
        const rooms = data.results || []
        this.notifications = rooms
          .filter(room => room.unread_count && room.unread_count > 0)
          .map(room => {
            let roomName = 'Chat'
            if (room.name) {
              roomName = room.name
            } else if (room.members && Array.isArray(room.members)) {
              roomName = room.members
                .map(m => m.full_name || m.username || 'User')
                .join(', ')
            }
            
            return {
              room_id: room.id,
              room_name: roomName,
              unread_count: room.unread_count,
              last_message: room.last_message?.content || 'New message',
              last_message_time: room.last_message?.created_at || room.updated_at || new Date().toISOString()
            }
          })
          .sort((a, b) => new Date(b.last_message_time) - new Date(a.last_message_time))
      } catch (e) {
        console.error('❌ Failed to load notifications:', e)
        this.notifications = []
      } finally {
        this.loadingNotifications = false
      }
    },
    closeNotifications() {
      this.showNotifications = false
    },
    formatNotifTime(timestamp) {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      const minutes = Math.floor(diff / (1000 * 60))
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      
      if (minutes < 1) return 'Just now'
      if (minutes < 60) return `${minutes}m ago`
      if (hours < 24) return `${hours}h ago`
      if (days < 7) return `${days}d ago`
      return date.toLocaleDateString()
    },
    confirmLogout() {
      this.showLogoutModal = true
    },
    logout() {
      userStore.clearProfile()
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('open_rooms')
      
      // Dispatch event to notify other components
      window.dispatchEvent(new CustomEvent('user-changed'))
      
      this.showLogoutModal = false
      window.location.href = '/login'
    },
  },
  watch: {
    openRooms: {
      deep: true,
      handler(newVal) {
        try {
          const ids = newVal.map(r => r.id)
          localStorage.setItem('open_rooms', JSON.stringify(ids))
        } catch {}
      }
    }
  }
}
</script>

<style scoped>
/* Dropdown animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Fade animation for toast */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Line clamp utility */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
