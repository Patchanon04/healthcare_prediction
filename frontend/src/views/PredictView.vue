<template>
  <AppShell title="Predict">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Left: Patient Form -->
      <div class="bg-white rounded-xl shadow p-6">
        <h2 class="text-xl font-semibold text-[#00BCD4] mb-4">Patient Information</h2>
        <form class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">Full Name <span class="text-red-500">*</span></label>
            <input v-model="patient.patient_name" class="w-full border rounded-lg px-3 py-2" placeholder="John Doe" required />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">MRN <span class="text-red-500">*</span></label>
            <input v-model="patient.mrn" class="w-full border rounded-lg px-3 py-2" placeholder="MRN-0001" required />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">Age <span class="text-red-500">*</span></label>
            <input type="number" v-model.number="patient.age" class="w-full border rounded-lg px-3 py-2" placeholder="35" required />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">Gender <span class="text-red-500">*</span></label>
            <select v-model="patient.gender" class="w-full border rounded-lg px-3 py-2" required>
              <option value="">Select Gender</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">Phone</label>
            <input v-model="patient.phone" class="w-full border rounded-lg px-3 py-2" placeholder="081-234-5678" />
          </div>
        </form>
      </div>

      <!-- Right: Upload Card -->
      <div class="bg-white rounded-xl shadow p-6">
        <h2 class="text-xl font-semibold text-[#00BCD4] mb-4">Upload Medical Image</h2>
        <UploadForm :patient="patient" @upload-success="onSuccess" @upload-error="onError" />
      </div>
    </div>

    <!-- Success Modal -->
    <Modal :show="showSuccessModal" title="Success" @close="closeSuccessModal">
      <div class="text-center py-4">
        <div class="text-6xl mb-4">✅</div>
        <p class="text-lg text-gray-700 mb-2">Prediction completed successfully!</p>
        <p class="text-sm text-gray-500">Redirecting to results...</p>
      </div>
      <template #footer>
        <button @click="closeSuccessModal" class="px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition">
          View Results
        </button>
      </template>
    </Modal>

    <!-- Error Modal -->
    <Modal :show="showErrorModal" title="Error" @close="showErrorModal = false">
      <div class="text-center py-4">
        <div class="text-6xl mb-4">❌</div>
        <p class="text-gray-700">{{ errorMessage }}</p>
      </div>
      <template #footer>
        <button @click="showErrorModal = false" class="px-4 py-2 bg-[#00BCD4] text-white rounded-lg hover:bg-[#00ACC1] transition">
          OK
        </button>
      </template>
    </Modal>
  </AppShell>
</template>

<script>
import { ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import UploadForm from '../components/UploadForm.vue'
import Modal from '../components/Modal.vue'

export default {
  name: 'PredictView',
  components: { AppShell, UploadForm, Modal },
  setup() {
    const patient = ref({ patient_name: '', mrn: '', age: null, gender: '', phone: '' })
    const showSuccessModal = ref(false)
    const showErrorModal = ref(false)
    const errorMessage = ref('')
    const resultId = ref(null)

    const onSuccess = (tx) => {
      resultId.value = tx.id
      showSuccessModal.value = true
      setTimeout(() => {
        window.location.href = `/result/${tx.id}`
      }, 1500)
    }

    const onError = (msg) => {
      errorMessage.value = msg
      showErrorModal.value = true
    }

    const closeSuccessModal = () => {
      showSuccessModal.value = false
      if (resultId.value) {
        window.location.href = `/result/${resultId.value}`
      }
    }

    return { 
      patient, 
      onSuccess, 
      onError,
      showSuccessModal,
      showErrorModal,
      errorMessage,
      closeSuccessModal
    }
  }
}
</script>
