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
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Token ${token}`
    }
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
export const uploadImage = async (imageFile, patient) => {
  const formData = new FormData()
  formData.append('image', imageFile)
  formData.append('patient_name', patient.patient_name)
  formData.append('age', patient.age)
  formData.append('gender', patient.gender)
  formData.append('mrn', patient.mrn)
  
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

export const getTransaction = async (id) => {
  const response = await api.get(`/api/v1/history/${id}/`)
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

// Auth APIs
export const register = async ({ username, password, email }) => {
  const response = await api.post('/api/v1/auth/register/', { username, password, email })
  return response.data
}

export const login = async ({ username, password }) => {
  const response = await api.post('/api/v1/auth/login/', { username, password })
  return response.data
}

export const me = async () => {
  const response = await api.get('/api/v1/auth/me/')
  return response.data
}

export const getProfile = async () => {
  const response = await api.get('/api/v1/auth/profile/')
  return response.data
}

export const updateProfile = async (profileData) => {
  const response = await api.put('/api/v1/auth/profile/', profileData)
  return response.data
}

export default api
