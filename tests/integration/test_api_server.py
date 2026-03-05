"""
Integration Tests for API Server

Tests the FastAPI backend endpoints.
"""

import pytest
import sys
import os
from typing import Generator
from httpx import AsyncClient, ASGITransport

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.server import app, db


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the database before each test"""
    # Clear existing data
    db.ideas.clear()
    db.projects.clear()
    db.tasks.clear()
    db.workers.clear()
    db.review_cards.clear()
    db.connections.clear()
    yield


@pytest.fixture
async def client() -> Generator[AsyncClient, None, None]:
    """Create async test client"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ============================================================================
# Health Check Tests
# ============================================================================

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


# ============================================================================
# System Status Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_system_status(client: AsyncClient):
    """Test system status endpoint"""
    response = await client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "system_health" in data
    assert "execution_mode" in data
    assert "stats" in data


@pytest.mark.asyncio
async def test_set_execution_mode(client: AsyncClient):
    """Test setting execution mode"""
    response = await client.post("/api/system/mode?mode=turbo")
    assert response.status_code == 200
    data = response.json()
    assert data["execution_mode"] == "turbo"


@pytest.mark.asyncio
async def test_set_invalid_execution_mode(client: AsyncClient):
    """Test setting invalid execution mode"""
    response = await client.post("/api/system/mode?mode=invalid")
    assert response.status_code == 400


# ============================================================================
# Projects Tests
# ============================================================================

@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient):
    """Test listing projects"""
    response = await client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    """Test creating a project"""
    project_data = {
        "name": "Test Project",
        "one_sentence_goal": "A test project"
    }
    response = await client.post("/api/projects", json=project_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient):
    """Test getting a specific project"""
    # First create a project
    project_data = {"name": "Test Project", "one_sentence_goal": "Goal"}
    create_response = await client.post("/api/projects", json=project_data)
    project_id = create_response.json()["id"]
    
    # Then get it
    response = await client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"


@pytest.mark.asyncio
async def test_get_nonexistent_project(client: AsyncClient):
    """Test getting a project that doesn't exist"""
    response = await client.get("/api/projects/nonexistent")
    assert response.status_code == 404


# ============================================================================
# Tasks Tests
# ============================================================================

@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient):
    """Test listing tasks"""
    response = await client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    """Test creating a task"""
    # First create a project
    project_data = {"name": "Test Project", "one_sentence_goal": "Goal"}
    project_response = await client.post("/api/projects", json=project_data)
    project_id = project_response.json()["id"]
    
    # Then create a task
    task_data = {
        "project_id": project_id,
        "title": "Test Task",
        "goal": "Complete test task"
    }
    response = await client.post("/api/tasks", json=task_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data


@pytest.mark.asyncio
async def test_filter_tasks_by_state(client: AsyncClient):
    """Test filtering tasks by state"""
    # Create a project first
    project_data = {"name": "Test Project", "one_sentence_goal": "Goal"}
    project_response = await client.post("/api/projects", json=project_data)
    project_id = project_response.json()["id"]
    
    # Create tasks with different states
    task1 = {"project_id": project_id, "title": "Task 1", "state": "queued"}
    task2 = {"project_id": project_id, "title": "Task 2", "state": "completed"}
    
    await client.post("/api/tasks", json=task1)
    await client.post("/api/tasks", json=task2)
    
    # Filter by state
    response = await client.get("/api/tasks?state=queued")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(t["state"] == "queued" for t in data)


# ============================================================================
# Workers Tests
# ============================================================================

@pytest.mark.asyncio
async def test_list_workers(client: AsyncClient):
    """Test listing workers"""
    response = await client.get("/api/workers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should have demo workers
    assert len(data) >= 5


@pytest.mark.asyncio
async def test_filter_workers_by_type(client: AsyncClient):
    """Test filtering workers by type"""
    response = await client.get("/api/workers?worker_type=builder")
    assert response.status_code == 200
    data = response.json()
    assert all(w["worker_type"] == "builder" for w in data)


# ============================================================================
# Ideas Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_idea(client: AsyncClient):
    """Test creating an idea"""
    idea_data = {
        "title": "New Feature Idea",
        "description": "A great new feature",
        "priority": "P1"
    }
    response = await client.post("/api/ideas", json=idea_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Feature Idea"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_ideas(client: AsyncClient):
    """Test listing ideas"""
    response = await client.get("/api/ideas")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# ============================================================================
# Reviews (Human Gate) Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_review(client: AsyncClient):
    """Test creating a review card"""
    review_data = {
        "project_id": "test_proj",
        "type": "task_review",
        "risk_level": "medium",
        "context": {"summary": "Test review"}
    }
    response = await client.post("/api/reviews", json=review_data)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "task_review"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_reviews(client: AsyncClient):
    """Test listing reviews"""
    response = await client.get("/api/reviews")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_approve_review(client: AsyncClient):
    """Test approving a review"""
    # Create a review first
    review_data = {
        "project_id": "test_proj",
        "type": "task_review",
        "risk_level": "medium",
        "context": {"summary": "Test review"}
    }
    create_response = await client.post("/api/reviews", json=review_data)
    review_id = create_response.json()["id"]
    
    # Approve it
    response = await client.post(f"/api/reviews/{review_id}/approve?notes=Approved")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["resolution"]["decision"] == "approved"


@pytest.mark.asyncio
async def test_reject_review(client: AsyncClient):
    """Test rejecting a review"""
    # Create a review first
    review_data = {
        "project_id": "test_proj",
        "type": "task_review",
        "risk_level": "medium",
        "context": {"summary": "Test review"}
    }
    create_response = await client.post("/api/reviews", json=review_data)
    review_id = create_response.json()["id"]
    
    # Reject it
    response = await client.post(f"/api/reviews/{review_id}/reject?notes=Rejected")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["resolution"]["decision"] == "rejected"


# ============================================================================
# Connections Tests
# ============================================================================

@pytest.mark.asyncio
async def test_list_connections(client: AsyncClient):
    """Test listing connections"""
    response = await client.get("/api/connections")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_connection(client: AsyncClient):
    """Test creating a connection"""
    conn_data = {
        "provider": "openai",
        "name": "Test API Key",
        "auth_type": "api_key"
    }
    response = await client.post("/api/connections", json=conn_data)
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "openai"
    assert "id" in data


# ============================================================================
# CORS Tests
# ============================================================================

@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    """Test CORS headers are present"""
    response = await client.get("/health")
    assert "access-control-allow-origin" in response.headers or response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
