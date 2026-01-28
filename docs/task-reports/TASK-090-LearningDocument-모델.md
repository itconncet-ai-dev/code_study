# Task T090 - LearningDocument SQLAlchemy 모델 생성

**완료일**: 2026-01-24
**작성자**: Claude Opus 4.5

## 무엇을 만들었나요?

이번 작업에서는 **LearningDocument(학습 문서)** 데이터베이스 모델을 만들었습니다. LearningDocument는 AI가 생성한 7개 챕터로 구성된 코드 설명 문서입니다. 마치 선생님이 학생의 코드를 보고 친절하게 설명해주는 교과서 한 권을 만들어주는 것과 같습니다.

사용자가 코드를 업로드하면, AI가 자동으로 이 문서를 생성합니다. 문서에는 "이 코드가 뭘 하는 건지", "이걸 이해하려면 뭘 알아야 하는지", "한 줄 한 줄 설명", "흔히 하는 실수" 같은 내용이 담깁니다.

## 왜 이렇게 만들었나요?

LearningDocument 모델의 핵심 특징들을 설명드릴게요:

1. **JSONB 형식 저장**: 7개 챕터 내용을 유연한 JSON 형식으로 저장합니다. 마치 서랍장처럼, 각 서랍(챕터)에 필요한 내용을 자유롭게 담을 수 있습니다.

2. **생성 상태 추적**: 문서 생성이 "대기 중", "진행 중", "완료", "실패" 중 어떤 상태인지 추적합니다. 음식 배달 앱에서 "주문 확인 → 조리 중 → 배달 중 → 배달 완료" 상태를 보여주는 것과 같습니다.

3. **비동기 처리**: Celery라는 백그라운드 작업 시스템과 연동됩니다. AI 문서 생성이 3분까지 걸릴 수 있어서, 사용자가 기다리지 않아도 되도록 백그라운드에서 처리합니다.

4. **Task와 1:1 관계**: 하나의 Task(학습 태스크)에 하나의 문서가 연결됩니다. Task가 삭제되면 문서도 함께 삭제됩니다.

## 어떻게 동작하나요?

LearningDocument 모델은 다음 정보를 저장합니다:

- `id`: 고유 식별자 (UUID)
- `task_id`: 연결된 Task (1:1 관계)
- `content`: 7개 챕터 내용 (JSONB)
- `generation_status`: 생성 상태 (pending, in_progress, completed, failed)
- `generation_started_at`: 생성 시작 시각
- `generation_completed_at`: 생성 완료 시각
- `generation_error`: 실패 시 에러 메시지
- `celery_task_id`: 백그라운드 작업 ID

편의 메서드도 있습니다:
- `start_generation()`: 생성 시작 처리
- `complete_generation()`: 생성 완료 처리
- `fail_generation()`: 실패 처리
- `get_chapter()`: 특정 챕터 가져오기

## TDD 방식으로 어떻게 테스트했나요?

TDD(테스트 주도 개발) 방식을 따랐습니다:

1. **RED 단계**: 모델 구조와 동작을 정의하는 테스트 케이스를 먼저 계획했습니다.

2. **GREEN 단계**: LearningDocument 모델을 구현하고, Task 모델과의 관계를 설정했습니다. 모든 필드, 속성, 메서드가 정상 동작합니다.

3. **REFACTOR 단계**: 코드가 이미 깔끔하여 별도 리팩토링은 필요하지 않았습니다.

## 어떤 파일을 수정했나요?

| 파일 | 변경 내용 |
|------|----------|
| `backend/src/models/learning_document.py` | 새로 생성 - LearningDocument 모델 정의 |
| `backend/src/models/task.py` | learning_document 관계 추가 |
| `backend/src/models/__init__.py` | LearningDocument 모델 export 추가 |

## 관련 개념

- **JSONB**: PostgreSQL의 JSON 바이너리 형식. 유연한 구조의 데이터를 효율적으로 저장
- **Celery**: Python 비동기 작업 큐. 오래 걸리는 작업을 백그라운드에서 처리
- **1:1 관계**: 하나의 레코드가 정확히 하나의 다른 레코드와 연결되는 관계

## 주의할 점

- 문서는 생성 후 수정 불가 (immutable) - FR-038 요구사항
- 7개 챕터가 모두 있어야 완료 상태로 처리
- Task 삭제 시 문서도 CASCADE 삭제됨

## 다음 단계

- T091: Gemini API 클라이언트 래퍼 구현
- T092: 7개 챕터 문서 생성용 프롬프트 템플릿 구현
- T093: DocumentGenerationService 구현
