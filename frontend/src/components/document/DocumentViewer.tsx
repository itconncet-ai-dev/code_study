import { useState, useCallback } from 'react'
import { CodePanel } from './CodePanel'
import { ExplanationPanel } from './ExplanationPanel'
import { Chapter1Summary } from './chapters/Chapter1'
import { Chapter2Prerequisites } from './chapters/Chapter2'
import { Chapter4LineByLine } from './chapters/Chapter4'
import type { LearningDocument, ChapterNumber } from '@/types/document'

interface DocumentViewerProps {
  document: LearningDocument
  code: string
  language: string
  onChapterComplete?: (chapter: ChapterNumber, completed: boolean) => void
  completedChapters?: ChapterNumber[]
}

/**
 * DocumentViewer component displays the learning document in a 2-column layout.
 * Features:
 * - Code panel on the left with syntax highlighting
 * - Explanation panel on the right with chapter navigation
 * - Synchronized scrolling between panels
 * - Chapter completion tracking
 * - Non-linear chapter navigation
 */
export function DocumentViewer({
  document,
  code,
  language,
  onChapterComplete,
  completedChapters = [],
}: DocumentViewerProps) {
  const [currentChapter, setCurrentChapter] = useState<ChapterNumber>(1)
  const [highlightedLines, setHighlightedLines] = useState<number[]>([])

  // Chapter navigation data
  const chapters = [
    { number: 1 as ChapterNumber, title: document.content.chapter1.title, completed: completedChapters.includes(1) },
    { number: 2 as ChapterNumber, title: document.content.chapter2.title, completed: completedChapters.includes(2) },
    { number: 3 as ChapterNumber, title: document.content.chapter3.title, completed: completedChapters.includes(3) },
    { number: 4 as ChapterNumber, title: document.content.chapter4.title, completed: completedChapters.includes(4) },
    { number: 5 as ChapterNumber, title: document.content.chapter5.title, completed: completedChapters.includes(5) },
    { number: 6 as ChapterNumber, title: document.content.chapter6.title, completed: completedChapters.includes(6) },
    { number: 7 as ChapterNumber, title: document.content.chapter7.title, completed: completedChapters.includes(7) },
  ]

  /**
   * Handle chapter navigation
   */
  const handleChapterClick = useCallback((chapter: ChapterNumber) => {
    setCurrentChapter(chapter)
    setHighlightedLines([])
  }, [])

  /**
   * Handle chapter completion toggle
   */
  const handleChapterComplete = useCallback(
    (chapter: ChapterNumber, completed: boolean) => {
      if (onChapterComplete) {
        onChapterComplete(chapter, completed)
      }
    },
    [onChapterComplete]
  )

  /**
   * Handle code panel scroll for synchronization
   * (Future enhancement: can implement synchronized scrolling logic here)
   */
  const handleCodeScroll = useCallback((scrollTop: number) => {
    // Placeholder for synchronized scrolling logic
    // Could calculate which explanation corresponds to visible code lines
    console.log('Code scrolled to:', scrollTop)
  }, [])

  /**
   * Handle explanation panel scroll for synchronization
   * (Future enhancement: can implement synchronized scrolling logic here)
   */
  const handleExplanationScroll = useCallback((scrollTop: number) => {
    // Placeholder for synchronized scrolling logic
    console.log('Explanation scrolled to:', scrollTop)
  }, [])

  /**
   * Render current chapter content
   */
  const renderChapterContent = () => {
    switch (currentChapter) {
      case 1:
        return <Chapter1Summary content={document.content.chapter1} />
      case 2:
        return <Chapter2Prerequisites content={document.content.chapter2} />
      case 3:
        return (
          <div className="space-y-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {document.content.chapter3.title}
            </h1>
            <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto">
              <code>{document.content.chapter3.flowchart}</code>
            </pre>
          </div>
        )
      case 4:
        return <Chapter4LineByLine content={document.content.chapter4} />
      case 5:
        return (
          <div className="space-y-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {document.content.chapter5.title}
            </h1>
            <div className="space-y-4">
              {document.content.chapter5.steps.map((step) => (
                <div key={step.step_number} className="border-l-4 border-indigo-500 bg-white p-4 rounded-r-lg shadow-sm">
                  <div className="font-semibold text-indigo-900 mb-2">
                    Step {step.step_number}
                  </div>
                  <p className="text-gray-800">{step.description}</p>
                </div>
              ))}
            </div>
          </div>
        )
      case 6:
        return (
          <div className="space-y-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {document.content.chapter6.title}
            </h1>
            <div className="space-y-4">
              {document.content.chapter6.concepts.map((concept, index) => (
                <div key={index} className="bg-white border border-gray-200 p-4 rounded-lg">
                  <h3 className="font-semibold text-lg text-gray-900 mb-2">
                    {concept.name}
                  </h3>
                  <div className="space-y-2 text-sm">
                    <p><strong>무엇인가요?</strong> {concept.what_it_is}</p>
                    <p><strong>왜 사용하나요?</strong> {concept.why_used}</p>
                    <p><strong>어디에 적용되나요?</strong> {concept.where_applied}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      case 7:
        return (
          <div className="space-y-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {document.content.chapter7.title}
            </h1>
            <div className="space-y-4">
              {document.content.chapter7.mistakes.map((mistake, index) => (
                <div key={index} className="bg-red-50 border border-red-200 p-4 rounded-lg">
                  <div className="grid md:grid-cols-2 gap-4 mb-3">
                    <div>
                      <h4 className="text-sm font-semibold text-red-900 mb-2">❌ 잘못된 코드</h4>
                      <pre className="bg-white p-2 rounded text-xs overflow-x-auto">
                        <code>{mistake.wrong}</code>
                      </pre>
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-green-900 mb-2">✅ 올바른 코드</h4>
                      <pre className="bg-white p-2 rounded text-xs overflow-x-auto">
                        <code>{mistake.right}</code>
                      </pre>
                    </div>
                  </div>
                  <div className="space-y-2 text-sm">
                    <p><strong>왜 문제인가요?</strong> {mistake.why}</p>
                    <p><strong>어떻게 고치나요?</strong> {mistake.fix}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="h-full grid grid-cols-2 gap-0">
      {/* Code Panel - Left Side */}
      <CodePanel
        code={code}
        language={language}
        highlightedLines={highlightedLines}
        onScroll={handleCodeScroll}
      />

      {/* Explanation Panel - Right Side */}
      <ExplanationPanel
        chapters={chapters}
        currentChapter={currentChapter}
        onChapterClick={handleChapterClick}
        onChapterComplete={handleChapterComplete}
        onScroll={handleExplanationScroll}
      >
        {renderChapterContent()}
      </ExplanationPanel>
    </div>
  )
}
