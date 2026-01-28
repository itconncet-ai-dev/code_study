import { useState, useRef, ChangeEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Folder, X } from 'lucide-react'
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

const MAX_TOTAL_SIZE = 10 * 1024 * 1024 // 10MB

interface FolderUploadProps {
  onFilesChange: (files: File[]) => void
}

interface FileNode {
  name: string
  path: string
  isDirectory: boolean
  children?: FileNode[]
  file?: File
}

export function FolderUpload({ onFilesChange }: FolderUploadProps) {
  const [files, setFiles] = useState<File[]>([])
  const [error, setError] = useState<string>('')
  const [filteredCount, setFilteredCount] = useState<number>(0)
  const [folderName, setFolderName] = useState<string>('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const isValidFile = (file: File): boolean => {
    const extension = '.' + file.name.split('.').pop()?.toLowerCase()
    return SUPPORTED_EXTENSIONS.includes(extension)
  }

  const buildFileTree = (filesList: File[]): FileNode | null => {
    if (filesList.length === 0) return null

    const root: FileNode = {
      name: '',
      path: '',
      isDirectory: true,
      children: [],
    }

    filesList.forEach((file) => {
      const path = (file as File & { webkitRelativePath?: string })
        .webkitRelativePath || file.name
      const parts = path.split('/')

      let current = root
      for (let i = 0; i < parts.length; i++) {
        const part = parts[i]
        const isFile = i === parts.length - 1

        if (i === 0 && !root.name) {
          root.name = part
          root.path = part
          continue
        }

        let child = current.children?.find((c) => c.name === part)
        if (!child) {
          child = {
            name: part,
            path: parts.slice(0, i + 1).join('/'),
            isDirectory: !isFile,
            children: isFile ? undefined : [],
            file: isFile ? file : undefined,
          }
          current.children?.push(child)
        }

        if (!isFile) {
          current = child
        }
      }
    })

    return root
  }

  const handleFolderSelection = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files
    if (!selectedFiles || selectedFiles.length === 0) return

    const fileArray = Array.from(selectedFiles)

    // Filter valid files
    const validFiles = fileArray.filter(isValidFile)
    const filtered = fileArray.length - validFiles.length

    setFilteredCount(filtered)

    if (validFiles.length === 0) {
      setError('선택한 폴더에 지원되는 파일이 없습니다')
      setFiles([])
      setFolderName('')
      onFilesChange([])
      return
    }

    // Check total size
    const totalSize = validFiles.reduce((sum, file) => sum + file.size, 0)
    if (totalSize > MAX_TOTAL_SIZE) {
      setError('총 크기는 10MB 이하여야 합니다')
      setFiles([])
      setFolderName('')
      onFilesChange([])
      return
    }

    // Get folder name from first file
    const firstFile = validFiles[0] as File & { webkitRelativePath?: string }
    const folderPath = firstFile.webkitRelativePath || firstFile.name
    const folder = folderPath.split('/')[0]

    setError('')
    setFiles(validFiles)
    setFolderName(folder)
    onFilesChange(validFiles)
  }

  const handleClear = () => {
    setFiles([])
    setError('')
    setFilteredCount(0)
    setFolderName('')
    onFilesChange([])
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  const renderFileTree = (node: FileNode, level = 0): JSX.Element[] => {
    const elements: JSX.Element[] = []

    if (node.isDirectory && node.children) {
      if (level > 0) {
        elements.push(
          <div
            key={`dir-${node.path}`}
            className="flex items-center py-1"
            style={{ paddingLeft: `${level * 16}px` }}
          >
            <Folder className="h-4 w-4 mr-2 text-blue-500" />
            <span className="text-sm font-medium">{node.name}</span>
          </div>
        )
      }

      node.children.forEach((child, index) => {
        elements.push(...renderFileTree(child, level + 1).map((el, i) => ({
          ...el,
          key: `${el.key}-${index}-${i}`
        })))
      })
    } else if (node.file) {
      elements.push(
        <div
          key={`file-${node.path}`}
          className="flex items-center py-1"
          style={{ paddingLeft: `${level * 16}px` }}
        >
          <span className="text-sm text-gray-700">{node.name}</span>
          <span className="text-xs text-gray-500 ml-2">
            ({formatFileSize(node.file.size)})
          </span>
        </div>
      )
    }

    return elements
  }

  const totalSize = files.reduce((sum, file) => sum + file.size, 0)
  const fileTree = buildFileTree(files)

  return (
    <div className="space-y-4">
      {/* Folder Selection Area */}
      <div
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          files.length > 0
            ? 'border-gray-300'
            : 'border-gray-300 hover:border-gray-400',
          error && 'border-red-300'
        )}
        onClick={files.length === 0 ? handleClick : undefined}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleFolderSelection}
          {...({ webkitdirectory: '', directory: '' } as any)}
          aria-label="폴더 선택"
        />
        <Folder className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-gray-600 mb-2">폴더를 선택하세요</p>
        <p className="text-sm text-gray-500">
          폴더 구조가 그대로 유지됩니다
        </p>
        <p className="text-sm text-gray-500 mt-1">
          지원 형식: .py, .js, .ts, .jsx, .tsx, .html, .css, .java, .cpp, .c, .txt, .md
        </p>
        <p className="text-sm text-gray-500 mt-1">최대 크기: 10MB</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 text-sm text-red-800 bg-red-100 rounded-md">{error}</div>
      )}

      {/* Filtered Files Warning */}
      {filteredCount > 0 && (
        <div className="p-3 text-sm text-yellow-800 bg-yellow-100 rounded-md">
          {filteredCount}개 파일이 필터링되었습니다 (지원하지 않는 형식)
        </div>
      )}

      {/* Folder Preview */}
      {files.length > 0 && fileTree && (
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <h4 className="text-sm font-medium">
              {folderName} ({files.length}개 파일, {formatFileSize(totalSize)})
            </h4>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleClear}
              aria-label="폴더 선택 취소"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          <div className="bg-gray-50 rounded-md p-3 max-h-96 overflow-y-auto">
            <div className="flex items-center mb-2">
              <Folder className="h-4 w-4 mr-2 text-blue-500" />
              <span className="text-sm font-medium">{folderName}</span>
            </div>
            {renderFileTree(fileTree, 1)}
          </div>
        </div>
      )}
    </div>
  )
}
