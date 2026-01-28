# TASK-077: FolderUpload 컴포넌트

**작업 유형**: 프론트엔드 UI 컴포넌트
**파일 위치**: `frontend/src/components/upload/FolderUpload.tsx`
**완료일**: 2025-01-24

## 무엇을 만들었나요?

전체 폴더를 선택해서 업로드하는 컴포넌트입니다. 프로젝트 폴더 전체를 업로드하면 폴더 구조(예: src/components/Button.tsx)가 그대로 유지됩니다.

## 왜 이렇게 만들었나요?

실제 프로젝트는 여러 파일과 폴더로 구성되어 있습니다. 파일을 하나씩 선택하는 것보다 폴더 전체를 한 번에 업로드하는 것이 훨씬 편리합니다. 또한 폴더 구조를 유지해야 코드 간의 관계(import 경로 등)를 이해할 수 있습니다.

## 어떻게 동작하나요?

1. **폴더 선택**: `webkitdirectory` 속성을 사용해 폴더 선택 대화상자 표시
2. **파일 필터링**: 지원하지 않는 확장자(.exe, .dll 등)는 자동으로 제외
3. **트리 구조 표시**: 선택한 폴더의 파일 구조를 트리 형태로 미리보기
4. **총 크기 검사**: 모든 파일의 합이 10MB 이하인지 확인

## 주요 기능

```tsx
interface FileNode {
  name: string      // 파일/폴더 이름
  path: string      // 전체 경로
  isDirectory: boolean
  children?: FileNode[]
  file?: File       // 실제 파일 객체
}
```

- `buildFileTree()`: 선택된 파일들을 트리 구조로 변환
- `webkitRelativePath`: 브라우저가 제공하는 상대 경로 정보 활용
- 필터링된 파일 개수 경고 표시

## 수정한 파일

- `frontend/src/components/upload/FolderUpload.tsx` (신규 생성)

## 관련 개념

- **webkitdirectory**: 폴더 선택을 가능하게 하는 비표준 HTML 속성 (Chrome, Edge 지원)
- **파일 트리**: 계층적 파일 구조를 표현하는 자료구조
- **재귀 렌더링**: 중첩된 구조를 화면에 그리는 기법

## 주의사항

- Safari에서는 폴더 선택이 제한될 수 있음
- 숨김 폴더(.git, node_modules)는 브라우저가 자동 제외
- 매우 큰 폴더(수천 개 파일)는 성능 저하 가능

## 다음 단계

- 파일 개수 제한 추가 (최대 20개)
- 대용량 폴더 경고 메시지
