import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { FileUpload } from '@/components/upload/FileUpload'
import { FolderUpload } from '@/components/upload/FolderUpload'
import { PasteCode } from '@/components/upload/PasteCode'
import { taskService } from '@/services/task-service'
import { ApiClientError } from '@/services/api-client'
import { cn } from '@/lib/utils'

interface CreateTaskModalProps {
  projectId: string
  open: boolean
  onClose: () => void
}

type UploadMethod = 'file' | 'folder' | 'paste'

export function CreateTaskModal({ projectId, open, onClose }: CreateTaskModalProps) {
  const queryClient = useQueryClient()

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [uploadMethod, setUploadMethod] = useState<UploadMethod>('file')
  const [files, setFiles] = useState<File[]>([])
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('python')
  const [errors, setErrors] = useState<{ title?: string; description?: string; general?: string }>(
    {}
  )

  const createMutation = useMutation({
    mutationFn: () => {
      return taskService.createTask(
        projectId,
        {
          title: title.trim(),
          description: description.trim() || undefined,
          upload_method: uploadMethod,
        },
        files.length > 0 ? files : undefined,
        code || undefined,
        language
      )
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'tasks'] })
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] })
      handleClose()
    },
    onError: (error: ApiClientError) => {
      setErrors({ general: error.message })
    },
  })

  const handleClose = () => {
    setTitle('')
    setDescription('')
    setUploadMethod('file')
    setFiles([])
    setCode('')
    setLanguage('python')
    setErrors({})
    onClose()
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const newErrors: { title?: string; description?: string } = {}

    if (!title.trim()) {
      newErrors.title = '작업 제목은 필수입니다'
    } else if (title.trim().length < 5) {
      newErrors.title = '최소 5자 이상 입력해주세요'
    }

    if (description.length > 500) {
      newErrors.description = '500자 이하로 입력해주세요'
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    setErrors({})
    createMutation.mutate()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>새 작업 만들기</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {errors.general && (
            <div className="p-3 text-sm text-red-800 bg-red-100 rounded-md">{errors.general}</div>
          )}

          <div>
            <Label htmlFor="task-title">작업 제목 *</Label>
            <Input
              id="task-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className={errors.title ? 'border-red-500' : ''}
              disabled={createMutation.isPending}
              placeholder="작업 제목을 입력하세요 (최소 5자)"
            />
            {errors.title && <p className="text-sm text-red-500 mt-1">{errors.title}</p>}
          </div>

          <div>
            <Label htmlFor="task-description">작업 설명 (선택)</Label>
            <textarea
              id="task-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className={cn(
                'flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm resize-none',
                errors.description && 'border-red-500'
              )}
              disabled={createMutation.isPending}
              placeholder="작업에 대한 설명을 입력하세요 (최대 500자)"
              maxLength={500}
            />
            <div className="flex justify-between mt-1">
              {errors.description && <p className="text-sm text-red-500">{errors.description}</p>}
              <p className="text-sm text-gray-500 ml-auto">{description.length} / 500</p>
            </div>
          </div>

          <div>
            <Label>코드 업로드 방법</Label>
            <div className="flex gap-2 mt-2" role="tablist">
              <button
                type="button"
                role="tab"
                aria-selected={uploadMethod === 'file'}
                onClick={() => setUploadMethod('file')}
                className={cn(
                  'px-4 py-2 rounded-md text-sm font-medium transition-colors',
                  uploadMethod === 'file'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                )}
              >
                파일 업로드
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={uploadMethod === 'folder'}
                onClick={() => setUploadMethod('folder')}
                className={cn(
                  'px-4 py-2 rounded-md text-sm font-medium transition-colors',
                  uploadMethod === 'folder'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                )}
              >
                폴더 업로드
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={uploadMethod === 'paste'}
                onClick={() => setUploadMethod('paste')}
                className={cn(
                  'px-4 py-2 rounded-md text-sm font-medium transition-colors',
                  uploadMethod === 'paste'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                )}
              >
                코드 붙여넣기
              </button>
            </div>
          </div>

          <div>
            {uploadMethod === 'file' && <FileUpload onFilesChange={setFiles} />}
            {uploadMethod === 'folder' && <FolderUpload onFilesChange={setFiles} />}
            {uploadMethod === 'paste' && (
              <PasteCode onCodeChange={setCode} onLanguageChange={setLanguage} />
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={createMutation.isPending}
            >
              취소
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? '만드는 중...' : '만들기'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
