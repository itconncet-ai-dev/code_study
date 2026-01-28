import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '../../src/lib/queryClient'
import App from '../../src/App'

const renderWithProviders = (ui: React.ReactElement) => {
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>)
}

describe('App', () => {
  it('renders the dashboard page at root route', () => {
    renderWithProviders(<App />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('renders the project list placeholder', () => {
    renderWithProviders(<App />)
    expect(
      screen.getByText('Project list - to be implemented')
    ).toBeInTheDocument()
  })
})
