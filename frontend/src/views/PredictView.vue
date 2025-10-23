<template>
  <AppShell title="Predict">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Patient Form -->
      <div class="lg:col-span-2 bg-white rounded-xl shadow p-6">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">Patient Information</h2>
        <form class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">Full Name</label>
            <input v-model="patient.patient_name" class="w-full border rounded-lg px-3 py-2" placeholder="John Doe" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">MRN</label>
            <input v-model="patient.mrn" class="w-full border rounded-lg px-3 py-2" placeholder="MRN-0001" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">Age</label>
            <input type="number" v-model.number="patient.age" class="w-full border rounded-lg px-3 py-2" placeholder="35" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">Gender</label>
            <select v-model="patient.gender" class="w-full border rounded-lg px-3 py-2">
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
          </div>
        </form>
      </div>

      <!-- Upload Card -->
      <div class="bg-white rounded-xl shadow p-6">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">Predict Tumor Scan</h2>
        <UploadForm :patient="patient" @upload-success="onSuccess" @upload-error="onError" />
      </div>
    </div>
  </AppShell>
</template>

<script>
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import AppShell from '../components/AppShell.vue'
import UploadForm from '../components/UploadForm.vue'

export default {
  name: 'PredictView',
  components: { AppShell, UploadForm },
  setup() {
    const toast = useToast()
    const patient = ref({ patient_name: '', mrn: '', age: null, gender: 'M' })

    const onSuccess = (tx) => {
      toast.success('Prediction completed!')
      // go to result page
      window.location.href = `/result/${tx.id}`
    }
    const onError = (msg) => toast.error(msg)

    return { patient, onSuccess, onError }
  }
}
</script>
