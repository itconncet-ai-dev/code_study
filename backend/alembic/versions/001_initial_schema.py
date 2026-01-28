"""Initial database schema with all entity tables.

This migration creates the complete database schema for the AI Code Learning Platform.
All entities support user isolation, soft deletion (30-day trash retention), and timestamps.

Revision ID: 001
Revises:
Create Date: 2025-01-19

Entity Order (by dependency):
1. users - no dependencies
2. refresh_tokens - depends on users
3. projects - depends on users
4. tasks - depends on projects
5. uploaded_code - depends on tasks
6. code_files - depends on uploaded_code
7. learning_documents - depends on tasks
8. practice_problems - depends on tasks
9. questions - depends on tasks, users
10. progress - depends on tasks, users
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables and indexes for the AI Code Learning Platform."""

    # =========================================================================
    # 1. users table
    # =========================================================================
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("skill_level", sa.String(50), server_default="Complete Beginner"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            r"email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'",
            name="valid_email"
        ),
    )
    op.create_index("idx_users_email", "users", ["email"])

    # =========================================================================
    # 2. refresh_tokens table
    # =========================================================================
    op.create_table(
        "refresh_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked", sa.Boolean, server_default="false", nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("idx_refresh_tokens_hash", "refresh_tokens", ["token_hash"])
    op.create_index("idx_refresh_tokens_expires", "refresh_tokens", ["expires_at"])

    # =========================================================================
    # 3. projects table
    # =========================================================================
    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        # Soft delete fields
        sa.Column("deletion_status", sa.String(20), server_default="active", nullable=False),
        sa.Column("trashed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_deletion_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("char_length(title) >= 1", name="title_min_length"),
        sa.CheckConstraint("deletion_status IN ('active', 'trashed')", name="valid_deletion_status"),
    )
    op.create_index("idx_projects_user_id", "projects", ["user_id"])
    op.create_index("idx_projects_deletion_status", "projects", ["deletion_status"])
    # Partial index for active projects per user
    op.execute(
        "CREATE INDEX idx_projects_user_active ON projects(user_id, deletion_status) "
        "WHERE deletion_status = 'active'"
    )

    # =========================================================================
    # 4. tasks table
    # =========================================================================
    op.create_table(
        "tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("task_number", sa.Integer, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("upload_method", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        # Soft delete fields
        sa.Column("deletion_status", sa.String(20), server_default="active", nullable=False),
        sa.Column("trashed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_deletion_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("char_length(title) >= 5", name="task_title_min_length"),
        sa.CheckConstraint("description IS NULL OR char_length(description) <= 500", name="description_max_length"),
        sa.CheckConstraint("upload_method IS NULL OR upload_method IN ('file', 'folder', 'paste')", name="valid_upload_method"),
        sa.CheckConstraint("deletion_status IN ('active', 'trashed')", name="task_valid_deletion_status"),
        sa.UniqueConstraint("project_id", "task_number", name="unique_task_number_per_project"),
    )
    op.create_index("idx_tasks_project_id", "tasks", ["project_id"])
    op.create_index("idx_tasks_deletion_status", "tasks", ["deletion_status"])
    op.create_index("idx_tasks_number_order", "tasks", ["project_id", "task_number"])
    # Partial index for active tasks per project
    op.execute(
        "CREATE INDEX idx_tasks_project_active ON tasks(project_id, deletion_status) "
        "WHERE deletion_status = 'active'"
    )

    # =========================================================================
    # 5. uploaded_code table
    # =========================================================================
    op.create_table(
        "uploaded_code",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("detected_language", sa.String(50), nullable=True),
        sa.Column("complexity_level", sa.String(20), nullable=True),
        sa.Column("total_lines", sa.Integer, nullable=True),
        sa.Column("total_files", sa.Integer, nullable=True),
        sa.Column("upload_size_bytes", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("complexity_level IS NULL OR complexity_level IN ('beginner', 'intermediate', 'advanced')", name="valid_complexity_level"),
        sa.CheckConstraint("upload_size_bytes IS NULL OR upload_size_bytes <= 10485760", name="valid_upload_size"),
    )
    op.create_index("idx_uploaded_code_task_id", "uploaded_code", ["task_id"])

    # =========================================================================
    # 6. code_files table
    # =========================================================================
    op.create_table(
        "code_files",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("uploaded_code_id", UUID(as_uuid=True), sa.ForeignKey("uploaded_code.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.Text, nullable=True),
        sa.Column("file_extension", sa.String(20), nullable=True),
        sa.Column("file_size_bytes", sa.Integer, nullable=True),
        sa.Column("storage_path", sa.Text, nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "file_extension IS NULL OR file_extension IN ('.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.java', '.cpp', '.c', '.txt', '.md')",
            name="supported_extension"
        ),
    )
    op.create_index("idx_code_files_uploaded_code_id", "code_files", ["uploaded_code_id"])

    # =========================================================================
    # 7. learning_documents table
    # =========================================================================
    op.create_table(
        "learning_documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("content", JSONB, nullable=False, server_default="{}"),
        sa.Column("generation_status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("generation_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("generation_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("generation_error", sa.Text, nullable=True),
        sa.Column("celery_task_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "generation_status IN ('pending', 'in_progress', 'completed', 'failed')",
            name="valid_generation_status"
        ),
    )
    op.create_index("idx_learning_documents_task_id", "learning_documents", ["task_id"])
    op.create_index("idx_learning_documents_status", "learning_documents", ["generation_status"])
    op.create_index("idx_learning_documents_celery_task", "learning_documents", ["celery_task_id"])

    # =========================================================================
    # 8. practice_problems table
    # =========================================================================
    op.create_table(
        "practice_problems",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("problem_number", sa.Integer, nullable=False),
        sa.Column("problem_type", sa.String(20), nullable=False),
        sa.Column("problem_statement", sa.Text, nullable=False),
        sa.Column("learning_objective", sa.Text, nullable=True),
        sa.Column("hints", JSONB, nullable=True),
        sa.Column("model_solution", sa.Text, nullable=True),
        sa.Column("expected_output", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("problem_number BETWEEN 1 AND 5", name="valid_problem_number"),
        sa.CheckConstraint(
            "problem_type IN ('follow_along', 'fill_blanks', 'modify', 'debug', 'create')",
            name="valid_problem_type"
        ),
        sa.UniqueConstraint("task_id", "problem_number", name="unique_problem_per_task"),
    )
    op.create_index("idx_practice_problems_task_id", "practice_problems", ["task_id"])
    op.create_index("idx_practice_problems_number", "practice_problems", ["task_id", "problem_number"])

    # =========================================================================
    # 9. questions table
    # =========================================================================
    op.create_table(
        "questions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_text", sa.Text, nullable=False),
        sa.Column("selected_code_context", sa.Text, nullable=True),
        sa.Column("answer_text", sa.Text, nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("helpful_feedback", sa.Boolean, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("char_length(question_text) >= 3 AND char_length(question_text) <= 500", name="question_length"),
        sa.CheckConstraint("selected_code_context IS NULL OR char_length(selected_code_context) <= 50000", name="code_context_length"),
    )
    op.create_index("idx_questions_task_id", "questions", ["task_id"])
    op.create_index("idx_questions_user_id", "questions", ["user_id"])
    op.create_index("idx_questions_task_user", "questions", ["task_id", "user_id"])

    # =========================================================================
    # 10. progress table
    # =========================================================================
    op.create_table(
        "progress",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        # Document reading progress
        sa.Column("chapters_completed", JSONB, server_default="[]", nullable=False),
        sa.Column("document_read_percentage", sa.Integer, server_default="0", nullable=False),
        # Practice problems progress
        sa.Column("problems_completed", JSONB, server_default="[]", nullable=False),
        sa.Column("practice_completion_count", sa.Integer, server_default="0", nullable=False),
        # Q&A activity
        sa.Column("questions_asked_count", sa.Integer, server_default="0", nullable=False),
        # Task completion
        sa.Column("task_completed", sa.Boolean, server_default="false", nullable=False),
        sa.Column("task_completion_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("document_read_percentage BETWEEN 0 AND 100", name="valid_read_percentage"),
        sa.CheckConstraint("practice_completion_count BETWEEN 0 AND 5", name="valid_practice_count"),
        sa.UniqueConstraint("task_id", "user_id", name="unique_progress_per_task_user"),
    )
    op.create_index("idx_progress_task_id", "progress", ["task_id"])
    op.create_index("idx_progress_user_id", "progress", ["user_id"])
    op.create_index("idx_progress_task_user", "progress", ["task_id", "user_id"])


def downgrade() -> None:
    """Drop all tables in reverse dependency order."""

    # Drop indexes first (partial indexes created with raw SQL)
    op.execute("DROP INDEX IF EXISTS idx_tasks_project_active")
    op.execute("DROP INDEX IF EXISTS idx_projects_user_active")

    # Drop tables in reverse dependency order
    op.drop_table("progress")
    op.drop_table("questions")
    op.drop_table("practice_problems")
    op.drop_table("learning_documents")
    op.drop_table("code_files")
    op.drop_table("uploaded_code")
    op.drop_table("tasks")
    op.drop_table("projects")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
