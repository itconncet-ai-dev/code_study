# TASK-019: TanStack Query 설정

## 무엇을 만들었나요?

프론트엔드에서 서버 데이터를 쉽게 가져오고 관리할 수 있도록 TanStack Query(구 React Query)를 설정했습니다. 이것은 마치 음식점에서 주문을 관리하는 시스템과 같습니다. 손님이 음식을 주문하면, 주방에 전달하고, 음식이 나오면 손님에게 가져다주는 전 과정을 자동으로 관리해주는 것과 비슷합니다.

## 왜 이 방식을 선택했나요?

TanStack Query를 선택한 이유는:
- **자동 캐싱**: 한번 가져온 데이터를 저장해두어서 같은 정보를 다시 요청할 때 빠르게 보여줍니다. 마치 자주 가는 카페에서 단골 손님의 주문을 기억하는 것처럼요.
- **자동 재시도**: 인터넷이 잠깐 끊겼다가 다시 연결되면 자동으로 데이터를 다시 가져옵니다.
- **상태 관리 간소화**: 로딩 중, 에러, 성공 상태를 자동으로 관리해줍니다.

## 어떻게 동작하나요?

1. `queryClient.ts` 파일에서 TanStack Query의 기본 설정을 정의합니다
2. `main.tsx`에서 앱 전체를 `QueryClientProvider`로 감싸서 모든 컴포넌트에서 사용할 수 있게 합니다
3. 이제 어떤 페이지에서든 서버 데이터를 쉽게 가져올 수 있습니다

## 어떻게 테스트했나요? (TDD 사이클)

### 🔴 RED 단계
먼저 `queryClient.test.ts` 테스트 파일을 작성했습니다. 테스트가 실패하는 것을 확인했습니다 (파일이 없으니까요).

### 🟢 GREEN 단계
1. `@tanstack/react-query` 패키지를 설치했습니다
2. `queryClient.ts` 파일을 만들고 기본 설정을 추가했습니다
3. 테스트가 통과하는 것을 확인했습니다

### 🔵 REFACTOR 단계
`main.tsx`를 업데이트하여 QueryClientProvider를 추가하고, 기존 App 테스트도 새로운 Provider 구조에 맞게 수정했습니다.

## 수정한 파일들

- `frontend/src/lib/queryClient.ts` (새로 생성) - Query 클라이언트 설정
- `frontend/src/lib/queryClient.test.ts` (새로 생성) - 테스트 코드
- `frontend/src/main.tsx` (수정) - QueryClientProvider 추가
- `frontend/tests/unit/App.test.tsx` (수정) - Provider 래퍼 추가
- `frontend/package.json` (업데이트) - 의존성 추가

## 관련 개념

- **캐싱 (Caching)**: 자주 사용하는 데이터를 임시로 저장해두는 것
- **Provider 패턴**: React에서 여러 컴포넌트가 공유하는 데이터나 기능을 제공하는 방식
- **Stale Time**: 캐시된 데이터가 "오래됐다"고 판단하기까지의 시간 (현재 5분으로 설정)

## 주의할 점

- `staleTime`이 5분으로 설정되어 있어서, 5분 이내에 같은 데이터를 요청하면 서버에 다시 요청하지 않고 캐시된 데이터를 사용합니다
- `refetchOnWindowFocus`가 비활성화되어 있어서, 브라우저 탭을 전환해도 자동으로 데이터를 다시 가져오지 않습니다

## 다음 단계

- T020: Axios를 사용한 API 클라이언트 설정 (이것과 연동해서 실제 서버 요청을 처리하게 됩니다)
- T021: Zustand 인증 스토어 설정 (로그인 상태 관리)
