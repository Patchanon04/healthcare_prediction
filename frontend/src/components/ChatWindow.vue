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
      <div v-for="(m,i) in messages" :key="m.id || i" class="flex w-full" :class="isSelf(m) ? 'justify-end' : 'justify-start'">
        <div class="max-w-[80%] rounded-2xl px-3 py-2 text-sm" :class="isSelf(m) ? 'bg-[#7b68ee] text-white' : 'bg-white border text-gray-800'">
          <div v-if="!isSelf(m)" class="text-[10px] opacity-70 font-semibold mb-0.5">{{ m.sender?.full_name || m.sender?.username }}</div>
          <div class="whitespace-pre-wrap break-words">{{ m.content }}</div>
          <div class="text-[10px] mt-0.5" :class="isSelf(m) ? 'text-blue-100' : 'text-gray-400'">{{ formatTime(m.created_at) }}</div>
        </div>
      </div>
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

    const isSelf = (m) => {
      if (!m || !m.sender) return false
      const senderId = m.sender.id || m.sender
      const currentId = props.currentUserId
      const result = String(senderId) === String(currentId)
      if (!result) {
        console.log(`🔍 isSelf check: senderId=${senderId}, currentId=${currentId}, result=${result}`)
      }
      return result
    }

    // Title: for direct chat show only counterpart name, for group fall back to room.name or members (excluding self)
    const roomTitle = computed(() => {
      const allMembers = props.room.members || []
      const others = allMembers.filter(m => String(m.id) !== String(props.currentUserId))
      console.log(`🏷️ Title computation: currentUserId=${props.currentUserId}, allMembers=`, allMembers, 'others=', others)
      
      if ((props.room.room_type === 'direct' || others.length === 1) && others.length >= 1) {
        const o = others[0]
        const title = o.full_name || o.username || 'Chat'
        console.log(`🏷️ Direct chat title: ${title}`)
        return title
      }
      if (props.room.name) {
        console.log(`🏷️ Group chat with name: ${props.room.name}`)
        return props.room.name
      }
      const groupTitle = others.map(m => m.full_name || m.username).join(', ')
      console.log(`🏷️ Group chat title: ${groupTitle}`)
      return groupTitle
    })
    const roomAvatar = null

    const scrollToBottom = () => { if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight }

    const formatTime = (ts) => new Date(ts).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })

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
        if (unread.length) markMessagesRead(props.room.id, unread).catch(()=>{})
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

    onMounted(() => { 
      // restore draft
      try { const d = localStorage.getItem(`chat_draft_${props.room.id}`); if (d) draft.value = d } catch {}
      load(); connectWS() 
    })
    onBeforeUnmount(() => { if (ws.value) ws.value.close() })
    watch(() => props.room.id, () => { 
      try { const d = localStorage.getItem(`chat_draft_${props.room.id}`); if (d) draft.value = d; else draft.value = '' } catch { draft.value = '' }
      load(); connectWS() 
    })

    return { messages, draft, send, isSelf, formatTime, typingUser, handleTyping, messagesEl, roomTitle, roomAvatar, close }
  }
}
</script>
