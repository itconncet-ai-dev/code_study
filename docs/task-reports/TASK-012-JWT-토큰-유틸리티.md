# Task 012: JWT 토큰 유틸리티 구현

**완료일**: 2026-01-19
**파일 경로**: `backend/src/utils/jwt.py`
**테스트**: `backend/tests/unit/test_jwt.py`

## 무엇을 만들었나요?

JWT(JSON Web Token) 토큰을 생성하고, 검증하고, 해독하는 유틸리티 모듈을 만들었습니다.

이것은 사용자 인증 시스템의 핵심 부품입니다. 마치 놀이공원의 입장 팔찌와 같습니다 - 팔찌를 차면 놀이기구를 탈 수 있고, 팔찌가 없으면 탈 수 없죠. JWT 토큰이 바로 그 역할을 합니다.

## 왜 이렇게 만들었나요?

### 두 종류의 토큰

1. **Access Token (접근 토큰)**: 15분짜리 단기 패스
   - API 호출할 때마다 사용
   - 짧은 수명이라 털려도 피해가 적음

2. **Refresh Token (갱신 토큰)**: 7일짜리 장기 패스
   - Access Token이 만료되면 새로 발급받는 데 사용
   - 데이터베이스에 해시값으로 저장해서 필요하면 무효화 가능

이것은 마치 신용카드와 비슷합니다. 카드(Refresh Token)는 오래 쓰지만, 일회용 결제 비밀번호(Access Token)는 짧은 시간만 유효하죠.

### 환경 변수 기반 설정

```python
JWT_SECRET_KEY=비밀키  # 토큰 서명에 사용
JWT_ALGORITHM=HS256     # 서명 알고리즘
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15  # 접근 토큰 수명
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7     # 갱신 토큰 수명
```

개발 환경과 운영 환경에서 다른 값을 쓸 수 있도록 환경 변수로 설정합니다.

## 어떻게 동작하나요?

### 토큰 생성

```python
from backend.src.utils.jwt import create_access_token, create_refresh_token

# 사용자가 로그인하면
access_token = create_access_token(user_id="사용자-UUID")
refresh_token = create_refresh_token(user_id="사용자-UUID")
```

### 토큰 검증

```python
from backend.src.utils.jwt import verify_token, TokenExpiredError, TokenInvalidError

try:
    payload = verify_token(token)
    user_id = payload.sub  # 사용자 ID 추출
except TokenExpiredError:
    # 토큰 만료됨 - 갱신 필요
except TokenInvalidError:
    # 토큰이 조작됨 - 로그인 필요
```

### 토큰 해독 (만료 무시)

```python
from backend.src.utils.jwt import decode_token

# 만료된 토큰에서도 정보 추출 가능 (갱신 시 필요)
payload = decode_token(expired_token)
user_id = payload.sub
```

## 어떻게 테스트했나요? (TDD)

### RED 단계 (실패하는 테스트 작성)
31개의 테스트 케이스를 먼저 작성했습니다:
- 토큰 생성 테스트 8개
- 토큰 검증 테스트 9개
- 토큰 만료 테스트 5개
- 토큰 해독 테스트 4개
- 모델 및 열거형 테스트 5개

### GREEN 단계 (구현)
테스트를 통과시키는 최소한의 코드를 작성했습니다.

### REFACTOR 단계 (개선)
코드 가독성과 타입 힌트를 개선했습니다.

**테스트 결과**: 31개 모두 통과 (0.44초)

## 수정된 파일들

| 파일 | 변경 내용 |
|------|----------|
| `backend/src/utils/jwt.py` | JWT 유틸리티 모듈 생성 |
| `backend/src/utils/__init__.py` | 패키지 exports 추가 |
| `backend/tests/unit/test_jwt.py` | 단위 테스트 31개 작성 |

## 관련 개념

- **JWT**: JSON Web Token - URL-safe한 토큰 형식
- **HS256**: HMAC-SHA256 - 대칭키 서명 알고리즘
- **python-jose**: Python JWT 라이브러리
- **pydantic-settings**: 환경 변수 설정 관리

## 주의사항

1. **비밀키 관리**: `JWT_SECRET_KEY`는 절대 코드에 하드코딩하지 말 것
2. **토큰 저장**: Access Token은 메모리나 HTTP-only 쿠키에 저장
3. **Refresh Token 해시**: 데이터베이스에는 해시값만 저장 (T026에서 구현 예정)

## 다음 단계

- T013: 비밀번호 해싱 유틸리티 (bcrypt)
- T026: TokenService - Refresh Token 회전 및 폐기
- T027: 인증 의존성 - FastAPI 라우트 보호
