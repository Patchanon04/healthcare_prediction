<template>
  <div class="bg-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
    <h2 class="text-2xl font-semibold text-gray-800 mb-6">Upload Medical Image</h2>
    
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Image Preview -->
      <div 
        v-if="imagePreview" 
        class="relative w-full h-64 bg-gray-100 rounded-lg overflow-hidden"
      >
        <img 
          :src="imagePreview" 
          alt="Preview" 
          class="w-full h-full object-contain"
        />
        <button
          type="button"
          @click="clearImage"
          class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-2 hover:bg-red-600 transition"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Upload Area -->
      <div 
        v-else
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        :class="[
          'border-2 border-dashed rounded-lg p-8 text-center transition',
          isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        ]"
      >
        <input
          ref="fileInput"
          type="file"
          accept="image/jpeg,image/jpg,image/png"
          @change="handleFileSelect"
          class="hidden"
        />
        
        <div class="space-y-4">
          <div class="text-6xl">📸</div>
          <div>
            <p class="text-lg text-gray-600 mb-2">
              Drag and drop your medical image here
            </p>
            <p class="text-sm text-gray-500 mb-4">or</p>
            <button
              type="button"
              @click="$refs.fileInput.click()"
              class="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition"
            >
              Browse Files
            </button>
          </div>
          <p class="text-xs text-gray-500">
            Supported formats: JPG, PNG | Max size: 10MB
          </p>
        </div>
      </div>

      <!-- File Info -->
      <div v-if="selectedFile" class="bg-gray-50 rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-gray-800">{{ selectedFile.name }}</p>
            <p class="text-sm text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
          </div>
          <svg class="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
      </div>

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="!selectedFile || isLoading"
        :class="[
          'w-full py-3 px-6 rounded-lg font-semibold text-white transition',
          !selectedFile || isLoading 
            ? 'bg-gray-300 cursor-not-allowed' 
            : 'bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700'
        ]"
      >
        <span v-if="isLoading" class="flex items-center justify-center">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Analyzing...
        </span>
        <span v-else>Predict Breed</span>
      </button>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'
import { uploadImage } from '../services/api'

export default {
  name: 'UploadForm',
  props: {
    patient: {
      type: Object,
      required: false,
      default: () => ({})
    }
  },
  emits: ['upload-success', 'upload-error'],
  setup(props, { emit }) {
    const fileInput = ref(null)
    const selectedFile = ref(null)
    const imagePreview = ref(null)
    const isLoading = ref(false)
    const isDragging = ref(false)

    const validateFile = (file) => {
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png']
      const maxSize = 10 * 1024 * 1024 // 10MB

      if (!allowedTypes.includes(file.type)) {
        throw new Error('Only JPG and PNG images are allowed')
      }

      if (file.size > maxSize) {
        throw new Error('File size must be less than 10MB')
      }
    }

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        try {
          validateFile(file)
          selectedFile.value = file
          
          // Create preview
          const reader = new FileReader()
          reader.onload = (e) => {
            imagePreview.value = e.target.result
          }
          reader.readAsDataURL(file)
        } catch (error) {
          emit('upload-error', error.message)
        }
      }
    }

    const handleDrop = (event) => {
      isDragging.value = false
      const file = event.dataTransfer.files[0]
      
      if (file) {
        try {
          validateFile(file)
          selectedFile.value = file
          
          const reader = new FileReader()
          reader.onload = (e) => {
            imagePreview.value = e.target.result
          }
          reader.readAsDataURL(file)
        } catch (error) {
          emit('upload-error', error.message)
        }
      }
    }

    const clearImage = () => {
      selectedFile.value = null
      imagePreview.value = null
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    const handleSubmit = async () => {
      if (!selectedFile.value) return

      isLoading.value = true

      try {
        // minimal patient validation if provided
        const p = props.patient || {}
        const required = ['patient_name', 'age', 'gender', 'mrn']
        for (const key of required) {
          if (p[key] === undefined || p[key] === null || p[key] === '') {
            throw new Error('Please fill patient information completely')
          }
        }
        const result = await uploadImage(selectedFile.value, p)
        emit('upload-success', result)
        clearImage()
      } catch (error) {
        emit('upload-error', error.message || 'Upload failed')
      } finally {
        isLoading.value = false
      }
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }

    return {
      fileInput,
      selectedFile,
      imagePreview,
      isLoading,
      isDragging,
      handleFileSelect,
      handleDrop,
      handleSubmit,
      clearImage,
      formatFileSize
    }
  }
}
</script>
