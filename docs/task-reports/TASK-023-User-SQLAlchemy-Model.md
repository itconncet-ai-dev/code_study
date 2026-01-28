# TASK-023: User SQLAlchemy 모델 생성

**작성일**: 2026-01-21
**작업 유형**: 백엔드 모델 구현
**TDD 사이클**: RED → GREEN → REFACTOR 완료

---

## 무엇을 만들었나요?

플랫폼 사용자 정보를 저장하는 `User` 데이터베이스 모델을 만들었습니다. 이 모델은 마치 회원 카드와 같습니다 - 이메일 주소(로그인 ID), 비밀번호(암호화된 형태), 실력 수준, 가입 날짜 등 사용자에 대한 모든 정보를 담고 있습니다.

---

## 왜 이렇게 만들었나요?

### 1. UUID 사용 이유
일반 숫자(1, 2, 3...) 대신 UUID라는 긴 랜덤 문자열을 사용했습니다. 이렇게 하면 ID를 보고 "이 사람이 3번째 가입자구나"라고 추측할 수 없어서 보안에 좋습니다.

### 2. 비밀번호 해시 저장
비밀번호를 그대로 저장하면 해커가 데이터베이스를 훔쳤을 때 모든 비밀번호가 노출됩니다. 대신 비밀번호를 "해시"라는 특수한 방법으로 변환해서 저장합니다. 해시는 일방통행 - 원래 비밀번호로 되돌릴 수 없습니다.

### 3. 'Complete Beginner' 기본값
constitution(헌법) 규칙에 따라 모든 사용자는 처음에 "완전 초보자"로 시작합니다. 이 플랫폼이 코딩을 처음 배우는 분들을 위한 것이기 때문입니다.

### 4. Mixin 패턴 사용
`TimestampMixin`과 `UUIDPrimaryKeyMixin`을 상속받아 코드 중복을 줄였습니다. 레고 블록처럼 필요한 기능을 조립하는 방식입니다.

---

## 어떻게 동작하나요?

```python
# 새 사용자 생성 예시
user = User(
    email="student@example.com",
    password_hash="$2b$12$암호화된문자열..."
)

print(user.id)          # UUID가 자동 생성됨
print(user.skill_level)  # "Complete Beginner" 자동 설정
print(user.created_at)   # DB 저장 시 자동 기록
```

데이터베이스에 저장되면:
- `id`: 고유 식별자 (UUID)
- `email`: 유일해야 함 (중복 불가)
- `password_hash`: 암호화된 비밀번호
- `skill_level`: 초보/중급/고급
- `created_at`: 가입 시간
- `updated_at`: 정보 수정 시간
- `last_login_at`: 마지막 로그인 시간

---

## TDD로 어떻게 테스트했나요?

### RED 단계 (실패하는 테스트 작성)
먼저 User 모델이 없는 상태에서 8개의 테스트를 작성했습니다:
- 모델이 존재하는지
- UUID가 자동 생성되는지
- 기본값들이 올바른지
- 필수 필드가 정의되어 있는지

### GREEN 단계 (최소한의 코드로 통과)
테스트를 통과시키기 위해 User 모델을 구현했습니다. SQLAlchemy 2.0의 기본값이 객체 생성 시점에 적용되지 않는 문제를 발견하고, `__init__` 메서드에서 직접 기본값을 설정하도록 수정했습니다.

### REFACTOR 단계
코드 품질을 개선하고 문서화를 추가했습니다.

---

## 수정한 파일들

| 파일 | 변경 내용 |
|------|----------|
| `backend/src/models/user.py` | 새로 생성 - User 모델 정의 |
| `backend/src/models/__init__.py` | User 모델 export 추가 |
| `backend/tests/unit/test_user_model.py` | 새로 생성 - 8개 단위 테스트 |
| `specs/001-code-learning-platform/tasks.md` | T023 완료 표시 |

---

## 관련 개념

- **ORM (Object-Relational Mapping)**: 데이터베이스 테이블을 Python 클래스로 다루는 기술
- **SQLAlchemy 2.0**: Python에서 가장 많이 쓰이는 ORM 라이브러리
- **Mixin**: 재사용 가능한 기능을 담은 클래스 (상속으로 기능 추가)
- **UUID**: 전 세계적으로 고유한 식별자 (충돌 확률 거의 0)

---

## 주의사항

1. **비밀번호 직접 저장 금지**: `password_hash` 필드에는 반드시 해시된 값만 저장해야 합니다
2. **SQLAlchemy 기본값**: 객체 생성 시 즉시 기본값이 필요하면 `__init__`에서 처리해야 합니다
3. **관계(Relationship)**: Project, RefreshToken 모델이 만들어지면 관계를 추가해야 합니다

---

## 다음 단계

1. **T024**: RefreshToken 모델 생성 (JWT 인증용)
2. **T025**: UserService 구현 (회원가입, 로그인, 로그아웃)
3. 데이터베이스 마이그레이션 업데이트 (이미 T009에서 스키마 정의됨)
