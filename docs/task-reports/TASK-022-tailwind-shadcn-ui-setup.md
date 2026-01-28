# Task 022: Tailwind CSS 및 shadcn/ui 설정

**완료일**: 2025-01-20
**상태**: 완료

## 무엇을 만들었나요?

프론트엔드 프로젝트에 **Tailwind CSS**와 **shadcn/ui** 컴포넌트 라이브러리를 설정했습니다.

마치 집을 지을 때 먼저 기초 공사를 하는 것처럼, 이번 작업은 앱의 모든 화면을 꾸밀 수 있는 "스타일 기초 공사"를 한 것입니다.

## 왜 이렇게 만들었나요?

### Tailwind CSS를 선택한 이유
- **유틸리티 우선 방식**: CSS 클래스를 직접 HTML에 붙이면 됨 (마치 레고 블록처럼)
- **빠른 개발 속도**: 별도 CSS 파일 없이 컴포넌트 안에서 바로 스타일링
- **일관된 디자인 시스템**: 미리 정해진 색상, 간격, 크기를 사용

### shadcn/ui를 선택한 이유
- **복사해서 붙여넣기 방식**: 라이브러리 종속성 없이 코드를 직접 소유
- **커스터마이징 자유**: 모든 컴포넌트를 프로젝트에 맞게 수정 가능
- **Tailwind와 완벽 호환**: Tailwind CSS 기반으로 제작됨

### Tailwind v3을 선택한 이유
- v4는 아직 새로운 버전이라 shadcn/ui와의 호환성이 완벽하지 않음
- v3이 더 안정적이고 문서화가 잘 되어 있음

## 어떻게 작동하나요?

### 1. Tailwind CSS 동작 원리
```
코드 작성 → Tailwind가 사용된 클래스 분석 → 필요한 CSS만 생성
```
마치 필요한 재료만 골라서 요리하는 것처럼, 사용하는 스타일만 최종 결과물에 포함됩니다.

### 2. shadcn/ui 동작 원리
```
컴포넌트 필요 → components/ui/ 폴더에 추가 → 프로젝트에서 import
```
버튼, 카드, 입력창 등 미리 만들어진 부품을 가져다 쓰는 것과 같습니다.

### 3. CSS 변수 시스템
```css
:root {
  --primary: 222.2 47.4% 11.2%;  /* 기본 색상 */
  --background: 0 0% 100%;       /* 배경 색상 */
}
```
색상표를 한 곳에 정의해두면 전체 앱에서 일관되게 사용됩니다.

## 어떻게 테스트했나요?

### TDD 사이클

**RED (실패 테스트)**: 설정 전 빌드 시도 → Tailwind 오류 발생
**GREEN (통과)**: 설정 완료 후 빌드 성공
**REFACTOR (개선)**: ESLint 경고 수정

### 검증 항목
1. `npm run typecheck` - TypeScript 오류 없음 ✅
2. `npm run build` - 프로덕션 빌드 성공 ✅
3. `npm run lint` - ESLint 경고 없음 ✅

## 수정된 파일들

### 새로 생성된 파일
- [tailwind.config.ts](frontend/tailwind.config.ts) - Tailwind 설정
- [postcss.config.js](frontend/postcss.config.js) - PostCSS 설정
- [src/globals.css](frontend/src/globals.css) - 전역 스타일
- [src/lib/utils.ts](frontend/src/lib/utils.ts) - cn 유틸리티 함수
- [components.json](frontend/components.json) - shadcn/ui 설정
- [src/components/ui/button.tsx](frontend/src/components/ui/button.tsx) - 버튼 컴포넌트
- [src/components/ui/input.tsx](frontend/src/components/ui/input.tsx) - 입력 컴포넌트
- [src/components/ui/card.tsx](frontend/src/components/ui/card.tsx) - 카드 컴포넌트
- [src/components/ui/label.tsx](frontend/src/components/ui/label.tsx) - 라벨 컴포넌트

### 수정된 파일
- [vite.config.ts](frontend/vite.config.ts) - 경로 별칭 개선
- [src/main.tsx](frontend/src/main.tsx) - globals.css import 추가
- [package.json](frontend/package.json) - 의존성 추가

## 관련 개념 설명

### 유틸리티 CSS란?
전통적인 CSS는 "카드 컴포넌트"라는 이름의 스타일을 만들지만, Tailwind는 "둥근 모서리", "그림자", "패딩"처럼 작은 단위의 스타일을 조합합니다.

### CSS-in-JS vs Tailwind
CSS-in-JS는 JavaScript로 스타일을 작성하지만, Tailwind는 미리 만들어진 클래스를 조합합니다. 빌드 시간에 최적화되어 런타임 성능이 좋습니다.

## 주의사항

1. **다크 모드**: `.dark` 클래스 기반으로 작동하므로, 나중에 테마 토글 기능 구현 필요
2. **컴포넌트 추가**: 새 shadcn/ui 컴포넌트는 수동으로 추가해야 함
3. **Tailwind v3 유지**: v4로 업그레이드 시 설정 파일 대폭 수정 필요

## 다음 단계

- T023: User SQLAlchemy 모델 생성 (인증 시스템 시작)
- 추가 shadcn/ui 컴포넌트 필요시 설치 (Dialog, Dropdown, Toast 등)
