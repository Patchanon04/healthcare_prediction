<template>
  <aside class="hidden lg:flex fixed right-0 top-16 bottom-0 w-72 bg-white border-l z-30 flex-col">
    <div class="p-3 flex items-center justify-between border-b">
      <div class="font-semibold text-gray-700">Contacts</div>
      <input v-model="query" type="text" placeholder="Search" class="text-sm border rounded px-2 py-1 w-32" />
    </div>
    <div class="flex-1 overflow-y-auto">
      <button
        v-for="u in filteredUsers"
        :key="u.id"
        @click="$emit('open-chat', u)"
        class="w-full px-3 py-2 hover:bg-gray-50 flex items-center gap-3"
      >
        <div class="relative w-9 h-9 rounded-full overflow-hidden bg-gray-200 flex items-center justify-center">
          <img v-if="u.avatar" :src="u.avatar" class="w-full h-full object-cover" />
          <span v-else class="text-sm font-semibold text-gray-600">{{ (u.full_name || u.username || 'U').charAt(0).toUpperCase() }}</span>
          <span v-if="u.online" class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-green-500 ring-2 ring-white"></span>
        </div>
        <div class="text-sm text-left">
          <div class="font-medium text-gray-800 truncate">{{ u.full_name || u.username }}</div>
          <div class="text-xs text-gray-500 capitalize">{{ u.role || 'user' }}<span v-if="u.online" class="text-green-600 font-semibold ml-1">• Online</span></div>
        </div>
      </button>
      <div v-if="loading" class="p-3 text-center text-gray-500 text-sm">Loading...</div>
      <div v-else-if="filteredUsers.length === 0" class="p-3 text-center text-gray-400 text-sm">No contacts</div>
    </div>
  </aside>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { listChatUsers } from '../services/api'

export default {
  name: 'ContactsPanel',
  props: {
    currentUserId: { type: [String, Number], default: null }
  },
  emits: ['open-chat'],
  setup(props) {
    const users = ref([])
    const loading = ref(false)
    const query = ref('')

    const load = async () => {
      try {
        loading.value = true
        const data = await listChatUsers()
        users.value = (data.users || []).filter(u => !!u.id)
      } finally {
        loading.value = false
      }
    }

    const filteredUsers = computed(() => {
      const q = query.value.trim().toLowerCase()
      let list = users.value.filter(u => String(u.id) !== String(props.currentUserId))
      if (q) list = list.filter(u => (u.full_name || u.username || '').toLowerCase().includes(q))
      // Online first, then by display name
      return list.slice().sort((a, b) => {
        if (Boolean(b.online) !== Boolean(a.online)) return b.online ? 1 : -1
        const an = (a.full_name || a.username || '').toLowerCase()
        const bn = (b.full_name || b.username || '').toLowerCase()
        return an.localeCompare(bn)
      })
    })

    onMounted(load)

    return { users, loading, query, filteredUsers }
  }
}
</script>
