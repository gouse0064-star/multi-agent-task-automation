
from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Multi-Agent Task Automation API is running"
    )


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_empty_task_is_rejected():
    response = client.post(
        "/api/tasks",
        json={"task": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Task cannot be empty"


def test_missing_task_is_rejected():
    response = client.post("/api/tasks", json={})

    assert response.status_code == 422


def test_task_too_long_is_rejected():
    response = client.post(
        "/api/tasks",
        json={"task": "a" * 2001},
    )

    assert response.status_code == 422

def test_stream_requires_task_id():
    response = client.post(
        "/api/tasks/stream",
        json={"task": "Test task"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Missing X-Task-ID header"


def test_cancel_unknown_task():
    response = client.post(
        "/api/tasks/test-unknown-task-id/cancel"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "not_running"


def test_cancel_active_task():
    import threading
    from app.api import active_tasks, active_tasks_lock

    task_id = "test-active-task"
    cancel_event = threading.Event()

    with active_tasks_lock:
        active_tasks[task_id] = cancel_event

    try:
        response = client.post(
            f"/api/tasks/{task_id}/cancel"
        )

        assert response.status_code == 200
        assert response.json()["status"] == "cancellation_requested"
        assert cancel_event.is_set()

    finally:
        with active_tasks_lock:
            active_tasks.pop(task_id, None)
