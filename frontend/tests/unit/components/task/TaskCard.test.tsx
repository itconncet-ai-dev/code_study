import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { TaskCard } from '@/components/task/TaskCard'
import type { Task } from '@/types/task'

const mockTask: Task = {
  id: 'task-1',
  project_id: 'project-1',
  task_number: 1,
  title: 'Implement User Authentication',
  description: 'Add JWT-based authentication',
  upload_method: 'file',
  created_at: '2024-01-15T10:00:00Z',
  updated_at: '2024-01-15T10:00:00Z',
  deletion_status: 'active',
}

describe('TaskCard', () => {
  const renderWithRouter = (ui: React.ReactElement) => {
    return render(<BrowserRouter>{ui}</BrowserRouter>)
  }

  it('should render task information', () => {
    renderWithRouter(<TaskCard task={mockTask} />)

    expect(screen.getByText(/작업 #1/)).toBeInTheDocument()
    expect(screen.getByText('Implement User Authentication')).toBeInTheDocument()
    expect(screen.getByText('Add JWT-based authentication')).toBeInTheDocument()
  })

  it('should display upload method badge', () => {
    renderWithRouter(<TaskCard task={mockTask} />)

    expect(screen.getByText('파일')).toBeInTheDocument()
  })

  it('should show folder upload method badge', () => {
    const folderTask = { ...mockTask, upload_method: 'folder' as const }
    renderWithRouter(<TaskCard task={folderTask} />)

    expect(screen.getByText('폴더')).toBeInTheDocument()
  })

  it('should show paste upload method badge', () => {
    const pasteTask = { ...mockTask, upload_method: 'paste' as const }
    renderWithRouter(<TaskCard task={pasteTask} />)

    expect(screen.getByText('붙여넣기')).toBeInTheDocument()
  })

  it('should display created date', () => {
    renderWithRouter(<TaskCard task={mockTask} />)

    expect(screen.getByText(/2024/)).toBeInTheDocument()
  })

  it('should link to task detail page', () => {
    renderWithRouter(<TaskCard task={mockTask} />)

    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/tasks/task-1')
  })

  it('should show progress indicator placeholder', () => {
    renderWithRouter(<TaskCard task={mockTask} />)

    expect(screen.getByText(/진행 중/)).toBeInTheDocument()
  })

  it('should not display description if not provided', () => {
    const taskWithoutDesc = { ...mockTask, description: undefined }
    renderWithRouter(<TaskCard task={taskWithoutDesc} />)

    expect(screen.queryByText('Add JWT-based authentication')).not.toBeInTheDocument()
  })
})
