import { useState, useRef, DragEvent, ChangeEvent } from 'react'
import { Button } from '@/components/ui/button'
import { X, Upload } from 'lucide-react'
import { cn } from '@/lib/utils'

const SUPPORTED_EXTENSIONS = [
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

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

interface FileUploadProps {
  onFilesChange: (files: File[]) => void
  multiple?: boolean
}

export function FileUpload({ onFilesChange, multiple = false }: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([])
  const [error, setError] = useState<string>('')
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const validateFiles = (filesToValidate: File[]): { valid: File[]; error: string } => {
    const validFiles: File[] = []
    let errorMessage = ''

    for (const file of filesToValidate) {
      // Check file extension
      const extension = '.' + file.name.split('.').pop()?.toLowerCase()
      if (!SUPPORTED_EXTENSIONS.includes(extension)) {
        errorMessage = `지원하지 않는 파일 형식입니다: ${file.name}`
        break
      }

      // Check file size
      if (file.size > MAX_FILE_SIZE) {
        errorMessage = `파일 크기는 10MB 이하여야 합니다: ${file.name}`
        break
      }

      validFiles.push(file)
    }

    return { valid: validFiles, error: errorMessage }
  }

  const handleFiles = (newFiles: FileList | null) => {
    if (!newFiles || newFiles.length === 0) return

    const fileArray = Array.from(newFiles)
    const { valid, error: validationError } = validateFiles(fileArray)

    if (validationError) {
      setError(validationError)
      setFiles([])
      onFilesChange([])
      return
    }

    setError('')
    setFiles(valid)
    onFilesChange(valid)
  }

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
  }

  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    handleFiles(e.dataTransfer.files)
  }

  const handleRemoveFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index)
    setFiles(newFiles)
    onFilesChange(newFiles)
    setError('')
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  const totalSize = files.reduce((sum, file) => sum + file.size, 0)

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400',
          error && 'border-red-300'
        )}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleFileInputChange}
          multiple={multiple}
          accept={SUPPORTED_EXTENSIONS.join(',')}
          aria-label="파일 선택"
        />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-gray-600 mb-2">파일을 드래그하거나 클릭하여 선택하세요</p>
        <p className="text-sm text-gray-500">
          지원 형식: .py, .js, .ts, .jsx, .tsx, .html, .css, .java, .cpp, .c, .txt,
          .md
        </p>
        <p className="text-sm text-gray-500 mt-1">최대 크기: 10MB</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 text-sm text-red-800 bg-red-100 rounded-md">{error}</div>
      )}

      {/* Selected Files */}
      {files.length > 0 && (
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <h4 className="text-sm font-medium">선택된 파일</h4>
            {files.length > 1 && (
              <span className="text-sm text-gray-500">
                총 크기: {formatFileSize(totalSize)}
              </span>
            )}
          </div>
          <div className="space-y-2">
            {files.map((file, index) => {
              const extension = '.' + file.name.split('.').pop()?.toLowerCase()
              return (
                <div
                  key={`${file.name}-${index}`}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)} • {extension}
                    </p>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveFile(index)}
                    className="ml-2"
                    aria-label="제거"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
