import axios from 'axios'

// Get API URL from environment or fallback
const getApiUrl = () => {
  // Try Vite env first
  if (import.meta && import.meta.env && import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  // Try Vue CLI env (legacy)
  if (process.env.VUE_APP_API_URL) {
    return process.env.VUE_APP_API_URL
  }
  // Fallback: empty string (same-origin)
  return ''
}

// Create axios instance with default config
const apiUrl = getApiUrl()
console.log('🔧 API Base URL:', apiUrl || '(same-origin)')

const api = axios.create({
  baseURL: apiUrl,
  timeout: 60000,
  // Do not set a static Content-Type here. We'll set it per-request in the interceptor
})

// Request interceptor
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Token ${token}`
    }

    // Dynamically set Content-Type
    // - For FormData: let the browser set the proper multipart boundary
    // - Otherwise: JSON
    const isFormData = typeof FormData !== 'undefined' && config.data instanceof FormData
    if (isFormData) {
      // Ensure we don't override the boundary
      delete config.headers['Content-Type']
    } else {
      config.headers['Content-Type'] = 'application/json'
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
  // Prefer patient_id if provided (new flow)
  if (patient?.patient_id) {
    formData.append('patient_id', patient.patient_id)
  } else {
    // Legacy fields for backward compatibility
    formData.append('patient_name', patient.patient_name)
    formData.append('age', patient.age)
    formData.append('gender', patient.gender)
    formData.append('mrn', patient.mrn)
    if (patient.phone) formData.append('phone', patient.phone)
  }
  
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

// Patient APIs
export const listPatients = async ({ page = 1, pageSize = 10, search = '' } = {}) => {
  const response = await api.get('/api/v1/patients/', {
    params: { page, page_size: pageSize, ...(search ? { search } : {}) },
  })
  return response.data
}

export const getPatient = async (id) => {
  const response = await api.get(`/api/v1/patients/${id}/`)
  return response.data
}

export const createPatient = async (data) => {
  const response = await api.post('/api/v1/patients/', data)
  return response.data
}

export const getPatientTransactions = async (id, { page = 1, pageSize = 10 } = {}) => {
  const response = await api.get(`/api/v1/patients/${id}/transactions/`, {
    params: { page, page_size: pageSize },
  })
  return response.data
}

export const updatePatient = async (id, data) => {
  const response = await api.put(`/api/v1/patients/${id}/`, data)
  return response.data
}

// Dashboard metrics
export const getMetricsSummary = async () => {
  const res = await api.get('/api/v1/metrics/summary/')
  return res.data
}

export const getMetricsDaily = async (days = 14) => {
  const res = await api.get('/api/v1/metrics/daily/', { params: { days } })
  return res.data
}

export const getDiagnosisDistribution = async () => {
  const res = await api.get('/api/v1/metrics/diagnosis-distribution/')
  return res.data
}

export const getReportSummary = async ({ start, end } = {}) => {
  const res = await api.get('/api/v1/reports/summary/', { params: { start, end } })
  return res.data
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

// Chat APIs
export const listChatUsers = async () => {
  const response = await api.get('/api/v1/chat/users/')
  return response.data
}

export const listChatRooms = async ({ page = 1, pageSize = 20 } = {}) => {
  const response = await api.get('/api/v1/chat/rooms/', {
    params: { page, page_size: pageSize }
  })
  return response.data
}

export const getChatRoom = async (roomId) => {
  const response = await api.get(`/api/v1/chat/rooms/${roomId}/`)
  return response.data
}

export const createChatRoom = async (data) => {
  const response = await api.post('/api/v1/chat/rooms/', data)
  return response.data
}

export const listMessages = async (roomId, { page = 1, pageSize = 50 } = {}) => {
  const response = await api.get(`/api/v1/chat/rooms/${roomId}/messages/`, {
    params: { page, page_size: pageSize }
  })
  return response.data
}

export const sendMessage = async (roomId, content) => {
  const response = await api.post(`/api/v1/chat/rooms/${roomId}/messages/`, { content })
  return response.data
}

export const markMessagesRead = async (roomId, messageIds) => {
  const response = await api.post(`/api/v1/chat/rooms/${roomId}/read/`, { message_ids: messageIds })
  return response.data
}

export default api
