from fastapi.testclient import TestClient
from fastapi import status

from app.dependencies import get_db, get_current_user
from .utils import *
from main import app


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_admin_read_all_todos(test_todo):
    response = client.get("/admin/todos/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "description": "This is a test todo",
            "completed": False,
            "owner_id": 1,
            "title": "Test Todo",
            "priority": 1,
            "id": test_todo.id,
        }
    ]


def test_admin_delete_todo(test_todo):
    response = client.delete(f"/admin/todos/{test_todo.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Verify the todo is deleted
    response = client.get(f"/admin/todos/{test_todo.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}
