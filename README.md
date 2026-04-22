# Cyberfyx Website

Building the next-generation website for Cyberfyx with a high-performance **Astro 4.x** frontend and a robust **FastAPI** backend.

## Overview

The Cyberfyx website project is a secure, decoupled web application. It delivers a blazing-fast, SEO-optimized user experience while maintaining a professional and administrative-ready backend.

- **🚀 Frontend**: Built with [Astro](https://astro.build/) for high-end Core Web Vitals and SEO.
- **⚙️ Backend**: Built with [FastAPI](https://fastapi.tiangolo.com/) for reliable data handling and lead routing.

## Navigation

- **[Architecture](docs/architecture.md)**: Explore the high-level system design.
- **[Backend Guide](docs/backend.md)**: Deep dive into the API, database, and background workers.
- **[Frontend Guide](docs/frontend.md)**: Details on the design system, animations, and Astro configuration.
- **[Getting Started](docs/getting-started.md)**: Step-by-step instructions for local development.

## Project Structure

```text
/                   # Root project folder
├── backend/        # FastAPI application (FastAPI, SQLAlchemy, Alembic)
├── frontend-astro/ # Astro static site generator (Astro, Vanilla TS, CSS)
├── docs/           # Comprehensive documentation suite
└── README.md       # Project entry point
```

## Quick Start

To get up and running quickly:
1. **Backend**: `cd backend && pip install -e .[dev] && uvicorn app.main:app --reload`
2. **Frontend**: `cd frontend-astro && npm install && npm run dev`

## One-command local run (script-based)

Use these helper scripts from the repository root to run the full local stack:

- `./runall.sh` — starts backend + frontend local development processes.
- `./kill.sh` — stops processes started by `./runall.sh`.

## Run Scripts

The frontend now has standard npm scripts you can use throughout development:

- `npm run dev` — start the Astro dev server.
- `npm run build` — run checks and build a production bundle.
- `npm run preview` — preview the production build locally.
- `npm run astro -- <args>` — run Astro CLI commands.

For a full backend/frontend local workflow (including migrations and seed data), use the commands in **[Getting Started](docs/getting-started.md)**.

## Root `npm start`

You can also start the full local development stack from the repository root with:

`npm start`

This root command installs the backend and frontend dependencies, runs backend migrations, seeds the database, and starts both the FastAPI backend and Astro frontend. If the default ports are already in use, it automatically selects the next available local ports and prints the active URLs.
