# Backend Integration Summary

## ✅ What's Already Integrated

### 1. **Contact Form Integration**
- **Location**: [frontend-astro/src/scripts/contact-form.ts](frontend-astro/src/scripts/contact-form.ts)
- **How it works**:
  - Form submission POSTs to `/api/v1/public/inquiries`
  - Captures: name, email, phone, interest, message, UTM parameters
  - Tracks: referrer, source page, client IP, user agent
  - Fallback: If API fails, shows email address to send to manually

### 2. **Contact Profile Loading**
- **Location**: [frontend-astro/src/lib/api.ts](frontend-astro/src/lib/api.ts)
- **How it works**:
  - `fetchContactProfile()` loads contact info at build time
  - Fetches from `/api/v1/public/site/contact-profile`
  - Returns: sales email/phone, office locations, interest options
  - Used by: Contact form to populate interest dropdown

### 3. **API Configuration**
- **Frontend files**:
  - [frontend-astro/.env](frontend-astro/.env) - Configuration file (created)
  - [frontend-astro/astro.config.mjs](frontend-astro/astro.config.mjs) - Vite proxy config
  - [frontend-astro/src/layouts/BaseLayout.astro](frontend-astro/src/layouts/BaseLayout.astro) - Meta tag injection

- **Environment variables**:
  - `PUBLIC_API_BASE`: API endpoint URL (leave empty for same-origin proxy)
  - `API_PROXY_TARGET`: Dev server proxy target

### 4. **Backend API Endpoints**
All endpoints are ready and implemented:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/public/inquiries` | Submit contact form |
| GET | `/api/v1/public/site/contact-profile` | Get contact info & interests |
| GET | `/api/v1/public/site/search-index` | Get search data |
| GET | `/api/v1/public/solution-tracks/{slug}` | Get solution track details |

## 🚀 How to Run (Development)

### Terminal 1: Backend
```bash
cd backend
pip install -r requirements.txt  # or use poetry if set up
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend-astro
npm install
npm run dev
```

**Result**: Frontend dev server runs on `http://localhost:3000` with `/api` proxied to backend at `http://127.0.0.1:8000`

## 🐳 How to Run (Docker)

```bash
docker-compose up
```

This starts:
- Backend FastAPI on `http://localhost:8000`
- Frontend Astro on `http://localhost:3000`
- Nginx proxy handling `/api` requests to backend

## 📝 What Happens When User Submits Contact Form

1. **Form loads**: `loadInterestOptions()` fetches contact profile from backend
2. **Interest dropdown populated** with options from backend
3. **User fills form**: name, email, phone, interest, message
4. **Submit clicked**: Form POSTs inquiry to `/api/v1/public/inquiries`
5. **Backend processes**: Validates data, stores in database, fires outbox event
6. **Response returned**: Success message shown or error if API fails
7. **Fallback**: If API call fails after 6 seconds, shows email to send to manually

## 🔧 Configuration

### For Development (Local Testing)
Edit [frontend-astro/.env](frontend-astro/.env):
```
PUBLIC_API_BASE=http://127.0.0.1:8000
API_PROXY_TARGET=http://127.0.0.1:8000
```

### For Production (Docker/Nginx Setup)
Edit [frontend-astro/.env](frontend-astro/.env):
```
PUBLIC_API_BASE=
API_PROXY_TARGET=http://backend:8000
```
- Empty `PUBLIC_API_BASE` means client requests proxy through same-origin (`/api` → backend)
- `API_PROXY_TARGET` used only by dev server

## ✅ Verification Checklist

- [x] Backend API endpoints implemented in `/backend/app/api/public/`
- [x] CORS middleware configured in [backend/app/main.py](backend/app/main.py)
- [x] Frontend contact form submission handler in [frontend-astro/src/scripts/contact-form.ts](frontend-astro/src/scripts/contact-form.ts)
- [x] API client utilities in [frontend-astro/src/lib/api.ts](frontend-astro/src/lib/api.ts)
- [x] Environment configuration in [frontend-astro/.env](frontend-astro/.env)
- [x] Astro proxy config in [frontend-astro/astro.config.mjs](frontend-astro/astro.config.mjs)
- [x] Contact profile meta tag in [frontend-astro/src/layouts/BaseLayout.astro](frontend-astro/src/layouts/BaseLayout.astro)

## 📚 Endpoint Details

### POST `/api/v1/public/inquiries`
**Request**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-234-567-8900",
  "interest": "Cybersecurity Assessment",
  "message": "I need help...",
  "source_page": "/services/cybersecurity",
  "referrer_url": "https://google.com",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "security"
}
```

**Response** (200):
```json
{
  "id": "uuid-string",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### GET `/api/v1/public/site/contact-profile`
**Response**:
```json
{
  "sales_email": "sales@cyberfyx.com",
  "sales_phone": "+1-555-0100",
  "office_regions": ["US", "EU"],
  "interest_options": [
    {"id": 1, "name": "Cybersecurity Assessment"},
    {"id": 2, "name": "Penetration Testing"},
    ...
  ]
}
```

## 🐛 Troubleshooting

**Issue**: Contact form says "Network error" but backend is running
- Solution: Check `PUBLIC_API_BASE` in `.env` matches backend URL

**Issue**: Interest dropdown is empty
- Solution: Backend `/api/v1/public/site/contact-profile` endpoint may be failing. Check backend logs.

**Issue**: Form submission succeeds but no email received
- Solution: Backend may need email service configured (check `backend/app/core/config.py` for email settings)

**Issue**: CORS errors in browser console
- Solution: Check [backend/app/main.py](backend/app/main.py) - CORS middleware should allow frontend origin

## 📖 Related Files

- Backend docs: [docs/backend.md](docs/backend.md)
- Frontend docs: [docs/frontend.md](docs/frontend.md)
- Architecture: [docs/architecture.md](docs/architecture.md)
- Deployment: [DEPLOYMENT.md](DEPLOYMENT.md)
