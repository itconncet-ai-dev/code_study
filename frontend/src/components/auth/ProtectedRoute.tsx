import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import useAuth from '@/hooks/useAuth'

/**
 * Props for the ProtectedRoute component.
 */
export interface ProtectedRouteProps {
  /** Child components to render if authenticated */
  children: ReactNode
  /** Route to redirect to if not authenticated (default: /login) */
  redirectTo?: string
}

/**
 * Wrapper component for protecting routes that require authentication.
 * Redirects to login page if user is not authenticated.
 * Shows loading state while checking authentication.
 */
export function ProtectedRoute({ children, redirectTo = '/login' }: ProtectedRouteProps) {
  const { isAuthenticated, isInitialized, isLoading } = useAuth()
  const location = useLocation()

  // Show loading state while checking authentication
  if (!isInitialized || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto"></div>
          <p className="mt-2 text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    // Pass the current location so we can redirect back after login
    return <Navigate to={redirectTo} state={{ from: location }} replace />
  }

  // User is authenticated, render children
  return <>{children}</>
}

export default ProtectedRoute
