import { useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { LoginForm } from '@/components/auth/LoginForm'
import { useAuth } from '@/hooks/useAuth'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

/**
 * Location state for redirect after login.
 */
interface LocationState {
  from?: { pathname: string }
}

/**
 * Login page component.
 * Displays the login form and handles user authentication.
 * Redirects to dashboard (or previous location) on successful login.
 */
export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isAuthenticated, isLoginLoading, loginError, error } = useAuth()

  // Get the redirect path from location state (set by ProtectedRoute)
  const from = (location.state as LocationState)?.from?.pathname || '/'

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true })
    }
  }, [isAuthenticated, navigate, from])

  /**
   * Handle form submission.
   */
  const handleSubmit = async (email: string, password: string) => {
    try {
      await login(email, password)
      navigate(from, { replace: true })
    } catch {
      // Error is handled by the hook and displayed via error state
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">Welcome back</CardTitle>
          <CardDescription>
            Enter your credentials to sign in to your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <LoginForm
            onSubmit={handleSubmit}
            isLoading={isLoginLoading}
            error={loginError || error}
          />
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          <div className="text-center text-sm text-muted-foreground">
            Don&apos;t have an account?{' '}
            <Link to="/register" className="text-primary hover:underline">
              Sign up
            </Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
