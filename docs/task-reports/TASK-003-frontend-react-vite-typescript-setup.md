# TASK-003: 프론트엔드 React + Vite + TypeScript 프로젝트 초기화

**완료일**: 2026-01-16
**상태**: 완료

## 무엇을 만들었나요?

프론트엔드 웹 애플리케이션의 기반을 만들었습니다. 마치 집을 짓기 전에 땅을 고르고 기초 공사를 하는 것과 같습니다. 이 기반 위에 앞으로 로그인 화면, 프로젝트 관리 화면, 코드 학습 문서 뷰어 등 모든 사용자 인터페이스가 만들어집니다.

## 왜 이 방식을 선택했나요?

**Vite를 선택한 이유**:
Vite는 개발할 때 변경 사항이 브라우저에 즉시 반영됩니다. 마치 요리할 때 간을 보면서 바로바로 조절하는 것처럼, 코드를 수정하면 결과를 바로 확인할 수 있어 개발 속도가 빨라집니다.

**React 18을 선택한 이유**:
React는 레고 블록처럼 작은 부품(컴포넌트)들을 조립해서 화면을 만드는 도구입니다. 로그인 버튼, 프로젝트 카드, 문서 뷰어 같은 부품들을 각각 만들어 조합하면 복잡한 화면도 쉽게 관리할 수 있습니다.

**TypeScript를 선택한 이유**:
TypeScript는 코드에 타입이라는 라벨을 붙이는 것입니다. 마치 서랍에 양말, 속옷, 티셔츠 라벨을 붙여두면 정리가 쉽듯이, 코드에서 어떤 데이터가 어디로 가는지 명확해져서 실수를 줄일 수 있습니다.

## 어떻게 작동하나요?

1. `npm run dev` 명령으로 개발 서버 시작 (http://localhost:3000)
2. `npm run build` 명령으로 배포용 파일 생성
3. `npm run test` 명령으로 테스트 실행

개발 서버는 백엔드 API 서버(http://localhost:8000)와 연동되도록 프록시 설정이 되어 있어, `/api/...` 주소로 요청하면 자동으로 백엔드로 전달됩니다.

## 어떻게 테스트했나요?

기본 테스트 파일(`tests/unit/App.test.tsx`)을 만들어 앱이 제대로 렌더링되는지 확인했습니다:
- 앱 제목이 화면에 표시되는지 확인
- 환영 메시지가 표시되는지 확인

Vitest 테스트 프레임워크를 사용했고, 모든 테스트가 통과했습니다.

## 어떤 파일들이 생성/수정되었나요?

**새로 생성된 파일**:
- `frontend/package.json` - 프로젝트 설정 및 의존성 목록
- `frontend/vite.config.ts` - Vite 빌드 도구 설정
- `frontend/vitest.config.ts` - 테스트 도구 설정
- `frontend/tsconfig.json` - TypeScript 설정
- `frontend/tsconfig.node.json` - Node.js용 TypeScript 설정
- `frontend/eslint.config.js` - 코드 품질 검사 설정
- `frontend/index.html` - HTML 진입점
- `frontend/src/main.tsx` - React 앱 시작점
- `frontend/src/App.tsx` - 메인 앱 컴포넌트
- `frontend/src/vite-env.d.ts` - Vite 타입 선언
- `frontend/src/test/setup.ts` - 테스트 환경 설정
- `frontend/tests/unit/App.test.tsx` - 기본 테스트
- `frontend/public/vite.svg` - 아이콘

## 관련 개념

- **번들러(Bundler)**: 여러 개의 파일을 하나로 묶어주는 도구. Vite가 이 역할을 합니다.
- **컴포넌트(Component)**: 재사용 가능한 UI 조각. 버튼, 입력창, 카드 등
- **JSX/TSX**: HTML처럼 생긴 JavaScript/TypeScript 코드

## 주의사항

- `node_modules/` 폴더는 427개의 패키지를 포함하며 용량이 큽니다. Git에 올리지 않습니다.
- 7개의 보안 취약점 경고가 있으나, 개발 의존성 관련이라 운영에는 영향 없습니다.
- `frontend/dist/` 폴더는 빌드 결과물이므로 Git에 올리지 않습니다.

## 다음 단계

- T004: Docker Compose로 PostgreSQL, Redis 설정
- T005: 환경 변수 템플릿 생성
- T006: 린팅 및 포맷팅 도구 설정 (ESLint, Prettier)
- T007: Git ignore 패턴 설정
