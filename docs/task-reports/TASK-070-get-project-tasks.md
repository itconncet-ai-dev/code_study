# Task 보고서: T070 - GET /projects/{project_id}/tasks 엔드포인트 구현

## 작업 정보
- **작업 번호**: T070
- **작업 제목**: 프로젝트 태스크 목록 조회 API 구현
- **담당자**: Backend TDD Implementation Specialist
- **작업 일자**: 2026-01-24
- **상태**: 완료

## 작업 개요
프로젝트에 속한 모든 태스크를 순차적으로 조회하는 REST API 엔드포인트를 구현했습니다.

## API 스펙

### 엔드포인트
```
GET /api/v1/projects/{project_id}/tasks
```

### 요청 파라미터
- **Path Parameters**
  - `project_id` (UUID, required): 프로젝트 ID

- **Query Parameters**
  - `include_trashed` (boolean, optional): 휴지통 항목 포함 여부 (기본값: false)

### 응답
**Status Code**: 200 OK

**Response Body**:
```json
{
  "tasks": [
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
      "has_code": true
    }
  ],
  "total": 1
}
```

## 구현 내용

### 파일 경로
`backend/src/api/tasks.py` - `get_project_tasks()` 함수

### 핵심 로직
```python
@router.get("/{project_id}/tasks", ...)
async def get_project_tasks(
    project_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    include_trashed: bool = False,
) -> TaskListResponse:
    task_service = TaskService(db)
    tasks = await task_service.get_project_tasks(
        project_id=project_id,
        user_id=current_user.id,
        include_trashed=include_trashed,
    )

    task_responses = [_task_to_response(t) for t in tasks]

    return TaskListResponse(
        tasks=task_responses,
        total=len(task_responses),
    )
```

### 데이터 변환
```python
def _task_to_response(task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        task_number=task.task_number,
        title=task.title,
        description=task.description,
        upload_method=task.upload_method,
        created_at=task.created_at,
        updated_at=task.updated_at,
        deletion_status=task.deletion_status,
        has_code=task.uploaded_code is not None,
    )
```

## 비즈니스 로직

### 1. 순차 정렬
- task_number 오름차순 정렬
- 사용자가 생성한 순서대로 표시
- 불변하는 순서 보장

### 2. 소유권 검증
- TaskService에서 프로젝트 소유권 자동 확인
- 다른 사용자의 프로젝트 접근 차단
- ForbiddenError 반환

### 3. 휴지통 필터링
- 기본적으로 활성 태스크만 반환
- `include_trashed=true` 시 휴지통 항목 포함
- deletion_status 필드로 구분 가능

### 4. 코드 업로드 여부
- `has_code` 필드로 업로드 상태 표시
- uploaded_code 관계 존재 여부 확인
- 프론트엔드에서 UI 분기 처리용

## 응답 스키마

### TaskResponse
```python
class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    task_number: int
    title: str
    description: str | None
    upload_method: str | None
    created_at: datetime
    updated_at: datetime
    deletion_status: str
    has_code: bool  # uploaded_code 존재 여부
```

### TaskListResponse
```python
class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int  # 태스크 총 개수
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
프로젝트 소유자가 아님
```json
{
  "error": "forbidden",
  "detail": "You do not have permission to access this project"
}
```

### 404 Not Found
프로젝트가 존재하지 않음
```json
{
  "error": "not_found",
  "detail": "Project with ID 'xxx' not found"
}
```

## 인증 및 권한

### 인증 방식
```python
current_user: CurrentUser  # Depends(get_current_user)
```
- JWT Bearer 토큰 필수
- Authorization 헤더 또는 쿠키

### 권한 검증
- TaskService.get_project_tasks() 내부에서 검증
- ProjectService.validate_ownership() 호출
- 프로젝트 소유자만 접근 가능

## 성능 고려사항

### 1. 쿼리 최적화
```python
# TaskService.get_project_tasks()
stmt = select(Task).where(Task.project_id == project_id)
if not include_trashed:
    stmt = stmt.where(Task.deletion_status == "active")
stmt = stmt.order_by(Task.task_number.asc())
```
- 단일 쿼리로 모든 태스크 조회
- 인덱스 활용 (project_id, deletion_status)

### 2. 관계 로딩
```python
# Task 모델에서 설정
uploaded_code: Mapped["UploadedCode | None"] = relationship(
    ...,
    lazy="selectin",  # 즉시 로드
)
```
- has_code 판별을 위해 uploaded_code 로드
- N+1 쿼리 문제 방지

### 3. 페이지네이션
현재 미구현, 향후 추가 필요:
```python
# 향후 구현 예정
limit: int = 50,
offset: int = 0,
```

## 사용 예시

### 활성 태스크 조회
```bash
curl -X GET \
  "https://api.example.com/api/v1/projects/650e8400-e29b-41d4-a716-446655440000/tasks" \
  -H "Authorization: Bearer {access_token}"
```

### 휴지통 포함 조회
```bash
curl -X GET \
  "https://api.example.com/api/v1/projects/650e8400-e29b-41d4-a716-446655440000/tasks?include_trashed=true" \
  -H "Authorization: Bearer {access_token}"
```

## 테스트 필요사항
- [ ] 프로젝트 소유자의 정상 조회
- [ ] task_number 순서대로 정렬 확인
- [ ] 다른 사용자 접근 시 403 Forbidden
- [ ] 존재하지 않는 프로젝트 시 404 Not Found
- [ ] 인증 없이 요청 시 401 Unauthorized
- [ ] include_trashed=false 시 활성 태스크만 반환
- [ ] include_trashed=true 시 모든 태스크 반환
- [ ] has_code 필드 정확도

## OpenAPI 문서

### 요약
"List project tasks"

### 설명
"Get all tasks for a project in sequential order"

### 태그
["Tasks"]

### 응답 예시
Swagger UI에서 자동 생성되는 예시:
- 200: Tasks retrieved successfully
- 401: Not authenticated
- 403: Access forbidden (not project owner)
- 404: Project not found

## 완료 기준 충족
✅ GET /projects/{project_id}/tasks 엔드포인트 구현
✅ 순차 정렬 (task_number 오름차순)
✅ 프로젝트 소유권 검증
✅ 휴지통 필터링 옵션
✅ has_code 필드 추가
✅ 적절한 HTTP 상태 코드
✅ 에러 처리 및 메시지
✅ OpenAPI 문서화
