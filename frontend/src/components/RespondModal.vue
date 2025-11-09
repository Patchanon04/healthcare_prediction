<template>
  <transition name="modal">
    <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center" @click.self="handleClose">
      <div class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-xl mx-4 bg-white rounded-2xl shadow-xl overflow-hidden">
        <header class="bg-[#2C597D] px-6 py-4 text-white">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold">Provide Response</h2>
              <p class="text-xs text-white/70">Share your findings and update the status</p>
            </div>
            <button @click="handleClose" class="w-9 h-9 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18M6 6l12 12" /></svg>
            </button>
          </div>
        </header>

        <div class="px-6 py-5 space-y-5">
          <div class="bg-gray-100 rounded-xl p-4 text-sm text-gray-700">
            <div class="font-semibold text-gray-800">Request Context</div>
            <p class="mt-2 whitespace-pre-line">{{ request?.question }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-600 mb-2">Response<span class="text-red-500">*</span></label>
            <textarea
              v-model="form.response"
              rows="5"
              class="w-full border rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#2C597D]"
              placeholder="Summarize your findings"
              required
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-600 mb-2">Status</label>
            <select v-model="form.status" class="w-full border rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#2C597D]">
              <option value="completed">Completed</option>
              <option value="declined">Declined</option>
              <option value="accepted">Accepted</option>
            </select>
            <p class="text-xs text-gray-500 mt-1">Use declined if you cannot provide an assessment.</p>
          </div>
        </div>

        <footer class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
          <button type="button" @click="handleClose" class="px-4 py-2 rounded-xl border text-gray-600 hover:bg-gray-50">Cancel</button>
          <button type="button" :disabled="loading || !form.response" @click="submit" class="px-5 py-2 rounded-xl bg-[#2C597D] text-white hover:bg-[#24476a] disabled:opacity-60">
            {{ loading ? 'Submitting...' : 'Submit Response' }}
          </button>
        </footer>
      </div>
    </div>
  </transition>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'RespondModal',
  props: {
    visible: { type: Boolean, default: false },
    loading: { type: Boolean, default: false },
    request: { type: Object, default: null },
  },
  emits: ['close', 'submit'],
  setup(props, { emit }) {
    const form = ref({ response: '', status: 'completed' })

    watch(
      () => props.visible,
      (newVal) => {
        if (newVal) {
          form.value = { response: '', status: 'completed' }
        }
      }
    )

    const handleClose = () => {
      emit('close')
    }

    const submit = () => {
      emit('submit', { ...form.value })
    }

    return { form, handleClose, submit }
  },
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
