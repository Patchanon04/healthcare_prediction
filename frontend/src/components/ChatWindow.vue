<template>
  <div class="fixed bottom-0 right-0 m-3 w-80 bg-white rounded-t-lg shadow-2xl border flex flex-col overflow-hidden" :style="{ right: `${offsetRight}px` }">
    <div class="bg-[#6a5acd] text-white px-3 py-2 flex items-center justify-between">
      <div class="flex items-center gap-2 truncate">
        <div class="w-7 h-7 rounded-full overflow-hidden bg-white/20 flex items-center justify-center">
          <img v-if="roomAvatar" :src="roomAvatar" class="w-full h-full object-cover" />
          <span v-else class="text-xs font-semibold">{{ roomTitle.charAt(0).toUpperCase() }}</span>
        </div>
        <div class="truncate">
          <div class="text-sm font-semibold truncate">{{ roomTitle }}</div>
          <div class="text-[10px] text-white/80 truncate" v-if="typingUser">{{ typingUser }} is typing...</div>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button @click="$emit('minimize', room.id)" class="text-white/90 hover:text-white text-sm">_</button>
        <button @click="close" class="text-white/90 hover:text-white text-sm">✕</button>
      </div>
    </div>

    <div ref="messagesEl" class="h-80 overflow-y-auto p-3 space-y-2 bg-gray-50">
      <template v-for="group in groupedMessages" :key="group.dateKey">
        <div class="text-center text-[10px] uppercase tracking-wide text-gray-400 mt-3 mb-2">
          <span class="px-3 py-1 bg-gray-200/60 rounded-full">{{ formatDateLabel(group.dateKey) }}</span>
        </div>
        <div v-for="(m,i) in group.items" :key="m.id || `${group.dateKey}-${i}`" class="space-y-1">
          <div class="flex w-full" :class="isSelf(m) ? 'justify-end' : 'justify-start'">
            <div class="max-w-[80%] rounded-2xl px-3 py-2 text-sm" :class="isSelf(m) ? 'bg-[#7b68ee] text-white' : 'bg-white border text-gray-800'">
              <div v-if="!isSelf(m)" class="text-[10px] opacity-70 font-semibold mb-0.5">{{ m.sender?.full_name || m.sender?.username }}</div>
              <div class="whitespace-pre-wrap break-words">{{ m.content }}</div>
              <div class="text-[10px] mt-0.5" :class="isSelf(m) ? 'text-blue-100' : 'text-gray-400'">{{ formatTime(m.created_at) }}</div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <form @submit.prevent="send" class="border-t p-2 bg-white flex items-center gap-2">
      <input v-model="draft" @input="handleTyping" type="text" placeholder="Aa" class="flex-1 text-sm border rounded-full px-3 py-2 focus:ring-2 focus:ring-[#7b68ee]" />
      <button type="submit" :disabled="!draft.trim()" class="text-white bg-[#7b68ee] px-3 py-1 rounded-full text-sm disabled:opacity-50">Send</button>
    </form>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { listMessages, markMessagesRead } from '../services/api'

export default {
  name: 'ChatWindow',
  props: {
    room: { type: Object, required: true },
    currentUserId: { type: [String, Number], required: true },
    offsetRight: { type: Number, default: 16 }
  },
  setup(props, { emit }) {
    const messages = ref([])
    const draft = ref('')
    const ws = ref(null)
    const typingUser = ref(null)
    const typingTimeout = ref(null)
    const messagesEl = ref(null)

    const normalizeId = (value) => {
      if (value === null || value === undefined) return null
      if (typeof value === 'object') {
        if ('value' in value) return normalizeId(value.value)
        if ('id' in value) return normalizeId(value.id)
      }
      return String(value)
    }

    const currentUserId = computed(() => {
      const normalized = normalizeId(props.currentUserId)
      if (!normalized) {
        console.warn('⚠️ currentUserId not ready for room', props.room?.id, props.currentUserId)
      }
      return normalized
    })

    const isSelf = (m) => {
      if (!m) return false
      const rawSender = m.sender?.id ?? m.sender
      const senderId = normalizeId(rawSender)
      const currentId = currentUserId.value
      const result = senderId !== null && currentId !== null && senderId === currentId
      if (!result) {
        console.debug('🔍 message alignment check', { messageId: m.id, senderId, currentId, rawSender })
      }
      return result
    }

    // Title: for direct chat show only counterpart name, for group fall back to room.name or members (excluding self)
    const roomTitle = computed(() => {
      const allMembers = props.room.members || []
      const currentId = currentUserId.value
      const others = allMembers.filter(member => normalizeId(member.id) !== currentId)

      if ((props.room.room_type === 'direct' || others.length === 1) && others.length >= 1) {
        const partner = others[0]
        return partner.full_name || partner.username || 'Chat'
      }

      if (props.room.name) return props.room.name

      if (others.length) {
        return others.map(member => member.full_name || member.username || 'User').join(', ')
      }

      return props.room.members?.length === 1
        ? (props.room.members[0].full_name || props.room.members[0].username || 'Chat')
        : 'Chat'
    })
    const roomAvatar = null

    const scrollToBottom = () => { if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight }

    const formatTime = (ts) => new Date(ts).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    const formatDateLabel = (dateStr) => {
      const today = new Date()
      const date = new Date(dateStr)
      const isToday = date.toDateString() === today.toDateString()
      const yesterday = new Date(); yesterday.setDate(today.getDate() - 1)
      const isYesterday = date.toDateString() === yesterday.toDateString()
      if (isToday) return 'Today'
      if (isYesterday) return 'Yesterday'
      return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
    }
    const groupedMessages = computed(() => {
      const groups = messages.value.reduce((acc, message) => {
        const dateKey = message.created_at ? new Date(message.created_at).toISOString().slice(0, 10) : 'unknown'
        if (!acc[dateKey]) acc[dateKey] = []
        acc[dateKey].push(message)
        return acc
      }, {})

      return Object.entries(groups)
        .map(([dateKey, items]) => {
          const parsed = new Date(dateKey)
          const sortKey = Number.isNaN(parsed.getTime()) ? Infinity : parsed.getTime()
          return { dateKey, items, sortKey }
        })
        .sort((a, b) => a.sortKey - b.sortKey)
    })

    const connectWS = () => {
      try {
        if (ws.value) ws.value.close()
        const token = localStorage.getItem('token')
        if (!token) return
        const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        let host = 'localhost:8000'
        try {
          if (import.meta?.env?.VITE_API_URL) {
            host = import.meta.env.VITE_API_URL.replace('http://','').replace('https://','')
          } else if (window.location.hostname !== 'localhost') {
            host = `${window.location.hostname}:8000`
          }
        } catch {}
        ws.value = new WebSocket(`${proto}//${host}/ws/chat/${props.room.id}/?token=${encodeURIComponent(token)}`)
        ws.value.onmessage = (e) => {
          const data = JSON.parse(e.data)
          if (data.type === 'message') {
            messages.value.push(data.message)
            nextTick(scrollToBottom)
            // Broadcast to other components
            window.dispatchEvent(new CustomEvent('chat-message-received', { 
              detail: { roomId: props.room.id, message: data.message } 
            }))
          } else if (data.type === 'typing') {
            if (data.is_typing) {
              typingUser.value = data.username
              clearTimeout(typingTimeout.value)
              typingTimeout.value = setTimeout(() => typingUser.value = null, 3000)
            } else typingUser.value = null
          } else if (data.type === 'read') {
            // no-op for now
          }
        }
      } catch {}
    }

    const load = async () => {
      try {
        console.log(`📥 Loading messages for room ${props.room.id}`)
        const data = await listMessages(props.room.id, { pageSize: 100 })
        console.log(`📥 Loaded ${(data.results || []).length} messages:`, data.results)
        messages.value = data.results || []
        await nextTick(); scrollToBottom()
        // mark read
        const unread = messages.value.filter(m => !m.is_read && String(m.sender?.id) !== String(props.currentUserId)).map(m => m.id)
        if (unread.length) {
          console.log(`✅ ChatWindow: Marking ${unread.length} messages as read`)
          markMessagesRead(props.room.id, unread)
            .then(() => {
              // Notify AppShell to refresh unread count
              console.log(`📤 ChatWindow: Dispatching messages-marked-read event (count: ${unread.length})`)
              window.dispatchEvent(new CustomEvent('messages-marked-read', { detail: { count: unread.length } }))
            })
            .catch(() => {})
        }
      } catch (error) {
        console.error(`❌ Failed to load messages for room ${props.room.id}:`, error)
      }
    }

    const send = () => {
      if (!draft.value.trim()) return
      if (!ws.value || ws.value.readyState !== WebSocket.OPEN) return
      ws.value.send(JSON.stringify({ type: 'message', content: draft.value.trim() }))
      draft.value = ''
      try { localStorage.removeItem(`chat_draft_${props.room.id}`) } catch {}
    }

    const handleTyping = () => {
      if (!ws.value) return
      ws.value.send(JSON.stringify({ type: 'typing', is_typing: true }))
      clearTimeout(typingTimeout.value)
      typingTimeout.value = setTimeout(() => {
        ws.value?.send(JSON.stringify({ type: 'typing', is_typing: false }))
      }, 800)
      // persist draft per room
      try { localStorage.setItem(`chat_draft_${props.room.id}`, draft.value) } catch {}
    }

    const close = () => emit('close', props.room.id)

    // Listen for messages from other components
    const handleExternalMessage = (event) => {
      if (event.detail.roomId === props.room.id) {
        const msg = event.detail.message
        // Only add if not already in list
        if (!messages.value.find(m => m.id === msg.id)) {
          messages.value.push(msg)
          nextTick(scrollToBottom)
        }
      }
    }

    onMounted(() => { 
      // restore draft
      try { const d = localStorage.getItem(`chat_draft_${props.room.id}`); if (d) draft.value = d } catch {}
      load(); connectWS()
      // Listen for messages from other components
      window.addEventListener('chat-message-received', handleExternalMessage)
    })
    onBeforeUnmount(() => { 
      if (ws.value) ws.value.close()
      window.removeEventListener('chat-message-received', handleExternalMessage)
    })
    watch(() => props.room.id, () => { 
      try { const d = localStorage.getItem(`chat_draft_${props.room.id}`); if (d) draft.value = d; else draft.value = '' } catch { draft.value = '' }
      load(); connectWS() 
    })

    return { messages, draft, send, isSelf, formatTime, typingUser, handleTyping, messagesEl, roomTitle, roomAvatar, close, currentUserId, groupedMessages, formatDateLabel }
  }
}
</script>
