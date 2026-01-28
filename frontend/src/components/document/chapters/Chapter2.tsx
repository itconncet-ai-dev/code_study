import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { Chapter2Content } from '@/types/document'

interface Chapter2Props {
  content: Chapter2Content
}

/**
 * Chapter 2: Prerequisites Knowledge
 * Displays concept cards with explanations, analogies, examples, and use cases
 * Maximum 5 concepts per FR-029
 */
export function Chapter2Prerequisites({ content }: Chapter2Props) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{content.title}</h1>
        <p className="text-gray-600">이 코드를 이해하기 위해 알아야 할 기본 개념들</p>
      </div>

      <div className="grid gap-6">
        {content.concepts.map((concept, index) => (
          <Card key={index} className="border-l-4 border-blue-500">
            <CardHeader>
              <CardTitle className="text-xl text-gray-900">{concept.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Simple Explanation */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">쉬운 설명</h3>
                <p className="text-gray-800 leading-relaxed">{concept.explanation}</p>
              </div>

              {/* Real-life Analogy */}
              <div className="bg-amber-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-amber-900 mb-2 flex items-center gap-2">
                  <span>💡</span>
                  실생활 비유
                </h3>
                <p className="text-amber-900 leading-relaxed">{concept.analogy}</p>
              </div>

              {/* Code Example */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">코드 예시</h3>
                <pre className="bg-gray-100 p-3 rounded-lg overflow-x-auto">
                  <code className="text-sm text-gray-800">{concept.example}</code>
                </pre>
              </div>

              {/* Use Cases */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">언제 사용하나요?</h3>
                <p className="text-gray-800 leading-relaxed">{concept.use_cases}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="bg-gray-50 p-4 rounded-lg">
        <p className="text-sm text-gray-600">
          이제 기본 개념을 알았으니 코드를 한 줄씩 자세히 살펴보겠습니다.
        </p>
      </div>
    </div>
  )
}
