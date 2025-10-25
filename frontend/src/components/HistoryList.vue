<template>
  <div class="bg-white rounded-lg shadow-lg p-8">
    <h2 class="text-2xl font-semibold text-gray-800 mb-6">Prediction History</h2>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-12">
      <svg class="animate-spin h-12 w-12 text-blue-500 mx-auto" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="text-gray-600 mt-4">Loading history...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!transactions.length" class="text-center py-12">
      <div class="text-6xl mb-4">📋</div>
      <p class="text-xl text-gray-600 mb-2">No predictions yet</p>
      <p class="text-gray-500">Upload an image to start making medical diagnoses!</p>
    </div>

    <!-- History Table -->
    <div v-else class="space-y-4">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-[#00BCD4] text-white">
            <tr>
              <th class="px-4 py-3 text-left text-sm font-semibold">Date</th>
              <th class="px-4 py-3 text-left text-sm font-semibold">Patient</th>
              <th class="px-4 py-3 text-left text-sm font-semibold">MRN</th>
              <th class="px-4 py-3 text-left text-sm font-semibold">Gender</th>
              <th class="px-4 py-3 text-left text-sm font-semibold">Phone</th>
              <th class="px-4 py-3 text-left text-sm font-semibold">Prediction/Diagnosis</th>
              <th class="px-4 py-3 text-left text-sm font-semibold">Confidence Score</th>
              <th class="px-4 py-3 text-left text-sm font-semibold">Image</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="transaction in transactions" :key="transaction.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-sm text-gray-900">
                {{ formatDateShort(transaction.uploaded_at) }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">
                <router-link 
                  v-if="transaction.patient_data"
                  :to="{ name: 'PatientDetail', params: { id: transaction.patient_data.id } }"
                  class="text-[#00BCD4] hover:underline"
                >
                  {{ transaction.patient_data.full_name }}
                </router-link>
                <span v-else>-</span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">
                {{ transaction.patient_data?.mrn || '-' }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">
                {{ getGenderText(transaction.patient_data?.gender) }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">
                {{ transaction.patient_data?.phone || '-' }}
              </td>
              <td class="px-4 py-3 text-sm font-medium text-gray-900">
                {{ transaction.diagnosis }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">
                {{ Math.round(transaction.confidence * 100) }}%
              </td>
              <td class="px-4 py-3">
                <a 
                  :href="transaction.image_url" 
                  target="_blank"
                  class="text-[#00BCD4] hover:text-[#00ACC1] text-sm font-medium underline"
                >
                  View
                </a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="flex items-center justify-between border-t pt-4">
        <div class="text-sm text-gray-600">
          Showing {{ ((currentPage - 1) * pageSize) + 1 }} to 
          {{ Math.min(currentPage * pageSize, totalCount) }} of 
          {{ totalCount }} results
        </div>
        
        <div class="flex space-x-2">
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="!hasPrevious"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition',
              hasPrevious 
                ? 'bg-blue-500 text-white hover:bg-blue-600' 
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            ]"
          >
            Previous
          </button>
          
          <div class="flex items-center px-4 py-2 bg-gray-100 rounded-lg text-sm">
            Page {{ currentPage }} of {{ totalPages }}
          </div>
          
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="!hasNext"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition',
              hasNext 
                ? 'bg-blue-500 text-white hover:bg-blue-600' 
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            ]"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { getHistory } from '../services/api'
import { useToast } from 'vue-toastification'

export default {
  name: 'HistoryList',
  setup() {
    const toast = useToast()
    const transactions = ref([])
    const isLoading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalCount = ref(0)

    const totalPages = computed(() => {
      return Math.ceil(totalCount.value / pageSize.value)
    })

    const hasNext = computed(() => {
      return currentPage.value < totalPages.value
    })

    const hasPrevious = computed(() => {
      return currentPage.value > 1
    })

    const fetchHistory = async () => {
      isLoading.value = true
      try {
        const data = await getHistory(currentPage.value, pageSize.value)
        transactions.value = data.results
        totalCount.value = data.count
      } catch (error) {
        toast.error('Failed to load history: ' + error.message)
      } finally {
        isLoading.value = false
      }
    }

    const goToPage = (page) => {
      if (page < 1 || page > totalPages.value) return
      currentPage.value = page
      fetchHistory()
    }

    const refreshHistory = () => {
      currentPage.value = 1
      fetchHistory()
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatDateShort = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    }

    const getGenderText = (gender) => {
      const map = { 'M': 'Male', 'F': 'Female', 'O': 'Other' }
      return map[gender] || gender
    }

    const getConfidenceColor = (confidence) => {
      if (confidence >= 0.9) return 'bg-green-500'
      if (confidence >= 0.75) return 'bg-blue-500'
      if (confidence >= 0.6) return 'bg-yellow-500'
      return 'bg-orange-500'
    }

    onMounted(() => {
      fetchHistory()
    })

    return {
      transactions,
      isLoading,
      currentPage,
      pageSize,
      totalCount,
      totalPages,
      hasNext,
      hasPrevious,
      goToPage,
      refreshHistory,
      formatDate,
      formatDateShort,
      getGenderText,
      getConfidenceColor
    }
  }
}
</script>
