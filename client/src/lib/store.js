/**
 * Zustand Store with JSDoc Type Hints
 * Central state management for the application
 *
 * @typedef {Object} Message
 * @property {string} id - Unique message ID
 * @property {string} text - Message content
 * @property {'user' | 'bot'} role - Who sent the message
 * @property {string} [timestamp] - ISO timestamp
 *
 * @typedef {Object} StudentRecord
 * @property {string} name - Student name
 * @property {number} grade - Grade level
 * @property {string} class_name - Class name
 * @property {string} [score] - Quiz score
 *
 * @typedef {Object} RoleModel
 * @property {number} grade - Grade level (7-12)
 * @property {string} class_name - Class identifier (A, B, C)
 *
 * @typedef {Object} AppState
 * @property {string} theme - Current theme ('dark' or 'light')
 * @property {boolean} sidebarOpen - Sidebar visibility state
 * @property {Message[]} messages - Conversation history
 * @property {StudentRecord[]} results - Query results
 * @property {string} condition - Generated filter condition
 * @property {boolean} loading - Loading state
 * @property {string|null} error - Error message
 * @property {RoleModel} role - Current role settings
 * @property {(theme: string) => void} setTheme - Set theme
 * @property {(open: boolean) => void} setSidebarOpen - Toggle sidebar
 * @property {(message: Message) => void} addMessage - Add message to history
 * @property {(messages: Message[]) => void} setMessages - Set all messages
 * @property {(results: StudentRecord[]) => void} setResults - Set query results
 * @property {(condition: string) => void} setCondition - Set filter condition
 * @property {(loading: boolean) => void} setLoading - Set loading state
 * @property {(error: string|null) => void} setError - Set error message
 * @property {(role: RoleModel) => void} setRole - Set role settings
 * @property {() => void} resetQuery - Reset query state
 * @property {() => void} clearError - Clear error message
 */

import { create } from 'zustand'

/**
 * Global Zustand store for application state
 * @type {import('zustand').UseBoundStore<AppState>}
 */
export const useAppStore = create((set) => ({
  // UI State
  theme: 'dark',
  sidebarOpen: true,

  // Query State
  messages: [],
  results: [],
  condition: '',
  loading: false,
  error: null,

  // Role State
  role: { grade: 8, class_name: 'A' },

  // Actions
  /**
   * Set the current theme
   * @param {string} theme - Theme name
   */
  setTheme: (theme) => set({ theme }),

  /**
   * Toggle sidebar visibility
   * @param {boolean} open - Sidebar open state
   */
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  /**
   * Add a message to the conversation history
   * @param {Message} message - Message to add
   */
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),

  /**
   * Set all messages at once
   * @param {Message[]} messages - Array of messages
   */
  setMessages: (messages) => set({ messages }),

  /**
   * Set query results
   * @param {StudentRecord[]} results - Array of student records
   */
  setResults: (results) => set({ results }),

  /**
   * Set the filter condition
   * @param {string} condition - Filter condition string
   */
  setCondition: (condition) => set({ condition }),

  /**
   * Set loading state
   * @param {boolean} loading - Loading state
   */
  setLoading: (loading) => set({ loading }),

  /**
   * Set error message
   * @param {string|null} error - Error message or null
   */
  setError: (error) => set({ error }),

  /**
   * Set role configuration
   * @param {RoleModel} role - Role settings
   */
  setRole: (role) => set({ role }),

  /**
   * Reset query-related state
   */
  resetQuery: () => set({
    messages: [],
    results: [],
    condition: '',
    error: null
  }),

  /**
   * Clear error message
   */
  clearError: () => set({ error: null })
}))
