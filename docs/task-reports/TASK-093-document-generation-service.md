# Task 093: DocumentGenerationService 구현 (재시도 로직 포함)

**작성일**: 2026-01-24
**상태**: 완료
**파일**: `backend/src/services/document/document_generation_service.py`

## 무엇을 만들었나요?

코드를 AI에게 보내서 7장짜리 학습 문서를 만들어주는 "문서 생성 서비스"를 만들었습니다. 마치 전문 번역가에게 번역을 의뢰하는 것처럼, 코드를 AI에게 보내면 초보자가 이해할 수 있는 설명서로 변환해줍니다.

## 왜 이렇게 만들었나요?

AI 서비스는 가끔 실패할 수 있습니다 (네트워크 오류, 서버 과부하 등). 사용자가 "문서 만들기"를 눌렀는데 한 번 실패했다고 포기하면 안 됩니다. 그래서 자동으로 다시 시도하는 로직을 넣었습니다:

- **최대 3번 재시도**: 한 번 실패해도 3번까지 다시 시도
- **점점 늘어나는 대기 시간**: 2초 → 4초 → 8초로 점점 늘림 (서버에 부담 주지 않기 위해)
- **상태 추적**: "생성 중", "완료", "실패" 상태를 데이터베이스에 기록

## 어떻게 작동하나요?

```
[사용자가 코드 업로드]
        ↓
[DocumentGenerationService.generate_document() 호출]
        ↓
[1. 데이터베이스에서 코드 파일 정보 가져오기]
        ↓
[2. 파일 저장소에서 실제 코드 내용 읽기]
        ↓
[3. 프롬프트 생성 (prompts.py 사용)]
        ↓
[4. AI API 호출 (재시도 로직 포함)]
        ↓
[5. 결과 검증 및 저장]
        ↓
[완료된 7장 학습 문서]
```

## 주요 기능

| 메서드 | 설명 |
|--------|------|
| `generate_document(task_id)` | 메인 함수 - 전체 문서 생성 프로세스 실행 |
| `_generate_with_retry()` | AI 호출 + 재시도 로직 |
| `get_document_status(task_id)` | 현재 생성 상태 조회 |
| `get_document(task_id)` | 완성된 문서 조회 |

## 에러 처리

여러 종류의 에러를 각각 다르게 처리합니다:

- **TaskNotFoundError**: 태스크가 없으면 바로 실패
- **NoCodeUploadedError**: 코드가 없으면 바로 실패
- **DocumentAlreadyExistsError**: 이미 문서가 있으면 알림 (강제 재생성 옵션 있음)
- **GenerationFailedError**: AI 호출 실패 (재시도 후에도 실패하면)

## 어떻게 테스트했나요?

**TDD 방식**으로 진행했습니다:

1. **RED 단계**: 모듈 import가 없는 상태 확인
2. **GREEN 단계**: 서비스 클래스 구현
3. **검증**: Python import 테스트로 모듈이 제대로 로드되는지 확인

```python
from src.services.document import DocumentGenerationService
# Import successful
```

## 수정된 파일들

| 파일 | 변경 내용 |
|------|----------|
| `backend/src/services/document/document_generation_service.py` | 새로 생성 - 메인 서비스 |
| `backend/src/services/document/__init__.py` | 서비스 export 추가 |

## 관련 개념

- **재시도 패턴 (Retry Pattern)**: 일시적인 오류에 대해 자동으로 재시도
- **지수 백오프 (Exponential Backoff)**: 재시도 간격을 점점 늘려 서버 부하 방지
- **비동기 처리 (Async)**: 여러 요청을 동시에 처리할 수 있음

## 주의사항

- 문서 생성은 AI 응답 시간에 따라 최대 3분까지 걸릴 수 있음
- 재시도 횟수 초과 시 `GenerationFailedError` 발생
- 이미 완료된 문서는 `force_regenerate=True`로 재생성 가능

## 다음 단계

- T094: Celery 비동기 태스크 구현 (백그라운드에서 문서 생성)
- T095: 문서 생성 큐 서비스 구현 (상태 추적)
- T096: 코드 업로드 후 자동 문서 생성 트리거
