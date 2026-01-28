# Data Model: AI Code Learning Platform - Phase 1 MVP

**Date**: 2025-11-15
**Feature**: AI Code Learning Platform
**Database**: PostgreSQL 15+

## Overview

This document defines the database schema for the AI Code Learning Platform. All entities support user isolation, soft deletion with 30-day trash retention, and timestamps for audit trails.

## Core Entities

### User

Represents a platform user (authentication and profile).

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt hashed
    skill_level VARCHAR(50) DEFAULT 'Complete Beginner',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
```

**Fields**:
- `id`: UUID primary key
- `email`: Unique email address (validated)
- `password_hash`: bcrypt hashed password (cost factor 12)
- `skill_level`: Default 'Complete Beginner' (per constitution)
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update
- `last_login_at`: Last successful login

**Relationships**:
- Has many Projects
- Has many RefreshTokens (for JWT auth)

**Validation Rules**:
- Email must be unique and valid format
- Password must be hashed (never store plaintext)
- Skill level defaults to 'Complete Beginner'

---

### Project

Represents a learning container for related tasks.

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Soft delete fields
    deletion_status VARCHAR(20) DEFAULT 'active' CHECK (deletion_status IN ('active', 'trashed')),
    trashed_at TIMESTAMP WITH TIME ZONE,
    scheduled_deletion_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT title_min_length CHECK (char_length(title) >= 1)
);

CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_deletion_status ON projects(deletion_status);
CREATE INDEX idx_projects_user_active ON projects(user_id, deletion_status) WHERE deletion_status = 'active';
```

**Fields**:
- `id`: UUID primary key
- `user_id`: Foreign key to User (owner)
- `title`: Project name
- `description`: Optional project description
- `created_at`: Project creation timestamp
- `updated_at`: Last modification timestamp
- `last_activity_at`: Last task activity (updated when tasks are modified)
- `deletion_status`: 'active' or 'trashed'
- `trashed_at`: When project was moved to trash
- `scheduled_deletion_at`: When project will be permanently deleted (trashed_at + 30 days)

**Relationships**:
- Belongs to User
- Has many Tasks

**Business Rules**:
- Title required (minimum 1 character)
- Soft delete: When deleted, all tasks also move to trash
- After 30 days in trash, permanent deletion cascade to tasks

---

### Task

Represents a single learning unit focused on one code upload.

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    task_number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    upload_method VARCHAR(20) CHECK (upload_method IN ('file', 'folder', 'paste')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Soft delete fields
    deletion_status VARCHAR(20) DEFAULT 'active' CHECK (deletion_status IN ('active', 'trashed')),
    trashed_at TIMESTAMP WITH TIME ZONE,
    scheduled_deletion_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT title_min_length CHECK (char_length(title) >= 5),
    CONSTRAINT description_max_length CHECK (char_length(description) <= 500),
    CONSTRAINT unique_task_number_per_project UNIQUE (project_id, task_number)
);

CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_deletion_status ON tasks(deletion_status);
CREATE INDEX idx_tasks_project_active ON tasks(project_id, deletion_status) WHERE deletion_status = 'active';
CREATE INDEX idx_tasks_number_order ON tasks(project_id, task_number);
```

**Fields**:
- `id`: UUID primary key
- `project_id`: Foreign key to Project
- `task_number`: Sequential number within project (immutable once assigned)
- `title`: Task name (min 5 characters per FR-008)
- `description`: Optional description (max 500 characters per FR-009)
- `upload_method`: How code was uploaded ('file', 'folder', 'paste')
- `created_at`: Task creation timestamp
- `updated_at`: Last modification timestamp
- `deletion_status`: 'active' or 'trashed'
- `trashed_at`: When task was moved to trash
- `scheduled_deletion_at`: When task will be permanently deleted (trashed_at + 30 days)

**Relationships**:
- Belongs to Project
- Has one UploadedCode
- Has one LearningDocument
- Has many PracticeProblems (5 per task)
- Has many Questions
- Has one Progress

**Business Rules**:
- Task numbers are sequential and immutable (FR-004)
- Users cannot reorder tasks (FR-005)
- Title min 5 chars, description max 500 chars
- Soft delete preserves task for 30 days

---

### UploadedCode

Stores metadata and content for code uploaded by user.

```sql
CREATE TABLE uploaded_code (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID UNIQUE NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    detected_language VARCHAR(50),
    complexity_level VARCHAR(20) CHECK (complexity_level IN ('beginner', 'intermediate', 'advanced')),
    total_lines INTEGER,
    total_files INTEGER,
    upload_size_bytes INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_upload_size CHECK (upload_size_bytes <= 10485760)  -- 10MB limit
);

CREATE INDEX idx_uploaded_code_task_id ON uploaded_code(task_id);
```

**Fields**:
- `id`: UUID primary key
- `task_id`: Foreign key to Task (one-to-one)
- `detected_language`: Programming language detected (e.g., 'python', 'javascript')
- `complexity_level`: Assessment ('beginner', 'intermediate', 'advanced')
- `total_lines`: Total lines of code across all files
- `total_files`: Number of files uploaded
- `upload_size_bytes`: Total size in bytes
- `created_at`: Upload timestamp

**Relationships**:
- Belongs to Task (one-to-one)
- Has many CodeFiles

**Business Rules**:
- Maximum upload size 10MB (FR-014)
- One uploaded code per task
- Permanently deleted when task is permanently deleted

---

### CodeFile

Individual code file within an uploaded code set.

```sql
CREATE TABLE code_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    uploaded_code_id UUID NOT NULL REFERENCES uploaded_code(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT,  -- Relative path for folder uploads
    file_extension VARCHAR(20),
    file_size_bytes INTEGER,
    storage_path TEXT NOT NULL,  -- Actual path on filesystem/S3
    mime_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT supported_extension CHECK (
        file_extension IN ('.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.java', '.cpp', '.c', '.txt', '.md')
    )
);

CREATE INDEX idx_code_files_uploaded_code_id ON code_files(uploaded_code_id);
```

**Fields**:
- `id`: UUID primary key
- `uploaded_code_id`: Foreign key to UploadedCode
- `file_name`: Original filename
- `file_path`: Relative path within folder structure
- `file_extension`: File extension for validation
- `file_size_bytes`: Individual file size
- `storage_path`: Path to actual file in storage (e.g., `storage/uploads/{user_id}/{task_id}/{uuid}.py`)
- `mime_type`: MIME type for validation
- `created_at`: File upload timestamp

**Relationships**:
- Belongs to UploadedCode

**Business Rules**:
- Only supported extensions allowed (FR-015)
- Binary files rejected (FR-016)
- 1-20 files per upload (FR-018)

---

### LearningDocument

Generated 7-chapter educational content for a task.

```sql
CREATE TABLE learning_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID UNIQUE NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    content JSONB NOT NULL,  -- 7-chapter structure
    generation_status VARCHAR(20) DEFAULT 'pending' CHECK (
        generation_status IN ('pending', 'in_progress', 'completed', 'failed')
    ),
    generation_started_at TIMESTAMP WITH TIME ZONE,
    generation_completed_at TIMESTAMP WITH TIME ZONE,
    generation_error TEXT,
    celery_task_id VARCHAR(255),  -- For tracking async task
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_content_structure CHECK (
        jsonb_typeof(content) = 'object' AND
        content ? 'chapter1' AND
        content ? 'chapter2' AND
        content ? 'chapter3' AND
        content ? 'chapter4' AND
        content ? 'chapter5' AND
        content ? 'chapter6' AND
        content ? 'chapter7'
    )
);

CREATE INDEX idx_learning_documents_task_id ON learning_documents(task_id);
CREATE INDEX idx_learning_documents_status ON learning_documents(generation_status);
CREATE INDEX idx_learning_documents_celery_task ON learning_documents(celery_task_id);
```

**Fields**:
- `id`: UUID primary key
- `task_id`: Foreign key to Task (one-to-one)
- `content`: JSONB containing 7 chapters (each chapter has structured fields)
- `generation_status`: Status of document generation
- `generation_started_at`: When generation began
- `generation_completed_at`: When generation finished
- `generation_error`: Error message if generation failed
- `celery_task_id`: Celery task ID for status tracking
- `created_at`: Document creation timestamp
- `updated_at`: Last modification timestamp

**JSONB Structure** (content field):
```json
{
  "chapter1": {
    "title": "What This Code Does",
    "summary": "One-sentence plain language summary"
  },
  "chapter2": {
    "title": "Prerequisites Knowledge",
    "concepts": [
      {
        "name": "Variables",
        "explanation": "...",
        "analogy": "...",
        "example": "...",
        "use_cases": "..."
      }
    ]
  },
  "chapter3": {
    "title": "Code Structure Overview",
    "flowchart": "ASCII/Mermaid diagram",
    "file_breakdown": {...}
  },
  "chapter4": {
    "title": "Line-by-Line Explanation",
    "explanations": [...]
  },
  "chapter5": {
    "title": "Execution Flow Simulation",
    "steps": [...]
  },
  "chapter6": {
    "title": "Core Concepts Summary",
    "concepts": [...]
  },
  "chapter7": {
    "title": "Common Mistakes",
    "mistakes": [
      {"wrong": "...", "right": "...", "why": "...", "fix": "..."}
    ]
  }
}
```

**Relationships**:
- Belongs to Task (one-to-one)

**Business Rules**:
- Immutable after generation (FR-038 - content immutability)
- Generate within 3 minutes for 500 LOC (FR-083)
- Stored, not regenerated on view (FR-038)

---

### PracticeProblem

Generated practice exercises for a task.

```sql
CREATE TABLE practice_problems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    problem_number INTEGER NOT NULL CHECK (problem_number BETWEEN 1 AND 5),
    problem_type VARCHAR(20) NOT NULL CHECK (
        problem_type IN ('follow_along', 'fill_blanks', 'modify', 'debug', 'create')
    ),
    problem_statement TEXT NOT NULL,
    learning_objective TEXT,
    hints JSONB,  -- Array of progressive hints
    model_solution TEXT,
    expected_output TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_problem_per_task UNIQUE (task_id, problem_number)
);

CREATE INDEX idx_practice_problems_task_id ON practice_problems(task_id);
CREATE INDEX idx_practice_problems_number ON practice_problems(task_id, problem_number);
```

**Fields**:
- `id`: UUID primary key
- `task_id`: Foreign key to Task
- `problem_number`: 1-5 (increasing difficulty)
- `problem_type`: Type of practice problem
- `problem_statement`: Description of what user should do
- `learning_objective`: What this problem teaches
- `hints`: JSON array of progressive hints
- `model_solution`: Complete solution (hidden initially)
- `expected_output`: Expected result or behavior
- `created_at`: Creation timestamp

**Relationships**:
- Belongs to Task

**Business Rules**:
- Exactly 5 problems per task (FR-048)
- Problems in specific order (FR-049)
- Solvable with document concepts (FR-051)
- Text-only, no in-browser execution (FR-056)

---

### Question

User-submitted questions during learning (Q&A system).

```sql
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    selected_code_context TEXT,  -- If user selected code
    answer_text TEXT,
    answered_at TIMESTAMP WITH TIME ZONE,
    helpful_feedback BOOLEAN,  -- User feedback on answer
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT question_length CHECK (char_length(question_text) >= 3 AND char_length(question_text) <= 500),
    CONSTRAINT code_context_length CHECK (selected_code_context IS NULL OR char_length(selected_code_context) <= 50000)
);

CREATE INDEX idx_questions_task_id ON questions(task_id);
CREATE INDEX idx_questions_user_id ON questions(user_id);
CREATE INDEX idx_questions_task_user ON questions(task_id, user_id);
```

**Fields**:
- `id`: UUID primary key
- `task_id`: Foreign key to Task
- `user_id`: Foreign key to User
- `question_text`: The user's question (3-500 chars)
- `selected_code_context`: Code snippet if user selected text (max 50 lines)
- `answer_text`: AI-generated answer
- `answered_at`: When answer was generated
- `helpful_feedback`: Whether user found answer helpful
- `created_at`: Question timestamp

**Relationships**:
- Belongs to Task
- Belongs to User

**Business Rules**:
- Question length 3-500 characters (FR-060, FR-061)
- Selected code max 50 lines (FR-062)
- Answer generated within 10 seconds (FR-087)
- Questions saved per task (FR-066)
- Conversation history preserved (FR-067)

---

### Progress

Tracks user's learning progress for a task.

```sql
CREATE TABLE progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID UNIQUE NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Document reading progress
    chapters_completed JSONB DEFAULT '[]'::jsonb,  -- Array of chapter numbers (1-7)
    document_read_percentage INTEGER DEFAULT 0 CHECK (document_read_percentage BETWEEN 0 AND 100),

    -- Practice problems progress
    problems_completed JSONB DEFAULT '[]'::jsonb,  -- Array of problem numbers (1-5)
    practice_completion_count INTEGER DEFAULT 0 CHECK (practice_completion_count BETWEEN 0 AND 5),

    -- Q&A activity
    questions_asked_count INTEGER DEFAULT 0,

    -- Task completion
    task_completed BOOLEAN DEFAULT FALSE,
    task_completion_date TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_chapter_completion CHECK (
        jsonb_typeof(chapters_completed) = 'array' AND
        jsonb_array_length(chapters_completed) <= 7
    ),
    CONSTRAINT valid_problem_completion CHECK (
        jsonb_typeof(problems_completed) = 'array' AND
        jsonb_array_length(problems_completed) <= 5
    )
);

CREATE INDEX idx_progress_task_id ON progress(task_id);
CREATE INDEX idx_progress_user_id ON progress(user_id);
CREATE INDEX idx_progress_task_user ON progress(task_id, user_id);
```

**Fields**:
- `id`: UUID primary key
- `task_id`: Foreign key to Task (one-to-one per user)
- `user_id`: Foreign key to User
- `chapters_completed`: JSON array of completed chapter numbers
- `document_read_percentage`: Calculated percentage (0-100)
- `problems_completed`: JSON array of completed problem numbers
- `practice_completion_count`: Count of completed problems (0-5)
- `questions_asked_count`: Number of questions asked
- `task_completed`: Whether user marked task as complete
- `task_completion_date`: When task was marked complete
- `created_at`: Progress tracking start
- `updated_at`: Last progress update

**Relationships**:
- Belongs to Task (one-to-one)
- Belongs to User

**Business Rules**:
- Progress persists across sessions (FR-074)
- Task completion requires document read + manual mark (FR-073)
- Progress calculation: completed items / total items (FR-072)
- No time limits (FR-076)

---

### RefreshToken

JWT refresh tokens for authentication.

```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,  -- SHA-256 hash of token
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
```

**Fields**:
- `id`: UUID primary key
- `user_id`: Foreign key to User
- `token_hash`: SHA-256 hash of refresh token (not stored in plaintext)
- `expires_at`: Token expiration (7 days from creation)
- `created_at`: Token creation timestamp
- `revoked`: Whether token has been revoked
- `revoked_at`: When token was revoked

**Relationships**:
- Belongs to User

**Business Rules**:
- Tokens expire after 7 days
- Rotate on use (issue new, revoke old)
- Store hash only (never plaintext)
- Revoke on logout

---

## Scheduled Tasks

### Trash Cleanup Job

Background job runs daily to permanently delete items that have been in trash for 30+ days.

```python
# Celery task (pseudo-code)
@celery.task
def cleanup_trash():
    # Delete projects older than 30 days in trash
    DELETE FROM projects
    WHERE deletion_status = 'trashed'
      AND scheduled_deletion_at < NOW();

    # Delete tasks older than 30 days in trash
    DELETE FROM tasks
    WHERE deletion_status = 'trashed'
      AND scheduled_deletion_at < NOW();
```

**Schedule**: Daily at 2:00 AM UTC

---

## Indexes Summary

**Performance-Critical Indexes**:
1. `idx_users_email` - Login queries
2. `idx_projects_user_active` - Active projects per user
3. `idx_tasks_project_active` - Active tasks per project
4. `idx_tasks_number_order` - Task sequential ordering
5. `idx_learning_documents_status` - Document generation status queries
6. `idx_progress_task_user` - Progress tracking queries

**Soft Delete Indexes**:
- All `deletion_status` indexes for filtering active/trashed items
- Partial indexes on `WHERE deletion_status = 'active'` for performance

---

## Entity Relationship Diagram

```
User
├── Projects (1:N)
│   └── Tasks (1:N)
│       ├── UploadedCode (1:1)
│       │   └── CodeFiles (1:N)
│       ├── LearningDocument (1:1)
│       ├── PracticeProblems (1:5)
│       ├── Questions (1:N)
│       └── Progress (1:1 per user)
└── RefreshTokens (1:N)
```

---

## Data Integrity Rules

### Cascade Delete Behavior

**User Deletion** (if implemented in Phase 2):
- CASCADE to Projects → Tasks → all associated data
- Permanently delete all files from storage

**Project Soft Delete**:
- Move all tasks to trash
- Set `scheduled_deletion_at` = `trashed_at` + 30 days

**Project Permanent Delete**:
- CASCADE to Tasks → UploadedCode → CodeFiles
- CASCADE to LearningDocuments, PracticeProblems, Questions, Progress
- Delete associated files from storage

**Task Soft Delete**:
- Set `deletion_status` = 'trashed'
- Set `scheduled_deletion_at` = `trashed_at` + 30 days

**Task Permanent Delete**:
- CASCADE delete all associated data
- Delete code files from storage

---

## Migration Strategy

### Initial Migration (Alembic)

```python
# migrations/versions/001_initial_schema.py
def upgrade():
    # Create tables in dependency order
    op.create_table('users', ...)
    op.create_table('projects', ...)
    op.create_table('tasks', ...)
    op.create_table('uploaded_code', ...)
    op.create_table('code_files', ...)
    op.create_table('learning_documents', ...)
    op.create_table('practice_problems', ...)
    op.create_table('questions', ...)
    op.create_table('progress', ...)
    op.create_table('refresh_tokens', ...)

    # Create indexes
    # ...

def downgrade():
    # Drop tables in reverse order
    # ...
```

### Future Migrations

- Add columns for Phase 2 features
- Create indexes for performance
- Data migrations (if needed)

---

## Performance Considerations

### Query Optimization

1. **User Projects List**:
   ```sql
   SELECT * FROM projects
   WHERE user_id = ? AND deletion_status = 'active'
   ORDER BY last_activity_at DESC;
   ```
   - Uses `idx_projects_user_active` partial index

2. **Task Timeline**:
   ```sql
   SELECT * FROM tasks
   WHERE project_id = ? AND deletion_status = 'active'
   ORDER BY task_number ASC;
   ```
   - Uses `idx_tasks_number_order` index

3. **Progress Query**:
   ```sql
   SELECT p.*, t.* FROM progress p
   JOIN tasks t ON p.task_id = t.id
   WHERE p.user_id = ? AND t.project_id = ?;
   ```
   - Uses `idx_progress_user_id` and `idx_tasks_project_id`

### JSONB Performance

- Use GIN indexes for JSONB columns if querying nested fields (Phase 2)
- Current schema uses JSONB for flexible storage, not complex querying
- Extract frequently queried fields to columns if needed

---

## Security Considerations

### Data Isolation

- All queries MUST filter by `user_id` to prevent data leakage
- Use row-level security policies (PostgreSQL RLS) in production
- Never expose internal UUIDs in URLs (use opaque tokens if needed)

### Sensitive Data

- Never log password_hash
- Never return password_hash in API responses
- Hash refresh tokens before storage
- Sanitize user input before storage (XSS prevention)

---

## Next Steps

1. Generate API contracts in `/contracts/`
2. Implement SQLAlchemy models based on this schema
3. Create Alembic migrations
4. Write model unit tests
