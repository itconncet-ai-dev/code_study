import { describe, it, expect, vi, beforeEach } from 'vitest'
import { taskService } from './task-service'
import * as apiClient from './api-client'
import type {
  Task,
  TaskDetail,
  CreateTaskRequest,
  UpdateTaskRequest,
  UploadedCode,
} from '@/types/task'

// Mock the api-client module
vi.mock('./api-client', () => ({
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
  del: vi.fn(),
  uploadFiles: vi.fn(),
}))

describe('taskService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getTasks', () => {
    it('should fetch tasks for a project without trashed tasks', async () => {
      const mockTasks: Task[] = [
        {
          id: 'task-1',
          project_id: 'project-1',
          task_number: 1,
          title: 'Test Task',
          upload_method: 'file',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          deletion_status: 'active',
        },
      ]

      vi.mocked(apiClient.get).mockResolvedValue({ tasks: mockTasks })

      const result = await taskService.getTasks('project-1')

      expect(apiClient.get).toHaveBeenCalledWith('/projects/project-1/tasks')
      expect(result).toEqual({ tasks: mockTasks })
    })

    it('should fetch tasks including trashed when specified', async () => {
      const mockTasks: Task[] = [
        {
          id: 'task-1',
          project_id: 'project-1',
          task_number: 1,
          title: 'Test Task',
          upload_method: 'file',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          deletion_status: 'trashed',
        },
      ]

      vi.mocked(apiClient.get).mockResolvedValue({ tasks: mockTasks })

      const result = await taskService.getTasks('project-1', true)

      expect(apiClient.get).toHaveBeenCalledWith('/projects/project-1/tasks?include_trashed=true')
      expect(result).toEqual({ tasks: mockTasks })
    })
  })

  describe('createTask', () => {
    it('should create a task with file upload', async () => {
      const mockTask: Task = {
        id: 'task-1',
        project_id: 'project-1',
        task_number: 1,
        title: 'New Task',
        description: 'Test description',
        upload_method: 'file',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        deletion_status: 'active',
      }

      const request: CreateTaskRequest = {
        title: 'New Task',
        description: 'Test description',
        upload_method: 'file',
      }

      const file = new File(['content'], 'test.py', { type: 'text/plain' })

      vi.mocked(apiClient.uploadFiles).mockResolvedValue(mockTask)

      const result = await taskService.createTask('project-1', request, [file])

      expect(apiClient.uploadFiles).toHaveBeenCalledWith(
        '/projects/project-1/tasks',
        expect.any(FormData)
      )
      expect(result).toEqual(mockTask)
    })

    it('should create a task with folder upload', async () => {
      const mockTask: Task = {
        id: 'task-1',
        project_id: 'project-1',
        task_number: 1,
        title: 'New Task',
        upload_method: 'folder',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        deletion_status: 'active',
      }

      const request: CreateTaskRequest = {
        title: 'New Task',
        upload_method: 'folder',
      }

      const files = [
        new File(['content1'], 'src/test1.py', { type: 'text/plain' }),
        new File(['content2'], 'src/test2.py', { type: 'text/plain' }),
      ]

      vi.mocked(apiClient.uploadFiles).mockResolvedValue(mockTask)

      const result = await taskService.createTask('project-1', request, files)

      expect(apiClient.uploadFiles).toHaveBeenCalledWith(
        '/projects/project-1/tasks',
        expect.any(FormData)
      )
      expect(result).toEqual(mockTask)
    })

    it('should create a task with pasted code', async () => {
      const mockTask: Task = {
        id: 'task-1',
        project_id: 'project-1',
        task_number: 1,
        title: 'New Task',
        upload_method: 'paste',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        deletion_status: 'active',
      }

      const request: CreateTaskRequest = {
        title: 'New Task',
        upload_method: 'paste',
      }

      const codeContent = 'def hello(): print("Hello")'
      const language = 'python'

      vi.mocked(apiClient.uploadFiles).mockResolvedValue(mockTask)

      const result = await taskService.createTask(
        'project-1',
        request,
        undefined,
        codeContent,
        language
      )

      expect(apiClient.uploadFiles).toHaveBeenCalledWith(
        '/projects/project-1/tasks',
        expect.any(FormData)
      )
      expect(result).toEqual(mockTask)
    })
  })

  describe('getTask', () => {
    it('should fetch a single task by ID', async () => {
      const mockTask: TaskDetail = {
        id: 'task-1',
        project_id: 'project-1',
        task_number: 1,
        title: 'Test Task',
        upload_method: 'file',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        deletion_status: 'active',
        document_status: 'pending',
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockTask)

      const result = await taskService.getTask('task-1')

      expect(apiClient.get).toHaveBeenCalledWith('/tasks/task-1')
      expect(result).toEqual(mockTask)
    })
  })

  describe('updateTask', () => {
    it('should update a task', async () => {
      const mockTask: Task = {
        id: 'task-1',
        project_id: 'project-1',
        task_number: 1,
        title: 'Updated Task',
        upload_method: 'file',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
        deletion_status: 'active',
      }

      const updateData: UpdateTaskRequest = {
        title: 'Updated Task',
      }

      vi.mocked(apiClient.patch).mockResolvedValue(mockTask)

      const result = await taskService.updateTask('task-1', updateData)

      expect(apiClient.patch).toHaveBeenCalledWith('/tasks/task-1', updateData)
      expect(result).toEqual(mockTask)
    })
  })

  describe('deleteTask', () => {
    it('should soft delete a task', async () => {
      vi.mocked(apiClient.del).mockResolvedValue(undefined)

      await taskService.deleteTask('task-1')

      expect(apiClient.del).toHaveBeenCalledWith('/tasks/task-1')
    })
  })

  describe('getTaskCode', () => {
    it('should fetch uploaded code for a task', async () => {
      const mockCode: UploadedCode = {
        id: 'code-1',
        detected_language: 'python',
        complexity_level: 'beginner',
        total_lines: 100,
        total_files: 1,
        upload_size_bytes: 1024,
        code_files: [
          {
            id: 'file-1',
            file_name: 'test.py',
            file_extension: '.py',
            file_size_bytes: 1024,
          },
        ],
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockCode)

      const result = await taskService.getTaskCode('task-1')

      expect(apiClient.get).toHaveBeenCalledWith('/tasks/task-1/code')
      expect(result).toEqual(mockCode)
    })
  })
})
