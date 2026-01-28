import { get, post, patch, del } from './api-client'
import type {
  CreateProjectRequest,
  CreateProjectResponse,
  GetProjectResponse,
  ProjectListResponse,
  UpdateProjectRequest,
  UpdateProjectResponse,
} from '@/types/project'

/**
 * Project service for handling project-related API operations.
 * Uses the API client for HTTP requests with cookie-based JWT authentication.
 */
export const projectService = {
  /**
   * Get all projects for the current user.
   * @param includeTrashed - Include soft-deleted projects (default: false)
   * @returns List of projects with task statistics
   */
  async getProjects(includeTrashed = false): Promise<ProjectListResponse> {
    const params = includeTrashed ? '?include_trashed=true' : ''
    return get<ProjectListResponse>(`/projects${params}`)
  },

  /**
   * Create a new project.
   * @param data - Project creation data (title, description)
   * @returns The created project
   */
  async createProject(data: CreateProjectRequest): Promise<CreateProjectResponse> {
    return post<CreateProjectResponse>('/projects', data)
  },

  /**
   * Get a single project by ID with task statistics.
   * @param projectId - Project ID
   * @returns Project detail with task statistics
   */
  async getProject(projectId: string): Promise<GetProjectResponse> {
    return get<GetProjectResponse>(`/projects/${projectId}`)
  },

  /**
   * Update a project.
   * @param projectId - Project ID
   * @param data - Update data (title, description)
   * @returns The updated project
   */
  async updateProject(
    projectId: string,
    data: UpdateProjectRequest
  ): Promise<UpdateProjectResponse> {
    return patch<UpdateProjectResponse>(`/projects/${projectId}`, data)
  },

  /**
   * Soft delete a project.
   * @param projectId - Project ID
   */
  async deleteProject(projectId: string): Promise<void> {
    return del<void>(`/projects/${projectId}`)
  },
}

export default projectService
