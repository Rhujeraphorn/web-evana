"""ตั้งค่าเชื่อมต่อฐานข้อมูลและ dependency ของ FastAPI"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

# สร้าง engine เชื่อม PostgreSQL โดยเปิด pre_ping เพื่อตรวจสอบ connection
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# Factory สำหรับสร้าง session ต่อคำร้อง
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """dependency ให้ FastAPI เอา session ไปใช้และปิดเมื่อจบ request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
