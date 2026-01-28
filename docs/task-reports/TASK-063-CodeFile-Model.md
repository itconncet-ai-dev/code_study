# TASK-063: CodeFile SQLAlchemy 모델 생성

**완료일**: 2025-01-24
**관련 파일**: `backend/src/models/code_file.py`

## 무엇을 만들었나요?

업로드된 코드 파일 하나하나의 정보를 저장하는 데이터베이스 모델을 만들었습니다. 예를 들어, 사용자가 폴더를 업로드하면 그 안에 `main.py`, `utils.py`, `README.md` 같은 여러 파일이 있을 수 있는데, 각 파일마다 CodeFile 레코드가 생성됩니다.

## 왜 이렇게 만들었나요?

하나의 업로드(UploadedCode)에는 여러 개의 파일이 포함될 수 있습니다. 각 파일에 대해 다음 정보를 별도로 관리해야 합니다:
- 파일 이름과 경로
- 파일 확장자 (지원되는 형식인지 확인용)
- 파일 크기
- 실제 저장 위치 (storage_path)
- MIME 타입

이렇게 분리하면 나중에 개별 파일을 조회하거나, 특정 확장자만 필터링하는 것이 쉬워집니다.

## 어떻게 작동하나요?

1. **UploadedCode와 1:N 관계**: 하나의 UploadedCode에 여러 CodeFile이 연결됩니다
2. **연쇄 삭제(CASCADE)**: UploadedCode가 삭제되면 모든 CodeFile도 자동 삭제
3. **지원 확장자 검증**: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.html`, `.css`, `.java`, `.cpp`, `.c`, `.txt`, `.md`
4. **파일 개수 제한**: 업로드당 1-20개 파일

## TDD 사이클

- **GREEN**: 모델 생성 후 관계 및 CASCADE 삭제 테스트 통과
- **테스트 결과**:
  - 3개 CodeFile 생성 및 관계 확인 성공
  - UploadedCode 삭제 시 모든 CodeFile CASCADE 삭제 확인

## 수정된 파일들

| 파일 경로 | 변경 내용 |
|-----------|-----------|
| `backend/src/models/code_file.py` | 새로 생성 - CodeFile 모델 정의 |
| `backend/src/models/uploaded_code.py` | code_files 관계 추가 |
| `backend/src/models/__init__.py` | CodeFile import 및 export 추가 |

## 주요 속성들

```python
# 지원되는 파일 확장자
SUPPORTED_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.java', '.cpp', '.c', '.txt', '.md'}

# 업로드당 파일 개수 제한
MAX_FILES_PER_UPLOAD = 20
MIN_FILES_PER_UPLOAD = 1
```

## 유용한 메서드들

- `is_supported_extension()`: 지원되는 확장자인지 확인
- `size_in_kb`, `size_in_mb`: 파일 크기를 KB/MB 단위로 변환
- `full_path`: file_path가 있으면 사용, 없으면 file_name 반환
- `extract_extension(filename)`: 파일명에서 확장자 추출

## 다음 단계

- **T064**: 파일 유효성 검증 유틸리티 (확장자, 크기, 바이너리 파일 감지)
- **T067**: 파일 저장 서비스 (storage/uploads/{user_id}/{task_id}/ 경로에 저장)
