# Fast Todo API

Fast Todo API is a Python FastAPI-based Todo application with user authentication, JWT tokens, and admin management. It uses SQLAlchemy for ORM, Alembic for database migrations, and SQLite as the default database (with PostgreSQL support).

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

Bootstrap, build, and test the repository:
- `python3 -m venv .venv` -- takes 3 seconds.
- `source .venv/bin/activate`
- `pip install -r requirements.txt` -- takes 30 seconds. NEVER CANCEL. Set timeout to 600+ seconds.
  - If network timeouts occur, retry with: `pip install --timeout 300 -r requirements.txt`
- Create environment file: `echo "SQLALCHEMY_DATABASE_URL=sqlite:///./todos.db\nSECRET_KEY=your-secret-key-here-change-this-in-production\nALGORITHM=HS256" > .env`
- `alembic upgrade head` -- takes less than 1 second.

Run tests:
- `pytest -v` -- takes 4 seconds. NEVER CANCEL. Set timeout to 30+ seconds.
- All 13 tests should pass. If JWT-related tests fail, verify .env file has SECRET_KEY and ALGORITHM set.

Run the application:
- ALWAYS run the bootstrapping steps first.
- `uvicorn main:app --reload --host 0.0.0.0 --port 8000` -- starts immediately.
- Application available at `http://localhost:8000`
- API documentation at `http://localhost:8000/docs`
- Health check at `http://localhost:8000/health`

## Validation

- ALWAYS manually validate any new code by testing API endpoints after making changes.
- Test the complete workflow: register user → login → create todo → get todos.
- Example validation workflow:
  ```bash
  # Register user
  curl -X POST "http://localhost:8000/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "username": "testuser", "first_name": "Test", "last_name": "User", "password": "test123"}'
  
  # Login to get token
  curl -X POST "http://localhost:8000/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d 'username=testuser&password=test123'
  
  # Create todo (use token from login)
  curl -X POST "http://localhost:8000/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_TOKEN_HERE" \
    -d '{"title": "Test Todo", "description": "Test description", "priority": 1}'
  
  # Get todos
  curl -H "Authorization: Bearer YOUR_TOKEN_HERE" "http://localhost:8000/"
  ```
- Always run `black --check .` and then `black .` to format code before committing.

## Common tasks

### Essential Commands
- Virtual environment creation: `python3 -m venv .venv` (3 seconds)
- Dependency installation: `pip install -r requirements.txt` (30 seconds)
- Database migration: `alembic upgrade head` (<1 second)
- Run tests: `pytest -v` (4 seconds)
- Code formatting check: `black --check .` (<1 second)
- Code formatting: `black .` (<1 second)
- Start application: `uvicorn main:app --reload` (immediate)

### Repository Structure
```
.
├── README.md
├── requirements.txt
├── main.py                 # FastAPI application entry point
├── alembic.ini            # Database migration configuration
├── alembic/               # Database migration scripts
├── app/
│   ├── __init__.py
│   ├── database.py        # SQLAlchemy database setup
│   ├── dependencies.py    # JWT auth, password hashing
│   ├── models.py          # User and Todo SQLAlchemy models
│   ├── schema.py          # Pydantic schemas for validation
│   └── routers/
│       ├── auth.py        # Authentication endpoints
│       ├── todos.py       # Todo CRUD endpoints
│       └── admin.py       # Admin management endpoints
└── tests/
    ├── test_main.py       # Health check tests
    ├── test_auth.py       # Authentication tests
    ├── test_todos.py      # Todo functionality tests
    ├── test_admin.py      # Admin functionality tests
    └── utils.py           # Test fixtures and utilities
```

### Environment Requirements
- Python 3.12.3 (or compatible 3.9+)
- Required environment variables in `.env`:
  ```
  SQLALCHEMY_DATABASE_URL=sqlite:///./todos.db
  SECRET_KEY=your-secret-key-here-change-this-in-production
  ALGORITHM=HS256
  ```

### API Endpoints Summary
- **Health**: `GET /health`
- **Auth**: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `POST /auth/change_password`
- **Todos**: `GET /`, `POST /`, `GET /{todo_id}`, `PUT /{todo_id}`, `DELETE /{todo_id}`
- **Admin**: `GET /admin/users`, `DELETE /admin/users/{user_id}`, `GET /admin/todos`, `GET /admin/todos/{todo_id}`, `DELETE /admin/todos/{todo_id}`

### Key Files to Check After Changes
- Always check `app/dependencies.py` after making changes to authentication
- Always check `app/models.py` after making changes to database schema
- Always run tests after making changes to router files in `app/routers/`
- Always run `black .` after making any code changes

### Database
- Uses SQLite by default (file: `todos.db`)
- Supports PostgreSQL via psycopg2-binary
- Database migrations managed by Alembic
- Test database is separate (`test.db`) and managed by test fixtures

### Known Issues
- One deprecation warning about 'crypt' module in tests (Python 3.13 compatibility) - this is from passlib dependency and can be ignored
- Pip install may timeout due to network issues - retry with `pip install --timeout 300 -r requirements.txt` if needed
- No GitHub Actions CI/CD pipeline exists yet