<template>
  <AppShell :title="pageTitle">
    <div class="flex items-center justify-between mb-4">
      <div class="flex gap-2">
        <input v-model="search" @keyup.enter="fetchPatients" type="text" placeholder="Search name / MRN / phone" class="border rounded-lg px-3 py-2 w-72" />
        <button @click="fetchPatients" class="px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1]">Search</button>
        <button @click="clearSearch" class="px-4 py-2 border rounded-lg">Clear</button>
      </div>
      <button @click="showCreate = true" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">Add Patient</button>
    </div>

    <div class="bg-white rounded-xl shadow p-4">
      <div v-if="isLoading" class="py-8 text-center text-gray-500">Loading...</div>
      <div v-else>
        <div v-if="!patients.length" class="py-8 text-center text-gray-500">No patients found</div>
        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-100 text-gray-600">
              <tr>
                <th class="text-left px-4 py-2">Name</th>
                <th class="text-left px-4 py-2">MRN</th>
                <th class="text-left px-4 py-2">Phone</th>
                <th class="text-left px-4 py-2">Age</th>
                <th class="text-left px-4 py-2">Gender</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in patients" :key="p.id" class="border-t">
                <td class="px-4 py-2">
                  <router-link :to="{ name: 'PatientDetail', params: { id: p.id } }" class="text-[#00BCD4] hover:underline">
                    {{ p.full_name }}
                  </router-link>
                </td>
                <td class="px-4 py-2">{{ p.mrn || '-' }}</td>
                <td class="px-4 py-2">{{ p.phone || '-' }}</td>
                <td class="px-4 py-2">{{ p.age }}</td>
                <td class="px-4 py-2">{{ genderLabel(p.gender) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex items-center justify-between border-t mt-4 pt-4" v-if="totalCount > 0">
          <div class="text-sm text-gray-600">Showing {{ ((page - 1) * pageSize) + 1 }} - {{ Math.min(page * pageSize, totalCount) }} of {{ totalCount }}</div>
          <div class="flex gap-2">
            <button :disabled="page===1" @click="go(page-1)" class="px-3 py-1 border rounded disabled:opacity-50">Prev</button>
            <span class="px-3 py-1">Page {{ page }} of {{ totalPages }}</span>
            <button :disabled="page===totalPages" @click="go(page+1)" class="px-3 py-1 border rounded disabled:opacity-50">Next</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Patient Modal -->
    <div v-if="showCreate" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click="showCreate=false">
      <div class="bg-white rounded-xl shadow p-6 w-full max-w-md" @click.stop>
        <h3 class="text-lg font-semibold mb-4">Add Patient</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-sm text-gray-600 mb-1">Full name <span class="text-red-500">*</span></label>
            <input v-model="form.full_name" type="text" placeholder="Full name" class="w-full border rounded px-3 py-2" required />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">MRN <span class="text-red-500">*</span></label>
            <input v-model="form.mrn" type="text" placeholder="Medical Record Number" class="w-full border rounded px-3 py-2" required />
          </div>
          <div class="flex gap-3">
            <div class="w-1/2">
              <label class="block text-sm text-gray-600 mb-1">Age <span class="text-red-500">*</span></label>
              <input v-model.number="form.age" type="number" placeholder="Age" class="w-full border rounded px-3 py-2" required />
            </div>
            <div class="w-1/2">
              <label class="block text-sm text-gray-600 mb-1">Gender <span class="text-red-500">*</span></label>
              <div class="relative">
                <select v-model="form.gender" class="w-full border rounded px-3 pr-10 py-2 appearance-none bg-white" required>
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
            <input v-model="form.phone" type="text" placeholder="Phone number" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">Notes</label>
            <textarea v-model="form.notes" placeholder="Additional notes" class="w-full border rounded px-3 py-2" rows="3"></textarea>
          </div>
        </div>
        <div class="flex gap-2 mt-4">
          <button @click="showCreate=false" class="px-4 py-2 border rounded">Cancel</button>
          <button @click="create" class="ml-auto px-4 py-2 bg-[#00BCD4] text-white rounded hover:bg-[#00ACC1]" :disabled="submitting">Create</button>
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import { listPatients, createPatient } from '../services/api'

export default {
  name: 'PatientsList',
  components: { AppShell },
  setup() {
    const route = useRoute()
    const isHistoryMode = computed(() => !!route.meta?.historyMode)
    const pageTitle = computed(() => route.meta?.title || (isHistoryMode.value ? 'History' : 'Patients'))

    const search = ref('')
    const patients = ref([])
    const isLoading = ref(false)
    const page = ref(1)
    const pageSize = ref(10)
    const totalCount = ref(0)

    const showCreate = ref(false)
    const submitting = ref(false)
    const form = ref({ full_name: '', mrn: '', phone: '', age: null, gender: '', notes: '' })

    const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))

    const fetchPatients = async () => {
      isLoading.value = true
      try {
        const data = await listPatients({ page: page.value, pageSize: pageSize.value, search: search.value })
        patients.value = data.results
        totalCount.value = data.count
      } finally {
        isLoading.value = false
      }
    }

    const go = (p) => {
      if (p < 1 || p > totalPages.value) return
      page.value = p
      fetchPatients()
    }

    const clearSearch = () => {
      search.value = ''
      page.value = 1
      fetchPatients()
    }

    const genderLabel = (g) => ({ M: 'Male', F: 'Female', O: 'Other' }[g] || '-')

    const create = async () => {
      submitting.value = true
      try {
        if (!form.value.full_name || !form.value.mrn || !form.value.age || !form.value.gender) {
          throw new Error('Please fill required fields: Full name, MRN, Age, and Gender')
        }
        await createPatient(form.value)
        showCreate.value = false
        form.value = { full_name: '', mrn: '', phone: '', age: null, gender: '', notes: '' }
        page.value = 1
        fetchPatients()
      } catch (e) {
        alert(e.message || 'Create failed')
      } finally {
        submitting.value = false
      }
    }

    onMounted(fetchPatients)

    return { pageTitle, search, patients, isLoading, page, pageSize, totalCount, totalPages, fetchPatients, clearSearch, go, showCreate, form, create, submitting, genderLabel }
  }
}
</script>
