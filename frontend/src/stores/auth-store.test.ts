import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuthStore } from './auth-store'
import type { User } from './auth-store'

// Mock user data
const mockUser: User = {
  id: 'user-123',
  email: 'test@example.com',
  username: 'testuser',
  created_at: '2024-01-01T00:00:00Z',
}

describe('useAuthStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.getState().reset()
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const state = useAuthStore.getState()

      expect(state.user).toBeNull()
      expect(state.isAuthenticated).toBe(false)
      expect(state.isLoading).toBe(false)
      expect(state.error).toBeNull()
      expect(state.isInitialized).toBe(false)
    })
  })

  describe('setUser', () => {
    it('should set user and mark as authenticated', () => {
      useAuthStore.getState().setUser(mockUser)

      const state = useAuthStore.getState()
      expect(state.user).toEqual(mockUser)
      expect(state.isAuthenticated).toBe(true)
      expect(state.error).toBeNull()
    })

    it('should clear user when setting to null', () => {
      // First set a user
      useAuthStore.getState().setUser(mockUser)
      // Then clear it
      useAuthStore.getState().setUser(null)

      const state = useAuthStore.getState()
      expect(state.user).toBeNull()
      expect(state.isAuthenticated).toBe(false)
    })
  })

  describe('setLoading', () => {
    it('should update loading state', () => {
      useAuthStore.getState().setLoading(true)
      expect(useAuthStore.getState().isLoading).toBe(true)

      useAuthStore.getState().setLoading(false)
      expect(useAuthStore.getState().isLoading).toBe(false)
    })
  })

  describe('setError', () => {
    it('should set error message', () => {
      const errorMessage = 'Authentication failed'
      useAuthStore.getState().setError(errorMessage)

      expect(useAuthStore.getState().error).toBe(errorMessage)
    })

    it('should clear error when setting to null', () => {
      useAuthStore.getState().setError('Some error')
      useAuthStore.getState().setError(null)

      expect(useAuthStore.getState().error).toBeNull()
    })
  })

  describe('setInitialized', () => {
    it('should mark store as initialized', () => {
      useAuthStore.getState().setInitialized(true)

      expect(useAuthStore.getState().isInitialized).toBe(true)
    })
  })

  describe('clearAuth', () => {
    it('should clear user and auth state', () => {
      // Setup authenticated state
      useAuthStore.getState().setUser(mockUser)
      useAuthStore.getState().setInitialized(true)

      // Clear auth
      useAuthStore.getState().clearAuth()

      const state = useAuthStore.getState()
      expect(state.user).toBeNull()
      expect(state.isAuthenticated).toBe(false)
      expect(state.error).toBeNull()
      // isInitialized should remain true (we know auth state, just logged out)
      expect(state.isInitialized).toBe(true)
    })
  })

  describe('reset', () => {
    it('should reset all state to initial values', () => {
      // Modify all state
      useAuthStore.getState().setUser(mockUser)
      useAuthStore.getState().setLoading(true)
      useAuthStore.getState().setError('Some error')
      useAuthStore.getState().setInitialized(true)

      // Reset
      useAuthStore.getState().reset()

      const state = useAuthStore.getState()
      expect(state.user).toBeNull()
      expect(state.isAuthenticated).toBe(false)
      expect(state.isLoading).toBe(false)
      expect(state.error).toBeNull()
      expect(state.isInitialized).toBe(false)
    })
  })

  describe('selectors', () => {
    it('should provide isLoggedIn computed value', () => {
      expect(useAuthStore.getState().isAuthenticated).toBe(false)

      useAuthStore.getState().setUser(mockUser)
      expect(useAuthStore.getState().isAuthenticated).toBe(true)
    })
  })
})
