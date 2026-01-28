# TASK-044: ProjectService 구현

**작업 완료일**: 2025-01-22
**TDD 사이클**: RED-GREEN-REFACTOR 완료

## 무엇을 만들었나요?

프로젝트 관리를 위한 **ProjectService**를 구현했습니다. 이 서비스는 사용자가 학습 프로젝트를 생성하고, 조회하고, 수정하고, 삭제할 수 있게 해주는 "관리자" 역할을 합니다.

마치 도서관에서 책을 빌리고 반납하는 것처럼, 사용자들은 이 서비스를 통해 자신만의 학습 공간(프로젝트)을 만들고 관리할 수 있습니다.

## 왜 이렇게 만들었나요?

### 서비스 패턴 사용

기존의 `UserService` 패턴을 따라 일관성 있는 코드 구조를 유지했습니다. 서비스 계층을 분리함으로써:

1. **데이터베이스 로직 분리**: API 엔드포인트에서 비즈니스 로직을 분리하여 코드가 더 깨끗해집니다.
2. **테스트 용이성**: Mock을 사용한 단위 테스트가 쉬워집니다.
3. **재사용성**: 같은 로직을 여러 곳에서 사용할 수 있습니다.

### 소프트 삭제 (Soft Delete)

프로젝트를 바로 삭제하지 않고 "휴지통"으로 옮기는 방식을 사용합니다. 실수로 삭제해도 30일 동안은 복구할 수 있어서 사용자 경험이 좋아집니다. 마치 컴퓨터의 휴지통처럼요!

### 소유권 검증

다른 사람의 프로젝트에 접근하지 못하도록 모든 조회/수정/삭제 작업에서 소유권을 확인합니다. 보안을 위해 필수적인 기능입니다.

## 어떻게 작동하나요?

### 주요 기능들

| 메서드 | 설명 | 비유 |
|--------|------|------|
| `create()` | 새 프로젝트 생성 | 새 폴더 만들기 |
| `get_by_id()` | ID로 프로젝트 조회 | 폴더 열어보기 |
| `get_user_projects()` | 사용자의 모든 프로젝트 목록 | 내 폴더 목록 보기 |
| `update()` | 프로젝트 정보 수정 | 폴더 이름 바꾸기 |
| `soft_delete()` | 휴지통으로 이동 | 폴더를 휴지통에 넣기 |

### 코드 흐름 예시

```python
# 프로젝트 생성
service = ProjectService(db_session)
project = await service.create(
    user_id=current_user.id,
    title="내 첫 번째 프로젝트",
    description="Python 기초 학습"
)

# 프로젝트 목록 조회
my_projects = await service.get_user_projects(current_user.id)

# 프로젝트 수정
updated = await service.update(
    project_id=project.id,
    user_id=current_user.id,
    title="Python 고급 학습"
)

# 프로젝트 삭제 (휴지통으로)
await service.soft_delete(project.id, current_user.id)
```

## TDD로 어떻게 테스트했나요?

### RED 단계 (테스트 먼저 작성)

24개의 테스트 케이스를 먼저 작성했습니다:

- **Create 테스트 (5개)**: 프로젝트 생성, 설명 추가, 상태 설정, 빈 제목 거부
- **GetById 테스트 (5개)**: 조회 성공, 없는 프로젝트, 권한 없음, 휴지통 처리
- **GetUserProjects 테스트 (4개)**: 목록 조회, 휴지통 제외/포함, 빈 목록
- **Update 테스트 (5개)**: 제목/설명 수정, 권한/존재 확인, 빈 제목 거부
- **SoftDelete 테스트 (5개)**: 휴지통 이동, 30일 삭제 예약, 권한/존재 확인

### GREEN 단계 (구현)

테스트를 통과할 수 있는 최소한의 코드를 작성했습니다.

### REFACTOR 단계

중복 코드를 `_validate_title()` 같은 private 메서드로 추출하여 정리했습니다.

## 수정된 파일들

| 파일 | 변경 내용 |
|------|----------|
| `backend/src/services/project_service.py` | **신규** - ProjectService 구현 |
| `backend/tests/unit/test_project_service.py` | **신규** - 24개 테스트 케이스 |
| `specs/001-code-learning-platform/tasks.md` | T044 완료 표시 |

## 관련 개념들

- **서비스 계층 (Service Layer)**: 비즈니스 로직을 담당하는 중간 계층
- **소프트 삭제 (Soft Delete)**: 데이터를 바로 삭제하지 않고 "삭제됨" 상태로 표시
- **의존성 주입 (Dependency Injection)**: 외부에서 데이터베이스 세션을 주입받아 유연성 확보
- **비동기 프로그래밍 (Async/Await)**: 데이터베이스 작업 중 다른 요청을 처리할 수 있음

## 주의사항

1. **T045와의 관계**: 소유권 검증은 이미 `get_by_id()`에 포함되어 있습니다. T045는 추가적인 검증 로직이 필요한 경우를 위한 것입니다.

2. **트랜잭션 처리**: 서비스는 `commit()`을 호출하지만, FastAPI의 `get_db()` 의존성에서도 자동 커밋/롤백이 처리됩니다.

3. **휴지통 조회**: `include_trashed=True` 파라미터를 사용해야 휴지통의 프로젝트를 볼 수 있습니다.

## 다음 단계

- **T045**: 프로젝트 소유권 검증 추가 (필요시)
- **T046-T050**: Project API 엔드포인트 구현
- **T051-T056**: Frontend 프로젝트 UI 구현
