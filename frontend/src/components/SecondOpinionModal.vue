<template>
  <transition name="modal">
    <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center" @click.self="handleClose">
      <div class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-xl mx-4 bg-white rounded-2xl shadow-xl overflow-hidden">
        <header class="bg-gradient-to-r from-[#00BCD4] via-[#0097A7] to-[#007C91] px-6 py-4 text-white">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold">Request Second Opinion</h2>
              <p class="text-xs text-white/80">Share this diagnosis with another specialist</p>
            </div>
            <button @click="handleClose" class="w-9 h-9 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18M6 6l12 12" /></svg>
            </button>
          </div>
        </header>

        <form @submit.prevent="submit" class="px-6 py-5 space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-2">Assign Specialist</label>
            <select v-model="form.assignee" class="w-full border rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#00BCD4]">
              <option value="">Unassigned</option>
              <option v-for="specialist in specialists" :key="specialist.id" :value="specialist.id">
                {{ specialist.full_name || specialist.username }}
              </option>
            </select>
            <p class="text-xs text-gray-500 mt-1">You can leave unassigned and let specialists pick it up later.</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-600 mb-2">Clinical Question<span class="text-red-500">*</span></label>
            <textarea
              v-model="form.question"
              rows="4"
              class="w-full border rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#00BCD4]"
              placeholder="Describe what you need the specialist to review"
              required
            ></textarea>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-2">Due Date</label>
              <input
                v-model="form.due_at"
                type="datetime-local"
                class="w-full border rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#00BCD4]"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-2">Additional Notes</label>
              <input
                v-model="form.notes"
                type="text"
                class="w-full border rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#00BCD4]"
                placeholder="Optional context"
              />
            </div>
          </div>

          <footer class="flex justify-end gap-3 pt-4 border-t border-gray-100">
            <button type="button" @click="handleClose" class="px-4 py-2 rounded-xl border text-gray-600 hover:bg-gray-50">Cancel</button>
            <button type="submit" :disabled="loading || !form.question" class="px-5 py-2 rounded-xl bg-[#00BCD4] text-white hover:bg-[#0097A7] disabled:opacity-60">
              {{ loading ? 'Submitting...' : 'Submit Request' }}
            </button>
          </footer>
        </form>
      </div>
    </div>
  </transition>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'SecondOpinionModal',
  props: {
    visible: { type: Boolean, default: false },
    loading: { type: Boolean, default: false },
    specialists: { type: Array, default: () => [] },
  },
  emits: ['close', 'submit'],
  setup(props, { emit }) {
    const form = ref({ assignee: '', question: '', due_at: '', notes: '' })

    const reset = () => {
      form.value = { assignee: '', question: '', due_at: '', notes: '' }
    }

    watch(
      () => props.visible,
      (newVal) => {
        if (newVal) {
          reset()
        }
      }
    )

    const handleClose = () => {
      emit('close')
    }

    const submit = () => {
      emit('submit', {
        assignee: form.value.assignee || null,
        question: form.value.question,
        due_at: form.value.due_at || null,
        notes: form.value.notes || '',
      })
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
