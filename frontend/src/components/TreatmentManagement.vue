<template>
  <div class="space-y-6">
    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            activeTab === tab.id
              ? 'border-[#00BCD4] text-[#00BCD4]'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- Treatment Plans Tab -->
    <div v-if="activeTab === 'treatments'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-semibold text-[#2C597D]">Treatment Plans</h3>
        <button @click="showTreatmentModal = true" class="px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition">
          + Add Treatment Plan
        </button>
      </div>

      <div v-if="treatments.length === 0" class="text-center py-8 text-gray-500">
        No treatment plans yet
      </div>

      <div v-for="treatment in treatments" :key="treatment.id" class="bg-white border rounded-lg p-4 hover:shadow-md transition">
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <h4 class="font-semibold text-[#2C597D]">{{ treatment.title }}</h4>
            <p class="text-sm text-gray-600 mt-1">{{ treatment.description }}</p>
            <div class="flex items-center gap-4 mt-2 text-xs text-gray-500">
              <span>📅 {{ formatDate(treatment.start_date) }} - {{ treatment.end_date ? formatDate(treatment.end_date) : 'Ongoing' }}</span>
              <span :class="statusClass(treatment.status)">{{ treatment.status }}</span>
              <span v-if="treatment.created_by_name">👤 {{ treatment.created_by_name }}</span>
            </div>
          </div>
          <div class="flex gap-2">
            <button @click="editTreatment(treatment)" class="text-blue-600 hover:text-blue-800">✏️</button>
            <button @click="deleteTreatmentConfirm(treatment)" class="text-red-600 hover:text-red-800">🗑️</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Medications Tab -->
    <div v-if="activeTab === 'medications'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-semibold text-[#2C597D]">Medications</h3>
        <button @click="showMedicationModal = true" class="px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition">
          + Add Medication
        </button>
      </div>

      <div v-if="medications.length === 0" class="text-center py-8 text-gray-500">
        No medications yet
      </div>

      <div v-for="med in medications" :key="med.id" class="bg-white border rounded-lg p-4 hover:shadow-md transition">
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <h4 class="font-semibold text-[#2C597D]">💊 {{ med.drug_name }}</h4>
            <p class="text-sm text-gray-600 mt-1">{{ med.dosage }} - {{ med.frequency }}</p>
            <p v-if="med.instructions" class="text-xs text-gray-500 mt-1">{{ med.instructions }}</p>
            <div class="flex items-center gap-4 mt-2 text-xs text-gray-500">
              <span>📅 {{ formatDate(med.start_date) }} - {{ med.end_date ? formatDate(med.end_date) : 'Ongoing' }}</span>
              <span :class="statusClass(med.status)">{{ med.status }}</span>
            </div>
          </div>
          <div class="flex gap-2">
            <button @click="editMedication(med)" class="text-blue-600 hover:text-blue-800">✏️</button>
            <button @click="deleteMedicationConfirm(med)" class="text-red-600 hover:text-red-800">🗑️</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Follow-up Notes Tab -->
    <div v-if="activeTab === 'followups'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-semibold text-[#2C597D]">Follow-up Notes</h3>
        <button @click="showFollowUpModal = true" class="px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition">
          + Add Note
        </button>
      </div>

      <div v-if="followups.length === 0" class="text-center py-8 text-gray-500">
        No follow-up notes yet
      </div>

      <div v-for="note in followups" :key="note.id" class="bg-white border rounded-lg p-4 hover:shadow-md transition">
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <span class="text-lg">{{ noteTypeIcon(note.note_type) }}</span>
              <h4 class="font-semibold text-[#2C597D]">{{ note.title }}</h4>
            </div>
            <p class="text-sm text-gray-600 mt-2 whitespace-pre-wrap">{{ note.note }}</p>
            <div class="flex items-center gap-4 mt-2 text-xs text-gray-500">
              <span>📅 {{ formatDateTime(note.created_at) }}</span>
              <span v-if="note.created_by_name">👤 {{ note.created_by_name }}</span>
            </div>
          </div>
          <div class="flex gap-2">
            <button @click="editFollowUp(note)" class="text-blue-600 hover:text-blue-800">✏️</button>
            <button @click="deleteFollowUpConfirm(note)" class="text-red-600 hover:text-red-800">🗑️</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Timeline Tab -->
    <div v-if="activeTab === 'timeline'" class="space-y-4">
      <h3 class="text-lg font-semibold text-[#2C597D]">Progress Timeline</h3>
      
      <div v-if="timeline.length === 0" class="text-center py-8 text-gray-500">
        No timeline events yet
      </div>

      <div class="relative">
        <div class="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>
        
        <div v-for="(event, index) in timeline" :key="index" class="relative pl-16 pb-8">
          <div class="absolute left-6 w-4 h-4 rounded-full bg-[#00BCD4] border-4 border-white"></div>
          
          <div class="bg-white border rounded-lg p-4 hover:shadow-md transition">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-lg">{{ timelineIcon(event.type) }}</span>
              <span class="font-semibold text-[#2C597D]">{{ timelineTitle(event) }}</span>
              <span class="text-xs text-gray-500 ml-auto">{{ formatDateTime(event.date) }}</span>
            </div>
            <div class="text-sm text-gray-600">
              {{ timelineDescription(event) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Treatment Plan Modal -->
    <Modal :show="showTreatmentModal" title="Treatment Plan" @close="closeTreatmentModal">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
          <input v-model="treatmentForm.title" type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Description *</label>
          <textarea v-model="treatmentForm.description" rows="3" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition resize-none"></textarea>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Start Date *</label>
            <input v-model="treatmentForm.start_date" type="date" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input v-model="treatmentForm.end_date" type="date" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select v-model="treatmentForm.status" class="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition cursor-pointer">
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>
      <template #footer>
        <button @click="closeTreatmentModal" class="px-4 py-2 border rounded-lg hover:bg-gray-50 transition">Cancel</button>
        <button @click="saveTreatment" class="px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition">Save</button>
      </template>
    </Modal>

    <!-- Medication Modal -->
    <Modal :show="showMedicationModal" title="Medication" @close="closeMedicationModal">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Drug Name *</label>
          <input v-model="medicationForm.drug_name" type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Dosage *</label>
            <input v-model="medicationForm.dosage" type="text" placeholder="e.g., 500mg" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Frequency *</label>
            <input v-model="medicationForm.frequency" type="text" placeholder="e.g., twice daily" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Instructions</label>
          <textarea v-model="medicationForm.instructions" rows="2" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition resize-none"></textarea>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Start Date *</label>
            <input v-model="medicationForm.start_date" type="date" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input v-model="medicationForm.end_date" type="date" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select v-model="medicationForm.status" class="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition cursor-pointer">
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="discontinued">Discontinued</option>
          </select>
        </div>
      </div>
      <template #footer>
        <button @click="closeMedicationModal" class="px-4 py-2 border rounded-lg hover:bg-gray-50 transition">Cancel</button>
        <button @click="saveMedication" class="px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition">Save</button>
      </template>
    </Modal>

    <!-- Follow-up Note Modal -->
    <Modal :show="showFollowUpModal" title="Follow-up Note" @close="closeFollowUpModal">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
          <input v-model="followUpForm.title" type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Note Type</label>
          <select v-model="followUpForm.note_type" class="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition cursor-pointer">
            <option value="checkup">Check-up</option>
            <option value="progress">Progress Update</option>
            <option value="complication">Complication</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Note *</label>
          <textarea v-model="followUpForm.note" rows="4" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#00BCD4] focus:border-transparent transition resize-none"></textarea>
        </div>
      </div>
      <template #footer>
        <button @click="closeFollowUpModal" class="px-4 py-2 border rounded-lg hover:bg-gray-50 transition">Cancel</button>
        <button @click="saveFollowUp" class="px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition">Save</button>
      </template>
    </Modal>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import Modal from './Modal.vue'
import { 
  getTreatmentPlans, createTreatmentPlan, updateTreatmentPlan, deleteTreatmentPlan,
  getMedications, createMedication, updateMedication, deleteMedication,
  getFollowUpNotes, createFollowUpNote, updateFollowUpNote, deleteFollowUpNote,
  getPatientTimeline
} from '../services/api'

export default {
  name: 'TreatmentManagement',
  components: { Modal },
  props: {
    patientId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const activeTab = ref('treatments')
    const tabs = [
      { id: 'treatments', name: 'Treatment Plans' },
      { id: 'medications', name: 'Medications' },
      { id: 'followups', name: 'Follow-up Notes' },
      { id: 'timeline', name: 'Timeline' }
    ]

    // Data
    const treatments = ref([])
    const medications = ref([])
    const followups = ref([])
    const timeline = ref([])

    // Modals
    const showTreatmentModal = ref(false)
    const showMedicationModal = ref(false)
    const showFollowUpModal = ref(false)

    // Forms
    const treatmentForm = ref({
      id: null,
      title: '',
      description: '',
      start_date: '',
      end_date: '',
      status: 'active'
    })

    const medicationForm = ref({
      id: null,
      drug_name: '',
      dosage: '',
      frequency: '',
      instructions: '',
      start_date: '',
      end_date: '',
      status: 'active'
    })

    const followUpForm = ref({
      id: null,
      title: '',
      note: '',
      note_type: 'progress'
    })

    // Load data
    const loadTreatments = async () => {
      try {
        const data = await getTreatmentPlans(props.patientId)
        // Handle both paginated response and array
        treatments.value = data.results || (Array.isArray(data) ? data : [])
      } catch (e) {
        console.error('Failed to load treatments:', e)
        console.error('Error response:', e.response?.data)
        treatments.value = []
      }
    }

    const loadMedications = async () => {
      try {
        const data = await getMedications(props.patientId)
        // Handle both paginated response and array
        medications.value = data.results || (Array.isArray(data) ? data : [])
      } catch (e) {
        console.error('Failed to load medications:', e)
        console.error('Error response:', e.response?.data)
        medications.value = []
      }
    }

    const loadFollowUps = async () => {
      try {
        const data = await getFollowUpNotes(props.patientId)
        // Handle both paginated response and array
        followups.value = data.results || (Array.isArray(data) ? data : [])
      } catch (e) {
        console.error('Failed to load follow-ups:', e)
        console.error('Error response:', e.response?.data)
        followups.value = []
      }
    }

    const loadTimeline = async () => {
      try {
        const data = await getPatientTimeline(props.patientId)
        timeline.value = data.events || []
      } catch (e) {
        console.error('Failed to load timeline:', e)
        console.error('Error response:', e.response?.data)
        timeline.value = []
      }
    }

    // Treatment CRUD
    const editTreatment = (treatment) => {
      treatmentForm.value = { ...treatment }
      showTreatmentModal.value = true
    }

    const saveTreatment = async () => {
      try {
        if (treatmentForm.value.id) {
          await updateTreatmentPlan(props.patientId, treatmentForm.value.id, treatmentForm.value)
        } else {
          await createTreatmentPlan(props.patientId, treatmentForm.value)
        }
        closeTreatmentModal()
        loadTreatments()
        loadTimeline()
      } catch (e) {
        console.error('Failed to save treatment:', e)
        console.error('Error response:', e.response?.data)
        alert('Failed to save treatment plan: ' + (e.response?.data?.detail || e.response?.data?.title || e.message || 'Unknown error'))
      }
    }

    const deleteTreatmentConfirm = async (treatment) => {
      if (confirm(`Delete treatment plan "${treatment.title}"?`)) {
        try {
          await deleteTreatmentPlan(props.patientId, treatment.id)
          loadTreatments()
          loadTimeline()
        } catch (e) {
          console.error('Failed to delete treatment:', e)
        }
      }
    }

    const closeTreatmentModal = () => {
      showTreatmentModal.value = false
      treatmentForm.value = { id: null, title: '', description: '', start_date: '', end_date: '', status: 'active' }
    }

    // Medication CRUD
    const editMedication = (med) => {
      medicationForm.value = { ...med }
      showMedicationModal.value = true
    }

    const saveMedication = async () => {
      try {
        if (medicationForm.value.id) {
          await updateMedication(props.patientId, medicationForm.value.id, medicationForm.value)
        } else {
          await createMedication(props.patientId, medicationForm.value)
        }
        closeMedicationModal()
        loadMedications()
        loadTimeline()
      } catch (e) {
        console.error('Failed to save medication:', e)
        console.error('Error response:', e.response?.data)
        alert('Failed to save medication: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message || 'Unknown error'))
      }
    }

    const deleteMedicationConfirm = async (med) => {
      if (confirm(`Delete medication "${med.drug_name}"?`)) {
        try {
          await deleteMedication(props.patientId, med.id)
          loadMedications()
          loadTimeline()
        } catch (e) {
          console.error('Failed to delete medication:', e)
        }
      }
    }

    const closeMedicationModal = () => {
      showMedicationModal.value = false
      medicationForm.value = { id: null, drug_name: '', dosage: '', frequency: '', instructions: '', start_date: '', end_date: '', status: 'active' }
    }

    // Follow-up CRUD
    const editFollowUp = (note) => {
      followUpForm.value = { ...note }
      showFollowUpModal.value = true
    }

    const saveFollowUp = async () => {
      try {
        if (followUpForm.value.id) {
          await updateFollowUpNote(props.patientId, followUpForm.value.id, followUpForm.value)
        } else {
          await createFollowUpNote(props.patientId, followUpForm.value)
        }
        closeFollowUpModal()
        loadFollowUps()
        loadTimeline()
      } catch (e) {
        console.error('Failed to save follow-up:', e)
        console.error('Error response:', e.response?.data)
        alert('Failed to save follow-up note: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message || 'Unknown error'))
      }
    }

    const deleteFollowUpConfirm = async (note) => {
      if (confirm(`Delete note "${note.title}"?`)) {
        try {
          await deleteFollowUpNote(props.patientId, note.id)
          loadFollowUps()
          loadTimeline()
        } catch (e) {
          console.error('Failed to delete follow-up:', e)
        }
      }
    }

    const closeFollowUpModal = () => {
      showFollowUpModal.value = false
      followUpForm.value = { id: null, title: '', note: '', note_type: 'progress' }
    }

    // Helpers
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString()
    }

    const formatDateTime = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString()
    }

    const statusClass = (status) => {
      const classes = {
        active: 'px-2 py-1 bg-green-100 text-green-800 rounded',
        completed: 'px-2 py-1 bg-blue-100 text-blue-800 rounded',
        cancelled: 'px-2 py-1 bg-red-100 text-red-800 rounded',
        discontinued: 'px-2 py-1 bg-red-100 text-red-800 rounded'
      }
      return classes[status] || ''
    }

    const noteTypeIcon = (type) => {
      const icons = {
        checkup: '🩺',
        progress: '📈',
        complication: '⚠️',
        other: '📝'
      }
      return icons[type] || '📝'
    }

    const timelineIcon = (type) => {
      const icons = {
        diagnosis: '🔬',
        treatment: '💉',
        medication: '💊',
        followup: '📝'
      }
      return icons[type] || '📌'
    }

    const timelineTitle = (event) => {
      if (event.type === 'diagnosis') return event.data.diagnosis || 'Diagnosis'
      if (event.type === 'treatment') return event.data.title || 'Treatment Plan'
      if (event.type === 'medication') return event.data.drug_name || 'Medication'
      if (event.type === 'followup') return event.data.title || 'Follow-up Note'
      return 'Event'
    }

    const timelineDescription = (event) => {
      if (event.type === 'diagnosis') return `Confidence: ${(event.data.confidence * 100).toFixed(1)}%`
      if (event.type === 'treatment') return event.data.description || ''
      if (event.type === 'medication') return `${event.data.dosage} - ${event.data.frequency}`
      if (event.type === 'followup') return event.data.note || ''
      return ''
    }

    onMounted(() => {
      loadTreatments()
      loadMedications()
      loadFollowUps()
      loadTimeline()
    })

    return {
      activeTab,
      tabs,
      treatments,
      medications,
      followups,
      timeline,
      showTreatmentModal,
      showMedicationModal,
      showFollowUpModal,
      treatmentForm,
      medicationForm,
      followUpForm,
      editTreatment,
      saveTreatment,
      deleteTreatmentConfirm,
      closeTreatmentModal,
      editMedication,
      saveMedication,
      deleteMedicationConfirm,
      closeMedicationModal,
      editFollowUp,
      saveFollowUp,
      deleteFollowUpConfirm,
      closeFollowUpModal,
      formatDate,
      formatDateTime,
      statusClass,
      noteTypeIcon,
      timelineIcon,
      timelineTitle,
      timelineDescription
    }
  }
}
</script>
