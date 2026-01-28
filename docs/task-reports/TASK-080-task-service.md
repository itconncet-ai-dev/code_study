# TASK-080: Task Service

**작업 유형**: 프론트엔드 서비스
**파일 위치**: `frontend/src/services/task-service.ts`
**완료일**: 2025-01-24

## 무엇을 만들었나요?

작업(Task) 관련 API를 호출하는 서비스 레이어입니다. 작업 목록 조회, 생성, 수정, 삭제 및 코드 업로드 기능을 제공합니다.

## 왜 이렇게 만들었나요?

API 호출 로직을 컴포넌트에서 분리하면 코드 재사용성이 높아지고 테스트가 쉬워집니다. 또한 `project-service.ts`와 동일한 패턴을 사용해 일관성을 유지했습니다.

## 어떻게 동작하나요?

1. **getTasks**: 프로젝트의 모든 작업 조회 (휴지통 포함 옵션)
2. **createTask**: 작업 생성 + 파일 업로드 (multipart/form-data)
3. **getTask**: 단일 작업 상세 조회
4. **updateTask**: 작업 제목/설명 수정
5. **deleteTask**: 작업 휴지통으로 이동 (30일 후 자동 삭제)
6. **getTaskCode**: 업로드된 코드 파일 조회

## 주요 기능

```typescript
async createTask(
  projectId: string,
  data: CreateTaskRequest,
  files?: File[],           // 파일/폴더 업로드 시
  codeContent?: string,     // 붙여넣기 시 코드 내용
  language?: string         // 붙여넣기 시 언어
): Promise<CreateTaskResponse>
```

- `uploadFiles` 함수로 FormData 전송
- 업로드 방식(file/folder/paste)에 따라 다른 데이터 첨부
- TypeScript 타입으로 API 응답 타입 안전성 보장

## 수정한 파일

- `frontend/src/services/task-service.ts` (신규 생성)
- `frontend/src/types/task.ts` (타입 정의 추가)

## 관련 개념

- **Service Layer**: UI와 API 사이의 중간 계층
- **FormData**: 파일 업로드에 사용하는 브라우저 API
- **multipart/form-data**: 파일을 포함한 폼 데이터 전송 형식

## API 엔드포인트

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | /projects/{id}/tasks | 작업 목록 |
| POST | /projects/{id}/tasks | 작업 생성 |
| GET | /tasks/{id} | 작업 상세 |
| PATCH | /tasks/{id} | 작업 수정 |
| DELETE | /tasks/{id} | 작업 삭제 |
| GET | /tasks/{id}/code | 코드 조회 |

## 주의사항

- 파일 업로드 시 10MB 제한은 서버에서 검사
- 휴지통에 있는 작업은 `includeTrashed=true`로 조회

## 다음 단계

- 업로드 진행률 표시 기능
- 작업 복원 API 연동 (휴지통에서 복원)
