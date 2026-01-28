# TASK-006: 린팅 및 포매팅 도구 설정

**완료일**: 2025-01-16
**상태**: ✅ 완료

## 무엇을 만들었나요?

코드 품질을 자동으로 검사하고 일관된 스타일로 정리해주는 도구들을 설정했습니다.

### 백엔드 (Python)
- **Ruff**: 코드에서 문제가 될 수 있는 부분을 찾아주는 검사 도구 (린터)
- **Black**: 코드를 일관된 스타일로 자동 정리해주는 도구 (포매터)

### 프론트엔드 (TypeScript/React)
- **ESLint**: JavaScript/TypeScript 코드 검사 도구
- **Prettier**: 코드 자동 정리 도구

## 왜 이렇게 했나요?

코드 품질 도구를 사용하는 이유를 일상 비유로 설명하면:

**린터(Linter)**는 마치 **문법 검사기**와 같습니다. 글을 쓸 때 맞춤법 검사기가 "이 단어는 틀렸어요"라고 알려주듯이, 린터는 "이 코드는 문제가 될 수 있어요"라고 알려줍니다.

**포매터(Formatter)**는 마치 **문서 정리 도구**와 같습니다. 여러 사람이 함께 문서를 작성할 때 들여쓰기, 줄바꿈 등이 제각각이면 읽기 어렵죠. 포매터는 모든 코드를 동일한 스타일로 자동 정리해줍니다.

## 어떻게 작동하나요?

### 백엔드 명령어
```bash
# 코드 검사 (Ruff)
ruff check src/

# 코드 정리 (Black)
black src/
```

### 프론트엔드 명령어
```bash
# 코드 검사
npm run lint

# 코드 검사 및 자동 수정
npm run lint:fix

# 코드 스타일 정리
npm run format

# 스타일 확인만 (수정 없이)
npm run format:check

# 전체 검사 (타입 + 린트 + 포맷)
npm run check
```

## 수정된 파일들

| 파일 | 설명 |
|------|------|
| `backend/pyproject.toml` | Ruff, Black 설정 (이미 구성됨) |
| `frontend/eslint.config.js` | ESLint 규칙 강화 |
| `frontend/.prettierrc` | Prettier 스타일 설정 (신규) |
| `frontend/.prettierignore` | Prettier 제외 파일 목록 (신규) |
| `frontend/package.json` | Prettier 의존성 및 스크립트 추가 |
| `frontend/src/main.tsx` | ESLint 경고 수정 |

## 주요 설정 내용

### ESLint 규칙 (TypeScript)
- 사용하지 않는 변수 경고 (`_`로 시작하면 허용)
- `console.log` 사용 경고 (`console.warn`, `console.error`는 허용)
- `===` 대신 `==` 사용 금지
- `var` 대신 `const`/`let` 사용 강제

### Prettier 스타일
- 세미콜론 없음 (`semi: false`)
- 작은따옴표 사용 (`singleQuote: true`)
- 한 줄 최대 100자 (`printWidth: 100`)
- 탭 너비 2칸

## 관련 개념

- **Linting**: 코드를 실행하지 않고 잠재적 오류나 스타일 문제를 찾는 정적 분석
- **Formatting**: 코드의 시각적 스타일(들여쓰기, 공백, 줄바꿈)을 일관되게 정리
- **Code Quality**: 버그 없이 읽기 쉽고 유지보수하기 좋은 코드를 작성하는 것

## 주의사항

- 린터 규칙을 무시하려면 `// eslint-disable-next-line` 주석 사용 (권장하지 않음)
- Prettier와 ESLint가 충돌할 경우, 스타일 관련은 Prettier가 담당하도록 ESLint 규칙 비활성화

## 다음 단계

- T007: Git ignore 패턴 설정
- Phase 2: Database & Migrations 설정
