import { useEffect, useState } from 'react'
import type { DocumentGenerationStatus } from '@/types/document'

interface DocumentLoadingProps {
  status: DocumentGenerationStatus
  progress?: number
  estimatedTimeRemaining?: number
  error?: string
}

/**
 * DocumentLoading component displays the document generation progress.
 * Shows different states: pending, in_progress, failed
 * Features:
 * - Progress bar with percentage
 * - Estimated time remaining
 * - Error messages with retry option
 * - Loading animations
 */
export function DocumentLoading({
  status,
  progress = 0,
  estimatedTimeRemaining,
  error,
}: DocumentLoadingProps) {
  const [dots, setDots] = useState('')

  // Animate loading dots
  useEffect(() => {
    if (status === 'in_progress' || status === 'pending') {
      const interval = setInterval(() => {
        setDots((prev) => (prev.length >= 3 ? '' : prev + '.'))
      }, 500)
      return () => clearInterval(interval)
    }
  }, [status])

  if (status === 'failed') {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="max-w-md text-center">
          <div className="mb-4">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full">
              <svg
                className="w-8 h-8 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">문서 생성 실패</h3>
          <p className="text-gray-600 mb-4">{error || '문서를 생성하는 중 오류가 발생했습니다.'}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            다시 시도
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="max-w-md w-full px-4">
        <div className="text-center mb-6">
          {/* Loading Spinner */}
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-blue-200 rounded-full"></div>
              <div className="absolute top-0 left-0 w-16 h-16 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
            </div>
          </div>

          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            AI가 학습 문서를 생성하고 있습니다{dots}
          </h3>
          <p className="text-sm text-gray-600 mb-6">
            {status === 'pending'
              ? '곧 시작됩니다. 잠시만 기다려주세요.'
              : '코드를 분석하여 7개 챕터로 구성된 문서를 작성하고 있습니다.'}
          </p>
        </div>

        {/* Progress Bar */}
        {status === 'in_progress' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">진행률</span>
              <span className="font-semibold text-blue-600">{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            {estimatedTimeRemaining !== undefined && estimatedTimeRemaining > 0 && (
              <p className="text-xs text-gray-500 text-center">
                예상 남은 시간: 약 {Math.ceil(estimatedTimeRemaining / 60)}분
              </p>
            )}
          </div>
        )}

        {/* Info Message */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-xs text-blue-900">
            문서 생성은 코드 크기에 따라 1-3분 정도 소요됩니다. 이 페이지를 벗어나도 생성은 계속
            진행되며, 완료되면 확인할 수 있습니다.
          </p>
        </div>
      </div>
    </div>
  )
}
