import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { projectService } from '@/services/project-service'
import { taskService } from '@/services/task-service'
import { ApiClientError } from '@/services/api-client'
import { TaskCard } from '@/components/task/TaskCard'
import { CreateTaskModal } from '@/components/task/CreateTaskModal'

export default function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [isEditing, setIsEditing] = useState(false)
  const [editTitle, setEditTitle] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [editErrors, setEditErrors] = useState<{ title?: string; general?: string }>({})
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

  // Fetch project details
  const {
    data: project,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['projects', projectId],
    queryFn: () => projectService.getProject(projectId!),
    enabled: !!projectId,
  })

  // Fetch tasks for this project
  const {
    data: tasksData,
    isLoading: isLoadingTasks,
  } = useQuery({
    queryKey: ['projects', projectId, 'tasks'],
    queryFn: () => taskService.getTasks(projectId!),
    enabled: !!projectId,
  })

  // Update project mutation
  const updateMutation = useMutation({
    mutationFn: (data: { title?: string; description?: string }) =>
      projectService.updateProject(projectId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] })
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setIsEditing(false)
      setEditErrors({})
    },
    onError: (error: ApiClientError) => {
      if (error.isValidationError()) {
        setEditErrors({ general: error.message })
      } else {
        setEditErrors({ general: error.message })
      }
    },
  })

  // Delete project mutation
  const deleteMutation = useMutation({
    mutationFn: () => projectService.deleteProject(projectId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      navigate('/')
    },
    onError: (error: ApiClientError) => {
      alert(`프로젝트 삭제 실패: ${error.message}`)
    },
  })

  const handleEditStart = () => {
    if (project) {
      setEditTitle(project.title)
      setEditDescription(project.description || '')
      setIsEditing(true)
      setEditErrors({})
    }
  }

  const handleEditCancel = () => {
    setIsEditing(false)
    setEditTitle('')
    setEditDescription('')
    setEditErrors({})
  }

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validation
    const newErrors: { title?: string } = {}
    if (!editTitle.trim()) {
      newErrors.title = '프로젝트 제목은 필수입니다'
    } else if (editTitle.length > 255) {
      newErrors.title = '프로젝트 제목은 255자 이하여야 합니다'
    }

    if (Object.keys(newErrors).length > 0) {
      setEditErrors(newErrors)
      return
    }

    setEditErrors({})
    updateMutation.mutate({
      title: editTitle.trim(),
      description: editDescription.trim() || undefined,
    })
  }

  const handleDelete = () => {
    if (window.confirm('정말로 이 프로젝트를 삭제하시겠습니까?')) {
      deleteMutation.mutate()
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="text-gray-500">프로젝트 정보를 불러오는 중...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">프로젝트를 불러오는데 실패했습니다.</p>
          <Link to="/" className="text-blue-600 hover:underline mt-2 inline-block">
            대시보드로 돌아가기
          </Link>
        </div>
      </div>
    )
  }

  if (!project) {
    return null
  }

  const formattedDate = new Date(project.created_at).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  const lastActivityDate = new Date(project.last_activity_at).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <div className="mb-4">
          <Link to="/" className="text-blue-600 hover:underline">
            ← 대시보드로 돌아가기
          </Link>
        </div>

        {/* Project Info Card */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                {!isEditing ? (
                  <>
                    <CardTitle className="text-2xl">{project.title}</CardTitle>
                    {project.description && (
                      <CardDescription className="mt-2">
                        {project.description}
                      </CardDescription>
                    )}
                  </>
                ) : (
                  <form onSubmit={handleEditSubmit} className="space-y-4">
                    {editErrors.general && (
                      <div className="p-3 text-sm text-red-800 bg-red-100 rounded-md">
                        {editErrors.general}
                      </div>
                    )}
                    <div>
                      <Label htmlFor="edit-title">프로젝트 제목</Label>
                      <Input
                        id="edit-title"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        className={editErrors.title ? 'border-red-500' : ''}
                        disabled={updateMutation.isPending}
                      />
                      {editErrors.title && (
                        <p className="text-sm text-red-500 mt-1">{editErrors.title}</p>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="edit-description">프로젝트 설명</Label>
                      <textarea
                        id="edit-description"
                        value={editDescription}
                        onChange={(e) => setEditDescription(e.target.value)}
                        className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm resize-none"
                        disabled={updateMutation.isPending}
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button
                        type="submit"
                        disabled={updateMutation.isPending}
                      >
                        {updateMutation.isPending ? '저장 중...' : '저장'}
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={handleEditCancel}
                        disabled={updateMutation.isPending}
                      >
                        취소
                      </Button>
                    </div>
                  </form>
                )}
              </div>
              {!isEditing && (
                <div className="flex gap-2 ml-4">
                  <Button variant="outline" onClick={handleEditStart}>
                    수정
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={handleDelete}
                    disabled={deleteMutation.isPending}
                  >
                    {deleteMutation.isPending ? '삭제 중...' : '삭제'}
                  </Button>
                </div>
              )}
            </div>
          </CardHeader>

          {!isEditing && (
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">생성일:</span>
                  <span>{formattedDate}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">최근 활동:</span>
                  <span>{lastActivityDate}</span>
                </div>
                <div className="pt-4 border-t">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-muted-foreground">진행률</span>
                    <span className="font-semibold">{project.progress_percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${project.progress_percentage}%` }}
                    />
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {project.completed_task_count} / {project.task_count} 작업 완료
                  </div>
                </div>
              </div>
            </CardContent>
          )}
        </Card>

        {/* Task Timeline */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>작업 타임라인</CardTitle>
                <CardDescription>
                  {tasksData?.tasks.length || 0}개의 작업
                </CardDescription>
              </div>
              <Button onClick={() => setIsCreateModalOpen(true)}>
                새 작업
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {isLoadingTasks ? (
              <div className="text-center py-8 text-gray-500">
                작업 목록을 불러오는 중...
              </div>
            ) : tasksData && tasksData.tasks.length > 0 ? (
              <div className="space-y-4">
                {tasksData.tasks.map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                아직 작업이 없습니다. 새 작업을 만들어보세요!
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Create Task Modal */}
      <CreateTaskModal
        projectId={projectId!}
        open={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  )
}
