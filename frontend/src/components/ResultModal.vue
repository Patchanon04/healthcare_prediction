<template>
  <div 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
    @click.self="$emit('close')"
  >
    <div 
      class="bg-white rounded-xl shadow-2xl max-w-lg w-full p-8 relative transform transition-all"
      @click.stop
    >
      <!-- Close Button -->
      <button
        @click="$emit('close')"
        class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <!-- Success Icon -->
      <div class="text-center mb-6">
        <div class="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-4">
          <svg class="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 class="text-3xl font-bold text-gray-800 mb-2">Prediction Complete!</h2>
      </div>

      <!-- Prediction Results -->
      <div class="space-y-6">
        <!-- Diagnosis -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 text-center">
          <p class="text-sm text-gray-600 mb-2">Detected Diagnosis</p>
          <p class="text-3xl font-bold text-gray-800">{{ prediction.diagnosis }}</p>
        </div>

        <!-- Confidence -->
        <div class="space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Confidence</span>
            <span class="font-semibold text-gray-800">{{ confidencePercent }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div 
              class="h-full rounded-full transition-all duration-1000 ease-out"
              :class="confidenceColor"
              :style="{ width: confidencePercent + '%' }"
            ></div>
          </div>
        </div>

        <!-- Additional Info -->
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-gray-600 mb-1">Model Version</p>
            <p class="font-semibold text-gray-800">{{ prediction.model_version }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-gray-600 mb-1">Processing Time</p>
            <p class="font-semibold text-gray-800">{{ prediction.processing_time }}s</p>
          </div>
        </div>

        <!-- Transaction ID -->
        <div class="text-center text-xs text-gray-500">
          Transaction ID: {{ prediction.id }}
        </div>
      </div>

      <!-- Action Button -->
      <button
        @click="$emit('close')"
        class="mt-6 w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-600 hover:to-indigo-700 transition"
      >
        Close
      </button>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'ResultModal',
  props: {
    prediction: {
      type: Object,
      required: true
    }
  },
  emits: ['close'],
  setup(props) {
    const confidencePercent = computed(() => {
      return Math.min(100, Math.round((props.prediction.confidence || 0) * 100))
    })

    const confidenceColor = computed(() => {
      const confidence = props.prediction.confidence
      if (confidence >= 0.9) return 'bg-green-500'
      if (confidence >= 0.75) return 'bg-blue-500'
      if (confidence >= 0.6) return 'bg-yellow-500'
      return 'bg-orange-500'
    })

    return {
      confidencePercent,
      confidenceColor
    }
  }
}
</script>
