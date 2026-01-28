# 태스크 018: React Router 라우트 구조 설정

## 무엇을 만들었나요?

웹 애플리케이션에서 여러 페이지 사이를 이동할 수 있게 해주는 **라우팅 시스템**을 설정했습니다. 마치 책의 목차처럼, 사용자가 원하는 페이지로 바로 이동할 수 있는 "길 안내 시스템"을 만든 것입니다.

## 왜 이렇게 만들었나요?

일반적인 웹사이트는 여러 페이지로 구성되어 있습니다. 로그인 페이지, 회원가입 페이지, 대시보드 등이 있죠. 하지만 React는 기본적으로 한 페이지만 보여주기 때문에, React Router라는 도구를 사용해서 "이 주소로 가면 이 화면을 보여줘"라고 설정해줘야 합니다.

비유하자면, 아파트 건물의 엘리베이터 버튼과 같습니다. 1층을 누르면 로비로, 5층을 누르면 사무실로 가는 것처럼, 각 URL 주소에 맞는 페이지를 연결해준 것입니다.

## 어떻게 작동하나요?

설정한 라우트 구조:

| URL 경로 | 보여주는 페이지 | 설명 |
|---------|---------------|------|
| `/login` | Login | 로그인 페이지 |
| `/register` | Register | 회원가입 페이지 |
| `/` | Dashboard | 프로젝트 목록 (메인 페이지) |
| `/projects/:projectId` | ProjectDetail | 프로젝트 상세 (태스크 타임라인) |
| `/tasks/:taskId` | TaskDetail | 태스크 상세 (문서/연습/Q&A) |
| `/trash` | Trash | 휴지통 (삭제된 항목) |
| `*` | NotFound | 404 에러 페이지 |

`:projectId`나 `:taskId`는 "동적 파라미터"라고 부르는데, 어떤 숫자든 올 수 있다는 의미입니다. 예를 들어 `/projects/123`으로 가면 123번 프로젝트를 보여줍니다.

## 어떻게 테스트했나요?

1. **패키지 설치 확인**: `npm install react-router-dom` 실행 후 정상 설치 확인
2. **TypeScript 컴파일 검증**: `npm run typecheck` 실행 - 타입 에러 없음 확인
3. **파일 생성 확인**: 7개 페이지 컴포넌트와 App.tsx 라우터 설정 완료

## 수정된 파일들

- `frontend/package.json` - react-router-dom 의존성 추가
- `frontend/src/App.tsx` - BrowserRouter와 Routes 설정
- `frontend/src/pages/Login.tsx` - 로그인 페이지 플레이스홀더
- `frontend/src/pages/Register.tsx` - 회원가입 페이지 플레이스홀더
- `frontend/src/pages/Dashboard.tsx` - 대시보드 페이지 플레이스홀더
- `frontend/src/pages/ProjectDetail.tsx` - 프로젝트 상세 페이지 플레이스홀더
- `frontend/src/pages/TaskDetail.tsx` - 태스크 상세 페이지 플레이스홀더
- `frontend/src/pages/Trash.tsx` - 휴지통 페이지 플레이스홀더
- `frontend/src/pages/NotFound.tsx` - 404 페이지

## 관련 개념

- **SPA (Single Page Application)**: 페이지 전환 없이 한 페이지 안에서 내용만 바뀌는 방식
- **클라이언트 사이드 라우팅**: 서버가 아닌 브라우저에서 페이지 전환을 처리
- **동적 라우트 파라미터**: URL의 일부를 변수처럼 사용하는 기능

## 주의사항

- 현재 모든 페이지는 플레이스홀더 상태입니다. 실제 UI는 후속 태스크에서 구현됩니다.
- 인증 보호(ProtectedRoute)는 T037에서 별도로 구현될 예정입니다.
- BrowserRouter 사용 시 서버 설정이 필요할 수 있습니다 (모든 경로에서 index.html 반환).

## 다음 단계

- T019: TanStack Query 클라이언트 설정
- T020: Axios API 클라이언트 설정
- T021: Zustand 인증 스토어 설정
- T022: Tailwind CSS 및 shadcn/ui 설정
