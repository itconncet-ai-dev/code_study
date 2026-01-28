import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { PasteCode } from '@/components/upload/PasteCode'

describe('PasteCode', () => {
  it('should render paste code area', () => {
    const onCodeChange = vi.fn()
    const onLanguageChange = vi.fn()
    render(<PasteCode onCodeChange={onCodeChange} onLanguageChange={onLanguageChange} />)

    expect(screen.getByLabelText(/코드를 입력하세요/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/프로그래밍 언어/i)).toBeInTheDocument()
  })

  it('should handle code input', () => {
    const onCodeChange = vi.fn()
    const onLanguageChange = vi.fn()
    render(<PasteCode onCodeChange={onCodeChange} onLanguageChange={onLanguageChange} />)

    const textarea = screen.getByLabelText(/코드를 입력하세요/i)
    fireEvent.change(textarea, { target: { value: 'print("hello")' } })

    expect(onCodeChange).toHaveBeenCalledWith('print("hello")')
  })

  it('should display character count', () => {
    const onCodeChange = vi.fn()
    const onLanguageChange = vi.fn()
    render(<PasteCode onCodeChange={onCodeChange} onLanguageChange={onLanguageChange} />)

    const textarea = screen.getByLabelText(/코드를 입력하세요/i)
    fireEvent.change(textarea, { target: { value: 'hello' } })

    expect(screen.getByText(/5/)).toBeInTheDocument()
    expect(screen.getByText(/문자/)).toBeInTheDocument()
  })

  it('should handle language selection', () => {
    const onCodeChange = vi.fn()
    const onLanguageChange = vi.fn()
    render(<PasteCode onCodeChange={onCodeChange} onLanguageChange={onLanguageChange} />)

    const select = screen.getByLabelText(/프로그래밍 언어/i)
    fireEvent.change(select, { target: { value: 'javascript' } })

    expect(onLanguageChange).toHaveBeenCalledWith('javascript')
  })

  it('should have all supported languages in dropdown', () => {
    const onCodeChange = vi.fn()
    const onLanguageChange = vi.fn()
    render(<PasteCode onCodeChange={onCodeChange} onLanguageChange={onLanguageChange} />)

    const languages = ['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C', 'HTML', 'CSS']

    languages.forEach((lang) => {
      expect(screen.getByText(lang)).toBeInTheDocument()
    })
  })

  it('should show validation error when code exceeds limit', () => {
    const onCodeChange = vi.fn()
    const onLanguageChange = vi.fn()
    render(<PasteCode onCodeChange={onCodeChange} onLanguageChange={onLanguageChange} />)

    const longCode = 'x'.repeat(100001) // Exceeds 100k limit
    const textarea = screen.getByLabelText(/코드를 입력하세요/i)
    fireEvent.change(textarea, { target: { value: longCode } })

    expect(screen.getByText(/코드는 100,000자 이하여야 합니다/)).toBeInTheDocument()
  })

  it('should clear code when clear button is clicked', () => {
    const onCodeChange = vi.fn()
    const onLanguageChange = vi.fn()
    render(<PasteCode onCodeChange={onCodeChange} onLanguageChange={onLanguageChange} />)

    const textarea = screen.getByLabelText(/코드를 입력하세요/i)
    fireEvent.change(textarea, { target: { value: 'print("hello")' } })

    const clearButton = screen.getByRole('button', { name: /초기화/i })
    fireEvent.click(clearButton)

    expect(onCodeChange).toHaveBeenLastCalledWith('')
  })
})
