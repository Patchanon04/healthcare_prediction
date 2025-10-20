import axios from 'axios'

// Create axios instance with default config
const api = axios.create({
  // Use same-origin by default so requests go through Nginx proxy (/api -> backend)
  // Allow override via VUE_APP_API_URL for dev or explicit deployments
  baseURL: process.env.VUE_APP_API_URL || '',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    const errorMessage = error.response?.data?.error || error.message || 'An error occurred'
    return Promise.reject(new Error(errorMessage))
  }
)

/**
 * Upload image for breed prediction
 * @param {File} imageFile - The image file to upload
 * @returns {Promise} - Promise with prediction result
 */
export const uploadImage = async (imageFile) => {
  const formData = new FormData()
  formData.append('image', imageFile)
  
  const response = await api.post('/api/v1/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    }
  })
  
  return response.data
}

/**
 * Get prediction history with pagination
 * @param {number} page - Page number
 * @param {number} pageSize - Number of items per page
 * @returns {Promise} - Promise with history data
 */
export const getHistory = async (page = 1, pageSize = 10) => {
  const response = await api.get('/api/v1/history/', {
    params: { page, page_size: pageSize }
  })
  
  return response.data
}

/**
 * Check backend health status
 * @returns {Promise} - Promise with health status
 */
export const checkHealth = async () => {
  const response = await api.get('/api/v1/health/')
  return response.data
}

export default api
