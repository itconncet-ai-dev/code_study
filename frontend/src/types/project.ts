/**
 * Project entity matching backend Project schema.
 */
export interface Project {
  id: string
  user_id: string
  title: string
  description: string | null
  is_deleted: boolean
  created_at: string
  updated_at: string
  last_activity_at: string
}

/**
 * Project detail with task statistics.
 */
export interface ProjectDetail extends Project {
  task_count: number
  completed_task_count: number
  progress_percentage: number
}

/**
 * Request payload for creating a new project.
 */
export interface CreateProjectRequest {
  title: string
  description?: string
}

/**
 * Request payload for updating a project.
 */
export interface UpdateProjectRequest {
  title?: string
  description?: string
}

/**
 * Response from GET /api/v1/projects endpoint.
 */
export interface ProjectListResponse {
  projects: ProjectDetail[]
}

/**
 * Response from POST /api/v1/projects endpoint.
 */
export type CreateProjectResponse = Project

/**
 * Response from GET /api/v1/projects/{project_id} endpoint.
 */
export type GetProjectResponse = ProjectDetail

/**
 * Response from PATCH /api/v1/projects/{project_id} endpoint.
 */
export type UpdateProjectResponse = Project
