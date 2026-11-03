"""
Tests for task API endpoints.
"""
import pytest

import main


@pytest.fixture(autouse=True)
def reset_tasks():
    """Clear the in-memory task store so each test starts empty."""
    main.tasks.clear()
    yield
    main.tasks.clear()


def _create(client, **overrides):
    payload = {"title": "Check stock levels", "priority": "high", "dueDate": "2025-10-08"}
    payload.update(overrides)
    return client.post("/api/tasks", json=payload)


class TestTasksEndpoints:
    """Test suite for task endpoints."""

    def test_get_all_tasks_empty(self, client):
        """Test that the task list starts empty."""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_task(self, client):
        """Test creating a task returns it as pending."""
        response = _create(client)
        assert response.status_code == 201

        task = response.json()
        assert isinstance(task["id"], str)
        assert task["title"] == "Check stock levels"
        assert task["priority"] == "high"
        assert task["dueDate"] == "2025-10-08"
        assert task["status"] == "pending"

    def test_get_tasks_newest_first(self, client):
        """Test that tasks are listed newest first."""
        first = _create(client, title="First").json()
        second = _create(client, title="Second").json()

        data = client.get("/api/tasks").json()
        assert [t["id"] for t in data] == [second["id"], first["id"]]

    def test_create_task_strips_title(self, client):
        """Test that surrounding whitespace is removed from titles."""
        task = _create(client, title="  Approve orders  ").json()
        assert task["title"] == "Approve orders"

    @pytest.mark.parametrize("overrides", [
        {"title": "   "},
        {"title": "x" * 201},
        {"priority": "urgent"},
        {"dueDate": "next week"},
    ])
    def test_create_task_invalid_input(self, client, overrides):
        """Test that invalid task fields are rejected."""
        response = _create(client, **overrides)
        assert response.status_code == 422

    def test_create_task_store_full(self, client, monkeypatch):
        """Test that new tasks are refused once the in-memory store is full."""
        monkeypatch.setattr(main, "MAX_TASKS", 1)
        assert _create(client).status_code == 201

        response = _create(client)
        assert response.status_code == 409

    def test_toggle_task(self, client):
        """Test toggling a task between pending and completed."""
        task_id = _create(client).json()["id"]

        response = client.patch(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

        response = client.patch(f"/api/tasks/{task_id}")
        assert response.json()["status"] == "pending"

    def test_delete_task(self, client):
        """Test deleting a task removes it from the list."""
        task_id = _create(client).json()["id"]

        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 204
        assert client.get("/api/tasks").json() == []

    def test_task_ids_not_reused_after_delete(self, client):
        """Test that a new task never reuses a deleted task's id."""
        first_id = _create(client).json()["id"]
        client.delete(f"/api/tasks/{first_id}")

        assert _create(client).json()["id"] != first_id

    @pytest.mark.parametrize("method", ["patch", "delete"])
    def test_nonexistent_task(self, client, method):
        """Test that toggling or deleting a missing task returns 404."""
        response = getattr(client, method)("/api/tasks/nonexistent-999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestCorsPolicy:
    """Test suite for the CORS policy."""

    def test_cors_allows_dev_frontend(self, client):
        """Test that the local Vite dev server origin is allowed."""
        response = client.get("/api/inventory", headers={"Origin": "http://localhost:3000"})
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_cors_rejects_other_origins(self, client):
        """Test that arbitrary websites can't read API responses."""
        response = client.get("/api/inventory", headers={"Origin": "https://evil.example"})
        assert "access-control-allow-origin" not in response.headers
