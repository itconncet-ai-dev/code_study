import { get, post } from './api-client'
import { User } from '@/stores/auth-store'

/**
 * Login credentials for authentication.
 */
export interface LoginCredentials {
  email: string
  password: string
}

/**
 * Registration data for creating a new user.
 */
export interface RegisterData {
  email: string
  password: string
}

/**
 * Authentication service for handling user authentication operations.
 * Uses the API client for HTTP requests with cookie-based JWT authentication.
 */
export const authService = {
  /**
   * Register a new user.
   * @param data - Registration data (email, password)
   * @returns The created user
   */
  async register(data: RegisterData): Promise<User> {
    return post<User>('/auth/register', data)
  },

  /**
   * Login a user with credentials.
   * Sets authentication cookies on success.
   * @param credentials - Login credentials (email, password)
   * @returns The authenticated user
   */
  async login(credentials: LoginCredentials): Promise<User> {
    return post<User>('/auth/login', credentials)
  },

  /**
   * Logout the current user.
   * Clears authentication cookies.
   */
  async logout(): Promise<void> {
    return post<void>('/auth/logout')
  },

  /**
   * Get the current authenticated user.
   * @returns The current user or throws if not authenticated
   */
  async getCurrentUser(): Promise<User> {
    return get<User>('/auth/me')
  },

  /**
   * Refresh the access token using the refresh token.
   * @returns Success status
   */
  async refreshToken(): Promise<void> {
    return post<void>('/auth/refresh')
  },
}

export default authService
