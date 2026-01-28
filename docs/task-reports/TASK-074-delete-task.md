# Task 보고서: T074 - DELETE /tasks/{task_id} 엔드포인트 구현

## 작업 정보
- **작업 번호**: T074
- **작업 제목**: 태스크 삭제 (소프트 삭제) API 구현
- **담당자**: Backend TDD Implementation Specialist
- **작업 일자**: 2026-01-24
- **상태**: 완료

## 작업 개요
태스크를 휴지통으로 이동(소프트 삭제)하는 REST API 엔드포인트를 구현했습니다. 30일 보관 후 영구 삭제됩니다.

## API 스펙

### 엔드포인트
```
DELETE /api/v1/tasks/{task_id}
```

### 요청 파라미터
- **Path Parameters**
  - `task_id` (UUID, required): 태스크 ID

### 응답
**Status Code**: 204 No Content

**Response Body**: 없음 (빈 응답)

## 구현 내용

### 파일 경로
`backend/src/api/tasks.py` - `delete_task()` 함수

### 핵심 로직
```python
@router.delete("/{task_id}", ...)
async def delete_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    task_service = TaskService(db)
    await task_service.soft_delete(
        task_id=task_id,
        user_id=current_user.id,
    )
```

### 서비스 레이어 구현
```python
# TaskService.soft_delete()
async def soft_delete(
    self,
    task_id: UUID,
    user_id: UUID,
) -> None:
    # 태스크 조회 (소유권 검증 포함)
    task = await self.get_by_id(task_id, user_id)

    # 소프트 삭제 필드 설정
    now = datetime.now(timezone.utc)
    task.deletion_status = "trashed"
    task.trashed_at = now
    task.scheduled_deletion_at = now + timedelta(days=30)

    # 커밋
    await self.db.commit()
```

## 비즈니스 로직

### 1. 소프트 삭제 (Soft Delete)
물리적 삭제가 아닌 논리적 삭제:
- `deletion_status`: "active" → "trashed"
- `trashed_at`: 현재 시간 기록
- `scheduled_deletion_at`: 30일 후 시간 설정

### 2. 30일 보관 기간
```python
TRASH_RETENTION_DAYS = 30

scheduled_deletion_at = now + timedelta(days=TRASH_RETENTION_DAYS)
```
- 사용자는 30일 이내 복원 가능
- 30일 후 자동 영구 삭제 (백그라운드 작업)

### 3. 이미 삭제된 태스크
```python
# get_by_id()에서 필터링
if task.deletion_status == "trashed" and not include_trashed:
    raise NotFoundError(...)
```
- 이미 휴지통에 있는 태스크는 404 반환
- 중복 삭제 방지

### 4. 복원 기능 (향후 구현)
```python
# Task 모델에 정의된 메서드
def restore(self) -> None:
    self.deletion_status = "active"
    self.trashed_at = None
    self.scheduled_deletion_at = None
```

## HTTP 204 No Content

### 응답 특성
- 성공 시 응답 본문 없음
- Content-Length: 0
- 삭제 성공 확인은 상태 코드로만

### 클라이언트 처리
```javascript
const response = await fetch(`/api/v1/tasks/${taskId}`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

if (response.status === 204) {
  console.log('Task deleted successfully');
  // 캐시 무효화, UI 업데이트 등
}
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
태스크가 존재하지 않거나 이미 휴지통에 있음
```json
{
  "error": "not_found",
  "detail": "Task with ID 'xxx' not found"
}
```

## 연쇄 삭제 (Cascade)

### 데이터베이스 관계
```python
# Task 모델
uploaded_code: Mapped["UploadedCode | None"] = relationship(
    ...,
    cascade="all, delete-orphan"  # 연쇄 삭제
)

# UploadedCode 모델
code_files: Mapped[list["CodeFile"]] = relationship(
    ...,
    cascade="all, delete-orphan"  # 연쇄 삭제
)
```

### 소프트 삭제 시
- Task만 "trashed" 상태로 변경
- UploadedCode, CodeFile은 그대로 유지
- 복원 시 모든 데이터 복구 가능

### 영구 삭제 시 (30일 후)
```
Task (DELETE)
  ↓ cascade
UploadedCode (DELETE)
  ↓ cascade
CodeFile (DELETE)
```
- 관계된 모든 레코드 삭제
- 파일시스템의 파일도 삭제 필요 (향후 구현)

## 파일시스템 정리

### 현재 상태
파일은 삭제되지 않고 남아있음:
- `storage/uploads/{user_id}/{task_id}/`
- 디스크 공간 낭비 가능

### 향후 구현 필요
```python
# 영구 삭제 시 파일 정리
from src.services.code_analysis.file_storage import FileStorageService

async def permanent_delete(task: Task, user_id: UUID):
    # DB 삭제 전 파일 삭제
    await FileStorageService.delete_task_files(user_id, task.id)

    # DB 레코드 삭제
    await db.delete(task)
    await db.commit()
```

## 영구 삭제 자동화

### 백그라운드 작업 (향후 구현)
```python
# scheduled_tasks/cleanup.py
from datetime import datetime, timezone

async def cleanup_expired_tasks():
    """30일 지난 휴지통 항목 영구 삭제"""
    now = datetime.now(timezone.utc)

    # 삭제 대상 조회
    stmt = select(Task).where(
        Task.deletion_status == "trashed",
        Task.scheduled_deletion_at <= now
    )
    expired_tasks = await db.execute(stmt)

    for task in expired_tasks:
        # 파일 삭제
        await FileStorageService.delete_task_files(
            task.project.user_id,
            task.id
        )

        # 레코드 삭제
        await db.delete(task)

    await db.commit()
```

### 스케줄러 설정
```python
# Celery, APScheduler 등 사용
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(
    cleanup_expired_tasks,
    'cron',
    hour=2,  # 매일 새벽 2시
    minute=0
)
```

## 사용 예시

### cURL
```bash
curl -X DELETE \
  "https://api.example.com/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer {access_token}"
```

### JavaScript
```javascript
const deleteTask = async (taskId) => {
  const response = await fetch(`/api/v1/tasks/${taskId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });

  if (response.status !== 204) {
    throw new Error('Failed to delete task');
  }

  console.log('Task moved to trash');
};
```

### Python
```python
import httpx

response = httpx.delete(
    f"https://api.example.com/api/v1/tasks/{task_id}",
    headers={"Authorization": f"Bearer {access_token}"}
)

if response.status_code == 204:
    print("Task deleted successfully")
```

## 프론트엔드 활용

### React 예시
```typescript
// useDeleteTask hook
const useDeleteTask = () => {
  const queryClient = useQueryClient();

  return useMutation(
    (taskId: string) => api.delete(`/tasks/${taskId}`),
    {
      onSuccess: (_, taskId) => {
        // 캐시 무효화
        queryClient.invalidateQueries(['tasks']);

        // 성공 알림
        toast.success('Task moved to trash');
      },
      onError: (error) => {
        if (error.status === 404) {
          toast.error('Task not found or already deleted');
        } else if (error.status === 403) {
          toast.error('You do not have permission to delete this task');
        }
      }
    }
  );
};

// TaskActions.tsx
const TaskActions = ({ taskId }) => {
  const deleteTask = useDeleteTask();

  const handleDelete = async () => {
    const confirmed = await confirm(
      'Move this task to trash? You can restore it within 30 days.'
    );

    if (confirmed) {
      await deleteTask.mutateAsync(taskId);
    }
  };

  return (
    <button onClick={handleDelete}>
      Delete Task
    </button>
  );
};
```

### 확인 다이얼로그
```typescript
const DeleteConfirmDialog = ({ onConfirm }) => (
  <Dialog>
    <DialogTitle>Delete Task?</DialogTitle>
    <DialogContent>
      <p>This task will be moved to trash.</p>
      <p>You can restore it within 30 days.</p>
      <p>After 30 days, it will be permanently deleted.</p>
    </DialogContent>
    <DialogActions>
      <Button onClick={onCancel}>Cancel</Button>
      <Button onClick={onConfirm} color="error">
        Delete
      </Button>
    </DialogActions>
  </Dialog>
);
```

## 휴지통 UI

### 태스크 목록에서 필터링
```python
# include_trashed=false (기본값)
GET /projects/{id}/tasks
→ 활성 태스크만 반환

# include_trashed=true
GET /projects/{id}/tasks?include_trashed=true
→ 모든 태스크 반환 (휴지통 포함)
```

### 휴지통 페이지
```typescript
const TrashPage = () => {
  const { data: tasks } = useQuery(
    ['tasks', projectId, { trashed: true }],
    () => fetchTasks(projectId, { include_trashed: true })
  );

  const trashedTasks = tasks?.filter(
    task => task.deletion_status === 'trashed'
  );

  return (
    <div>
      <h1>Trash</h1>
      {trashedTasks.map(task => (
        <TaskCard
          key={task.id}
          task={task}
          actions={
            <>
              <RestoreButton taskId={task.id} />
              <PermanentDeleteButton taskId={task.id} />
            </>
          }
        />
      ))}
    </div>
  );
};
```

## 보안 고려사항

### 1. 소유권 검증
- get_by_id()에서 자동 검증
- 다른 사용자의 태스크 삭제 불가

### 2. 영구 삭제 방지
- 즉시 삭제가 아닌 휴지통 이동
- 실수로 삭제 시 복구 가능

### 3. 감사 로그
향후 구현 권장:
```python
AuditLog.create(
    entity_type="task",
    entity_id=task.id,
    action="soft_delete",
    user_id=current_user.id,
    metadata={
        "scheduled_deletion_at": task.scheduled_deletion_at.isoformat()
    }
)
```

## 테스트 필요사항
- [ ] 태스크 소유자의 정상 삭제
- [ ] deletion_status "trashed" 설정
- [ ] trashed_at 타임스탬프 기록
- [ ] scheduled_deletion_at 30일 후 설정
- [ ] 204 No Content 응답
- [ ] 다른 사용자 삭제 시 403 Forbidden
- [ ] 존재하지 않는 태스크 시 404 Not Found
- [ ] 이미 삭제된 태스크 재삭제 시 404 Not Found
- [ ] 인증 없이 요청 시 401 Unauthorized

## OpenAPI 문서

### 요약
"Delete task"

### 설명
"Soft delete task (move to trash with 30-day retention)"

### 태그
["Tasks"]

### 응답 예시
- 204: Task deleted successfully
- 401: Not authenticated
- 403: Access forbidden (not task owner)
- 404: Task not found

## DELETE vs 다른 HTTP 메서드

| 메서드 | 용도 | 멱등성 | 응답 본문 |
|--------|------|--------|-----------|
| DELETE | 삭제 | Yes | 없음 (204) |
| POST | 생성 | No | 생성된 리소스 (201) |
| PATCH | 부분 수정 | No | 수정된 리소스 (200) |
| PUT | 전체 교체 | Yes | 교체된 리소스 (200) |

### 멱등성 (Idempotency)
DELETE는 멱등적:
- 같은 요청을 여러 번 보내도 결과 동일
- 첫 번째: 204 No Content
- 두 번째 이후: 404 Not Found

## 완료 기준 충족
✅ DELETE /tasks/{task_id} 엔드포인트 구현
✅ 소프트 삭제 로직 (deletion_status="trashed")
✅ 30일 보관 기간 설정
✅ 소유권 검증
✅ 204 No Content 응답
✅ 적절한 HTTP 상태 코드
✅ 에러 처리 및 메시지
✅ OpenAPI 문서화
