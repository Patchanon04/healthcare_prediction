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
          <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-3">
            <div v-if="loadingMessages" class="text-center text-gray-500">Loading messages...</div>
            <div v-else-if="messages.length === 0" class="text-center text-gray-400">
              No messages yet. Start the conversation!
            </div>
            <div
              v-else
              v-for="msg in messages"
              :key="msg.id"
              :class="[
                'flex',
                msg.sender.id === currentUserId ? 'justify-end' : 'justify-start'
              ]"
            >
              <div :class="[
                'max-w-[70%] rounded-lg p-3',
                msg.sender.id === currentUserId 
                  ? 'bg-[#00BCD4] text-white' 
                  : 'bg-gray-200 text-gray-800'
              ]">
                <p v-if="msg.sender.id !== currentUserId" class="text-xs font-semibold mb-1">
                  {{ msg.sender.full_name || msg.sender.username }}
                </p>
                <p class="break-words">{{ msg.content }}</p>
                <p :class="[
                  'text-xs mt-1',
                  msg.sender.id === currentUserId ? 'text-blue-100' : 'text-gray-500'
                ]">
                  {{ formatTime(msg.created_at) }}
                </p>
              </div>
            </div>
            <div v-if="typingUser" class="text-sm text-gray-500 italic">
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
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import AppShell from '../components/AppShell.vue'
import Modal from '../components/Modal.vue'
import { listChatRooms, listChatUsers, createChatRoom, listMessages, markMessagesRead } from '../services/api'

export default {
  name: 'ChatView',
  components: { AppShell, Modal },
  setup() {
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
        messages.value = data.results || []
        await nextTick()
        scrollToBottom()
        
        // Mark as read
        const unreadIds = messages.value.filter(m => !m.is_read && m.sender.id !== currentUserId.value).map(m => m.id)
        if (unreadIds.length > 0) {
          await markMessagesRead(roomId, unreadIds)
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
      const backendHost = import.meta.env.VITE_API_URL?.replace('http://', '').replace('https://', '') || 'localhost:8000'
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
          messages.value.push(data.message)
          nextTick(() => scrollToBottom())
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
        } else if (data.type === 'error') {
          console.error('❌ WebSocket error:', data.message)
          showError(data.message)
        }
      }
      
      ws.value.onerror = (error) => {
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

    onMounted(async () => {
      // Get current user ID
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      currentUserId.value = user.id
      
      await fetchRooms()
      await fetchUsers()
    })

    onUnmounted(() => {
      if (ws.value) {
        ws.value.close()
      }
    })

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
      selectRoom,
      createRoom,
      sendMessageHandler,
      handleTyping,
      getRoomName,
      formatTime,
    }
  }
}
</script>
