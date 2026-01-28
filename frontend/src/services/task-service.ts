import { get, patch, del, uploadFiles } from './api-client'
import type {
  CreateTaskRequest,
  CreateTaskResponse,
  GetTaskResponse,
  TaskListResponse,
  UpdateTaskRequest,
  UpdateTaskResponse,
  GetTaskCodeResponse,
} from '@/types/task'

/**
 * Task service for handling task-related API operations.
 * Uses the API client for HTTP requests with cookie-based JWT authentication.
 */
export const taskService = {
  /**
   * Get all tasks for a project.
   * @param projectId - Project ID
   * @param includeTrashed - Include soft-deleted tasks (default: false)
   * @returns List of tasks
   */
  async getTasks(
    projectId: string,
    includeTrashed = false
  ): Promise<TaskListResponse> {
    const params = includeTrashed ? '?include_trashed=true' : ''
    return get<TaskListResponse>(`/projects/${projectId}/tasks${params}`)
  },

  /**
   * Create a new task with code upload.
   * @param projectId - Project ID
   * @param data - Task creation data (title, description, upload_method)
   * @param files - Files to upload (for file/folder upload methods)
   * @param codeContent - Code content (for paste upload method)
   * @param language - Programming language (for paste upload method)
   * @returns The created task
   */
  async createTask(
    projectId: string,
    data: CreateTaskRequest,
    files?: File[],
    codeContent?: string,
    language?: string
  ): Promise<CreateTaskResponse> {
    const formData = new FormData()

    // Add task metadata
    formData.append('title', data.title)
    if (data.description) {
      formData.append('description', data.description)
    }
    formData.append('upload_method', data.upload_method)

    // Add upload data based on method
    if (data.upload_method === 'file' || data.upload_method === 'folder') {
      if (files && files.length > 0) {
        files.forEach((file) => {
          formData.append('files', file)
        })
      }
    } else if (data.upload_method === 'paste') {
      if (codeContent) {
        formData.append('code_text', codeContent)
      }
      if (language) {
        formData.append('language', language)
      }
    }

    return uploadFiles<CreateTaskResponse>(
      `/projects/${projectId}/tasks`,
      formData
    )
  },

  /**
   * Get a single task by ID with details.
   * @param taskId - Task ID
   * @returns Task detail with uploaded code and progress
   */
  async getTask(taskId: string): Promise<GetTaskResponse> {
    return get<GetTaskResponse>(`/tasks/${taskId}`)
  },

  /**
   * Update a task.
   * @param taskId - Task ID
   * @param data - Update data (title, description)
   * @returns The updated task
   */
  async updateTask(
    taskId: string,
    data: UpdateTaskRequest
  ): Promise<UpdateTaskResponse> {
    return patch<UpdateTaskResponse>(`/tasks/${taskId}`, data)
  },

  /**
   * Soft delete a task.
   * @param taskId - Task ID
   */
  async deleteTask(taskId: string): Promise<void> {
    return del<void>(`/tasks/${taskId}`)
  },

  /**
   * Get uploaded code for a task.
   * @param taskId - Task ID
   * @returns Uploaded code with file details
   */
  async getTaskCode(taskId: string): Promise<GetTaskCodeResponse> {
    return get<GetTaskCodeResponse>(`/tasks/${taskId}/code`)
  },
}

export default taskService
