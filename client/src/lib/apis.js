/**
 * API Service Layer with JSDoc Type Hints
 */

import axios from 'axios'

class APIClient {
constructor(baseURL) {
  this.baseURL =
    baseURL ||
    import.meta.env.VITE_API_BASE ||
    (import.meta.env.PROD
      ? 'https://dumroo-ai-praveen.onrender.com'
      : 'http://localhost:8000')

  this.axiosInstance = axios.create({
    baseURL: this.baseURL,
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },
  })

  this.axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => this.handleError(error)
  )
}


  /**
   * Handle API errors
   * @param {Error} error - The error object
   * @returns {Promise} - Rejected promise
   */
  handleError(error) {
    if (error.response?.data) {
      throw error.response.data
    }
    throw {
      error: error.message || 'Network error',
      code: 'NETWORK_ERROR',
      timestamp: new Date().toISOString(),
    }
  }

  /**
   * Execute a natural language query
   * @param {Object} data - Query request data
   * @returns {Promise<Object>} - Query result or error
   */
  async postQuery(data) {
    try {
      const response = await this.axiosInstance.post('/query', data)
      return response.data
    } catch (error) {
      const errorData = error.response?.data || {}
      return {
        error: errorData.detail || error.message || 'Failed to process query',
        condition: '',
        results: [],
        count: 0,
        timestamp: new Date().toISOString(),
      }
    }
  }

  /**
   * Get system statistics
   * @param {number} grade - Grade level
   * @param {string} classId - Class ID
   * @returns {Promise<Object>} - Statistics data
   */
  async getStats(grade, classId) {
    try {
      const params = new URLSearchParams()
      if (grade !== undefined) params.append('grade', String(grade))
      if (classId) params.append('class_name', classId)

      const response = await this.axiosInstance.get(
        `/stats${params.toString() ? '?' + params.toString() : ''}`
      )
      return {
        data: response.data,
        status: 'success',
        timestamp: new Date().toISOString(),
      }
    } catch (error) {
      return {
        error: error.error || 'Failed to fetch statistics',
        status: 'error',
        timestamp: new Date().toISOString(),
      }
    }
  }

  /**
   * Check API health
   * @returns {Promise<Object>} - Health status
   */
  async getHealth() {
    try {
      const response = await this.axiosInstance.get('/health')
      return {
        data: response.data,
        status: 'success',
        timestamp: new Date().toISOString(),
      }
    } catch (error) {
      return {
        error: error.error || 'Health check failed',
        status: 'error',
        timestamp: new Date().toISOString(),
      }
    }
  }

  /**
   * Get base URL
   * @returns {string} - Base URL
   */
  getBaseURL() {
    return this.baseURL
  }

  /**
   * Set authorization header
   * @param {string} token - Authorization token
   */
  setAuthHeader(token) {
    this.axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  /**
   * Clear authorization header
   */
  clearAuthHeader() {
    delete this.axiosInstance.defaults.headers.common['Authorization']
  }
}

// Export singleton instance
export const api = new APIClient()

export default api

