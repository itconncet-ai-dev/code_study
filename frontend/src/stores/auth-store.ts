import { create } from 'zustand'

/**
 * User entity matching backend User schema.
 * Contains non-sensitive user information for display purposes.
 */
export interface User {
  id: string
  email: string
  username: string
  created_at: string
}

/**
 * Authentication store state interface.
 * Manages JWT authentication state for the frontend application.
 */
interface AuthState {
  /** Current authenticated user or null if not logged in */
  user: User | null

  /** Whether the user is currently authenticated */
  isAuthenticated: boolean

  /** Whether an auth operation (login/register/fetch user) is in progress */
  isLoading: boolean

  /** Error message from the last failed auth operation */
  error: string | null

  /** Whether the auth state has been initialized (checked on app load) */
  isInitialized: boolean
}

/**
 * Authentication store actions interface.
 * Provides methods to manage authentication state.
 */
interface AuthActions {
  /** Set the current user and update authentication status */
  setUser: (user: User | null) => void

  /** Update the loading state for auth operations */
  setLoading: (isLoading: boolean) => void

  /** Set an error message from auth operations */
  setError: (error: string | null) => void

  /** Mark the auth store as initialized after initial auth check */
  setInitialized: (isInitialized: boolean) => void

  /** Clear auth state on logout (preserves isInitialized) */
  clearAuth: () => void

  /** Reset all state to initial values (for testing) */
  reset: () => void
}

/** Combined store type */
type AuthStore = AuthState & AuthActions

/** Initial state values */
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  isInitialized: false,
}

/**
 * Zustand auth store for managing JWT authentication state.
 *
 * This store handles:
 * - User session state (logged in/out)
 * - Authentication status tracking
 * - Loading states for auth operations
 * - Error handling for auth failures
 *
 * Note: JWT tokens are stored in HTTPOnly cookies (managed by backend),
 * not in this store. This store only tracks the authentication state
 * and user information for UI purposes.
 *
 * Usage:
 * ```tsx
 * // In a component
 * const { user, isAuthenticated } = useAuthStore()
 *
 * // Check auth status
 * if (isAuthenticated) {
 *   console.log(`Logged in as ${user?.username}`)
 * }
 *
 * // Update after login
 * useAuthStore.getState().setUser(userData)
 * ```
 */
export const useAuthStore = create<AuthStore>((set) => ({
  // State
  ...initialState,

  // Actions
  setUser: (user) =>
    set({
      user,
      isAuthenticated: user !== null,
      error: null,
    }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  setInitialized: (isInitialized) => set({ isInitialized }),

  clearAuth: () =>
    set({
      user: null,
      isAuthenticated: false,
      error: null,
      // Keep isInitialized true - we know the auth state (logged out)
    }),

  reset: () => set(initialState),
}))

export default useAuthStore
