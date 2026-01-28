# Task 보고서: T068 - TaskService 구현

## 작업 정보
- **작업 번호**: T068
- **작업 제목**: TaskService CRUD 구현
- **담당자**: Backend TDD Implementation Specialist
- **작업 일자**: 2026-01-24
- **상태**: 완료

## 작업 개요
태스크 관리를 위한 TaskService를 구현했습니다. ProjectService 패턴을 따라 CRUD 작업, 소프트 삭제, 소유권 검증 기능을 제공합니다.

## 구현 내용

### 파일 경로: `backend/src/services/task_service.py`

### 주요 기능
1. **태스크 생성 (Create)**
   - 프로젝트 내 자동 증가하는 task_number 할당
   - 제목 최소 5자 검증
   - 설명 최대 500자 제한
   - upload_method 검증 (file/folder/paste)

2. **태스크 조회 (Read)**
   - ID로 단일 태스크 조회
   - 프로젝트별 태스크 목록 조회 (task_number 순서)
   - 소유권 검증 (프로젝트 소유자 확인)
   - 휴지통 항목 포함/제외 옵션

3. **태스크 수정 (Update)**
   - 제목 및 설명 수정
   - 수정 시간 자동 업데이트
   - 입력 검증

4. **소프트 삭제 (Soft Delete)**
   - 30일 휴지통 보관
   - 예정된 영구 삭제 시간 설정
   - 복원 가능

## 기술적 결정사항

### Task Number 자동 증가
```python
async def _get_next_task_number(self, project_id: UUID) -> int:
    stmt = select(func.max(Task.task_number)).where(
        Task.project_id == project_id
    )
    result = await self.db.execute(stmt)
    max_number = result.scalar()
    return 1 if max_number is None else max_number + 1
```
- 프로젝트별 독립적인 번호 체계
- MAX() 함수로 최대값 조회
- 첫 태스크는 1부터 시작

### 소유권 검증 패턴
```python
# 프로젝트 소유권을 통한 태스크 소유권 검증
project_service = ProjectService(self.db)
await project_service.validate_ownership(project_id, user_id)
```
- ProjectService를 통한 소유권 위임 검증
- 일관된 권한 검사 로직
- 서비스 간 협력 패턴

### 순차 조회 보장
```python
stmt = stmt.order_by(Task.task_number.asc())
```
- task_number 오름차순 정렬
- 사용자가 생성한 순서대로 표시
- 불변하는 순서 보장

## 비즈니스 규칙 구현

### 제목 검증
- 필수 입력
- 최소 5자 이상
- 공백 문자열 불허

### 설명 검증
- 선택 사항
- 최대 500자 제한
- None 허용

### 소프트 삭제
- 30일 보관 기간
- 복원 가능 기간
- 영구 삭제 예약

## 보안 고려사항
1. **소유권 검증**
   - 모든 작업에서 프로젝트 소유권 확인
   - 다른 사용자의 태스크 접근 차단

2. **에러 처리**
   - NotFoundError: 리소스 열거 공격 방지
   - ForbiddenError: 명시적인 권한 거부
   - ValidationError: 입력값 검증 실패

## API 예외 처리
```python
# 존재하지 않는 태스크
raise NotFoundError(
    detail=f"Task with ID '{task_id}' not found",
    resource="task",
    resource_id=str(task_id),
)

# 권한 없음
raise ForbiddenError(
    detail="You do not have permission to access this task"
)

# 입력값 검증 실패
raise ValidationError(
    detail="Title must be at least 5 characters",
    field="title",
)
```

## 테스트 필요사항
- [ ] 태스크 생성 시 task_number 자동 증가
- [ ] 같은 프로젝트 내 task_number 중복 없음
- [ ] 제목 5자 미만 시 ValidationError
- [ ] 다른 사용자 태스크 접근 시 ForbiddenError
- [ ] 소프트 삭제 후 30일 보관
- [ ] task_number 순서대로 정렬

## 데이터베이스 연동
- SQLAlchemy AsyncSession 사용
- 관계형 모델 활용 (Task.project)
- 트랜잭션 관리 (commit/rollback)

## ProjectService 패턴 준수
TaskService는 ProjectService와 동일한 패턴을 따릅니다:
- 비동기 메서드
- 일관된 메서드 명명 (create, get_by_id, update, soft_delete)
- validate_ownership 메서드 제공
- 명확한 예외 처리

## 완료 기준 충족
✅ CRUD 작업 구현 (create, get, update, delete)
✅ task_number 자동 증가
✅ ProjectService 패턴 준수
✅ 소유권 검증 구현
✅ 소프트 삭제 30일 보관
✅ 입력값 검증 (제목 최소 5자, 설명 최대 500자)
✅ 타입 힌트 및 docstring 작성
