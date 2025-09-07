from datetime import timedelta

from fastapi import status, HTTPException
from fastapi.testclient import TestClient
from jose import jwt

from app.dependencies import (
    get_db,
    get_current_user,
    authenticate_user,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)
from main import app
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(
        db, username="test_user", password="test.password"
    )
    assert authenticated_user is not None
    assert authenticated_user.username == "test_user"
    non_existent_user = authenticate_user(
        db, username="nonexistent", password="test.password"
    )
    assert non_existent_user is False
    wrong_password_user = authenticate_user(
        db, username="test_user", password="wrong.password"
    )
    assert wrong_password_user is False


def test_create_access_token(test_user):
    token = create_access_token(
        username="test_user",
        user_id=1,
        role="user",
        expires_delta=timedelta(minutes=30),
    )
    assert token is not None
    decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_payload["sub"] == "test_user"
    assert decoded_payload["id"] == 1
    assert decoded_payload["role"] == "user"


@pytest.mark.asyncio
async def test_get_current_user_valid_token(test_user):
    encode = {"sub": "test_user", "id": 1, "role": "user"}
    token = jwt.encode(
        encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    user = await get_current_user(token=token)
    assert user is not None
    assert user == {"id": 1, "username": "test_user", "role": "user"}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    token = jwt.encode(
        {},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"


def test_get_current_user(test_user):
    response = client.get("auth/me")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "email": "test_user@example.com",
        "phone_number": "1234567890",
        "username": "test_user",
        "is_active": True,
        "role": "user",
        "first_name": "Test",
        "last_name": "User",
    }


def test_change_password(test_user):
    response = client.post(
        "/auth/change_password",
        json={"old_password": "test.password", "new_password": "new.password"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "Password updated successfully"}

    # Verify that the old password no longer works
    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == "test_user").first()
    assert not bcrypt_context.verify("test.password", user.hashed_password)
    # Verify that the new password works
    assert bcrypt_context.verify("new.password", user.hashed_password)
