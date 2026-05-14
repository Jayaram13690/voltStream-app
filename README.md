# VoltStream

VoltStream is a prosumer energy dashboard: a React SPA with Tailwind and Recharts, backed by FastAPI with REST + WebSocket live telemetry, SQLite for local development, and PostgreSQL when you run the stack with Docker.

## Repository layout

- `frontend/` — Vite + React application
- `backend/` — FastAPI service (`app/` package) and **Python virtual environment in `backend/venv/`** (create locally; it is gitignored)
- `docker-compose.yml` — Postgres, API, and static UI (nginx)

## Local development

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Defaults use SQLite at `backend/voltstream.db`. The first boot seeds demo devices and billing rows.

### Frontend

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

With the default empty `VITE_API_URL`, the Vite dev server proxies `/api`, `/ws`, and `/health` to `http://127.0.0.1:8000` (see `frontend/vite.config.js`). Point `VITE_API_URL` at the API when you serve the built UI separately.

### Tests

```powershell
cd backend
.\venv\Scripts\python -m pytest
```

## Docker

```powershell
docker compose up --build
```

- API: `http://localhost:8000` (`/health`, `/api/v1/...`, WebSocket `/ws/live-energy`)
- UI (nginx): `http://localhost:8080`
- Postgres: `localhost:5432` (`voltstream` / `voltstream`)

Compose injects `DATABASE_URL` for Postgres and widens `CORS_ORIGINS` for the static bundle and dev origins.

## API surface (MVP)

- `GET /api/v1/dashboard/live`
- `GET /api/v1/analytics/history?period=daily|weekly|monthly`
- `GET /api/v1/devices` and `PATCH /api/v1/devices/{id}` with JSON `{ "status": "on" | "off" }`
- `GET /api/v1/billing/summary`
- `WS /ws/live-energy` — JSON snapshots every ~2 seconds (send any text periodically to keep the handler responsive)

## Notes

- Live metrics are simulated server-side for the MVP; swap `app/websocket/live_energy.py` and the dashboard service for real meter feeds when you integrate hardware.
- **UI & Theming**: The application features a custom **Bento Box UI** with a collapsible sidebar rail. It uses the modern **Ranade** font.
- **Color Palette**: Features high-contrast Neon Pink (`#ff3366`) and Electric Green (`#00e676`) accents.
- **Light/Dark Mode**: The application includes full support for Light and Dark modes, which can be toggled via the Settings page.
