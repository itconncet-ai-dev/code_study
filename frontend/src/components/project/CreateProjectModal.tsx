import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { projectService } from '@/services/project-service'
import type { CreateProjectRequest } from '@/types/project'
import { ApiClientError } from '@/services/api-client'

interface CreateProjectModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

/**
 * CreateProjectModal component for creating new projects.
 * Displays a form with title and description fields.
 */
export function CreateProjectModal({
  open,
  onOpenChange,
  onSuccess,
}: CreateProjectModalProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [errors, setErrors] = useState<{ title?: string; description?: string; general?: string }>({})

  const queryClient = useQueryClient()

  const createProjectMutation = useMutation({
    mutationFn: (data: CreateProjectRequest) => projectService.createProject(data),
    onSuccess: () => {
      // Invalidate projects query to refetch the list
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      
      // Reset form
      setTitle('')
      setDescription('')
      setErrors({})
      
      // Close modal
      onOpenChange(false)
      
      // Call success callback
      onSuccess?.()
    },
    onError: (error: ApiClientError) => {
      if (error.isValidationError()) {
        // Handle validation errors
        const detail = error.data?.detail
        if (typeof detail === 'string') {
          setErrors({ general: detail })
        } else {
          setErrors({ general: error.message })
        }
      } else {
        setErrors({ general: error.message })
      }
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Client-side validation
    const newErrors: { title?: string; description?: string } = {}
    
    if (!title.trim()) {
      newErrors.title = '프로젝트 제목은 필수입니다'
    } else if (title.length > 255) {
      newErrors.title = '프로젝트 제목은 255자 이하여야 합니다'
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }
    
    // Clear errors and submit
    setErrors({})
    createProjectMutation.mutate({
      title: title.trim(),
      description: description.trim() || undefined,
    })
  }

  const handleCancel = () => {
    setTitle('')
    setDescription('')
    setErrors({})
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>새 프로젝트 만들기</DialogTitle>
            <DialogDescription>
              새로운 학습 프로젝트를 시작하세요. 프로젝트 제목과 설명을 입력해주세요.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            {errors.general && (
              <div className="p-3 text-sm text-red-800 bg-red-100 rounded-md">
                {errors.general}
              </div>
            )}

            <div className="grid gap-2">
              <Label htmlFor="title">
                프로젝트 제목 <span className="text-red-500">*</span>
              </Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="예: React 학습 프로젝트"
                className={errors.title ? 'border-red-500' : ''}
                disabled={createProjectMutation.isPending}
              />
              {errors.title && (
                <p className="text-sm text-red-500">{errors.title}</p>
              )}
            </div>

            <div className="grid gap-2">
              <Label htmlFor="description">프로젝트 설명 (선택)</Label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="프로젝트에 대한 간단한 설명을 입력하세요"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm resize-none"
                disabled={createProjectMutation.isPending}
              />
              {errors.description && (
                <p className="text-sm text-red-500">{errors.description}</p>
              )}
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleCancel}
              disabled={createProjectMutation.isPending}
            >
              취소
            </Button>
            <Button type="submit" disabled={createProjectMutation.isPending}>
              {createProjectMutation.isPending ? '생성 중...' : '프로젝트 생성'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default CreateProjectModal
