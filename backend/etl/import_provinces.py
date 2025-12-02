"""นำเข้ารายชื่อจังหวัดจากค่าคงที่ใน config ลงฐานข้อมูล"""
from app.config import PROVINCE_SEED, DATABASE_URL
from sqlalchemy import create_engine, text

engine = create_engine(DATABASE_URL)

# upsert จังหวัดให้ครบ (มี ON CONFLICT กันซ้ำ)
with engine.begin() as conn:
    for slug, name in PROVINCE_SEED:
        conn.execute(text("""
            INSERT INTO provinces(slug_en, name_th)
            VALUES (:slug, :name)
            ON CONFLICT (slug_en) DO UPDATE SET name_th = EXCLUDED.name_th
        """), { 'slug': slug, 'name': name })
print('Provinces upserted:', len(PROVINCE_SEED))
