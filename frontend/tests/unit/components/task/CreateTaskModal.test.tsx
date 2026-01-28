import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { CreateTaskModal } from '@/components/task/CreateTaskModal'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
})

const renderWithQuery = (ui: React.ReactElement) => {
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>)
}

describe('CreateTaskModal', () => {
  it('should render modal when open', () => {
    const onClose = vi.fn()
    renderWithQuery(<CreateTaskModal projectId="project-1" open={true} onClose={onClose} />)

    expect(screen.getByText('새 작업 만들기')).toBeInTheDocument()
  })

  it('should not render when closed', () => {
    const onClose = vi.fn()
    renderWithQuery(<CreateTaskModal projectId="project-1" open={false} onClose={onClose} />)

    expect(screen.queryByText('새 작업 만들기')).not.toBeInTheDocument()
  })

  it('should show title input with validation', () => {
    const onClose = vi.fn()
    renderWithQuery(<CreateTaskModal projectId="project-1" open={true} onClose={onClose} />)

    const titleInput = screen.getByLabelText(/작업 제목/i)
    expect(titleInput).toBeInTheDocument()
  })

  it('should show description textarea', () => {
    const onClose = vi.fn()
    renderWithQuery(<CreateTaskModal projectId="project-1" open={true} onClose={onClose} />)

    const descInput = screen.getByLabelText(/작업 설명/i)
    expect(descInput).toBeInTheDocument()
  })

  it('should display upload method tabs', () => {
    const onClose = vi.fn()
    renderWithQuery(<CreateTaskModal projectId="project-1" open={true} onClose={onClose} />)

    expect(screen.getByRole('tab', { name: /파일 업로드/i })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: /폴더 업로드/i })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: /코드 붙여넣기/i })).toBeInTheDocument()
  })

  it('should switch between upload methods', () => {
    const onClose = vi.fn()
    renderWithQuery(<CreateTaskModal projectId="project-1" open={true} onClose={onClose} />)

    const folderTab = screen.getByRole('tab', { name: /폴더 업로드/i })
    fireEvent.click(folderTab)

    expect(screen.getByText(/폴더를 선택하세요/i)).toBeInTheDocument()
  })

  it('should validate title minimum length', async () => {
    const onClose = vi.fn()
    renderWithQuery(<CreateTaskModal projectId="project-1" open={true} onClose={onClose} />)

    const titleInput = screen.getByLabelText(/작업 제목/i)
    fireEvent.change(titleInput, { target: { value: 'abc' } })

    const submitButton = screen.getByRole('button', { name: /만들기/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/최소 5자 이상 입력해주세요/i)).toBeInTheDocument()
    })
  })

  it('should display character count for description', async () => {
    const onClose = vi.fn()
    renderWithQuery(<CreateTaskModal projectId="project-1" open={true} onClose={onClose} />)

    const descInput = screen.getByLabelText(/작업 설명/i)
    fireEvent.change(descInput, { target: { value: 'Test description' } })

    await waitFor(() => {
      expect(screen.getByText(/\/ 500/)).toBeInTheDocument()
    })
  })

  it('should show submit button with loading state', () => {
    const onClose = vi.fn()
    renderWithQuery(<CreateTaskModal projectId="project-1" open={true} onClose={onClose} />)

    const submitButton = screen.getByRole('button', { name: /만들기/i })
    expect(submitButton).toBeInTheDocument()
    expect(submitButton).not.toBeDisabled()
  })

  it('should close modal on cancel', () => {
    const onClose = vi.fn()
    renderWithQuery(<CreateTaskModal projectId="project-1" open={true} onClose={onClose} />)

    const cancelButton = screen.getByRole('button', { name: /취소/i })
    fireEvent.click(cancelButton)

    expect(onClose).toHaveBeenCalled()
  })
})
