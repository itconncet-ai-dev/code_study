# TASK-081: CreateTaskModal 컴포넌트

**작업 유형**: 프론트엔드 UI 컴포넌트
**파일 위치**: `frontend/src/components/task/CreateTaskModal.tsx`
**완료일**: 2025-01-24

## 무엇을 만들었나요?

새 작업을 만드는 모달 대화상자입니다. 작업 제목/설명 입력과 3가지 코드 업로드 방식(파일, 폴더, 붙여넣기)을 하나의 폼에서 처리합니다.

## 왜 이렇게 만들었나요?

작업 생성은 여러 입력 필드가 필요하지만 새 페이지로 이동하면 흐름이 끊깁니다. 모달을 사용하면 프로젝트 상세 페이지에서 바로 작업을 만들 수 있어 사용성이 좋습니다.

## 어떻게 동작하나요?

1. **제목 입력**: 필수, 최소 5자 이상
2. **설명 입력**: 선택, 최대 500자
3. **업로드 방식 탭**: 파일/폴더/붙여넣기 중 선택
4. **업로드 컴포넌트**: 선택에 따라 해당 컴포넌트 표시
5. **제출**: TaskService를 통해 API 호출
6. **성공 시**: 모달 닫고 작업 목록 자동 갱신

## 주요 기능

```tsx
// 업로드 방식 탭 전환
<button onClick={() => setUploadMethod('file')}>파일 업로드</button>
<button onClick={() => setUploadMethod('folder')}>폴더 업로드</button>
<button onClick={() => setUploadMethod('paste')}>코드 붙여넣기</button>

// 방식에 따른 컴포넌트 렌더링
{uploadMethod === 'file' && <FileUpload onFilesChange={setFiles} />}
{uploadMethod === 'folder' && <FolderUpload onFilesChange={setFiles} />}
{uploadMethod === 'paste' && <PasteCode onCodeChange={setCode} ... />}
```

- TanStack Query `useMutation`으로 API 호출 상태 관리
- `queryClient.invalidateQueries`로 성공 시 목록 자동 갱신
- 폼 유효성 검사 (제목 길이, 설명 길이)

## 수정한 파일

- `frontend/src/components/task/CreateTaskModal.tsx` (신규 생성)

## 관련 개념

- **모달 대화상자**: 배경을 어둡게 하고 포커스를 집중시키는 UI 패턴
- **탭 UI**: 같은 공간에서 다른 콘텐츠를 전환하는 패턴
- **폼 상태 관리**: 여러 입력값을 useState로 관리

## 주의사항

- 모달이 닫힐 때 모든 입력값 초기화
- 제출 중에는 버튼 비활성화 (중복 제출 방지)
- 스크롤 가능한 모달 (max-h-[90vh] overflow-y-auto)

## 다음 단계

- 업로드 진행률 바 표시
- 파일 미리보기 기능
- 드래프트 저장 기능
