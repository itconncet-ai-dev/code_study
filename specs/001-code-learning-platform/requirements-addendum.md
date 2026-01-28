# Requirements Addendum: AI Code Learning Platform - Phase 1 MVP

**Date**: 2025-11-17
**Purpose**: Document additional requirements identified during design review
**Status**: Complete
**Related Checklists**: design-review.md

This document addresses the 38 incomplete requirements identified in the design review checklist. All requirements are now fully specified to enable implementation.

---

## 1. AI Integration & Content Generation Requirements

### CHK005: AI Content Validation Requirements

**Requirement ID**: FR-095

**Description**: All AI-generated content MUST pass validation before being stored and displayed to users.

**Validation Criteria**:
1. **Structural Validation**:
   - Document must contain all 7 chapters (Intro, Prerequisites, Step-by-Step, Flow, Glossary, Practice, Tips)
   - Each chapter must have required fields: title, content, key_points (array)
   - Practice problems must include: question, difficulty_level, hints (array), model_solution

2. **Content Completeness**:
   - Minimum content length: 100 characters per chapter (ensures meaningful explanation)
   - Maximum content length: 5000 characters per chapter (prevents excessive verbosity)
   - Each practice problem must have at least 2 hints and 1 model solution
   - Q&A responses must be minimum 50 characters, maximum 2000 characters

3. **Format Validation**:
   - Content must be valid UTF-8 text
   - Code blocks must be properly formatted with language tags
   - No HTML/script tags in content (XSS prevention)
   - JSON structure must match schema exactly

4. **Educational Quality Validation**:
   - Content must not contain error messages or API failures
   - Must not contain placeholder text like "[TODO]", "[GENERATE]", etc.
   - Must contain at least 1 real-life analogy per chapter (verified by keyword matching: "like", "similar to", "imagine", etc.)

**Implementation**:
- Validation runs immediately after AI generation, before database storage
- Failed validation triggers fallback mechanism (see CHK006)
- Validation errors are logged for monitoring (see CHK010)

---

### CHK006: AI Content Generation Fallback Requirements

**Requirement ID**: FR-096

**Description**: When AI-generated content fails quality validation, the system MUST implement fallback strategies to ensure users receive usable content.

**Fallback Strategy** (in order of priority):

1. **Retry with Modified Prompt** (up to 2 attempts):
   - Regenerate with more explicit instructions about missing/invalid sections
   - Add examples to the prompt for chapters that failed validation
   - Increase temperature slightly (0.7 → 0.8) to improve creativity if content is too generic

2. **Partial Content Acceptance** (if 5+ chapters valid):
   - Accept valid chapters and mark invalid chapters as "Generation Failed"
   - Display error message: "Some sections could not be generated. You can ask questions to clarify these concepts."
   - Allow user to request regeneration of specific failed chapters via Q&A

3. **Basic Template Generation** (last resort):
   - Use predefined educational templates with placeholders
   - Extract code structure programmatically (functions, classes, imports)
   - Generate minimal explanatory text: "This code defines a function named X that takes Y parameters"
   - Mark task with warning: "Limited explanation available - please use Q&A for detailed questions"

4. **Complete Failure Handling**:
   - If all fallbacks fail, task status = "generation_failed"
   - Display user-friendly error: "We couldn't generate the learning document. Please try uploading a smaller code file or contact support."
   - Allow user to delete task and retry or ask questions directly about the code

**Notification**:
- Users are notified immediately when fallback strategies are used
- UI displays a yellow warning banner for partial content acceptance
- UI displays a red error banner for complete generation failure

---

### CHK007: Gemini API Rate Limit Handling Requirements

**Requirement ID**: FR-097

**Description**: System MUST handle Gemini API rate limits and quota exhaustion gracefully.

**Rate Limit Detection**:
- HTTP 429 (Too Many Requests) response from Gemini API
- HTTP 503 (Service Unavailable) for quota exhaustion
- Error messages containing "quota", "rate limit", "too many requests"

**Handling Strategy**:

1. **Exponential Backoff with Jitter**:
   - Retry delay = min(60s, base_delay * 2^attempt + random(0-1000ms))
   - Base delay: 2 seconds
   - Maximum retries: 3 attempts
   - Total max wait time: ~14 seconds (2s + 4s + 8s)

2. **Queue Management**:
   - If rate limit detected, pause all new AI requests for 60 seconds
   - Display to all users: "AI service is experiencing high demand. Your request is queued. Estimated wait time: X minutes"
   - Process queued requests FIFO after cooldown period

3. **Quota Monitoring**:
   - Track daily API usage count (requests and tokens)
   - Warning threshold: 80% of daily quota
   - Hard limit: 95% of daily quota (stop accepting new requests)
   - Admin notification when threshold reached

4. **User Communication**:
   - Real-time status updates during retry attempts
   - Clear error message for quota exhaustion: "AI service quota reached for today. Please try again tomorrow or contact support for priority access."
   - Progress bar shows "Waiting for AI service availability"

**Graceful Degradation**:
- During rate limiting, Q&A feature enters "lite mode": simple keyword-based answers from document content
- Document generation requests are queued but not rejected
- Users can still browse existing documents and practice problems

---

### CHK010: AI Generation Quality Monitoring Requirements

**Requirement ID**: FR-098

**Description**: System MUST monitor AI generation quality metrics to detect issues and improve service.

**Metrics to Track**:

1. **Success Rate Metrics**:
   - Total generation attempts (documents + Q&A + practice)
   - Successful generations (passed validation)
   - Failed generations (by failure reason: timeout, validation, API error)
   - Fallback usage count (by fallback type)

2. **Performance Metrics**:
   - Average generation time (P50, P95, P99)
   - Timeout occurrences (>180s for documents, >10s for Q&A)
   - API response time distribution

3. **Content Quality Metrics**:
   - Average content length per chapter
   - Validation failure rate by validation rule
   - Retry success rate (did retry fix the issue?)
   - User satisfaction proxy: Q&A question count per document (low count = good explanation)

4. **Cost Metrics**:
   - API calls per day/week/month
   - Tokens consumed (prompt + completion)
   - Cost per document generation
   - Cost per Q&A response

**Storage**:
- Metrics stored in PostgreSQL table `ai_generation_metrics`
- Fields: timestamp, metric_type, metric_value, task_id, user_id, metadata (JSONB)
- Retention: 90 days

**Monitoring Dashboard** (Phase 2):
- Admin-only dashboard displaying key metrics
- Alerts for: success rate < 90%, average response time > 2x baseline, quota usage > 80%

**Immediate Implementation** (Phase 1):
- Log all metrics to structured logs (JSON format)
- Basic console output for monitoring during development
- Manual review of logs weekly

---

### CHK013: Malformed AI Response Handling Requirements

**Requirement ID**: FR-099

**Description**: System MUST handle incomplete, malformed, or corrupted AI responses without crashing.

**Types of Malformed Responses**:

1. **Incomplete JSON**:
   - Response cuts off mid-generation (API timeout, network interruption)
   - Missing closing braces/brackets
   - **Handling**: Attempt JSON repair (add missing closures), retry if repair fails, trigger fallback

2. **Invalid JSON Structure**:
   - Response is valid JSON but doesn't match expected schema
   - Missing required fields (chapters, practice_problems)
   - **Handling**: Log schema validation errors, retry with more explicit schema in prompt, use fallback template

3. **Empty/Null Responses**:
   - API returns empty string, null, or whitespace only
   - **Handling**: Immediate retry (likely transient API issue), max 3 retries, then fallback

4. **Mixed Content Responses**:
   - Response contains error messages mixed with valid content
   - Example: "Error: timeout\n\n{valid_json}"
   - **Handling**: Extract valid JSON if possible, discard error messages, validate extracted content

5. **Encoding Issues**:
   - Invalid UTF-8 characters, mojibake (garbled text)
   - **Handling**: Attempt re-encoding (try common encodings: UTF-8, EUC-KR, CP949), reject if unrecoverable

**Error Recovery Flow**:
```
1. AI Response Received
   ↓
2. Parse JSON → [Parse Error?] → JSON Repair Attempt → [Still Fails?] → Retry (max 2x) → Fallback
   ↓ [Success]
3. Validate Schema → [Schema Error?] → Log + Retry with explicit schema → [Still Fails?] → Fallback
   ↓ [Success]
4. Validate Content Quality (CHK005) → [Quality Fail?] → Fallback (CHK006)
   ↓ [Success]
5. Store in Database
```

**Logging**:
- All malformed responses logged with full content for debugging
- Log fields: timestamp, task_id, error_type, raw_response (truncated to 1000 chars), recovery_action_taken
- Logs help identify patterns (e.g., specific prompts cause malformed responses)

---

## 2. Educational Content Quality Requirements

### CHK019: Practice Problem Difficulty Progression Requirements

**Requirement ID**: FR-100

**Description**: Practice problems MUST follow a clear difficulty progression with measurable criteria for each level.

**5 Difficulty Levels** (from spec FR-049):

1. **Follow Along** (Easiest):
   - **Criteria**: User types provided code exactly as shown
   - **Cognitive Load**: Memorization and typing accuracy
   - **Example**: "Type this function exactly: `def add(a, b): return a + b`"
   - **Success Metric**: Code matches model solution character-for-character

2. **Fill in the Blanks**:
   - **Criteria**: Code structure provided, user fills in 3-5 missing parts
   - **Cognitive Load**: Understanding variable names, function names, or simple expressions
   - **Example**: "Complete this function: `def add(a, b): return a ___ b`" (answer: +)
   - **Success Metric**: All blanks filled with correct values

3. **Modify Code**:
   - **Criteria**: Working code provided, user changes 1-2 specific behaviors
   - **Cognitive Load**: Understanding code flow, making targeted edits
   - **Example**: "Change this function to multiply instead of add"
   - **Success Metric**: Modified code produces expected output for test cases

4. **Debug**:
   - **Criteria**: Broken code provided (1-3 intentional bugs), user finds and fixes
   - **Cognitive Load**: Code comprehension, error analysis, problem-solving
   - **Example**: "This function should return True for even numbers but it's broken. Fix it."
   - **Success Metric**: Fixed code passes all test cases

5. **Create New** (Hardest):
   - **Criteria**: User writes code from scratch based on requirements
   - **Cognitive Load**: Full synthesis - planning, writing, testing
   - **Example**: "Write a function that finds the maximum value in a list"
   - **Success Metric**: Code passes functional test cases

**Progression Rules**:
- Each problem builds on concepts from previous problems
- Difficulty increases by adding: more blanks, more complex modifications, subtler bugs, stricter requirements
- All 5 problems must use concepts from the learning document
- Problems must be solvable in <10 minutes for target beginner audience

**AI Prompt Requirements**:
- Generate exactly one problem per difficulty level
- Specify difficulty level explicitly in generation prompt
- Include measurable success criteria for each problem
- Validate that difficulty progression is logical (no jumps in complexity)

---

### CHK026: Concept Explanation Consistency Requirements

**Requirement ID**: FR-101

**Description**: When the same programming concept appears in multiple documents, explanations MUST be consistent to avoid confusing beginners.

**Consistency Rules**:

1. **Core Terminology**:
   - Use identical definitions for fundamental concepts across all documents
   - Example: "variable" always explained as "a labeled container that stores a value"
   - Example: "function" always explained as "a reusable block of code that performs a specific task"

2. **Analogies**:
   - Prefer using the same real-life analogy for repeated concepts
   - Example: "function" → "like a recipe" (consistently across documents)
   - Example: "variable" → "like a labeled box" (consistently across documents)
   - Allow variations only if original analogy doesn't fit the specific context

3. **Code Examples**:
   - Use similar code patterns when demonstrating the same concept
   - Example: Variables always demonstrated with simple assignment first: `x = 5`
   - Example: Functions always demonstrated with a simple function that returns a value

**Implementation Strategy** (Phase 1 - Basic):
- Include "standard definitions" in AI prompts for common concepts
- Maintain a concept glossary file with canonical definitions (JSON)
- AI prompt includes: "Use these standard definitions when explaining concepts: {glossary}"

**Implementation Strategy** (Phase 2 - Advanced):
- Build user-specific concept memory: Track which concepts user has learned and how they were explained
- Inject previous explanations into prompts: "You previously explained 'function' as '...'. Use the same explanation if this code contains functions."
- Detect concept drift: Alert when new explanation significantly differs from previous

**Common Concepts Requiring Consistency**:
- Variables (assignment, naming, types)
- Functions (definition, parameters, return values, calling)
- Conditionals (if/else, boolean logic)
- Loops (for, while, iteration)
- Data structures (lists, dictionaries, tuples)
- Classes and objects (OOP concepts)

**Validation** (Phase 1):
- Manual review of generated documents during testing
- Test multiple documents with overlapping concepts
- Ensure no contradictory explanations

---

## 3. Data Model & Storage Requirements

### CHK037: Backup and Recovery Requirements

**Requirement ID**: NFR-001 (Non-Functional Requirement)

**Description**: System MUST implement backup and recovery mechanisms to protect user data.

**Scope**: This is a production operational requirement, not required for Phase 1 MVP development. Documented for completeness.

**Production Backup Strategy** (Phase 2+):

1. **Database Backups**:
   - Automated daily full backups of PostgreSQL database
   - Continuous WAL (Write-Ahead Logging) archiving for point-in-time recovery
   - Retention: 30 days of daily backups, 12 months of monthly backups
   - Storage: Encrypted off-site storage (AWS S3 Glacier or equivalent)

2. **File Backups**:
   - Uploaded code files backed up to S3-compatible object storage
   - Versioning enabled (retain deleted files for 30 days minimum)
   - Cross-region replication for disaster recovery

3. **Recovery Testing**:
   - Monthly backup restoration test to verify integrity
   - Document recovery procedures in runbook
   - RTO (Recovery Time Objective): 4 hours
   - RPO (Recovery Point Objective): 24 hours (maximum data loss)

**Phase 1 MVP**:
- Development environment: Manual backups before major changes
- Git repository backup for all code and configuration
- Database dumps before schema migrations
- No automated backup infrastructure (acceptable for MVP)

---

### CHK038: Data Retention Requirements (Beyond 30-Day Trash)

**Requirement ID**: NFR-002

**Description**: Define data retention policies for all user data beyond the 30-day trash retention period.

**Retention Policies**:

1. **Active User Data** (Unlimited Retention):
   - User accounts: Retained until user requests deletion
   - Active projects and tasks: Retained indefinitely while user is active
   - Learning documents and progress: Retained indefinitely (user's learning history)

2. **Trashed Data** (30-Day Retention):
   - Projects/tasks moved to trash: Permanently deleted after 30 days (per FR-009H)
   - User can restore from trash within 30 days (per FR-009F)
   - Automated cleanup job runs daily to delete expired trash items

3. **Deleted User Accounts** (Immediate Permanent Deletion):
   - When user deletes account: Cascade delete all associated data immediately
   - No grace period for account deletion (user must confirm with password)
   - Anonymize user ID in logs/metrics (GDPR compliance)

4. **Logs and Metrics** (90-Day Retention):
   - Application logs: 90 days, then deleted
   - AI generation metrics: 90 days, then aggregated and anonymized
   - Security logs: 1 year retention (audit compliance)

5. **Anonymous Usage Analytics** (Indefinite Retention):
   - Aggregated, anonymized usage statistics: Retained for product improvement
   - No personally identifiable information (PII)
   - Example: "Average document generation time per week"

**Compliance Considerations** (Phase 2):
- GDPR: Right to erasure (user can request full data deletion)
- Data export: User can download all their data (projects, tasks, documents)
- Data portability: Export format is JSON (machine-readable)

**Phase 1 MVP**:
- Implement 30-day trash retention only
- Manual account deletion upon request (no self-service UI)
- No data export feature (Phase 2)

---

### CHK040: Orphaned Data Handling Requirements

**Requirement ID**: FR-102

**Description**: System MUST handle orphaned data (files without database records or vice versa) to prevent data corruption and storage waste.

**Types of Orphaned Data**:

1. **Orphaned Files** (files in storage but no DB record):
   - **Cause**: Database transaction fails after file upload, or manual file deletion bypassed
   - **Detection**: Weekly cron job compares `CodeFile.storage_path` DB records with actual filesystem
   - **Handling**: Delete orphaned files older than 7 days (grace period for inflight uploads)

2. **Missing Files** (DB record but file doesn't exist):
   - **Cause**: File manually deleted, storage failure, migration error
   - **Detection**: On-demand when user accesses task (file read fails)
   - **Handling**: Mark task status as "file_missing", display error to user: "Code file not found. Please re-upload."

3. **Orphaned Database Records** (rare):
   - **Cause**: Foreign key constraint failures, partial cascade deletes
   - **Detection**: Database referential integrity checks (automated via pg_cron or manual)
   - **Handling**: Log warnings, manual cleanup with admin scripts (rare edge case)

**Prevention Mechanisms**:

1. **Atomic Operations**:
   - File upload and DB insert in a single transaction
   - On transaction rollback, delete uploaded file (cleanup handler)
   - Use database transactions for all create/update/delete operations

2. **Referential Integrity**:
   - All foreign key constraints include `ON DELETE CASCADE` or `ON DELETE SET NULL`
   - Soft deletes prevent orphans (deleted = trashed, not removed)

3. **File Storage Path Validation**:
   - All file paths stored in DB with checksums (SHA-256)
   - On file read, verify checksum matches (detect corruption/tampering)

**Cleanup Jobs**:

1. **Orphaned File Cleanup** (Weekly):
   ```sql
   -- Pseudocode: Find files in storage not in database
   SELECT storage_path FROM filesystem
   WHERE NOT EXISTS (SELECT 1 FROM code_files WHERE storage_path = filesystem.path)
   AND created_at < NOW() - INTERVAL '7 days'
   -- Delete these files
   ```

2. **Missing File Detection** (On-Access):
   ```python
   if not os.path.exists(code_file.storage_path):
       task.status = "file_missing"
       logger.error(f"Missing file for task {task.id}: {code_file.storage_path}")
       raise FileNotFoundError("Code file missing")
   ```

**Phase 1 MVP**:
- Implement atomic upload transactions
- Implement on-access missing file detection
- Manual orphaned file cleanup (no automated job)

---

## 4. API Contract Quality Requirements

### CHK046: Pagination Requirements

**Requirement ID**: FR-103

**Description**: List endpoints MUST support pagination to handle large datasets efficiently.

**Scope**: Explicitly EXCLUDED from Phase 1 MVP (per design review), documented for Phase 2.

**Phase 1 MVP Behavior**:
- All list endpoints return complete results (no pagination)
- Reasonable limits: Max 100 projects per user, max 1000 tasks per project
- If user exceeds limits, suggest archiving/deleting old projects

**Phase 2 Requirements** (Future):

1. **Pagination Parameters**:
   - `page`: Page number (1-based, default: 1)
   - `page_size`: Items per page (default: 20, max: 100)
   - Alternative: Cursor-based pagination (`cursor` parameter)

2. **Response Format**:
   ```json
   {
     "data": [...],
     "pagination": {
       "page": 1,
       "page_size": 20,
       "total_items": 150,
       "total_pages": 8,
       "has_next": true,
       "has_prev": false
     }
   }
   ```

3. **Endpoints Requiring Pagination**:
   - `GET /api/v1/projects` (user's project list)
   - `GET /api/v1/projects/{id}/tasks` (project's task list)
   - `GET /api/v1/tasks/{id}/questions` (Q&A history)

**Rationale for Exclusion**:
- MVP targets small user base with limited projects/tasks
- Pagination adds complexity (client-side handling, testing)
- YAGNI: Implement when users actually hit limits

---

### CHK049: Comprehensive Rate Limiting Requirements

**Requirement ID**: FR-104

**Description**: API endpoints MUST implement rate limiting to prevent abuse and ensure fair resource allocation.

**Rate Limiting Strategy**:

1. **Authentication Endpoints** (Strict):
   - `POST /api/v1/auth/login`: 5 attempts per 15 minutes per IP address
   - `POST /api/v1/auth/register`: 3 accounts per hour per IP address
   - `POST /api/v1/auth/refresh`: 10 requests per minute per user
   - **Reason**: Prevent brute force attacks, account enumeration, credential stuffing

2. **AI Generation Endpoints** (Resource-Intensive):
   - `POST /api/v1/tasks` (triggers document generation): 3 tasks per hour per user
   - `POST /api/v1/tasks/{id}/questions`: 20 questions per 10 minutes per user
   - **Reason**: Limit AI API costs, prevent quota exhaustion, ensure fair access

3. **Read Endpoints** (Permissive):
   - `GET /api/v1/projects`: 100 requests per minute per user
   - `GET /api/v1/tasks/{id}`: 100 requests per minute per user
   - `GET /api/v1/tasks/{id}/document`: 100 requests per minute per user
   - **Reason**: Allow normal browsing, prevent scraping

4. **Write Endpoints** (Moderate):
   - `POST /api/v1/projects`: 10 per hour per user
   - `PUT /api/v1/tasks/{id}`: 30 per minute per user
   - `DELETE /api/v1/projects/{id}`: 10 per hour per user
   - **Reason**: Prevent accidental spam, allow normal usage

**Implementation**:
- Use Redis for rate limit counters (fast, atomic increments)
- Sliding window algorithm (more accurate than fixed window)
- Rate limit key format: `rate_limit:{endpoint}:{user_id or ip}:{window}`

**Response Headers**:
```
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 15
X-RateLimit-Reset: 1637000000 (Unix timestamp)
```

**Error Response** (HTTP 429):
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please wait 8 minutes before trying again.",
  "retry_after": 480
}
```

**Phase 1 MVP**:
- Implement rate limiting for authentication endpoints (critical security)
- Implement rate limiting for AI generation endpoints (cost control)
- Permissive limits for other endpoints (monitoring only, no enforcement)

---

### CHK051: File Download/Streaming Requirements

**Requirement ID**: FR-105

**Description**: Users MUST be able to download their uploaded code files.

**Download Endpoints**:

1. **Single File Download**:
   - `GET /api/v1/tasks/{task_id}/code/download`
   - Returns: Original uploaded file with correct Content-Type and filename
   - Headers:
     ```
     Content-Type: text/x-python (or detected MIME type)
     Content-Disposition: attachment; filename="calculator.py"
     Content-Length: 1234
     ```

2. **Multiple Files (Folder Upload)**:
   - `GET /api/v1/tasks/{task_id}/code/download?format=zip`
   - Returns: ZIP archive containing all files with original directory structure
   - Headers:
     ```
     Content-Type: application/zip
     Content-Disposition: attachment; filename="task-001-code.zip"
     ```

**Security Requirements**:
- Validate user owns the task (prevent unauthorized access)
- Sanitize filenames (prevent path traversal: `../../etc/passwd`)
- Scan files for malware before download (ClamAV integration - Phase 2)
- Rate limiting: 100 downloads per hour per user (prevent scraping)

**Streaming for Large Files**:
- Use chunked transfer encoding for files >1MB
- Stream from disk without loading entire file into memory
- Example (FastAPI):
  ```python
  return StreamingResponse(
      file_stream(file_path),
      media_type=mime_type,
      headers={"Content-Disposition": f"attachment; filename={safe_filename}"}
  )
  ```

**Error Handling**:
- 404: File not found or task doesn't exist
- 403: User doesn't own the task
- 410: File was permanently deleted (task in trash >30 days)

**Phase 1 MVP**:
- Implement single file download
- Implement folder download as ZIP
- Basic filename sanitization
- No malware scanning (Phase 2)

---

## 5. Performance & Scalability Requirements

### CHK061: Background Task Monitoring Requirements

**Requirement ID**: FR-106

**Description**: Celery background tasks (document generation, practice problems, etc.) MUST be monitored for failures and performance issues.

**Monitoring Metrics**:

1. **Task Execution Metrics**:
   - Task success rate (% of tasks completed successfully)
   - Task failure rate (% of tasks failed)
   - Task retry count (how many tasks needed retries)
   - Task duration (P50, P95, P99 latencies)

2. **Queue Metrics**:
   - Queue depth (number of pending tasks)
   - Queue wait time (time from submission to execution start)
   - Worker utilization (% of workers busy)

3. **Failure Metrics**:
   - Failure reasons (timeout, exception type, validation error)
   - Stuck tasks (running >30 minutes for document generation)
   - Dead letter queue size (tasks that failed permanently)

**Monitoring Tools**:

1. **Celery Flower** (Web Dashboard):
   - Real-time task monitoring
   - Worker status and statistics
   - Task history and retry tracking
   - URL: `http://localhost:5555` (development)

2. **Structured Logging**:
   - All task starts, completions, failures logged to JSON
   - Log fields: task_id, task_name, status, duration_ms, error_message, user_id, task_metadata
   - Logs ingested by centralized logging (Phase 2: ELK stack or CloudWatch)

3. **Application Metrics**:
   - Store task metrics in `background_task_metrics` table
   - Fields: task_id, task_type, status, started_at, completed_at, duration_ms, retry_count, error_type
   - Retention: 90 days

**Alerting** (Phase 2):
- Alert when task failure rate >10% in last hour
- Alert when queue depth >100 tasks
- Alert when average task duration >2x baseline
- Alert when worker count drops below minimum

**Phase 1 MVP**:
- Enable Celery Flower for development monitoring
- Log all task executions with structured logs
- Store task metrics in database table
- Manual monitoring (no automated alerts)

---

### CHK063: Performance Degradation Handling Requirements

**Requirement ID**: FR-107

**Description**: When system performance degrades (e.g., AI service slow, database overloaded), system MUST gracefully degrade service rather than fail completely.

**Performance Targets** (from spec):
- Document generation: <3 minutes (FR-083)
- Q&A response: <10 seconds (FR-087)
- UI interactions: <200ms (Plan §Performance Goals)
- Page load: <3 seconds (Plan §Performance Goals)

**Degradation Triggers**:
1. AI service response time >2x normal (e.g., >6 minutes for documents)
2. Database query latency >1 second
3. Queue depth >50 pending tasks
4. Worker utilization >90% for >5 minutes

**Graceful Degradation Strategies**:

1. **AI Service Degradation**:
   - **Trigger**: Gemini API consistently slow (>6 min for documents)
   - **Action**:
     - Display warning: "AI service is slower than usual. Your document may take up to 10 minutes."
     - Increase timeout to 600s (10 minutes)
     - Reduce concurrent AI requests (from 3 to 1 per user)
     - Disable Q&A temporarily: "Q&A is temporarily unavailable. Please try again later."

2. **Database Degradation**:
   - **Trigger**: Query latency >1s
   - **Action**:
     - Enable aggressive caching (Redis)
     - Reduce complex queries (skip aggregations, return raw data)
     - Display cached data with timestamp: "Last updated: 2 minutes ago"

3. **Queue Overload**:
   - **Trigger**: Queue depth >50 tasks
   - **Action**:
     - Display queue position: "Your request is #23 in queue. Estimated wait: 45 minutes."
     - Reject new task submissions if queue >100: "System is at capacity. Please try again in 1 hour."
     - Prioritize paying users (Phase 2)

4. **High Load**:
   - **Trigger**: CPU >80%, memory >90%
   - **Action**:
     - Disable non-essential features (progress calculations, analytics)
     - Return simplified responses (skip optional fields)
     - Display system status banner: "System is experiencing high load. Some features may be slow."

**Recovery**:
- Auto-recovery when metrics return to normal for 5 minutes
- Clear degradation warnings from UI
- Send queued tasks for processing

**User Communication**:
- Transparent status messages (no vague "Please try again later")
- Estimated wait times when possible
- Option to cancel and retry later

**Phase 1 MVP**:
- Implement AI service degradation handling (critical for cost control)
- Implement queue overload messaging
- Monitor metrics manually, no auto-degradation (Phase 2)

---

## 6. Security & Authentication Requirements

### CHK072: Password Reset Requirements

**Requirement ID**: FR-108

**Description**: Users MUST be able to reset their password if forgotten.

**Scope**: Explicitly EXCLUDED from Phase 1 MVP (per design review), documented for Phase 2.

**Rationale for Exclusion**:
- MVP targets small, known user base (developers testing)
- Admin can manually reset passwords via database during MVP
- Password reset requires email infrastructure (SMTP, templates, etc.)
- Adds complexity: token generation, email delivery, security considerations

**Phase 2 Requirements** (Future):

1. **Reset Flow**:
   - User clicks "Forgot Password" on login page
   - User enters email address
   - System sends reset email with one-time token link
   - User clicks link, enters new password
   - Token expires after use or 1 hour

2. **Security Requirements**:
   - Reset token: Cryptographically secure random (32 bytes, hex-encoded)
   - Token storage: Hashed in database (bcrypt)
   - Token expiration: 1 hour
   - Single-use tokens (deleted after successful reset)
   - Rate limiting: 3 reset requests per hour per email

3. **Email Requirements**:
   - From address: noreply@codelearning.com
   - Subject: "Reset Your Password"
   - Body: Plain text + HTML template
   - Link format: `https://app.com/reset-password?token=abc123`
   - No sensitive data in email (no password, no user ID)

**Phase 1 MVP Workaround**:
- User contacts admin via support email
- Admin manually updates password hash in database
- Admin notifies user of temporary password
- User logs in and changes password immediately

---

### CHK073: Concurrent Session Management Requirements

**Requirement ID**: FR-109

**Description**: System MUST handle concurrent sessions (multiple devices/browsers) for the same user.

**Requirements**:

1. **Allow Concurrent Sessions**:
   - Users can log in from multiple devices simultaneously
   - Each session has independent JWT token pair (access + refresh)
   - No limit on concurrent sessions (YAGNI: most users have 1-2 devices)

2. **Token Management**:
   - Refresh tokens stored in `refresh_tokens` table with fields:
     - `id`, `user_id`, `token_hash`, `device_info`, `created_at`, `expires_at`, `revoked_at`
   - Each refresh token tied to a session (identified by device fingerprint)
   - Refresh token expiration: 7 days (per research.md)

3. **Session Visibility** (Phase 2):
   - User can view active sessions: "You're logged in on: Chrome (Windows), Safari (iPhone)"
   - User can revoke specific sessions: "Log out Chrome (Windows)"
   - Security feature: "If you don't recognize a device, revoke it immediately"

4. **Session Revocation**:
   - User changes password → Revoke ALL refresh tokens (force re-login everywhere)
   - User logs out → Revoke current refresh token only
   - User revokes session → Revoke specific refresh token
   - Revocation: Set `revoked_at` timestamp, invalidate immediately

5. **Security Considerations**:
   - No cross-device session sharing (each device has unique refresh token)
   - Access tokens are stateless JWT (cannot revoke individually)
   - Access token short expiration (15 minutes) limits damage if stolen

**Conflict Resolution**:
- No conflicts expected (users rarely edit same data from multiple devices simultaneously)
- If conflict occurs (unlikely in educational platform): Last write wins (simple, acceptable for MVP)
- Optimistic locking for critical operations (Phase 2)

**Phase 1 MVP**:
- Allow unlimited concurrent sessions
- Store refresh tokens in database
- Revoke all sessions on password change
- No session visibility UI (Phase 2)

---

### CHK077: Security Event Logging Requirements

**Requirement ID**: FR-110

**Description**: Security-relevant events MUST be logged for audit, monitoring, and incident response.

**Events to Log**:

1. **Authentication Events**:
   - Login attempts (success and failure)
   - Logout events
   - Password changes
   - Token refresh attempts (success and failure)
   - Account creation
   - Account deletion

2. **Authorization Events**:
   - Access denied (403 errors)
   - Unauthorized access attempts (401 errors)
   - Privilege escalation attempts (if RBAC added in future)

3. **Data Access Events** (High-Value Data):
   - Code file uploads
   - Code file downloads
   - Document generation requests
   - Task deletions (soft delete)
   - Project deletions (soft delete)
   - Permanent deletions (trash cleanup)

4. **Suspicious Activities**:
   - Rate limit violations (429 errors)
   - Input validation failures (potential injection attacks)
   - File upload rejections (malicious file types, oversized files)
   - Multiple failed login attempts (>3 in 10 minutes)
   - Token reuse attempts (refresh token already used)

**Log Format** (Structured JSON):
```json
{
  "timestamp": "2025-11-17T10:30:45.123Z",
  "event_type": "login_failed",
  "user_id": "uuid or null if not authenticated",
  "email": "user@example.com or null",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "details": {
    "reason": "invalid_password",
    "attempt_count": 3
  },
  "severity": "warning"
}
```

**Log Storage**:
- Development: Local JSON files (rotated daily)
- Production: Centralized logging service (e.g., CloudWatch Logs, Datadog)
- Retention: 1 year for security logs (compliance)
- Search: Full-text search enabled for incident investigation

**Log Levels by Severity**:
- **INFO**: Successful logins, account creation, normal operations
- **WARNING**: Failed logins, rate limit hits, validation errors
- **ERROR**: Authorization failures, unexpected errors
- **CRITICAL**: Multiple failed login attempts, potential security breaches

**Privacy Considerations**:
- Never log passwords (even failed attempts)
- Hash or truncate sensitive data (email: `u***@example.com`)
- Anonymize logs after 90 days (keep aggregate statistics only)

**Phase 1 MVP**:
- Log authentication events (login, logout, failures)
- Log authorization failures (401, 403)
- Log file uploads and deletions
- Store logs in local JSON files (structured format)
- Manual log review (no automated alerts)

---

## 7. UX & User Experience Requirements

### CHK084: Error Message Requirements

**Requirement ID**: FR-111

**Description**: Error messages MUST be user-friendly, actionable, and consistent across the application.

**Error Message Guidelines**:

1. **Language**:
   - All error messages in Korean (primary user language)
   - Use simple, everyday language (no technical jargon)
   - Exception: HTTP status codes in English (standard)

2. **Structure** (3 parts):
   - **What happened**: Clear description of the error
   - **Why it happened**: Brief explanation (if helpful)
   - **What to do**: Actionable next steps

3. **Examples**:

   **Good Error Messages**:
   - "파일 업로드 실패: 파일 크기가 10MB를 초과합니다. 더 작은 파일을 선택하거나 코드를 여러 태스크로 나누어 업로드하세요."
     - What: File upload failed
     - Why: File too large (>10MB)
     - Action: Upload smaller file or split code

   - "문서 생성 실패: AI 서비스가 응답하지 않습니다. 잠시 후 다시 시도하거나 고객지원에 문의하세요."
     - What: Document generation failed
     - Why: AI service unavailable
     - Action: Retry later or contact support

   **Bad Error Messages** (Avoid):
   - "Error 500: Internal Server Error" (Too vague, no action)
   - "Database connection failed: ECONNREFUSED 127.0.0.1:5432" (Too technical)
   - "An unexpected error occurred" (Not helpful)

4. **Error Categories**:

   **Validation Errors** (400):
   - "프로젝트 제목은 최소 1자 이상이어야 합니다."
   - "태스크 설명은 최대 500자까지 입력 가능합니다."

   **Authentication Errors** (401):
   - "로그인이 필요합니다. 로그인 페이지로 이동합니다."
   - "세션이 만료되었습니다. 다시 로그인하세요."

   **Authorization Errors** (403):
   - "이 프로젝트에 접근할 권한이 없습니다."
   - "다른 사용자의 태스크는 수정할 수 없습니다."

   **Not Found Errors** (404):
   - "요청한 프로젝트를 찾을 수 없습니다. 삭제되었거나 존재하지 않는 프로젝트입니다."
   - "요청한 페이지를 찾을 수 없습니다."

   **Rate Limit Errors** (429):
   - "요청이 너무 많습니다. 8분 후 다시 시도하세요."
   - "하루 AI 사용량을 초과했습니다. 내일 다시 시도하세요."

   **Server Errors** (500):
   - "서버 오류가 발생했습니다. 잠시 후 다시 시도하세요. 문제가 계속되면 고객지원에 문의하세요."

5. **Error Response Format** (API):
```json
{
  "error": "file_too_large",
  "message": "파일 크기가 10MB를 초과합니다.",
  "details": {
    "max_size_mb": 10,
    "uploaded_size_mb": 15.3
  },
  "suggestion": "더 작은 파일을 선택하거나 코드를 여러 태스크로 나누어 업로드하세요."
}
```

**Consistency Rules**:
- Use the same error message for the same error type across all endpoints
- Maintain error message dictionary/constants (no hardcoded strings scattered)
- Translate all error messages to Korean (centralized translation file)

**Phase 1 MVP**:
- Implement error message structure (what/why/action)
- Create error message constants file
- Korean error messages for all user-facing errors
- English for development/debug logs

---

### CHK085: Success Confirmation Requirements

**Requirement ID**: FR-112

**Description**: User actions MUST provide clear success feedback to confirm completion.

**Feedback Mechanisms**:

1. **Toast Notifications** (Temporary, Non-Blocking):
   - Position: Top-right corner
   - Duration: 3 seconds (auto-dismiss)
   - Types: Success (green), Info (blue), Warning (yellow), Error (red)
   - Examples:
     - "프로젝트가 생성되었습니다."
     - "태스크가 삭제되었습니다."
     - "파일 업로드 완료."

2. **Inline Success Messages** (Persistent, Contextual):
   - Display below/near the action button
   - Remain visible until user navigates away
   - Examples:
     - "✓ 프로젝트 설정이 저장되었습니다." (below Save button)
     - "✓ 진행률이 업데이트되었습니다." (below progress bar)

3. **UI State Changes** (Visual Feedback):
   - Button states: Disabled → Loading → Success → Enabled
   - Example: "Save" → "Saving..." (spinner) → "Saved ✓" (2s) → "Save"
   - Progress indicators: 0% → 50% → 100% ✓
   - Status badges: 🟡 In Progress → 🟢 Completed

4. **Page Redirects with Confirmation**:
   - After creating project: Redirect to project detail page
   - After creating task: Redirect to task detail page (ready to upload)
   - Display toast: "프로젝트 'My Todo App'이 생성되었습니다."

**Success Confirmations by Action**:

| Action | Feedback Type | Message (Korean) |
|--------|---------------|------------------|
| Create project | Toast + Redirect | "프로젝트가 생성되었습니다." |
| Create task | Toast + Redirect | "태스크가 생성되었습니다. 코드를 업로드하세요." |
| Upload code | Toast | "코드 업로드 완료. 문서 생성 중..." |
| Delete project | Toast | "프로젝트가 휴지통으로 이동되었습니다." |
| Restore from trash | Toast | "프로젝트가 복원되었습니다." |
| Mark task complete | UI state change | Task card shows ✅ checkmark |
| Answer practice problem | Inline message | "✓ 정답입니다!" or "✗ 다시 시도하세요." |
| Ask question | Toast | "질문이 전송되었습니다. 답변 생성 중..." |
| Update profile | Toast | "프로필이 업데이트되었습니다." |

**Accessibility**:
- Screen reader announcements for toast notifications
- ARIA live regions for dynamic content updates
- Keyboard focus management after actions (move to next logical element)

**Phase 1 MVP**:
- Implement toast notification component
- Add success messages for all create/update/delete actions
- Use UI state changes for progress tracking
- Korean messages for all user-facing feedback

---

### CHK086: Empty State Requirements

**Requirement ID**: FR-113

**Description**: When users have no data (no projects, no tasks, no progress), display helpful empty states instead of blank pages.

**Empty States to Implement**:

1. **No Projects**:
   - **When**: New user, or user deleted all projects
   - **Display**:
     - Icon: 📁 (folder icon)
     - Title: "아직 프로젝트가 없습니다"
     - Description: "프로젝트를 만들어 AI 코드 학습을 시작하세요. 프로젝트는 관련된 학습 태스크들을 모아둔 폴더입니다."
     - Action: Large "첫 프로젝트 만들기" button
     - Example: "예: '나의 Todo 앱', '계산기 프로그램'"

2. **No Tasks in Project**:
   - **When**: Project created but no tasks added
   - **Display**:
     - Icon: 📝 (document icon)
     - Title: "아직 태스크가 없습니다"
     - Description: "코드를 업로드하고 학습 자료를 생성하려면 태스크를 추가하세요."
     - Action: "첫 태스크 추가" button
     - Tip: "💡 팁: 작은 코드 단위로 나누어 학습하면 이해가 쉬워집니다."

3. **No Learning Document** (Document Generation in Progress):
   - **When**: Task created, code uploaded, document not yet generated
   - **Display**:
     - Icon: ⏳ (hourglass)
     - Title: "학습 문서 생성 중..."
     - Description: "AI가 코드를 분석하고 초보자용 설명을 작성하고 있습니다."
     - Progress: Spinner or progress bar
     - Estimated time: "약 2분 남음"

4. **No Practice Problems** (Document Not Complete):
   - **When**: User clicks Practice tab but document not fully read
   - **Display**:
     - Icon: 📖 (book icon)
     - Title: "학습 문서를 먼저 읽어주세요"
     - Description: "연습 문제를 풀기 전에 학습 문서를 모두 읽어야 합니다."
     - Action: "학습 문서로 이동" button

5. **No Questions Asked**:
   - **When**: User hasn't asked any questions yet
   - **Display**:
     - Icon: 💬 (speech bubble)
     - Title: "아직 질문이 없습니다"
     - Description: "이해가 안 되는 부분이 있나요? 언제든지 질문하세요."
     - Example: "예: '변수가 정확히 뭔가요?', '이 코드는 왜 이렇게 동작하나요?'"

6. **No Progress** (Task Not Started):
   - **When**: Task exists but no progress (document not read, no practice done)
   - **Display**:
     - Icon: 🎯 (target icon)
     - Title: "학습을 시작하세요"
     - Description: "학습 문서를 읽고 연습 문제를 풀어보세요."
     - Action: "학습 시작" button → Navigate to document

**Design Consistency**:
- All empty states use same layout: Icon → Title → Description → Action Button
- Friendly, encouraging tone (not negative: "You have nothing")
- Always provide clear next action (CTA button)
- Use emojis for visual interest (consistent with beginner-friendly brand)

**Phase 1 MVP**:
- Implement all 6 empty states
- Use placeholder illustrations or emojis (no custom artwork)
- Korean text for all empty states

---

### CHK087: Navigation Requirements

**Requirement ID**: FR-114

**Description**: Navigation patterns MUST be consistent and intuitive across all pages.

**Navigation Structure**:

1. **Top Navigation Bar** (Always Visible):
   - Logo: "CodeLearn" (links to dashboard/home)
   - Main Menu:
     - "대시보드" (Dashboard) - Project list
     - "학습 진행률" (Progress) - Overall progress view
   - Right Side:
     - User avatar/email
     - Settings dropdown: "프로필 설정", "로그아웃"

2. **Breadcrumb Navigation** (Contextual):
   - Show current location in hierarchy
   - Examples:
     - "대시보드 > 나의 Todo 앱" (Project detail page)
     - "대시보드 > 나의 Todo 앱 > Task 1: 할 일 추가 기능" (Task detail page)
     - "대시보드 > 나의 Todo 앱 > Task 1: 할 일 추가 기능 > 학습 문서" (Document page)
   - Each breadcrumb is clickable (navigate to parent levels)

3. **Tab Navigation** (Within Task Detail Page):
   - Tabs: "학습 문서" | "연습 문제" | "질문 & 답변"
   - Active tab highlighted (underline, bold, or color change)
   - Tab changes without page reload (SPA behavior)

4. **Side Navigation** (Optional, for Project Detail Page):
   - Show task list in sidebar (Task 1, Task 2, Task 3...)
   - Highlight current task
   - Click to navigate to different task
   - Collapse/expand sidebar button

5. **Back Navigation**:
   - Browser back button works correctly (SPA routing)
   - Explicit "← 뒤로" link in top-left corner (fallback)

**Navigation Rules**:
- Consistent navigation bar on all pages (except login/register)
- Active page/tab always clearly indicated (visual distinction)
- Navigation state preserved on page refresh (SPA with URL routing)
- Keyboard navigation: Tab key to navigate links, Enter to activate

**Mobile Responsive** (Phase 2):
- Top nav collapses to hamburger menu
- Breadcrumbs truncate long project/task names
- Side navigation becomes full-screen drawer

**Phase 1 MVP**:
- Top navigation bar (logo, menu, user dropdown)
- Breadcrumb navigation on all non-dashboard pages
- Tab navigation on task detail page
- Browser back button support (React Router)

---

### CHK088: Keyboard Navigation Requirements

**Requirement ID**: FR-115

**Description**: All interactive elements MUST be accessible via keyboard (no mouse required).

**Scope**: Partially EXCLUDED from Phase 1 MVP (basic keyboard support only), full accessibility in Phase 2.

**Phase 1 Minimum Requirements** (Basic Accessibility):

1. **Tab Navigation**:
   - All interactive elements (buttons, links, inputs) reachable via Tab key
   - Logical tab order (top-left to bottom-right, follows visual flow)
   - Visible focus indicators (blue outline, highlight, etc.)
   - Skip to main content link (bypass navigation)

2. **Enter/Space Activation**:
   - Buttons: Activate on Enter or Space
   - Links: Activate on Enter
   - Checkboxes: Toggle on Space

3. **Form Navigation**:
   - Tab moves between form fields
   - Enter submits form (when focused on submit button or input field)
   - Escape clears input or closes modal

4. **Modal/Dialog Keyboard Handling**:
   - Focus trapped inside modal (Tab doesn't leave modal)
   - Escape closes modal
   - Focus returns to trigger element on close

**Phase 2 Advanced Requirements** (Full Accessibility):

1. **Arrow Key Navigation**:
   - Tab groups: Left/Right arrow to navigate tabs
   - Lists: Up/Down arrow to navigate list items
   - Menus: Up/Down to navigate menu items, Enter to select

2. **Keyboard Shortcuts**:
   - Ctrl+K: Global search (tasks, projects)
   - Ctrl+N: Create new project
   - Ctrl+T: Create new task
   - ?: Show keyboard shortcuts help overlay

3. **Screen Reader Support**:
   - ARIA labels for all interactive elements
   - ARIA live regions for dynamic content (toast notifications)
   - Semantic HTML (nav, main, section, article)

**Testing**:
- Manual keyboard navigation test (disconnect mouse)
- Verify all critical flows: login, create project, create task, read document, ask question
- Ensure no keyboard traps (elements you can't Tab out of)

**Phase 1 MVP**:
- Implement basic Tab navigation
- Visible focus indicators
- Enter/Space activation for buttons
- Modal focus trapping and Escape to close
- No custom keyboard shortcuts (Phase 2)

---

### CHK090: Browser Compatibility Requirements

**Requirement ID**: NFR-003

**Description**: Application MUST work correctly on modern browsers, with specific version support defined.

**Supported Browsers** (Phase 1 MVP):

1. **Desktop Browsers**:
   - Google Chrome: Latest 2 versions (e.g., v120, v121)
   - Microsoft Edge: Latest 2 versions (Chromium-based)
   - Mozilla Firefox: Latest 2 versions
   - Safari: Latest 2 versions (macOS only)

2. **Minimum Browser Versions**:
   - Chrome/Edge: v100+ (released April 2022)
   - Firefox: v100+ (released May 2022)
   - Safari: v15+ (released September 2021)

**Not Supported**:
- Internet Explorer (any version) - Deprecated by Microsoft
- Opera, Brave, Vivaldi - Not tested, but likely work (Chromium-based)
- Mobile browsers - Phase 2 (explicitly excluded per spec assumptions)
- Old browser versions (>2 years old)

**Browser Features Required**:
- ES6+ JavaScript support (async/await, classes, modules)
- CSS Grid and Flexbox
- Fetch API (no XMLHttpRequest)
- LocalStorage/SessionStorage
- WebSocket (for future features)

**Polyfills/Transpilation**:
- Use Vite + Babel to transpile modern JavaScript to ES2020 target
- Include core-js polyfills for Array.prototype.at, Promise.allSettled, etc.
- CSS autoprefixer for vendor prefixes

**Testing Strategy**:
- Primary development/testing: Chrome Latest
- Manual testing on Firefox, Safari, Edge before releases
- Automated E2E tests run on Chrome only (Phase 1)
- BrowserStack for broader testing (Phase 2)

**Browser Detection**:
- Display warning banner for unsupported browsers:
  "이 브라우저는 지원되지 않습니다. 최신 버전의 Chrome, Firefox, Edge, 또는 Safari를 사용하세요."
- Detect browser: `navigator.userAgent` parsing or modern `navigator.userAgentData`

**Phase 1 MVP**:
- Support latest 2 versions of Chrome, Firefox, Edge, Safari
- No IE support
- Warning banner for unsupported browsers
- Manual testing on Chrome + 1 other browser (Firefox or Edge)

---

## 8. Progress Tracking Requirements

### CHK094: Progress Reset Requirements

**Requirement ID**: FR-116

**Description**: Users MUST be able to reset their progress if they want to re-learn a task from scratch.

**Scope**: Explicitly EXCLUDED from Phase 1 MVP, documented for Phase 2.

**Rationale for Exclusion**:
- YAGNI: Uncommon use case (users rarely want to "unlearn" progress)
- MVP focuses on forward progress tracking, not resetting
- Workaround: User can delete task and recreate (achieves same result)
- Adds complexity: Confirm dialog, progress history, cascade effects

**Phase 2 Requirements** (Future):

1. **Reset Options**:
   - Reset task progress: Clear document reading progress, practice completion, question history
   - Reset project progress: Reset all tasks in project
   - Reset user progress: Clear all progress for user (nuclear option)

2. **Reset Confirmation**:
   - Display confirmation dialog: "진행률을 초기화하시겠습니까? 이 작업은 되돌릴 수 없습니다."
   - Require checkbox: "네, 이 태스크의 모든 진행률을 삭제합니다."
   - Require typing "RESET" to confirm (prevent accidental clicks)

3. **Reset Behavior**:
   - Delete progress records from `progress` table
   - Delete question history from `questions` table
   - Keep learning document and practice problems (content immutability)
   - Update task status to "not_started"
   - Log reset action for analytics (why are users resetting?)

4. **Progress History** (Optional):
   - Keep archive of old progress: "You completed this task on 2025-11-10 (reset on 2025-11-15)"
   - Allow viewing old completion dates
   - Analytics: Track how often progress is reset

**Phase 1 MVP Workaround**:
- User can delete task (move to trash) and create new task with same code
- Trash retention (30 days) allows recovery if accidental deletion
- Admin can manually reset progress via database if requested

---

### CHK098: Progress Trends Requirements

**Requirement ID**: FR-117

**Description**: Users can view their learning progress trends over time (e.g., tasks completed per week, concepts learned).

**Scope**: Explicitly EXCLUDED from Phase 1 MVP, documented for Phase 2.

**Rationale for Exclusion**:
- YAGNI: MVP focuses on current progress, not historical trends
- Requires time-series data storage and visualization libraries
- Not critical for core learning experience
- Adds complexity: Date range selection, chart rendering, data aggregation

**Phase 2 Requirements** (Future):

1. **Trend Metrics**:
   - Tasks completed per week/month
   - Questions asked per week/month
   - Average time to complete a task
   - Concepts learned (count unique concepts across all documents)
   - Streak: Consecutive days with learning activity

2. **Visualizations**:
   - Line chart: Tasks completed over time
   - Bar chart: Questions asked per week
   - Calendar heatmap: Learning activity (GitHub-style)
   - Pie chart: Progress distribution (completed, in progress, not started)

3. **Date Ranges**:
   - Last 7 days
   - Last 30 days
   - Last 3 months
   - All time
   - Custom date range picker

4. **Insights**:
   - "You've completed 5 tasks this month, 2 more than last month!"
   - "Your most productive day is Wednesday"
   - "You've learned 47 unique programming concepts"

**Data Requirements**:
- Store timestamps for all progress events (task_completed_at, question_asked_at)
- Aggregate data daily (cron job) for fast chart rendering
- Store aggregations in `progress_trends` table

**Phase 1 MVP**:
- Show only current progress (no trends)
- Store timestamps for future trend analysis
- Manually query database for basic statistics if needed

---

### CHK099: Progress Export Requirements

**Requirement ID**: FR-118

**Description**: Users can export their learning progress data for personal records or portfolio.

**Scope**: Explicitly EXCLUDED from Phase 1 MVP, documented for Phase 2.

**Rationale for Exclusion**:
- YAGNI: Uncommon use case (most users don't export data)
- MVP focuses on in-app experience, not data portability
- Adds complexity: Export format, file generation, GDPR compliance
- Not required for core learning experience

**Phase 2 Requirements** (Future):

1. **Export Formats**:
   - JSON: Machine-readable, complete data
   - CSV: Spreadsheet-friendly, tasks and progress only
   - PDF: Human-readable report with charts and summaries
   - Markdown: Portable text format for documentation

2. **Export Scope**:
   - Single task: Include task details, document, practice, questions
   - Single project: All tasks in project
   - All data: User profile, all projects, all tasks, all progress

3. **Export Contents**:
   - **Task Export**: Task title, code files, learning document, practice problems, questions & answers, progress
   - **Project Export**: Project title, description, all tasks, overall progress
   - **User Export**: Profile, all projects, aggregated statistics

4. **Export Triggers**:
   - Manual export: "내 데이터 내보내기" button in settings
   - Scheduled export: Weekly email with progress report (opt-in)
   - Account deletion export: Automatic export before permanent deletion (GDPR)

5. **Security**:
   - Exports contain user's own data only (no other users' data)
   - Exports generated on-demand (not pre-generated or cached)
   - Download link expires after 24 hours
   - Rate limiting: 5 exports per day per user

**File Format Examples**:

**JSON Export** (tasks.json):
```json
{
  "user_id": "uuid",
  "export_date": "2025-11-17T10:00:00Z",
  "projects": [
    {
      "title": "My Todo App",
      "tasks": [
        {
          "task_number": 1,
          "title": "Add Todo Function",
          "code": "...",
          "document": {...},
          "progress": "completed"
        }
      ]
    }
  ]
}
```

**CSV Export** (tasks.csv):
```csv
project,task_number,task_title,status,completed_date
My Todo App,1,Add Todo Function,completed,2025-11-15
My Todo App,2,Display List,in_progress,
```

**Phase 1 MVP**:
- No export feature
- All data stored in PostgreSQL (exportable via manual SQL queries if needed)
- Admin can generate exports via database dump if requested

---

## 9. Error Handling & Recovery Requirements

### CHK103: Background Task Rollback Requirements

**Requirement ID**: FR-119

**Description**: When a background task (Celery) fails, system MUST roll back partial changes to maintain data consistency.

**Rollback Scenarios**:

1. **Document Generation Failure Mid-Process**:
   - **Failure Point**: AI generated 3/7 chapters, then API timeout
   - **Rollback**: Delete partial document from database
   - **Recovery**: Task status set to "generation_failed", user can retry
   - **Data Integrity**: No orphaned partial documents

2. **Database Insert Failure**:
   - **Failure Point**: Document generated successfully, but DB insert fails (connection error, constraint violation)
   - **Rollback**: Delete generated document content (if stored), mark task as failed
   - **Recovery**: Retry task automatically (Celery retry mechanism)
   - **Data Integrity**: No documents in memory without DB records

3. **File Upload Failure After DB Insert**:
   - **Failure Point**: Task record created, code file upload fails (disk full, permission error)
   - **Rollback**: Delete task record from database (or mark as failed)
   - **Recovery**: User retries upload from scratch
   - **Data Integrity**: No task records without associated files

**Implementation Strategy**:

1. **Database Transactions**:
   ```python
   async with db.transaction():
       # All DB operations in a single transaction
       task = await create_task(...)
       document = await create_document(...)
       await update_progress(...)
       # If any operation fails, entire transaction rolls back
   ```

2. **Celery Task Cleanup**:
   ```python
   @celery.task(bind=True)
   def generate_document(self, task_id):
       try:
           # Generate document
           doc = generate_via_ai(...)
           # Save to DB
           save_document(doc)
       except Exception as e:
           # Rollback: Delete partial data
           cleanup_partial_document(task_id)
           # Update task status
           mark_task_failed(task_id, error=str(e))
           raise
   ```

3. **Compensation Actions** (Manual Rollback):
   - After failure, run cleanup function to remove orphaned data
   - Example: Delete uploaded file if DB insert failed
   - Example: Delete partial AI-generated content if validation failed

**Celery Retry Mechanism**:
- Automatic retry: Up to 3 attempts for transient errors (network, timeout)
- Exponential backoff: 60s, 120s, 240s
- Permanent failure: After 3 retries, mark task as permanently failed
- User notification: "Document generation failed after 3 attempts. Please contact support."

**Monitoring**:
- Log all rollback actions with task_id and reason
- Track rollback frequency (high rollback rate = systemic issue)
- Alert admin if rollback rate >10%

**Phase 1 MVP**:
- Use database transactions for all multi-step operations
- Implement basic Celery retry (3 attempts)
- Manual cleanup for orphaned data (no automated cleanup job)

---

### CHK105: Database Connection Failure Handling Requirements

**Requirement ID**: FR-120

**Description**: System MUST handle database connection failures gracefully without crashing or losing data.

**Connection Failure Scenarios**:

1. **Connection Pool Exhausted**:
   - **Cause**: Too many concurrent queries, connection leak
   - **Detection**: `asyncpg.exceptions.TooManyConnectionsError`
   - **Handling**:
     - Wait for available connection (timeout: 30s)
     - If timeout: Return HTTP 503 "Service Temporarily Unavailable"
     - User message: "서버가 과부하 상태입니다. 잠시 후 다시 시도하세요."

2. **Database Server Down**:
   - **Cause**: PostgreSQL crashed, network partition, maintenance
   - **Detection**: `asyncpg.exceptions.CannotConnectNowError`
   - **Handling**:
     - Retry connection: 3 attempts with 5s delay
     - If all retries fail: Return HTTP 503
     - User message: "데이터베이스 연결 실패. 잠시 후 다시 시도하세요."
     - Alert admin immediately (critical failure)

3. **Connection Lost Mid-Query**:
   - **Cause**: Long-running query, network interruption
   - **Detection**: `asyncpg.exceptions.ConnectionDoesNotExistError`
   - **Handling**:
     - Rollback transaction (if in transaction)
     - Retry query automatically (1 retry only)
     - If retry fails: Return HTTP 500
     - User message: "요청 처리 중 오류가 발생했습니다. 다시 시도하세요."

**Prevention Strategies**:

1. **Connection Pooling**:
   - Use `asyncpg` connection pool
   - Pool size: min=10, max=50 connections
   - Connection timeout: 30 seconds
   - Idle connection timeout: 5 minutes (recycle idle connections)

2. **Connection Health Checks**:
   - Ping database on connection acquisition: `SELECT 1`
   - Detect stale connections and recycle
   - Prevent using dead connections

3. **Query Timeouts**:
   - Set query timeout: 30 seconds (prevents hanging queries)
   - Cancel long-running queries automatically
   - Alert admin for queries that timeout frequently

**Graceful Degradation**:
- If database unavailable, disable write operations
- Serve cached data for read operations (if possible)
- Display banner: "시스템이 읽기 전용 모드로 실행 중입니다."

**Monitoring**:
- Track connection pool utilization (% of pool used)
- Track connection errors (count and type)
- Alert when error rate >5% or pool utilization >80%

**Phase 1 MVP**:
- Implement connection pooling (asyncpg)
- Retry connection failures (3 attempts)
- Return HTTP 503 on database unavailable
- No graceful degradation (Phase 2)

---

### CHK107: Concurrent Data Modification Handling Requirements

**Requirement ID**: FR-121

**Description**: When multiple users (or multiple sessions of the same user) modify the same data concurrently, system MUST handle conflicts gracefully.

**Conflict Scenarios**:

1. **Low Risk: Single-User Concurrent Edits** (Most Common):
   - **Scenario**: User edits project title on laptop, then edits same project on phone before saving laptop changes
   - **Frequency**: Rare (users unlikely to edit same project from multiple devices simultaneously)
   - **Handling**: Last write wins (simple, acceptable for MVP)
   - **Example**: Phone edit at 10:01am overwrites laptop edit at 10:00am

2. **Very Low Risk: Multi-User Concurrent Edits** (Phase 1 MVP is single-user):
   - **Scenario**: Two users editing the same project (not possible in MVP - user isolation)
   - **Handling**: N/A for Phase 1 (no shared projects)

3. **No Risk: Read-Only Concurrent Access**:
   - **Scenario**: User reading task on laptop while also reading on phone
   - **Handling**: No conflict (reads don't modify data)

**Conflict Resolution Strategy** (Phase 1 - Simple):

**Last Write Wins**:
- No conflict detection
- No optimistic locking
- Database timestamp `updated_at` reflects last modification
- Acceptable for MVP because:
  - Single-user application (no collaboration)
  - Conflicts extremely rare (user editing same data from multiple devices simultaneously)
  - Low stakes (educational data, not financial/medical)

**Phase 2 Requirements** (Optimistic Locking):

1. **Version-Based Locking**:
   - Add `version` column to all mutable tables
   - Increment version on every update
   - Update query includes version check:
     ```sql
     UPDATE projects
     SET title = 'New Title', version = version + 1, updated_at = NOW()
     WHERE id = 'uuid' AND version = 5
     -- If version doesn't match, 0 rows updated (conflict detected)
     ```

2. **Conflict Detection**:
   - If 0 rows updated: Conflict detected (another edit happened)
   - Return HTTP 409 Conflict
   - Response:
     ```json
     {
       "error": "edit_conflict",
       "message": "이 프로젝트가 다른 곳에서 수정되었습니다.",
       "current_version": {...},
       "your_version": {...}
     }
     ```

3. **Conflict Resolution UI**:
   - Display both versions (current vs. user's edit)
   - User chooses: "내 버전 사용" or "최신 버전 사용"
   - Option to merge manually

**Phase 1 MVP**:
- No conflict detection (last write wins)
- No optimistic locking
- Acceptable risk for educational single-user application

---

### CHK108: Transaction Rollback Requirements

**Requirement ID**: FR-122

**Description**: When database operations fail mid-transaction, all changes MUST be rolled back to maintain data integrity.

**Transaction Scenarios**:

1. **Task Creation with File Upload**:
   - **Operations**:
     1. Insert task record
     2. Insert code_file record with file path
     3. Upload file to storage
   - **Transaction Scope**: Steps 1-2 in DB transaction, Step 3 outside
   - **Failure Handling**:
     - If Step 1 fails: Rollback, return error
     - If Step 2 fails: Rollback Step 1, return error
     - If Step 3 fails: Rollback Steps 1-2, delete task, return error

2. **Project Deletion (Soft Delete)**:
   - **Operations**:
     1. Update project.deletion_status = 'trashed'
     2. Update all tasks.deletion_status = 'trashed'
     3. Set scheduled_deletion_at = NOW() + 30 days
   - **Transaction Scope**: All steps in single transaction
   - **Failure Handling**:
     - If any step fails: Rollback all, return error
     - Result: Either all trashed or none (no partial trash)

3. **Progress Update**:
   - **Operations**:
     1. Update progress.chapters_completed += 1
     2. Update progress.document_progress_percent
     3. Update task.updated_at
   - **Transaction Scope**: All steps in single transaction
   - **Failure Handling**:
     - If any step fails: Rollback all, return error
     - Result: Consistent progress state (no mismatched counters)

**Implementation** (FastAPI + SQLAlchemy):

```python
from sqlalchemy.ext.asyncio import AsyncSession

async def create_task_with_file(
    db: AsyncSession,
    project_id: UUID,
    title: str,
    file: UploadFile
):
    async with db.begin():  # Start transaction
        # Step 1: Create task
        task = Task(project_id=project_id, title=title)
        db.add(task)
        await db.flush()  # Get task.id without committing

        # Step 2: Save file metadata
        file_path = f"uploads/{task.id}/{file.filename}"
        code_file = CodeFile(task_id=task.id, storage_path=file_path)
        db.add(code_file)

        # Step 3: Upload file (outside transaction)
        try:
            await save_upload_file(file, file_path)
        except Exception as e:
            # File upload failed, rollback transaction
            await db.rollback()
            raise

        # Commit transaction (Steps 1-2)
        await db.commit()

    return task
```

**Rollback Guarantees**:
- Database transactions provide ACID guarantees (Atomicity)
- If transaction fails: All changes automatically rolled back by PostgreSQL
- If application crashes mid-transaction: Database rolls back on restart

**Constraint Violations**:
- Foreign key violations: Automatic rollback
- Unique constraint violations: Automatic rollback
- Check constraint violations: Automatic rollback

**Logging**:
- Log all transaction rollbacks with reason
- Log fields: timestamp, operation, user_id, error_message
- Track rollback frequency (high rate = bug or data issue)

**Phase 1 MVP**:
- Use database transactions for all multi-step operations
- SQLAlchemy handles rollback automatically on exception
- Log transaction failures for debugging

---

## 10. TDD & Testing Requirements

### CHK117: Test Data Seeding Requirements

**Requirement ID**: FR-123

**Description**: Development and testing environments MUST have realistic test data for efficient development and QA.

**Test Data Scenarios**:

1. **User Accounts**:
   - `test_beginner@example.com` (complete beginner, no projects)
   - `test_active@example.com` (active user, 3 projects, 10 tasks)
   - `test_advanced@example.com` (power user, 10 projects, 50 tasks)
   - All passwords: `testpass123` (development only)

2. **Projects**:
   - "My First Todo App" (1 task, completed)
   - "Calculator Program" (3 tasks, in progress)
   - "Web Scraper" (5 tasks, not started)
   - "Data Analysis Script" (2 tasks, completed)

3. **Tasks**:
   - Task with simple Python function (10 lines)
   - Task with class definition (50 lines)
   - Task with multiple files (folder upload)
   - Task with complex algorithm (100+ lines)
   - Task in different languages (JavaScript, Java, C++)

4. **Learning Documents**:
   - Complete 7-chapter documents for all tasks
   - Documents with varying content length (short, medium, long)
   - Documents with different code complexity levels

5. **Progress States**:
   - Task not started (0% progress)
   - Task partially complete (50% document read, 2/5 practice done)
   - Task fully complete (100%, all practice done, questions asked)

6. **Q&A History**:
   - Tasks with no questions asked
   - Tasks with 1-2 questions (light usage)
   - Tasks with 10+ questions (heavy usage, complex topic)

**Seeding Implementation**:

1. **Seed Script** (`scripts/seed_test_data.py`):
   ```python
   async def seed_database():
       # Create test users
       users = await create_test_users()

       # Create projects for each user
       for user in users:
           projects = await create_test_projects(user)

           # Create tasks for each project
           for project in projects:
               tasks = await create_test_tasks(project)

               # Generate documents and progress
               for task in tasks:
                   await generate_test_document(task)
                   await create_test_progress(task)
   ```

2. **Sample Code Files**:
   - Store in `tests/fixtures/code_samples/`
   - Filenames: `simple_function.py`, `class_example.py`, `algorithm.py`
   - Cover common beginner code patterns

3. **Idempotent Seeding**:
   - Check if test data exists before seeding (avoid duplicates)
   - Delete all test data before re-seeding (clean slate)
   - Command: `python scripts/seed_test_data.py --reset`

**Seed Data Characteristics**:
- **Realistic**: Use actual code examples (not "foo/bar" placeholders)
- **Diverse**: Cover different languages, complexities, file structures
- **Consistent**: Same seed data across all dev environments
- **Versioned**: Seed script in Git, updated as schema changes

**Usage**:
- **Development**: Run seed script on fresh database setup
- **Testing**: Run before E2E test suite (isolated test database)
- **Demo**: Run before product demos (consistent demo data)
- **CI/CD**: Run in pipeline to test migrations with realistic data

**Security**:
- **Never seed in production** (check environment variable)
- Test emails: `*@example.com` (invalid domain)
- Weak passwords acceptable (development only)

**Phase 1 MVP**:
- Create seed script with 3 users, 5 projects, 15 tasks
- Include sample code files for common scenarios
- Idempotent seeding (can re-run without errors)
- Documentation: README with seed instructions

---

### CHK118: AI-Generated Content Testing Requirements

**Requirement ID**: FR-124

**Description**: AI-generated content (documents, practice problems, Q&A) MUST be tested to ensure quality, consistency, and correctness.

**Testing Challenges**:
- Non-deterministic output (same input ≠ same output)
- Difficult to assert exact content (AI creativity)
- Slow tests (AI API calls take seconds/minutes)
- Expensive tests (API costs)

**Testing Strategy**:

1. **Unit Tests** (Fast, Cheap, Deterministic):
   - **What to Test**: Validation logic, not AI generation
   - **Examples**:
     - Test that 7-chapter structure validator works
     - Test that practice problem parser extracts fields correctly
     - Test that Q&A response formatter adds proper markdown
   - **Mocking**: Mock AI API responses with realistic fixtures
   ```python
   def test_document_validation():
       # Mock AI response
       ai_response = load_fixture("valid_document.json")

       # Test validation
       result = validate_document(ai_response)
       assert result.is_valid == True
       assert len(result.chapters) == 7
   ```

2. **Integration Tests** (Slow, Expensive, Real AI):
   - **What to Test**: End-to-end AI generation with real API
   - **Frequency**: Run sparingly (nightly build, pre-release)
   - **Examples**:
     - Generate document for simple Python function, assert 7 chapters created
     - Ask Q&A question, assert response is >50 characters
     - Generate practice problems, assert 5 problems with correct difficulty levels
   - **Assertions** (Flexible):
     - Assert structure (7 chapters exist)
     - Assert content length (each chapter >100 chars)
     - Assert required fields present (title, content, key_points)
     - Do NOT assert exact content (too brittle)

3. **Snapshot Testing** (Detect Regressions):
   - **What to Test**: Consistency over time
   - **Approach**:
     - Generate document for fixed code sample
     - Save output as snapshot (first run)
     - Compare future outputs to snapshot (detect drift)
     - Manual review if snapshot differs (is change acceptable?)
   ```python
   def test_document_generation_snapshot():
       code = load_fixture("simple_function.py")
       document = generate_document(code)  # Real AI call

       # Compare to saved snapshot
       assert_matches_snapshot(document)  # Fail if different
   ```

4. **Manual QA Testing** (Human Review):
   - **What to Test**: Educational quality, beginner-friendliness
   - **Frequency**: Every major release
   - **Process**:
     - Generate documents for 5 sample tasks
     - Have non-developer tester read documents
     - Collect feedback: "Did you understand?", "Any confusing parts?"
     - Iterate on prompts based on feedback

5. **Monitoring in Production** (Real User Data):
   - **What to Monitor**: Success rates, quality metrics
   - **Examples**:
     - Track validation failure rate (should be <5%)
     - Track fallback usage rate (should be <10%)
     - Track user question count (low = good explanation)
   - **Action**: If metrics degrade, investigate and adjust prompts

**Test Fixtures** (Realistic AI Responses):
- Store in `tests/fixtures/ai_responses/`
- Files:
  - `valid_document.json` (perfect 7-chapter document)
  - `invalid_document.json` (missing chapters)
  - `malformed_document.json` (invalid JSON)
  - `empty_response.json` (AI returned nothing)
  - `valid_qa_response.json` (good Q&A answer)
  - `valid_practice_problems.json` (5 practice problems)

**Prompt Versioning**:
- Store AI prompts in version control (`prompts/document_generation.txt`)
- Tag prompts with version number (v1, v2, etc.)
- When prompt changes, re-run snapshot tests (detect regression)
- Document prompt changes in changelog

**Phase 1 MVP**:
- Unit tests for validation logic (mocked AI responses)
- 5-10 integration tests with real AI (critical paths only)
- Manual QA testing before releases
- No snapshot testing (Phase 2)
- No automated monitoring (manual log review)

---

## 11. Ambiguities & Final Clarifications

### CHK132: Assumption Invalidation Handling

**Requirement ID**: FR-125

**Description**: If assumptions documented in spec.md prove invalid during implementation, define process for handling changes.

**Process for Assumption Changes**:

1. **Detect Invalid Assumption**:
   - Developer encounters issue during implementation
   - Example: "Assumption: Users have programming knowledge" → Invalid (users are complete beginners)
   - Example: "Assumption: AI generation takes <3 minutes" → Invalid (taking 5+ minutes)

2. **Document Impact**:
   - Identify affected requirements and features
   - Estimate effort to address (hours/days)
   - Assess risk (high/medium/low)

3. **Decision Process**:
   - **Low Impact**: Developer makes decision, documents in commit message
   - **Medium Impact**: Discuss with team, update spec.md, proceed
   - **High Impact**: Halt implementation, escalate to product owner, reassess scope

4. **Update Documentation**:
   - Update spec.md: Mark assumption as invalid, add new assumption
   - Update plan.md: Reflect changes in technical approach
   - Update tasks.md: Add/remove/modify tasks as needed
   - Document in research.md: Why assumption was invalid, what changed

5. **Communicate Changes**:
   - Add note to task completion report: "Assumption X was found invalid, changed to Y"
   - Update design review checklist if new requirements added
   - Notify stakeholders if timeline/scope impacted

**Example Scenario**:

**Invalid Assumption**: "AI document generation completes in <3 minutes"

**Discovery**: During testing, average generation time is 6 minutes for 500 LOC

**Impact**: High (core performance requirement)

**Decision**:
1. Investigate why slow (prompt too complex? API rate limiting?)
2. Optimize if possible (simplify prompt, reduce API calls)
3. If optimization insufficient: Update requirement to 5 minutes (more realistic)
4. Update spec.md: FR-083 from "3 minutes" to "5 minutes"
5. Update UI: Loading message "This may take up to 5 minutes"

**Documentation Update**:
```markdown
### Assumption Change Log

**Date**: 2025-11-20
**Changed Assumption**: AI document generation time
**Original**: "< 3 minutes for 500 LOC" (spec.md §Assumptions)
**Updated**: "< 5 minutes for 500 LOC"
**Reason**: Real-world testing showed 6-minute average; optimized to 5 minutes
**Impact**: Updated FR-083, FR-084 (loading messages), UI text
```

**Phase 1 MVP**:
- Document all assumption changes in spec.md changelog section
- Update affected requirements immediately
- No formal change approval process (agile, small team)

---

### CHK141: "Related Concepts" Quantification in Q&A

**Requirement ID**: FR-126

**Description**: When Q&A responses include "related concepts" (per FR-064), define how many concepts and selection criteria.

**Clarification**:

**Related Concepts in Q&A Responses**:
- **Count**: 2-3 related concepts maximum (avoid overwhelming beginners)
- **Selection Criteria**:
  1. **Directly Related**: Concepts that naturally follow or build upon the question topic
     - Example: Question about "variables" → Related: "data types", "assignment operators"
  2. **Same Chapter**: Concepts from the same chapter in the learning document
     - Example: Question about Chapter 2 (Prerequisites) → Related concepts from Chapter 2
  3. **Prerequisite Concepts**: Concepts needed to understand the questioned concept
     - Example: Question about "loops" → Related: "conditionals" (often used together)
  4. **Commonly Confused**: Concepts beginners often confuse with the questioned concept
     - Example: Question about "class" → Related: "function" (clarify difference)

**Format in Q&A Response**:
```markdown
## 답변

[Main answer explaining the concept]

## 관련 개념

1. **데이터 타입 (Data Types)**: 변수에 저장할 수 있는 값의 종류 (숫자, 텍스트 등)
2. **할당 연산자 (Assignment Operator)**: 변수에 값을 저장할 때 사용하는 = 기호
```

**AI Prompt Instruction**:
```
When answering, include a "Related Concepts" section with 2-3 concepts that:
- Are directly related to the question topic
- Help the user build a mental model
- Are from the same learning document chapter
- Avoid overwhelming the beginner (max 3 concepts)
```

**Implementation**:
- Add related concepts section to Q&A response template
- AI generates related concepts based on document context
- Limit to 3 concepts (hard limit in validation)

**Phase 1 MVP**:
- Include 2-3 related concepts in Q&A responses
- AI selects concepts automatically (no manual curation)
- Simple format (bulleted list with brief explanation)

---

### CHK142: "Balanced Visual Weight" Clarification

**Requirement ID**: N/A (Not in Spec)

**Clarification**: The term "balanced visual weight" does NOT appear in the spec, plan, or any design documents.

**Status**: This checklist item is invalid and should be REMOVED.

**Rationale**:
- Searched spec.md, plan.md, data-model.md, research.md: No mention of "balanced visual weight"
- No UI/UX requirements use this term
- Likely a generic design checklist item not applicable to this project

**Action**: Mark CHK142 as N/A (Not Applicable) in design review checklist.

---

## Summary

This addendum addresses all 38 incomplete requirements identified in the design review checklist (CHK005-CHK142). All requirements are now fully specified and implementation-ready.

**Requirements Added**: 38 (FR-095 through FR-126, plus 3 NFRs)

**Scope Clarifications**:
- **Included in Phase 1 MVP**: 23 requirements (AI validation, error handling, UX, testing, etc.)
- **Explicitly Excluded from Phase 1 MVP**: 12 requirements (password reset, pagination, trends, export, etc.)
- **Production/Operational**: 3 requirements (backup, monitoring, browser compatibility)

**Next Steps**:
1. Update design-review.md checklist: Mark all items as complete
2. Verify checklist completion: Run through all 145 items
3. Proceed with implementation: Execute `/speckit.implement`

**Document Status**: ✅ COMPLETE - All design review gaps addressed
