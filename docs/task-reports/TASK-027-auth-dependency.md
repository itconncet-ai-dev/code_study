# TASK-027: 인증 의존성 (Authentication Dependency) 구현

**작성일**: 2025-01-22
**상태**: 완료 ✅
**TDD 사이클**: RED → GREEN → REFACTOR 완료

## 무엇을 만들었나요?

API 라우트를 보호하기 위한 **인증 의존성(Authentication Dependency)**을 만들었습니다. 이것은 마치 건물의 출입문에 있는 보안 시스템과 같습니다. 방문자가 유효한 출입증(토큰)을 가지고 있는지 확인하고, 출입증이 있으면 그 사람이 누구인지 확인해서 건물 안으로 들여보내 줍니다.

## 왜 이렇게 만들었나요?

FastAPI에서는 "의존성 주입(Dependency Injection)"이라는 패턴을 사용합니다. 이것은 마치 레스토랑에서 웨이터가 손님의 예약 확인, 테이블 안내, 메뉴 전달을 순서대로 해주는 것과 비슷합니다. 우리의 인증 시스템도 다음과 같은 순서로 작동합니다:

1. **출입증 확인** (토큰 추출): HTTP 요청의 `Authorization` 헤더에서 Bearer 토큰을 가져옵니다.
2. **출입증 검증** (토큰 검증): TokenService를 사용해서 토큰이 유효한지, 만료되지 않았는지 확인합니다.
3. **신원 확인** (사용자 조회): 토큰에 들어있는 사용자 ID로 데이터베이스에서 실제 사용자를 찾습니다.

## 어떻게 작동하나요?

```python
# 보호된 라우트 사용 예시
@app.get("/me")
async def get_my_profile(current_user: User = Depends(require_auth)):
    return {"email": current_user.email}
```

위 코드에서 `require_auth`가 실행되면:
- 토큰이 없으면 → "인증이 필요합니다" 에러
- 토큰이 유효하지 않으면 → "유효하지 않은 토큰입니다" 에러
- 토큰이 만료되었으면 → "토큰이 만료되었습니다" 에러
- 모든 검증 통과 → 사용자 정보 반환

## 어떻게 테스트했나요? (TDD 사이클)

**🔴 RED 단계**: 먼저 13개의 테스트를 작성했습니다.
- 유효한 토큰으로 사용자 조회 테스트
- 잘못된 토큰 거부 테스트
- 만료된 토큰 거부 테스트
- 토큰 없을 때 에러 테스트
- 선택적 인증 (Optional Auth) 테스트

**🟢 GREEN 단계**: 테스트를 통과하는 최소한의 코드를 작성했습니다.

```
pytest tests/unit/test_dependencies.py -v
============================= 13 passed in 0.51s ==============================
```

## 수정된 파일들

| 파일 | 변경 내용 |
|------|----------|
| `backend/src/api/dependencies.py` | **신규 생성** - 인증 의존성 함수들 |
| `backend/tests/unit/test_dependencies.py` | **신규 생성** - 13개의 단위 테스트 |
| `backend/src/db/session.py` | import 경로 수정 |
| `backend/src/db/__init__.py` | import 경로 수정 |

## 관련 개념 설명

### OAuth2PasswordBearer
FastAPI에서 제공하는 보안 스키마입니다. HTTP 요청의 `Authorization: Bearer {token}` 헤더에서 토큰을 자동으로 추출해 줍니다. Swagger UI에서도 자동으로 인증 버튼이 생깁니다.

### 의존성 주입 (Dependency Injection)
함수가 필요로 하는 것(데이터베이스 연결, 현재 사용자 등)을 외부에서 주입받는 패턴입니다. 테스트하기 쉽고, 코드 재사용이 편리해집니다.

## 주의사항

- `get_current_user`는 인증 실패 시 예외를 발생시킵니다.
- `get_current_user_optional`은 인증 실패 시 `None`을 반환합니다 (공개/비공개 혼합 라우트용).
- 토큰 검증은 서명과 만료 시간을 모두 확인합니다.

## 다음 단계

이제 인증 의존성이 준비되었으니, 다음 태스크들을 진행할 수 있습니다:
- T028: POST /auth/register 엔드포인트 구현
- T029: POST /auth/login 엔드포인트 구현
- T029A: GET /auth/me 엔드포인트 구현 (현재 사용자 정보)
