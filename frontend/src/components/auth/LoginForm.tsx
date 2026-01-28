import { useState, FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'

/**
 * Props for the LoginForm component.
 */
export interface LoginFormProps {
  /** Callback when form is submitted with valid data */
  onSubmit: (email: string, password: string) => void
  /** Whether the form submission is in progress */
  isLoading?: boolean
  /** Error message to display */
  error?: string | null
}

/**
 * Form validation errors.
 */
interface FormErrors {
  email?: string
  password?: string
}

/**
 * Login form component with email and password fields.
 * Includes client-side validation, loading/error states, and forgot password link.
 */
export function LoginForm({ onSubmit, isLoading = false, error }: LoginFormProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [formErrors, setFormErrors] = useState<FormErrors>({})

  /**
   * Validate form fields.
   * @returns True if all fields are valid
   */
  const validateForm = (): boolean => {
    const errors: FormErrors = {}

    // Email validation
    if (!email) {
      errors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Please enter a valid email address'
    }

    // Password validation
    if (!password) {
      errors.password = 'Password is required'
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  /**
   * Handle form submission.
   */
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()

    if (validateForm()) {
      onSubmit(email, password)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* API Error Display */}
      {error && (
        <div
          className="rounded-md bg-destructive/15 p-3 text-sm text-destructive"
          role="alert"
        >
          {error}
        </div>
      )}

      {/* Email Field */}
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={isLoading}
          aria-invalid={!!formErrors.email}
          aria-describedby={formErrors.email ? 'email-error' : undefined}
        />
        {formErrors.email && (
          <p id="email-error" className="text-sm text-destructive">
            {formErrors.email}
          </p>
        )}
      </div>

      {/* Password Field */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="password">Password</Label>
          <Link
            to="/forgot-password"
            className="text-sm text-primary hover:underline"
          >
            Forgot password?
          </Link>
        </div>
        <Input
          id="password"
          type="password"
          placeholder="Enter your password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={isLoading}
          aria-invalid={!!formErrors.password}
          aria-describedby={formErrors.password ? 'password-error' : undefined}
        />
        {formErrors.password && (
          <p id="password-error" className="text-sm text-destructive">
            {formErrors.password}
          </p>
        )}
      </div>

      {/* Submit Button */}
      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? 'Signing in...' : 'Sign In'}
      </Button>
    </form>
  )
}

export default LoginForm
