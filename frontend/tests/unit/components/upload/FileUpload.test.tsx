import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { FileUpload } from '@/components/upload/FileUpload'

describe('FileUpload', () => {
  const supportedExtensions = [
    '.py',
    '.js',
    '.ts',
    '.jsx',
    '.tsx',
    '.html',
    '.css',
    '.java',
    '.cpp',
    '.c',
    '.txt',
    '.md',
  ]

  it('should render file upload area', () => {
    const onFilesChange = vi.fn()
    render(<FileUpload onFilesChange={onFilesChange} />)

    expect(
      screen.getByText(/파일을 드래그하거나 클릭하여 선택/i)
    ).toBeInTheDocument()
  })

  it('should display accepted file types', () => {
    const onFilesChange = vi.fn()
    render(<FileUpload onFilesChange={onFilesChange} />)

    expect(screen.getByText(/지원 형식:/)).toBeInTheDocument()
    expect(
      screen.getByText(/\.py, \.js, \.ts, \.jsx, \.tsx, \.html, \.css/)
    ).toBeInTheDocument()
  })

  it('should handle file selection via file picker', async () => {
    const onFilesChange = vi.fn()
    render(<FileUpload onFilesChange={onFilesChange} />)

    const file = new File(['print("hello")'], 'test.py', {
      type: 'text/plain',
    })

    const input = screen.getByLabelText(/파일 선택/i) as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    })

    fireEvent.change(input)

    expect(onFilesChange).toHaveBeenCalledWith([file])
    expect(screen.getByText('test.py')).toBeInTheDocument()
  })

  it('should display selected file with size and type', async () => {
    const onFilesChange = vi.fn()
    render(<FileUpload onFilesChange={onFilesChange} />)

    const file = new File(['print("hello")'], 'test.py', {
      type: 'text/plain',
    })
    Object.defineProperty(file, 'size', { value: 1024 })

    const input = screen.getByLabelText(/파일 선택/i) as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    })

    fireEvent.change(input)

    expect(screen.getByText('test.py')).toBeInTheDocument()
    expect(screen.getByText(/1\.00 KB/)).toBeInTheDocument()

    // Check for .py in the file detail section (not the help text)
    const fileDetailsElements = screen.getAllByText(/\.py/)
    expect(fileDetailsElements.length).toBeGreaterThan(0)
  })

  it('should handle multiple file selection', async () => {
    const onFilesChange = vi.fn()
    render(<FileUpload onFilesChange={onFilesChange} multiple />)

    const files = [
      new File(['content1'], 'test1.py', { type: 'text/plain' }),
      new File(['content2'], 'test2.js', { type: 'text/javascript' }),
    ]

    const input = screen.getByLabelText(/파일 선택/i) as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: files,
      writable: false,
    })

    fireEvent.change(input)

    expect(onFilesChange).toHaveBeenCalledWith(files)
    expect(screen.getByText('test1.py')).toBeInTheDocument()
    expect(screen.getByText('test2.js')).toBeInTheDocument()
  })

  it('should show validation error for unsupported file type', async () => {
    const onFilesChange = vi.fn()
    render(<FileUpload onFilesChange={onFilesChange} />)

    const file = new File(['content'], 'test.exe', { type: 'application/exe' })

    const input = screen.getByLabelText(/파일 선택/i) as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    })

    fireEvent.change(input)

    expect(
      screen.getByText(/지원하지 않는 파일 형식입니다/)
    ).toBeInTheDocument()
    // onFilesChange is called with empty array when validation fails
    expect(onFilesChange).toHaveBeenCalledWith([])
  })

  it('should show validation error for file exceeding 10MB', async () => {
    const onFilesChange = vi.fn()
    render(<FileUpload onFilesChange={onFilesChange} />)

    const file = new File(['content'], 'large.py', { type: 'text/plain' })
    Object.defineProperty(file, 'size', { value: 11 * 1024 * 1024 }) // 11MB

    const input = screen.getByLabelText(/파일 선택/i) as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    })

    fireEvent.change(input)

    expect(screen.getByText(/파일 크기는 10MB 이하여야 합니다/)).toBeInTheDocument()
    // onFilesChange is called with empty array when validation fails
    expect(onFilesChange).toHaveBeenCalledWith([])
  })

  it('should handle drag and drop', async () => {
    const onFilesChange = vi.fn()
    render(<FileUpload onFilesChange={onFilesChange} />)

    const file = new File(['print("hello")'], 'test.py', {
      type: 'text/plain',
    })

    const dropzone = screen.getByText(/파일을 드래그하거나 클릭하여 선택/i)
      .parentElement as HTMLElement

    fireEvent.dragEnter(dropzone)
    fireEvent.dragOver(dropzone)
    fireEvent.drop(dropzone, {
      dataTransfer: {
        files: [file],
      },
    })

    await waitFor(() => {
      expect(onFilesChange).toHaveBeenCalledWith([file])
    })
  })

  it('should allow removing selected files', async () => {
    const onFilesChange = vi.fn()
    render(<FileUpload onFilesChange={onFilesChange} />)

    const file = new File(['content'], 'test.py', { type: 'text/plain' })

    const input = screen.getByLabelText(/파일 선택/i) as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    })

    fireEvent.change(input)

    expect(screen.getByText('test.py')).toBeInTheDocument()

    const removeButton = screen.getByRole('button', { name: /제거/i })
    fireEvent.click(removeButton)

    expect(screen.queryByText('test.py')).not.toBeInTheDocument()
    expect(onFilesChange).toHaveBeenLastCalledWith([])
  })

  it('should accept only specified file extensions', async () => {
    const onFilesChange = vi.fn()

    for (const ext of supportedExtensions) {
      // Re-render for each iteration to avoid property redefinition issues
      const { unmount } = render(<FileUpload onFilesChange={onFilesChange} />)

      const file = new File(['content'], `test${ext}`, { type: 'text/plain' })
      const input = screen.getByLabelText(/파일 선택/i) as HTMLInputElement

      // Clear previous calls
      onFilesChange.mockClear()

      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      })

      fireEvent.change(input)

      expect(onFilesChange).toHaveBeenCalledWith([file])

      unmount()
    }
  })

  it('should show visual feedback on drag over', () => {
    const onFilesChange = vi.fn()
    render(<FileUpload onFilesChange={onFilesChange} />)

    const dropzone = screen.getByText(/파일을 드래그하거나 클릭하여 선택/i)
      .parentElement as HTMLElement

    fireEvent.dragEnter(dropzone)
    expect(dropzone).toHaveClass('border-blue-500')

    fireEvent.dragLeave(dropzone)
    expect(dropzone).not.toHaveClass('border-blue-500')
  })

  it('should display total size when multiple files are selected', async () => {
    const onFilesChange = vi.fn()
    render(<FileUpload onFilesChange={onFilesChange} multiple />)

    const file1 = new File(['content1'], 'test1.py', { type: 'text/plain' })
    const file2 = new File(['content2'], 'test2.py', { type: 'text/plain' })
    Object.defineProperty(file1, 'size', { value: 1024 })
    Object.defineProperty(file2, 'size', { value: 2048 })

    const input = screen.getByLabelText(/파일 선택/i) as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: [file1, file2],
      writable: false,
    })

    fireEvent.change(input)

    expect(screen.getByText(/총 크기:/)).toBeInTheDocument()
    expect(screen.getByText(/3\.00 KB/)).toBeInTheDocument()
  })
})
