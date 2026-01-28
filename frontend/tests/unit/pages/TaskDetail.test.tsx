import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import TaskDetail from '@/pages/TaskDetail'
import * as taskService from '@/services/task-service'

vi.mock('@/services/task-service', () => ({
  taskService: {
    getTask: vi.fn(),
  },
}))

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
})

const renderWithRouter = (taskId: string) => {
  window.history.pushState({}, 'Test', `/tasks/${taskId}`)
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/tasks/:taskId" element={<TaskDetail />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('TaskDetail', () => {
  it('should render task header', async () => {
    const mockTask = {
      id: 'task-1',
      project_id: 'project-1',
      task_number: 1,
      title: 'Test Task',
      upload_method: 'file' as const,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      deletion_status: 'active' as const,
    }

    vi.mocked(taskService.taskService.getTask).mockResolvedValue(mockTask)

    renderWithRouter('task-1')

    await waitFor(() => {
      expect(screen.getByText(/작업 #1/)).toBeInTheDocument()
      expect(screen.getByText('Test Task')).toBeInTheDocument()
    })
  })

  it('should render tab navigation', async () => {
    const mockTask = {
      id: 'task-1',
      project_id: 'project-1',
      task_number: 1,
      title: 'Test Task',
      upload_method: 'file' as const,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      deletion_status: 'active' as const,
    }

    vi.mocked(taskService.taskService.getTask).mockResolvedValue(mockTask)

    renderWithRouter('task-1')

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /문서/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /실습/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /Q&A/i })).toBeInTheDocument()
    })
  })

  it('should show back navigation', async () => {
    const mockTask = {
      id: 'task-1',
      project_id: 'project-1',
      task_number: 1,
      title: 'Test Task',
      upload_method: 'file' as const,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      deletion_status: 'active' as const,
    }

    vi.mocked(taskService.taskService.getTask).mockResolvedValue(mockTask)

    renderWithRouter('task-1')

    await waitFor(() => {
      const backLink = screen.getByText(/프로젝트로 돌아가기/i)
      expect(backLink).toBeInTheDocument()
    })
  })

  it('should not crash when data is loading', () => {
    const mockTask = {
      id: 'task-1',
      project_id: 'project-1',
      task_number: 1,
      title: 'Test Task',
      upload_method: 'file' as const,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      deletion_status: 'active' as const,
    }

    vi.mocked(taskService.taskService.getTask).mockResolvedValue(mockTask)

    const { container } = renderWithRouter('task-1')

    // Component should render without crashing
    expect(container).toBeInTheDocument()
  })
})
