import os
import json
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

HERE = os.path.dirname(__file__)
PROJECT_ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
REPO_FOOD_DIR = os.path.join(PROJECT_ROOT, 'data', 'food')

PROVINCE_PREFIX = {
    'chiang-mai': 'chiangmai',
    'lamphun': 'lamphun',
    'lampang': 'lampang',
    'mae-hong-son': 'maehongson',
}


def slugify(s: str) -> str:
    s = (s or '').lower()
    s = re.sub(r"\s+", '-', s)
    s = re.sub(r"[^a-z0-9\-]", '', s)
    s = re.sub(r"-+", '-', s).strip('-')
    return s or 'item'


def province_id(conn, slug: str) -> int:
    r = conn.execute(text('SELECT id FROM provinces WHERE slug_en=:s'), { 's': slug }).first()
    if not r:
        raise RuntimeError('Province missing: ' + slug)
    return r[0]


def find_file(prefix: str, filename: str) -> str:
    candidates = [
        os.path.join(CSV_BASE_DIR, prefix, 'data', filename),
        os.path.join(CSV_BASE_DIR, prefix.capitalize(), 'data', filename),
        os.path.join(CSV_BASE_DIR, 'data', prefix, filename),
        os.path.join(CSV_BASE_DIR, 'data', prefix.capitalize(), filename),
        os.path.join(CSV_BASE_DIR, prefix.capitalize(), filename),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    repo_path = os.path.join(REPO_FOOD_DIR, filename)
    return repo_path if os.path.exists(repo_path) else ''


def load_csv(path: str) -> pd.DataFrame:
    last_exc = None
    for enc in ('utf-8-sig', 'utf-8', 'cp874'):
        try:
            return pd.read_csv(path, encoding=enc, engine='python')
        except Exception as exc:
            last_exc = exc
    if last_exc:
        raise last_exc
    raise RuntimeError('Unable to read foods CSV at ' + path)


with engine.begin() as conn:
    frames = []
    for slug, prefix in PROVINCE_PREFIX.items():
        fname = f'{prefix}_food.csv'
        path = find_file(prefix, fname)
        if not path:
            print('Missing food CSV for', slug)
            continue
        f = load_csv(path)
        f['province_slug'] = slug
        frames.append(f)
    if not frames:
        print('No food CSV files found')
        raise SystemExit(0)
    df = pd.concat(frames, ignore_index=True)
    if 'latitude' in df.columns:
        df = df.rename(columns={'latitude': 'lat'})
    if 'longitude' in df.columns:
        df = df.rename(columns={'longitude': 'lon'})
    if 'name_th' not in df.columns and 'name' in df.columns:
        df['name_th'] = df['name']
    df['name_th'] = df['name_th'].astype(str).str.strip()
    if 'name_en' in df.columns:
        df['name_en'] = df['name_en'].fillna('')
    else:
        df['name_en'] = ''
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    open_series = (df['open'] if 'open' in df.columns else pd.Series([''] * len(df))).astype(str).str.replace('\r', '', regex=False).str.replace('\n', '', regex=False).str.strip().str.strip('"')
    close_series = (df['close'] if 'close' in df.columns else pd.Series([''] * len(df))).astype(str).str.replace('\r', '', regex=False).str.replace('\n', '', regex=False).str.strip().str.strip('"')
    df['open_hours_json'] = [
        {'open': o, 'close': c} if (o or c) else None
        for o, c in zip(open_series, close_series)
    ]
    if 'price_range' in df.columns:
        df['price_range'] = df['price_range'].fillna('')
    else:
        df['price_range'] = ''
    if 'id' not in df.columns:
        df['id'] = [f"{slugify(n)}-{round(lat,4)}-{round(lon,4)}" for n, lat, lon in zip(df['name_th'], df['lat'], df['lon'])]
    df = df[df['province_slug'].notna() & df['lat'].notna() & df['lon'].notna()]
    pid_cache = {slug: province_id(conn, slug) for slug in sorted(df['province_slug'].unique())}
    # remove old records for these provinces before inserting fresh data
    for pid in pid_cache.values():
        conn.execute(text("DELETE FROM foods WHERE province_id = :pid"), {'pid': pid})

    for r in df.to_dict(orient='records'):
        slug = r['province_slug']
        conn.execute(text("""
            INSERT INTO foods(id,name_th,name_en,price_range,lat,lon,province_id,open_hours_json)
            VALUES (:id,:name_th,:name_en,:price_range,:lat,:lon,:province_id,:open_hours_json)
            ON CONFLICT (id) DO UPDATE SET name_th=EXCLUDED.name_th, name_en=EXCLUDED.name_en,
              price_range=EXCLUDED.price_range, lat=EXCLUDED.lat, lon=EXCLUDED.lon, province_id=EXCLUDED.province_id,
              open_hours_json=EXCLUDED.open_hours_json
        """), {
            'id': r['id'],
            'name_th': r['name_th'],
            'name_en': r.get('name_en') or '',
            'price_range': r.get('price_range') or '',
            'lat': float(r['lat']),
            'lon': float(r['lon']),
            'province_id': pid_cache[slug],
            'open_hours_json': json.dumps(r.get('open_hours_json')) if r.get('open_hours_json') else None,
        })
    print('Upserted foods:', len(df))
