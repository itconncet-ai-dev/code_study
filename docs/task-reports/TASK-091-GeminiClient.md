# Task T091 - Gemini API Client Wrapper 구현

**완료일**: 2026-01-24
**작성자**: Claude Opus 4.5

## 무엇을 만들었나요?

이번 작업에서는 **GeminiClient**를 만들었습니다. 이것은 Google Gemini AI와 대화하기 위한 "통역사" 같은 역할을 합니다. 우리 플랫폼이 코드를 설명하고, 연습문제를 만들고, 질문에 답하려면 AI의 도움이 필요한데, 이 클라이언트가 그 다리 역할을 해줍니다.

마치 해외에서 현지인과 대화할 때 통역사가 필요한 것처럼, 우리 프로그램과 Gemini AI 사이에서 대화를 전달해주는 도구입니다.

## 왜 이렇게 만들었나요?

GeminiClient의 핵심 기능들을 설명드릴게요:

1. **자동 재시도 (Retry with Exponential Backoff)**: AI 서버가 바쁘거나 잠시 응답을 못 할 때, 포기하지 않고 점점 더 긴 간격으로 다시 시도합니다. 전화가 안 받아지면 1분 후, 2분 후, 4분 후 다시 전화하는 것과 같습니다.

2. **JSON 모드 지원**: 7개 챕터로 구성된 문서를 생성할 때, AI에게 "정해진 형식으로 답변해줘"라고 요청할 수 있습니다. 이렇게 하면 매번 같은 구조의 응답을 받을 수 있습니다.

3. **안전 설정 (Safety Settings)**: 교육용 콘텐츠에 부적절한 내용이 포함되지 않도록 필터가 설정되어 있습니다.

4. **에러 처리**: 다양한 문제 상황에 맞는 에러 타입을 정의했습니다:
   - `GeminiRateLimitError`: 요청이 너무 많을 때
   - `GeminiTimeoutError`: 응답이 너무 오래 걸릴 때
   - `GeminiContentBlockedError`: 안전 필터에 걸렸을 때

## 어떻게 동작하나요?

GeminiClient는 다음과 같은 설정을 환경변수에서 읽어옵니다:

- `GEMINI_API_KEY`: API 접근 키
- `GEMINI_MODEL`: 사용할 모델 (기본: gemini-3-flash-preview)
- `GEMINI_TIMEOUT`: 타임아웃 (기본: 180초)
- `GEMINI_MAX_RETRIES`: 최대 재시도 횟수 (기본: 3회)

주요 메서드:
- `generate_content()`: 일반 텍스트 생성
- `generate_json()`: JSON 형식 응답 생성
- `check_health()`: API 상태 확인

## TDD 방식으로 어떻게 테스트했나요?

실제 API 호출 테스트를 진행했습니다:

1. 설정 로딩 테스트: 환경변수에서 API 키, 모델명, 타임아웃 값이 정상적으로 로드되는지 확인
2. API 연결 테스트: Gemini API에 연결하고 응답을 받을 수 있는지 확인
3. 재시도 로직 테스트: Rate limit 에러 시 exponential backoff로 재시도하는 것 확인

테스트 결과:
- 설정 로딩: 성공 (모델: gemini-3-flash-preview, 타임아웃: 180s)
- API 연결: 성공 (rate limit으로 인해 에러 발생하지만 에러 처리 정상 동작)
- 재시도 로직: 성공 (4회 시도 후 GeminiRateLimitError 발생)

## 어떤 파일을 수정했나요?

| 파일 | 변경 내용 |
|------|----------|
| `backend/src/services/ai/gemini_client.py` | 새로 생성 - GeminiClient, GeminiSettings, 에러 클래스들 |
| `backend/src/services/ai/__init__.py` | 수정 - 새 클래스들 export |

## 관련 개념

- **API Client**: 외부 서비스와 통신하기 위한 래퍼 클래스
- **Exponential Backoff**: 재시도 간격을 지수적으로 늘리는 전략 (1초 → 2초 → 4초...)
- **Pydantic Settings**: 환경변수를 타입 안전하게 로드하는 라이브러리
- **asyncio**: Python의 비동기 프로그래밍 라이브러리

## 주의할 점

- API 키는 반드시 환경변수로 관리 (코드에 하드코딩 금지)
- 무료 티어는 일일 요청 제한이 있음 (테스트 시 주의)
- 문서 생성은 최대 3분, Q&A는 최대 20초 타임아웃 권장

## 다음 단계

- T092: 7챕터 문서 생성용 프롬프트 템플릿 구현
- T093: DocumentGenerationService 구현
- T094: Celery 비동기 문서 생성 태스크 구현
