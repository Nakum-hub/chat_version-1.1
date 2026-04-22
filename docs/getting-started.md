# Getting Started

Follow these steps to get the Cyberfyx project (both backend and frontend) running locally on your machine.

## Prerequisites

- **Python**: 3.12+ (managed with `pyenv` or `conda` recommended)
- **Node.js**: 20.x+ (managed with `nvm` or `pnpm` recommended)
- **Git**: For version control.

---

## Quick Start via Helper Scripts

Run from the repository root:

```bash
./runall.sh
```

This starts the local development stack. To stop everything started by the script:

```bash
./kill.sh
```

---

## 1. Backend Setup

The backend handles the data API and inquiry processing.

1. **Navigate to the backend folder**:
   ```bash
   cd backend
   ```
2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
   ```
3. **Install dependencies**:
   ```bash
   pip install -e .[dev]
   ```
4. **Initialize the database**:
   ```bash
   # Run migrations
   alembic -c alembic/alembic.ini upgrade head

   # Seed reference data
   python -m app.db.seed
   ```
5. **Start the API server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The API will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 2. Frontend Setup

The frontend is the user-facing static site.

1. **Navigate to the frontend folder**:
   ```bash
   cd frontend-astro
   ```
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Configure environment**:
   Copy `.env.example` to `.env` and ensure `PUBLIC_API_BASE` points to your local backend:
   ```bash
   cp .env.example .env
   # Edit .env: PUBLIC_API_BASE=http://localhost:8000
   ```
4. **Start the development server**:
   ```bash
   npm run dev
   ```
   The website will be available at [http://localhost:4321](http://localhost:4321).

### Frontend Script Reference

Run these from `frontend-astro/`:

- `npm run dev`: Starts the local Astro development server.
- `npm run build`: Runs Astro checks and builds production output.
- `npm run preview`: Serves the production build locally.
- `npm run astro -- <args>`: Passes commands directly to the Astro CLI.

---

## 3. End-to-End Test

To verify everything is working:

1. Open the website in your browser ([http://localhost:4321](http://localhost:4321)).
2. Navigate to the **Contact** page.
3. Fill out the form and submit.
4. Check the backend logs for a successful inquiry submission (`POST /api/v1/public/inquiries` with a 201 status).

---

## 4. Running the Worker (Optional)

To process background tasks like email notifications, start the outbox worker:

```bash
cd backend
# With venv active
python -m app.worker
```
