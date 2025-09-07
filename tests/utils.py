import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Todo, User
from app.routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"id": 1, "username": "adminuser_test", "role": "admin"}


@pytest.fixture
def test_todo():
    db = TestingSessionLocal()
    todo = Todo(
        title="Test Todo",
        description="This is a test todo",
        priority=1,
        completed=False,
        owner_id=1,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.commit()


@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    hashed_password = bcrypt_context.hash("test.password")
    user = User(
        email="test_user@example.com",
        phone_number="1234567890",
        username="test_user",
        first_name="Test",
        last_name="User",
        hashed_password=hashed_password,
        is_active=True,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()
