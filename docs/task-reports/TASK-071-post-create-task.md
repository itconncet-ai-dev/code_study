# Task 보고서: T071 - POST /projects/{project_id}/tasks 엔드포인트 구현

## 작업 정보
- **작업 번호**: T071
- **작업 제목**: 태스크 생성 및 코드 업로드 API 구현
- **담당자**: Backend TDD Implementation Specialist
- **작업 일자**: 2026-01-24
- **상태**: 완료

## 작업 개요
태스크 생성과 코드 업로드를 동시에 처리하는 multipart/form-data API 엔드포인트를 구현했습니다.

## API 스펙

### 엔드포인트
```
POST /api/v1/projects/{project_id}/tasks
```

### 요청 형식
**Content-Type**: `multipart/form-data`

### 요청 파라미터

#### Path Parameters
- `project_id` (UUID, required): 프로젝트 ID

#### Form Data Fields
- `title` (string, required): 태스크 제목 (최소 5자, 최대 255자)
- `upload_method` (string, required): 업로드 방식 ("file", "folder", "paste")
- `files` (array[file], optional): 파일 배열 (file/folder 방식용)
- `code_text` (string, optional): 코드 텍스트 (paste 방식용)
- `language` (string, optional): 언어 힌트 (paste 방식용, 예: "python")
- `description` (string, optional): 태스크 설명 (최대 500자)

### 응답
**Status Code**: 201 Created

**Response Body**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "650e8400-e29b-41d4-a716-446655440000",
  "task_number": 1,
  "title": "Calculator Implementation",
  "description": "Basic calculator",
  "upload_method": "file",
  "created_at": "2025-01-20T10:30:00Z",
  "updated_at": "2025-01-20T10:30:00Z",
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
`backend/src/api/tasks.py` - `create_task()` 함수

### 핵심 로직
```python
@router.post("/{project_id}/tasks", ...)
async def create_task(
    project_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    title: Annotated[str, Form(min_length=5, max_length=255)],
    upload_method: Annotated[str, Form()],
    files: list[UploadFile] | None = File(default=None),
    code_text: Annotated[str | None, Form()] = None,
    language: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form(max_length=500)] = None,
) -> TaskDetailResponse:
    # 1. upload_method 검증
    if upload_method not in ["file", "folder", "paste"]:
        raise ValidationError(...)

    # 2. 태스크 생성
    task = await task_service.create(
        project_id=project_id,
        user_id=current_user.id,
        title=title,
        upload_method=upload_method,
        description=description,
    )

    # 3. 코드 업로드 처리
    upload_service = CodeUploadService(db)

    if upload_method in ["file", "folder"]:
        # 파일 업로드
        if not files or len(files) == 0:
            raise ValidationError(...)

        file_data = []
        for file in files:
            content = await file.read()
            file_data.append((file.filename, content))

        if upload_method == "file":
            await upload_service.handle_file_upload(...)
        else:
            await upload_service.handle_folder_upload(...)

    else:  # paste
        # 붙여넣기 업로드
        if not code_text:
            raise ValidationError(...)

        await upload_service.handle_paste_upload(...)

    # 4. 관계 데이터 로드 및 반환
    await db.refresh(task)
    return _task_to_detail_response(task)
```

## 업로드 방식별 처리

### 1. File Upload (upload_method="file")
**요청 예시**:
```bash
curl -X POST \
  "https://api.example.com/api/v1/projects/{project_id}/tasks" \
  -H "Authorization: Bearer {token}" \
  -F "title=Calculator App" \
  -F "upload_method=file" \
  -F "files=@main.py" \
  -F "files=@utils.py"
```

**처리 과정**:
1. 각 파일 읽기 (UploadFile.read())
2. 파일 검증 (확장자, 크기, 바이너리)
3. 언어 감지 (첫 번째 파일 기준)
4. 복잡도 분석
5. 파일 저장 및 DB 기록

### 2. Folder Upload (upload_method="folder")
**요청 예시**:
```bash
curl -X POST \
  "https://api.example.com/api/v1/projects/{project_id}/tasks" \
  -H "Authorization: Bearer {token}" \
  -F "title=Web Project" \
  -F "upload_method=folder" \
  -F "files=@src/main.js" \
  -F "files=@src/utils.js" \
  -F "files=@public/index.html"
```

**처리 과정**:
1. 파일 읽기 (경로 정보 포함)
2. 상대 경로 보존 (CodeFile.file_path)
3. 나머지는 file 방식과 동일

### 3. Paste Upload (upload_method="paste")
**요청 예시**:
```bash
curl -X POST \
  "https://api.example.com/api/v1/projects/{project_id}/tasks" \
  -H "Authorization: Bearer {token}" \
  -F "title=Quick Script" \
  -F "upload_method=paste" \
  -F "code_text=print('Hello, World!')" \
  -F "language=python"
```

**처리 과정**:
1. 코드 텍스트 검증 (비어있지 않은지)
2. 언어 감지 (힌트 또는 콘텐츠 분석)
3. 가상 파일 생성 (pasted_code.py)
4. 복잡도 분석
5. 파일 저장 및 DB 기록

## 데이터 흐름

```
1. FastAPI 요청 수신
   ↓
2. Form 데이터 파싱 및 검증
   ↓
3. TaskService.create()
   - 프로젝트 소유권 검증
   - task_number 자동 증가
   - Task 레코드 생성
   ↓
4. CodeUploadService.handle_*_upload()
   - 파일 검증 (FileValidator)
   - 언어 감지 (LanguageDetector)
   - 복잡도 분석 (ComplexityAnalyzer)
   - 파일 저장 (FileStorageService)
   - UploadedCode 및 CodeFile 생성
   ↓
5. TaskDetailResponse 반환
   - uploaded_code_summary 포함
```

## 검증 로직

### 1. 필수 필드 검증
```python
title: Annotated[str, Form(min_length=5, max_length=255)]
```
- FastAPI Annotated로 자동 검증
- 422 Unprocessable Entity 반환

### 2. upload_method 검증
```python
if upload_method not in ["file", "folder", "paste"]:
    raise ValidationError(
        detail="Upload method must be 'file', 'folder', or 'paste'",
        field="upload_method",
    )
```

### 3. 조건부 필드 검증
```python
# file/folder 방식: files 필수
if upload_method in ["file", "folder"]:
    if not files or len(files) == 0:
        raise ValidationError(
            detail="At least one file is required for file/folder upload",
            field="files",
        )

# paste 방식: code_text 필수
else:
    if not code_text:
        raise ValidationError(
            detail="code_text is required for paste upload method",
            field="code_text",
        )
```

### 4. 파일 크기 검증
- 총 업로드 크기 10MB 제한
- FileValidator에서 자동 검증
- 413 Payload Too Large 반환 (OpenAPI 문서화)

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
    uploaded_code_summary: dict | None  # 코드 메타데이터
```

### uploaded_code_summary 구조
```python
{
    "detected_language": "Python",
    "complexity_level": "beginner",
    "total_lines": 50,
    "total_files": 1,
    "upload_size_bytes": 1024
}
```

## 에러 응답

### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "detail": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "forbidden",
  "detail": "You do not have permission to access this project"
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "detail": "Project with ID 'xxx' not found"
}
```

### 413 Payload Too Large
```json
{
  "error": "validation_error",
  "detail": "Total upload size 12.5MB exceeds maximum allowed 10MB",
  "field": "files"
}
```

### 422 Validation Error
```json
{
  "error": "validation_error",
  "detail": "Title must be at least 5 characters",
  "field": "title"
}
```

## 트랜잭션 처리

### 원자성 보장
```python
# 태스크 생성
task = await task_service.create(...)  # commit 포함

# 코드 업로드
await upload_service.handle_file_upload(...)  # commit 포함
```

**참고**: 현재는 두 개의 별도 트랜잭션
- 향후 개선: 단일 트랜잭션으로 통합 필요
- 실패 시 롤백 전략 수립 필요

## 성능 고려사항

### 1. 파일 읽기
```python
for file in files:
    content = await file.read()  # 비동기 I/O
```
- 비동기 읽기로 블로킹 방지
- 대용량 파일 시 메모리 이슈 가능 (향후 스트리밍 개선)

### 2. 병렬 처리
현재는 순차 처리:
1. 태스크 생성
2. 파일 검증
3. 언어 감지
4. 복잡도 분석
5. 파일 저장

향후 개선: 독립적인 작업 병렬화

### 3. 데이터베이스
- 관계 로딩 최적화 (selectin)
- 인덱스 활용 (project_id, task_number)

## 보안 고려사항

### 1. 인증 및 권한
- JWT 토큰 필수
- 프로젝트 소유권 검증

### 2. 파일 검증
- 확장자 화이트리스트
- 바이너리 파일 거부
- 크기 제한

### 3. 파일 저장
- UUID 파일명으로 예측 불가
- 사용자별 디렉토리 격리

## 테스트 필요사항
- [ ] file 방식 정상 업로드
- [ ] folder 방식 경로 보존
- [ ] paste 방식 가상 파일 생성
- [ ] title 5자 미만 시 422 에러
- [ ] files 없이 file 방식 시 ValidationError
- [ ] code_text 없이 paste 방식 시 ValidationError
- [ ] 10MB 초과 시 413 에러
- [ ] 바이너리 파일 업로드 거부
- [ ] 21개 파일 업로드 거부
- [ ] task_number 자동 증가
- [ ] uploaded_code_summary 정확도

## 클라이언트 사용 예시

### JavaScript (Fetch API)
```javascript
const formData = new FormData();
formData.append('title', 'My Task');
formData.append('upload_method', 'file');
formData.append('files', fileInput.files[0]);

const response = await fetch(`/api/v1/projects/${projectId}/tasks`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  body: formData
});

const task = await response.json();
console.log('Task created:', task);
```

## 완료 기준 충족
✅ POST /projects/{project_id}/tasks 엔드포인트 구현
✅ multipart/form-data 형식 지원
✅ 세 가지 업로드 방식 (file/folder/paste) 구현
✅ title 최소 5자 검증
✅ 조건부 필드 검증
✅ 10MB 크기 제한
✅ task_number 자동 증가
✅ uploaded_code_summary 포함
✅ 적절한 HTTP 상태 코드 (201, 401, 403, 404, 413, 422)
✅ 에러 처리 및 메시지
✅ OpenAPI 문서화
