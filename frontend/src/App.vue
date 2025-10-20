<template>
  <div id="app" class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- Header -->
    <header class="bg-white shadow-md">
      <div class="container mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold text-gray-800 flex items-center">
          <span class="text-4xl mr-3">🐕</span>
          Dog Breed Prediction
        </h1>
        <p class="text-gray-600 mt-2">Upload a dog image and discover its breed using ML </p>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <!-- Upload Section -->
      <section class="mb-12">
        <UploadForm 
          @upload-success="handleUploadSuccess" 
          @upload-error="handleUploadError"
        />
      </section>

      <!-- History Section -->
      <section>
        <HistoryList ref="historyList" />
      </section>
    </main>

    <!-- Result Modal -->
    <ResultModal 
      v-if="showModal" 
      :prediction="currentPrediction"
      @close="closeModal"
    />

    <!-- Footer -->
    <footer class="bg-white shadow-inner mt-16">
      <div class="container mx-auto px-4 py-6 text-center text-gray-600">
        <p>© 2024 Dog Breed Prediction System | Built with Vue.js, Django, FastAPI</p>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import UploadForm from './components/UploadForm.vue'
import HistoryList from './components/HistoryList.vue'
import ResultModal from './components/ResultModal.vue'

export default {
  name: 'App',
  components: {
    UploadForm,
    HistoryList,
    ResultModal
  },
  setup() {
    const toast = useToast()
    const showModal = ref(false)
    const currentPrediction = ref(null)
    const historyList = ref(null)

    const handleUploadSuccess = (prediction) => {
      currentPrediction.value = prediction
      showModal.value = true
      toast.success('Prediction completed successfully!')
      
      // Refresh history list
      if (historyList.value) {
        historyList.value.refreshHistory()
      }
    }

    const handleUploadError = (error) => {
      toast.error(error)
    }

    const closeModal = () => {
      showModal.value = false
      currentPrediction.value = null
    }

    return {
      showModal,
      currentPrediction,
      historyList,
      handleUploadSuccess,
      handleUploadError,
      closeModal
    }
  }
}
</script>
