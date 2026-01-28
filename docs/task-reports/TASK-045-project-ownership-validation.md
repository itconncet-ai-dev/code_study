# TASK-045: 프로젝트 소유권 검증 구현

**작업일**: 2025-01-23
**파일**: `backend/src/services/project_service.py`
**관련 테스트**: `backend/tests/unit/test_project_service.py`

## 무엇을 만들었나요?

프로젝트의 "주인"이 맞는지 확인하는 기능을 만들었어요. 마치 아파트 경비원이 "이 집에 사는 분 맞으세요?"라고 확인하는 것처럼, 누군가 프로젝트를 수정하거나 접근하려 할 때 "정말 이 프로젝트의 주인이 맞나요?"를 검증하는 `validate_ownership` 메서드를 추가했습니다.

## 왜 이렇게 만들었나요?

기존에도 `get_by_id` 메서드 안에 소유권 검증이 있었지만, 이것만으로는 부족했어요:

1. **다른 서비스도 사용해야 해요**: 나중에 TaskService(할 일 관리 서비스)에서 "이 프로젝트에 할 일을 추가해도 되나요?"를 확인할 때, 명확한 이름의 메서드가 필요해요.

2. **코드를 읽는 사람이 이해하기 쉬워요**: `validate_ownership`이라는 이름만 봐도 "아, 소유권을 확인하는 거구나!"라고 바로 알 수 있어요.

3. **보안 패턴을 일관되게 유지해요**: 모든 곳에서 같은 방식으로 소유권을 확인하면, 실수로 검증을 빠뜨릴 가능성이 줄어들어요.

## 어떻게 작동하나요?

```python
# TaskService에서 사용 예시
project_service = ProjectService(db)
project = await project_service.validate_ownership(project_id, user_id)
# 여기까지 왔으면 user_id가 진짜 주인이에요!
# 이제 안전하게 할 일을 추가할 수 있어요
```

내부 동작은 간단해요:
1. 프로젝트가 존재하는지 확인 (없으면 "찾을 수 없음" 에러)
2. 요청한 사람이 프로젝트 주인인지 확인 (아니면 "권한 없음" 에러)
3. 휴지통에 있는 프로젝트인지 확인 (특별히 요청하지 않으면 휴지통 것은 안 보여줌)

## TDD(테스트 주도 개발) 과정

### RED 단계 (실패하는 테스트 작성)
먼저 `validate_ownership` 메서드가 어떻게 동작해야 하는지 6개의 테스트를 작성했어요:
- 주인이 맞으면 프로젝트 반환
- 프로젝트가 없으면 NotFoundError
- 주인이 아니면 ForbiddenError
- 휴지통 프로젝트는 기본적으로 거부
- 요청하면 휴지통 프로젝트도 검증 가능
- 다른 서비스에서 사용 가능한지 확인

메서드가 없으니 당연히 모든 테스트가 실패했어요! (`AttributeError`)

### GREEN 단계 (테스트 통과하는 코드 작성)
`validate_ownership` 메서드를 추가했어요. 이미 잘 동작하는 `get_by_id`를 재사용해서 간결하게 구현했습니다.

### 결과
- 새로 추가한 6개 테스트 모두 통과
- 기존 24개 테스트도 모두 통과 (총 30개)

## 수정한 파일

| 파일 | 변경 내용 |
|------|----------|
| `backend/src/services/project_service.py` | `validate_ownership()` 메서드 추가, 모듈 독스트링 업데이트 |
| `backend/tests/unit/test_project_service.py` | `TestProjectServiceValidateOwnership` 테스트 클래스 추가 (6개 테스트) |

## 관련 개념

- **권한 검증 (Authorization)**: "이 사람이 이 작업을 할 수 있나요?"를 확인하는 보안 절차
- **서비스 간 재사용**: 다른 서비스에서도 같은 로직을 쓸 수 있도록 메서드를 분리
- **TDD**: 코드보다 테스트를 먼저 작성하는 개발 방식

## 주의할 점

- 프로젝트가 없을 때 `ForbiddenError`가 아닌 `NotFoundError`를 반환해요. 이유는 해커가 "이 ID의 프로젝트가 존재하는군!"이라고 추측하지 못하게 하기 위해서예요.
- 휴지통에 있는 프로젝트도 검증하려면 `include_trashed=True`를 명시해야 해요.

## 다음 단계

T046부터 T050까지 프로젝트 API 엔드포인트를 구현할 때 이 `validate_ownership` 메서드를 활용하게 됩니다.
