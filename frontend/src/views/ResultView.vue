<template>
  <AppShell title="Result">
    <div class="bg-white rounded-xl shadow p-6">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">Predict Tumor Results</h2>

      <div v-if="loading" class="py-12 text-center">Loading...</div>
      <div v-else-if="error" class="py-12 text-center text-red-600">{{ error }}</div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Image with filename -->
        <div class="space-y-2">
          <div class="bg-gray-100 rounded-lg h-80 flex items-center justify-center overflow-hidden">
            <img v-if="tx.image_url" :src="tx.image_url" alt="Medical scan" class="max-w-full max-h-full object-contain" />
            <span v-else class="text-5xl">🖼️</span>
          </div>
          <p class="text-sm text-gray-600 text-center">{{ getFileName(tx.image_url) }}</p>
        </div>

        <!-- Details -->
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div class="bg-gray-50 p-4 rounded">
              <div class="text-gray-500">Patient Name</div>
              <div class="font-semibold">{{ tx.patient_name }}</div>
            </div>
            <div class="bg-gray-50 p-4 rounded">
              <div class="text-gray-500">MRN</div>
              <div class="font-semibold">{{ tx.mrn }}</div>
            </div>
            <div class="bg-gray-50 p-4 rounded">
              <div class="text-gray-500">Age</div>
              <div class="font-semibold">{{ tx.age }}</div>
            </div>
            <div class="bg-gray-50 p-4 rounded">
              <div class="text-gray-500">Gender</div>
              <div class="font-semibold">{{ tx.gender }}</div>
            </div>
          </div>

          <div class="bg-blue-50 p-4 rounded">
            <div class="text-gray-500">Detected Diagnosis</div>
            <div class="text-2xl font-bold">{{ tx.diagnosis }}</div>
          </div>

          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-600">Confidence</span>
              <span class="font-semibold">{{ Math.round(tx.confidence * 100) }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-3">
              <div class="h-3 rounded-full bg-green-500" :style="{ width: Math.round(tx.confidence * 100) + '%' }"></div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 text-sm">
            <div class="bg-gray-50 p-4 rounded">
              <div class="text-gray-500">Model Version</div>
              <div class="font-semibold">{{ tx.model_version }}</div>
            </div>
            <div class="bg-gray-50 p-4 rounded">
              <div class="text-gray-500">Processing Time</div>
              <div class="font-semibold">{{ tx.processing_time }}s</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>

<script>
import { ref, onMounted } from 'vue'
import AppShell from '../components/AppShell.vue'
import { getTransaction } from '../services/api'

export default {
  name: 'ResultView',
  components: { AppShell },
  props: { id: String },
  setup(props) {
    const tx = ref(null)
    const loading = ref(true)
    const error = ref('')

    const fetchTx = async () => {
      loading.value = true
      try {
        tx.value = await getTransaction(props.id)
      } catch (e) {
        error.value = e.message
      } finally {
        loading.value = false
      }
    }

    const getFileName = (url) => {
      if (!url) return 'No image'
      try {
        const parts = url.split('/')
        return decodeURIComponent(parts[parts.length - 1])
      } catch {
        return 'image.jpg'
      }
    }

    onMounted(fetchTx)

    return { tx, loading, error, getFileName }
  }
}
</script>
