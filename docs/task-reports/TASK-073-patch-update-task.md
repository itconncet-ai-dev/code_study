# Task 보고서: T073 - PATCH /tasks/{task_id} 엔드포인트 구현

## 작업 정보
- **작업 번호**: T073
- **작업 제목**: 태스크 수정 API 구현
- **담당자**: Backend TDD Implementation Specialist
- **작업 일자**: 2026-01-24
- **상태**: 완료

## 작업 개요
태스크의 제목 및 설명을 수정하는 REST API 엔드포인트를 구현했습니다.

## API 스펙

### 엔드포인트
```
PATCH /api/v1/tasks/{task_id}
```

### 요청 파라미터

#### Path Parameters
- `task_id` (UUID, required): 태스크 ID

#### Request Body (JSON)
```json
{
  "title": "Updated Task Title",
  "description": "Updated task description"
}
```

**필드 설명**:
- `title` (string, optional): 새로운 제목 (최소 5자)
- `description` (string, optional): 새로운 설명 (최대 500자)

### 응답
**Status Code**: 200 OK

**Response Body**: TaskDetailResponse (T072와 동일)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "650e8400-e29b-41d4-a716-446655440000",
  "task_number": 1,
  "title": "Updated Task Title",
  "description": "Updated task description",
  "upload_method": "file",
  "created_at": "2025-01-20T10:30:00Z",
  "updated_at": "2025-01-20T16:00:00Z",
  "deletion_status": "active",
  "uploaded_code_summary": {
    "detected_language": "Python",
    "complexity_level": "beginner",
    "total_lines": 50,
    "total_files": 1,
    "upload_size_bytes": 1024
  }
}
```

## 구현 내용

### 파일 경로
`backend/src/api/tasks.py` - `update_task()` 함수

### 핵심 로직
```python
@router.patch("/{task_id}", ...)
async def update_task(
    task_id: UUID,
    request: UpdateTaskRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskDetailResponse:
    task_service = TaskService(db)
    task = await task_service.update(
        task_id=task_id,
        user_id=current_user.id,
        title=request.title,
        description=request.description,
    )

    return _task_to_detail_response(task)
```

### 요청 스키마
```python
class UpdateTaskRequest(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=5,
        description="New task title (optional, minimum 5 characters)",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="New task description (optional, max 500 characters)",
    )
```

## 비즈니스 로직

### 1. 부분 업데이트 (Partial Update)
- 모든 필드가 선택 사항
- 제공된 필드만 업데이트
- 빈 요청 본문도 허용 (변경 없음)

```python
# 제목만 업데이트
{"title": "New Title"}

# 설명만 업데이트
{"description": "New Description"}

# 둘 다 업데이트
{"title": "New Title", "description": "New Description"}

# 빈 요청 (변경 없음, 하지만 200 OK)
{}
```

### 2. 검증 로직
```python
# TaskService.update()
if title is not None:
    self._validate_title(title)  # 최소 5자 검증

if description is not None and len(description) > 500:
    raise ValidationError(...)  # 최대 500자 검증
```

### 3. 타임스탬프 자동 업데이트
```python
# TaskService.update()
task.updated_at = datetime.now(timezone.utc)
```
- 변경 사항이 있으면 updated_at 갱신
- created_at은 불변

### 4. 불변 필드
다음 필드들은 수정 불가:
- `id`: 고유 식별자
- `project_id`: 프로젝트 소속 변경 불가
- `task_number`: 순서 변경 불가 (FR-005)
- `upload_method`: 업로드 방식 변경 불가
- `created_at`: 생성 시간 불변
- `deletion_status`: 별도 엔드포인트 (DELETE)

## 서비스 레이어 구현

### TaskService.update()
```python
async def update(
    self,
    task_id: UUID,
    user_id: UUID,
    title: str | None = None,
    description: str | None = None,
) -> Task:
    # 검증
    if title is not None:
        self._validate_title(title)

    if description is not None and len(description) > 500:
        raise ValidationError(...)

    # 태스크 조회 (소유권 검증 포함)
    task = await self.get_by_id(task_id, user_id)

    # 업데이트
    if title is not None:
        task.title = title

    if description is not None:
        task.description = description

    # 타임스탬프 갱신
    task.updated_at = datetime.now(timezone.utc)

    # 커밋
    await self.db.commit()
    await self.db.refresh(task)

    return task
```

## 에러 응답

### 401 Unauthorized
인증되지 않은 요청
```json
{
  "error": "unauthorized",
  "detail": "Authentication required"
}
```

### 403 Forbidden
태스크 소유자가 아님
```json
{
  "error": "forbidden",
  "detail": "You do not have permission to access this project"
}
```

### 404 Not Found
태스크가 존재하지 않거나 휴지통에 있음
```json
{
  "error": "not_found",
  "detail": "Task with ID 'xxx' not found"
}
```

### 422 Validation Error
입력값 검증 실패
```json
{
  "error": "validation_error",
  "detail": "Title must be at least 5 characters",
  "field": "title"
}
```

**검증 실패 케이스**:
- title이 5자 미만
- description이 500자 초과
- title이 빈 문자열 또는 공백만 포함

## HTTP PATCH vs PUT

### PATCH (부분 업데이트)
현재 구현 방식:
- 제공된 필드만 업데이트
- 누락된 필드는 기존 값 유지
- RESTful 모범 사례

### PUT (전체 업데이트)
구현하지 않음:
- 모든 필드 필수
- 누락된 필드는 null 또는 기본값으로 설정
- 오버라이트 위험

## 사용 예시

### cURL - 제목만 업데이트
```bash
curl -X PATCH \
  "https://api.example.com/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Task Title"
  }'
```

### cURL - 설명만 업데이트
```bash
curl -X PATCH \
  "https://api.example.com/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description"
  }'
```

### JavaScript
```javascript
const updateTask = async (taskId, updates) => {
  const response = await fetch(`/api/v1/tasks/${taskId}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updates)
  });

  return await response.json();
};

// 사용
await updateTask(taskId, {
  title: 'New Title',
  description: 'New Description'
});
```

### Python
```python
import httpx

response = httpx.patch(
    f"https://api.example.com/api/v1/tasks/{task_id}",
    headers={"Authorization": f"Bearer {access_token}"},
    json={
        "title": "Updated Title",
        "description": "Updated Description"
    }
)

updated_task = response.json()
```

## 프론트엔드 활용

### React 예시
```typescript
// useUpdateTask hook
const useUpdateTask = () => {
  const queryClient = useQueryClient();

  return useMutation(
    ({ taskId, updates }: { taskId: string; updates: UpdateTaskRequest }) =>
      api.patch(`/tasks/${taskId}`, updates),
    {
      onSuccess: (updatedTask) => {
        // 캐시 무효화
        queryClient.invalidateQueries(['task', updatedTask.id]);
        queryClient.invalidateQueries(['tasks', updatedTask.project_id]);
      }
    }
  );
};

// TaskEditForm.tsx
const TaskEditForm = ({ task }) => {
  const updateTask = useUpdateTask();

  const handleSubmit = async (values) => {
    await updateTask.mutateAsync({
      taskId: task.id,
      updates: {
        title: values.title,
        description: values.description
      }
    });
  };

  return <form onSubmit={handleSubmit}>...</form>;
};
```

## 낙관적 업데이트 (Optimistic Update)
```typescript
const updateTask = useMutation(
  (updates) => api.patch(`/tasks/${taskId}`, updates),
  {
    onMutate: async (newData) => {
      // 캐시 업데이트 (낙관적)
      await queryClient.cancelQueries(['task', taskId]);
      const previousTask = queryClient.getQueryData(['task', taskId]);

      queryClient.setQueryData(['task', taskId], (old) => ({
        ...old,
        ...newData,
        updated_at: new Date().toISOString()
      }));

      return { previousTask };
    },
    onError: (err, newData, context) => {
      // 에러 시 롤백
      queryClient.setQueryData(['task', taskId], context.previousTask);
    }
  }
);
```

## 동시성 제어

### 현재 구현
- Last Write Wins 전략
- 타임스탬프 기반 변경 추적

### 향후 개선 고려사항
1. **낙관적 잠금 (Optimistic Locking)**
   ```python
   # version 필드 추가
   if task.version != request.version:
       raise ConflictError("Task has been modified")
   task.version += 1
   ```

2. **ETag 헤더**
   ```python
   @app.patch("/tasks/{task_id}")
   async def update_task(
       task_id: UUID,
       if_match: str = Header(None)  # ETag 검증
   ):
       ...
   ```

## 감사 로그 (Audit Trail)

### 향후 구현 권장
```python
# 변경 이력 기록
AuditLog.create(
    entity_type="task",
    entity_id=task.id,
    action="update",
    user_id=current_user.id,
    changes={
        "title": {"old": old_title, "new": new_title},
        "description": {"old": old_desc, "new": new_desc}
    }
)
```

## 테스트 필요사항
- [ ] 제목만 업데이트
- [ ] 설명만 업데이트
- [ ] 제목과 설명 동시 업데이트
- [ ] 빈 요청 본문 (변경 없음)
- [ ] title 5자 미만 시 422 에러
- [ ] description 500자 초과 시 422 에러
- [ ] 다른 사용자 수정 시 403 Forbidden
- [ ] 존재하지 않는 태스크 시 404 Not Found
- [ ] 휴지통 태스크 수정 시 404 Not Found
- [ ] updated_at 타임스탬프 갱신
- [ ] 불변 필드 (task_number, upload_method 등) 유지

## OpenAPI 문서

### 요약
"Update task"

### 설명
"Update task title and/or description"

### 태그
["Tasks"]

### 요청 예시
```json
{
  "title": "Updated Title",
  "description": "Updated Description"
}
```

### 응답 예시
- 200: Task updated successfully
- 401: Not authenticated
- 403: Access forbidden (not task owner)
- 404: Task not found
- 422: Validation error

## 완료 기준 충족
✅ PATCH /tasks/{task_id} 엔드포인트 구현
✅ UpdateTaskRequest 스키마 정의
✅ 부분 업데이트 지원
✅ 제목/설명 검증 (최소 5자, 최대 500자)
✅ 소유권 검증
✅ updated_at 자동 갱신
✅ 불변 필드 보호
✅ 적절한 HTTP 상태 코드
✅ 에러 처리 및 메시지
✅ OpenAPI 문서화
