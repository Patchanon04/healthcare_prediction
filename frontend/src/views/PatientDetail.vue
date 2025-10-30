<template>
  <AppShell :title="patient?.full_name || 'Patient'">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Patient Info -->
      <div class="bg-white rounded-xl shadow p-6 lg:col-span-1">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">Patient Info</h3>
          <button @click="openEdit" class="px-3 py-1.5 text-sm rounded-lg border hover:bg-gray-50">Edit</button>
        </div>
        <div v-if="loadingPatient" class="text-gray-500">Loading...</div>
        <div v-else class="space-y-2">
          <div><span class="text-gray-500">MRN:</span> <span class="ml-2">{{ patient.mrn || '-' }}</span></div>
          <div><span class="text-gray-500">Phone:</span> <span class="ml-2">{{ patient.phone || '-' }}</span></div>
          <div><span class="text-gray-500">Age:</span> <span class="ml-2">{{ patient.age }}</span></div>
          <div><span class="text-gray-500">Gender:</span> <span class="ml-2">{{ genderLabel(patient.gender) }}</span></div>
          <div>
            <span class="text-gray-500">Notes:</span>
            <p class="mt-1 whitespace-pre-line">{{ patient.notes || '-' }}</p>
          </div>
        </div>
        <div class="mt-4">
          <h4 class="text-md font-semibold mb-2">Upload image for this patient</h4>
          <UploadForm :patient="{ patient_id: Number($route.params.id) }" @upload-success="onUploadSuccess" />
        </div>
      </div>

      <!-- Tabs: History & Treatment -->
      <div class="bg-white rounded-xl shadow p-6 lg:col-span-2">
        <div class="border-b border-gray-200 mb-4">
          <nav class="-mb-px flex space-x-8">
            <button
              @click="activeTab = 'history'"
              :class="[
                activeTab === 'history'
                  ? 'border-[#00BCD4] text-[#00BCD4]'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
              ]"
            >
              History
            </button>
            <button
              @click="activeTab = 'treatment'"
              :class="[
                activeTab === 'treatment'
                  ? 'border-[#00BCD4] text-[#00BCD4]'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
              ]"
            >
              Treatment
            </button>
          </nav>
        </div>

        <!-- History Tab -->
        <div v-if="activeTab === 'history'">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">Diagnosis History</h3>
          <div class="flex gap-2">
            <button @click="refresh" class="px-3 py-1 border rounded">Refresh</button>
          </div>
        </div>
        <div v-if="loadingTx" class="text-gray-500">Loading...</div>
        <div v-else-if="!transactions.length" class="text-gray-500">No transactions</div>
        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-100 text-gray-600">
              <tr>
                <th class="text-left px-4 py-2">Date</th>
                <th class="text-left px-4 py-2">Diagnosis</th>
                <th class="text-left px-4 py-2">Confidence</th>
                <th class="text-left px-4 py-2">Model</th>
                <th class="text-left px-4 py-2">Image</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in transactions" :key="t.id" class="border-t">
                <td class="px-4 py-2">{{ formatDate(t.uploaded_at) }}</td>
                <td class="px-4 py-2">{{ t.diagnosis }}</td>
                <td class="px-4 py-2">{{ Math.round(t.confidence * 100) }}%</td>
                <td class="px-4 py-2">{{ t.model_version }}</td>
                <td class="px-4 py-2">
                  <a :href="t.image_url" target="_blank" class="text-[#00BCD4] hover:underline">View</a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex items-center justify-between border-t mt-4 pt-4" v-if="count > 0">
          <div class="text-sm text-gray-600">Showing {{ ((page - 1) * pageSize) + 1 }} - {{ Math.min(page * pageSize, count) }} of {{ count }}</div>
          <div class="flex gap-2">
            <button :disabled="page===1" @click="go(page-1)" class="px-3 py-1 border rounded disabled:opacity-50">Prev</button>
            <span class="px-3 py-1">Page {{ page }} of {{ totalPages }}</span>
            <button :disabled="page===totalPages" @click="go(page+1)" class="px-3 py-1 border rounded disabled:opacity-50">Next</button>
          </div>
        </div>
        </div>

        <!-- Treatment Tab -->
        <div v-if="activeTab === 'treatment'">
          <TreatmentManagement :patient-id="Number($route.params.id)" />
        </div>
      </div>
    </div>
  </AppShell>
  
  <!-- Result Modal -->
  <transition name="modal">
    <div v-if="showResult" class="fixed inset-0 z-50 flex items-center justify-center" @click="showResult = false">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
      <div class="relative bg-white rounded-3xl shadow-[0_20px_60px_rgba(0,0,0,0.25)] w-full max-w-3xl mx-4 overflow-hidden border border-gray-100" @click.stop>
        <!-- Header -->
        <div class="relative bg-gradient-to-r from-[#00BCD4] via-[#00ACC1] to-[#0097A7] text-white p-5">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
              <span class="text-2xl">🎯</span>
            </div>
            <div>
              <h3 class="text-xl font-bold tracking-wide">Prediction Result</h3>
              <div class="text-white/80 text-sm">Model {{ resultTx?.model_version || '-' }} • {{ resultTx?.processing_time != null ? resultTx.processing_time + 's' : '-' }}</div>
            </div>
          </div>
          <button @click="showResult = false" class="absolute top-4 right-4 w-9 h-9 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        
        <!-- Body -->
        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Image -->
          <div class="bg-gray-50 rounded-2xl p-4 flex items-center justify-center border border-gray-100">
            <img v-if="resultTx?.image_url" :src="resultTx.image_url" alt="Uploaded" class="max-h-80 object-contain rounded-lg shadow-sm" />
            <div v-else class="text-gray-400">No image</div>
          </div>
          
          <!-- Details -->
          <div class="space-y-4">
            <div>
              <div class="text-sm text-gray-500">Diagnosis</div>
              <div class="mt-1 text-2xl font-semibold text-[#2C597D]">{{ resultTx?.diagnosis || '-' }}</div>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-sm text-gray-500">Confidence</span>
              <span :class="getConfidenceBadge(resultTx?.confidence)" class="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold">
                {{ resultTx?.confidence != null ? Math.round(resultTx.confidence * 100) + '%' : '-' }}
              </span>
            </div>
            <div class="text-sm text-gray-500">Patient</div>
            <div class="text-gray-700">
              {{ patient?.full_name }} <span class="text-gray-400">•</span> MRN {{ patient?.mrn || '-' }}
            </div>

            <div class="pt-2 flex gap-2">
              <a v-if="resultTx?.image_url" :href="resultTx.image_url" target="_blank" class="px-4 py-2 rounded-xl border text-[#00ACC1] hover:bg-[#00ACC1] hover:text-white transition">View Image</a>
              <button @click="showResult = false" class="px-4 py-2 rounded-xl bg-[#00BCD4] text-white hover:bg-[#00ACC1] transition">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>

  <!-- Edit Patient Modal -->
  <transition name="modal">
    <div v-if="showEdit" class="fixed inset-0 z-50 flex items-center justify-center" @click="showEdit = false">
      <div class="absolute inset-0 bg-black/50"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden" @click.stop>
        <div class="p-5 border-b">
          <h3 class="text-lg font-semibold text-[#2C597D]">Edit Patient</h3>
        </div>
        <div class="p-5 space-y-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">Full name <span class="text-red-500">*</span></label>
            <input v-model="editForm.full_name" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">MRN <span class="text-red-500">*</span></label>
            <input v-model="editForm.mrn" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div class="flex gap-3">
            <div class="w-1/2">
              <label class="block text-sm text-gray-600 mb-1">Age <span class="text-red-500">*</span></label>
              <input v-model.number="editForm.age" type="number" class="w-full border rounded px-3 py-2" />
            </div>
            <div class="w-1/2">
              <label class="block text-sm text-gray-600 mb-1">Gender <span class="text-red-500">*</span></label>
              <div class="relative">
                <select v-model="editForm.gender" class="w-full border rounded px-3 pr-10 py-2 appearance-none bg-white">
                  <option value="">Select gender</option>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                  <option value="O">Other</option>
                </select>
                <svg class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.106l3.71-3.876a.75.75 0 011.08 1.04l-4.24 4.43a.75.75 0 01-1.08 0l-4.24-4.43a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">Phone</label>
            <input v-model="editForm.phone" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">Notes</label>
            <textarea v-model="editForm.notes" rows="3" class="w-full border rounded px-3 py-2"></textarea>
          </div>
        </div>
        <div class="p-5 border-t flex justify-end gap-2">
          <button @click="showEdit = false" class="px-4 py-2 rounded-lg border">Cancel</button>
          <button @click="saveEdit" :disabled="savingEdit" class="px-4 py-2 rounded-lg bg-[#00BCD4] text-white hover:bg-[#00ACC1] disabled:opacity-50">
            {{ savingEdit ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import AppShell from '../components/AppShell.vue'
import UploadForm from '../components/UploadForm.vue'
import TreatmentManagement from '../components/TreatmentManagement.vue'
import { getPatient, getPatientTransactions, updatePatient } from '../services/api'

export default {
  name: 'PatientDetail',
  components: { AppShell, UploadForm, TreatmentManagement },
  setup(props, { attrs, root }) {
    const toast = useToast()
    const showResult = ref(false)
    const resultTx = ref(null)
    const routeId = Number(window.location.pathname.split('/').pop())
    const patient = ref(null)
    const transactions = ref([])
    const loadingPatient = ref(false)
    const loadingTx = ref(false)
    const showEditModal = ref(false)
    const showEdit = ref(false)
    const activeTab = ref('history')
    const savingEdit = ref(false)
    const editForm = ref({ full_name: '', mrn: '', phone: '', age: null, gender: '', notes: '' })

    const page = ref(1)
    const pageSize = ref(10)
    const count = ref(0)
    const totalPages = computed(() => Math.max(1, Math.ceil(count.value / pageSize.value)))

    const genderLabel = (g) => ({ M: 'Male', F: 'Female', O: 'Other' }[g] || '-')
    const formatDate = (d) => new Date(d).toLocaleString()

    const getConfidenceBadge = (c) => {
      if (c == null) return 'bg-gray-100 text-gray-600'
      if (c >= 0.9) return 'bg-green-100 text-green-700'
      if (c >= 0.75) return 'bg-blue-100 text-blue-700'
      if (c >= 0.6) return 'bg-yellow-100 text-yellow-700'
      return 'bg-orange-100 text-orange-700'
    }

    const openEdit = () => {
      showEdit.value = true
    }

    const saveEdit = async () => {
      try {
        if (!editForm.value.full_name || !editForm.value.mrn || !editForm.value.age || !editForm.value.gender) {
          toast.error('Please fill required fields: Full name, MRN, Age, Gender')
          return
        }
        savingEdit.value = true
        const updated = await updatePatient(routeId, editForm.value)
        patient.value = updated
        showEdit.value = false
        toast.success('Patient updated')
      } catch (e) {
        toast.error(e.message || 'Update failed')
      } finally {
        savingEdit.value = false
      }
    }

    const fetchPatient = async () => {
      loadingPatient.value = true
      try {
        patient.value = await getPatient(routeId)
        // sync edit form
        editForm.value = {
          full_name: patient.value.full_name || '',
          mrn: patient.value.mrn || '',
          phone: patient.value.phone || '',
          age: patient.value.age ?? null,
          gender: patient.value.gender || '',
          notes: patient.value.notes || ''
        }
      } finally {
        loadingPatient.value = false
      }
    }

    const fetchTransactions = async () => {
      loadingTx.value = true
      try {
        const data = await getPatientTransactions(routeId, { page: page.value, pageSize: pageSize.value })
        transactions.value = data.results
        count.value = data.count
      } finally {
        loadingTx.value = false
      }
    }

    const go = (p) => {
      if (p < 1 || p > totalPages.value) return
      page.value = p
      fetchTransactions()
    }

    const refresh = () => {
      page.value = 1
      fetchTransactions()
    }

    const onUploadSuccess = (tx) => {
      refresh()
      resultTx.value = tx
      showResult.value = true
      try {
        const msg = `Diagnosis: ${tx.diagnosis || 'N/A'}\nConfidence: ${tx.confidence != null ? Math.round(tx.confidence * 100) + '%': 'N/A'}`
        toast.success(msg, { timeout: 3000 })
      } catch (_) { /* ignore */ }
    }

    onMounted(() => {
      fetchPatient()
      fetchTransactions()
    })

    return { patient, transactions, loadingPatient, loadingTx, genderLabel, formatDate, page, pageSize, count, totalPages, go, refresh, onUploadSuccess, showResult, resultTx, getConfidenceBadge, showEdit, editForm, savingEdit, openEdit, saveEdit, activeTab }
  }
}
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
