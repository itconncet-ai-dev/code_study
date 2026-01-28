import { QueryClient } from '@tanstack/react-query'

/**
 * Default query options for the application.
 * These settings are optimized for a learning platform with
 * moderate caching and retry strategies.
 */
export const defaultQueryOptions = {
  retry: 3,
  staleTime: 5 * 60 * 1000, // 5 minutes
  refetchOnWindowFocus: false,
}

/**
 * Configured QueryClient instance for the application.
 * Uses default options suitable for API data fetching with:
 * - 3 retry attempts for failed queries
 * - 5 minute stale time for caching
 * - Disabled refetch on window focus to avoid unexpected API calls
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: defaultQueryOptions,
  },
})
