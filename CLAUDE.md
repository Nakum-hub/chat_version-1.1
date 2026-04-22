# Cyberfyx Website — Claude Code Guide

## Project Layout

```
prototype/
├── backend/   FastAPI + SQLAlchemy backend
└── frontend/  Vanilla HTML/CSS/JS prototype
```

## Backend

**Working directory for all backend commands:** `prototype/backend/`

### Setup
```bash
python -m venv venv && source venv/bin/activate
python -m pip install -e .[dev]
cp .env.example .env          # then set CYBERFYX_JWT_SECRET_KEY
alembic -c alembic/alembic.ini upgrade head
python -m app.db.seed
uvicorn app.main:app --reload --port 8000
```

### Tech Stack
- **Python 3.12**, FastAPI 0.115, SQLAlchemy 2.0, Alembic, Pydantic v2
- **Default DB:** SQLite (`cyberfyx.db`) — configured via `CYBERFYX_DATABASE_URL`
- **Auth:** argon2 password hashing, PyJWT HS256 access tokens
- **Config:** all settings via `CYBERFYX_*` env vars (see `app/core/config.py`)

### Key Files
| File | Purpose |
|---|---|
| `app/main.py` | App factory, CORS, security headers, health endpoints |
| `app/core/config.py` | `Settings` via pydantic-settings (`CYBERFYX_` prefix) |
| `app/core/database.py` | SQLAlchemy engine + `get_db()` session dependency |
| `app/core/security.py` | Password hash (argon2) + JWT encode/decode |
| `app/api/router.py` | Mounts public + conditional internal routers |
| `app/services/inquiry.py` | Inquiry creation with rate-limit + dedup logic |
| `app/services/outbox.py` | Outbox enqueue/process (transactional event delivery) |
| `app/worker.py` | Outbox batch runner (SMTP handlers are stubs — not yet wired) |

### API Routes
```
GET  /health/live                          — liveness
GET  /health/ready                         — readiness (checks DB)

GET  /api/v1/public/site/contact-profile   — contact info + interest options
GET  /api/v1/public/catalog/tracks         — solution tracks
GET  /api/v1/public/catalog/tracks/{slug}  — single track detail
POST /api/v1/public/inquiries              — submit contact inquiry

# Only when CYBERFYX_ENABLE_INTERNAL_API=true
POST /api/v1/internal/auth/token           — issue JWT
GET  /api/v1/internal/auth/me
GET  /api/v1/internal/inquiries
GET  /api/v1/internal/inquiries/{id}
PATCH /api/v1/internal/inquiries/{id}
```

### Running Tests
```bash
cd prototype/backend
pytest
```
Tests use an isolated SQLite DB (`.test-cyberfyx.db`) created/torn down per test. No real DB required.

### Alembic
```bash
cd prototype/backend
alembic -c alembic/alembic.ini upgrade head        # apply migrations
alembic -c alembic/alembic.ini revision --autogenerate -m "description"  # new migration
```

## Frontend

Static HTML pages served from `prototype/frontend/`. No build step.

- `main.js` — single JS module handling nav, animations, contact form, API integration
- API base is derived from `window.location.origin` or `<meta name="cyberfyx-api-base">` tag
- Falls back to `mailto:` if the backend is unreachable

**Local preview:** open HTML files directly, or serve with `python -m http.server 8080` from `prototype/frontend/`.

## Known Gaps (from audit)

- **SMTP not implemented** — outbox worker handlers are stubs (`_noop_handler`), so inquiry notifications never fire
- **Auth endpoint not rate-limited** — `slowapi` is in deps but not wired to `/auth/token`
- **No CSP header** — should be added to the HTTP middleware in `app/main.py`
- **`?apiBase=` query param** in `main.js` allows form destination override — security risk for production

## Environment Variables

All prefixed with `CYBERFYX_`. Key ones:

| Variable | Default | Notes |
|---|---|---|
| `CYBERFYX_ENVIRONMENT` | `development` | Set to `production` to hide docs + enforce secret |
| `CYBERFYX_DATABASE_URL` | `sqlite:///./cyberfyx.db` | Use `postgresql+asyncpg://...` for prod |
| `CYBERFYX_JWT_SECRET_KEY` | `replace-with-a-long-random-secret` | **Must change for production** |
| `CYBERFYX_ENABLE_INTERNAL_API` | `false` | Set `true` to mount admin endpoints |
| `CYBERFYX_CORS_ORIGINS` | `http://127.0.0.1:8080,...` | Comma-separated list |
| `CYBERFYX_SMTP_HOST` | _(empty)_ | SMTP not implemented yet |

## Docker

```bash
cd prototype/backend
docker build -t cyberfyx-backend .
docker run -p 8000:8000 --env-file .env cyberfyx-backend
```
