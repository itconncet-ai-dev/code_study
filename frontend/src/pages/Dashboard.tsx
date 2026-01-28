import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import useAuth from '../hooks/useAuth'
import { Button } from '@/components/ui/button'
import { ProjectCard } from '@/components/project/ProjectCard'
import { CreateProjectModal } from '@/components/project/CreateProjectModal'
import { projectService } from '@/services/project-service'

export default function Dashboard() {
  const { user, logout, isLogoutLoading } = useAuth()
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

  // Fetch projects
  const {
    data: projectsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectService.getProjects(false),
  })

  const handleLogout = async () => {
    try {
      await logout()
      window.location.href = '/login'
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const projects = projectsData?.projects ?? []
  const hasProjects = projects.length > 0

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">내 프로젝트</h1>
          <div className="flex items-center gap-4">
            {user && (
              <span className="text-sm text-gray-600">{user.email}</span>
            )}
            <Button
              variant="outline"
              onClick={handleLogout}
              disabled={isLogoutLoading}
            >
              {isLogoutLoading ? '로그아웃 중...' : '로그아웃'}
            </Button>
          </div>
        </div>

        {/* Create Project Button */}
        <div className="mb-6">
          <Button onClick={() => setIsCreateModalOpen(true)}>
            새 프로젝트 만들기
          </Button>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <div className="text-gray-500">프로젝트 목록을 불러오는 중...</div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">
              프로젝트 목록을 불러오는데 실패했습니다. 다시 시도해주세요.
            </p>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && !hasProjects && (
          <div className="flex flex-col items-center justify-center py-12 px-4 bg-white rounded-lg border border-gray-200">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                아직 프로젝트가 없습니다
              </h3>
              <p className="text-gray-600 mb-6">
                첫 번째 학습 프로젝트를 만들어 시작하세요
              </p>
              <Button onClick={() => setIsCreateModalOpen(true)}>
                프로젝트 만들기
              </Button>
            </div>
          </div>
        )}

        {/* Project Grid */}
        {!isLoading && !error && hasProjects && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}

        {/* Create Project Modal */}
        <CreateProjectModal
          open={isCreateModalOpen}
          onOpenChange={setIsCreateModalOpen}
        />
      </div>
    </div>
  )
}
