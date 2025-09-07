from fastapi.testclient import TestClient
from fastapi import status

from app.dependencies import get_db, get_current_user
from main import app
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_read_all_authenticated(test_todo):
    response = client.get("/")
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


def test_read_one_authenticated(test_todo):
    response = client.get(f"/{test_todo.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "description": "This is a test todo",
        "completed": False,
        "owner_id": 1,
        "title": "Test Todo",
        "priority": 1,
        "id": test_todo.id,
    }


def test_read_one_not_found(test_todo):
    response = client.get("/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}


def test_create_todo_authenticated(test_todo):
    response = client.post(
        "/",
        json={
            "title": "New Todo",
            "description": "New todo description",
            "priority": 2,
            "completed": False,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["title"] == "New Todo"
    assert response.json()["description"] == "New todo description"
    assert response.json()["priority"] == 2
    assert response.json()["completed"] is False
    assert response.json()["owner_id"] == 1
