import { get } from './api-client'
import type {
  GetDocumentResponse,
  DocumentStatusResponse,
} from '@/types/document'

/**
 * Document service for handling learning document-related API operations.
 * Supports fetching documents and polling generation status.
 */
export const documentService = {
  /**
   * Get the learning document for a task.
   * @param taskId - Task ID
   * @returns Learning document with all 7 chapters
   */
  async getDocument(taskId: string): Promise<GetDocumentResponse> {
    return get<GetDocumentResponse>(`/tasks/${taskId}/document`)
  },

  /**
   * Get the document generation status.
   * Used for polling during async document generation.
   * @param taskId - Task ID
   * @returns Generation status with progress and estimated time
   */
  async getDocumentStatus(taskId: string): Promise<DocumentStatusResponse> {
    return get<DocumentStatusResponse>(`/tasks/${taskId}/document/status`)
  },
}

export default documentService
