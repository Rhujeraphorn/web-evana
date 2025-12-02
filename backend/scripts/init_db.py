"""สคริปต์สร้าง schema ตามไฟล์ sql/ddl.sql"""
from sqlalchemy import create_engine
from pathlib import Path
import os

def main():
    """เชื่อม DB แล้ว execute DDL"""
    db_url = os.getenv('DATABASE_URL', 'postgresql+psycopg://postgres:postgres@localhost:5432/evjourney')
    engine = create_engine(db_url)
    sql_path = Path(__file__).resolve().parent.parent / 'sql' / 'ddl.sql'
    sql = sql_path.read_text(encoding='utf-8')
    with engine.begin() as conn:
        conn.exec_driver_sql(sql)
    print('Applied DDL from', sql_path)

if __name__ == '__main__':
    main()
