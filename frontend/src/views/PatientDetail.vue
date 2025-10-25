<template>
  <AppShell :title="patient?.full_name || 'Patient'">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Patient Info -->
      <div class="bg-white rounded-xl shadow p-6 lg:col-span-1">
        <h3 class="text-lg font-semibold mb-4">Patient Info</h3>
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

      <!-- History -->
      <div class="bg-white rounded-xl shadow p-6 lg:col-span-2">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">History</h3>
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
    </div>
  </AppShell>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import AppShell from '../components/AppShell.vue'
import UploadForm from '../components/UploadForm.vue'
import { getPatient, getPatientTransactions } from '../services/api'

export default {
  name: 'PatientDetail',
  components: { AppShell, UploadForm },
  setup(props, { attrs, root }) {
    const toast = useToast()
    const routeId = Number(window.location.pathname.split('/').pop())
    const patient = ref(null)
    const transactions = ref([])
    const loadingPatient = ref(true)
    const loadingTx = ref(true)

    const page = ref(1)
    const pageSize = ref(10)
    const count = ref(0)
    const totalPages = computed(() => Math.max(1, Math.ceil(count.value / pageSize.value)))

    const genderLabel = (g) => ({ M: 'Male', F: 'Female', O: 'Other' }[g] || '-')
    const formatDate = (d) => new Date(d).toLocaleString()

    const fetchPatient = async () => {
      loadingPatient.value = true
      try {
        patient.value = await getPatient(routeId)
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
      try {
        const msg = `Diagnosis: ${tx.diagnosis || 'N/A'}\nConfidence: ${tx.confidence != null ? Math.round(tx.confidence * 100) + '%': 'N/A'}`
        toast.success(msg, { timeout: 6000 })
      } catch (_) {
        // ignore toast error
      }
    }

    onMounted(() => {
      fetchPatient()
      fetchTransactions()
    })

    return { patient, transactions, loadingPatient, loadingTx, genderLabel, formatDate, page, pageSize, count, totalPages, go, refresh, onUploadSuccess }
  }
}
</script>
