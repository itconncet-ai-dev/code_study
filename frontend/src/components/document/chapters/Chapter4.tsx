import { Card, CardContent } from '@/components/ui/card'
import type { Chapter4Content } from '@/types/document'

interface Chapter4Props {
  content: Chapter4Content
}

/**
 * Chapter 4: Line-by-Line Explanation
 * Displays detailed explanations for each line of code with:
 * - What the line does
 * - Syntax breakdown
 * - Real-life analogy
 * - Alternative examples
 * - Important notes
 */
export function Chapter4LineByLine({ content }: Chapter4Props) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{content.title}</h1>
        <p className="text-gray-600">코드를 한 줄씩 자세히 설명합니다</p>
      </div>

      <div className="space-y-4">
        {content.explanations.map((explanation, index) => (
          <Card key={index} className="border-l-4 border-green-500">
            <CardContent className="pt-6">
              {/* Line Number and Code */}
              <div className="mb-4">
                <div className="flex items-baseline gap-2 mb-2">
                  <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-green-500 text-white text-xs font-bold">
                    {explanation.line_number}
                  </span>
                  <span className="text-xs text-gray-500">라인</span>
                </div>
                <pre className="bg-gray-900 text-gray-100 p-3 rounded-lg overflow-x-auto">
                  <code className="text-sm font-mono">{explanation.code}</code>
                </pre>
              </div>

              {/* What It Does */}
              <div className="space-y-3">
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-1">
                    이 줄은 무엇을 하나요?
                  </h3>
                  <p className="text-gray-800 leading-relaxed">{explanation.what_it_does}</p>
                </div>

                {/* Syntax Breakdown */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-1">문법 설명</h3>
                  <p className="text-gray-800 leading-relaxed">{explanation.syntax_breakdown}</p>
                </div>

                {/* Real-life Analogy */}
                <div className="bg-purple-50 p-3 rounded-lg">
                  <h3 className="text-sm font-semibold text-purple-900 mb-1 flex items-center gap-2">
                    <span>💡</span>
                    실생활 비유
                  </h3>
                  <p className="text-purple-900 leading-relaxed">{explanation.analogy}</p>
                </div>

                {/* Alternative Examples */}
                {explanation.alternative_examples && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-1">다른 예시</h3>
                    <pre className="bg-gray-100 p-3 rounded-lg overflow-x-auto">
                      <code className="text-sm text-gray-800">
                        {explanation.alternative_examples}
                      </code>
                    </pre>
                  </div>
                )}

                {/* Important Notes */}
                {explanation.notes && (
                  <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded-r-lg">
                    <h3 className="text-sm font-semibold text-yellow-900 mb-1 flex items-center gap-2">
                      <span>⚠️</span>
                      중요한 참고사항
                    </h3>
                    <p className="text-yellow-900 text-sm leading-relaxed">{explanation.notes}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="bg-gray-50 p-4 rounded-lg">
        <p className="text-sm text-gray-600">
          각 라인의 역할을 이해했다면, 다음 장에서 코드가 실행되는 전체 흐름을 살펴보세요.
        </p>
      </div>
    </div>
  )
}
