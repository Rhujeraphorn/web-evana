EV Journey — Northern Thailand (Next.js + FastAPI)

Overview
- A minimal, clean EV travel planner for four provinces: Chiang Mai, Lamphun, Lampang, Mae Hong Son.
- Stack: Next.js (App Router, TS, Tailwind, Leaflet) + FastAPI + PostgreSQL.
- Brand: white + sky-500, rounded-2xl, soft shadows, minimal UI.

Monorepo Layout
- frontend: Next.js app (App Router)
- backend: FastAPI app + ETL scripts + SQL schema

Quick Start
1) Prerequisites
   - Node 18+, Python 3.10+, PostgreSQL 14+
   - Optional: PostGIS if you want to store polylines as geometry

2) Env
   - Edit `backend/.env` and set `DATABASE_URL` (use driver `postgresql+psycopg://`) and `CSV_BASE_DIR` (Windows path root for CSV/JSON).
   - Optional: set `ALLOWED_ORIGINS` (comma-separated) to restrict CORS in production. Default: http://localhost:3000. Use `*` only for dev.
   - Edit `frontend/.env.local` and set `NEXT_PUBLIC_BACKEND_URL` (default http://localhost:8000).

3) Backend (dev)
   - cd backend
   - python -m venv .venv && .\\.venv\\Scripts\\activate
   - .\.venv\Scripts\activate     
   - pip install -r requirements.txt
   - Initialize schema:
     - Without psql: `python scripts/init_db.py`
     - With psql: `psql -U postgres -d evjourney -f sql/ddl.sql`
   - python -m uvicorn app.main:app --reload --port 8000

4) ETL (optional for demo)
   - Ensure CSV/JSON paths exist (see Context section). Adjust `CSV_BASE_DIR` to match your drive.
   - Run:
     - python etl/import_provinces.py
     - python etl/import_pois.py
     - python etl/import_chargers.py
     - python etl/import_agents.py
     - python etl/import_activities.py   
     - python etl/import_foods.py
     - python etl/import_cafes.py
     - python etl/import_hotels.py

5) Demo data (SQL seed)
   - After you create the schema (`sql/ddl.sql`), load a small demo dataset that includes 4 provinces, a Chiang Mai sample trip, and a few POIs:
     - `psql -U postgres -d evjourney -f backend/sql/seed_demo.sql`
   - If you need PostGIS for polylines, make sure the extension is available (the DDL creates it).
   - For production, prefer creating your own dataset via ETL or `backend/sql/seed_prod_template.sql` (idempotent, no TRUNCATE) with real data and PostGIS enabled.

5) Frontend (dev)
   - cd frontend
   - npm install
   - npm run dev
   - Open http://localhost:3000

Production
- Frontend: `npm run build && npm run start`
- Backend: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

Deployment checklist (EC2)
- Env/Secrets: ตั้งค่า `backend/.env` (`DATABASE_URL`, `CSV_BASE_DIR`, `PORT`) และ `frontend/.env.local` (`NEXT_PUBLIC_BACKEND_URL` เป็น URL สาธารณะ) — ห้าม commit ไฟล์จริง
- Database: ใช้ PostgreSQL เปิด security group เฉพาะ IP ของแอป
- CORS: ตรวจ `app/main.py` 
- Run app:
  - Backend: `pip install -r requirements.txt` แล้ว `uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Frontend: `npm ci && npm run build && npm run start` (หรือรันผ่าน PM2/systemd)
- Reverse proxy/SSL: ใช้ Nginx/ALB ทำ HTTPS แล้ว proxy ไป backend (8000) และ frontend (3000/3001)
- ETL: รันสคริปต์นำเข้าข้อมูลตาม README (รวม `etl/import_activities.py`) บนเครื่องที่เข้าถึงไฟล์ CSV/GeoJSON
- Static/media: รูปจาก URL ภายนอกใช้ได้ แต่ถ้าโฮสต์เองควรเก็บที่ S3/CloudFront
- Hardening: ปิด debug, จำกัดพอร์ต/ไฟร์วอลล์, สำรอง DB, ตั้ง health check (เช่น ปิดหรือจำกัดสิทธิ์ `/docs`)

Notes
- App Router uses SSR for search, SSG for province pages.
- Frontend `/api/*` proxies to backend `NEXT_PUBLIC_BACKEND_URL`.
- Map uses Leaflet with dynamic import to avoid SSR issues.

Definition of Done (tracking)
- Search shows Agent cards and timeline (stub data OK initially)
- Chargers/Attractions/Food/Cafes/Hotels index → province → detail routes scaffolded
- Google Maps links work for single point and multi-point
- Lighthouse Perf/Accessibility ≥ 85 (target after polishing)
- README includes dev+prod + ETL steps
