# Cyberfyx — Deployment Guide

## Architecture

```
Browser ──► Nginx (port 80)
               ├─ /api/*    ──► FastAPI backend (port 8000, internal)
               ├── /health/* ──► FastAPI backend
               └─ /*        ──► Astro static build output
```

All API calls from the browser use relative paths (`/api/v1/...`). Nginx proxies them to the backend. No CORS issues in production.

---

## Quick Start (Docker Compose)

### 1. Configure the backend

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set at minimum:

```env
CYBERFYX_JWT_SECRET_KEY=<long-random-string>   # openssl rand -hex 32
CYBERFYX_ENVIRONMENT=production

# Enable internal admin API (needed for /admin page)
CYBERFYX_ENABLE_INTERNAL_API=true

# Email notifications (optional but recommended)
CYBERFYX_SMTP_HOST=smtp.yourprovider.com
CYBERFYX_SMTP_PORT=587
CYBERFYX_SMTP_USERNAME=noreply@yourdomain.com
CYBERFYX_SMTP_PASSWORD=<smtp-password>
CYBERFYX_SMTP_FROM_EMAIL=noreply@yourdomain.com
CYBERFYX_SMTP_SALES_TO=sales@cyberfyx.net

# Bootstrap first admin user (created on first startup)
CYBERFYX_BOOTSTRAP_STAFF_EMAIL=admin@cyberfyx.net
CYBERFYX_BOOTSTRAP_STAFF_PASSWORD=<secure-password>
```

### 2. Seed the database

The backend auto-runs seed on startup. To run manually:

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -e .[dev]
alembic -c alembic/alembic.ini upgrade head
python -m app.db.seed
```

### 3. Build and start

```bash
docker compose up --build -d
```

The site will be available at `http://localhost`.

### 4. Enable outbox worker (email delivery)

The outbox worker processes notification emails. Run it as a cron job or background service:

```bash
# Via Docker Compose (add to docker-compose.yml):
  worker:
    build: ./backend
    env_file: ./backend/.env
    command: sh -c "while true; do python -m app.worker; sleep 30; done"
    depends_on:
      backend:
        condition: service_healthy
```

Or as a host cron:
```cron
*/1 * * * * cd /path/to/backend && source venv/bin/activate && python -m app.worker
```

---

## Baking backend data into service pages (optional, better SEO)

By default, service pages use **static fallback data** (always works, even if backend is down).

To bake live data from the backend into the built HTML (better for SEO / page load):

1. Start the backend first
2. Build the frontend with `PUBLIC_API_BASE` pointing to it:

```bash
# Start backend
docker compose up backend -d

# Build frontend with live data
docker compose build --build-arg PUBLIC_API_BASE=http://localhost:8000 frontend

# Start nginx
docker compose up frontend -d
```

Or in CI/CD:

```bash
# Step 1: Start backend
docker compose up backend -d
sleep 10  # wait for healthcheck

# Step 2: Build frontend (fetches catalog data at build time)
docker compose build \
  --build-arg PUBLIC_API_BASE=http://localhost:8000 \
  frontend

# Step 3: Deploy
docker compose up -d
```

---

## Local Development

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -e .[dev]
cp .env.example .env         # set CYBERFYX_JWT_SECRET_KEY
alembic -c alembic/alembic.ini upgrade head
python -m app.db.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend-astro
cp .env.example .env         # PUBLIC_API_BASE=http://localhost:8000
npm install
npm run dev                  # starts on http://localhost:4321
```

### Tests

```bash
cd backend
pytest                        # all tests
pytest tests/test_catalog_api.py -v
pytest tests/test_utm_inquiry.py -v
```

---

## Admin Panel

Access at `/admin`. Requires `CYBERFYX_ENABLE_INTERNAL_API=true` in the backend env.

Login with the `CYBERFYX_BOOTSTRAP_STAFF_EMAIL` / `CYBERFYX_BOOTSTRAP_STAFF_PASSWORD` credentials (created on first seed).

Features:
- List all inquiries with pagination
- Filter by status (new / triaged / responded / closed / spam)
- View full inquiry detail including UTM attribution data
- Update inquiry status

---

## Environment Variables Reference

| Variable | Default | Required | Notes |
|---|---|---|---|
| `CYBERFYX_JWT_SECRET_KEY` | `replace-me` | **Yes** | Use `openssl rand -hex 32` |
| `CYBERFYX_ENVIRONMENT` | `development` | Yes | Set `production` to hide docs |
| `CYBERFYX_DATABASE_URL` | `sqlite:///./cyberfyx.db` | No | Use PostgreSQL URL for prod |
| `CYBERFYX_ENABLE_INTERNAL_API` | `false` | No | Set `true` for admin panel |
| `CYBERFYX_CORS_ORIGINS` | `localhost:4321,...` | No | Add your production domain |
| `CYBERFYX_SMTP_HOST` | _(empty)_ | No | Required for email alerts |
| `CYBERFYX_SMTP_SALES_TO` | `sales@cyberfyx.net` | No | Inquiry destination email |
| `CYBERFYX_BOOTSTRAP_STAFF_EMAIL` | _(empty)_ | No | First admin account |
| `CYBERFYX_BOOTSTRAP_STAFF_PASSWORD` | _(empty)_ | No | First admin password |
| `CYBERFYX_INQUIRY_RATE_LIMIT_COUNT` | `5` | No | Submissions per window |
| `CYBERFYX_INQUIRY_RATE_LIMIT_WINDOW_MINUTES` | `15` | No | Rate limit window |

---

## Production Checklist

- [ ] `CYBERFYX_JWT_SECRET_KEY` is a long random secret
- [ ] `CYBERFYX_ENVIRONMENT=production` (disables `/docs` and `/redoc`)
- [ ] SMTP configured for inquiry email notifications
- [ ] `CYBERFYX_ENABLE_INTERNAL_API=true` if using `/admin`
- [ ] Bootstrap admin credentials set and changed after first login
- [ ] Database backed up (if using SQLite, mount a volume for `*.db`)
- [ ] Outbox worker running (for email delivery)
- [ ] Domain added to `CYBERFYX_CORS_ORIGINS` if deploying to a custom domain

---

## Upgrading / Re-seeding

```bash
# Apply any new migrations
docker compose exec backend alembic -c alembic/alembic.ini upgrade head

# Re-run seed (idempotent — safe to run multiple times)
docker compose exec backend python -m app.db.seed
```
