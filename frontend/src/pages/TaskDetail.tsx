import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { taskService } from '@/services/task-service'
import { documentService } from '@/services/document-service'
import { DocumentViewer } from '@/components/document/DocumentViewer'
import { DocumentLoading } from '@/components/document/DocumentLoading'
import { cn } from '@/lib/utils'
import type { ChapterNumber } from '@/types/document'

type TabType = 'document' | 'practice' | 'qa'

export default function TaskDetail() {
  const { taskId: rawTaskId } = useParams<{ taskId: string }>()
  const taskId = rawTaskId ?? ''
  const [activeTab, setActiveTab] = useState<TabType>('document')
  const [completedChapters, setCompletedChapters] = useState<ChapterNumber[]>([])

  // Fetch task details
  const {
    data: task,
    isLoading: isLoadingTask,
    error: taskError,
  } = useQuery({
    queryKey: ['tasks', taskId],
    queryFn: () => taskService.getTask(taskId),
    enabled: !!taskId,
  })

  // Fetch task code
  const { data: codeData, isLoading: isLoadingCode } = useQuery({
    queryKey: ['tasks', taskId, 'code'],
    queryFn: () => taskService.getTaskCode(taskId),
    enabled: !!taskId && activeTab === 'document',
  })

  // Fetch or poll document status
  const { data: documentStatus, isLoading: isLoadingDocumentStatus } = useQuery({
    queryKey: ['tasks', taskId, 'document', 'status'],
    queryFn: () => documentService.getDocumentStatus(taskId),
    enabled: !!taskId && activeTab === 'document',
    refetchInterval: (query) => {
      // Poll every 5 seconds if document is pending or in progress
      const data = query.state.data
      if (data?.status === 'pending' || data?.status === 'in_progress') {
        return 5000
      }
      return false
    },
  })

  // Fetch document when status is completed
  const { data: document } = useQuery({
    queryKey: ['tasks', taskId, 'document'],
    queryFn: () => documentService.getDocument(taskId),
    enabled: !!taskId && documentStatus?.status === 'completed',
  })

  // Handle chapter completion
  const handleChapterComplete = (chapter: ChapterNumber, completed: boolean) => {
    setCompletedChapters((prev) => {
      if (completed && !prev.includes(chapter)) {
        return [...prev, chapter]
      } else if (!completed) {
        return prev.filter((ch) => ch !== chapter)
      }
      return prev
    })
    // TODO: Send to backend to persist progress (T155)
  }

  const isLoading = isLoadingTask
  const error = taskError

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="text-gray-500">작업 정보를 불러오는 중...</div>
      </div>
    )
  }

  if (error || !task) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">작업을 불러오는데 실패했습니다.</p>
          {task?.project_id && (
            <Link
              to={`/projects/${task.project_id}`}
              className="text-blue-600 hover:underline mt-2 inline-block"
            >
              프로젝트로 돌아가기
            </Link>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <div className="mb-4">
          <Link to={`/projects/${task.project_id}`} className="text-blue-600 hover:underline">
            ← 프로젝트로 돌아가기
          </Link>
        </div>

        {/* Task Header */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm font-medium text-gray-500">
                    작업 #{task.task_number}
                  </span>
                </div>
                <CardTitle className="text-2xl">{task.title}</CardTitle>
                {task.description && <p className="text-gray-600 mt-2">{task.description}</p>}
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex gap-8" role="tablist">
              <button
                role="tab"
                aria-selected={activeTab === 'document'}
                onClick={() => setActiveTab('document')}
                className={cn(
                  'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                  activeTab === 'document'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                )}
              >
                문서
              </button>
              <button
                role="tab"
                aria-selected={activeTab === 'practice'}
                onClick={() => setActiveTab('practice')}
                className={cn(
                  'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                  activeTab === 'practice'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                )}
              >
                실습
              </button>
              <button
                role="tab"
                aria-selected={activeTab === 'qa'}
                onClick={() => setActiveTab('qa')}
                className={cn(
                  'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                  activeTab === 'qa'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                )}
              >
                Q&A
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'document' && (
          <div
            className="bg-white rounded-lg shadow-sm border border-gray-200"
            style={{ height: 'calc(100vh - 280px)' }}
          >
            {isLoadingDocumentStatus || isLoadingCode ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-gray-500">상태 확인 중...</div>
              </div>
            ) : documentStatus?.status === 'failed' ? (
              <DocumentLoading status="failed" error={documentStatus.error} />
            ) : documentStatus?.status === 'pending' || documentStatus?.status === 'in_progress' ? (
              <DocumentLoading
                status={documentStatus.status}
                progress={documentStatus.progress}
                estimatedTimeRemaining={documentStatus.estimated_time_remaining}
              />
            ) : document && codeData ? (
              <DocumentViewer
                document={document}
                code={codeData.content || ''}
                language={codeData.detected_language || 'plaintext'}
                onChapterComplete={handleChapterComplete}
                completedChapters={completedChapters}
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-gray-500">문서를 불러올 수 없습니다</div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'practice' && (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-12 text-gray-500">
                <p className="text-lg font-medium mb-2">실습 기능</p>
                <p className="text-sm">실습 환경은 문서 생성 후 이용 가능합니다.</p>
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === 'qa' && (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-12 text-gray-500">
                <p className="text-lg font-medium mb-2">질문하기</p>
                <p className="text-sm">AI에게 코드에 대한 질문을 할 수 있습니다.</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
