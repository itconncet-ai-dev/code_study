import type { Chapter1Content } from '@/types/document'

interface Chapter1Props {
  content: Chapter1Content
}

/**
 * Chapter 1: What This Code Does
 * Displays a one-sentence summary in plain language without jargon
 */
export function Chapter1Summary({ content }: Chapter1Props) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{content.title}</h1>
        <p className="text-gray-600">이 코드가 무엇을 하는지 한 문장으로 이해하세요</p>
      </div>

      <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-r-lg">
        <p className="text-lg leading-relaxed text-gray-800">{content.summary}</p>
      </div>

      <div className="bg-gray-50 p-4 rounded-lg">
        <p className="text-sm text-gray-600">
          이 요약은 프로그래밍 용어 없이 일상 언어로 작성되었습니다. 다음 장에서 필요한 개념들을
          하나씩 배우게 됩니다.
        </p>
      </div>
    </div>
  )
}
