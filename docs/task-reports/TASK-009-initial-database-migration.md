# TASK-009: 초기 데이터베이스 마이그레이션 생성

**완료일**: 2025-01-19
**작업 위치**: `backend/alembic/versions/001_initial_schema.py`

## 무엇을 만들었나요?

AI 코드 학습 플랫폼의 모든 데이터베이스 테이블을 생성하는 초기 마이그레이션 파일을 작성했습니다.

마이그레이션이 뭘까요? 건축에 비유하면 이해하기 쉽습니다. 건물을 지을 때 "설계도"가 필요하듯이, 데이터베이스도 "테이블 설계도"가 필요합니다. 이 마이그레이션 파일이 바로 그 설계도입니다. `alembic upgrade head` 명령어 한 번으로 설계도대로 모든 테이블이 자동으로 만들어집니다.

## 왜 이 방식을 선택했나요?

**테이블 의존성 순서가 중요합니다.** 예를 들어 "프로젝트" 테이블은 "사용자" 테이블을 참조하므로, 사용자 테이블이 먼저 만들어져야 합니다.

생성 순서:
1. `users` - 모든 것의 시작점 (사용자)
2. `refresh_tokens` - 사용자에 연결 (로그인 유지용)
3. `projects` - 사용자에 연결 (학습 프로젝트)
4. `tasks` - 프로젝트에 연결 (개별 학습 단위)
5. `uploaded_code` - 태스크에 연결 (업로드된 코드)
6. `code_files` - 업로드된 코드에 연결 (개별 파일)
7. `learning_documents` - 태스크에 연결 (AI 생성 문서)
8. `practice_problems` - 태스크에 연결 (연습 문제)
9. `questions` - 태스크와 사용자에 연결 (Q&A)
10. `progress` - 태스크와 사용자에 연결 (학습 진행도)

## 어떻게 작동하나요?

```python
# 테이블 생성 예시 (users 테이블)
op.create_table(
    "users",
    sa.Column("id", UUID(as_uuid=True), primary_key=True),
    sa.Column("email", sa.String(255), unique=True, nullable=False),
    sa.Column("password_hash", sa.String(255), nullable=False),
    # ... 더 많은 컬럼들
)
```

각 테이블마다:
- **UUID 기본키**: 고유한 ID 자동 생성
- **타임스탬프**: 생성/수정 시간 자동 기록
- **Soft Delete**: 프로젝트와 태스크는 바로 삭제되지 않고 30일간 휴지통에 보관
- **제약 조건**: 이메일 형식 검증, 최소/최대 길이 등

## 어떻게 테스트했나요?

1. **Python 구문 검사**:
   ```bash
   python -m py_compile alembic/versions/001_initial_schema.py  # 성공
   ```

2. **임포트 테스트**:
   ```bash
   python -c "from alembic import op; import sqlalchemy as sa; ..."  # 성공
   ```

## 생성된 테이블 요약

| 테이블 | 설명 | 주요 특징 |
|--------|------|----------|
| users | 사용자 정보 | 이메일 유효성 검사 |
| refresh_tokens | JWT 리프레시 토큰 | 해시 저장, 7일 만료 |
| projects | 학습 프로젝트 | Soft delete, 30일 보관 |
| tasks | 개별 학습 단위 | 순차 번호, Soft delete |
| uploaded_code | 업로드된 코드 메타데이터 | 10MB 제한 |
| code_files | 개별 코드 파일 | 지원 확장자 제한 |
| learning_documents | AI 생성 학습 문서 | 7개 챕터 JSONB |
| practice_problems | 연습 문제 | 5개/태스크, 난이도순 |
| questions | Q&A 기록 | 질문 길이 제한 |
| progress | 학습 진행도 | 챕터별/문제별 추적 |

## 수정된 파일들

| 파일 | 변경 내용 |
|------|----------|
| `backend/alembic/versions/001_initial_schema.py` | 신규 - 10개 테이블 스키마 정의 |
| `specs/001-code-learning-platform/tasks.md` | T009 완료 표시 |

## 관련 개념

- **외래 키(Foreign Key)**: 테이블 간 연결 고리. 예: 프로젝트는 반드시 사용자에게 속함
- **CASCADE DELETE**: 부모 삭제시 자식도 자동 삭제. 예: 사용자 삭제 → 프로젝트도 삭제
- **JSONB**: PostgreSQL의 JSON 저장 타입. 유연한 구조의 데이터 저장에 적합
- **부분 인덱스(Partial Index)**: 특정 조건의 행만 인덱싱. 예: `WHERE deletion_status = 'active'`

## 주의사항

1. **실제 DB 적용 필요**: 이 파일은 "설계도"일 뿐. `alembic upgrade head`로 실제 적용해야 함
2. **PostgreSQL 필수**: `gen_random_uuid()`, `JSONB` 등 PostgreSQL 전용 기능 사용
3. **downgrade() 주의**: 롤백시 모든 데이터가 삭제됨 (개발 환경에서만 사용)

## 다음 단계

- **T010** [P]: 데이터베이스 세션 관리 구현 (`backend/src/db/session.py`)
- **T011** [P]: 데이터베이스 연결 풀 설정 (`backend/src/db/config.py`)
- T010과 T011은 병렬 작업 가능 (서로 독립적)
