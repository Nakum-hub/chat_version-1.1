# Backend Documentation

The Cyberfyx backend is a **FastAPI** application designed to handle public inquiries, internal staff management, and lead-routing workflows.

## Technical Stack

- **Framework**: FastAPI (Python 3.12+)
- **ORM**: SQLAlchemy 2.x
- **Migrations**: Alembic
- **Database**: SQLite (default), PostgreSQL (production-ready)
- **Task Processing**: Custom outbox worker for background tasks (e.g., email notifications).

## Project Structure

```text
backend/
├── alembic/            # Database migration scripts
├── app/
│   ├── api/            # API routers (Public & Internal)
│   ├── core/           # Configuration, Database, Error handlers
│   ├── models/         # SQLAlchemy model definitions
│   ├── schemas/        # Pydantic data models
│   ├── services/       # Core business logic
│   ├── worker.py       # Outbox notification process
│   └── main.py         # Application entry point
├── scripts/            # Utility scripts (seeding, etc.)
└── tests/              # Pytest suite
```

## Key API Features

### Public API (`/api/v1/public`)
- **`POST /inquiries`**: Accepts contact form submissions. Supports both JSON and form-encoded payloads.
- **`GET /catalog`**: Read-only access to service and solution descriptions.

### Internal API (`/api/v1/internal`)
- **Authentication**: JWT-based security for administrative endpoints.
- **`GET /staff-users`**: Directory used for assignment and contact workflows.
- **Inquiry Management**: Endpoints for tracking and updating the status of lead inquiries.

## Core Workflows

### 1. Database Migrations
We use Alembic to manage schema changes. To apply migrations:
```bash
alembic -c alembic/alembic.ini upgrade head
```

### 2. Data Seediing
To initialize the database with reference data (e.g., initial catalog, staff):
```bash
python -m app.db.seed
```

### 3. Outbox Worker
Email notifications are handled using the **Outbox Pattern** to ensure reliability. The worker process monitors the database for pending events:
```bash
python -m app.worker
```

## Configuration

Configuration is managed via environment variables. Key settings in `.env` include:
- `CYBERFYX_DATABASE_URL`: Connection string for the database.
- `CYBERFYX_ENABLE_INTERNAL_API`: Boolean to toggle administrative features.
- `CYBERFYX_SMTP_HOST`: Host for outgoing notifications.

For a full list of configuration options, refer to `app/core/config.py`.
