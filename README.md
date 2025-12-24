# EVANA Project
EV Journey for Northern Thailand (Next.js + FastAPI).

## Table of Contents
- Overview
- Features
- Tech Stack
- Project Structure
- Getting Started
- Demo Data
- License

## Overview
EVANA is a lightweight EV travel planner for four provinces in Northern Thailand.
It provides trip recommendations, POI discovery, and charger locations with a clean UI.

## Features
- Trip search with detailed timelines
- Chargers, attractions, food, cafes, and hotels by province
- Map visualization with Google Maps handoff
- Embedded demo data for offline-friendly dev runs

## Tech Stack
- Frontend: Next.js (App Router), TypeScript, Tailwind, Leaflet
- Backend: FastAPI, SQLAlchemy
- Database: PostgreSQL (optional for demo)

## Project Structure
High-level folders:
```
backend/   # FastAPI app, schemas, routers, demo data
frontend/  # Next.js app (App Router)
data/      # Route aggregates and demo assets
nginx/     # Reverse proxy config
```

Directory tree (condensed):
```
.
|-- backend/
|   |-- app/
|   |   |-- routers/
|   |   |   |-- agents.py
|   |   |   |-- chargers.py
|   |   |   |-- pois.py
|   |   |   |-- routes.py
|   |   |   `-- search.py
|   |   |-- config.py
|   |   |-- db.py
|   |   |-- demo_data.py
|   |   |-- main.py
|   |   |-- models.py
|   |   `-- schemas.py
|   |-- etl/
|   |   |-- import_activities.py
|   |   |-- import_agents.py
|   |   |-- import_cafes.py
|   |   |-- import_chargers.py
|   |   |-- import_foods.py
|   |   |-- import_hotels.py
|   |   |-- import_pois.py
|   |   `-- import_provinces.py
|   |-- scripts/
|   |   |-- bootstrap.py
|   |   `-- init_db.py
|   |-- sql/
|   |   |-- ddl.sql
|   |   |-- seed_demo.sql
|   |   `-- seed_prod_template.sql
|   |-- Dockerfile
|   `-- requirements.txt
|-- data/
|   `-- routes/
|       |-- Chiangmai_routes_all.geojson
|       |-- Chiangmai_routes_all.json
|       |-- Lampang_routes_all.geojson
|       |-- Lampang_routes_all.json
|       |-- Lamphun_routes.geojson
|       |-- Lamphun_routes.json
|       |-- Maehongson_all.geojson
|       `-- Maehongson_all.json
|-- frontend/
|   |-- app/
|   |-- components/
|   |-- lib/
|   |-- public/
|   |-- styles/
|   |-- Dockerfile
|   |-- next.config.mjs
|   |-- nginx.conf
|   |-- package.json
|   |-- postcss.config.js
|   |-- tailwind.config.ts
|   `-- tsconfig.json
|-- nginx/
|   `-- default.conf
|-- .env
|-- .gitignore
|-- docker-compose.yml
|-- LICENSE
`-- README.md
```

Note: This tree omits local/dev artifacts such as `.venv`, `node_modules`, `.next`, `__pycache__`, and `.vscode`.

## Getting Started
### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+ (optional for demo)

### Install Dependencies
Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Frontend
```powershell
cd frontend
npm install
```

### Run (Development)
Backend
```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Frontend
```powershell
cd frontend
npm run dev
```

Open http://localhost:3000

## Demo Data
Demo POIs and routes are embedded in `backend/app/demo_data.py`, so the app can
serve data even if PostgreSQL is not available. If you want to use the database
instead, you can seed it with:
```bash
psql -U postgres -d evjourney -f backend/sql/seed_demo.sql
```

## License
MIT. See `LICENSE`.
