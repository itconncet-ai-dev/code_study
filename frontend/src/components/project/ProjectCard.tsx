import { Link } from 'react-router-dom'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import type { ProjectDetail } from '@/types/project'

interface ProjectCardProps {
  project: ProjectDetail
}

/**
 * ProjectCard component displays a single project in a card layout.
 * Shows project title, description, dates, task progress, and deletion status.
 */
export function ProjectCard({ project }: ProjectCardProps) {
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
    <Link to={`/projects/${project.id}`} className="block">
      <Card className="hover:shadow-lg transition-shadow cursor-pointer">
        <CardHeader>
          <div className="flex items-start justify-between">
            <CardTitle className="text-xl">{project.title}</CardTitle>
            {project.is_deleted && (
              <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                삭제됨
              </span>
            )}
            {!project.is_deleted && (
              <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                활성
              </span>
            )}
          </div>
          {project.description && (
            <CardDescription className="mt-2 line-clamp-2">{project.description}</CardDescription>
          )}
        </CardHeader>

        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>생성일:</span>
              <span>{formattedDate}</span>
            </div>
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>최근 활동:</span>
              <span>{lastActivityDate}</span>
            </div>
          </div>
        </CardContent>

        <CardFooter className="flex flex-col items-start space-y-2">
          <div className="w-full flex justify-between text-sm">
            <span className="text-muted-foreground">진행률</span>
            <span className="font-semibold">{project.progress_percentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${project.progress_percentage}%` }}
            />
          </div>
          <div className="text-sm text-muted-foreground">
            {project.completed_task_count} / {project.task_count} 작업 완료
          </div>
        </CardFooter>
      </Card>
    </Link>
  )
}

export default ProjectCard
