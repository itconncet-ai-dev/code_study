"""
Integration Tests for Project API Endpoints - AI Code Learning Platform

Tests for Tasks T046-T050: Project CRUD API endpoints.

Test Coverage:
- T046: GET /projects - List user projects
- T047: POST /projects - Create new project
- T048: GET /projects/{project_id} - Get project details
- T049: PATCH /projects/{project_id} - Update project
- T050: DELETE /projects/{project_id} - Soft delete project

Testing Strategy (TDD):
1. RED: Write failing tests first
2. GREEN: Implement minimal code to pass tests
3. REFACTOR: Improve code quality

Reference: api-spec.yaml §Project endpoints
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from src.main import app
from src.models.user import User
from src.models.project import Project
from src.services.auth.token_service import TokenService


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
async def client() -> AsyncClient:
    """
    Provide an async HTTP client for API tests.

    Returns:
        AsyncClient configured with the FastAPI app
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    Create and return a test user for authentication.

    Args:
        db_session: Database session fixture

    Returns:
        User: Test user instance
    """
    from src.utils.security import hash_password

    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPass123!"),
        skill_level="Intermediate",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def auth_headers(db_session: AsyncSession, test_user: User) -> dict[str, str]:
    """
    Generate authentication headers with valid access token.

    Args:
        db_session: Database session fixture
        test_user: Test user fixture

    Returns:
        dict: Headers with Authorization Bearer token
    """
    token_service = TokenService(db_session)
    access_token, _ = await token_service.create_token_pair(test_user.id)

    return {
        "Authorization": f"Bearer {access_token}"
    }


@pytest.fixture
async def test_project(db_session: AsyncSession, test_user: User) -> Project:
    """
    Create and return a test project.

    Args:
        db_session: Database session fixture
        test_user: Test user fixture

    Returns:
        Project: Test project instance
    """
    project = Project(
        user_id=test_user.id,
        title="Test Project",
        description="Test project description",
        deletion_status="active",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    return project


@pytest.fixture
async def trashed_project(db_session: AsyncSession, test_user: User) -> Project:
    """
    Create and return a trashed test project.

    Args:
        db_session: Database session fixture
        test_user: Test user fixture

    Returns:
        Project: Trashed test project instance
    """
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    project = Project(
        user_id=test_user.id,
        title="Trashed Project",
        description="This project is trashed",
        deletion_status="trashed",
        trashed_at=now,
        scheduled_deletion_at=now + timedelta(days=30),
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    return project


# =============================================================================
# T046: GET /projects - List User Projects
# =============================================================================


class TestGetProjects:
    """Test suite for GET /projects endpoint."""

    @pytest.mark.asyncio
    async def test_get_projects_requires_authentication(self, client: AsyncClient):
        """Test that GET /projects requires authentication."""
        response = await client.get("/api/v1/projects")

        assert response.status_code == 401
        assert "error" in response.json()
        assert response.json()["error"] == "AUTH_UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_get_projects_returns_empty_list(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test GET /projects returns empty list when user has no projects."""
        response = await client.get("/api/v1/projects", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert "total" in data
        assert data["projects"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_projects_returns_user_projects(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_project: Project,
    ):
        """Test GET /projects returns user's active projects."""
        response = await client.get("/api/v1/projects", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["projects"]) == 1

        project = data["projects"][0]
        assert project["id"] == str(test_project.id)
        assert project["title"] == test_project.title
        assert project["description"] == test_project.description
        assert project["deletion_status"] == "active"
        assert "created_at" in project
        assert "last_activity_at" in project

    @pytest.mark.asyncio
    async def test_get_projects_excludes_trashed_by_default(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_project: Project,
        trashed_project: Project,
    ):
        """Test GET /projects excludes trashed projects by default."""
        response = await client.get("/api/v1/projects", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

        project_ids = [p["id"] for p in data["projects"]]
        assert str(test_project.id) in project_ids
        assert str(trashed_project.id) not in project_ids

    @pytest.mark.asyncio
    async def test_get_projects_includes_trashed_when_requested(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_project: Project,
        trashed_project: Project,
    ):
        """Test GET /projects includes trashed projects when include_trashed=true."""
        response = await client.get(
            "/api/v1/projects",
            headers=auth_headers,
            params={"include_trashed": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

        project_ids = [p["id"] for p in data["projects"]]
        assert str(test_project.id) in project_ids
        assert str(trashed_project.id) in project_ids

    @pytest.mark.asyncio
    async def test_get_projects_only_returns_own_projects(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_project: Project,
        db_session: AsyncSession,
    ):
        """Test GET /projects only returns authenticated user's projects."""
        from src.utils.security import hash_password

        # Create another user with a project
        other_user = User(
            email="other@example.com",
            password_hash=hash_password("OtherPass123!"),
            skill_level="Beginner",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        other_project = Project(
            user_id=other_user.id,
            title="Other User's Project",
            deletion_status="active",
        )
        db_session.add(other_project)
        await db_session.commit()

        # Request with first user's auth
        response = await client.get("/api/v1/projects", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

        project_ids = [p["id"] for p in data["projects"]]
        assert str(test_project.id) in project_ids
        assert str(other_project.id) not in project_ids


# =============================================================================
# T047: POST /projects - Create New Project
# =============================================================================


class TestCreateProject:
    """Test suite for POST /projects endpoint."""

    @pytest.mark.asyncio
    async def test_create_project_requires_authentication(self, client: AsyncClient):
        """Test that POST /projects requires authentication."""
        response = await client.post(
            "/api/v1/projects",
            json={"title": "New Project"}
        )

        assert response.status_code == 401
        assert "error" in response.json()

    @pytest.mark.asyncio
    async def test_create_project_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test successful project creation."""
        response = await client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={
                "title": "My New Project",
                "description": "Learning Python basics"
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["title"] == "My New Project"
        assert data["description"] == "Learning Python basics"
        assert data["deletion_status"] == "active"
        assert "created_at" in data
        assert "last_activity_at" in data

    @pytest.mark.asyncio
    async def test_create_project_without_description(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test creating project without description (optional field)."""
        response = await client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={"title": "Project Without Description"}
        )

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == "Project Without Description"
        assert data["description"] is None or data["description"] == ""

    @pytest.mark.asyncio
    async def test_create_project_title_required(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test that title is required."""
        response = await client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={"description": "No title provided"}
        )

        assert response.status_code == 422
        assert "error" in response.json()

    @pytest.mark.asyncio
    async def test_create_project_title_not_empty(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test that title cannot be empty string."""
        response = await client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={"title": "   "}
        )

        assert response.status_code == 422
        assert "error" in response.json()

    @pytest.mark.asyncio
    async def test_create_project_title_max_length(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test that title respects max length (255 chars)."""
        long_title = "A" * 256
        response = await client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={"title": long_title}
        )

        assert response.status_code == 422
        assert "error" in response.json()


# =============================================================================
# T048: GET /projects/{project_id} - Get Project Details
# =============================================================================


class TestGetProjectById:
    """Test suite for GET /projects/{project_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_project_requires_authentication(
        self,
        client: AsyncClient,
        test_project: Project,
    ):
        """Test that GET /projects/{id} requires authentication."""
        response = await client.get(f"/api/v1/projects/{test_project.id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_project_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_project: Project,
    ):
        """Test successful retrieval of project details."""
        response = await client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(test_project.id)
        assert data["title"] == test_project.title
        assert data["description"] == test_project.description
        assert data["deletion_status"] == "active"
        assert "created_at" in data
        assert "last_activity_at" in data

    @pytest.mark.asyncio
    async def test_get_project_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test 404 response for non-existent project."""
        fake_id = uuid4()
        response = await client.get(
            f"/api/v1/projects/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404
        assert "error" in response.json()
        assert response.json()["error"] == "RESOURCE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_get_project_forbidden_other_user(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test 403 response when trying to access another user's project."""
        from src.utils.security import hash_password

        # Create another user with a project
        other_user = User(
            email="other@example.com",
            password_hash=hash_password("OtherPass123!"),
            skill_level="Beginner",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        other_project = Project(
            user_id=other_user.id,
            title="Other User's Project",
            deletion_status="active",
        )
        db_session.add(other_project)
        await db_session.commit()
        await db_session.refresh(other_project)

        # Try to access with first user's auth
        response = await client.get(
            f"/api/v1/projects/{other_project.id}",
            headers=auth_headers
        )

        assert response.status_code == 403
        assert "error" in response.json()
        assert response.json()["error"] == "AUTH_FORBIDDEN"

    @pytest.mark.asyncio
    async def test_get_trashed_project_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        trashed_project: Project,
    ):
        """Test that trashed projects return 404 by default."""
        response = await client.get(
            f"/api/v1/projects/{trashed_project.id}",
            headers=auth_headers
        )

        assert response.status_code == 404


# =============================================================================
# T049: PATCH /projects/{project_id} - Update Project
# =============================================================================


class TestUpdateProject:
    """Test suite for PATCH /projects/{project_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_project_requires_authentication(
        self,
        client: AsyncClient,
        test_project: Project,
    ):
        """Test that PATCH /projects/{id} requires authentication."""
        response = await client.patch(
            f"/api/v1/projects/{test_project.id}",
            json={"title": "Updated Title"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_project_title(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_project: Project,
    ):
        """Test updating project title."""
        response = await client.patch(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers,
            json={"title": "Updated Project Title"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(test_project.id)
        assert data["title"] == "Updated Project Title"
        assert data["description"] == test_project.description  # Unchanged

    @pytest.mark.asyncio
    async def test_update_project_description(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_project: Project,
    ):
        """Test updating project description."""
        response = await client.patch(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers,
            json={"description": "New description"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(test_project.id)
        assert data["title"] == test_project.title  # Unchanged
        assert data["description"] == "New description"

    @pytest.mark.asyncio
    async def test_update_project_both_fields(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_project: Project,
    ):
        """Test updating both title and description."""
        response = await client.patch(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers,
            json={
                "title": "New Title",
                "description": "New Description"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["title"] == "New Title"
        assert data["description"] == "New Description"

    @pytest.mark.asyncio
    async def test_update_project_empty_title_rejected(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_project: Project,
    ):
        """Test that empty title is rejected."""
        response = await client.patch(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers,
            json={"title": "   "}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_project_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test 404 for non-existent project."""
        fake_id = uuid4()
        response = await client.patch(
            f"/api/v1/projects/{fake_id}",
            headers=auth_headers,
            json={"title": "New Title"}
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_project_forbidden_other_user(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test 403 when trying to update another user's project."""
        from src.utils.security import hash_password

        other_user = User(
            email="other@example.com",
            password_hash=hash_password("OtherPass123!"),
            skill_level="Beginner",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        other_project = Project(
            user_id=other_user.id,
            title="Other User's Project",
            deletion_status="active",
        )
        db_session.add(other_project)
        await db_session.commit()
        await db_session.refresh(other_project)

        response = await client.patch(
            f"/api/v1/projects/{other_project.id}",
            headers=auth_headers,
            json={"title": "Hacked Title"}
        )

        assert response.status_code == 403


# =============================================================================
# T050: DELETE /projects/{project_id} - Soft Delete Project
# =============================================================================


class TestDeleteProject:
    """Test suite for DELETE /projects/{project_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_project_requires_authentication(
        self,
        client: AsyncClient,
        test_project: Project,
    ):
        """Test that DELETE /projects/{id} requires authentication."""
        response = await client.delete(f"/api/v1/projects/{test_project.id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_project_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_project: Project,
        db_session: AsyncSession,
    ):
        """Test successful soft delete of project."""
        response = await client.delete(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )

        assert response.status_code == 204
        assert response.content == b""

        # Verify project is trashed in database
        await db_session.refresh(test_project)
        assert test_project.deletion_status == "trashed"
        assert test_project.trashed_at is not None
        assert test_project.scheduled_deletion_at is not None

    @pytest.mark.asyncio
    async def test_delete_project_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test 404 for non-existent project."""
        fake_id = uuid4()
        response = await client.delete(
            f"/api/v1/projects/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project_forbidden_other_user(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test 403 when trying to delete another user's project."""
        from src.utils.security import hash_password

        other_user = User(
            email="other@example.com",
            password_hash=hash_password("OtherPass123!"),
            skill_level="Beginner",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        other_project = Project(
            user_id=other_user.id,
            title="Other User's Project",
            deletion_status="active",
        )
        db_session.add(other_project)
        await db_session.commit()
        await db_session.refresh(other_project)

        response = await client.delete(
            f"/api/v1/projects/{other_project.id}",
            headers=auth_headers
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_already_trashed_project(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        trashed_project: Project,
    ):
        """Test that deleting already trashed project returns 404."""
        response = await client.delete(
            f"/api/v1/projects/{trashed_project.id}",
            headers=auth_headers
        )

        assert response.status_code == 404
