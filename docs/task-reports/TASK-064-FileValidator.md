# TASK-064: 파일 검증 유틸리티 구현

**완료일**: 2025-01-24
**관련 파일**: `backend/src/utils/file_validator.py`

## 무엇을 만들었나요?

사용자가 업로드하는 코드 파일들이 올바른지 검사하는 도구를 만들었습니다. 마치 공항 보안검색대처럼, 업로드되는 파일들을 하나하나 검사해서 허용된 것만 통과시킵니다.

## 왜 이렇게 만들었나요?

악성 파일이나 너무 큰 파일이 서버에 올라오면 보안 문제가 생기고, 서버 자원도 낭비됩니다. 그래서:
- **확장자 검증**: .exe, .dll 같은 실행 파일 차단
- **크기 검증**: 10MB 초과 파일 차단
- **바이너리 감지**: 텍스트가 아닌 이진 파일 차단
- **개수 검증**: 한 번에 20개 이상 파일 업로드 차단

## 어떻게 작동하나요?

### 1. 확장자 검증
```python
FileValidator.validate_extension("main.py")  # 통과
FileValidator.validate_extension("virus.exe")  # 차단
```

허용 확장자: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.html`, `.css`, `.java`, `.cpp`, `.c`, `.txt`, `.md`

### 2. 크기 검증
```python
FileValidator.validate_file_size(5 * 1024 * 1024)   # 5MB → 통과
FileValidator.validate_file_size(15 * 1024 * 1024)  # 15MB → 차단
```

### 3. 바이너리 감지
```python
FileValidator.is_binary_content(b"print('hello')")  # False (텍스트)
FileValidator.is_binary_content(bytes([0x00, 0x01]))  # True (바이너리)
```

### 4. 파일 개수 검증
```python
FileValidator.validate_file_count(15)  # 통과
FileValidator.validate_file_count(25)  # 차단 (최대 20개)
```

## TDD 사이클

- **GREEN**: 유틸리티 구현 후 모든 테스트 케이스 통과
- **테스트 결과**: 확장자, 크기, 바이너리, 개수 검증 모두 PASS

## 수정된 파일들

| 파일 경로 | 변경 내용 |
|-----------|-----------|
| `backend/src/utils/file_validator.py` | 새로 생성 - FileValidator 클래스 |
| `backend/src/utils/__init__.py` | FileValidator, ValidationResult export 추가 |

## 주요 클래스 및 상수

```python
class FileValidator:
    SUPPORTED_EXTENSIONS = {'.py', '.js', '.ts', ...}  # 12개 확장자
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
    MIN_FILES_PER_UPLOAD = 1
    MAX_FILES_PER_UPLOAD = 20

class ValidationResult:
    is_valid: bool
    error_message: str | None
```

## 주요 메서드

| 메서드 | 용도 |
|--------|------|
| `validate_extension()` | 파일 확장자 검증 |
| `validate_file_size()` | 개별 파일 크기 검증 |
| `validate_total_upload_size()` | 전체 업로드 크기 검증 |
| `validate_file_count()` | 파일 개수 검증 |
| `is_binary_content()` | 바이너리 파일 감지 |
| `validate_file()` | 단일 파일 종합 검증 |
| `validate_upload()` | 전체 업로드 종합 검증 |

## 다음 단계

- **T065**: 언어 감지 서비스 (Pygments 사용)
- **T069**: CodeUploadService에서 FileValidator 활용
