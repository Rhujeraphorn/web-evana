import os
import re
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

# Ensure project root (backend/) is on sys.path when running as a script
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import CSV_BASE_DIR, DATABASE_URL

engine = create_engine(DATABASE_URL)

PROVINCE_PREFIX = {
    'chiang-mai': 'chiangmai',
    'lampang': 'lampang',
    'lamphun': 'lamphun',
    'mae-hong-son': 'maehongson',
}


def slugify(s: str) -> str:
    s = (s or '').lower()
    s = re.sub(r"\s+", '-', s)
    s = re.sub(r"[^a-z0-9\-]", '', s)
    s = re.sub(r"-+", '-', s).strip('-')
    return s or 'item'


def get_province_id(conn, slug: str) -> int:
    row = conn.execute(text("SELECT id FROM provinces WHERE slug_en = :s"), { 's': slug }).first()
    if not row:
        raise RuntimeError(f"Province not found: {slug}")
    return row[0]


def find_file(prefix: str, filename: str) -> str:
    candidates = [
        os.path.join(CSV_BASE_DIR, prefix, 'data', filename),
        os.path.join(CSV_BASE_DIR, 'data', prefix, filename),
        os.path.join(CSV_BASE_DIR, 'data', prefix.capitalize(), filename),
        os.path.join(CSV_BASE_DIR, prefix.capitalize(), filename),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return ''


def load_csv(path: str) -> pd.DataFrame:
    last_exc = None
    for enc in ('utf-8-sig', 'utf-8', 'cp874'):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as exc:
            last_exc = exc
    if last_exc:
        raise last_exc
    raise RuntimeError('Unable to read chargers CSV at ' + path)


with engine.begin() as conn:
    for slug, prefix in PROVINCE_PREFIX.items():
        fname = f'{prefix}_charger.csv'
        path = find_file(prefix, fname)
        if not path:
            print('Missing charger CSV for', slug)
            continue
        pid = get_province_id(conn, slug)
        # remove old records for this province before inserting fresh data
        conn.execute(text("DELETE FROM chargers WHERE province_id = :pid"), {'pid': pid})
        df = load_csv(path)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df.columns = [str(c).strip().lower() for c in df.columns]
        if 'latitude' in df.columns:
            df = df.rename(columns={'latitude': 'lat'})
        if 'longitude' in df.columns:
            df = df.rename(columns={'longitude': 'lon'})
        if 'power_kw' in df.columns:
            df = df.rename(columns={'power_kw': 'kw'})
        if 'name' not in df.columns:
            print('Skip (no name):', path)
            continue
        df['name'] = df['name'].astype(str).str.strip()
        df['type'] = df.get('type', '').astype(str).str.strip().str.upper()
        df['kw'] = pd.to_numeric(df.get('kw'), errors='coerce')
        df['capacity'] = pd.to_numeric(df.get('capacity'), errors='coerce')
        df['lat'] = pd.to_numeric(df.get('lat'), errors='coerce')
        df['lon'] = pd.to_numeric(df.get('lon'), errors='coerce')
        if 'brand' in df.columns:
            df['brand'] = df['brand'].fillna('')
        else:
            df['brand'] = ''
        if 'address' in df.columns:
            df['address'] = df['address'].fillna('')
        elif 'district' in df.columns:
            df['address'] = df['district'].fillna('')
        else:
            df['address'] = ''
        if 'id' not in df.columns:
            df['id'] = [f"{slugify(n)}-{round(lat,4)}-{round(lon,4)}" for n, lat, lon in zip(df['name'], df['lat'], df['lon'])]
        df = df[df['lat'].notna() & df['lon'].notna()]
        rows = df.to_dict(orient='records')
        for r in rows:
            ctype = r.get('type')
            if ctype not in ('AC', 'DC'):
                ctype = None
            capacity = r.get('capacity')
            capacity_val = int(capacity) if isinstance(capacity, (int, float)) and capacity == capacity else None
            conn.execute(text("""
              INSERT INTO chargers(id,name,type,kw,capacity,lat,lon,province_id,brand,address)
              VALUES (:id,:name,:type,:kw,:capacity,:lat,:lon,:province_id,:brand,:address)
              ON CONFLICT (id) DO UPDATE SET 
                name=EXCLUDED.name, type=EXCLUDED.type, kw=EXCLUDED.kw, capacity=EXCLUDED.capacity,
                lat=EXCLUDED.lat, lon=EXCLUDED.lon, province_id=EXCLUDED.province_id, brand=EXCLUDED.brand, address=EXCLUDED.address
            """), {
                'id': r['id'],
                'name': r['name'],
                'type': ctype,
                'kw': float(r['kw']) if r.get('kw') == r.get('kw') else None,
                'capacity': capacity_val,
                'lat': float(r['lat']),
                'lon': float(r['lon']),
                'province_id': pid,
                'brand': r.get('brand') or '',
                'address': r.get('address') or '',
            })
        print('Upserted chargers for', slug, len(rows))
