# TASK-078: PasteCode 컴포넌트

**작업 유형**: 프론트엔드 UI 컴포넌트
**파일 위치**: `frontend/src/components/upload/PasteCode.tsx`
**완료일**: 2025-01-24

## 무엇을 만들었나요?

코드를 직접 붙여넣을 수 있는 텍스트 영역 컴포넌트입니다. ChatGPT나 GitHub에서 복사한 코드를 바로 붙여넣고, 프로그래밍 언어를 선택할 수 있습니다.

## 왜 이렇게 만들었나요?

AI가 생성한 코드는 대부분 채팅창이나 웹페이지에 텍스트로 표시됩니다. 이 코드를 파일로 저장했다가 다시 업로드하는 것은 번거롭습니다. 복사-붙여넣기가 가장 빠른 방법이므로 이 옵션을 제공합니다.

## 어떻게 동작하나요?

1. **언어 선택 드롭다운**: Python, JavaScript, TypeScript, Java, C++, C, HTML, CSS 중 선택
2. **코드 입력 영역**: 고정폭 폰트로 코드를 편하게 입력
3. **글자 수 카운터**: 현재 입력된 글자 수를 실시간 표시 (최대 10만 자)
4. **초기화 버튼**: 입력 내용을 한 번에 지우기

## 주요 기능

```tsx
const SUPPORTED_LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  // ...
]

const MAX_CODE_LENGTH = 100000  // 10만 자
```

- `onCodeChange`: 코드 내용 변경 시 부모 컴포넌트에 전달
- `onLanguageChange`: 언어 선택 변경 시 부모 컴포넌트에 전달
- `font-mono` 클래스로 코드 가독성 향상

## 수정한 파일

- `frontend/src/components/upload/PasteCode.tsx` (신규 생성)

## 관련 개념

- **고정폭 폰트(Monospace)**: 모든 문자가 같은 너비를 가져 코드 정렬이 깔끔함
- **Controlled Component**: React에서 입력값을 state로 관리하는 패턴
- **언어 감지**: 서버에서 Pygments 라이브러리로 자동 감지 (수동 선택은 보조)

## 주의사항

- 붙여넣기한 코드는 파일명이 없으므로 "pasted_code.{확장자}"로 저장
- 10만 자 초과 시 더 이상 입력 불가
- 줄바꿈과 들여쓰기는 그대로 유지됨

## 다음 단계

- 문법 강조(Syntax Highlighting) 추가
- 자동 언어 감지 기능
