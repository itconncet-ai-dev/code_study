# Research: AI Code Learning Platform - Phase 1 MVP

**Date**: 2025-11-15
**Feature**: AI Code Learning Platform
**Purpose**: Resolve technical unknowns and establish implementation approach

## Research Tasks

### 1. Backend Language & Framework Selection

**Decision**: Python 3.11+ with FastAPI

**Rationale**:
- **Python chosen for**:
  - Best ecosystem for AI/LLM integration (OpenAI SDK, Anthropic SDK, LangChain)
  - Excellent libraries for code analysis (ast, tokenize, pygments for syntax highlighting)
  - Strong async support for concurrent AI operations (asyncio, httpx)
  - Educational codebase aligns with target users learning Python

- **FastAPI chosen for**:
  - Modern async/await support (critical for AI operations)
  - Automatic OpenAPI documentation (supports contract-first development)
  - Built-in request validation (Pydantic models)
  - High performance (Starlette + uvicorn)
  - Easy WebSocket support for future real-time features

**Alternatives Considered**:
- **Node.js + Express/NestJS**: Rejected because Python has superior AI/ML ecosystem
- **Django**: Rejected because FastAPI offers better async performance for AI operations
- **Go**: Rejected due to less mature LLM client libraries and educational complexity

**Best Practices**:
- Use Pydantic models for request/response validation
- Implement dependency injection for services (FastAPI dependencies)
- Structure as modular services (auth, code_analysis, ai, document, etc.)
- Use async database ORM (SQLAlchemy 2.0+ async or Tortoise-ORM)

---

### 2. Database Selection

**Decision**: PostgreSQL 15+ with SQLAlchemy 2.0 (async)

**Rationale**:
- **PostgreSQL chosen for**:
  - ACID compliance for user data integrity
  - JSONB support for flexible document storage (7-chapter structure)
  - Full-text search capabilities (for future search features)
  - Excellent Python support (asyncpg)
  - Row-level security for multi-tenant data isolation

- **SQLAlchemy 2.0+ chosen for**:
  - Modern async support
  - Type-safe query builder
  - Alembic migrations for version control
  - ORM abstractions without losing SQL power

**Alternatives Considered**:
- **MongoDB**: Rejected because relational structure (User → Project → Task) benefits from SQL
- **SQLite**: Rejected due to limited concurrency support for AI operations
- **MySQL**: Rejected because PostgreSQL has better JSONB and array support

**Data Storage Strategy**:
- **User data, Projects, Tasks**: PostgreSQL tables
- **Uploaded code files**: Object storage (local filesystem for MVP, S3-compatible for production)
- **Generated documents**: PostgreSQL JSONB (7 chapters as structured JSON)
- **Progress tracking**: PostgreSQL (relational for efficient queries)

**Best Practices**:
- Use connection pooling (asyncpg pool)
- Implement soft deletes with indexes on deletion_status
- Store file metadata in DB, actual files in object storage
- Use database transactions for data consistency

---

### 3. LLM Integration for Content Generation

**Decision**: Google Gemini 3 Flash Preview API

**Rationale**:
- **Gemini 3 Flash Preview chosen for**:
  - Superior code understanding across multiple languages
  - Excellent at generating beginner-friendly explanations
  - Native JSON mode support for structured output (7-chapter format)
  - Strong performance on Korean and multilingual content
  - Very fast response times (optimized for speed)
  - Cost-effective compared to other enterprise models
  - Long context window (1M tokens) for large code files
  - Strong multimodal capabilities (future: image explanations)

**Implementation Approach**:
- Primary: Google Gemini 3 Flash Preview (gemini-3-flash-preview)
- Same model for both document generation and Q&A (unified, cost-effective)
- Retry strategy: Exponential backoff up to 3 retries (per clarification)
- Queue system: Celery + Redis for async document generation

**Alternatives Considered**:
- **OpenAI GPT-4**: More expensive, similar quality for educational content
- **Anthropic Claude**: Excellent but higher cost for high-volume usage
- **Local LLM**: Rejected due to infrastructure complexity and quality concerns

**Prompt Engineering Strategy**:
- **Document Generation**:
  - System instruction: "You are an expert teacher explaining code to complete beginners with zero programming knowledge"
  - Use JSON mode for structured 7-chapter output
  - Include examples, analogies, and step-by-step breakdowns
  - Leverage long context window for full file analysis

- **Practice Problems**:
  - Generate 5 problems with increasing difficulty
  - Include hints, solutions, and expected outputs
  - Context-aware based on document content

- **Q&A System**:
  - Context-aware prompts including code snippet and document context
  - Response format: explanation + analogy + example + related concepts
  - Fast responses (typically <5 seconds with Gemini Flash)

**Cost Optimization**:
- Gemini 3 Flash Preview is already cost-optimized (cheaper than GPT-3.5)
- Cache common concept explanations using Gemini's context caching
- Batch similar requests when possible
- Use streaming for real-time Q&A responses (future)

**Best Practices**:
- Implement rate limiting (respects Google AI quotas)
- Add request timeouts (20s for Q&A, 3min for documents)
- Log all API calls for debugging and cost tracking
- Handle API errors gracefully with user-friendly messages
- Use safety settings to ensure beginner-appropriate content

---

### 4. Frontend Framework Selection

**Decision**: React 18+ with TypeScript and Vite

**Rationale**:
- **React chosen for**:
  - Large ecosystem for code editor components (Monaco, CodeMirror)
  - Excellent state management options (Zustand, Redux Toolkit)
  - Strong TypeScript support
  - Component reusability for complex UI (2-column layout, Q&A panel)

- **TypeScript chosen for**:
  - Type safety reduces bugs
  - Better IDE support
  - Self-documenting code (important for educational project)

- **Vite chosen for**:
  - Fast development server (HMR)
  - Optimized production builds
  - Modern tooling (ESM, tree-shaking)

**Alternatives Considered**:
- **Vue 3**: Excellent but React has better code editor ecosystem
- **Svelte**: Smaller ecosystem for complex components
- **Next.js**: Over-engineered for desktop-first SPA requirements

**Key Libraries**:
- **UI Framework**: Tailwind CSS + shadcn/ui (accessible components)
- **Code Display**: Monaco Editor (VSCode's editor, syntax highlighting)
- **State Management**: Zustand (lightweight, simple API)
- **API Client**: TanStack Query (React Query) for caching and optimistic updates
- **Routing**: React Router v6
- **Form Handling**: React Hook Form + Zod validation

**Best Practices**:
- Component-driven development
- Atomic design pattern (atoms, molecules, organisms)
- Co-locate tests with components
- Use custom hooks for reusable logic

---

### 5. Testing Strategy

**Decision**: Multi-layer testing with pytest (backend) and Vitest + Testing Library (frontend)

**Backend Testing**:
- **Unit Tests**: pytest + pytest-asyncio
- **Integration Tests**: pytest with TestClient (FastAPI)
- **Contract Tests**: pytest with OpenAPI validation
- **Coverage**: pytest-cov (target 80% minimum)

**Frontend Testing**:
- **Unit Tests**: Vitest (Vite-native, fast)
- **Component Tests**: Testing Library (user-centric)
- **E2E Tests**: Playwright (Phase 2 - not in initial MVP)
- **Coverage**: Vitest coverage (target 80%)

**TDD Workflow** (Constitution Requirement):
```
🔴 RED Phase:
1. Write failing test
2. Verify it fails (run test suite)
3. Commit: "test: [feature] - RED"

🟢 GREEN Phase:
1. Minimal implementation to pass test
2. Verify it passes
3. Commit: "feat: [feature] - GREEN"

🔵 REFACTOR Phase:
1. Improve code quality
2. Verify tests still pass
3. Commit: "refactor: [feature] - REFACTOR"
```

**Best Practices**:
- Write tests first (TDD cycle)
- Use fixtures for test data
- Mock external dependencies (LLM API, database)
- Test user workflows, not implementation details
- Maintain 100% coverage for core business logic

---

### 6. Code Analysis & Language Detection

**Decision**: Pygments for syntax highlighting + custom language detection

**Rationale**:
- **Pygments**:
  - Supports 500+ languages
  - Syntax highlighting for code display
  - Token-based analysis for structure detection

- **Custom Detection**:
  - File extension mapping (primary method)
  - Shebang detection for scripts
  - Pattern matching for ambiguous files

**Language Support (Phase 1)**:
- Python (.py)
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- HTML (.html)
- CSS (.css)
- Java (.java)
- C/C++ (.c, .cpp, .h)
- Markdown (.md)
- Plain text (.txt)

**Code Analysis Features**:
- **Language detection**: File extension + content analysis
- **Complexity assessment**: Line count, nesting depth, function count
- **Dependency extraction**: Import statements, file references
- **Concept extraction**: Keywords (function, class, loop, variable, etc.)

**Best Practices**:
- Validate file size before analysis (10MB limit)
- Reject binary files (magic number detection)
- Normalize line endings (CRLF → LF)
- Handle encoding issues (UTF-8 with fallback)

---

### 7. File Storage Strategy

**Decision**: Local filesystem for MVP, S3-compatible for production

**MVP Approach**:
- Store uploaded files in `storage/uploads/{user_id}/{task_id}/`
- Use UUIDs for collision-free filenames
- Store metadata (filename, size, MIME type) in PostgreSQL
- Implement file cleanup on permanent deletion

**Production Approach** (Future):
- AWS S3 or MinIO (S3-compatible)
- Signed URLs for secure access
- Lifecycle policies for trash (30-day auto-delete)

**Security**:
- Validate file types (whitelist extensions)
- Scan for malicious content (future: ClamAV)
- Enforce size limits (10MB per task)
- User-scoped access control

**Best Practices**:
- Store relative paths in database
- Use environment variables for storage paths
- Implement atomic operations for file writes
- Handle partial uploads gracefully

---

### 8. Authentication & Session Management

**Decision**: JWT-based authentication with HTTPOnly cookies

**Rationale**:
- **JWT chosen for**:
  - Stateless authentication (scales horizontally)
  - Self-contained tokens (no DB lookup per request)
  - Standard format (RFC 7519)

- **HTTPOnly cookies chosen for**:
  - CSRF protection (SameSite=Strict)
  - XSS protection (not accessible via JavaScript)
  - Automatic token management

**Implementation**:
- **Access token**: Short-lived (15 minutes), HTTPOnly cookie
- **Refresh token**: Long-lived (7 days), HTTPOnly cookie, secure flag
- **Password hashing**: bcrypt (cost factor 12)
- **CSRF protection**: Double-submit cookie pattern

**Security Measures**:
- Rate limiting on auth endpoints (5 attempts / 15 min)
- Password requirements (min 8 chars, complexity rules)
- Email verification (future Phase 2)
- Account lockout after failed attempts
- Secure password reset flow

**Best Practices**:
- Use HTTPS in production (enforce)
- Implement CORS properly (whitelist origins)
- Log authentication events
- Rotate refresh tokens on use

---

### 9. Background Task Processing

**Decision**: Celery + Redis for async document generation

**Rationale**:
- **Celery chosen for**:
  - Python-native async task queue
  - Retry mechanisms built-in
  - Monitoring with Flower
  - Supports long-running AI operations

- **Redis chosen for**:
  - Fast message broker
  - Result backend for task status
  - Also used for caching

**Task Types**:
1. **Document Generation**: Long-running (1-3 minutes)
2. **Practice Problem Generation**: Medium (30-60 seconds)
3. **Trash Cleanup**: Scheduled daily (delete 30-day old items)

**Implementation**:
- Queue tasks immediately upon code upload
- Poll task status via API (`/tasks/{task_id}/status`)
- Send notification when complete (WebSocket in Phase 2)
- Implement task retry with exponential backoff

**Best Practices**:
- Set task timeouts (5 minutes max)
- Implement idempotent tasks
- Log task failures with traceback
- Monitor queue depth and worker health

---

### 10. Performance Optimization Strategy

**Goals** (from spec):
- Document generation < 3 minutes (500 LOC)
- Q&A responses < 10 seconds
- UI interactions < 200ms
- Page load < 3 seconds

**Backend Optimizations**:
- Use async/await throughout (FastAPI, SQLAlchemy, httpx)
- Connection pooling (database, Redis)
- Cache frequently accessed data (user sessions, document metadata)
- Stream large responses (for future file downloads)
- Index database columns (user_id, task_id, deletion_status)

**Frontend Optimizations**:
- Code splitting by route (React.lazy)
- Lazy load Monaco Editor (not on initial page load)
- Virtualize long lists (react-window for task lists)
- Debounce Q&A input (300ms)
- Optimistic UI updates (React Query)
- Cache API responses (React Query with stale-while-revalidate)

**LLM Optimizations**:
- Use streaming for Q&A responses (future)
- Cache common concept explanations
- Batch similar requests when possible
- Use GPT-3.5 for Q&A (faster than GPT-4)

**Monitoring**:
- Track API response times
- Monitor LLM API latency
- Alert on slow database queries
- Log frontend performance metrics (Core Web Vitals)

---

## Technology Stack Summary

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0 (async)
- **Task Queue**: Celery
- **Message Broker**: Redis
- **LLM**: Google Gemini 3 Flash Preview (gemini-3-flash-preview)
- **Testing**: pytest, pytest-asyncio, pytest-cov

### Frontend
- **Framework**: React 18+
- **Language**: TypeScript
- **Build Tool**: Vite
- **UI Library**: Tailwind CSS + shadcn/ui
- **Code Editor**: Monaco Editor
- **State Management**: Zustand
- **API Client**: TanStack Query (React Query)
- **Testing**: Vitest + Testing Library

### Infrastructure (MVP)
- **File Storage**: Local filesystem
- **Cache**: Redis
- **Server**: Uvicorn (ASGI)
- **Reverse Proxy**: Nginx (production)

### Development Tools
- **Version Control**: Git
- **Code Formatting**: Black (Python), Prettier (TypeScript)
- **Linting**: Ruff (Python), ESLint (TypeScript)
- **Migration Tool**: Alembic (database)
- **API Documentation**: OpenAPI (auto-generated by FastAPI)

---

## Implementation Roadmap

### Phase 0: Project Setup (Foundation)
1. Initialize backend (FastAPI + PostgreSQL + SQLAlchemy)
2. Initialize frontend (Vite + React + TypeScript)
3. Set up CI/CD (GitHub Actions for tests)
4. Configure development environment (Docker Compose)

### Phase 1: Authentication & User Management
1. User registration, login, logout
2. JWT token management
3. Password hashing and validation
4. Session management

### Phase 2: Project & Task Management
1. Project CRUD operations
2. Task CRUD operations
3. Soft delete + trash functionality
4. Progress tracking models

### Phase 3: Code Upload & Analysis
1. File upload (single/multiple/folder/paste)
2. File validation and storage
3. Language detection
4. Code complexity analysis

### Phase 4: AI Integration & Document Generation
1. OpenAI API integration
2. Prompt engineering for 7-chapter documents
3. Celery task queue setup
4. Document generation background tasks
5. Practice problem generation

### Phase 5: Q&A System
1. Q&A API endpoints
2. Context-aware prompt construction
3. Answer generation with GPT-3.5
4. Question history storage

### Phase 6: Frontend Implementation
1. Authentication UI (login, register)
2. Project dashboard
3. Task timeline view
4. Code upload UI (3 methods)
5. Document viewer (2-column layout)
6. Practice problem UI
7. Q&A panel
8. Progress tracking UI
9. Trash view

### Phase 7: Testing & Quality
1. Backend unit tests (80% coverage)
2. Frontend component tests (80% coverage)
3. Integration tests (critical flows)
4. Security testing (auth, XSS, CSRF)
5. Performance testing (load tests)

### Phase 8: Deployment
1. Production configuration
2. Database migrations
3. Environment setup
4. Monitoring and logging
5. Documentation (quickstart.md)

---

## Risk Mitigation

### High-Impact Risks

**1. LLM API Rate Limits / Costs**
- **Mitigation**: Implement request queuing, use cheaper models for Q&A, cache common responses
- **Monitoring**: Track API usage and costs daily

**2. Document Generation Performance**
- **Mitigation**: Async processing with Celery, set realistic expectations (3 min target)
- **Monitoring**: Track generation times, alert on failures

**3. Database Performance at Scale**
- **Mitigation**: Proper indexing, connection pooling, query optimization
- **Monitoring**: Slow query logs, database metrics

**4. Security Vulnerabilities**
- **Mitigation**: Follow OWASP guidelines, security review before production
- **Monitoring**: Security audit, dependency scanning

---

## Next Steps

1. **Phase 1**: Generate data-model.md with entity schemas
2. **Phase 1**: Generate API contracts in `/contracts/`
3. **Phase 1**: Generate quickstart.md for development setup
4. **Phase 2**: Use `/speckit.tasks` to break down implementation into actionable tasks
