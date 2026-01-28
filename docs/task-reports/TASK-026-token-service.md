# T026: TokenService 구현

**작성일**: 2026-01-22
**태스크**: T026 - TokenService (토큰 생성, 검증, 갱신) 구현

## 무엇을 만들었나요?

TokenService는 사용자 인증을 위한 JWT 토큰을 관리하는 서비스입니다. 마치 놀이공원 입장권과 비슷하다고 생각하면 됩니다.

- **Access Token (접근 토큰)**: 짧은 시간(15분) 동안 유효한 "당일 입장권"입니다. API 요청 시 신분 확인용으로 사용됩니다.
- **Refresh Token (갱신 토큰)**: 7일간 유효한 "회원권"입니다. 당일 입장권이 만료되면 회원권을 보여주고 새 입장권을 받을 수 있습니다.

## 왜 이런 방식으로 만들었나요?

보안을 위해 두 종류의 토큰을 사용합니다:

1. **Access Token을 짧게 유지**: 만약 토큰이 탈취되더라도 15분 후 쓸모없어집니다
2. **Refresh Token은 DB에 저장**: SHA-256 해시로 저장해서 토큰 원본은 서버에 없습니다. 로그아웃 시 해당 토큰을 "폐기됨"으로 표시하여 재사용을 막습니다
3. **토큰 교체(Rotation)**: Refresh Token을 사용할 때마다 새 토큰을 발급하고 기존 토큰을 폐기합니다. 마치 은행에서 OTP 번호를 한 번만 쓸 수 있는 것처럼요

## 어떻게 동작하나요?

```python
# 로그인 성공 후 토큰 쌍 발급
access_token, refresh_token = await token_service.create_token_pair(user_id)

# API 요청 시 Access Token 검증
payload = token_service.verify_access_token(access_token)

# Access Token 만료 시 Refresh Token으로 갱신
new_access, new_refresh = await token_service.rotate_tokens(refresh_token)

# 로그아웃 시 토큰 폐기
await token_service.revoke_refresh_token(refresh_token)
```

## 어떻게 테스트했나요? (TDD)

1. **RED**: 먼저 25개의 테스트를 작성했습니다 - 모두 실패!
2. **GREEN**: TokenService를 구현하여 모든 테스트를 통과시켰습니다
3. **테스트 항목**: 토큰 생성, 검증, 만료 토큰 거부, DB 저장 확인, 토큰 갱신, 폐기 처리

## 수정한 파일들

| 파일 | 역할 |
|------|------|
| `backend/src/services/auth/token_service.py` | TokenService 구현 (신규) |
| `backend/src/services/auth/__init__.py` | TokenService 내보내기 추가 |
| `backend/tests/unit/test_token_service.py` | 단위 테스트 25개 (신규) |

## 관련 개념

- **JWT (JSON Web Token)**: 정보를 JSON 형태로 담아 서명한 토큰
- **SHA-256 해싱**: 원본 복원이 불가능한 단방향 암호화
- **Token Rotation**: 보안 강화를 위한 토큰 자동 교체 방식

## 주의사항

- Refresh Token은 반드시 HttpOnly 쿠키에 저장해야 합니다 (XSS 방지)
- 비밀번호 변경 시 `revoke_all_user_tokens()`로 모든 기기 로그아웃 처리 필요

## 다음 단계

- T027: 라우트 보호를 위한 인증 의존성(Dependency) 구현
- T028-T031: 인증 API 엔드포인트 구현
