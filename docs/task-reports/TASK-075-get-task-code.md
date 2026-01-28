# Task 보고서: T075 - GET /tasks/{task_id}/code 엔드포인트 구현

## 작업 정보
- **작업 번호**: T075
- **작업 제목**: 업로드된 코드 조회 API 구현
- **담당자**: Backend TDD Implementation Specialist
- **작업 일자**: 2026-01-24
- **상태**: 완료

## 작업 개요
태스크에 업로드된 코드의 메타데이터와 파일 목록을 조회하는 REST API 엔드포인트를 구현했습니다.

## API 스펙

### 엔드포인트
```
GET /api/v1/tasks/{task_id}/code
```

### 요청 파라미터
- **Path Parameters**
  - `task_id` (UUID, required): 태스크 ID

### 응답
**Status Code**: 200 OK

**Response Body**:
```json
{
  "id": "750e8400-e29b-41d4-a716-446655440000",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "detected_language": "Python",
  "complexity_level": "beginner",
  "total_lines": 50,
  "total_files": 2,
  "upload_size_bytes": 2048,
  "created_at": "2025-01-20T10:30:00Z",
  "code_files": [
    {
      "id": "850e8400-e29b-41d4-a716-446655440000",
      "file_name": "main.py",
      "file_path": "main.py",
      "file_extension": ".py",
      "file_size_bytes": 1024,
      "mime_type": "text/x-python"
    },
    {
      "id": "950e8400-e29b-41d4-a716-446655440000",
      "file_name": "utils.py",
      "file_path": "src/utils.py",
      "file_extension": ".py",
      "file_size_bytes": 1024,
      "mime_type": "text/x-python"
    }
  ]
}
```

## 구현 내용

### 파일 경로
`backend/src/api/tasks.py` - `get_task_code()` 함수

### 핵심 로직
```python
@router.get("/{task_id}/code", ...)
async def get_task_code(
    task_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UploadedCodeResponse:
    task_service = TaskService(db)
    task = await task_service.get_by_id(
        task_id=task_id,
        user_id=current_user.id,
    )

    if task.uploaded_code is None:
        raise NotFoundError(
            detail=f"No uploaded code found for task '{task_id}'",
            resource="uploaded_code",
            resource_id=str(task_id),
        )

    return _uploaded_code_to_response(task.uploaded_code)
```

### 데이터 변환
```python
def _uploaded_code_to_response(uploaded_code) -> UploadedCodeResponse:
    code_files = [
        CodeFileResponse(
            id=cf.id,
            file_name=cf.file_name,
            file_path=cf.file_path,
            file_extension=cf.file_extension,
            file_size_bytes=cf.file_size_bytes,
            mime_type=cf.mime_type,
        )
        for cf in uploaded_code.code_files
    ]

    return UploadedCodeResponse(
        id=uploaded_code.id,
        task_id=uploaded_code.task_id,
        detected_language=uploaded_code.detected_language,
        complexity_level=uploaded_code.complexity_level,
        total_lines=uploaded_code.total_lines,
        total_files=uploaded_code.total_files,
        upload_size_bytes=uploaded_code.upload_size_bytes,
        created_at=uploaded_code.created_at,
        code_files=code_files,
    )
```

## 응답 스키마

### UploadedCodeResponse
```python
class UploadedCodeResponse(BaseModel):
    id: UUID                          # UploadedCode ID
    task_id: UUID                     # 부모 Task ID
    detected_language: str | None     # 감지된 언어
    complexity_level: str | None      # 복잡도 수준
    total_lines: int | None           # 총 라인 수
    total_files: int | None           # 파일 개수
    upload_size_bytes: int | None     # 총 크기
    created_at: datetime              # 업로드 시간
    code_files: list[CodeFileResponse]  # 파일 목록
```

### CodeFileResponse
```python
class CodeFileResponse(BaseModel):
    id: UUID                      # CodeFile ID
    file_name: str                # 파일명 (예: "main.py")
    file_path: str | None         # 상대 경로 (예: "src/main.py")
    file_extension: str | None    # 확장자 (예: ".py")
    file_size_bytes: int | None   # 파일 크기
    mime_type: str | None         # MIME 타입
```

## 반환되는 정보

### 1. 메타데이터
- **detected_language**: 감지된 프로그래밍 언어
  - 예: "Python", "JavaScript", "TypeScript"
  - LanguageDetector로 자동 감지

- **complexity_level**: 코드 복잡도 수준
  - "beginner": 초급 (0-35점)
  - "intermediate": 중급 (36-65점)
  - "advanced": 고급 (66-100점)
  - ComplexityAnalyzer로 분석

- **total_lines**: 총 라인 수
  - 모든 파일의 라인 수 합계
  - 빈 줄 포함

- **total_files**: 파일 개수
  - 1-20개 범위

- **upload_size_bytes**: 총 크기
  - 모든 파일 크기의 합
  - 바이트 단위 (최대 10MB)

### 2. 파일 목록
각 파일에 대해:
- **file_name**: 원본 파일명
- **file_path**: 폴더 업로드 시 상대 경로 보존
- **file_extension**: 확장자 (.py, .js 등)
- **file_size_bytes**: 개별 파일 크기
- **mime_type**: MIME 타입

### 3. 포함되지 않는 정보
- ❌ **파일 내용**: storage_path만 DB에 저장, 내용은 미포함
- ❌ **실제 코드**: 보안 및 성능상 이유로 별도 다운로드 엔드포인트 필요

## 비즈니스 로직

### 1. 코드 업로드 확인
```python
if task.uploaded_code is None:
    raise NotFoundError(
        detail=f"No uploaded code found for task '{task_id}'",
        resource="uploaded_code",
        resource_id=str(task_id),
    )
```
- 태스크는 존재하지만 코드가 없으면 404 반환
- 코드 업로드 전 태스크만 생성한 경우 발생 가능

### 2. 소유권 검증
- task_service.get_by_id()에서 자동 검증
- 프로젝트 소유권을 통한 간접 검증

### 3. 파일 순서
- DB에 저장된 순서대로 반환
- 특별한 정렬 없음
- 향후 file_path 기준 정렬 고려

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

### 404 Not Found - 태스크 없음
```json
{
  "error": "not_found",
  "detail": "Task with ID 'xxx' not found",
  "resource": "task",
  "resource_id": "xxx"
}
```

### 404 Not Found - 코드 없음
```json
{
  "error": "not_found",
  "detail": "No uploaded code found for task 'xxx'",
  "resource": "uploaded_code",
  "resource_id": "xxx"
}
```

## 사용 예시

### cURL
```bash
curl -X GET \
  "https://api.example.com/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000/code" \
  -H "Authorization: Bearer {access_token}"
```

### JavaScript
```javascript
const getTaskCode = async (taskId) => {
  const response = await fetch(`/api/v1/tasks/${taskId}/code`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });

  const uploadedCode = await response.json();

  console.log(`Language: ${uploadedCode.detected_language}`);
  console.log(`Complexity: ${uploadedCode.complexity_level}`);
  console.log(`Files: ${uploadedCode.total_files}`);

  uploadedCode.code_files.forEach(file => {
    console.log(`- ${file.file_name} (${file.file_size_bytes} bytes)`);
  });
};
```

### Python
```python
import httpx

response = httpx.get(
    f"https://api.example.com/api/v1/tasks/{task_id}/code",
    headers={"Authorization": f"Bearer {access_token}"}
)

uploaded_code = response.json()
print(f"Language: {uploaded_code['detected_language']}")
print(f"Files: {uploaded_code['total_files']}")
```

## 프론트엔드 활용

### React 예시
```typescript
// useTaskCode hook
const useTaskCode = (taskId: string) => {
  return useQuery(
    ['task-code', taskId],
    () => api.get(`/tasks/${taskId}/code`)
  );
};

// CodeSummary 컴포넌트
const CodeSummary = ({ taskId }) => {
  const { data: code, isLoading, error } = useTaskCode(taskId);

  if (isLoading) return <Spinner />;

  if (error?.status === 404) {
    return <EmptyState message="No code uploaded yet" />;
  }

  return (
    <div>
      <h2>Code Summary</h2>
      <div>
        <Badge>{code.detected_language}</Badge>
        <Badge color={getComplexityColor(code.complexity_level)}>
          {code.complexity_level}
        </Badge>
      </div>

      <Stats>
        <Stat label="Files" value={code.total_files} />
        <Stat label="Lines" value={code.total_lines} />
        <Stat label="Size" value={formatBytes(code.upload_size_bytes)} />
      </Stats>

      <h3>Files</h3>
      <FileList files={code.code_files} />
    </div>
  );
};
```

### 파일 목록 렌더링
```typescript
const FileList = ({ files }) => (
  <ul>
    {files.map(file => (
      <li key={file.id}>
        <FileIcon extension={file.file_extension} />
        <span>{file.file_path || file.file_name}</span>
        <span className="file-size">
          {formatBytes(file.file_size_bytes)}
        </span>
        <DownloadButton fileId={file.id} />
      </li>
    ))}
  </ul>
);
```

### 복잡도 뱃지 색상
```typescript
const getComplexityColor = (level: string) => {
  const colors = {
    beginner: 'green',
    intermediate: 'yellow',
    advanced: 'red'
  };
  return colors[level] || 'gray';
};
```

## 파일 다운로드 (향후 구현)

### 별도 엔드포인트 필요
```
GET /api/v1/code-files/{file_id}/download
```

**응답**:
```
Content-Type: text/x-python
Content-Disposition: attachment; filename="main.py"

[파일 내용]
```

**구현 예시**:
```python
from fastapi.responses import StreamingResponse

@router.get("/code-files/{file_id}/download")
async def download_code_file(
    file_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    # CodeFile 조회
    code_file = await db.get(CodeFile, file_id)

    # 소유권 검증 (UploadedCode → Task → Project → User)
    # ...

    # 파일 읽기
    content = await FileStorageService.read_file(code_file.storage_path)

    # 스트리밍 응답
    return StreamingResponse(
        io.BytesIO(content),
        media_type=code_file.mime_type,
        headers={
            "Content-Disposition": f"attachment; filename={code_file.file_name}"
        }
    )
```

## 성능 고려사항

### 1. 관계 로딩
```python
# UploadedCode 모델
code_files: Mapped[list["CodeFile"]] = relationship(
    ...,
    lazy="selectin"  # 즉시 로드
)
```
- N+1 쿼리 문제 방지
- 단일 쿼리로 모든 파일 정보 로드

### 2. 페이지네이션 (미구현)
현재는 모든 파일 반환:
- 최대 20개 제한 (FileValidator)
- 대부분 케이스에서 문제없음

향후 개선:
```python
code_files: list[CodeFileResponse] = Field(
    ...,
    description="List of code files (max 20)"
)
```

## 데이터베이스 쿼리

### 실행되는 쿼리
```sql
-- 1. Task 조회 (소유권 검증)
SELECT * FROM tasks WHERE id = ?;
SELECT * FROM projects WHERE id = ?;

-- 2. UploadedCode와 CodeFile 조회 (selectin)
SELECT * FROM uploaded_code WHERE task_id = ?;
SELECT * FROM code_files WHERE uploaded_code_id = ?;
```

### 최적화
- 인덱스: task_id, uploaded_code_id
- selectin 로딩으로 쿼리 수 최소화

## 테스트 필요사항
- [ ] 코드가 있는 태스크 정상 조회
- [ ] 모든 필드 정확도 확인
- [ ] code_files 배열 정확도
- [ ] 코드가 없는 태스크 시 404 Not Found
- [ ] 다른 사용자 접근 시 403 Forbidden
- [ ] 존재하지 않는 태스크 시 404 Not Found
- [ ] 인증 없이 요청 시 401 Unauthorized
- [ ] 응답 스키마 검증

## OpenAPI 문서

### 요약
"Get uploaded code"

### 설명
"Get uploaded code with file details"

### 태그
["Tasks"]

### 응답 예시
- 200: Uploaded code retrieved successfully
- 401: Not authenticated
- 403: Access forbidden (not task owner)
- 404: Task or uploaded code not found

## API 엔드포인트 구조

### 태스크 관련 엔드포인트
```
GET    /projects/{id}/tasks       # 태스크 목록
POST   /projects/{id}/tasks       # 태스크 생성 + 코드 업로드
GET    /tasks/{id}                # 태스크 상세
PATCH  /tasks/{id}                # 태스크 수정
DELETE /tasks/{id}                # 태스크 삭제
GET    /tasks/{id}/code           # 업로드된 코드 조회 ← 현재 구현
```

### 리소스 중첩 (Nested Resources)
```
/tasks/{task_id}/code             # 코드 메타데이터
/tasks/{task_id}/document         # 학습 문서 (향후)
/tasks/{task_id}/practice         # 연습 문제 (향후)
/tasks/{task_id}/questions        # 질문 (향후)
```

## 완료 기준 충족
✅ GET /tasks/{task_id}/code 엔드포인트 구현
✅ UploadedCodeResponse 스키마 정의
✅ CodeFileResponse 스키마 정의
✅ 코드 메타데이터 반환 (언어, 복잡도, 라인, 파일 수, 크기)
✅ 파일 목록 반환 (파일명, 경로, 확장자, 크기, MIME)
✅ 코드 미업로드 시 404 처리
✅ 소유권 검증
✅ 적절한 HTTP 상태 코드
✅ 에러 처리 및 메시지
✅ OpenAPI 문서화
