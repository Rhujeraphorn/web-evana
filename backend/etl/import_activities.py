import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import Session

# Ensure project root (backend/) is on sys.path when running as a script
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import DATABASE_URL
from app.db import get_db
from app.models import Province

engine = create_engine(DATABASE_URL)

PROVINCE_MAP = {
    'CHIANG MAI': 'chiang-mai',
    'LAMPANG': 'lampang',
    'LAMPHUN': 'lamphun',
    'MAE HONG SON': 'mae-hong-son',
}

FILES = [
    ('chiang-mai', r'D:\chiangmai\data\chiangmai_activity.csv'),
    ('lamphun', r'D:\lamphun\data\lamphun_activity.csv'),
    ('lampang', r'D:\lampang\data\lampang_activity.csv'),
    ('mae-hong-son', r'D:\maehongson\data\maehongson_activity.csv'),
]


def load_csv(path: str) -> pd.DataFrame:
    last_exc = None
    for enc in ('utf-8-sig', 'utf-8', 'cp874'):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as exc:
            last_exc = exc
    if last_exc:
        raise last_exc
    raise RuntimeError('Unable to read activities CSV at ' + path)


def slugify(s: str) -> str:
    s = (s or '').lower()
    s = re.sub(r"\s+", '-', s)
    s = re.sub(r"[^a-z0-9\-]", '', s)
    s = re.sub(r"-+", '-', s).strip('-')
    return s or 'activity'


def province_ids(session: Session) -> Dict[str, int]:
    rows = session.execute(select(Province.slug_en, Province.id)).all()
    return {slug: pid for slug, pid in rows}


with engine.begin() as conn:
    session = Session(bind=conn)
    pid_map = province_ids(session)
    for slug, path in FILES:
        if not os.path.exists(path):
            print('Missing activity CSV:', path)
            continue
        df = load_csv(path)
        df.columns = [c.strip().lower() for c in df.columns]
        df = df.rename(columns={'name': 'name_th'})
        if 'lat' not in df.columns or 'lon' not in df.columns:
            print('Skip (missing lat/lon):', path)
            continue
        df['name_th'] = df['name_th'].astype(str).str.strip()
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df = df[df['name_th'].notna() & df['name_th'].ne('') & df['lat'].notna() & df['lon'].notna()]
        pid = pid_map.get(slug)
        if not pid:
            print('Province missing:', slug)
            continue
        # clear existing activities (kind AVT) for this province to avoid duplicates
        conn.execute(text("DELETE FROM attractions WHERE province_id=:pid AND kind='AVT'"), {'pid': pid})
        rows: List[Dict[str, Any]] = df.to_dict(orient='records')
        payload_map: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            lat = float(r['lat'])
            lon = float(r['lon'])
            name = r['name_th']
            rid = f"{slugify(name)}-{round(lat,4)}-{round(lon,4)}"
            payload_map[rid] = {
                'id': rid,
                'name_th': name,
                'name_en': '',
                'kind': 'AVT',
                'lat': lat,
                'lon': lon,
                'province_id': pid,
            }
        payload = list(payload_map.values())
        if payload:
            conn.execute(text("""
                INSERT INTO attractions(id,name_th,name_en,kind,lat,lon,province_id)
                VALUES (:id,:name_th,:name_en,:kind,:lat,:lon,:province_id)
                ON CONFLICT (id) DO NOTHING
            """), payload)
            print(f'Upserted activities for {slug}: {len(payload)}')
