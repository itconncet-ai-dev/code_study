# Task 015: API 라우터 구조 생성

**작업 완료일**: 2025-01-20
**상태**: 완료

## 무엇을 만들었나요?

웹 API의 "교통 정리" 시스템을 만들었습니다. 마치 큰 백화점에서 각 층별로 안내 데스크가 있는 것처럼, API 요청이 들어오면 어느 부서(기능)로 보내야 할지 정리해주는 구조입니다.

`/api/v1`이라는 주소 아래에 8개의 영역을 구분했습니다:
- `/auth` - 로그인, 회원가입 담당
- `/projects` - 프로젝트 관리 담당
- `/tasks` - 학습 과제 관리 담당
- `/documents` - 학습 문서 조회 담당
- `/practice` - 연습 문제 담당
- `/qa` - 질문/답변 담당
- `/progress` - 학습 진도 담당
- `/trash` - 휴지통 관리 담당

## 왜 이렇게 만들었나요?

**버전 관리 용이성**: `/api/v1` 접두사를 사용하면 나중에 API를 업그레이드할 때 `/api/v2`를 새로 만들 수 있어서, 기존 사용자에게 영향을 주지 않고 변경할 수 있습니다.

**점진적 개발 지원**: 각 라우터가 아직 없으면 자동으로 건너뛰도록 `try/except` 구조를 사용했습니다. 덕분에 기능을 하나씩 순차적으로 개발할 수 있습니다.

**관심사 분리**: 각 기능별로 파일을 분리하면 코드가 깔끔해지고, 여러 사람이 동시에 다른 기능을 개발할 수 있습니다.

## 어떻게 동작하나요?

1. FastAPI 앱이 시작되면 `main.py`에서 `api_router`를 불러옵니다
2. `api_router`는 `/api/v1` 경로에 연결됩니다
3. `include_routers()` 함수가 각 하위 라우터를 찾아서 연결을 시도합니다
4. 아직 만들어지지 않은 라우터는 조용히 건너뜁니다
5. 이후 구현되는 라우터는 자동으로 API에 추가됩니다

## 테스트는 어떻게 했나요?

Python 인터프리터에서 직접 import 테스트를 수행했습니다:
```python
from backend.src.main import app
from backend.src.api import api_router
# 결과: "API router imported successfully"
# 현재 등록된 라우트: 0 (하위 라우터가 아직 없으므로 정상)
```

## 수정한 파일

| 파일 | 변경 내용 |
|------|----------|
| [backend/src/api/__init__.py](backend/src/api/__init__.py) | API 라우터 구조 전체 생성 |
| [backend/src/main.py:228-231](backend/src/main.py#L228-L231) | api_router를 /api/v1에 연결 |

## 관련 개념

- **라우터(Router)**: 웹 요청을 적절한 처리 함수로 연결해주는 역할. 교통 경찰과 비슷합니다.
- **API 버전 관리**: URL에 버전 번호를 포함시켜 하위 호환성을 유지하는 방법
- **관심사 분리(Separation of Concerns)**: 각 기능을 독립적인 모듈로 나누는 설계 원칙

## 주의할 점

- 새 라우터를 추가할 때는 `include_routers()` 함수에 해당 import 블록을 추가해야 합니다
- 라우터 모듈은 반드시 `router`라는 이름의 `APIRouter` 객체를 export해야 합니다
- prefix가 비어있는 라우터(`""`)는 상위 경로를 포함하여 전체 경로를 직접 정의해야 합니다

## 다음 단계

1. **T016**: 에러 처리 미들웨어 구현 (`backend/src/api/exceptions.py`)
2. **T017**: Celery 앱 및 Redis 연결 설정
3. **T028 이후**: 실제 API 엔드포인트(auth, projects 등) 구현
