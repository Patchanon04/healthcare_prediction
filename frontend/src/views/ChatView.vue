<template>
  <AppShell title="Chat">
    <div class="flex h-[calc(100vh-120px)] bg-gray-50 rounded-xl shadow overflow-hidden">
      <!-- Left Sidebar: Room List -->
      <div class="w-80 bg-white border-r flex flex-col">
        <!-- Header -->
        <div class="p-4 border-b">
          <button @click="showNewChatModal = true" class="w-full px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition font-semibold">
            + New Chat
          </button>
        </div>

        <!-- Room List -->
        <div class="flex-1 overflow-y-auto">
          <div v-if="loadingRooms" class="p-4 text-center text-gray-500">
            Loading...
          </div>
          <div v-else-if="rooms.length === 0" class="p-4 text-center text-gray-500">
            No chats yet. Start a new conversation!
          </div>
          <div v-else>
            <div
              v-for="room in rooms"
              :key="room.id"
              @click="selectRoom(room)"
              :class="[
                'p-4 border-b cursor-pointer hover:bg-gray-50 transition',
                selectedRoom?.id === room.id ? 'bg-blue-50 border-l-4 border-[#00BCD4]' : ''
              ]"
            >
              <div class="flex items-center justify-between mb-1">
                <h3 class="font-semibold text-gray-800">{{ getRoomName(room) }}</h3>
                <span v-if="room.unread_count > 0" class="bg-red-500 text-white text-xs px-2 py-1 rounded-full">
                  {{ room.unread_count }}
                </span>
              </div>
              <p v-if="room.last_message" class="text-sm text-gray-600 truncate">
                {{ room.last_message.sender }}: {{ room.last_message.content }}
              </p>
              <p v-else class="text-sm text-gray-400 italic">No messages yet</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Chat Area -->
      <div class="flex-1 flex flex-col bg-white">
        <div v-if="!selectedRoom" class="flex-1 flex items-center justify-center text-gray-400">
          <div class="text-center">
            <div class="text-6xl mb-4">💬</div>
            <p class="text-lg">Select a chat to start messaging</p>
          </div>
        </div>

        <template v-else>
          <!-- Chat Header -->
          <div class="p-4 border-b bg-gray-50">
            <h2 class="text-xl font-bold text-gray-800">{{ getRoomName(selectedRoom) }}</h2>
            <p class="text-sm text-gray-500">
              {{ selectedRoom.members.map(m => m.full_name || m.username).join(', ') }}
            </p>
          </div>

          <!-- Messages -->
          <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 flex flex-col">
            <div v-if="loadingMessages" class="text-center text-gray-500">Loading messages...</div>
            <div v-else-if="messages.length === 0" class="text-center text-gray-400">
              No messages yet. Start the conversation!
            </div>
            <div
              v-else
              v-for="(msg, idx) in messages"
              :key="msg.id || idx"
              :class="[
                'flex w-full',
                isSelf(msg) ? 'justify-end' : 'justify-start',
                !isFirstInGroup(idx) ? 'mt-0.5' : 'mt-2'
              ]"
            >
              <!-- Message container with consistent width -->
              <div :class="[
                'flex items-end gap-2',
                isSelf(msg) ? 'flex-row-reverse' : 'flex-row'
              ]">
                <!-- Avatar (left side for others, hidden for self) -->
                <div :class="[
                  'flex-shrink-0',
                  isSelf(msg) ? 'w-0' : 'w-8'
                ]">
                  <div v-if="!isSelf(msg) && isLastInGroup(idx)">
                    <div v-if="msg.sender?.avatar" class="w-8 h-8 rounded-full overflow-hidden border">
                      <img :src="msg.sender.avatar" class="w-full h-full object-cover" alt="avatar" />
                    </div>
                    <div v-else class="w-8 h-8 rounded-full bg-gray-300 text-gray-700 flex items-center justify-center text-sm font-semibold">
                      {{ (msg.sender.full_name || msg.sender.username || '?').charAt(0).toUpperCase() }}
                    </div>
                  </div>
                </div>

                <!-- Message bubble -->
                <div class="relative max-w-[85%]">
                  <div :class="[
                    'rounded-2xl px-4 py-2.5 shadow-sm',
                    isSelf(msg)
                      ? 'bg-[#0084FF] text-white rounded-br-md'
                      : 'bg-gray-200 text-gray-800 rounded-bl-md'
                  ]">
                    <p v-if="!isSelf(msg) && isFirstInGroup(idx)" class="text-xs font-semibold mb-1 opacity-80">
                      {{ msg.sender.full_name || msg.sender.username }}
                    </p>
                    <p class="break-words text-[15px] leading-relaxed">{{ msg.content }}</p>
                    <div class="flex items-center gap-2 mt-1">
                      <span :class="[
                        'text-[10px]',
                        isSelf(msg) ? 'text-blue-100' : 'text-gray-500'
                      ]">{{ formatTime(msg.created_at) }}</span>
                      <!-- Delivery/Read indicators for self -->
                      <span v-if="isSelf(msg)" class="text-[10px] select-none">
                        <template v-if="msg.status === 'read' || msg.is_read">
                          ✓✓
                        </template>
                        <template v-else>
                          ✓
                        </template>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="typingUser" class="text-sm text-gray-500 italic mt-2">
              {{ typingUser }} is typing...
            </div>
          </div>

          <!-- Input -->
          <div class="p-4 border-t bg-gray-50">
            <form @submit.prevent="sendMessageHandler" class="flex gap-2">
              <input
                v-model="newMessage"
                @input="handleTyping"
                type="text"
                placeholder="Type a message..."
                class="flex-1 border rounded-lg px-4 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent"
              />
              <button
                type="submit"
                :disabled="!newMessage.trim()"
                class="px-6 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </form>
          </div>
        </template>
      </div>
    </div>

    <!-- New Chat Modal -->
    <Modal :show="showNewChatModal" title="New Chat" @close="showNewChatModal = false">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Select Users</label>
          <div class="max-h-60 overflow-y-auto border rounded-lg p-2">
            <div v-for="user in availableUsers" :key="user.id" class="flex items-center gap-2 p-2 hover:bg-gray-50 rounded">
              <input
                type="checkbox"
                :id="`user-${user.id}`"
                v-model="selectedUserIds"
                :value="user.id"
                class="w-4 h-4"
              />
              <label :for="`user-${user.id}`" class="flex-1 cursor-pointer">
                {{ user.full_name || user.username }} <span class="text-gray-500 text-sm">({{ user.role }})</span>
              </label>
            </div>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Room Name (optional)</label>
          <input v-model="newRoomName" type="text" placeholder="e.g., Team Discussion" class="w-full border rounded-lg px-3 py-2" />
        </div>
      </div>
      <template #footer>
        <button @click="showNewChatModal = false" class="px-4 py-2 text-gray-600 hover:text-gray-800 transition">
          Cancel
        </button>
        <button @click="createRoom" :disabled="selectedUserIds.length === 0" class="px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition disabled:opacity-50">
          Create
        </button>
      </template>
    </Modal>

    <!-- Error Modal -->
    <Modal :show="showErrorModal" title="Error" @close="showErrorModal = false">
      <p class="text-gray-700">{{ errorMessage }}</p>
      <template #footer>
        <button @click="showErrorModal = false" class="px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition">
          OK
        </button>
      </template>
    </Modal>
  </AppShell>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import Modal from '../components/Modal.vue'
import { listChatRooms, listChatUsers, createChatRoom, listMessages, markMessagesRead, getProfile } from '../services/api'

export default {
  name: 'ChatView',
  components: { AppShell, Modal },
  setup() {
    const route = useRoute()
    const rooms = ref([])
    const selectedRoom = ref(null)
    const messages = ref([])
    const newMessage = ref('')
    const loadingRooms = ref(false)
    const loadingMessages = ref(false)
    const showNewChatModal = ref(false)
    const showErrorModal = ref(false)
    const errorMessage = ref('')
    const availableUsers = ref([])
    const selectedUserIds = ref([])
    const newRoomName = ref('')
    const messagesContainer = ref(null)
    const ws = ref(null)
    const typingUser = ref(null)
    const typingTimeout = ref(null)
    const currentUserId = ref(null)
    const currentUsername = ref(null)
    const GROUP_WINDOW_MS = 5 * 60 * 1000 // 5 minutes

    const showError = (msg) => {
      errorMessage.value = msg
      showErrorModal.value = true
    }

    const fetchRooms = async () => {
      try {
        loadingRooms.value = true
        const data = await listChatRooms()
        rooms.value = data.results || []
      } catch (err) {
        console.error('Failed to load rooms:', err)
        showError('Failed to load chat rooms')
      } finally {
        loadingRooms.value = false
      }
    }

    const fetchUsers = async () => {
      try {
        const data = await listChatUsers()
        availableUsers.value = data.users || []
      } catch (err) {
        console.error('Failed to load users:', err)
      }
    }

    const fetchMessages = async (roomId) => {
      try {
        loadingMessages.value = true
        const data = await listMessages(roomId, { pageSize: 100 })
        messages.value = (data.results || []).map(m => ({
          ...m,
          status: m.is_read ? 'read' : (isSelf(m) ? 'delivered' : undefined),
        }))
        await nextTick()
        scrollToBottom()
        
        // Mark as read
        const unreadIds = messages.value.filter(m => !m.is_read && m.sender.id !== currentUserId.value).map(m => m.id)
        if (unreadIds.length > 0) {
          await markMessagesRead(roomId, unreadIds)
          // Locally clear unread badge for this room
          setRoomUnread(roomId, 0)
          // Notify AppShell to refresh unread count
          window.dispatchEvent(new CustomEvent('messages-marked-read', { detail: { count: unreadIds.length } }))
        }
      } catch (err) {
        console.error('Failed to load messages:', err)
        showError('Failed to load messages')
      } finally {
        loadingMessages.value = false
      }
    }

    const selectRoom = (room) => {
      selectedRoom.value = room
      messages.value = []
      fetchMessages(room.id)
      connectWebSocket(room.id)
    }

    const createRoom = async () => {
      if (selectedUserIds.value.length === 0) return
      
      try {
        const roomType = selectedUserIds.value.length === 1 ? 'direct' : 'group'
        const data = await createChatRoom({
          name: newRoomName.value || '',
          room_type: roomType,
          member_ids: selectedUserIds.value
        })
        
        rooms.value.unshift(data)
        showNewChatModal.value = false
        selectedUserIds.value = []
        newRoomName.value = ''
        selectRoom(data)
      } catch (err) {
        console.error('Failed to create room:', err)
        showError('Failed to create chat room')
      }
    }

    const connectWebSocket = (roomId) => {
      if (ws.value) {
        ws.value.close()
      }

      const token = localStorage.getItem('token')
      // Use backend URL for WebSocket (not frontend URL)
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      
      // Get API URL from env or fallback to current host
      let backendHost = 'localhost:8000'
      if (import.meta && import.meta.env && import.meta.env.VITE_API_URL) {
        backendHost = import.meta.env.VITE_API_URL.replace('http://', '').replace('https://', '')
      } else if (window.location.hostname !== 'localhost') {
        // If not localhost, use current hostname with port 8000
        backendHost = `${window.location.hostname}:8000`
      }
      
      const wsUrl = `${wsProtocol}//${backendHost}/ws/chat/${roomId}/?token=${token}`
      
      console.log('Connecting to WebSocket:', wsUrl)
      ws.value = new WebSocket(wsUrl)
      
      ws.value.onopen = () => {
        console.log('✅ WebSocket connected successfully')
      }
      
      ws.value.onmessage = (event) => {
        console.log('📨 Received WebSocket message:', event.data)
        const data = JSON.parse(event.data)
        
        if (data.type === 'message') {
          console.log('💬 New message:', data.message)
          // Normalize status for self messages
          const m = { ...data.message }
          if (isSelf(m)) m.status = 'delivered'
          messages.value.push(m)
          nextTick(() => scrollToBottom())
          // Auto-mark as read if it's from others and we're viewing this room
          if (!isSelf(m) && selectedRoom.value && m && selectedRoom.value.id) {
            // fire and forget; backend will broadcast read receipt
            markMessagesRead(selectedRoom.value.id, [m.id]).catch(() => {})
            setRoomUnread(selectedRoom.value.id, 0)
          }
        } else if (data.type === 'typing') {
          if (data.is_typing) {
            typingUser.value = data.username
            clearTimeout(typingTimeout.value)
            typingTimeout.value = setTimeout(() => {
              typingUser.value = null
            }, 3000)
          } else {
            typingUser.value = null
          }
        } else if (data.type === 'read') {
          // Mark provided message ids as read if they were sent by me
          const readerId = data.user_id
          if (readerId && String(readerId) !== String(currentUserId.value)) {
            const setIds = new Set(data.message_ids || [])
            messages.value = messages.value.map(msg => {
              if (setIds.has(msg.id) && isSelf(msg)) {
                return { ...msg, status: 'read', is_read: true }
              }
              return msg
            })
          } else if (readerId && String(readerId) === String(currentUserId.value) && selectedRoom.value) {
            // If I am the reader, clear the badge for the active room
            setRoomUnread(selectedRoom.value.id, 0)
          }
        } else if (data.type === 'error') {
          console.error('❌ WebSocket error:', data.message)
          showError(data.message)
        }
        console.error('❌ WebSocket error:', error)
        showError('WebSocket connection error')
      }
      
      ws.value.onclose = (event) => {
        console.log('🔌 WebSocket disconnected:', event.code, event.reason)
        if (event.code !== 1000) {
          showError('Connection lost. Please refresh the page.')
        }
      }
    }

    const sendMessageHandler = () => {
      if (!newMessage.value.trim()) {
        console.warn('⚠️ Cannot send empty message')
        return
      }
      
      if (!ws.value) {
        console.error('❌ WebSocket not connected')
        showError('Not connected to chat server')
        return
      }
      
      if (ws.value.readyState !== WebSocket.OPEN) {
        console.error('❌ WebSocket not ready:', ws.value.readyState)
        showError('Connection not ready. Please wait...')
        return
      }
      
      const messageData = {
        type: 'message',
        content: newMessage.value.trim()
      }
      
      console.log('📤 Sending message:', messageData)
      ws.value.send(JSON.stringify(messageData))
      
      newMessage.value = ''
    }

    const handleTyping = () => {
      if (!ws.value) return
      
      ws.value.send(JSON.stringify({
        type: 'typing',
        is_typing: true
      }))
      
      clearTimeout(typingTimeout.value)
      typingTimeout.value = setTimeout(() => {
        ws.value.send(JSON.stringify({
          type: 'typing',
          is_typing: false
        }))
      }, 1000)
    }

    const scrollToBottom = () => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }

    const getRoomName = (room) => {
      if (room.name) return room.name
      const otherMembers = room.members.filter(m => m.id !== currentUserId.value)
      return otherMembers.map(m => m.full_name || m.username).join(', ') || 'Chat'
    }

    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }

    const loadCurrentUser = async () => {
      try {
        const userStr = localStorage.getItem('user')
        if (userStr) {
          const user = JSON.parse(userStr)
          currentUserId.value = user.id
          currentUsername.value = user.username || null
        } else {
          // Fallback: fetch from API
          const token = localStorage.getItem('token')
          if (token) {
            try {
              const profile = await getProfile()
              currentUserId.value = profile.id || profile.user?.id
              currentUsername.value = profile.username || profile.user?.username
              // Cache for future
              localStorage.setItem('user', JSON.stringify({ id: currentUserId.value, username: currentUsername.value }))
            } catch (e) {
              console.error('Failed to fetch user profile:', e)
            }
          }
        }
      } catch (e) {
        console.error('Failed to parse user from localStorage:', e)
      }
      
      console.log('🔑 Current User ID:', currentUserId.value, 'Username:', currentUsername.value)
    }

    // Handle user change event (dispatched from login/logout)
    const handleUserChange = async (newUserId = null) => {
      console.log('👤 User change detected, reloading...')
      
      // Store current messages before clearing
      const currentMessages = [...messages.value]
      const currentRoomId = selectedRoom.value?.id
      
      await loadCurrentUser()
      
      // Update lastUserId after loading
      lastUserId = currentUserId.value
      console.log('✅ User reloaded. New ID:', lastUserId)
      
      await fetchRooms()
      await fetchUsers()
      
      // Clear current selection
      if (ws.value) {
        ws.value.close()
      }
      selectedRoom.value = null
      messages.value = []
      
      // If we were viewing a room, reload it to force re-render with new user context
      if (currentRoomId && currentMessages.length > 0) {
        await nextTick()
        const room = rooms.value.find(r => r.id === currentRoomId)
        if (room) {
          console.log('🔄 Re-selecting room to force re-render')
          selectRoom(room)
        }
      }
    }

    // Poll for user changes (in case of account switch without page reload)
    let userCheckInterval = null
    let lastUserId = null

    onMounted(async () => {
      await loadCurrentUser()
      lastUserId = currentUserId.value
      
      await fetchRooms()
      await fetchUsers()
      
      // Listen for user change events
      window.addEventListener('user-changed', handleUserChange)
      
      // Poll every 2 seconds to detect user changes
      userCheckInterval = setInterval(() => {
        const userStr = localStorage.getItem('user')
        if (userStr) {
          try {
            const user = JSON.parse(userStr)
            if (user.id && String(user.id) !== String(lastUserId)) {
              console.log('🔄 User ID changed from', lastUserId, 'to', user.id)
              handleUserChange(user.id)
            }
          } catch (e) {
            // ignore
          }
        } else if (lastUserId) {
          // User logged out
          console.log('🚪 User logged out')
          handleUserChange(null)
        }
      }, 2000)
      
      // Auto-select room from query param if present
      if (route.query.room) {
        const roomId = route.query.room
        const room = rooms.value.find(r => String(r.id) === String(roomId))
        if (room) {
          selectRoom(room)
        }
      }
    })

    // Watch for query param changes (e.g., when clicking notification)
    watch(() => route.query.room, (newRoomId) => {
      if (newRoomId) {
        const room = rooms.value.find(r => String(r.id) === String(newRoomId))
        if (room) {
          selectRoom(room)
        }
      }
    })

    onUnmounted(() => {
      if (ws.value) {
        ws.value.close()
      }
      // Remove event listener
      window.removeEventListener('user-changed', handleUserChange)
      // Clear interval
      if (userCheckInterval) {
        clearInterval(userCheckInterval)
      }
    })

    const isSelf = (msg) => {
      const sid = msg?.sender?.id
      const suser = msg?.sender?.username
      // match by id (string-safe) or by username fallback
      if (sid != null && currentUserId.value != null) {
        if (String(sid) === String(currentUserId.value)) return true
      }
      if (suser && currentUsername.value) {
        if (suser === currentUsername.value) return true
      }
      // Debug log for first message
      if (messages.value.length > 0 && msg === messages.value[0]) {
        console.log('🔍 isSelf check:', { msgSenderId: sid, msgSenderUsername: suser, currentUserId: currentUserId.value, currentUsername: currentUsername.value })
      }
      return false
    }

    const sameSender = (a, b) => {
      if (!a || !b) return false
      const aid = a?.sender?.id, bid = b?.sender?.id
      if (aid != null && bid != null) return String(aid) === String(bid)
      const au = a?.sender?.username, bu = b?.sender?.username
      if (au && bu) return au === bu
      return false
    }

    const closeInTime = (a, b) => {
      if (!a || !b) return false
      const ta = new Date(a.created_at).getTime()
      const tb = new Date(b.created_at).getTime()
      return Math.abs(tb - ta) <= GROUP_WINDOW_MS
    }

    const isFirstInGroup = (index) => {
      const msg = messages.value[index]
      const prev = messages.value[index - 1]
      if (!prev) return true
      return !(sameSender(msg, prev) && closeInTime(msg, prev))
    }

    const isLastInGroup = (index) => {
      const msg = messages.value[index]
      const next = messages.value[index + 1]
      if (!next) return true
      return !(sameSender(msg, next) && closeInTime(msg, next))
    }

    // Helper: update unread_count for a room locally
    const setRoomUnread = (roomId, value) => {
      rooms.value = rooms.value.map(r => r.id === roomId ? { ...r, unread_count: value } : r)
      if (selectedRoom.value && selectedRoom.value.id === roomId) {
        selectedRoom.value = { ...selectedRoom.value, unread_count: value }
      }
    }

    return {
      rooms,
      selectedRoom,
      messages,
      newMessage,
      loadingRooms,
      loadingMessages,
      showNewChatModal,
      showErrorModal,
      errorMessage,
      availableUsers,
      selectedUserIds,
      newRoomName,
      messagesContainer,
      typingUser,
      currentUserId,
      currentUsername,
      selectRoom,
      createRoom,
      sendMessageHandler,
      handleTyping,
      getRoomName,
      formatTime,
      isSelf,
      isFirstInGroup,
      isLastInGroup,
      setRoomUnread,
    }
  }
}
</script>
