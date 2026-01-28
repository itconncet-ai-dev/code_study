import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Code } from 'lucide-react'

const MAX_CODE_LENGTH = 100000

const SUPPORTED_LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
  { value: 'c', label: 'C' },
  { value: 'html', label: 'HTML' },
  { value: 'css', label: 'CSS' },
]

interface PasteCodeProps {
  onCodeChange: (code: string) => void
  onLanguageChange: (language: string) => void
}

export function PasteCode({ onCodeChange, onLanguageChange }: PasteCodeProps) {
  const [code, setCode] = useState<string>('')
  const [language, setLanguage] = useState<string>('python')
  const [error, setError] = useState<string>('')

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newCode = e.target.value

    if (newCode.length > MAX_CODE_LENGTH) {
      setError(`코드는 100,000자 이하여야 합니다`)
      return
    }

    setError('')
    setCode(newCode)
    onCodeChange(newCode)
  }

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLanguage = e.target.value
    setLanguage(newLanguage)
    onLanguageChange(newLanguage)
  }

  const handleClear = () => {
    setCode('')
    setError('')
    onCodeChange('')
  }

  return (
    <div className="space-y-4">
      {/* Language Selector */}
      <div>
        <Label htmlFor="language-select">프로그래밍 언어</Label>
        <select
          id="language-select"
          value={language}
          onChange={handleLanguageChange}
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm mt-1"
          aria-label="프로그래밍 언어"
        >
          {SUPPORTED_LANGUAGES.map((lang) => (
            <option key={lang.value} value={lang.value}>
              {lang.label}
            </option>
          ))}
        </select>
      </div>

      {/* Code Textarea */}
      <div>
        <div className="flex justify-between items-center mb-1">
          <Label htmlFor="code-textarea">코드를 입력하세요</Label>
          <span className="text-sm text-gray-500">
            {code.length.toLocaleString()} 문자
          </span>
        </div>
        <textarea
          id="code-textarea"
          value={code}
          onChange={handleCodeChange}
          className="flex min-h-[300px] w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm resize-none font-mono"
          placeholder="여기에 코드를 붙여넣으세요..."
          aria-label="코드를 입력하세요"
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 text-sm text-red-800 bg-red-100 rounded-md">{error}</div>
      )}

      {/* Info and Actions */}
      <div className="flex justify-between items-center">
        <div className="flex items-center text-sm text-gray-500">
          <Code className="h-4 w-4 mr-1" />
          <span>최대 100,000자</span>
        </div>
        {code && (
          <Button type="button" variant="outline" size="sm" onClick={handleClear}>
            초기화
          </Button>
        )}
      </div>
    </div>
  )
}
