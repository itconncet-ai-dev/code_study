import { useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuthStore, User } from '@/stores/auth-store'
import { authService } from '@/services/auth-service'
import { ApiClientError } from '@/services/api-client'

/**
 * Query key for the current user.
 */
export const AUTH_QUERY_KEY = ['auth', 'user'] as const

/**
 * Custom hook for authentication operations.
 * Provides login, register, logout mutations and current user query.
 * Handles automatic token refresh on 401 errors.
 */
export function useAuth() {
  const queryClient = useQueryClient()
  const {
    user,
    isAuthenticated,
    isInitialized,
    isLoading: storeLoading,
    error: storeError,
    setUser,
    setLoading,
    setError,
    setInitialized,
    clearAuth,
  } = useAuthStore()

  /**
   * Query for fetching the current user.
   * Runs on mount to check if user is already authenticated (via cookies).
   */
  const {
    data: currentUser,
    isLoading: isUserLoading,
    error: userError,
    refetch: refetchUser,
  } = useQuery({
    queryKey: AUTH_QUERY_KEY,
    queryFn: authService.getCurrentUser,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: !isInitialized, // Only run on initial load
  })

  /**
   * Update store when user data changes.
   */
  useEffect(() => {
    if (currentUser) {
      setUser(currentUser)
      setInitialized(true)
    } else if (userError) {
      // User is not authenticated
      setUser(null)
      setInitialized(true)
    }
  }, [currentUser, userError, setUser, setInitialized])

  /**
   * Mark as initialized if query is complete but user is null.
   */
  useEffect(() => {
    if (!isUserLoading && !isInitialized) {
      setInitialized(true)
    }
  }, [isUserLoading, isInitialized, setInitialized])

  /**
   * Login mutation.
   */
  const loginMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authService.login({ email, password }),
    onMutate: () => {
      setLoading(true)
      setError(null)
    },
    onSuccess: (userData: User) => {
      setUser(userData)
      queryClient.setQueryData(AUTH_QUERY_KEY, userData)
    },
    onError: (error: ApiClientError) => {
      setError(error.message)
    },
    onSettled: () => {
      setLoading(false)
    },
  })

  /**
   * Register mutation.
   */
  const registerMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authService.register({ email, password }),
    onMutate: () => {
      setLoading(true)
      setError(null)
    },
    onSuccess: (userData: User) => {
      setUser(userData)
      queryClient.setQueryData(AUTH_QUERY_KEY, userData)
    },
    onError: (error: ApiClientError) => {
      setError(error.message)
    },
    onSettled: () => {
      setLoading(false)
    },
  })

  /**
   * Logout mutation.
   */
  const logoutMutation = useMutation({
    mutationFn: authService.logout,
    onMutate: () => {
      setLoading(true)
    },
    onSuccess: () => {
      clearAuth()
      queryClient.setQueryData(AUTH_QUERY_KEY, null)
      queryClient.clear() // Clear all cached data on logout
    },
    onError: () => {
      // Even on error, clear local auth state
      clearAuth()
      queryClient.clear()
    },
    onSettled: () => {
      setLoading(false)
    },
  })

  /**
   * Refresh token mutation.
   * Called automatically by api-client on 401 errors.
   */
  const refreshTokenMutation = useMutation({
    mutationFn: authService.refreshToken,
    onSuccess: () => {
      // Refetch user data after successful refresh
      refetchUser()
    },
    onError: () => {
      // Token refresh failed, clear auth state
      clearAuth()
      queryClient.clear()
    },
  })

  /**
   * Login with email and password.
   */
  const login = (email: string, password: string) => {
    return loginMutation.mutateAsync({ email, password })
  }

  /**
   * Register a new user.
   */
  const register = (email: string, password: string) => {
    return registerMutation.mutateAsync({ email, password })
  }

  /**
   * Logout the current user.
   */
  const logout = () => {
    return logoutMutation.mutateAsync()
  }

  /**
   * Refresh the authentication token.
   */
  const refreshToken = () => {
    return refreshTokenMutation.mutateAsync()
  }

  return {
    // State
    user,
    isAuthenticated,
    isInitialized,
    isLoading: storeLoading || isUserLoading,
    error: storeError,

    // Mutations
    login,
    register,
    logout,
    refreshToken,

    // Mutation states
    isLoginLoading: loginMutation.isPending,
    isRegisterLoading: registerMutation.isPending,
    isLogoutLoading: logoutMutation.isPending,
    loginError: loginMutation.error?.message,
    registerError: registerMutation.error?.message,
  }
}

export default useAuth
