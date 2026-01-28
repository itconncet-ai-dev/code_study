import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { FolderUpload } from '@/components/upload/FolderUpload'

describe('FolderUpload', () => {
  it('should render folder upload area', () => {
    const onFilesChange = vi.fn()
    render(<FolderUpload onFilesChange={onFilesChange} />)

    expect(screen.getByText(/폴더를 선택하세요/i)).toBeInTheDocument()
  })

  it('should handle folder selection with multiple files', async () => {
    const onFilesChange = vi.fn()
    render(<FolderUpload onFilesChange={onFilesChange} />)

    const files = [
      new File(['content1'], 'src/test1.py', { type: 'text/plain' }),
      new File(['content2'], 'src/utils/test2.js', { type: 'text/javascript' }),
    ]

    // Simulate folder structure by setting webkitRelativePath
    Object.defineProperty(files[0], 'webkitRelativePath', {
      value: 'myproject/src/test1.py',
    })
    Object.defineProperty(files[1], 'webkitRelativePath', {
      value: 'myproject/src/utils/test2.js',
    })

    const input = screen.getByLabelText(/폴더 선택/i) as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: files,
      writable: false,
    })

    fireEvent.change(input)

    expect(onFilesChange).toHaveBeenCalledWith(files)
    const folderElements = screen.getAllByText(/myproject/)
    expect(folderElements.length).toBeGreaterThan(0)
  })

  it('should display folder structure preview', async () => {
    const onFilesChange = vi.fn()
    render(<FolderUpload onFilesChange={onFilesChange} />)

    const files = [
      new File(['content1'], 'src/app.py', { type: 'text/plain' }),
      new File(['content2'], 'src/utils/helper.py', { type: 'text/plain' }),
      new File(['content3'], 'tests/test_app.py', { type: 'text/plain' }),
    ]

    Object.defineProperty(files[0], 'webkitRelativePath', {
      value: 'project/src/app.py',
    })
    Object.defineProperty(files[1], 'webkitRelativePath', {
      value: 'project/src/utils/helper.py',
    })
    Object.defineProperty(files[2], 'webkitRelativePath', {
      value: 'project/tests/test_app.py',
    })

    const input = screen.getByLabelText(/폴더 선택/i) as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: files,
      writable: false,
    })

    fireEvent.change(input)

    const srcElements = screen.getAllByText(/src/)
    expect(srcElements.length).toBeGreaterThan(0)
    const testsElements = screen.getAllByText(/tests/)
    expect(testsElements.length).toBeGreaterThan(0)
    expect(screen.getByText('app.py')).toBeInTheDocument()
  })

  it('should filter out unsupported file types', async () => {
    const onFilesChange = vi.fn()
    render(<FolderUpload onFilesChange={onFilesChange} />)

    const files = [
      new File(['content1'], 'app.py', { type: 'text/plain' }),
      new File(['content2'], 'data.exe', { type: 'application/exe' }),
      new File(['content3'], 'script.js', { type: 'text/javascript' }),
    ]

    Object.defineProperty(files[0], 'webkitRelativePath', {
      value: 'project/app.py',
    })
    Object.defineProperty(files[1], 'webkitRelativePath', {
      value: 'project/data.exe',
    })
    Object.defineProperty(files[2], 'webkitRelativePath', {
      value: 'project/script.js',
    })

    const input = screen.getByLabelText(/폴더 선택/i) as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: files,
      writable: false,
    })

    fireEvent.change(input)

    // Should only include valid files
    const validFiles = [files[0], files[2]]
    expect(onFilesChange).toHaveBeenCalledWith(validFiles)
    expect(screen.getByText(/1개 파일이 필터링되었습니다/)).toBeInTheDocument()
  })

  it('should show error when total size exceeds 10MB', async () => {
    const onFilesChange = vi.fn()
    render(<FolderUpload onFilesChange={onFilesChange} />)

    const file = new File(['content'], 'large.py', { type: 'text/plain' })
    Object.defineProperty(file, 'size', { value: 11 * 1024 * 1024 }) // 11MB
    Object.defineProperty(file, 'webkitRelativePath', {
      value: 'project/large.py',
    })

    const input = screen.getByLabelText(/폴더 선택/i) as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    })

    fireEvent.change(input)

    expect(screen.getByText(/총 크기는 10MB 이하여야 합니다/)).toBeInTheDocument()
    expect(onFilesChange).toHaveBeenCalledWith([])
  })

  it('should display total file count and size', async () => {
    const onFilesChange = vi.fn()
    render(<FolderUpload onFilesChange={onFilesChange} />)

    const file1 = new File(['content1'], 'app.py', { type: 'text/plain' })
    const file2 = new File(['content2'], 'utils.py', { type: 'text/plain' })
    Object.defineProperty(file1, 'size', { value: 1024 })
    Object.defineProperty(file2, 'size', { value: 2048 })
    Object.defineProperty(file1, 'webkitRelativePath', {
      value: 'project/app.py',
    })
    Object.defineProperty(file2, 'webkitRelativePath', {
      value: 'project/utils.py',
    })

    const input = screen.getByLabelText(/폴더 선택/i) as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: [file1, file2],
      writable: false,
    })

    fireEvent.change(input)

    expect(screen.getByText(/2개 파일/)).toBeInTheDocument()
    expect(screen.getByText(/3\.00 KB/)).toBeInTheDocument()
  })

  it('should allow clearing selected folder', async () => {
    const onFilesChange = vi.fn()
    render(<FolderUpload onFilesChange={onFilesChange} />)

    const file = new File(['content'], 'app.py', { type: 'text/plain' })
    Object.defineProperty(file, 'webkitRelativePath', {
      value: 'project/app.py',
    })

    const input = screen.getByLabelText(/폴더 선택/i) as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    })

    fireEvent.change(input)

    expect(screen.getByText('app.py')).toBeInTheDocument()

    const clearButton = screen.getByRole('button', { name: /폴더 선택 취소/i })
    fireEvent.click(clearButton)

    expect(screen.queryByText('app.py')).not.toBeInTheDocument()
    expect(onFilesChange).toHaveBeenLastCalledWith([])
  })
})
