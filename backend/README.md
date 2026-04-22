# Cyberfyx Backend

This package provides the production-grade backend foundation for the Cyberfyx website.

## Scope

- Public inquiry intake API for the contact form
- Optional internal authenticated inquiry-management API
- Internal staff directory API for assignment workflows
- Public read APIs for contact profile and solution catalog content
- Strong schema integrity with Alembic migrations
- Audit logging for inquiry lifecycle changes
- Outbox-backed notification foundation

## Stack Decision

- Python `FastAPI` modular monolith
- SQLAlchemy + Alembic
- PostgreSQL-ready schema, SQLite default for local development

Node.js and Java are intentionally not used in this first backend cut because the current frontend only justifies a secure marketing, catalog, and lead-routing backend. Introducing multiple services or languages now would add operational cost without product value.

## Local Run

1. Create and activate a virtual environment.
2. Install dependencies:

   `python -m pip install -e .[dev]`

3. Copy `.env.example` to `.env` and adjust values.
   Keep `CYBERFYX_ENABLE_INTERNAL_API=false` for a public-only deployment. Turn it on only for a staff-admin deployment path.
4. Run migrations:

   `alembic -c alembic/alembic.ini upgrade head`

5. Seed reference data:

   `python -m app.db.seed`

6. Start the API:

   `uvicorn app.main:app --reload --port 8000`

## Container Deploy

Build from the `prototype` directory so the image includes both `backend/` and `frontend/`:

`docker build -f backend/Dockerfile -t cyberfyx-web .`

Run:

`docker run --rm -p 8000:8000 --env CYBERFYX_JWT_SECRET_KEY=replace-in-production cyberfyx-web`

Notes:

- The container serves the frontend and backend from the same origin.
- The entrypoint runs Alembic migrations on startup.
- The entrypoint runs the idempotent reference-data seed on startup.
- Override `CYBERFYX_RUN_MIGRATIONS_ON_START` or `CYBERFYX_RUN_SEED_ON_START` to `false` if your platform handles those separately.

## API Notes

- `POST /api/v1/public/inquiries` accepts both JSON and form-encoded payloads.
- The inquiry endpoint accepts the frontend form field `subject` as an alias for `interest_slug`.
- Frontend subject values such as `cybersecurity`, `endpoint`, `itsecurity`, `iso`, and `other` are normalized to the backend's canonical interest slugs.
- When internal APIs are enabled, `GET /api/v1/internal/staff-users` returns the assignable staff directory used by inquiry workflows.

## Outbox Worker

- `python -m app.worker` processes pending outbox events.
- If SMTP settings are configured, inquiry notifications are delivered by email.
- If SMTP is not configured, the worker still drains the queue cleanly and logs that delivery was skipped.

## Bootstrap an admin user

PowerShell:

`python -m app.db.seed --bootstrap-admin-email admin@cyberfyx.net --bootstrap-admin-password "ChangeMeLonger123!"`

## Run tests

`pytest`
