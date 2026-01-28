import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileText, Folder, Code } from 'lucide-react'
import type { Task } from '@/types/task'

interface TaskCardProps {
  task: Task
}

const UPLOAD_METHOD_LABELS = {
  file: '파일',
  folder: '폴더',
  paste: '붙여넣기',
}

const UPLOAD_METHOD_ICONS = {
  file: FileText,
  folder: Folder,
  paste: Code,
}

export function TaskCard({ task }: TaskCardProps) {
  const Icon = UPLOAD_METHOD_ICONS[task.upload_method]

  const formattedDate = new Date(task.created_at).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <Link to={`/tasks/${task.id}`} className="block hover:shadow-md transition-shadow">
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm font-medium text-gray-500">작업 #{task.task_number}</span>
                <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                  <Icon className="h-3 w-3" />
                  {UPLOAD_METHOD_LABELS[task.upload_method]}
                </span>
              </div>
              <CardTitle className="text-lg">{task.title}</CardTitle>
              {task.description && <p className="text-sm text-gray-600 mt-2">{task.description}</p>}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-500">{formattedDate}</span>
            <span className="text-blue-600 font-medium">진행 중</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
