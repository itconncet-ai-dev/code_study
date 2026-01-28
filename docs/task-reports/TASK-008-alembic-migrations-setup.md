# TASK-008: Alembic 마이그레이션 프레임워크 설정

**완료일**: 2025-01-19
**작업 위치**: `backend/alembic/`

## 무엇을 만들었나요?

데이터베이스 테이블 구조를 관리하는 Alembic 마이그레이션 시스템을 설정했습니다.

마이그레이션이란 뭘까요? 은행에서 장부 양식을 바꾼다고 생각해보세요. 예전에는 "이름, 계좌번호" 두 칸만 있었는데, 새로운 규정으로 "이름, 계좌번호, 전화번호" 세 칸이 필요해졌어요. 이때 모든 기존 장부를 새 양식으로 바꾸는 작업이 필요합니다. Alembic이 바로 데이터베이스에서 이런 "양식 변경" 작업을 자동으로 해주는 도구입니다.

## 왜 이 방식을 선택했나요?

**Python + SQLAlchemy 프로젝트에서 Alembic은 표준 선택입니다.** 다른 도구도 있지만, Alembic은:

1. **자동 감지**: 코드에서 모델을 바꾸면 변경사항을 자동으로 찾아줍니다
2. **되돌리기 가능**: 실수해도 이전 상태로 돌아갈 수 있습니다
3. **이력 관리**: 누가, 언제, 무엇을 바꿨는지 기록됩니다

## 어떻게 작동하나요?

```
backend/
├── alembic.ini          # 설정 파일 (연결 정보, 로깅 등)
├── alembic/
│   ├── env.py           # 실행 환경 설정 (DB 연결 방법)
│   ├── script.py.mako   # 마이그레이션 파일 템플릿
│   ├── README           # 사용법 안내
│   └── versions/        # 마이그레이션 파일들이 저장되는 곳
└── src/models/
    └── base.py          # 모든 DB 모델의 기본 클래스
```

**작동 흐름**:
1. 개발자가 모델 파일에서 새 컬럼 추가
2. `alembic revision --autogenerate` 명령 실행
3. Alembic이 변경사항 감지하고 마이그레이션 스크립트 생성
4. `alembic upgrade head`로 실제 DB에 적용

## 어떻게 테스트했나요?

1. **문법 검사**: Python 파일들의 구문 오류 확인
   ```bash
   python -m py_compile alembic/env.py  # 성공
   python -m py_compile src/models/base.py  # 성공
   ```

2. **임포트 테스트**: 모델 클래스가 제대로 불러와지는지 확인
   ```bash
   python -c "from src.models.base import Base; print('OK')"  # 성공
   ```

## 수정된 파일들

| 파일 | 변경 내용 |
|------|----------|
| `backend/alembic.ini` | 신규 - Alembic 메인 설정 |
| `backend/alembic/env.py` | 신규 - 마이그레이션 실행 환경 |
| `backend/alembic/script.py.mako` | 신규 - 마이그레이션 스크립트 템플릿 |
| `backend/alembic/README` | 신규 - 사용법 문서 |
| `backend/src/models/base.py` | 신규 - SQLAlchemy Base 클래스 및 공통 Mixin |
| `backend/src/models/__init__.py` | 수정 - Base 클래스 내보내기 |
| `backend/requirements.txt` | 수정 - psycopg2-binary 추가 |

## 관련 개념

- **ORM (Object-Relational Mapping)**: 파이썬 클래스를 DB 테이블로 자동 변환
- **마이그레이션**: DB 스키마 버전 관리 (Git처럼)
- **Mixin**: 여러 클래스에서 공통으로 쓰는 기능을 모아둔 것 (레고 블록처럼 조립)

## 주의사항

1. **동기 드라이버 필요**: Alembic은 `psycopg2`(동기)를 사용, 앱은 `asyncpg`(비동기) 사용
2. **환경변수 필수**: `.env` 파일에 `DATABASE_URL` 설정 필요
3. **모델 임포트**: 새 모델 생성 시 `src/models/__init__.py`에 추가해야 자동 감지됨

## 다음 단계

- **T009**: 초기 마이그레이션 생성 (data-model.md의 모든 테이블 스키마)
- **T010**: 데이터베이스 세션 관리 구현
- **T011**: 연결 풀 설정
