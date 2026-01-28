import { useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import type { ChapterNumber } from '@/types/document'

interface ChapterNavItem {
  number: ChapterNumber
  title: string
  completed: boolean
}

interface ExplanationPanelProps {
  children: React.ReactNode
  chapters: ChapterNavItem[]
  currentChapter: ChapterNumber
  onChapterClick: (chapter: ChapterNumber) => void
  onChapterComplete: (chapter: ChapterNumber, completed: boolean) => void
  onScroll?: (scrollTop: number) => void
}

/**
 * ExplanationPanel component displays learning content with chapter navigation.
 * Features:
 * - Chapter navigation sidebar with current chapter highlighting
 * - Chapter completion checkboxes
 * - Scrollable content area
 * - Scroll event callback for synchronization with CodePanel
 */
export function ExplanationPanel({
  children,
  chapters,
  currentChapter,
  onChapterClick,
  onChapterComplete,
  onScroll,
}: ExplanationPanelProps) {
  const contentRef = useRef<HTMLDivElement>(null)

  /**
   * Handle scroll events for synchronization
   */
  useEffect(() => {
    const content = contentRef.current
    if (!content || !onScroll) {
      return
    }

    const handleScroll = () => {
      onScroll(content.scrollTop)
    }

    content.addEventListener('scroll', handleScroll)
    return () => content.removeEventListener('scroll', handleScroll)
  }, [onScroll])

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
        <h2 className="text-sm font-semibold text-gray-700">설명</h2>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Chapter Navigation */}
        <nav className="w-64 border-r border-gray-200 overflow-y-auto bg-gray-50">
          <div className="p-4 space-y-1">
            {chapters.map((chapter) => (
              <div
                key={chapter.number}
                className="flex items-start gap-2 group"
              >
                <input
                  type="checkbox"
                  checked={chapter.completed}
                  onChange={(e) =>
                    onChapterComplete(chapter.number, e.target.checked)
                  }
                  className="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  aria-label={`${chapter.title} 완료`}
                />
                <button
                  onClick={() => onChapterClick(chapter.number)}
                  className={cn(
                    'flex-1 text-left px-3 py-2 rounded-md text-sm transition-colors',
                    currentChapter === chapter.number
                      ? 'bg-blue-100 text-blue-900 font-medium'
                      : 'text-gray-700 hover:bg-gray-100'
                  )}
                >
                  <div className="font-medium">Chapter {chapter.number}</div>
                  <div className="text-xs mt-0.5 opacity-90">
                    {chapter.title}
                  </div>
                </button>
              </div>
            ))}
          </div>
        </nav>

        {/* Content Area */}
        <div
          ref={contentRef}
          className="flex-1 overflow-y-auto p-6"
        >
          {children}
        </div>
      </div>
    </div>
  )
}
