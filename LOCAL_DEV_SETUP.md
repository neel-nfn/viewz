# Viewz Local Development Setup

This guide walks you through running the full Viewz stack locally on macOS.

## Prerequisites

- Docker Desktop installed and running
- Python 3.11+ installed
- Node.js 18+ installed (use `nvm` if needed)
- PostgreSQL client tools (optional, for manual DB access)

## Quick Start (Three Terminal Tabs)

### Terminal 1: Database (Postgres in Docker)

```bash
cd /Users/mddeloarhossain/Desktop/Viewz-Workspace

# Start Postgres container
docker compose up -d

# Verify it's running
docker ps

# Check logs if needed
docker compose logs -f db
```

**Expected output**: Container `viewz_db` should be running and healthy.

---

### Terminal 2: Backend (FastAPI)

```bash
cd /Users/mddeloarhossain/Desktop/Viewz-Workspace/backend

# Create and activate virtual environment (first time only)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (first time only)
pip install -U pip
pip install -r requirements.txt

# Copy the local environment template
cp .env.local .env

# IMPORTANT: Edit .env and add your Google OAuth credentials
# GOOGLE_CLIENT_ID=your_actual_client_id
# GOOGLE_CLIENT_SECRET=your_actual_client_secret

# Run database migrations (first time only)
alembic upgrade head

# Start the backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output**: 
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test backend health**:
```bash
# In a new terminal tab
curl http://localhost:8000/api/v1/health
```

---

### Terminal 3: Frontend (Vite)

```bash
cd /Users/mddeloarhossain/Desktop/Viewz-Workspace/frontend

# Install dependencies (first time only)
npm install

# Start the dev server
npm run dev
```

**Expected output**:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## Verify Everything is Running

### Browser URLs to Test

1. **Landing Page**: http://localhost:5173/
2. **Dashboard (Today)**: http://localhost:5173/app
3. **Legacy Dashboard**: http://localhost:5173/app/dashboard
4. **Workflow Kanban**: http://localhost:5173/app/workflow
5. **Analytics**: http://localhost:5173/app/analytics
6. **Research**: http://localhost:5173/app/research
7. **Settings**: http://localhost:5173/app/settings

### API Health Checks

```bash
# Backend health
curl -sS http://localhost:8000/api/v1/health | jq

# Should return:
# {
#   "status": "healthy",
#   "timestamp": "2025-11-02T...",
#   "oauth_client": "configured",
#   "sched_enabled": false,
#   ...
# }

# Auth endpoint (should return 401 when not logged in)
curl -sS -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/v1/auth/me
# Expected: 401
```

---

## Google OAuth Setup

To enable YouTube channel connection:

1. **Google Cloud Console**: https://console.cloud.google.com/
2. Create a new project or use existing
3. Enable **YouTube Data API v3**
4. Create OAuth 2.0 credentials:
   - Application type: **Web application**
   - Authorized redirect URIs: `http://localhost:8000/api/v1/auth/callback`
5. Copy the **Client ID** and **Client Secret** to `backend/.env`:
   ```
   GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=xxxxx
   ```
6. Restart the backend server

---

## Troubleshooting

### Database won't start
```bash
# Check Docker is running
docker ps

# View database logs
docker compose logs db

# Reset database (WARNING: deletes all data)
docker compose down -v
docker compose up -d
```

### Backend errors
```bash
# Check if Postgres is reachable
psql postgresql://viewz:viewzpass@localhost:5432/viewz -c "SELECT 1"

# Check backend logs for errors
# Backend runs with --reload so it auto-restarts on code changes

# Reset migrations (WARNING: deletes all data)
alembic downgrade base
alembic upgrade head
```

### Frontend errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if backend is reachable
curl http://localhost:8000/api/v1/health
```

### Port conflicts
```bash
# If port 5432 (Postgres) is in use:
docker compose down
# Edit docker-compose.yml to use a different port, e.g., "5433:5432"

# If port 8000 (Backend) is in use:
# Run backend on different port:
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
# Update frontend/.env.local: VITE_API_BASE_URL=http://localhost:8001

# If port 5173 (Frontend) is in use:
npm run dev -- --port 5174
```

---

## Stopping Everything

```bash
# Terminal 1 (Database)
docker compose down

# Terminal 2 (Backend)
# Press Ctrl+C

# Terminal 3 (Frontend)
# Press Ctrl+C
```

---

## Demo Mode (No Backend Required)

If you just want to test the UI without setting up the backend:

```bash
cd /Users/mddeloarhossain/Desktop/Viewz-Workspace/frontend

# Frontend already has demo mode enabled via .env.local:
# VITE_DEMO_MODE=1
# VITE_DATA_SOURCE=demo

npm run dev
```

Then visit:
- http://localhost:5173/demo (Pipeline demo)
- http://localhost:5173/app/workflow (Kanban board)
- http://localhost:5173/app (Dashboard Today)

---

## Next Steps

1. **Connect a YouTube channel**: Visit http://localhost:5173/app/settings/channels
2. **Create your first task**: Visit http://localhost:5173/app/workflow
3. **View analytics**: Visit http://localhost:5173/app/analytics
4. **Try AI assist**: Press `G` on any page or click the AI icon in the sidebar

---

## Production Deployment

For production deployment instructions, see:
- `docs/beta/DEPLOYMENT.md` (coming soon)
- Or use the Dokploy setup from Batch-10

---

## Support

- **Issues**: Create an issue in the repository
- **Feedback**: Visit http://localhost:5173/public/feedback
- **Documentation**: See `docs/beta/` directory

