# Todo Application

A simple Todo application with user authentication and admin management, built with FastAPI and containerized with Docker.

## Features

*   User registration and authentication with JWT.
*   Create, read, update, and delete Todos.
*   Admin panel to manage users.
*   Database migrations with Alembic.
*   Containerized with Docker and Docker Compose.
*   Production-ready Nginx reverse proxy.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.9+ (for local development)
*   Docker and Docker Compose (for containerized development/production)

## Docker Setup (Recommended)

### Production Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```

2.  **Start all services:**

    ```bash
    docker compose up -d
    ```

    This will start:
    - PostgreSQL database
    - Database migration service
    - FastAPI application
    - Nginx reverse proxy

3.  **Access the application:**

    - API: `http://localhost` (via Nginx)
    - Direct API: `http://localhost:8000`
    - API Documentation: `http://localhost/docs`

4.  **Stop services:**

    ```bash
    docker compose down
    ```

### Development Setup

For development with hot reload:

1.  **Start development services:**

    ```bash
    docker compose -f docker-compose.dev.yml up -d
    ```

    This uses SQLite and enables hot reload for faster development.

2.  **Access the application:**

    - API: `http://localhost:8000`
    - API Documentation: `http://localhost:8000/docs`

3.  **Optional: Start with Nginx:**

    ```bash
    docker compose -f docker-compose.dev.yml --profile nginx up -d
    ```

### Database Migrations

Migrations are automatically handled in the production setup. For manual migration management:

```bash
# Create a new migration
docker compose exec api alembic revision --autogenerate -m "Your migration message"

# Apply migrations
docker compose exec api alembic upgrade head

# Downgrade migrations
docker compose exec api alembic downgrade -1
```

## Local Development (Without Docker)

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

4.  **Set up environment variables:**

    Create a `.env` file with:
    ```env
    SQLALCHEMY_DATABASE_URL=sqlite:///./todos.db
    SECRET_KEY=your-secret-key-here-change-in-production
    ALGORITHM=HS256
    ```

5.  **Run the database migrations:**

    ```bash
    alembic upgrade head
    ```

6.  **Run the application:**

    ```bash
    uvicorn main:app --reload
    ```

The application will be available at `http://127.0.0.1:8000`.

## Usage

The API documentation is available at:
- Production: `http://localhost/docs`
- Development: `http://localhost:8000/docs`

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

## Architecture

### Production Architecture

```
Internet → Nginx (Port 80) → FastAPI (Port 8000) → PostgreSQL (Port 5432)
                ↓
          Migration Service (One-time)
```

### Services

- **nginx**: Reverse proxy and load balancer
- **api**: FastAPI application server
- **db**: PostgreSQL database
- **migrate**: Database migration service (runs once)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SQLALCHEMY_DATABASE_URL` | Database connection URL | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000,http://localhost:5173` |

### Database Configuration

- **Production**: PostgreSQL (recommended)
- **Development**: SQLite (simpler setup)

## Running Tests

To run the tests:

```bash
# Local environment
pytest

# Docker environment
docker compose exec api pytest
```

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature`).
6.  Open a pull request.

## Deployment

### Production Deployment

1. Clone the repository to your server
2. Update environment variables in `docker-compose.yml` or use environment files
3. Run `docker compose up -d`
4. Configure your domain and SSL certificates as needed

### Environment Files

For production, consider using environment files:

```bash
# Create production environment file
cp .env.docker .env.production

# Start with production environment
docker compose --env-file .env.production up -d
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 80, 8000, and 5432 are available
2. **Database connection**: Ensure PostgreSQL is healthy before API starts
3. **Migration failures**: Check database credentials and connectivity

### Logs

```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs api
docker compose logs nginx
docker compose logs db
```
