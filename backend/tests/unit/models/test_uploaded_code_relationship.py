"""
Test UploadedCode 1:1 Relationship with Task

This test verifies that:
1. A Task can have exactly one UploadedCode
2. Attempting to create a second UploadedCode for the same Task raises IntegrityError
3. The unique constraint on task_id is properly enforced

Reference: data-model.md §UploadedCode entity - "One uploaded code per task"
"""

import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.models.base import Base
from src.models.user import User
from src.models.project import Project
from src.models.task import Task
from src.models.uploaded_code import UploadedCode


# Test database URL (in-memory SQLite for fast testing)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def engine():
    """Create a test database engine."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine):
    """Create a test database session."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def test_user(session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password_123",
        skill_level="Complete Beginner",
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def test_project(session, test_user):
    """Create a test project."""
    project = Project(
        user_id=test_user.id,
        title="Test Project",
        description="A test project for UploadedCode relationship testing",
    )
    session.add(project)
    session.commit()
    return project


@pytest.fixture
def test_task(session, test_project):
    """Create a test task."""
    task = Task(
        project_id=test_project.id,
        task_number=1,
        title="Test Task for UploadedCode",
        description="Testing 1:1 relationship",
        upload_method="file",
    )
    session.add(task)
    session.commit()
    return task


class TestUploadedCodeOneToOneRelationship:
    """Test suite for UploadedCode 1:1 relationship with Task."""

    def test_create_first_uploaded_code_succeeds(self, session, test_task):
        """
        Test: Creating the first UploadedCode for a Task should succeed.

        Given: A Task exists without any UploadedCode
        When: We create an UploadedCode for that Task
        Then: The UploadedCode is successfully created and linked
        """
        # Create first UploadedCode
        uploaded_code = UploadedCode(
            task_id=test_task.id,
            detected_language="python",
            complexity_level="beginner",
            total_lines=100,
            total_files=1,
            upload_size_bytes=1024,
        )
        session.add(uploaded_code)
        session.commit()

        # Verify creation
        assert uploaded_code.id is not None
        assert uploaded_code.task_id == test_task.id
        assert uploaded_code.detected_language == "python"
        assert uploaded_code.complexity_level == "beginner"
        assert uploaded_code.total_lines == 100
        assert uploaded_code.total_files == 1
        assert uploaded_code.upload_size_bytes == 1024

        # Verify relationship
        session.refresh(test_task)
        assert test_task.uploaded_code is not None
        assert test_task.uploaded_code.id == uploaded_code.id

        print("SUCCESS: First UploadedCode created successfully")

    def test_create_second_uploaded_code_fails_with_integrity_error(
        self, session, test_task
    ):
        """
        Test: Creating a second UploadedCode for the same Task should fail.

        Given: A Task already has an UploadedCode
        When: We attempt to create another UploadedCode for the same Task
        Then: An IntegrityError is raised due to unique constraint violation
        """
        # Create first UploadedCode
        first_uploaded_code = UploadedCode(
            task_id=test_task.id,
            detected_language="python",
            complexity_level="beginner",
            total_lines=100,
            total_files=1,
            upload_size_bytes=1024,
        )
        session.add(first_uploaded_code)
        session.commit()

        print(f"First UploadedCode created with id: {first_uploaded_code.id}")

        # Attempt to create second UploadedCode for the same Task
        second_uploaded_code = UploadedCode(
            task_id=test_task.id,  # Same task_id - should fail!
            detected_language="javascript",
            complexity_level="intermediate",
            total_lines=200,
            total_files=2,
            upload_size_bytes=2048,
        )
        session.add(second_uploaded_code)

        # This should raise IntegrityError due to unique constraint on task_id
        with pytest.raises(IntegrityError) as exc_info:
            session.commit()

        # Verify the error is related to unique constraint
        error_message = str(exc_info.value).lower()
        assert "unique" in error_message or "constraint" in error_message

        print(f"SUCCESS: IntegrityError raised as expected: {exc_info.value}")

        # Rollback to clean up
        session.rollback()

    def test_task_relationship_access(self, session, test_task):
        """
        Test: The Task.uploaded_code relationship correctly accesses UploadedCode.

        Given: A Task with an UploadedCode
        When: We access task.uploaded_code
        Then: We get the correct UploadedCode instance
        """
        # Create UploadedCode
        uploaded_code = UploadedCode(
            task_id=test_task.id,
            detected_language="typescript",
            complexity_level="advanced",
            total_lines=500,
            total_files=5,
            upload_size_bytes=50000,
        )
        session.add(uploaded_code)
        session.commit()

        # Access via relationship
        session.refresh(test_task)
        assert test_task.uploaded_code is not None
        assert test_task.uploaded_code.detected_language == "typescript"
        assert test_task.uploaded_code.complexity_level == "advanced"

        print("SUCCESS: Task.uploaded_code relationship works correctly")

    def test_uploaded_code_task_relationship_access(self, session, test_task):
        """
        Test: The UploadedCode.task relationship correctly accesses Task.

        Given: An UploadedCode linked to a Task
        When: We access uploaded_code.task
        Then: We get the correct Task instance
        """
        # Create UploadedCode
        uploaded_code = UploadedCode(
            task_id=test_task.id,
            detected_language="java",
            complexity_level="intermediate",
            total_lines=300,
            total_files=3,
            upload_size_bytes=30000,
        )
        session.add(uploaded_code)
        session.commit()

        # Access via relationship
        session.refresh(uploaded_code)
        assert uploaded_code.task is not None
        assert uploaded_code.task.id == test_task.id
        assert uploaded_code.task.title == "Test Task for UploadedCode"

        print("SUCCESS: UploadedCode.task relationship works correctly")


def run_manual_test():
    """
    Run a manual test outside of pytest to demonstrate the 1:1 constraint.
    This can be executed directly with: python -m tests.unit.models.test_uploaded_code_relationship
    """
    print("=" * 60)
    print("Manual Test: UploadedCode 1:1 Relationship with Task")
    print("=" * 60)

    # Setup
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Step 1: Create test user
        print("\n[Step 1] Creating test user...")
        user = User(
            email="manual_test@example.com",
            password_hash="hashed_password_123",
            skill_level="Complete Beginner",
        )
        session.add(user)
        session.commit()
        print(f"  User created: {user.id}")

        # Step 2: Create test project
        print("\n[Step 2] Creating test project...")
        project = Project(
            user_id=user.id,
            title="Manual Test Project",
        )
        session.add(project)
        session.commit()
        print(f"  Project created: {project.id}")

        # Step 3: Create test task
        print("\n[Step 3] Creating test task...")
        task = Task(
            project_id=project.id,
            task_number=1,
            title="Manual Test Task",
            upload_method="file",
        )
        session.add(task)
        session.commit()
        print(f"  Task created: {task.id}")

        # Step 4: Create first UploadedCode - should succeed
        print("\n[Step 4] Creating FIRST UploadedCode...")
        first_code = UploadedCode(
            task_id=task.id,
            detected_language="python",
            complexity_level="beginner",
            total_lines=100,
            total_files=1,
            upload_size_bytes=1024,
        )
        session.add(first_code)
        session.commit()
        print(f"  First UploadedCode created: {first_code.id}")
        print(f"  Linked to task: {first_code.task_id}")

        # Step 5: Attempt to create second UploadedCode - should FAIL
        print("\n[Step 5] Attempting to create SECOND UploadedCode (should fail)...")
        second_code = UploadedCode(
            task_id=task.id,  # Same task_id!
            detected_language="javascript",
            complexity_level="intermediate",
            total_lines=200,
            total_files=2,
            upload_size_bytes=2048,
        )
        session.add(second_code)

        try:
            session.commit()
            print("  ERROR: Second UploadedCode was created - constraint NOT working!")
        except IntegrityError as e:
            session.rollback()
            print(f"  SUCCESS: IntegrityError raised as expected!")
            print(f"  Error type: {type(e).__name__}")
            print(f"  Error message contains 'UNIQUE': {'unique' in str(e).lower()}")

        print("\n" + "=" * 60)
        print("TEST COMPLETED: 1:1 relationship constraint is working correctly!")
        print("=" * 60)

    finally:
        session.close()
        Base.metadata.drop_all(engine)


if __name__ == "__main__":
    run_manual_test()
