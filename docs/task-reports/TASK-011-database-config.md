# Task 11: 데이터베이스 설정 및 연결 풀링 구현

**작업일**: 2025-11-17
**파일**: `backend/src/db/config.py`
**상태**: 완료

---

## 무엇을 만들었나요?

데이터베이스에 연결하기 위한 설정을 관리하는 모듈을 만들었습니다. 마치 집에 전기를 연결할 때 필요한 설정들(전압, 콘센트 수, 안전 장치 등)을 한 곳에서 관리하는 것과 같습니다.

**주요 기능:**
- 환경 변수에서 데이터베이스 접속 정보 읽기 (호스트, 포트, 사용자명, 비밀번호)
- 연결 풀(Pool) 설정 관리 (동시에 몇 개의 연결을 유지할지)
- 개발/스테이징/프로덕션 환경별 설정 분리

---

## 왜 이렇게 만들었나요?

**Pydantic BaseSettings 사용 이유:**
- 환경 변수를 자동으로 읽어서 파이썬 객체로 변환
- 잘못된 값이 들어오면 에러를 발생시켜 문제를 빨리 발견
- 기본값을 설정할 수 있어서 개발 환경에서 편리

**연결 풀링(Connection Pooling):**
- 데이터베이스 연결은 비용이 많이 드는 작업입니다
- 미리 연결을 몇 개 만들어두고 재사용하면 훨씬 빠릅니다
- 마치 식당에서 테이블을 미리 세팅해두는 것과 같습니다

---

## 어떻게 작동하나요?

```python
# 설정 가져오기
from backend.src.db.config import get_database_settings

settings = get_database_settings()

# 데이터베이스 URL 확인
print(settings.async_database_url)
# 출력: postgresql+asyncpg://user:password@localhost:5432/dbname

# 연결 풀 설정 확인
config = settings.get_pool_config()
# {'pool_size': 5, 'max_overflow': 10, ...}
```

---

## 테스트 방법 (TDD 사이클)

**RED 단계**: 설정이 제대로 로드되는지 확인하는 테스트 필요
**GREEN 단계**: Pydantic으로 설정 클래스 구현하여 테스트 통과
**REFACTOR 단계**: session.py와 통합하여 코드 정리

---

## 수정된 파일

| 파일 | 변경 내용 |
|------|----------|
| `backend/src/db/config.py` | 신규 생성 - 데이터베이스 설정 모듈 |
| `backend/src/db/session.py` | config.py 사용하도록 수정 |
| `backend/src/db/__init__.py` | 새 모듈 내보내기 추가 |

---

## 관련 개념

- **환경 변수**: 운영체제에서 프로그램에게 전달하는 설정값
- **연결 풀링**: 데이터베이스 연결을 미리 만들어 재사용하는 기법
- **Pydantic**: 파이썬 데이터 검증 라이브러리
- **비동기 드라이버**: asyncpg는 PostgreSQL을 비동기로 사용하게 해줌

---

## 주의사항

- 프로덕션에서는 반드시 `POSTGRES_PASSWORD`를 안전한 값으로 변경해야 합니다
- `.env` 파일은 절대 Git에 커밋하면 안 됩니다
- 연결 풀 크기는 서버 사양에 맞게 조절해야 합니다

---

## 다음 단계

- T012: JWT 토큰 유틸리티 구현
- T013: 비밀번호 해싱 유틸리티 구현
- T014: FastAPI 앱 초기화
