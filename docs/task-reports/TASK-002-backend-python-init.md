# Task 002: 백엔드 Python 프로젝트 초기화

**작업일**: 2026-01-16
**상태**: 완료

## 무엇을 만들었나요?

백엔드 서버를 만들기 위한 Python 프로젝트의 기초 설정을 완료했습니다. 마치 집을 짓기 전에 땅을 고르고, 설계도를 준비하고, 필요한 건축 자재 목록을 작성하는 것과 같은 작업이었습니다.

## 왜 이렇게 했나요?

Python과 FastAPI를 선택한 이유:
- **AI 친화적**: Python은 AI 도구들과 가장 잘 어울리는 언어입니다. 마치 요리사가 좋은 칼을 선택하듯, AI 기능을 만들기에 가장 적합한 도구입니다.
- **빠른 개발**: FastAPI는 현대적이고 빠른 웹 서버 프레임워크입니다. 자동으로 API 문서도 만들어주어 개발이 편리합니다.
- **안정적인 데이터 관리**: SQLAlchemy와 PostgreSQL 조합으로 사용자 데이터를 안전하게 저장할 수 있습니다.

## 어떻게 작동하나요?

1. **requirements.txt**: 프로젝트에 필요한 모든 라이브러리 목록입니다. `pip install -r requirements.txt` 명령어로 한 번에 설치할 수 있습니다.

2. **pyproject.toml**: 프로젝트 설정 파일입니다. 코드 스타일 규칙(Ruff, Black), 테스트 설정(pytest), 타입 검사(mypy) 등이 모두 포함되어 있습니다.

3. **패키지 구조**:
   - `src/api/` - API 엔드포인트
   - `src/models/` - 데이터 모델
   - `src/services/` - 비즈니스 로직
   - `src/db/` - 데이터베이스 연결
   - `src/tasks/` - 백그라운드 작업
   - `src/utils/` - 공용 유틸리티

## 어떻게 테스트했나요?

- 모든 디렉토리에 `__init__.py` 파일을 생성하여 Python 패키지로 인식되는지 확인
- 파일 구조가 plan.md의 설계와 일치하는지 검증
- requirements.txt와 pyproject.toml이 올바르게 생성되었는지 확인

## 수정된 파일

**새로 생성**:
- `backend/requirements.txt` - 의존성 목록
- `backend/pyproject.toml` - 프로젝트 설정
- `backend/src/__init__.py` - 메인 패키지
- `backend/src/api/__init__.py`
- `backend/src/db/__init__.py`
- `backend/src/models/__init__.py`
- `backend/src/services/__init__.py` (및 하위 디렉토리들)
- `backend/src/tasks/__init__.py`
- `backend/src/utils/__init__.py`
- `backend/tests/__init__.py` (및 하위 디렉토리들)
- `backend/tests/conftest.py` - pytest 설정

## 관련 개념

- **의존성 관리**: 프로젝트가 필요로 하는 외부 라이브러리들을 명시하고 관리하는 것
- **패키지 구조**: Python에서 코드를 논리적으로 구분하는 방법. `__init__.py` 파일이 있어야 패키지로 인식됩니다.
- **프로젝트 설정**: pyproject.toml은 Python 프로젝트의 현대적인 설정 방식으로, 빌드, 테스트, 린팅 등 모든 설정을 한 곳에 관리합니다.

## 주의사항

- Python 3.11 이상 버전이 필요합니다
- 가상환경(venv)을 사용하여 의존성을 격리하는 것을 권장합니다
- 실제 의존성 설치는 개발 환경 설정 단계에서 수행됩니다

## 다음 단계

- **T003**: 프론트엔드 React 프로젝트 초기화
- **T004**: Docker Compose로 PostgreSQL, Redis 설정
- **T005**: 환경 설정 템플릿(.env.example) 생성
