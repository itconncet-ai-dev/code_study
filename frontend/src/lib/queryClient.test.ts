import { describe, it, expect } from 'vitest'
import { queryClient, defaultQueryOptions } from './queryClient'

describe('queryClient', () => {
  it('should be a QueryClient instance', () => {
    expect(queryClient).toBeDefined()
    expect(typeof queryClient.getQueryCache).toBe('function')
    expect(typeof queryClient.getMutationCache).toBe('function')
  })

  it('should have default query options configured', () => {
    const defaultOptions = queryClient.getDefaultOptions()
    expect(defaultOptions.queries).toBeDefined()
  })

  it('should have retry set to 3 for queries', () => {
    const defaultOptions = queryClient.getDefaultOptions()
    expect(defaultOptions.queries?.retry).toBe(3)
  })

  it('should have staleTime configured for caching', () => {
    const defaultOptions = queryClient.getDefaultOptions()
    // 5 minutes stale time for caching
    expect(defaultOptions.queries?.staleTime).toBe(5 * 60 * 1000)
  })

  it('should have refetchOnWindowFocus set appropriately', () => {
    const defaultOptions = queryClient.getDefaultOptions()
    // Disable refetch on window focus to avoid unexpected API calls
    expect(defaultOptions.queries?.refetchOnWindowFocus).toBe(false)
  })

  it('should export defaultQueryOptions for custom configurations', () => {
    expect(defaultQueryOptions).toBeDefined()
    expect(defaultQueryOptions.retry).toBe(3)
    expect(defaultQueryOptions.staleTime).toBe(5 * 60 * 1000)
  })
})
