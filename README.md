# Todo Application

A simple Todo application with user authentication and admin management.

## Features

*   User registration and authentication with JWT.
*   Create, read, update, and delete Todos.
*   Admin panel to manage users.
*   Database migrations with Alembic.
*   **Redis caching for improved performance** (optional, with graceful fallback).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.9+
*   pip
*   Redis (optional, for caching)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the database:**

    The application uses SQLite by default. No further setup is required.

5.  **Configure environment variables (optional):**

    Create a `.env` file in the project root with the following variables:

    ```env
    # Database
    SQLALCHEMY_DATABASE_URL=sqlite:///./app.db

    # JWT Configuration
    SECRET_KEY=your-secret-key-here
    ALGORITHM=HS256

    # CORS Origins
    CORS_ORIGINS=http://localhost:3000,http://localhost:5173

    # Redis Configuration (optional)
    REDIS_HOST=localhost
    REDIS_PORT=6379
    REDIS_PASSWORD=
    REDIS_DB=0
    CACHE_TTL=300
    ```

    **Redis Caching:**
    - If Redis is available, the application will use it to cache frequently accessed data
    - If Redis is not available, the application will continue to work normally without caching
    - Cached data includes: user todos, individual todos, and user profiles
    - Default cache TTL is 5 minutes (300 seconds)

6.  **Run the database migrations:**

    ```bash
    alembic upgrade head
    ```

7.  **Run the application:**

    ```bash
    uvicorn main:app --reload
    ```

The application will be available at `http://127.0.0.1:8000`.

## Usage

The API documentation is available at `http://127.0.0.1:8000/docs`.

### API Endpoints

*   **Auth:**
    *   `POST /auth/register`: Register a new user.
    *   `POST /auth/token`: Get a JWT token.
*   **Todos:**
    *   `GET /todos`: Get all todos for the authenticated user.
    *   `POST /todos`: Create a new todo.
    *   `GET /todos/{todo_id}`: Get a specific todo.
    *   `PUT /todos/{todo_id}`: Update a specific todo.
    *   `DELETE /todos/{todo_id}`: Delete a specific todo.
*   **Admin:**
    *   `GET /admin/users`: Get all users (admin only).
    *   `DELETE /admin/users/{user_id}`: Delete a user (admin only).

## Database Migrations

This project uses Alembic to manage database migrations.

*   **Create a new migration:**

    ```bash
    alembic revision --autogenerate -m "Your migration message"
    ```

*   **Apply migrations:**

    ```bash
    alembic upgrade head
    ```

*   **Downgrade migrations:**

    ```bash
    alembic downgrade -1
    ```

## Running Tests

To run the tests, use the following command:

```bash
pytest
```

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature`).
6.  Open a pull request.
