import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { RegisterForm } from '@/components/auth/RegisterForm'
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
 * Registration page component.
 * Displays the registration form and handles user registration.
 * Redirects to dashboard on successful registration.
 */
export default function Register() {
  const navigate = useNavigate()
  const { register, isAuthenticated, isRegisterLoading, registerError, error } =
    useAuth()

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true })
    }
  }, [isAuthenticated, navigate])

  /**
   * Handle form submission.
   */
  const handleSubmit = async (email: string, password: string) => {
    try {
      await register(email, password)
      navigate('/', { replace: true })
    } catch {
      // Error is handled by the hook and displayed via error state
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">Create an account</CardTitle>
          <CardDescription>
            Enter your email and password to create your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <RegisterForm
            onSubmit={handleSubmit}
            isLoading={isRegisterLoading}
            error={registerError || error}
          />
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          <div className="text-center text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link to="/login" className="text-primary hover:underline">
              Sign in
            </Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
