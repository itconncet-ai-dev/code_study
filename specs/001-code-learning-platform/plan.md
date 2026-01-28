# Implementation Plan: AI Code Learning Platform - Phase 1 MVP

**Branch**: `001-code-learning-platform` | **Date**: 2025-11-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-code-learning-platform/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Building an educational platform that transforms AI-generated code into beginner-friendly learning materials. Core features: task-based code upload system, automatic code analysis, 7-chapter textbook-style document generation, practice problem generation, contextual Q&A, and progress tracking. Target users are complete programming beginners who use AI tools but struggle to understand the generated code.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/React 18+ (frontend)
**Primary Dependencies**: FastAPI, PostgreSQL, SQLAlchemy 2.0, Google Gemini 3 Flash Preview API, Celery, Redis, React, TanStack Query
**Storage**: PostgreSQL 15+ (user data, documents as JSONB), Local filesystem (uploaded code files for MVP)
**Testing**: pytest + pytest-asyncio (backend), Vitest + Testing Library (frontend)
**Target Platform**: Web application (desktop-first per spec assumptions)
**Project Type**: Web (frontend + backend architecture required)
**Performance Goals**:
- Document generation < 3 minutes for 500 LOC
- Q&A responses < 10 seconds
- UI interactions < 200ms
- Page load < 3 seconds

**Constraints**:
- Educational content must be accessible to complete beginners (zero programming knowledge)
- All explanations in Korean for task reports, code explanations can be English
- Desktop-first UI (mobile responsive in Phase 2)
- Maximum 10MB upload per task
- Support 3 concurrent document generations per user
- 80% test coverage minimum (100% for core business logic)

**Scale/Scope**:
- Initial scale: Small user base (hundreds of users)
- Storage: ~100MB per user average (code + generated documents)
- Concurrent users: Target 100+ concurrent users
- Document generation: CPU/memory intensive AI operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I-A. Generated Content Quality (NON-NEGOTIABLE)
- ✅ **PASS**: Spec requires all explanations written for zero programming knowledge (FR-035)
- ✅ **PASS**: Technical terms must be explained with everyday language (FR-036)
- ✅ **PASS**: Real-life analogies mandatory for abstract concepts (FR-037)
- ✅ **PASS**: 7-chapter document structure ensures comprehensive educational quality

### I-B. Development Process Documentation (NON-NEGOTIABLE)
- ✅ **PASS**: This plan will generate task completion reports in Korean
- ✅ **PASS**: Reports will be stored in `docs/task-reports/TASK-{number}-{title}.md`
- ⚠️ **ACTION REQUIRED**: Must follow TDD and document each step

### II. Test-Driven Development (NON-NEGOTIABLE)
- ✅ **PASS**: Spec requires 80% test coverage (FR-069, FR-070 for progress tracking)
- ⚠️ **ACTION REQUIRED**: TDD cycle (RED-GREEN-REFACTOR) must be followed during implementation
- ⚠️ **ACTION REQUIRED**: Each TDD phase requires separate commit

### III. Content Immutability Strategy
- ✅ **PASS**: Spec FR-038 requires generated documents to be stored (not regenerated)
- ✅ **PASS**: Q&A system appends questions without modifying original document (FR-066)
- ✅ **PASS**: Clarification confirms no document versioning within tasks (always new task)

### IV. User Architecture & Authentication
- ✅ **PASS**: Spec assumption #1 references constitution authentication requirements
- ✅ **PASS**: Basic email/password authentication required
- ✅ **PASS**: Data isolation per user (FR-081: uploaded code stored securely)
- ✅ **PASS**: YAGNI respected - no social features, complex RBAC, or OAuth in Phase 1
- ⚠️ **ACTION REQUIRED**: Must implement password hashing (bcrypt/argon2), CSRF, XSS prevention

### V. Real-Time User Experience
- ✅ **PASS**: Loading states with estimated time (FR-084, FR-089)
- ✅ **PASS**: Non-blocking UI during document generation (FR-085, FR-092)
- ✅ **PASS**: Performance targets align: 3 min generation, 10 sec Q&A (FR-083, FR-087)

### YAGNI Principle
- ✅ **PASS**: No premature abstractions in spec
- ✅ **PASS**: Phase 1 excludes advanced features (visual diagrams, in-browser execution, etc.)
- ✅ **PASS**: Simple task structure (sequential, immutable numbers)
- ⚠️ **WATCH**: Complexity limits during implementation (max 4 params, 3 nesting, 250 lines/file)

### Quality Gates
- ✅ **PASS**: Test coverage ≥ 80% required
- ✅ **PASS**: Performance targets defined (3s page load, 3min generation, 10s Q&A)
- ⚠️ **ACTION REQUIRED**: Security review for authentication flows before production
- ⚠️ **ACTION REQUIRED**: Educational content validation by non-developer tester

**GATE STATUS**: ✅ **PASS** - Proceed to Phase 0 research with action items noted

## Project Structure

### Documentation (this feature)

```text
specs/001-code-learning-platform/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (completed)
├── research.md          # Phase 0 output (/speckit.plan command) - PENDING
├── data-model.md        # Phase 1 output (/speckit.plan command) - PENDING
├── quickstart.md        # Phase 1 output (/speckit.plan command) - PENDING
├── contracts/           # Phase 1 output (/speckit.plan command) - PENDING
├── checklists/
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Web application structure

backend/
├── src/
│   ├── models/              # Data models (User, Project, Task, LearningDocument, etc.)
│   ├── services/            # Business logic
│   │   ├── auth/           # Authentication & session management
│   │   ├── code_analysis/  # Code upload, parsing, language detection
│   │   ├── ai/             # LLM integration for document & Q&A generation
│   │   ├── document/       # Learning document generation & storage
│   │   ├── practice/       # Practice problem generation
│   │   └── progress/       # Progress tracking
│   ├── api/                # REST/GraphQL API endpoints
│   │   ├── auth.py/ts      # Login, register, logout endpoints
│   │   ├── projects.py/ts  # Project CRUD
│   │   ├── tasks.py/ts     # Task CRUD, code upload
│   │   ├── documents.py/ts # Document retrieval
│   │   ├── qa.py/ts        # Q&A endpoints
│   │   └── progress.py/ts  # Progress tracking endpoints
│   ├── db/                 # Database migrations & connection
│   └── utils/              # Shared utilities
└── tests/
    ├── contract/           # API contract tests
    ├── integration/        # Integration tests
    └── unit/               # Unit tests

frontend/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── auth/          # Login, register forms
│   │   ├── project/       # Project dashboard, project cards
│   │   ├── task/          # Task cards, task timeline
│   │   ├── upload/        # Code upload UI (file/folder/paste)
│   │   ├── document/      # Learning document viewer (2-column layout)
│   │   ├── practice/      # Practice problem UI
│   │   ├── qa/            # Q&A panel
│   │   └── progress/      # Progress indicators, badges
│   ├── pages/             # Route pages
│   │   ├── dashboard.tsx/vue    # Project list
│   │   ├── project.tsx/vue      # Project detail with task timeline
│   │   ├── task.tsx/vue         # Task detail with document/practice/Q&A
│   │   ├── login.tsx/vue
│   │   ├── register.tsx/vue
│   │   └── trash.tsx/vue        # Trash/deleted items view
│   ├── services/          # API client wrappers
│   ├── hooks/             # Custom React hooks (or composables for Vue)
│   └── utils/             # Frontend utilities
└── tests/
    ├── integration/       # E2E tests
    └── unit/              # Component unit tests

docs/
└── task-reports/          # Task completion reports (constitution requirement)
    └── TASK-{number}-{title}.md
```

**Structure Decision**: Selected **Web application (Option 2)** structure because:
1. Spec requires desktop web UI with code editor features (side-by-side panels, syntax highlighting)
2. Backend needed for AI integration, authentication, and database operations
3. Frontend needs rich interactivity (Q&A panel, progress tracking, synchronized scrolling)
4. Clear separation enables independent scaling of AI operations vs UI serving
5. Allows for future mobile app to use same backend API

## Complexity Tracking

> **No constitutional violations identified at planning stage**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

**Notes**:
- Soft delete with 30-day trash retention (FR-009E - FR-009J) adds complexity but justified by user error prevention
- AI service retry logic (FR-088 - FR-094) adds complexity but essential for reliability
- 7-chapter document structure is inherent to educational quality requirements (non-negotiable)
- All complexity aligns with YAGNI - features have concrete use cases in spec
