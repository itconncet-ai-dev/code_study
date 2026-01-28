# Task 보고서: T069 - CodeUploadService 구현

## 작업 정보
- **작업 번호**: T069
- **작업 제목**: CodeUploadService 구현
- **담당자**: Backend TDD Implementation Specialist
- **작업 일자**: 2026-01-24
- **상태**: 완료

## 작업 개요
코드 업로드를 처리하는 CodeUploadService를 구현했습니다. 세 가지 업로드 방식(file, folder, paste)을 지원하며, 파일 검증, 언어 감지, 복잡도 분석을 통합합니다.

## 구현 내용

### 파일 경로: `backend/src/services/code_analysis/code_upload_service.py`

### 주요 기능

#### 1. 파일 업로드 (File Upload)
```python
async def handle_file_upload(
    task_id: UUID,
    user_id: UUID,
    files: list[tuple[str, bytes]],
) -> UploadedCode
```
- 단일 또는 다중 파일 업로드
- 파일 검증 (확장자, 크기, 바이너리 검사)
- 언어 자동 감지 (첫 번째 파일 기준)
- 복잡도 분석
- UploadedCode 및 CodeFile 레코드 생성

#### 2. 폴더 업로드 (Folder Upload)
```python
async def handle_folder_upload(
    task_id: UUID,
    user_id: UUID,
    files: list[tuple[str, bytes]],
) -> UploadedCode
```
- 디렉토리 구조 보존
- file_path에 상대 경로 저장 (예: "src/main.py")
- 파일 업로드와 동일한 검증 및 분석

#### 3. 붙여넣기 업로드 (Paste Upload)
```python
async def handle_paste_upload(
    task_id: UUID,
    user_id: UUID,
    code_text: str,
    language: str | None = None,
) -> UploadedCode
```
- 코드 텍스트 직접 입력
- 언어 힌트 제공 가능
- 가상 파일 생성 (pasted_code.{ext})
- 단일 파일로 처리

## 통합된 서비스 활용

### 1. FileValidator
```python
validation_result = FileValidator.validate_upload(
    [(name, len(content), content) for name, content in files]
)
```
- 확장자 검증 (.py, .js, .ts 등 12가지)
- 파일 크기 검증 (최대 10MB)
- 바이너리 파일 거부
- 파일 개수 검증 (1-20개)

### 2. LanguageDetector
```python
language_info = LanguageDetector.detect(
    first_filename,
    first_content.decode("utf-8", errors="ignore"),
)
```
- 확장자 기반 감지 (우선)
- Pygments 콘텐츠 분석 (대체)
- 신뢰도 점수 제공

### 3. ComplexityAnalyzer
```python
complexity_result = ComplexityAnalyzer.analyze_files(file_contents)
```
- 복잡도 수준 계산 (beginner/intermediate/advanced)
- 다중 메트릭 분석
- 코드 라인 수, 함수 수, 클래스 수 등 집계

### 4. FileStorageService
```python
storage_path = await FileStorageService.save_file(
    content=content,
    user_id=user_id,
    task_id=task_id,
    filename=filename,
)
```
- 파일시스템에 저장
- UUID 기반 고유 파일명
- 디렉토리 자동 생성

## 데이터 모델 생성

### UploadedCode 레코드
```python
uploaded_code = UploadedCode(
    task_id=task_id,
    detected_language=language_info.language,
    complexity_level=complexity_result.level.value,
    total_lines=total_lines,
    total_files=len(files),
    upload_size_bytes=total_size_bytes,
)
```
- 태스크와 1:1 관계
- 전체 업로드 메타데이터 저장

### CodeFile 레코드
```python
code_file = CodeFile(
    uploaded_code_id=uploaded_code.id,
    file_name=filename,
    file_path=file_path,
    file_extension=extension,
    file_size_bytes=len(content),
    storage_path=storage_path,
    mime_type=mime_type,
)
```
- 개별 파일 정보 저장
- 파일시스템 경로 매핑

## 업로드 방식별 차이점

| 특성 | File Upload | Folder Upload | Paste Upload |
|------|-------------|---------------|--------------|
| 파일 개수 | 1-20개 | 1-20개 | 1개 (가상) |
| 경로 보존 | file_name만 | 전체 경로 | 가상 파일명 |
| 언어 감지 | 첫 파일 확장자 | 첫 파일 확장자 | 언어 힌트 또는 콘텐츠 분석 |
| 파일명 | 원본 유지 | 원본 유지 | pasted_code.{ext} |

## 검증 로직

### 1. 파일 업로드 검증
- 확장자: SUPPORTED_EXTENSIONS 확인
- 크기: 개별 파일 + 전체 10MB 제한
- 바이너리: NULL 바이트 비율 확인
- 개수: 1-20개 제한

### 2. 붙여넣기 검증
- 빈 텍스트 거부
- UTF-8 인코딩
- 10MB 크기 제한

## 트랜잭션 처리
```python
self.db.add(uploaded_code)
await self.db.flush()  # ID 생성

# CodeFile 레코드 생성
for filename, content in files:
    # ... 파일 저장 및 레코드 생성

await self.db.commit()
await self.db.refresh(uploaded_code)
```
- flush(): ID 즉시 생성 (관계 설정용)
- commit(): 트랜잭션 완료
- refresh(): 관계 데이터 로드

## 에러 처리
```python
if not validation_result.is_valid:
    raise ValidationError(
        detail=validation_result.error_message,
        field="files",
    )
```
- 검증 실패 시 명확한 에러 메시지
- field 파라미터로 문제 필드 명시

## 언어별 확장자 매핑 (Paste Upload)
```python
extension_map = {
    "Python": ".py",
    "JavaScript": ".js",
    "TypeScript": ".ts",
    "Java": ".java",
    "C++": ".cpp",
    "C": ".c",
    "HTML": ".html",
    "CSS": ".css",
}
extension = extension_map.get(detected_language, ".txt")
```
- 감지된 언어에 맞는 확장자 자동 할당
- 기본값: .txt

## 테스트 필요사항
- [ ] 파일 업로드 정상 처리
- [ ] 폴더 업로드 경로 보존 확인
- [ ] 붙여넣기 업로드 가상 파일 생성
- [ ] 10MB 초과 시 ValidationError
- [ ] 바이너리 파일 거부
- [ ] 21개 이상 파일 거부
- [ ] UploadedCode와 CodeFile 관계 확인
- [ ] 언어 감지 정확도
- [ ] 복잡도 분석 결과

## 성능 고려사항
1. **비동기 I/O**: 파일 저장 시 블로킹 방지
2. **트랜잭션 최적화**: flush로 ID 즉시 생성
3. **메모리 효율**: 스트리밍 읽기 (향후 개선 필요)

## 보안 고려사항
1. **파일 검증**: 악성 파일 업로드 방지
2. **크기 제한**: DoS 공격 방지
3. **바이너리 거부**: 실행 파일 차단
4. **UUID 파일명**: 경로 예측 불가

## 향후 개선 사항
1. 대용량 파일 스트리밍 처리
2. 압축 파일 (.zip) 지원
3. 파일 미리보기 생성
4. 악성 코드 스캔 통합
5. 진행률 표시 (청크 업로드)

## 완료 기준 충족
✅ 파일 업로드 방식 구현
✅ 폴더 업로드 방식 구현
✅ 붙여넣기 업로드 방식 구현
✅ FileValidator 사용
✅ LanguageDetector 사용
✅ ComplexityAnalyzer 사용
✅ FileStorageService 사용
✅ UploadedCode 및 CodeFile 레코드 생성
✅ 검증 로직 통합
✅ 타입 힌트 및 docstring 작성
