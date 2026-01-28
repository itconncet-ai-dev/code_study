/**
 * Task entity matching backend Task schema.
 */
export interface Task {
  id: string
  project_id: string
  task_number: number
  title: string
  description?: string
  upload_method: 'file' | 'folder' | 'paste'
  created_at: string
  updated_at: string
  deletion_status: 'active' | 'trashed'
}

/**
 * Task detail with uploaded code and progress information.
 */
export interface TaskDetail extends Task {
  uploaded_code?: UploadedCode
  document_status?: 'pending' | 'in_progress' | 'completed' | 'failed'
  progress?: TaskProgress
}

/**
 * Uploaded code information.
 */
export interface UploadedCode {
  id: string
  detected_language?: string
  complexity_level?: 'beginner' | 'intermediate' | 'advanced'
  total_lines?: number
  total_files?: number
  upload_size_bytes?: number
  code_files: CodeFile[]
}

/**
 * Individual code file in uploaded code.
 */
export interface CodeFile {
  id: string
  file_name: string
  file_path?: string
  file_extension?: string
  file_size_bytes?: number
  content?: string
}

/**
 * Task progress information (placeholder for future implementation).
 */
export interface TaskProgress {
  document_progress?: number
  practice_progress?: number
  qa_progress?: number
}

/**
 * Request payload for creating a new task.
 */
export interface CreateTaskRequest {
  title: string
  description?: string
  upload_method: 'file' | 'folder' | 'paste'
}

/**
 * Request payload for updating a task.
 */
export interface UpdateTaskRequest {
  title?: string
  description?: string
}

/**
 * Response from GET /api/v1/projects/{project_id}/tasks endpoint.
 */
export interface TaskListResponse {
  tasks: Task[]
}

/**
 * Response from POST /api/v1/projects/{project_id}/tasks endpoint.
 */
export type CreateTaskResponse = Task

/**
 * Response from GET /api/v1/tasks/{task_id} endpoint.
 */
export type GetTaskResponse = TaskDetail

/**
 * Response from PATCH /api/v1/tasks/{task_id} endpoint.
 */
export type UpdateTaskResponse = Task

/**
 * Response from GET /api/v1/tasks/{task_id}/code endpoint.
 * Includes the full concatenated code content for document viewer.
 */
export interface GetTaskCodeResponse extends UploadedCode {
  content: string // Concatenated code from all files
}
