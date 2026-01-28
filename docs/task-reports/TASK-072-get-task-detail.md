# Task 보고서: T072 - GET /tasks/{task_id} 엔드포인트 구현

## 작업 정보
- **작업 번호**: T072
- **작업 제목**: 태스크 상세 조회 API 구현
- **담당자**: Backend TDD Implementation Specialist
- **작업 일자**: 2026-01-24
- **상태**: 완료

## 작업 개요
특정 태스크의 상세 정보를 조회하는 REST API 엔드포인트를 구현했습니다.

## API 스펙

### 엔드포인트
```
GET /api/v1/tasks/{task_id}
```

### 요청 파라미터
- **Path Parameters**
  - `task_id` (UUID, required): 태스크 ID

### 응답
**Status Code**: 200 OK

**Response Body**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "650e8400-e29b-41d4-a716-446655440000",
  "task_number": 1,
  "title": "Calculator Implementation",
  "description": "Basic calculator with operations",
  "upload_method": "file",
  "created_at": "2025-01-20T10:30:00Z",
  "updated_at": "2025-01-20T15:45:00Z",
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
`backend/src/api/tasks.py` - `get_task()` 함수

### 핵심 로직
```python
@router.get("/{task_id}", ...)
async def get_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskDetailResponse:
    task_service = TaskService(db)
    task = await task_service.get_by_id(
        task_id=task_id,
        user_id=current_user.id,
    )

    return _task_to_detail_response(task)
```

### 데이터 변환
```python
def _task_to_detail_response(task) -> TaskDetailResponse:
    uploaded_code_summary = None
    if task.uploaded_code:
        uploaded_code_summary = {
            "detected_language": task.uploaded_code.detected_language,
            "complexity_level": task.uploaded_code.complexity_level,
            "total_lines": task.uploaded_code.total_lines,
            "total_files": task.uploaded_code.total_files,
            "upload_size_bytes": task.uploaded_code.upload_size_bytes,
        }

    return TaskDetailResponse(
        id=task.id,
        project_id=task.project_id,
        task_number=task.task_number,
        title=task.title,
        description=task.description,
        upload_method=task.upload_method,
        created_at=task.created_at,
        updated_at=task.updated_at,
        deletion_status=task.deletion_status,
        uploaded_code_summary=uploaded_code_summary,
    )
```

## 비즈니스 로직

### 1. 소유권 검증
- TaskService.get_by_id()에서 자동 처리
- 프로젝트 소유권을 통한 간접 검증
- 다른 사용자의 태스크 접근 차단

### 2. 코드 메타데이터 포함
- uploaded_code_summary 필드로 제공
- 파일 내용은 포함하지 않음 (별도 엔드포인트)
- 언어, 복잡도, 라인 수, 파일 수, 크기 정보

### 3. 휴지통 필터링
- 기본적으로 휴지통 항목 제외
- deletion_status="trashed" 시 404 반환
- 명시적으로 include_trashed 옵션 없음

## 응답 스키마

### TaskDetailResponse
```python
class TaskDetailResponse(BaseModel):
    id: UUID
    project_id: UUID
    task_number: int
    title: str
    description: str | None
    upload_method: str | None
    created_at: datetime
    updated_at: datetime
    deletion_status: str
    uploaded_code_summary: dict | None  # 코드 업로드 시에만 존재
```

### uploaded_code_summary 구조
```python
{
    "detected_language": str | None,      # 감지된 언어 (예: "Python")
    "complexity_level": str | None,       # 복잡도 (beginner/intermediate/advanced)
    "total_lines": int | None,            # 총 라인 수
    "total_files": int | None,            # 파일 개수
    "upload_size_bytes": int | None       # 총 크기 (바이트)
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
태스크 소유자가 아님 (프로젝트 소유자가 아님)
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
  "detail": "Task with ID 'xxx' not found",
  "resource": "task",
  "resource_id": "xxx"
}
```

## 인증 및 권한

### 인증 방식
```python
current_user: CurrentUser  # Depends(get_current_user)
```
- JWT Bearer 토큰 필수
- Authorization 헤더 또는 쿠키

### 권한 검증 흐름
```
1. get_task() 호출
   ↓
2. TaskService.get_by_id() 호출
   ↓
3. Task 조회
   ↓
4. ProjectService.validate_ownership() 호출
   ↓
5. Project 소유권 검증
   - user_id 일치 확인
   - 불일치 시 ForbiddenError
   ↓
6. Task 반환
```

## 성능 고려사항

### 1. 관계 로딩
```python
# Task 모델 설정
uploaded_code: Mapped["UploadedCode | None"] = relationship(
    ...,
    lazy="selectin",  # 즉시 로드
)
```
- selectin 로딩으로 N+1 쿼리 방지
- uploaded_code_summary 생성 시 추가 쿼리 없음

### 2. 단일 쿼리
```python
stmt = select(Task).where(Task.id == task_id)
result = await self.db.execute(stmt)
task = result.scalar_one_or_none()
```
- 태스크 및 관계 데이터를 한 번에 로드
- 프로젝트는 별도 쿼리 (소유권 검증용)

## 데이터 흐름

```
1. 클라이언트 요청
   - GET /tasks/{task_id}
   - Authorization 헤더 포함
   ↓
2. FastAPI 라우터
   - 경로 파라미터 파싱
   - JWT 토큰 검증
   ↓
3. TaskService.get_by_id()
   - DB에서 Task 조회
   - 프로젝트 소유권 검증
   - 휴지통 필터링
   ↓
4. _task_to_detail_response()
   - Task 모델 → TaskDetailResponse
   - uploaded_code_summary 생성
   ↓
5. JSON 응답 반환
```

## 사용 예시

### cURL
```bash
curl -X GET \
  "https://api.example.com/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer {access_token}"
```

### JavaScript
```javascript
const response = await fetch(`/api/v1/tasks/${taskId}`, {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const task = await response.json();
console.log('Language:', task.uploaded_code_summary?.detected_language);
console.log('Complexity:', task.uploaded_code_summary?.complexity_level);
```

### Python
```python
import httpx

response = httpx.get(
    f"https://api.example.com/api/v1/tasks/{task_id}",
    headers={"Authorization": f"Bearer {access_token}"}
)

task = response.json()
print(f"Task: {task['title']}")
print(f"Language: {task['uploaded_code_summary']['detected_language']}")
```

## 프론트엔드 활용

### 1. 태스크 상세 페이지
```typescript
// TaskDetailPage.tsx
const { data: task } = useQuery(['task', taskId], fetchTask);

return (
  <div>
    <h1>{task.title}</h1>
    <p>Task #{task.task_number}</p>
    <p>Created: {formatDate(task.created_at)}</p>

    {task.uploaded_code_summary && (
      <CodeSummary
        language={task.uploaded_code_summary.detected_language}
        complexity={task.uploaded_code_summary.complexity_level}
        lines={task.uploaded_code_summary.total_lines}
        files={task.uploaded_code_summary.total_files}
      />
    )}
  </div>
);
```

### 2. 코드 뱃지 표시
```typescript
// CodeBadge.tsx
const ComplexityBadge = ({ level }) => {
  const colors = {
    beginner: 'green',
    intermediate: 'yellow',
    advanced: 'red'
  };

  return (
    <Badge color={colors[level]}>
      {level.toUpperCase()}
    </Badge>
  );
};
```

## 테스트 필요사항
- [ ] 태스크 소유자의 정상 조회
- [ ] uploaded_code_summary 정확도
- [ ] 코드 업로드 없는 태스크 조회 (summary=null)
- [ ] 다른 사용자 접근 시 403 Forbidden
- [ ] 존재하지 않는 태스크 시 404 Not Found
- [ ] 휴지통 태스크 접근 시 404 Not Found
- [ ] 인증 없이 요청 시 401 Unauthorized
- [ ] 응답 스키마 검증

## OpenAPI 문서

### 요약
"Get task details"

### 설명
"Get detailed information about a specific task"

### 태그
["Tasks"]

### 응답 예시
- 200: Task retrieved successfully
- 401: Not authenticated
- 403: Access forbidden (not task owner)
- 404: Task not found

## GET vs POST 엔드포인트 비교

| 특성 | GET /tasks/{task_id} | POST /projects/{id}/tasks |
|------|----------------------|----------------------------|
| 목적 | 조회 | 생성 |
| 응답 | TaskDetailResponse | TaskDetailResponse |
| summary | 기존 데이터 | 새로 생성된 데이터 |
| 코드 파일 | 포함 안 됨 | 포함 안 됨 (메타만) |

## 완료 기준 충족
✅ GET /tasks/{task_id} 엔드포인트 구현
✅ TaskDetailResponse 스키마 정의
✅ uploaded_code_summary 포함
✅ 소유권 검증 (프로젝트 통한)
✅ 휴지통 필터링
✅ 적절한 HTTP 상태 코드
✅ 에러 처리 및 메시지
✅ OpenAPI 문서화
