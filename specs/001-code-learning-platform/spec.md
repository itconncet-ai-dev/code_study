# Feature Specification: AI Code Learning Platform - Phase 1 MVP

**Feature Branch**: `001-code-learning-platform`
**Created**: 2025-11-15
**Status**: Draft
**Input**: User description: "AI Code Learning Platform - Phase 1 MVP"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload Code and Get Textbook Explanation (Priority: P1)

Sarah asked AI to create a calculator function. The AI gave her code, but she doesn't understand what "def", "return", or parameters mean. She uploads the code file to the platform, waits for analysis to complete (under 3 minutes), and receives a comprehensive 7-chapter textbook-style learning document that explains every concept from scratch using real-life analogies.

**Why this priority**: This is the core value proposition - turning incomprehensible AI-generated code into understandable educational content. Without this, the platform has no purpose.

**Independent Test**: Can be fully tested by uploading a simple code file, waiting for document generation, and verifying that a non-developer can understand the explanation without prior programming knowledge.

**Acceptance Scenarios**:

1. **Given** a user has uploaded a Python function with 50 lines of code, **When** the system analyzes the code, **Then** a 7-chapter learning document is generated within 3 minutes with all technical terms explained using everyday language
2. **Given** a complete beginner reads the generated document, **When** they finish all 7 chapters, **Then** they can explain what the code does in their own words
3. **Given** a user uploads code with functions and variables, **When** the Prerequisites chapter is generated, **Then** each concept includes a simple explanation, real-life analogy, code example, and common use cases
4. **Given** a user views the learning document, **When** they scroll through the code panel, **Then** the explanation panel automatically scrolls to show the relevant explanation for the visible code

---

### User Story 2 - Practice with Generated Exercises (Priority: P2)

Maria reads the code explanation and thinks she understands. She clicks on the Practice tab and sees 5 progressively difficult practice problems. She starts with "Follow Along" (typing code exactly), then moves to "Fill in the Blanks", "Modify Code", "Debug", and finally "Create New". When stuck, she can reveal hints progressively, and if completely blocked, she can view the model solution to learn from it.

**Why this priority**: Reading alone doesn't ensure comprehension. Practice problems allow users to apply what they learned and identify gaps in understanding before moving forward.

**Independent Test**: Can be tested by completing the learning document for a task, then accessing the practice problems, working through them in order, using hints when stuck, and marking completion when understood.

**Acceptance Scenarios**:

1. **Given** a user has completed reading a task's learning document, **When** they click "Practice" tab, **Then** 5 practice problems are displayed with difficulty labels (Follow Along, Fill Blanks, Modify, Debug, Create)
2. **Given** a user is stuck on a practice problem, **When** they click "Show Hints", **Then** hints are revealed progressively (first hint, second hint, etc.) without immediately showing the full solution
3. **Given** a user cannot solve a problem even with hints, **When** they click "Show Solution", **Then** the complete model solution is displayed with explanation of the approach
4. **Given** a user completes all 5 practice problems, **When** they mark the last one as understood, **Then** the system displays "Practice Complete" badge and updates progress to 5/5

---

### User Story 3 - Ask Questions While Learning (Priority: P3)

While reading the learning document, Alex encounters the term "variable" that still confuses him despite the explanation. He selects the confusing text, clicks "Ask About This", types "what does this mean in simpler words?", and receives an immediate beginner-friendly answer with analogies and examples. The conversation history remains visible so he can refer back to previous questions.

**Why this priority**: Static explanations can't anticipate every confusion point. A contextual Q&A system provides personalized clarification exactly when needed, preventing frustration and abandonment.

**Independent Test**: Can be tested by selecting code or text in any learning document, asking a question about it, receiving a beginner-optimized response within 10 seconds, asking follow-up questions, and verifying conversation history persists.

**Acceptance Scenarios**:

1. **Given** a user is reading a learning document, **When** they select confusing code and click "Ask About This", **Then** the question panel opens with the selected code already included as context
2. **Given** a user types a question and presses Enter, **When** the system generates a response, **Then** the answer includes simple explanation, real-life analogy, code example, and related concepts within 10 seconds
3. **Given** a user has asked 3 questions during a session, **When** they scroll through the question panel, **Then** all previous questions and answers remain visible for reference
4. **Given** a user asks a general concept question without selecting code, **When** the system responds, **Then** the answer is contextualized to the current task and document they're viewing

---

### User Story 4 - Manage Multiple Tasks in a Project (Priority: P4)

John is building a todo app. Instead of trying to understand the entire codebase at once, he creates a project called "My Todo App" and adds Task 1 for "Add Todo Function". After completing that, he adds Task 2 for "Display List", then Task 3 for "Mark Complete". Each task builds on previous knowledge. The project dashboard shows him he's completed 2/3 tasks (67% progress), and he can see which concepts he's learned across all tasks.

**Why this priority**: Learning is more manageable when broken into small, sequential tasks. This organizational structure prevents overwhelm and provides clear progress tracking to maintain motivation.

**Independent Test**: Can be tested by creating a project, adding multiple tasks in sequence, completing them one by one, and verifying that progress tracking accurately reflects completion status across the project.

**Acceptance Scenarios**:

1. **Given** a user creates a new project, **When** they add 3 tasks over time, **Then** tasks are automatically numbered (Task 1, Task 2, Task 3) and displayed in sequential order
2. **Given** a user has completed 2 out of 5 tasks in a project, **When** they view the project dashboard, **Then** the progress bar shows 40% and displays "2/5 tasks completed"
3. **Given** a user is viewing Task 3, **When** the system detects it builds on concepts from Task 2, **Then** a notification displays "This builds on Task 2 concepts" with a link to review Task 2
4. **Given** a user has multiple projects, **When** they view the project list, **Then** each project shows title, description, task completion count, progress percentage, and last activity date

---

### User Story 5 - Track Learning Progress (Priority: P5)

Emma is working through her project with 5 tasks. She can see that Task 1 is completed ✅ (document read + 5/5 practice done + 4 questions asked), Task 2 is in progress ⏳ (document 60% read + 2/5 practice done), and Tasks 3-5 are not started ⬜. This visual progress tracking helps her see exactly where she is, what she's accomplished, and what's next.

**Why this priority**: Progress visibility maintains motivation and helps users understand their learning journey. Without tracking, users lose sense of accomplishment and direction.

**Independent Test**: Can be tested by working through multiple tasks, partially completing some and fully completing others, then verifying that all progress indicators accurately reflect completion states and persist across sessions.

**Acceptance Scenarios**:

1. **Given** a user has read 4 out of 7 chapters in a task document, **When** they view the task card, **Then** it shows "Document: 57% complete" with visual progress bar
2. **Given** a user has completed 3 out of 5 practice problems, **When** they return to the task after logging out and back in, **Then** the progress still shows "Practice: 3/5 completed"
3. **Given** a user marks a task as complete, **When** the task transitions to "completed" status, **Then** the task card displays a ✅ checkmark and the completion date
4. **Given** a user has asked 6 questions across all tasks in a project, **When** they view project statistics, **Then** the project shows "6 questions asked" as an engagement metric

---

## Clarifications

### Session 2025-11-15

- Q: AI 서비스가 다운되거나 응답 시간이 초과될 때 시스템이 어떻게 동작해야 할까요? → A: 대기열 방식 + 자동 재시도 (요청을 대기열에 추가, 예상 대기 시간 표시, 최대 3회 자동 재시도, 완료 시 알림)
- Q: 사용자가 동일한 코드를 여러 번 업로드하거나 코드를 수정해서 다시 업로드하는 경우 시스템이 어떻게 처리해야 할까요? → A: 새 태스크로 생성 (항상 새로운 태스크 번호 부여, 이전 태스크는 보존)
- Q: 사용자가 프로젝트, 태스크, 업로드한 코드, 생성된 학습 문서를 삭제하고 싶을 때 시스템이 어떻게 처리해야 할까요? → A: 소프트 삭제 + 영구 삭제 옵션 (삭제 시 휴지통으로 이동하여 30일 보관, 사용자가 원하면 영구 삭제 가능)

### Edge Cases

- **What happens when a user uploads a binary file instead of source code?** System detects non-text file, rejects the upload, and displays clear error message: "Only source code text files are supported. Please upload .py, .js, .html, or other text-based code files."
- **What happens when code analysis takes longer than expected (>3 minutes)?** System continues processing in background, allows user to navigate away, and sends notification when document is ready. User can return anytime to view completed document.
- **What happens when a user uploads 500+ lines of code?** System displays warning: "Large code file detected. Document generation may take 3-5 minutes for files exceeding 500 LOC. You can navigate away and return when ready." Continues processing.
- **What happens when a user tries to upload 100 files at once?** System rejects upload and displays error: "Maximum 20 files per upload. Please select fewer files or use folder upload."
- **What happens when folder upload includes .git or node_modules directories?** System automatically excludes these folders and displays message: "Excluded common build/system folders: .git, node_modules, __pycache__"
- **What happens when a user pastes code but forgets to select the programming language?** System displays validation error: "Please select the programming language from the dropdown before uploading."
- **What happens when a user marks a task complete without reading all chapters?** System allows it (self-reported progress) but displays confirmation: "Not all chapters have been read. Mark complete anyway?"
- **What happens when 3 document generations are already running and user tries to start a 4th?** System displays: "Maximum 3 concurrent document generations. Please wait for one to complete before starting another."
- **What happens when a user asks a question longer than 500 characters?** System truncates or displays error: "Question too long. Please ask a more specific question (max 500 characters)."
- **What happens when a user tries to ask a question with less than 3 characters?** System displays validation error: "Please enter a complete question (minimum 3 characters)."
- **What happens when the AI service is unavailable during document generation?** System queues the request, displays estimated wait time, automatically retries up to 3 times, and notifies user when complete. User can navigate away and continue other work.
- **What happens when the AI service times out during Q&A?** System displays "Response delayed, retrying..." message, automatically retries up to 3 times, and if all retries fail, shows error: "Unable to generate answer. Please try again later."
- **What happens when a user uploads the same or similar code multiple times?** System treats each upload as a new independent task with sequential task number. Previous tasks and their learning documents are preserved for comparison and reference.
- **What happens when a user deletes a task?** Task moves to "Trash" (soft delete) and is hidden from main view. User can restore within 30 days or permanently delete immediately.
- **What happens when a user deletes a project?** All tasks within the project move to "Trash" together. User can restore entire project or permanently delete it.
- **What happens to tasks in Trash after 30 days?** System automatically permanently deletes tasks and all associated data (code, documents, progress) after 30 days in Trash.

## Requirements *(mandatory)*

### Functional Requirements

**Project & Task Management:**

- **FR-001**: System MUST allow users to create projects with title and optional description
- **FR-002**: System MUST allow users to add tasks to projects with task title, description, and auto-assigned sequential task number (Task 1, Task 2, etc.)
- **FR-003**: System MUST display tasks in sequential order based on task number
- **FR-004**: Task numbers MUST be immutable once assigned
- **FR-005**: Users MUST NOT be able to reorder tasks after creation
- **FR-006**: Each task MUST belong to exactly one project
- **FR-007**: Projects MUST NOT support nesting
- **FR-008**: Task title MUST be minimum 5 characters
- **FR-009**: Task description MUST be maximum 500 characters
- **FR-009A**: Each code upload MUST create a new independent task (no overwriting or versioning within tasks)
- **FR-009B**: Previous tasks and their learning documents MUST be preserved when similar code is uploaded again
- **FR-009C**: Users MUST be able to delete tasks (soft delete to Trash)
- **FR-009D**: Users MUST be able to delete projects (soft delete all tasks to Trash)
- **FR-009E**: Deleted tasks MUST be moved to "Trash" and hidden from main views
- **FR-009F**: Users MUST be able to restore tasks from Trash within 30 days
- **FR-009G**: Users MUST be able to permanently delete tasks immediately from Trash
- **FR-009H**: System MUST automatically permanently delete tasks after 30 days in Trash
- **FR-009I**: Permanent deletion MUST remove all associated data: code, learning documents, practice problems, questions, and progress
- **FR-009J**: System MUST display confirmation dialog before soft delete and permanent delete operations

**Code Upload:**

- **FR-010**: Users MUST be able to upload code using three methods: single/multiple files, folder, or paste code
- **FR-011**: System MUST support file upload via drag-and-drop or file picker
- **FR-012**: System MUST support folder upload that preserves folder structure
- **FR-013**: System MUST support direct code paste with language selection from dropdown
- **FR-014**: Maximum upload size MUST be 10MB total per task
- **FR-015**: System MUST support these file formats: .py, .js, .html, .css, .java, .cpp, .c, .txt, .md
- **FR-016**: System MUST reject binary files with clear error message
- **FR-017**: System MUST automatically exclude .git, node_modules, .DS_Store, __pycache__ from folder uploads
- **FR-018**: System MUST allow 1-20 files per upload
- **FR-019**: System MUST display upload confirmation showing all uploaded files after successful upload

**Code Analysis:**

- **FR-020**: System MUST automatically detect programming language from uploaded code
- **FR-021**: System MUST assess code complexity level (beginner, intermediate, advanced)
- **FR-022**: System MUST identify file relationships and dependencies
- **FR-023**: System MUST extract prerequisite programming concepts needed to understand the code
- **FR-024**: System MUST display analysis progress with estimated time remaining
- **FR-025**: Analysis MUST complete within 3 minutes for typical tasks (up to 500 lines of code)

**Learning Document Generation:**

- **FR-026**: System MUST generate a 7-chapter textbook-style learning document for each task
- **FR-027**: Chapter 1 MUST provide one-sentence summary in plain language without jargon
- **FR-028**: Chapter 2 MUST list prerequisite concepts with simple explanation, real-life analogy, code example, and common use cases
- **FR-029**: Chapter 2 MUST limit concept cards to maximum 5 concepts
- **FR-030**: Chapter 3 MUST provide visual flowchart showing execution flow and file structure breakdown
- **FR-031**: Chapter 4 MUST provide line-by-line code explanation including: what the line does, syntax breakdown, real-life analogy, alternative examples, and important notes
- **FR-032**: Chapter 5 MUST provide step-by-step execution flow simulation showing how data flows through the program
- **FR-033**: Chapter 6 MUST summarize core programming concepts learned with what it is, why it's used, and where it's applied
- **FR-034**: Chapter 7 MUST provide 3-5 common mistakes with wrong code example, right code example, why it matters, and how to fix it
- **FR-035**: All explanations MUST be written for users with zero programming knowledge
- **FR-036**: Every technical term MUST be explained using everyday language
- **FR-037**: Real-life analogies MUST be included for abstract concepts
- **FR-038**: Generated documents MUST be stored (not regenerated on each view)
- **FR-039**: Document generation MUST be deterministic (same code produces same document structure)

**Document Reading Experience:**

- **FR-040**: System MUST display code and explanation side-by-side on desktop
- **FR-041**: System MUST provide synchronized scrolling between code and explanation panels
- **FR-042**: System MUST apply syntax highlighting to code
- **FR-043**: System MUST show line numbers on code panel
- **FR-044**: System MUST highlight current chapter being read in navigation
- **FR-045**: Users MUST be able to jump to any chapter directly (non-linear navigation)
- **FR-046**: Users MUST be able to mark each chapter as complete
- **FR-047**: Code panel MUST highlight relevant lines as user reads corresponding explanations

**Practice Problem Generation:**

- **FR-048**: System MUST generate 5 practice problems per task with increasing difficulty
- **FR-049**: Practice problems MUST include these types in order: Follow Along, Fill in Blanks, Modify Code, Debug, Create New
- **FR-050**: Each practice problem MUST include: clear problem statement, learning objective, progressive hints, model solution (hidden initially), and expected output
- **FR-051**: Practice problems MUST be solvable with concepts covered in the task's learning document
- **FR-052**: Users MUST be able to reveal hints progressively without immediately seeing full solution
- **FR-053**: Users MUST be able to reveal model solution when needed
- **FR-054**: Users MUST be able to mark practice problems as completed (self-reported)
- **FR-055**: System MUST display practice completion progress (X out of 5 completed)
- **FR-056**: Practice problems MUST be text-only (no in-browser code execution in Phase 1)

**Q&A System:**

- **FR-057**: System MUST provide question panel accessible from any screen within a task
- **FR-058**: Users MUST be able to select code/text and ask questions about it with context included
- **FR-059**: Users MUST be able to ask general questions without code selection
- **FR-060**: Question minimum length MUST be 3 characters
- **FR-061**: Question maximum length MUST be 500 characters
- **FR-062**: Selected code snippet maximum length MUST be 50 lines
- **FR-063**: System MUST generate beginner-optimized answers within 10 seconds
- **FR-064**: Answers MUST include: simple explanation, real-life analogy, code example, and related concepts
- **FR-065**: System MUST maintain conversation history visible during session
- **FR-066**: System MUST save questions per task (not globally)
- **FR-067**: Users MUST be able to view previous questions for a task
- **FR-068**: System MUST be context-aware of which document and task user is viewing

**Progress Tracking:**

- **FR-069**: System MUST track document reading progress per chapter
- **FR-070**: System MUST track practice problem completion per problem
- **FR-071**: System MUST track number of questions asked per task
- **FR-072**: System MUST calculate task completion percentage accurately (completed items / total items)
- **FR-073**: Task completion MUST require both document fully read AND user manually marks complete
- **FR-074**: Progress MUST persist across sessions (survive logout/login)
- **FR-075**: System MUST display progress bars, checkmarks, and status badges (✅ completed, ⏳ in progress, ⬜ not started)
- **FR-076**: System MUST NOT impose time limits or deadlines on task completion
- **FR-077**: System MUST track completion dates for tasks
- **FR-078**: System MUST calculate project-level progress as total completed tasks / total tasks

**Data Persistence:**

- **FR-079**: System MUST persist all projects, tasks, uploaded code, generated documents, and progress
- **FR-080**: Users MUST be able to access content after logging out and back in
- **FR-081**: Uploaded code MUST be stored securely
- **FR-082**: Question history MUST be preserved per task

**Performance:**

- **FR-083**: Document generation MUST complete within 3 minutes for tasks up to 500 lines of code
- **FR-084**: Loading states MUST show estimated time remaining
- **FR-085**: Users MUST be able to navigate away during document generation and return later
- **FR-086**: System MUST handle at least 3 concurrent document generations per user
- **FR-087**: Q&A responses MUST be generated within 10 seconds

**AI Service Reliability:**

- **FR-088**: System MUST queue AI generation requests when service is unavailable
- **FR-089**: System MUST display estimated wait time for queued requests
- **FR-090**: System MUST automatically retry failed AI requests up to 3 times with exponential backoff
- **FR-091**: System MUST notify users when queued document generation completes
- **FR-092**: System MUST allow users to navigate away from queued tasks and return later
- **FR-093**: For Q&A requests, system MUST display "Response delayed, retrying..." during retry attempts
- **FR-094**: After 3 failed retry attempts, system MUST display clear error message with option to try again manually

### Key Entities *(include if feature involves data)*

- **Project**: Represents a learning container for related tasks. Attributes: title, description, creation date, last activity date, deletion status (active/trashed), trash date, scheduled permanent deletion date. Contains multiple Tasks.
- **Task**: Represents a single learning unit focused on one feature or code snippet. Attributes: task number (sequential, immutable), title, description, upload method used, creation date, deletion status (active/trashed), trash date, scheduled permanent deletion date. Belongs to one Project. Contains uploaded Code, Learning Document, Practice Problems, and Questions.
- **Code**: The source code uploaded by user for a task. Attributes: file names, file paths, folder structure, detected language, complexity level, total lines. Associated with one Task.
- **Learning Document**: The generated 7-chapter educational content explaining the code. Attributes: 7 chapters with structured content, generation date, version. Associated with one Task.
- **Practice Problem**: Generated exercise for applying learned concepts. Attributes: problem number (1-5), type (Follow Along/Fill/Modify/Debug/Create), problem statement, learning objective, hints, model solution, expected output. Associated with one Task.
- **Question**: User-submitted question during learning. Attributes: question text, selected code context (if any), answer text, timestamp, helpful/not helpful feedback. Associated with one Task.
- **Progress**: Tracks user's learning state. Attributes: chapters completed, practice problems completed, questions asked count, task completion status, completion date. Associated with one Task and one User.
- **User**: Platform user (authentication covered by constitution). Attributes: email, hashed password, skill level (default: Complete Beginner), registration date. Has multiple Projects.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload AI-generated code and receive a comprehensible textbook-quality explanation within 3 minutes
- **SC-002**: Complete beginners can understand at least 80% of generated learning documents without prior programming knowledge (validated through user testing)
- **SC-003**: Users successfully complete at least 3 tasks in sequence for a single project, demonstrating ability to organize learning incrementally
- **SC-004**: After reading a task's learning document, users can explain "what does this code do?" in their own words with 80% accuracy
- **SC-005**: At least 60% of generated practice problems are marked as completed by users, indicating engagement and perceived value
- **SC-006**: Users ask an average of 3-5 questions per task, demonstrating active engagement and curiosity
- **SC-007**: Users can navigate back to previously completed tasks and recall what they learned when asked to summarize
- **SC-008**: Document generation completes within 3 minutes for 90% of typical tasks (up to 500 lines of code)
- **SC-009**: Question responses are generated within 10 seconds for 95% of queries
- **SC-010**: Progress tracking accurately reflects completion status across sessions (100% data persistence after logout/login)
- **SC-011**: Users can successfully upload code using all three methods (file, folder, paste) without errors or confusion
- **SC-012**: Learning documents contain zero technical jargon without immediate explanation in everyday language (validated by non-developer reviewers)

## Assumptions

1. **Authentication**: Users have existing authentication system per constitution (email/password, session management) - not re-specified here
2. **AI Model**: Platform has access to LLM capable of generating educational content and answering questions in beginner-friendly language
3. **Storage**: Adequate storage is available for uploaded code files (10MB per task, multiple tasks per user)
4. **Desktop-First**: Primary user interface is desktop/laptop (mobile responsiveness is Phase 2)
5. **Text-Based Practice**: Phase 1 practice problems are text-only exercises; users test code in their own local environment
6. **Single Language Support**: All educational content and UI text is in Korean for task completion reports (per constitution), but code explanations can be in English
7. **Sequential Learning**: Users are expected to complete tasks in order (Task 1 → Task 2 → Task 3) for optimal learning progression
8. **Self-Reported Progress**: Practice problem completion and task completion rely on user self-reporting (no automated code validation in Phase 1)
9. **Standard Web Performance**: Platform runs in modern web browsers (Chrome, Firefox, Safari, Edge) with standard internet connection
10. **Code Quality**: Uploaded code is assumed to be syntactically valid (platform explains code, not debugs invalid syntax in Phase 1)
