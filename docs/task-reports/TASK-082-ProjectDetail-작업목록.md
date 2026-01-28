# TASK-082: ProjectDetail 페이지에 작업 목록 추가

**작업 유형**: 프론트엔드 페이지 업데이트
**파일 위치**: `frontend/src/pages/ProjectDetail.tsx`
**완료일**: 2025-01-24

## 무엇을 만들었나요?

프로젝트 상세 페이지에 작업 타임라인 섹션을 추가했습니다. 해당 프로젝트의 모든 작업이 카드 형태로 표시되고, "새 작업" 버튼으로 CreateTaskModal을 열 수 있습니다.

## 왜 이렇게 만들었나요?

프로젝트는 여러 작업(Task)의 모음입니다. 프로젝트 페이지에서 바로 작업 목록을 보고 새 작업을 만들 수 있어야 자연스러운 워크플로우가 됩니다.

## 어떻게 동작하나요?

1. **작업 목록 조회**: 페이지 로드 시 `taskService.getTasks()` 호출
2. **타임라인 표시**: TaskCard 컴포넌트로 각 작업 렌더링
3. **새 작업 버튼**: 클릭 시 CreateTaskModal 열기
4. **빈 상태**: 작업이 없으면 안내 메시지 표시
5. **로딩 상태**: 목록 조회 중 스피너 표시

## 주요 변경사항

```tsx
// 작업 목록 조회 쿼리 추가
const { data: tasksData, isLoading: isLoadingTasks } = useQuery({
  queryKey: ['projects', projectId, 'tasks'],
  queryFn: () => taskService.getTasks(projectId!),
  enabled: !!projectId,
})

// 모달 상태
const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
```

- 기존 "작업 관리 기능은 추후 구현될 예정입니다" 플레이스홀더 제거
- 실제 작업 목록과 생성 기능으로 대체

## 수정한 파일

- `frontend/src/pages/ProjectDetail.tsx` (업데이트)

## 관련 개념

- **타임라인 UI**: 시간 순으로 항목을 나열하는 패턴
- **TanStack Query**: 서버 상태 관리 및 캐싱 라이브러리
- **빈 상태(Empty State)**: 데이터가 없을 때 보여주는 안내 UI

## UI 구조

```
프로젝트 상세 페이지
├── 뒤로가기 링크
├── 프로젝트 정보 카드 (제목, 설명, 수정/삭제)
├── 작업 타임라인 카드
│   ├── 헤더 (제목 + "새 작업" 버튼)
│   └── 작업 목록 (TaskCard × N) 또는 빈 상태
└── CreateTaskModal (조건부 렌더링)
```

## 주의사항

- 프로젝트와 작업 목록은 별도 API로 조회 (병렬 요청)
- 작업 생성 후 `invalidateQueries`로 목록 자동 갱신

## 다음 단계

- 작업 드래그 앤 드롭 정렬 (Phase 2)
- 작업 필터링/검색 기능
