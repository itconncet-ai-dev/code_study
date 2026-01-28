import axios, {
  AxiosError,
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios'

/**
 * API error response structure matching backend error schema.
 */
export interface ApiError {
  error: string
  detail?: string
  code?: string
}

/**
 * Custom error class for API errors with typed error data.
 */
export class ApiClientError extends Error {
  public readonly status: number
  public readonly data?: ApiError
  public readonly originalError: AxiosError

  constructor(error: AxiosError<ApiError>) {
    const message = error.response?.data?.error || error.message
    super(message)
    this.name = 'ApiClientError'
    this.status = error.response?.status || 0
    this.data = error.response?.data
    this.originalError = error
  }

  /**
   * Check if the error is an authentication error (401).
   */
  isUnauthorized(): boolean {
    return this.status === 401
  }

  /**
   * Check if the error is a forbidden error (403).
   */
  isForbidden(): boolean {
    return this.status === 403
  }

  /**
   * Check if the error is a not found error (404).
   */
  isNotFound(): boolean {
    return this.status === 404
  }

  /**
   * Check if the error is a validation error (400).
   */
  isValidationError(): boolean {
    return this.status === 400
  }

  /**
   * Check if the error is a server error (5xx).
   */
  isServerError(): boolean {
    return this.status >= 500
  }
}

/**
 * API base URL from environment or default to localhost development server.
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

/**
 * Flag to track if a token refresh is in progress.
 * Prevents multiple simultaneous refresh requests.
 */
let isRefreshing = false

/**
 * Queue of requests waiting for token refresh.
 * These requests will be retried after successful refresh.
 */
let refreshSubscribers: Array<(success: boolean) => void> = []

/**
 * Subscribe to token refresh completion.
 */
function subscribeToRefresh(callback: (success: boolean) => void): void {
  refreshSubscribers.push(callback)
}

/**
 * Notify all subscribers about refresh result.
 */
function notifyRefreshSubscribers(success: boolean): void {
  refreshSubscribers.forEach((callback) => callback(success))
  refreshSubscribers = []
}

/**
 * Attempt to refresh the access token using the refresh token.
 * Returns true if refresh was successful, false otherwise.
 */
async function refreshAccessToken(): Promise<boolean> {
  try {
    await axios.post(`${API_BASE_URL}/auth/refresh`, {}, { withCredentials: true })
    return true
  } catch {
    return false
  }
}

/**
 * Create and configure the axios instance.
 */
function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true, // Include cookies for JWT authentication
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 second timeout
  })

  // Request interceptor for error transformation
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => config,
    (error: AxiosError) => {
      return Promise.reject(new ApiClientError(error as AxiosError<ApiError>))
    }
  )

  // Response interceptor for error handling and token refresh
  client.interceptors.response.use(
    (response: AxiosResponse) => response,
    async (error: AxiosError<ApiError>) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & {
        _retry?: boolean
      }

      // Handle 401 Unauthorized - attempt token refresh
      if (error.response?.status === 401 && !originalRequest._retry) {
        // Skip refresh for auth endpoints to avoid infinite loops
        if (
          originalRequest.url?.includes('/auth/login') ||
          originalRequest.url?.includes('/auth/register') ||
          originalRequest.url?.includes('/auth/refresh')
        ) {
          return Promise.reject(new ApiClientError(error))
        }

        if (isRefreshing) {
          // Wait for ongoing refresh to complete
          return new Promise((resolve, reject) => {
            subscribeToRefresh((success) => {
              if (success) {
                resolve(client(originalRequest))
              } else {
                reject(new ApiClientError(error))
              }
            })
          })
        }

        originalRequest._retry = true
        isRefreshing = true

        const refreshSuccess = await refreshAccessToken()
        isRefreshing = false
        notifyRefreshSubscribers(refreshSuccess)

        if (refreshSuccess) {
          return client(originalRequest)
        }

        // Refresh failed - redirect to login or emit event
        // This will be handled by the auth store (T021)
        return Promise.reject(new ApiClientError(error))
      }

      return Promise.reject(new ApiClientError(error))
    }
  )

  return client
}

/**
 * Configured axios instance for API requests.
 * Includes:
 * - Base URL configuration
 * - Cookie-based JWT authentication (withCredentials)
 * - Automatic token refresh on 401 errors
 * - Request/response logging in development
 * - Typed error handling
 */
export const apiClient = createApiClient()

/**
 * Type-safe GET request.
 */
export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.get<T>(url, config)
  return response.data
}

/**
 * Type-safe POST request.
 */
export async function post<T, D = unknown>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.post<T>(url, data, config)
  return response.data
}

/**
 * Type-safe PATCH request.
 */
export async function patch<T, D = unknown>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.patch<T>(url, data, config)
  return response.data
}

/**
 * Type-safe PUT request.
 */
export async function put<T, D = unknown>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.put<T>(url, data, config)
  return response.data
}

/**
 * Type-safe DELETE request.
 */
export async function del<T = void>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.delete<T>(url, config)
  return response.data
}

/**
 * Upload file(s) with multipart/form-data.
 * Used for code upload endpoints.
 */
export async function uploadFiles<T>(
  url: string,
  formData: FormData,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.post<T>(url, formData, {
    ...config,
    headers: {
      ...config?.headers,
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export default apiClient
