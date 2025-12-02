"""จุดเริ่มต้นของ FastAPI ตั้ง middleware/routers และ healthcheck"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from .routers import search, agents, chargers, routes, pois
from . import config

app = FastAPI(title='EV Journey API')

# ตั้งค่า CORS จาก env: ถ้าเจอ * จะเปิดกว้าง แต่ตัด credential ออก
allow_all = '*' in config.ALLOWED_ORIGINS
cors_origins = ['*'] if allow_all else config.ALLOWED_ORIGINS
cors_allow_credentials = not allow_all

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials,
    allow_methods=['*'],
    allow_headers=['*'],
)

# บีบอัด response JSON ที่ใหญ่เกิน 1KB ให้โหลดเร็วขึ้น
app.add_middleware(GZipMiddleware, minimum_size=1024)

# รวม router ตามโดเมนของข้อมูล
app.include_router(search.router)
app.include_router(agents.router)
app.include_router(chargers.router)
app.include_router(routes.router)
app.include_router(pois.router)

@app.get('/api/health')
def health():
    """เช็กว่าเซิร์ฟเวอร์ยังทำงาน"""
    return { 'ok': True }
