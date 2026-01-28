# TASK-020: API 클라이언트 기본 설정

## 무엇을 만들었나요?

프론트엔드 애플리케이션이 백엔드 서버와 대화할 수 있는 "통신 도구"를 만들었습니다. 마치 전화기를 설치해서 외부와 연락할 수 있게 된 것처럼요.

이 도구는 `axios`라는 라이브러리를 기반으로 하며, 다음과 같은 기능을 갖추고 있습니다:

1. **자동 인증 처리**: 로그인 정보(쿠키)를 자동으로 포함해서 보냅니다
2. **토큰 자동 갱신**: 로그인 세션이 만료되면 자동으로 새로 갱신을 시도합니다
3. **에러 분류**: 발생한 에러가 어떤 종류인지 쉽게 파악할 수 있습니다

## 왜 이렇게 만들었나요?

### 중앙 집중식 관리

모든 API 호출이 한 곳(`api-client.ts`)을 통과하면 다음과 같은 장점이 있습니다:
- 인증 헤더를 매번 추가할 필요가 없음
- 에러 처리를 일관되게 할 수 있음
- 나중에 로깅이나 모니터링을 추가하기 쉬움

### HTTPOnly 쿠키 인증

JWT 토큰을 쿠키에 저장하는 방식을 사용합니다. `withCredentials: true` 설정으로 모든 요청에 쿠키가 자동 포함됩니다. 이렇게 하면 JavaScript에서 토큰에 접근할 수 없어서 보안이 강화됩니다.

### 토큰 자동 갱신 메커니즘

401 에러(인증 실패)가 발생하면:
1. 토큰 갱신 요청을 보냄
2. 갱신 성공 시 원래 요청을 재시도
3. 갱신 실패 시 로그아웃 처리 (auth-store에서 담당 예정)

여러 요청이 동시에 401을 받아도 토큰 갱신은 한 번만 수행됩니다.

## 어떻게 작동하나요?

```typescript
// GET 요청 예시
const user = await get<User>('/auth/me')

// POST 요청 예시
const project = await post<Project>('/projects', { title: '새 프로젝트' })

// 파일 업로드 예시
const formData = new FormData()
formData.append('file', file)
const result = await uploadFiles<Task>('/tasks', formData)
```

에러가 발생하면 `ApiClientError` 클래스로 감싸져서 반환됩니다:

```typescript
try {
  await get('/protected')
} catch (error) {
  if (error instanceof ApiClientError) {
    if (error.isUnauthorized()) {
      // 로그인 페이지로 이동
    } else if (error.isNotFound()) {
      // 404 처리
    }
  }
}
```

## 어떻게 테스트했나요?

TDD 방식을 따라 먼저 테스트를 작성했습니다:

1. **ApiClientError 클래스 테스트** (7개)
   - 에러 메시지 추출
   - 상태 코드별 분류 (401, 403, 404, 400, 5xx)

2. **API 클라이언트 설정 테스트** (3개)
   - 기본 URL 설정
   - Content-Type 헤더
   - 타임아웃 설정

3. **헬퍼 함수 테스트** (6개)
   - GET, POST, PATCH, PUT, DELETE 요청
   - 파일 업로드

4. **에러 핸들링 테스트** (1개)
   - ApiClientError로 변환 확인

총 17개의 테스트가 모두 통과했습니다.

## 수정된 파일

- `frontend/src/services/api-client.ts` (새로 생성)
- `frontend/src/services/api-client.test.ts` (새로 생성)
- `frontend/package.json` (axios 의존성 추가)

## 관련 개념

- **Axios Interceptors**: 요청/응답을 가로채서 처리하는 미들웨어 같은 개념
- **JWT (JSON Web Token)**: 사용자 인증 정보를 담은 토큰
- **HTTPOnly Cookie**: JavaScript에서 접근 불가능한 보안 쿠키

## 주의사항

- 토큰 갱신 실패 시 로그아웃 처리는 T021(auth-store)에서 구현 예정
- 환경 변수 `VITE_API_BASE_URL`로 API 주소 변경 가능
- 기본 타임아웃은 30초

## 다음 단계

- T021: Zustand auth store 설정 (토큰 갱신 실패 시 처리)
- T022: Tailwind CSS 및 shadcn/ui 설정
