import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Generator
from decimal import Decimal

from sqlalchemy import create_engine, text

# Ensure project root (backend/) is on sys.path when running as a script
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import CSV_BASE_DIR, DATABASE_URL

engine = create_engine(DATABASE_URL)

AGENT_DIR = os.path.join(CSV_BASE_DIR, 'agent')
PROVINCE_PREFIX = {
    'chiang-mai': 'Chiangmai',
    'lampang': 'Lampang',
    'lamphun': 'Lamphun',
    'mae-hong-son': 'Maehongson',
}
# optional overrides for agent route GeoJSON source directories
AGENT_GEO_OVERRIDE = {
    'Lampang': r'D:\Lampang_geo\routes',
    'Lamphun': r'D:\Lamphun_geo\routes',
    'Maehongson': r'D:\Maehongson_geo\routes',
}


def _agent_json_path(prefix: str) -> str:
    return os.path.join(AGENT_DIR, f'{prefix}_agent.json')


def _agent_geojson_path(prefix: str) -> str:
    # prefer override directory if provided, otherwise fall back to single GeoJSON file in AGENT_DIR
    if prefix in AGENT_GEO_OVERRIDE:
        return AGENT_GEO_OVERRIDE[prefix]
    return os.path.join(AGENT_DIR, f'{prefix}_agent.geojson')


def _count_days(logs: List[str]) -> int:
    dmax = 0
    for line in logs or []:
        m = re.search(r"\[D(\d+)\s", line or '')
        if m:
            dmax = max(dmax, int(m.group(1)))
    return dmax or (1 if logs else 0)


def _parse_log_line(line: str):
    ts_part = ''
    day_num = 0
    action_text = line.strip()
    m = re.match(r"\[(.*?)\]\s*(.*)$", action_text)
    if m:
        ts_part = m.group(1)
        action_text = m.group(2).strip()
        md = re.match(r"D(\d+)\s", ts_part)
        if md:
            day_num = int(md.group(1))
    poi = None
    patterns = [
        r"->\s*([^()\[]+?)\s*(?:\(|$)",
        r"แวะ[^ ]*ที่\s+([^()\[]+?)\s*(?:\(|$)",
        r"เที่ยว\s+([^()\[]+?)\s*(?:\(|$)",
        r"โรงแรม[:\s]+([^()\[]+?)\s*(?:\(|$)",
    ]
    for p in patterns:
        mp = re.search(p, action_text)
        if mp:
            poi = mp.group(1).strip()
            break
    return ts_part, day_num or 0, action_text, poi


def insert_logs(conn, agent_id: int, logs: List[str], batch_size: int = 1000):
    if not logs:
        return
    rows = []
    for line in logs:
        ts_text, day_num, action, poi_name = _parse_log_line(line or '')
        rows.append({
            'agent_id': agent_id,
            'ts_text': ts_text,
            'day_num': day_num,
            'action': action,
            'poi_name': poi_name,
        })
    sql = text("""
        INSERT INTO agent_logs(agent_id, ts_text, day_num, action, poi_name)
        VALUES (:agent_id, :ts_text, :day_num, :action, :poi_name)
    """)
    for i in range(0, len(rows), batch_size):
        conn.execute(sql, rows[i:i+batch_size])


def upsert_agent(conn, new_id: int, row: Dict[str, Any], province_id: int):
    total_km = row.get('total_distance_km')
    if total_km is None:
        total_km = row.get('total_km', 0)
    logs = row.get('log') or []
    conn.execute(text("""
      INSERT INTO agents(id,label,style,days,total_km,province_id)
      VALUES (:id,:label,:style,:days,:total_km,:province_id)
      ON CONFLICT (id) DO UPDATE SET
        label=EXCLUDED.label,
        style=EXCLUDED.style,
        days=EXCLUDED.days,
        total_km=EXCLUDED.total_km,
        province_id=EXCLUDED.province_id
    """), {
        'id': new_id,
        'label': row.get('title') or row.get('tourist_type') or f"Agent #{row.get('agent_id')}",
        'style': (row.get('policy_main') or row.get('tourist_type') or row.get('stereotype') or 'mix').lower(),
        'days': row.get('days') or _count_days(logs),
        'total_km': float(total_km or 0),
        'province_id': province_id,
    })


def insert_routes(conn, agent_id: int, features: List[Dict[str, Any]], batch_size: int = 200):
    if not features:
        return
    payload = []
    for ft in features:
        geom = ft.get('geom')
        if not geom:
            continue
        payload.append({
            'agent_id': agent_id,
            'day': int(ft.get('day') or 0),
            'action': ft.get('action') or '',
            'target': ft.get('target') or '',
            'poi_type_th': ft.get('poi_type_th') or '',
            't_start_min': float(ft.get('t_start_min')) if ft.get('t_start_min') is not None else None,
            't_end_min': float(ft.get('t_end_min')) if ft.get('t_end_min') is not None else None,
            'distance_m': float(ft.get('distance_m')) if ft.get('distance_m') is not None else None,
            'geom_json': json.dumps(geom, ensure_ascii=False),
        })
    if not payload:
        return
    sql = text("""
        INSERT INTO agent_routes(agent_id, day, action, target, poi_type_th, t_start_min, t_end_min, distance_m, geom)
        VALUES (:agent_id, :day, :action, :target, :poi_type_th, :t_start_min, :t_end_min, :distance_m, ST_GeomFromGeoJSON(:geom_json))
    """)
    for i in range(0, len(payload), batch_size):
        conn.execute(sql, payload[i:i+batch_size])


def load_geo_features(path: str) -> Dict[int, List[Dict[str, Any]]]:
    grouped: Dict[int, List[Dict[str, Any]]] = {}
    p = Path(path)
    if not p.exists():
        return grouped

    def _load_file(file_path: Path):
        try:
            import ijson
            with file_path.open('rb') as f:
                parser = ijson.items(f, 'features.item')
                for ft in parser:
                    _collect_feature(grouped, ft)
            return
        except Exception:
            pass
        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            for ft in data.get('features', []):
                _collect_feature(grouped, ft)
        except Exception:
            return

    if p.is_dir():
        processed = 0
        for fp in sorted(p.glob('*.geojson')):
            _load_file(fp)
            processed += 1
            if processed % 500 == 0:
                print(f'  …loaded {processed} geojson files from {p}', flush=True)
    else:
        _load_file(p)

    _sort_grouped(grouped)
    return grouped


def _collect_feature(grouped: Dict[int, List[Dict[str, Any]]], ft: Any):
    if not isinstance(ft, dict):
        return
    props = ft.get('properties') or {}
    geom = ft.get('geometry')
    if not geom or props.get('agent_id') is None:
        return
    aid = int(props.get('agent_id'))
    grouped.setdefault(aid, []).append({
        'day': props.get('day'),
        'action': props.get('action'),
        'target': props.get('target'),
        'poi_type_th': props.get('poi_type_th'),
        't_start_min': _to_float(props.get('t_start_min')),
        't_end_min': _to_float(props.get('t_end_min')),
        'distance_m': _to_float(props.get('dist_m')),
        'geom': _convert_geometry(geom),
    })


def _sort_grouped(grouped: Dict[int, List[Dict[str, Any]]]):
    for segs in grouped.values():
        segs.sort(key=lambda r: ((r.get('day') or 0), (r.get('t_start_min') or 0)))


def _to_float(val):
    if val is None:
        return None
    try:
        return float(val)
    except Exception:
        return None


def _convert_geometry(geom: Any):
    if isinstance(geom, dict):
        return {k: _convert_geometry(v) for k, v in geom.items()}
    if isinstance(geom, list):
        return [_convert_geometry(v) for v in geom]
    if isinstance(geom, (int, float, Decimal)):
        return float(geom)
    return geom


def _delete_scope(conn, pid: int):
    base = int(pid) * 1_000_000
    hi = base + 999_999
    conn.execute(text('DELETE FROM agent_logs WHERE agent_id BETWEEN :lo AND :hi'), {'lo': base, 'hi': hi})
    conn.execute(text('DELETE FROM agent_routes WHERE agent_id BETWEEN :lo AND :hi'), {'lo': base, 'hi': hi})


def _iter_agents(json_path: str) -> Generator[Dict[str, Any], None, None]:
    if not os.path.exists(json_path):
        return
    try:
        import ijson
        with open(json_path, 'rb') as f:
            parser = ijson.items(f, 'item')
            for obj in parser:
                if obj:
                    yield obj
            return
    except Exception:
        pass
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    for row in data or []:
        yield row


with engine.begin() as conn:
    pid_map = { slug: pid for pid, slug in conn.execute(text('SELECT id, slug_en FROM provinces')) }
    for slug, prefix in PROVINCE_PREFIX.items():
        json_path = _agent_json_path(prefix)
        geo_path = _agent_geojson_path(prefix)
        if not os.path.exists(json_path):
            print('Missing agent JSON:', json_path)
            continue
        geo_features = load_geo_features(geo_path) if os.path.exists(geo_path) else {}
        pid = pid_map.get(slug)
        if not pid:
            print('Province missing for slug', slug)
            continue
        print(f'Processing {slug} ({prefix}) …', flush=True)
        _delete_scope(conn, pid)
        count = 0
        for row in _iter_agents(json_path):
            original_id = int(row.get('agent_id'))
            new_id = int(pid) * 1_000_000 + original_id
            upsert_agent(conn, new_id, row, pid)
            insert_logs(conn, new_id, row.get('log') or [])
            insert_routes(conn, new_id, geo_features.get(original_id, []))
            count += 1
            if count % 100 == 0:
                print(f'  …{count} agents imported', flush=True)
        print(f'Upserted agents for {slug} {count}', flush=True)
