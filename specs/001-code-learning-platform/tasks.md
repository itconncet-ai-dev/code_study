# Tasks: AI Code Learning Platform - Phase 1 MVP

**Feature Branch**: `001-code-learning-platform`
**Created**: 2025-11-15
**Organization**: Vertical Slice - Each feature completed end-to-end before moving to next

**Input**: Design documents from `/specs/001-code-learning-platform/`
- plan.md (technical stack, architecture)
- spec.md (5 user stories with priorities)
- data-model.md (PostgreSQL schema)
- contracts/api-spec.yaml (REST API specification)
- research.md (technology decisions)
- quickstart.md (development setup)

**Vertical Slice Approach**: Each functional area is completed from backend models → API → frontend UI → browser testing before starting the next feature. This ensures working, demonstrable features at each checkpoint.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Exact file paths included in descriptions

## Path Conventions

Web application structure (from plan.md):
- **Backend**: `backend/src/` (Python/FastAPI)
- **Frontend**: `frontend/src/` (React/TypeScript)
- **Tests**: `backend/tests/`, `frontend/tests/`
- **Storage**: `storage/uploads/` (code files)
- **Docs**: `docs/task-reports/` (TDD task reports)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and development environment setup

- [X] T001 Create project directory structure per plan.md (backend/, frontend/, storage/, docs/)
- [X] T001A Create docs/task-reports/ directory per constitution I-B requirement
- [X] T002 Initialize backend Python project with FastAPI dependencies in backend/requirements.txt
- [X] T003 Initialize frontend React project with Vite and TypeScript in frontend/
- [X] T004 [P] Create Docker Compose configuration for PostgreSQL, Redis in docker-compose.yml
- [X] T005 [P] Create environment configuration template in .env.example
- [X] T006 [P] Configure linting and formatting (Ruff, Black for Python; ESLint, Prettier for TypeScript)
- [X] T007 [P] Setup Git ignore patterns for node_modules, venv, .env, storage/uploads/

**Checkpoint**: Development environment ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & Migrations

- [X] T008 Setup Alembic migrations framework in backend/alembic/
- [X] T009 Create initial database migration with all entity schemas from data-model.md in backend/alembic/versions/001_initial_schema.py
- [X] T010 [P] Implement database connection and session management in backend/src/db/session.py
- [X] T011 [P] Create database configuration and connection pooling in backend/src/db/config.py

### Base Infrastructure

- [X] T012 [P] Implement JWT token utilities (generate, verify, decode) in backend/src/utils/jwt.py
- [X] T013 [P] Implement password hashing utilities (bcrypt) in backend/src/utils/security.py
- [X] T014 [P] Setup FastAPI app initialization with CORS, middleware in backend/src/main.py
- [X] T015 [P] Create API router structure (/api/v1) in backend/src/api/__init__.py
- [X] T016 [P] Implement error handling middleware and exception schemas in backend/src/api/exceptions.py
- [X] T017 [P] Setup Celery app and Redis connection in backend/src/tasks/celery_app.py

### Frontend Foundation

- [X] T018 [P] Setup React Router with route structure in frontend/src/App.tsx
- [X] T019 [P] Configure TanStack Query client in frontend/src/lib/queryClient.ts
- [X] T020 [P] Create API client base with axios configuration in frontend/src/services/api-client.ts
- [X] T021 [P] Setup Zustand auth store for JWT state in frontend/src/stores/auth-store.ts
- [X] T022 [P] Configure Tailwind CSS and install shadcn/ui components in frontend/

### TDD Workflow (Constitution Requirement)

**MANDATORY for ALL implementation tasks (Phases 3-10)**: Follow the RED-GREEN-REFACTOR cycle

**🔴 RED Phase** (Write Test First):
1. Write a failing test that specifies the expected behavior
2. Run the test and verify it FAILS (proves test is valid)
3. Commit with message: `test: [feature name] - RED`

**🟢 GREEN Phase** (Minimal Implementation):
1. Write the SIMPLEST code to make the test pass
2. Run the test and verify it PASSES
3. Commit with message: `feat: [feature name] - GREEN`

**🔵 REFACTOR Phase** (Improve Code):
1. Improve code quality (readability, performance, structure)
2. Run tests and verify they STILL pass
3. Commit with message: `refactor: [feature name] - REFACTOR`

**Task Report Requirement** (Constitution I-B):
- After completing each task, create a Korean-language report in `docs/task-reports/TASK-{number}-{title}.md`
- Report must explain: what was built, why this approach, how it works, how it was tested (TDD cycle), files modified, related concepts, caveats, next steps
- Use everyday Korean language with real-world analogies (no technical jargon)
- Length: 300-500 words

**Tests are IMMUTABLE**: If a test fails, fix the IMPLEMENTATION, never modify the test to make it pass.

**Checkpoint**: Foundation ready - vertical slice implementation can now begin

---

## Phase 3: Authentication Slice (User Story 1 Dependency) 🔐

**Goal**: Complete authentication system from database to browser

**Vertical Slice**: Backend models → API endpoints → Frontend UI → Browser testing

### Backend: Authentication Models & Services

- [X] T023 [P] Create User SQLAlchemy model in backend/src/models/user.py
- [X] T024 [P] Create RefreshToken SQLAlchemy model in backend/src/models/refresh_token.py
- [X] T025 Implement UserService (register, login, logout) in backend/src/services/auth/user_service.py
- [X] T026 Implement TokenService (create access/refresh tokens, verify, rotate) in backend/src/services/auth/token_service.py
- [X] T027 [P] Create authentication dependency for route protection in backend/src/api/dependencies.py

### Backend: Authentication API Endpoints

- [X] T028 Implement POST /auth/register endpoint in backend/src/api/auth.py
- [X] T029 Implement POST /auth/login endpoint in backend/src/api/auth.py
- [X] T029A Implement GET /auth/me endpoint (current user) in backend/src/api/auth.py
- [X] T030 Implement POST /auth/logout endpoint in backend/src/api/auth.py
- [X] T031 Implement POST /auth/refresh endpoint in backend/src/api/auth.py

### Frontend: Authentication UI

- [X] T032 [P] Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx
- [X] T033 [P] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx
- [X] T034 Create authentication service (register, login, logout API calls) in frontend/src/services/auth-service.ts
- [X] T035 Implement Register page in frontend/src/pages/Register.tsx
- [X] T036 Implement Login page in frontend/src/pages/Login.tsx
- [X] T037 Create ProtectedRoute wrapper component in frontend/src/components/auth/ProtectedRoute.tsx
- [X] T038 Implement auto token refresh logic in frontend/src/hooks/useAuth.ts

### Browser Testing: Authentication Flow

- [X] T039 Manual browser test: Register new user → verify success response and redirect
- [X] T040 Manual browser test: Login with valid credentials → verify dashboard access
- [X] T041 Manual browser test: Access protected route without login → verify redirect to login
- [X] T042 Manual browser test: Logout → verify cookies cleared and redirect to login

**Checkpoint**: Complete authentication system working end-to-end in browser

---

## Phase 4: Projects Slice (User Story 4 - P4) 📁

**Goal**: Project management from creation to display

**Vertical Slice**: Backend models → API → Frontend UI → Browser testing

### Backend: Project Models & Services

- [X] T043 Create Project SQLAlchemy model with soft delete fields in backend/src/models/project.py
- [X] T044 Implement ProjectService (create, get, update, soft delete) in backend/src/services/project_service.py
- [X] T045 Implement project ownership validation in backend/src/services/project_service.py

### Backend: Project API Endpoints

- [X] T046 Implement GET /projects endpoint in backend/src/api/projects.py
- [X] T047 Implement POST /projects endpoint in backend/src/api/projects.py
- [X] T048 Implement GET /projects/{project_id} endpoint in backend/src/api/projects.py
- [X] T049 Implement PATCH /projects/{project_id} endpoint in backend/src/api/projects.py
- [X] T050 Implement DELETE /projects/{project_id} (soft delete) endpoint in backend/src/api/projects.py

### Frontend: Project UI

- [X] T051 [P] Create ProjectCard component in frontend/src/components/project/ProjectCard.tsx
- [X] T052 [P] Create CreateProjectModal component in frontend/src/components/project/CreateProjectModal.tsx
- [X] T053 Create project service (CRUD API calls) in frontend/src/services/project-service.ts
- [X] T054 Implement Dashboard page (project list view) in frontend/src/pages/Dashboard.tsx
- [X] T055 Implement ProjectDetail page with task timeline placeholder in frontend/src/pages/ProjectDetail.tsx
- [X] T056 Add project creation flow in Dashboard page

### Browser Testing: Project Management

- [X] T057 Manual browser test: Create new project → verify appears in dashboard
- [X] T058 Manual browser test: View project detail → verify project info displays
- [X] T059 Manual browser test: Edit project title → verify update persists
- [X] T060 Manual browser test: Delete project → verify soft delete and trash visibility

**Checkpoint**: Complete project management system working in browser

---

## Phase 5: Tasks & Code Upload Slice (User Story 1 - P1) 🎯 MVP CORE

**Goal**: Task creation and code upload system

**Vertical Slice**: Backend models → API → Frontend UI → Browser testing

### Backend: Task & Code Models

- [X] T061 [P] Create Task SQLAlchemy model with sequential task_number in backend/src/models/task.py
- [X] T062 [P] Create UploadedCode SQLAlchemy model in backend/src/models/uploaded_code.py
- [X] T063 [P] Create CodeFile SQLAlchemy model in backend/src/models/code_file.py
- [X] T064 Implement file validation utilities (extension, size, binary detection) in backend/src/utils/file_validator.py
- [X] T065 Implement language detection service using Pygments in backend/src/services/code_analysis/language_detector.py
- [X] T066 Implement code complexity analyzer in backend/src/services/code_analysis/complexity_analyzer.py

### Backend: Code Upload Services

- [X] T067 Implement file storage service (save to storage/uploads/{user_id}/{task_id}/) in backend/src/services/code_analysis/file_storage.py
- [X] T068 Implement TaskService (create, get, update, soft delete with task_number auto-increment) in backend/src/services/task_service.py
- [X] T069 Implement CodeUploadService (handle file/folder/paste uploads) in backend/src/services/code_analysis/code_upload_service.py

### Backend: Task API Endpoints

- [X] T070 Implement GET /projects/{project_id}/tasks endpoint in backend/src/api/tasks.py
- [X] T071 Implement POST /projects/{project_id}/tasks (multipart/form-data upload) endpoint in backend/src/api/tasks.py
- [X] T072 Implement GET /tasks/{task_id} endpoint in backend/src/api/tasks.py
- [X] T073 Implement PATCH /tasks/{task_id} endpoint in backend/src/api/tasks.py
- [X] T074 Implement DELETE /tasks/{task_id} (soft delete) endpoint in backend/src/api/tasks.py
- [X] T075 Implement GET /tasks/{task_id}/code endpoint in backend/src/api/tasks.py

### Frontend: Code Upload UI

- [X] T076 [P] Create FileUpload component (drag-and-drop, file picker) in frontend/src/components/upload/FileUpload.tsx
- [X] T077 [P] Create FolderUpload component (preserves structure) in frontend/src/components/upload/FolderUpload.tsx
- [X] T078 [P] Create PasteCode component (textarea + language selector) in frontend/src/components/upload/PasteCode.tsx
- [X] T079 [P] Create TaskCard component for task timeline display in frontend/src/components/task/TaskCard.tsx
- [X] T080 Create task service (CRUD + upload API calls) in frontend/src/services/task-service.ts
- [X] T081 Implement CreateTaskModal with 3 upload methods in frontend/src/components/task/CreateTaskModal.tsx
- [X] T082 Add task list and creation to ProjectDetail page in frontend/src/pages/ProjectDetail.tsx
- [X] T083 Implement TaskDetail page skeleton with tabs (Document, Practice, Q&A) in frontend/src/pages/TaskDetail.tsx

### Browser Testing: Task & Code Upload

- [X] T084 Manual browser test: Create task with single file upload → verify task created with Task 1 number
- [X] T085 Manual browser test: Create task with folder upload → verify folder structure preserved
- [X] T086 Manual browser test: Create task with paste code → verify language detection
- [X] T087 Manual browser test: Upload 11MB file → verify rejection with error message
- [X] T088 Manual browser test: Upload binary file → verify rejection with error message
- [X] T089 Manual browser test: Create 3 tasks in sequence → verify task numbers are 1, 2, 3

**Checkpoint**: Complete task creation and code upload system working in browser

---

## Phase 6: Document Generation Slice (User Story 1 - P1 Continued) 📚 MVP CORE

**Goal**: AI-powered learning document generation

**Vertical Slice**: Backend models → Celery tasks → API → Frontend UI → Browser testing

### Backend: Document Models & AI Integration

- [X] T090 Create LearningDocument SQLAlchemy model with JSONB content in backend/src/models/learning_document.py
- [X] T091 Implement Gemini API client wrapper in backend/src/services/ai/gemini_client.py
- [X] T092 Implement prompt templates for 7-chapter document generation in backend/src/services/ai/prompts.py
- [X] T093 Implement DocumentGenerationService with retry logic in backend/src/services/document/document_generation_service.py

### Backend: Async Document Generation

- [x] T094 Implement Celery task for async document generation in backend/src/tasks/document_generation.py
- [x] T095 Implement document generation queue with status tracking in backend/src/services/document/document_queue_service.py
- [x] T096 Add document generation trigger after code upload in TaskService

### Backend: Document API Endpoints

- [X] T097 Implement GET /tasks/{task_id}/document endpoint in backend/src/api/documents.py
- [X] T098 Implement GET /tasks/{task_id}/document/status endpoint in backend/src/api/documents.py

### Frontend: Document Viewer UI

- [X] T099 [P] Install and configure Monaco Editor in frontend/
- [X] T100 [P] Create CodePanel component with syntax highlighting in frontend/src/components/document/CodePanel.tsx
- [X] T101 [P] Create ExplanationPanel component with chapter navigation in frontend/src/components/document/ExplanationPanel.tsx
- [X] T102 [P] Create Chapter1Summary component in frontend/src/components/document/chapters/Chapter1.tsx
- [X] T103 [P] Create Chapter2Prerequisites component (concept cards) in frontend/src/components/document/chapters/Chapter2.tsx
- [X] T104 [P] Create Chapter4LineByLine component in frontend/src/components/document/chapters/Chapter4.tsx
- [X] T105 Create DocumentViewer component (2-column layout with sync scroll) in frontend/src/components/document/DocumentViewer.tsx
- [X] T106 Create document service (fetch document, poll status) in frontend/src/services/document-service.ts
- [X] T107 Implement loading state with progress indicator in DocumentViewer
- [X] T108 Add Document tab content to TaskDetail page in frontend/src/pages/TaskDetail.tsx

### Browser Testing: Document Generation

- [ ] T109 Manual browser test: Upload code → verify "Generating..." status displays with estimated time
- [ ] T110 Manual browser test: Wait for generation → verify 7-chapter document loads
- [ ] T111 Manual browser test: Navigate chapters → verify chapter highlighting and content display
- [ ] T112 Manual browser test: Scroll code panel → verify explanation panel scrolls to corresponding section
- [ ] T113 Manual browser test: Check Chapter 2 → verify 5 concept cards with analogies display
- [ ] T114 Manual browser test: Trigger AI service failure → verify retry message and error handling

**Checkpoint**: Complete document generation system working end-to-end in browser

---

## Phase 7: Practice Problems Slice (User Story 2 - P2) ✏️

**Goal**: Practice problem generation and completion tracking

**Vertical Slice**: Backend models → Celery tasks → API → Frontend UI → Browser testing

### Backend: Practice Models & Generation

- [ ] T115 Create PracticeProblem SQLAlchemy model in backend/src/models/practice_problem.py
- [ ] T116 Implement practice problem generation prompts in backend/src/services/ai/prompts.py
- [ ] T117 Implement PracticeGenerationService (generate 5 problems with hints) in backend/src/services/practice/practice_generation_service.py
- [ ] T118 Implement Celery task for async practice generation in backend/src/tasks/practice_generation.py
- [ ] T119 Add practice generation trigger after document generation in document_generation.py

### Backend: Practice API Endpoints

- [ ] T120 Implement GET /tasks/{task_id}/practice endpoint in backend/src/api/practice.py
- [ ] T121 Implement GET /tasks/{task_id}/practice/{problem_number} endpoint in backend/src/api/practice.py

### Frontend: Practice UI

- [ ] T122 [P] Create ProblemCard component with difficulty badge in frontend/src/components/practice/ProblemCard.tsx
- [ ] T123 [P] Create HintReveal component (progressive hints) in frontend/src/components/practice/HintReveal.tsx
- [ ] T124 [P] Create SolutionDisplay component (hidden until requested) in frontend/src/components/practice/SolutionDisplay.tsx
- [ ] T125 Create PracticeViewer component with 5 problems in frontend/src/components/practice/PracticeViewer.tsx
- [ ] T126 Create practice service (fetch problems) in frontend/src/services/practice-service.ts
- [ ] T127 Add Practice tab content to TaskDetail page in frontend/src/pages/TaskDetail.tsx

### Browser Testing: Practice Problems

- [ ] T128 Manual browser test: Navigate to Practice tab → verify 5 problems display with types (Follow Along, Fill Blanks, Modify, Debug, Create)
- [ ] T129 Manual browser test: Click "Show Hints" → verify progressive hint reveal
- [ ] T130 Manual browser test: Click "Show Solution" → verify model solution displays
- [ ] T131 Manual browser test: Mark problem as complete → verify completion badge appears

**Checkpoint**: Complete practice problem system working in browser

---

## Phase 8: Q&A System Slice (User Story 3 - P3) 💬

**Goal**: Contextual question and answer system

**Vertical Slice**: Backend models → AI integration → API → Frontend UI → Browser testing

### Backend: Q&A Models & Services

- [ ] T132 Create Question SQLAlchemy model in backend/src/models/question.py
- [ ] T133 Implement Q&A generation prompts (context-aware) in backend/src/services/ai/prompts.py
- [ ] T134 Implement QuestionService (create, answer with Gemini, get history) in backend/src/services/qa/question_service.py
- [ ] T135 Implement context extraction from document and code in backend/src/services/qa/context_builder.py

### Backend: Q&A API Endpoints

- [ ] T136 Implement GET /tasks/{task_id}/questions endpoint in backend/src/api/qa.py
- [ ] T137 Implement POST /tasks/{task_id}/questions endpoint in backend/src/api/qa.py
- [ ] T138 Implement POST /questions/{question_id}/feedback endpoint in backend/src/api/qa.py

### Frontend: Q&A UI

- [ ] T139 [P] Create QuestionInput component with code selection support in frontend/src/components/qa/QuestionInput.tsx
- [ ] T140 [P] Create QuestionHistoryCard component in frontend/src/components/qa/QuestionHistoryCard.tsx
- [ ] T141 [P] Create AnswerDisplay component with formatted answer in frontend/src/components/qa/AnswerDisplay.tsx
- [ ] T142 Create QAPanel component (floating panel, conversation history) in frontend/src/components/qa/QAPanel.tsx
- [ ] T143 Create qa service (ask question, get history, submit feedback) in frontend/src/services/qa-service.ts
- [ ] T144 Add Q&A tab content to TaskDetail page in frontend/src/pages/TaskDetail.tsx
- [ ] T145 Implement code selection → "Ask About This" flow in DocumentViewer

### Browser Testing: Q&A System

- [ ] T146 Manual browser test: Type question without code selection → verify answer generated in <10 seconds
- [ ] T147 Manual browser test: Select code snippet → click "Ask About This" → verify code included in context
- [ ] T148 Manual browser test: Ask 3 questions → verify conversation history persists and displays
- [ ] T149 Manual browser test: Mark answer as helpful → verify feedback recorded
- [ ] T150 Manual browser test: Ask question during retry → verify "Response delayed, retrying..." message

**Checkpoint**: Complete Q&A system working in browser

---

## Phase 9: Progress Tracking Slice (User Story 5 - P5) 📊

**Goal**: Learning progress tracking and display

**Vertical Slice**: Backend models → API → Frontend UI → Browser testing

### Backend: Progress Models & Services

- [ ] T151 Create Progress SQLAlchemy model with JSONB arrays in backend/src/models/progress.py
- [ ] T152 Implement ProgressService (track chapters, problems, completion) in backend/src/services/progress/progress_service.py
- [ ] T153 Implement progress calculation utilities (percentage, completion status) in backend/src/services/progress/progress_calculator.py

### Backend: Progress API Endpoints

- [ ] T154 Implement GET /tasks/{task_id}/progress endpoint in backend/src/api/progress.py
- [ ] T155 Implement PATCH /tasks/{task_id}/progress endpoint in backend/src/api/progress.py

### Frontend: Progress UI

- [ ] T156 [P] Create ProgressBar component in frontend/src/components/progress/ProgressBar.tsx
- [ ] T157 [P] Create ChapterCheckbox component in frontend/src/components/progress/ChapterCheckbox.tsx
- [ ] T158 [P] Create TaskCompletionBadge component (✅ ⏳ ⬜) in frontend/src/components/progress/TaskCompletionBadge.tsx
- [ ] T159 Create progress service (get, update progress) in frontend/src/services/progress-service.ts
- [ ] T160 Add chapter completion checkboxes to DocumentViewer in frontend/src/components/document/DocumentViewer.tsx
- [ ] T161 Add problem completion checkboxes to PracticeViewer in frontend/src/components/practice/PracticeViewer.tsx
- [ ] T162 Add task completion button to TaskDetail page in frontend/src/pages/TaskDetail.tsx
- [ ] T163 Add progress indicators to ProjectCard in frontend/src/components/project/ProjectCard.tsx
- [ ] T164 Add progress indicators to TaskCard in frontend/src/components/task/TaskCard.tsx

### Browser Testing: Progress Tracking

- [ ] T165 Manual browser test: Mark 3 chapters complete → verify progress bar shows 43% (3/7)
- [ ] T166 Manual browser test: Mark 5 practice problems complete → verify progress shows 5/5
- [ ] T167 Manual browser test: Logout and login → verify progress persists across sessions
- [ ] T168 Manual browser test: Mark task complete → verify ✅ badge and completion date display
- [ ] T169 Manual browser test: View project dashboard → verify task completion count (2/5 tasks)

**Checkpoint**: Complete progress tracking system working in browser

---

## Phase 10: Trash & Soft Delete Slice 🗑️

**Goal**: Trash management with 30-day retention

**Vertical Slice**: Backend services → API → Frontend UI → Browser testing

### Backend: Trash Services

- [ ] T170 Implement trash restoration service in backend/src/services/trash_service.py
- [ ] T171 Implement permanent deletion service with cascade in backend/src/services/trash_service.py
- [ ] T172 Implement Celery scheduled task for 30-day auto-delete in backend/src/tasks/trash_cleanup.py

### Backend: Trash API Endpoints

- [ ] T173 Implement GET /trash endpoint in backend/src/api/trash.py
- [ ] T174 Implement POST /trash/projects/{project_id}/restore endpoint in backend/src/api/trash.py
- [ ] T175 Implement DELETE /trash/projects/{project_id}/permanent-delete endpoint in backend/src/api/trash.py
- [ ] T176 Implement POST /trash/tasks/{task_id}/restore endpoint in backend/src/api/trash.py
- [ ] T177 Implement DELETE /trash/tasks/{task_id}/permanent-delete endpoint in backend/src/api/trash.py

### Frontend: Trash UI

- [ ] T178 [P] Create TrashedProjectCard component with restore button in frontend/src/components/trash/TrashedProjectCard.tsx
- [ ] T179 [P] Create TrashedTaskCard component with restore button in frontend/src/components/trash/TrashedTaskCard.tsx
- [ ] T180 Create trash service (list, restore, permanent delete) in frontend/src/services/trash-service.ts
- [ ] T181 Implement Trash page with projects and tasks sections in frontend/src/pages/Trash.tsx
- [ ] T182 Add "View Trash" link to Dashboard navigation in frontend/src/pages/Dashboard.tsx

### Browser Testing: Trash Management

- [ ] T183 Manual browser test: Delete project → verify appears in trash with 30-day countdown
- [ ] T184 Manual browser test: Restore project from trash → verify returns to active projects
- [ ] T185 Manual browser test: Permanently delete task → verify confirmation dialog and complete removal
- [ ] T186 Manual browser test: Wait for scheduled task → verify items deleted after 30 days (mock)

**Checkpoint**: Complete trash management system working in browser

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and production readiness

### Documentation & Setup

- [ ] T187 [P] Create seed_test_user.py script in backend/scripts/
- [ ] T188 [P] Create seed_test_data.py script (sample projects/tasks) in backend/scripts/
- [ ] T189 [P] Update quickstart.md with actual setup steps and troubleshooting
- [ ] T190 [P] Create API documentation examples in docs/api-examples.md

### Error Handling & Validation

- [ ] T191 [P] Add comprehensive error messages for all validation failures
- [ ] T192 [P] Implement rate limiting on auth endpoints (5 attempts / 15 min)
- [ ] T193 [P] Add request logging middleware in backend/src/api/middleware.py
- [ ] T194 [P] Implement global error boundary in frontend/src/components/ErrorBoundary.tsx

### Performance & Optimization

- [ ] T195 [P] Add database indexes for user_id, task_id, deletion_status queries
- [ ] T196 [P] Implement React.lazy code splitting for heavy components (Monaco Editor)
- [ ] T197 [P] Add API response caching with React Query stale-while-revalidate
- [ ] T198 [P] Optimize document JSONB queries with PostgreSQL indexes

### Security Hardening

- [ ] T199 [P] Implement CSRF protection with double-submit cookie pattern
- [ ] T200 [P] Add XSS sanitization for user-generated content
- [ ] T201 [P] Configure secure cookie flags (HttpOnly, Secure, SameSite=Strict)
- [ ] T202 [P] Implement file upload virus scanning placeholder (future: ClamAV)

### UI Polish

- [ ] T203 [P] Add loading skeletons for all async data loading states
- [ ] T204 [P] Implement toast notifications for success/error messages
- [ ] T205 [P] Add responsive design adjustments for tablet viewport
- [ ] T206 [P] Implement dark mode toggle (optional enhancement)

### Testing & Quality

- [ ] T207 [P] Write backend unit tests for critical services (target 80% coverage) in backend/tests/unit/
- [ ] T208 [P] Write frontend component tests for critical UI (target 80% coverage) in frontend/tests/
- [ ] T209 [P] Create integration tests for user workflows in backend/tests/integration/
- [ ] T210 Run complete end-to-end browser test suite across all features

### Deployment Preparation

- [ ] T211 [P] Create production environment configuration template
- [ ] T212 [P] Setup database backup script for PostgreSQL
- [ ] T213 [P] Configure Redis persistence (AOF or RDB)
- [ ] T214 [P] Create Nginx reverse proxy configuration
- [ ] T215 Validate quickstart.md setup on clean environment

**Checkpoint**: Production-ready MVP complete

---

## Dependencies & Execution Order

### Phase Dependencies (Vertical Slice Order)

1. **Phase 1: Setup** - No dependencies, start immediately
2. **Phase 2: Foundational** - Depends on Setup, BLOCKS all vertical slices
3. **Phase 3: Authentication** - Depends on Foundational, BLOCKS all protected features
4. **Phase 4: Projects** - Depends on Authentication (required for ownership)
5. **Phase 5: Tasks & Code Upload** - Depends on Projects (tasks belong to projects)
6. **Phase 6: Document Generation** - Depends on Tasks (generates documents for tasks)
7. **Phase 7: Practice Problems** - Depends on Document Generation (practice based on document)
8. **Phase 8: Q&A System** - Depends on Document Generation (questions about document/code)
9. **Phase 9: Progress Tracking** - Depends on Document, Practice, Q&A (tracks all activities)
10. **Phase 10: Trash** - Depends on Projects & Tasks (manages deleted items)
11. **Phase 11: Polish** - Depends on all features being complete

### User Story Mapping to Phases

- **User Story 1 (P1)**: Phases 5 + 6 (Upload Code + Document Generation) - MVP CORE
- **User Story 2 (P2)**: Phase 7 (Practice Problems)
- **User Story 3 (P3)**: Phase 8 (Q&A System)
- **User Story 4 (P4)**: Phase 4 (Project Management)
- **User Story 5 (P5)**: Phase 9 (Progress Tracking)

### Critical Path for MVP

**Minimum viable product (User Story 1 only)**:
1. Phase 1: Setup
2. Phase 2: Foundational
3. Phase 3: Authentication
4. Phase 4: Projects
5. Phase 5: Tasks & Code Upload
6. Phase 6: Document Generation

After Phase 6 completion → **Functional MVP that demonstrates core value proposition**

### Parallel Opportunities

**Within each phase**, tasks marked [P] can run in parallel:
- Phase 1: T003, T004, T005, T006, T007 (setup configs)
- Phase 2: T010-T011 (DB), T012-T017 (backend utils), T018-T022 (frontend foundation)
- Phase 3: T023-T024 (models), T032-T033 (UI components)
- Phase 4: T051-T052 (UI components)
- Phase 5: T061-T063 (models), T076-T079 (upload components)
- Phase 6: T099-T104 (document UI components)
- Phase 7: T122-T124 (practice UI components)
- Phase 8: T139-T141 (Q&A UI components)
- Phase 9: T156-T158 (progress UI components)
- Phase 10: T178-T179 (trash UI components)
- Phase 11: All polish tasks can run in parallel

**Between phases**: Once a phase is complete, the next phase can begin immediately (no blocking dependencies within vertical slice approach)

---

## Vertical Slice Validation Points

After each phase, perform end-to-end browser testing to validate the complete feature:

### Phase 3 Complete → Authentication Working
- ✅ User can register, login, logout in browser
- ✅ Protected routes redirect to login
- ✅ Tokens refresh automatically

### Phase 4 Complete → Project Management Working
- ✅ User can create, view, edit, delete projects
- ✅ Project list displays with accurate counts
- ✅ Soft delete moves to trash

### Phase 5 Complete → Code Upload Working
- ✅ User can upload code via 3 methods
- ✅ Tasks display with sequential numbers
- ✅ File validation works correctly

### Phase 6 Complete → **MVP ACHIEVED** 🎯
- ✅ Document generation completes within 3 minutes
- ✅ 7-chapter document displays beautifully
- ✅ Code and explanation panels synchronized
- ✅ All Chapter 2 concepts have analogies

### Phase 7 Complete → Practice System Working
- ✅ 5 practice problems generated per task
- ✅ Hints reveal progressively
- ✅ Solutions display on request

### Phase 8 Complete → Q&A System Working
- ✅ Questions answered within 10 seconds
- ✅ Context-aware responses
- ✅ Conversation history persists

### Phase 9 Complete → Progress Tracking Working
- ✅ Chapter completion tracked accurately
- ✅ Progress persists across sessions
- ✅ Task completion badges display

### Phase 10 Complete → Trash Management Working
- ✅ Deleted items move to trash
- ✅ Restoration works correctly
- ✅ Permanent deletion removes all data

### Phase 11 Complete → **PRODUCTION READY** 🚀
- ✅ 80% test coverage achieved
- ✅ Security hardening complete
- ✅ Performance optimized
- ✅ Documentation up-to-date

---

## Implementation Strategy

### Recommended Approach: Sequential Vertical Slices

Complete each phase fully before moving to the next:

1. **Phase 1 → Phase 2**: Setup foundation (2-3 days)
2. **Phase 3**: Authentication slice (1-2 days)
3. **Phase 4**: Projects slice (1-2 days)
4. **Phase 5**: Code upload slice (2-3 days)
5. **Phase 6**: Document generation slice (3-4 days) → **MVP DEMO**
6. **Phase 7**: Practice slice (2 days)
7. **Phase 8**: Q&A slice (2 days)
8. **Phase 9**: Progress slice (1-2 days)
9. **Phase 10**: Trash slice (1 day)
10. **Phase 11**: Polish (2-3 days) → **PRODUCTION READY**

**Total Estimated Time**: 18-24 days for full implementation

### Stop Points for Validation

- **After Phase 6**: Validate MVP with real users (User Story 1 complete)
- **After Phase 9**: Validate full feature set (All user stories complete)
- **After Phase 11**: Production deployment

---

## Notes

- **[P] tasks**: Different files, no dependencies, can run simultaneously
- **[Story] labels**: Map to user stories (US1-US5) for traceability
- **Vertical slice approach**: Each phase delivers working feature from database to browser
- **TDD requirement**: Follow RED-GREEN-REFACTOR cycle per constitution
- **Task reports**: Document each task completion in docs/task-reports/ (Korean)
- **Commit frequency**: Commit after each task or logical group
- **Browser testing**: Critical for vertical slice validation - ensures feature works end-to-end
- **MVP scope**: Phases 1-6 deliver core value (User Story 1)
- **Incremental delivery**: Each phase adds demonstrable value

---

## Total Task Count: 216 tasks

- Setup: 8 tasks (including T001A for docs/task-reports/ directory)
- Foundational: 15 tasks
- Authentication: 20 tasks
- Projects: 18 tasks
- Tasks & Code Upload: 29 tasks
- Document Generation: 25 tasks
- Practice Problems: 17 tasks
- Q&A System: 18 tasks
- Progress Tracking: 19 tasks
- Trash Management: 18 tasks
- Polish: 29 tasks

**Parallel opportunities identified**: 67 tasks marked [P] (31% of total)

**Independent test criteria**: 11 validation checkpoints throughout implementation

**Suggested MVP scope**: Phases 1-6 (109 tasks) → Core value proposition demonstrated
