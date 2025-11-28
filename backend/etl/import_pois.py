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

from app.config import CSV_BASE_DIR, DATABASE_URL, PROVINCE_SEED

engine = create_engine(DATABASE_URL)

THAI_KIND_MAP = {
    'แหล่งท่องเที่ยวทางธรรมชาติ': 'NTA',
    'ธรรมชาติ': 'NTA',
    'วัฒนธรรม': 'CTA',
    'วิถีชีวิตความเป็นอยู่ (ชุมชน)': 'CTA',
    'กิจกรรม': 'AVT',
}

THAI_TO_SLUG = { th: slug for slug, th in PROVINCE_SEED }


def slugify(s: str) -> str:
    s = (s or '').lower()
    s = re.sub(r"\s+", '-', s)
    s = re.sub(r"[^a-z0-9\-]", '', s)
    s = re.sub(r"-+", '-', s).strip('-')
    return s or 'item'


def clean_col(name: str) -> str:
    name = name.replace('\ufeff', '').strip()
    name = re.sub(r'^"+|"+$', '', name)
    name = name.replace('""', '"')
    if 'ATT_ID' in name:
        return 'ATT_ID'
    return name


def province_id(conn, slug: str) -> int:
    r = conn.execute(text('SELECT id FROM provinces WHERE slug_en=:s'), { 's': slug }).first()
    if not r:
        raise RuntimeError('Province missing: ' + slug)
    return r[0]


def load_csv(path: str) -> pd.DataFrame:
    last_exc = None
    for enc in ('utf-8-sig', 'utf-8', 'cp874'):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as exc:
            last_exc = exc
    if last_exc:
        raise last_exc
    raise RuntimeError('Unable to read CSV at ' + path)


DATA_CANDIDATES = [
    os.path.join(CSV_BASE_DIR, 'data', 'attraction_all.csv'),
    os.path.join(CSV_BASE_DIR, 'attraction_all.csv'),
    os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'attraction.csv')),
]

csv_path = None
for candidate in DATA_CANDIDATES:
    if os.path.exists(candidate):
        csv_path = candidate
        break

if not csv_path:
    print('Missing attraction CSV. Checked:', DATA_CANDIDATES)
    raise SystemExit(0)

df = load_csv(csv_path)
df.columns = [clean_col(str(c)) for c in df.columns]
required = ['ATT_ID', 'ATT_NAME_TH', 'ATT_LOCATION', 'PROVINCE_NAME_TH']
if not all(col in df.columns for col in required):
    print('CSV missing required columns, aborting')
    raise SystemExit(0)

rows = []
for _, r in df.iterrows():
    try:
        name_th = str(r.get('ATT_NAME_TH') or '').strip()
        if not name_th:
            continue
        loc_str = str(r.get('ATT_LOCATION') or '').strip()
        if ',' not in loc_str:
            continue
        lat_s, lon_s = [p.strip() for p in loc_str.split(',', 1)]
        lat = float(lat_s)
        lon = float(lon_s)
        province_th = str(r.get('PROVINCE_NAME_TH') or '').strip()
        slug = THAI_TO_SLUG.get(province_th)
        if not slug:
            continue
        name_en = str(r.get('ATT_NAME_EN') or '').strip()
        cat_th = str(r.get('ATT_CATEGORY_LABEL') or '').strip()
        kind = THAI_KIND_MAP.get(cat_th, 'CTA')
        raw_id = str(r.get('ATT_ID') or '').strip()
        rid = raw_id
        if not rid or re.search(r'[eE]', rid) or re.search(r'\.', rid):
            base_name = name_en or name_th
            rid = f"{slugify(base_name)}-{round(lat,4)}-{round(lon,4)}"
        subdistrict_th = str(r.get('SUBDISTRICT_NAME_TH') or '').strip()
        district_th = str(r.get('DISTRICT_NAME_TH') or '').strip()
        address_parts = []
        if subdistrict_th:
            address_parts.append(f"ตำบล{subdistrict_th}")
        if district_th:
            address_parts.append(f"อำเภอ{district_th}")
        if province_th:
            address_parts.append(f"จังหวัด{province_th}")
        address_th = ', '.join(address_parts)
        rows.append({
            'id': rid,
            'source_id': raw_id,
            'province_slug': slug,
            'name_th': name_th,
            'name_en': name_en,
            'kind': kind,
            'lat': lat,
            'lon': lon,
            'province_th': province_th,
            'address_th': address_th,
            'district_th': district_th,
            'subdistrict_th': subdistrict_th,
            'type_th': str(r.get('ATT_TYPE_LABEL') or '').strip(),
            'detail_th': str(r.get('ATT_DETAIL_TH') or '').strip(),
            'nearby_location': str(r.get('ATT_NEARBY_LOCATION') or '').strip(),
            'address_road': str(r.get('ATT_ADDRESS_ROAD') or '').strip(),
            'postcode': str(r.get('ATT_POSTCODE') or '').strip(),
            'tel': str(r.get('ATT_TEL') or '').strip(),
            'email': str(r.get('ATT_EMAIL') or '').strip(),
            'start_end': str(r.get('ATT_START_END') or '').strip(),
            'hilight': str(r.get('ATT_HILIGHT') or '').strip(),
            'reward': str(r.get('ATT_REWARD') or '').strip(),
            'suitable_duration': str(r.get('ATT_SUITABLE_DURATION') or '').strip(),
            'market_limitation': str(r.get('ATT_MARKET_LIMITATION') or '').strip(),
            'market_chance': str(r.get('ATT_MARKET_CHANCE') or '').strip(),
            'traveler_pre': str(r.get('ATT_TRAVELER_PRE') or '').strip(),
            'website': str(r.get('ATT_WEBSITE') or '').strip(),
            'facebook': str(r.get('ATT_FACEBOOK') or '').strip(),
            'instagram': str(r.get('ATT_INSTAGRAM') or '').strip(),
            'tiktok': str(r.get('ATT_TIKTOK') or '').strip(),
            'region_th': str(r.get('REGION_NAME_TH') or '').strip(),
        })
    except Exception:
        continue

if not rows:
    print('No attraction rows parsed, aborting')
    raise SystemExit(0)

with engine.begin() as conn:
    pid_cache = {slug: province_id(conn, slug) for slug in sorted({r['province_slug'] for r in rows})}
    # remove old records for these provinces before inserting fresh data
    for pid in pid_cache.values():
        conn.execute(text("DELETE FROM attractions WHERE province_id = :pid"), {'pid': pid})

    for row in rows:
        slug = row['province_slug']
        params = {
            'id': row['id'],
            'name_th': row['name_th'],
            'name_en': row['name_en'],
            'kind': row['kind'],
            'lat': row['lat'],
            'lon': row['lon'],
            'province_id': pid_cache[slug],
            'source_id': row['source_id'],
            'address_th': row['address_th'],
            'province_th': row['province_th'],
            'district_th': row['district_th'],
            'subdistrict_th': row['subdistrict_th'],
            'address_road': row['address_road'],
            'postcode': row['postcode'],
            'tel': row['tel'],
            'email': row['email'],
            'start_end': row['start_end'],
            'hilight': row['hilight'],
            'reward': row['reward'],
            'suitable_duration': row['suitable_duration'],
            'market_limitation': row['market_limitation'],
            'market_chance': row['market_chance'],
            'traveler_pre': row['traveler_pre'],
            'website': row['website'],
            'facebook': row['facebook'],
            'instagram': row['instagram'],
            'tiktok': row['tiktok'],
            'detail_th': row['detail_th'],
            'nearby_location': row['nearby_location'],
            'type_th': row['type_th'],
            'region_th': row['region_th'],
        }
        conn.execute(text("""
            INSERT INTO attractions(
                id,name_th,name_en,kind,lat,lon,province_id,source_id,address_th,province_th,
                district_th,subdistrict_th,address_road,postcode,tel,email,start_end,hilight,reward,
                suitable_duration,market_limitation,market_chance,traveler_pre,website,facebook,
                instagram,tiktok,detail_th,nearby_location,type_th,region_th
            ) VALUES (
                :id,:name_th,:name_en,:kind,:lat,:lon,:province_id,:source_id,:address_th,:province_th,
                :district_th,:subdistrict_th,:address_road,:postcode,:tel,:email,:start_end,:hilight,:reward,
                :suitable_duration,:market_limitation,:market_chance,:traveler_pre,:website,:facebook,
                :instagram,:tiktok,:detail_th,:nearby_location,:type_th,:region_th
            )
            ON CONFLICT (id) DO UPDATE SET
              name_th=EXCLUDED.name_th,
              name_en=EXCLUDED.name_en,
              kind=EXCLUDED.kind,
              lat=EXCLUDED.lat,
              lon=EXCLUDED.lon,
              province_id=EXCLUDED.province_id,
              source_id=EXCLUDED.source_id,
              address_th=EXCLUDED.address_th,
              province_th=EXCLUDED.province_th,
              district_th=EXCLUDED.district_th,
              subdistrict_th=EXCLUDED.subdistrict_th,
              address_road=EXCLUDED.address_road,
              postcode=EXCLUDED.postcode,
              tel=EXCLUDED.tel,
              email=EXCLUDED.email,
              start_end=EXCLUDED.start_end,
              hilight=EXCLUDED.hilight,
              reward=EXCLUDED.reward,
              suitable_duration=EXCLUDED.suitable_duration,
              market_limitation=EXCLUDED.market_limitation,
              market_chance=EXCLUDED.market_chance,
              traveler_pre=EXCLUDED.traveler_pre,
              website=EXCLUDED.website,
              facebook=EXCLUDED.facebook,
              instagram=EXCLUDED.instagram,
              tiktok=EXCLUDED.tiktok,
              detail_th=EXCLUDED.detail_th,
              nearby_location=EXCLUDED.nearby_location,
              type_th=EXCLUDED.type_th,
              region_th=EXCLUDED.region_th
        """), params)
    print('Upserted attractions:', len(rows))
