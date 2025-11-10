<template>
  <AppShell :title="pageTitle">
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div class="xl:col-span-2 space-y-6">
        <section class="bg-white rounded-2xl shadow p-6">
          <header class="flex items-center justify-between mb-6">
            <div>
              <h2 class="text-xl font-semibold text-[#2C597D]">Diagnosis Summary</h2>
              <p class="text-sm text-gray-500">Review model output and metadata</p>
            </div>
            <button
              v-if="secondOpinionEnabled"
              @click="openSecondOpinion"
              class="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#00BCD4] text-white hover:bg-[#0097A7]"
            >
              <span>Request Second Opinion</span>
            </button>
          </header>

          <div v-if="loading" class="py-12 text-center text-gray-500">Loading...</div>
          <div v-else-if="error" class="py-12 text-center text-red-600">{{ error }}</div>
          <div v-else-if="transaction" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div class="aspect-[4/3] bg-gray-100 rounded-xl overflow-hidden flex items-center justify-center">
                <img
                  v-if="transaction.image_url"
                  :src="transaction.image_url"
                  alt="Scan"
                  class="max-w-full max-h-full object-contain"
                />
                <div v-else class="text-5xl text-gray-300">🧠</div>
              </div>
              <div class="flex items-center justify-between text-sm text-gray-500">
                <span>Uploaded</span>
                <span>{{ formatDate(transaction.uploaded_at) }}</span>
              </div>
            </div>

            <div class="space-y-5">
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div class="bg-gray-50 rounded-xl p-4">
                  <div class="text-gray-500">Diagnosis</div>
                  <div class="text-lg font-semibold text-[#2C597D]">{{ transaction.diagnosis }}</div>
                </div>
                <div class="bg-gray-50 rounded-xl p-4">
                  <div class="text-gray-500">Confidence</div>
                  <div class="flex items-center gap-2">
                    <div class="font-semibold">
                      {{ transaction.confidence != null ? Math.round(transaction.confidence * 100) + '%' : '-' }}
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div
                        class="h-2 rounded-full bg-green-500"
                        :style="{ width: (transaction.confidence || 0) * 100 + '%' }"
                      ></div>
                    </div>
                  </div>
                </div>
                <div class="bg-gray-50 rounded-xl p-4">
                  <div class="text-gray-500">Model Version</div>
                  <div class="font-semibold">{{ transaction.model_version || '-' }}</div>
                </div>
                <div class="bg-gray-50 rounded-xl p-4">
                  <div class="text-gray-500">Processing Time</div>
                  <div class="font-semibold">
                    {{ transaction.processing_time != null ? transaction.processing_time + 's' : '-' }}
                  </div>
                </div>
              </div>

              <div class="bg-blue-50 border border-blue-100 rounded-xl p-4">
                <div class="text-sm text-blue-700">Patient</div>
                <div class="mt-1 text-lg font-semibold text-blue-900">
                  {{ transaction.patient_data?.full_name || 'Unknown' }}
                </div>
                <div class="text-sm text-blue-700/70 flex flex-wrap gap-2">
                  <span>MRN {{ transaction.patient_data?.mrn || '-' }}</span>
                  <span>Age {{ transaction.patient_data?.age ?? '-' }}</span>
                  <span>Gender {{ genderLabel(transaction.patient_data?.gender) }}</span>
                </div>
              </div>

              <div class="flex gap-2">
                <a
                  v-if="transaction.image_url"
                  :href="transaction.image_url"
                  target="_blank"
                  class="px-4 py-2 rounded-xl border text-[#00BCD4] hover:bg-[#00BCD4] hover:text-white transition"
                >
                  Open Image
                </a>
                <router-link
                  :to="{ name: 'PatientDetail', params: { id: transaction.patient_data?.id } }"
                  class="px-4 py-2 rounded-xl bg-gray-100 text-[#2C597D] hover:bg-gray-200"
                >
                  View Patient
                </router-link>
              </div>
            </div>
          </div>
        </section>

        <section v-if="secondOpinionEnabled" class="bg-white rounded-2xl shadow p-6">
          <header class="flex items-center justify-between mb-4">
            <div>
              <h3 class="text-lg font-semibold text-[#2C597D]">Second Opinion Requests</h3>
              <p class="text-sm text-gray-500">Track hand-offs with specialists</p>
            </div>
            <button @click="refreshSecondOpinions" class="px-3 py-1.5 text-sm border rounded-lg hover:bg-gray-50">
              Refresh
            </button>
          </header>

          <div v-if="loadingSecondOpinions" class="text-gray-500">Loading second opinions...</div>
          <div v-else-if="secondOpinions.length === 0" class="text-gray-500 text-sm">No second opinion requests yet.</div>
          <div v-else class="space-y-4">
            <article v-for="request in secondOpinions" :key="request.id" class="border border-gray-200 rounded-xl p-4">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="flex items-center gap-3">
                  <span class="px-3 py-1 rounded-full text-xs font-semibold" :class="statusBadge(request.status)">
                    {{ statusLabel(request.status) }}
                  </span>
                  <span class="text-sm text-gray-500">Requested {{ formatRelative(request.created_at) }}</span>
                </div>
                <div class="text-sm text-gray-500">
                  Assigned to: <span class="font-medium text-gray-700">{{ request.assignee_username || 'Unassigned' }}</span>
                </div>
              </div>

              <p class="mt-3 text-gray-700 whitespace-pre-line">{{ request.question }}</p>

              <div class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                <div>
                  <span class="text-gray-500">Notes:</span>
                  <div class="mt-1">{{ request.notes || '-' }}</div>
                </div>
                <div>
                  <span class="text-gray-500">Due:</span>
                  <div class="mt-1">{{ dueDateLabel(request.due_at) }}</div>
                </div>
              </div>

              <div v-if="request.response" class="mt-4 bg-green-50 border border-green-100 rounded-xl p-4">
                <div class="text-sm font-semibold text-green-700 mb-1">Response</div>
                <p class="text-green-800 whitespace-pre-line">{{ request.response }}</p>
                <div class="mt-2 text-xs text-green-700/80">Responded {{ formatRelative(request.responded_at) }}</div>
              </div>

              <div v-else-if="canRespond(request)" class="mt-4">
                <button
                  @click="openRespondDialog(request)"
                  class="px-4 py-2 rounded-xl bg-[#2C597D] text-white hover:bg-[#24476a]"
                >
                  Respond
                </button>
              </div>
            </article>
          </div>
        </section>
      </div>

      <aside class="space-y-6">
        <section class="bg-white rounded-2xl shadow p-6">
          <h3 class="text-lg font-semibold text-[#2C597D] mb-4">Audit Trail</h3>
          <ul class="space-y-3 text-sm text-gray-600">
            <li v-for="event in activity" :key="event.label" class="flex items-start gap-3">
              <div class="mt-1 w-2 h-2 rounded-full bg-[#00BCD4]"></div>
              <div>
                <div class="font-medium text-gray-700">{{ event.label }}</div>
                <div class="text-xs text-gray-500">{{ event.time }}</div>
              </div>
            </li>
          </ul>
        </section>

        <section v-if="transaction?.patient_data" class="bg-white rounded-2xl shadow p-6">
          <h3 class="text-lg font-semibold text-[#2C597D] mb-4">Patient Snapshot</h3>
          <dl class="space-y-3 text-sm text-gray-600">
            <div class="flex justify-between">
              <dt class="text-gray-500">MRN</dt>
              <dd class="font-medium">{{ transaction.patient_data.mrn || '-' }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-gray-500">Age</dt>
              <dd class="font-medium">{{ transaction.patient_data.age ?? '-' }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-gray-500">Gender</dt>
              <dd class="font-medium">{{ genderLabel(transaction.patient_data.gender) }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-gray-500">Phone</dt>
              <dd class="font-medium">{{ transaction.patient_data.phone || '-' }}</dd>
            </div>
          </dl>
        </section>
      </aside>
    </div>

    <!-- New Second Opinion Modal -->
    <SecondOpinionModal
      v-if="secondOpinionEnabled"
      :visible="showSecondOpinion"
      :loading="creatingSecondOpinion"
      :specialists="specialists"
      @close="showSecondOpinion = false"
      @submit="submitSecondOpinion"
    />

    <!-- Respond Modal -->
    <RespondModal
      v-if="secondOpinionEnabled"
      :visible="showRespond"
      :loading="responding"
      :request="selectedRequest"
      @close="closeRespond"
      @submit="submitResponse"
    />
  </AppShell>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'
import AppShell from '../components/AppShell.vue'
import SecondOpinionModal from '../components/SecondOpinionModal.vue'
import RespondModal from '../components/RespondModal.vue'
import {
  getTransaction,
  listSecondOpinions,
  createSecondOpinion,
  updateSecondOpinion,
  listChatUsers,
  getProfile,
} from '../services/api'
import { getStoredUser } from '../services/storage'

const ROLE_SPECIALIST = ['radiologist', 'doctor']

export default {
  name: 'DiagnosisDetail',
  components: { AppShell, SecondOpinionModal, RespondModal },
  setup() {
    const toast = useToast()
    const route = useRoute()
    const transaction = ref(null)
    const loading = ref(false)
    const error = ref('')
    const activity = ref([])
    const secondOpinionEnabled = true
    const secondOpinions = ref([])
    const loadingSecondOpinions = ref(false)
    const showSecondOpinion = ref(false)
    const creatingSecondOpinion = ref(false)
    const specialists = ref([])
    const showRespond = ref(false)
    const responding = ref(false)
    const selectedRequest = ref(null)
    const currentUser = ref(getStoredUser())

    const pageTitle = computed(() => {
      if (!transaction.value) return 'Diagnosis'
      const patient = transaction.value.patient_data?.full_name || 'Patient'
      return `Diagnosis • ${patient}`
    })

    const fetchTransaction = async () => {
      loading.value = true
      error.value = ''
      try {
        transaction.value = await getTransaction(route.params.id)
        buildActivity()
        await fetchSecondOpinions()
      } catch (e) {
        error.value = e.message || 'Failed to load diagnosis'
      } finally {
        loading.value = false
      }
    }

    const buildActivity = () => {
      if (!transaction.value) {
        activity.value = []
        return
      }
      const events = []
      events.push({ label: 'Diagnosis generated', time: formatDate(transaction.value.uploaded_at) })
      activity.value = events
    }

    const fetchSecondOpinions = async () => {
      if (!secondOpinionEnabled) return
      loadingSecondOpinions.value = true
      try {
        const patientId = transaction.value?.patient_data?.id
        const params = { pageSize: 50, diagnosis: route.params.id }
        if (patientId) params.patient = patientId
        const res = await listSecondOpinions(params)
        const items = res.results || []
        if (patientId) {
          const matchId = String(patientId)
          secondOpinions.value = items.filter(item => String(item.patient) === matchId)
        } else {
          secondOpinions.value = items
        }
      } catch (e) {
        toast.error(e.message || 'Failed to load second opinions')
      } finally {
        loadingSecondOpinions.value = false
      }
    }

    const fetchSpecialists = async () => {
      try {
        const res = await listChatUsers()
        specialists.value = (res.users || []).filter((user) => ROLE_SPECIALIST.includes(user.role))
      } catch (e) {
        console.warn('Failed to load specialists', e)
      }
    }

    const openSecondOpinion = () => {
      if (!transaction.value?.patient_data?.id) {
        toast.error('Missing patient linkage for this diagnosis')
        return
      }
      showSecondOpinion.value = true
    }

    const submitSecondOpinion = async (payload) => {
      if (!transaction.value) return
      creatingSecondOpinion.value = true
      try {
        const assigneeId = payload.assignee != null ? Number(payload.assignee) : null
        await createSecondOpinion({
          patient: transaction.value.patient_data.id,
          diagnosis: transaction.value.id,
          ...payload,
          assignee: assigneeId,
        })
        toast.success('Second opinion request created')
        showSecondOpinion.value = false
        fetchSecondOpinions()
      } catch (e) {
        toast.error(e.message || 'Failed to create second opinion request')
      } finally {
        creatingSecondOpinion.value = false
      }
    }

    const refreshSecondOpinions = () => {
      fetchSecondOpinions()
    }

    const genderLabel = (gender) => ({ M: 'Male', F: 'Female', O: 'Other' }[gender] || '-')

    const statusLabel = (status) => ({
      pending: 'Pending',
      accepted: 'Accepted',
      completed: 'Completed',
      declined: 'Declined',
    }[status] || status)

    const statusBadge = (status) => ({
      pending: 'bg-yellow-100 text-yellow-700',
      accepted: 'bg-blue-100 text-blue-700',
      completed: 'bg-green-100 text-green-700',
      declined: 'bg-red-100 text-red-700',
    }[status] || 'bg-gray-100 text-gray-700')

    const dueDateLabel = (d) => {
      if (!d) return 'Not set'
      return formatDate(d)
    }

    const canRespond = (request) => {
      const user = getCurrentUser()
      if (!user) return false
      return request.assignee === user.id || (request.assignee === null && ROLE_SPECIALIST.includes(user.role))
    }

    const openRespondDialog = (request) => {
      selectedRequest.value = request
      showRespond.value = true
    }

    const closeRespond = () => {
      showRespond.value = false
      selectedRequest.value = null
    }

    const submitResponse = async ({ response, status }) => {
      if (!selectedRequest.value) return
      responding.value = true
      try {
        await updateSecondOpinion(selectedRequest.value.id, { response, status })
        toast.success('Response submitted')
        closeRespond()
        fetchSecondOpinions()
      } catch (e) {
        toast.error(e.message || 'Failed to submit response')
      } finally {
        responding.value = false
      }
    }

    const getCurrentUser = () => {
      return currentUser.value
    }

    const formatDate = (value) => {
      if (!value) return '-'
      return new Date(value).toLocaleString()
    }

    const formatRelative = (value) => {
      if (!value) return '-'
      const date = new Date(value)
      const diff = Date.now() - date.getTime()
      const mins = Math.round(diff / 60000)
      if (mins < 1) return 'just now'
      if (mins < 60) return `${mins}m ago`
      const hours = Math.round(mins / 60)
      if (hours < 24) return `${hours}h ago`
      const days = Math.round(hours / 24)
      return `${days}d ago`
    }

    const fetchCurrentUser = async () => {
      try {
        const profile = await getProfile()
        currentUser.value = {
          ...(currentUser.value || {}),
          role: profile?.role,
          full_name: profile?.full_name,
          email: profile?.email,
          username: profile?.username || currentUser.value?.username,
        }
      } catch (e) {
        console.warn('Failed to load profile', e)
      }
    }

    onMounted(() => {
      fetchTransaction()
      fetchSpecialists()
       fetchCurrentUser()
    })

    watch(
      () => route.params.id,
      () => {
        fetchTransaction()
      }
    )

    return {
      transaction,
      loading,
      error,
      pageTitle,
      genderLabel,
      formatDate,
      formatRelative,
      activity,
      secondOpinionEnabled,
      secondOpinions,
      loadingSecondOpinions,
      openSecondOpinion,
      showSecondOpinion,
      submitSecondOpinion,
      creatingSecondOpinion,
      statusLabel,
      statusBadge,
      dueDateLabel,
      refreshSecondOpinions,
      specialists,
      canRespond,
      openRespondDialog,
      showRespond,
      closeRespond,
      submitResponse,
      responding,
      selectedRequest,
    }
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
