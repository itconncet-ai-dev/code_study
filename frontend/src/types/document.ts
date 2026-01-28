/**
 * Document types for the AI Code Learning Platform.
 * Based on the LearningDocument JSONB structure from data-model.md
 */

/**
 * Chapter 1: What This Code Does
 * One-sentence summary in plain language
 */
export interface Chapter1Content {
  title: string
  summary: string
}

/**
 * Individual concept card for Chapter 2
 */
export interface PrerequisiteConcept {
  name: string
  explanation: string
  analogy: string
  example: string
  use_cases: string
}

/**
 * Chapter 2: Prerequisites Knowledge
 * Concept cards with analogies (maximum 5 concepts)
 */
export interface Chapter2Content {
  title: string
  concepts: PrerequisiteConcept[]
}

/**
 * Chapter 3: Code Structure Overview
 */
export interface Chapter3Content {
  title: string
  flowchart: string // ASCII/Mermaid diagram
  file_breakdown: Record<string, unknown>
}

/**
 * Line-by-line explanation entry for Chapter 4
 */
export interface LineExplanation {
  line_number: number
  code: string
  what_it_does: string
  syntax_breakdown: string
  analogy: string
  alternative_examples?: string
  notes?: string
}

/**
 * Chapter 4: Line-by-Line Explanation
 */
export interface Chapter4Content {
  title: string
  explanations: LineExplanation[]
}

/**
 * Execution flow step for Chapter 5
 */
export interface ExecutionStep {
  step_number: number
  description: string
  state_changes?: Record<string, unknown>
}

/**
 * Chapter 5: Execution Flow Simulation
 */
export interface Chapter5Content {
  title: string
  steps: ExecutionStep[]
}

/**
 * Core concept summary for Chapter 6
 */
export interface CoreConcept {
  name: string
  what_it_is: string
  why_used: string
  where_applied: string
}

/**
 * Chapter 6: Core Concepts Summary
 */
export interface Chapter6Content {
  title: string
  concepts: CoreConcept[]
}

/**
 * Common mistake entry for Chapter 7
 */
export interface CommonMistake {
  wrong: string
  right: string
  why: string
  fix: string
}

/**
 * Chapter 7: Common Mistakes
 */
export interface Chapter7Content {
  title: string
  mistakes: CommonMistake[]
}

/**
 * Complete learning document with all 7 chapters
 */
export interface LearningDocumentContent {
  chapter1: Chapter1Content
  chapter2: Chapter2Content
  chapter3: Chapter3Content
  chapter4: Chapter4Content
  chapter5: Chapter5Content
  chapter6: Chapter6Content
  chapter7: Chapter7Content
}

/**
 * Generation status for async document generation
 */
export type DocumentGenerationStatus = 'pending' | 'in_progress' | 'completed' | 'failed'

/**
 * Learning document entity with generation metadata
 */
export interface LearningDocument {
  id: string
  task_id: string
  content: LearningDocumentContent
  generation_status: DocumentGenerationStatus
  generation_started_at?: string
  generation_completed_at?: string
  generation_error?: string
  celery_task_id?: string
  created_at: string
  updated_at: string
}

/**
 * Document status response for polling
 */
export interface DocumentStatusResponse {
  status: DocumentGenerationStatus
  progress?: number // 0-100
  estimated_time_remaining?: number // seconds
  error?: string
}

/**
 * Get document response from API
 */
export type GetDocumentResponse = LearningDocument

/**
 * Chapter identifier (1-7)
 */
export type ChapterNumber = 1 | 2 | 3 | 4 | 5 | 6 | 7

/**
 * Chapter metadata for navigation
 */
export interface ChapterMetadata {
  number: ChapterNumber
  title: string
  completed: boolean
}
