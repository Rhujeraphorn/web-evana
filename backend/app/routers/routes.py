"""API เส้นทางการเดินทาง/segment ของ EV (โหลดจากไฟล์ภายนอก, DB, และ cache)"""
import json
import os
from typing import Dict, List, Any, Tuple, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from fastapi import APIRouter, HTTPException, Query
import time

router = APIRouter(prefix='/api/routes', tags=['routes'])

# Key -> (filename, display name)
SOURCES: Dict[str, Tuple[str, str]] = {
    'chiang-mai': ('Chiangmai_trip_segments_ev.json', 'เชียงใหม่'),
    'lamphun': ('Lamphun_trip_segments_ev.json', 'ลำพูน'),
    'lampang': ('Lampang_trip_segments_ev.json', 'ลำปาง'),
    'mae-hong-son': ('Maehongson_trip_segments_ev.json', 'แม่ฮ่องสอน'),
}

AGG_SOURCE_MAP: Dict[str, str] = {
    'mae-hong-son-agg': 'mae-hong-son',
    'chiang-mai-agg': 'chiang-mai',
    'lampang-agg': 'lampang',
    'lamphun-agg': 'lamphun',
}

_DB_STATE: Dict[str, Any] = {
    'engine': None,
    'url': None,
}


def _data_dir() -> str:
    """หาตำแหน่งโฟลเดอร์ data ภายใน repo"""
    here = os.path.dirname(__file__)
    # backend/app/routers/routes.py -> project root three levels up
    return os.path.normpath(os.path.join(here, '..', '..', '..', 'data'))

def _repo_routes_dir() -> Optional[str]:
    here = os.path.dirname(__file__)
    candidate = os.path.normpath(os.path.join(here, '..', '..', '..', 'data', 'routes'))
    if os.path.isdir(candidate):
        return candidate
    return None


def _external_dirs() -> Dict[str, str]:
    """พาธไฟล์เส้นทางที่ผู้ใช้วางเอง (ตั้งผ่าน OUTPUT_ROUTES_DIR)"""
    # Allow override via env var; otherwise use known Windows paths
    # Format: OUTPUT_ROUTES_DIR= D:\output\routes
    base = os.environ.get('OUTPUT_ROUTES_DIR')
    if base and os.path.isdir(base):
        return {
            'chiang-mai-ext': os.path.join(base, 'Chiangmai'),
            'lamphun-ext': os.path.join(base, 'Lamphun'),
            'lampang-ext': os.path.join(base, 'Lampang'),
            'mae-hong-son-ext': os.path.join(base, 'Maehongson'),
        }
    # Fallback absolute defaults on Windows
    guesses = {
        'chiang-mai-ext': r'D:\output\routes\Chiangmai',
        'lamphun-ext': r'D:\output\routes\Lamphun',
        'lampang-ext': r'D:\output\routes\Lampang',
        'mae-hong-son-ext': r'D:\output\routes\Maehongson',
    }
    return guesses


def _output_base() -> str:
    """โฟลเดอร์หลักที่เก็บไฟล์ aggregate (.json/.geojson)"""
    base = os.environ.get('OUTPUT_ROUTES_DIR')
    if base and os.path.isdir(base):
        return base
    repo_dir = _repo_routes_dir()
    if repo_dir:
        return repo_dir
    return r'D:\output\routes'


def _aggregated_files() -> Dict[str, Dict[str, str]]:
    """คืน mapping ไปยังไฟล์ aggregate ของแต่ละจังหวัด (json + geojson)"""
    base = _output_base()
    return {
        'mae-hong-son': {
            'json': os.path.join(base, 'Maehongson_all.json'),
            'geojson': os.path.join(base, 'Maehongson_all.geojson'),
        },
        'chiang-mai': {
            'json': os.path.join(base, 'Chiangmai_routes_all.json'),
            'geojson': os.path.join(base, 'Chiangmai_routes_all.geojson'),
        },
        'lampang': {
            'json': os.path.join(base, 'Lampang_routes_all.json'),
            'geojson': os.path.join(base, 'Lampang_routes_all.geojson'),
        },
        'lamphun': {
            'json': os.path.join(base, 'Lamphun_routes.json'),
            'geojson': os.path.join(base, 'Lamphun_routes.geojson'),
        },
    }


def _get_db_engine():
    """สร้าง/รีใช้ engine จาก DATABASE_URL (ถ้าไม่ได้ตั้งจะไม่ใช้ DB)"""
    url = os.environ.get('DATABASE_URL')
    if not url:
        return None
    if _DB_STATE.get('engine') is not None and _DB_STATE.get('url') == url:
        return _DB_STATE['engine']
    try:
        engine = create_engine(url)
    except Exception:
        _DB_STATE['engine'] = None
        _DB_STATE['url'] = None
        return None
    _DB_STATE['engine'] = engine
    _DB_STATE['url'] = url
    return engine


def _source_to_provinces(source: Optional[str]) -> Optional[List[str]]:
    """แปลง key source (-agg/-ext) ให้กลายเป็น list ของจังหวัดที่ต้องใช้"""
    if not source:
        return None
    source = source.strip()
    if source in AGG_SOURCE_MAP:
        return [AGG_SOURCE_MAP[source]]
    if source == 'all-agg':
        return sorted(set(AGG_SOURCE_MAP.values()))
    if source in AGG_SOURCE_MAP.values():
        return [source]
    return None


def _load_routes_from_db(source: Optional[str]) -> Optional[List[Dict[str, Any]]]:
    """โหลด segment จากตาราง route_segments ถ้ามี DB และ source ระบุจังหวัด"""
    provinces = _source_to_provinces(source)
    if not provinces:
        return None
    engine = _get_db_engine()
    if not engine:
        return None
    routes: List[Dict[str, Any]] = []
    try:
        with engine.begin() as conn:
            for prov in provinces:
                rows = conn.execute(text("SELECT attrs FROM route_segments WHERE province = :province"), {'province': prov}).fetchall()
                for row in rows:
                    seg = row[0]
                    if isinstance(seg, str):
                        try:
                            seg = json.loads(seg)
                        except Exception:
                            continue
                    if isinstance(seg, dict):
                        routes.append({'agent_id': 0, 'segments': [seg]})
    except SQLAlchemyError:
        return None
    return routes


def _get_geojson_from_db(from_name: str, to_name: str, source: Optional[str]) -> Optional[Dict[str, Any]]:
    """ดึง GeoJSON จากตาราง route_geoms โดยค้นจากชื่อเริ่ม-ปลายทาง"""
    engine = _get_db_engine()
    provinces = _source_to_provinces(source) or sorted(set(AGG_SOURCE_MAP.values()))
    if not engine or not provinces:
        return None
    from_norm = (from_name or '').strip()
    to_norm = (to_name or '').strip()
    try:
        with engine.begin() as conn:
            for prov in provinces:
                row = conn.execute(text("""
                    SELECT ST_AsGeoJSON(geom) AS geom_json, attrs
                    FROM route_geoms
                    WHERE province = :province
                      AND lower(from_name) = lower(:from_name)
                      AND lower(to_name) = lower(:to_name)
                    ORDER BY id ASC
                    LIMIT 1
                """), {'province': prov, 'from_name': from_norm, 'to_name': to_norm}).first()
                if not row:
                    continue
                geom_json = row[0]
                props = row[1]
                if isinstance(props, str):
                    try:
                        props = json.loads(props)
                    except Exception:
                        props = {}
                if not isinstance(props, dict):
                    props = {}
                props.setdefault('from', from_norm)
                props.setdefault('to', to_norm)
                geom = json.loads(geom_json) if isinstance(geom_json, str) else geom_json
                return {'type': 'Feature', 'geometry': geom, 'properties': props}
    except SQLAlchemyError:
        return None
    return None


def _load_file(path: str) -> List[Dict[str, Any]]:
    """อ่านไฟล์ JSON ที่เป็น list ของเส้นทาง/segment"""
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8-sig') as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except Exception:
            return []


def _load_external_segments() -> List[Dict[str, Any]]:
    """ดึง segment จากไฟล์ JSON ในโฟลเดอร์ external (OUTPUT_ROUTES_DIR/*)"""
    items: List[Dict[str, Any]] = []
    for key, d in _external_dirs().items():
        if not os.path.isdir(d):
            continue
        try:
            for name in os.listdir(d):
                if not name.lower().endswith('.json'):
                    continue
                path = os.path.join(d, name)
                try:
                    with open(path, 'r', encoding='utf-8-sig') as f:
                        data = json.load(f)
                except Exception:
                    continue
                # Normalize into segment dict(s)
                if isinstance(data, list):
                    for obj in data:
                        if isinstance(obj, dict) and 'from' in obj and 'to' in obj:
                            obj['_ext_file'] = path
                            items.append(obj)
                elif isinstance(data, dict):
                    obj = data
                    if 'from' in obj and 'to' in obj:
                        obj['_ext_file'] = path
                        items.append(obj)
        except Exception:
            continue
    return items


def _wrap_as_routes(objs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """ห่อ segment เป็นรูปแบบ {agent_id, segments:[...]} ให้ตรงกับ frontend"""
    wrapped: List[Dict[str, Any]] = []
    for obj in objs:
        if not isinstance(obj, dict):
            continue
        if 'segments' in obj and isinstance(obj['segments'], list):
            wrapped.append(obj)
        elif 'from' in obj and 'to' in obj:
            wrapped.append({'agent_id': 0, 'segments': [obj]})
    return wrapped


def _load_aggregated_segments() -> List[Dict[str, Any]]:
    """โหลด segment จากไฟล์ aggregate ที่ระบุไว้ (รองรับทั้ง route array หรือ segment เดี่ยว)"""
    def _iter_route_like(obj: Any):
        # Yield dicts that are either wrapped routes (have 'segments')
        # or plain segments (have 'from' and 'to'), searching recursively.
        if isinstance(obj, dict):
            if 'segments' in obj and isinstance(obj['segments'], list):
                yield obj
            elif 'from' in obj and 'to' in obj:
                yield obj
            else:
                for v in obj.values():
                    yield from _iter_route_like(v)
        elif isinstance(obj, (list, tuple)):
            for it in obj:
                yield from _iter_route_like(it)

    items: List[Dict[str, Any]] = []
    for meta in _aggregated_files().values():
        jpath = meta.get('json')
        if not jpath or not os.path.exists(jpath):
            continue
        try:
            with open(jpath, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
        except Exception:
            continue
        found = [d for d in _iter_route_like(data) if isinstance(d, dict)]
        # Preserve wrapped routes, wrap plain segments
        wrapped = []
        for d in found:
            if 'segments' in d and isinstance(d['segments'], list):
                wrapped.append(d)
            else:
                wrapped.extend(_wrap_as_routes([d]))
        items.extend(wrapped)
    return items


def _load_output_dir_segments() -> List[Dict[str, Any]]:
    """สแกนไฟล์ JSON ทุกตัวใต้ OUTPUT_ROUTES_DIR แล้วดึงข้อมูล route/segment ออกมา"""
    base = _output_base()
    if not os.path.isdir(base):
        return []

    def _iter_route_like(obj: Any):
        if isinstance(obj, dict):
            if 'segments' in obj and isinstance(obj['segments'], list):
                yield obj
            elif 'from' in obj and 'to' in obj:
                yield obj
            else:
                for v in obj.values():
                    yield from _iter_route_like(v)
        elif isinstance(obj, (list, tuple)):
            for it in obj:
                yield from _iter_route_like(it)

    results: List[Dict[str, Any]] = []
    for root, _, files in os.walk(base):
        for name in files:
            if not name.lower().endswith('.json'):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
            except Exception:
                continue
            found = [d for d in _iter_route_like(data) if isinstance(d, dict)]
            if not found:
                continue
            for d in found:
                if 'segments' in d and isinstance(d['segments'], list):
                    results.append(d)
                else:
                    results.append({'agent_id': 0, 'segments': [d]})
    return results


# ---------------------- In-memory cache ----------------------
_CACHE: Dict[str, Any] = {
    'by_source': {},  # source -> { sig, nodes, routes, adj, label_map, ts }
}


def _norm(s: str) -> str:
    """ทำความสะอาดข้อความชื่อจุดเริ่ม/ปลายทางให้เปรียบเทียบง่าย"""
    if not s:
        return ''
    # Normalize similar to frontend
    out = str(s)
    out = out.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '').replace('\ufeff', '')
    for ch in ['\u2010','\u2011','\u2012','\u2013','\u2014','\u2015','\u2212','\ufe58','\ufe63','\uff0d']:
        out = out.replace(ch, '-')
    for ch in ['“','”','"','‘','’']:
        out = out.replace(ch, '')
    for ch in ['(',')','[',']','{','}','（','）']:
        out = out.replace(ch, ' ')
    out = ' '.join(out.split()).strip().lower()
    return out


def _build_graph(routes: List[Dict[str, Any]]):
    """สร้าง graph adjacency สำหรับค้นหาเส้นทาง (BFS)"""
    adj: Dict[str, List[Dict[str, Any]]] = {}
    label_map: Dict[str, set] = {}
    for r in routes:
        segs = r.get('segments') or []
        if not isinstance(segs, list):
            continue
        for s in segs:
            if not isinstance(s, dict):
                continue
            fr = str(s.get('from',''))
            to = str(s.get('to',''))
            if not fr or not to:
                continue
            nf = _norm(fr)
            nt = _norm(to)
            adj.setdefault(nf, []).append(s)
            label_map.setdefault(nf, set()).add(fr)
            label_map.setdefault(nt, set()).add(to)
    nodes = sorted({orig for vals in label_map.values() for orig in vals})
    return adj, label_map, nodes


def _files_signature_for(source: str) -> List[tuple]:
    """สร้างลายเซ็นไฟล์ (path+mtime+size) เพื่อเช็ก cache"""
    sig: List[tuple] = []
    dd = _data_dir()
    # built-in jsons
    if source in (None, '', 'all', 'ALL') or source in SOURCES:
        for _, (fname, _) in SOURCES.items():
            p = os.path.join(dd, fname)
            if os.path.exists(p):
                sig.append((p, os.path.getmtime(p), os.path.getsize(p)))
    # aggregated
    if source in (None, '', 'all', 'ALL') or source.endswith('-agg'):
        for meta in _aggregated_files().values():
            p = meta.get('json')
            if p and os.path.exists(p):
                sig.append((p, os.path.getmtime(p), os.path.getsize(p)))
    # output dir scan
    base = _output_base()
    if os.path.isdir(base):
        for root, _, files in os.walk(base):
            for name in files:
                if name.lower().endswith('.json'):
                    p = os.path.join(root, name)
                    try:
                        sig.append((p, os.path.getmtime(p), os.path.getsize(p)))
                    except Exception:
                        continue
    return sorted(sig)


def _load_routes_for_source(source: str) -> List[Dict[str, Any]]:
    """โหลดชุด route ตาม source key (รวม external/aggregate/output scan)"""
    dd = _data_dir()
    items: List[Dict[str, Any]] = []
    db_items = _load_routes_from_db(source)
    if db_items is not None:
        return db_items
    if source in (None, '', 'all', 'ALL'):
        for _, meta in SOURCES.items():
            path = os.path.join(dd, meta[0])
            items.extend(_load_file(path))
        items.extend([{ 'agent_id': 0, 'segments': [seg] } for seg in _load_external_segments()])
        items.extend(_load_aggregated_segments())
        items.extend(_load_output_dir_segments())
        return items
    if source.endswith('-ext'):
        return [{ 'agent_id': 0, 'segments': [seg] } for seg in _load_external_segments()]
    if source.endswith('-agg'):
        return _load_aggregated_segments()
    meta = SOURCES.get(source)
    if meta:
        return _load_file(os.path.join(dd, meta[0]))
    # fallback to everything
    return _load_aggregated_segments() + _load_output_dir_segments()


def _get_graph_cached(source: str = 'all'):
    """คืน routes/graph จาก cache ถ้าไฟล์ไม่เปลี่ยน"""
    cache = _CACHE['by_source'].setdefault(source, {'sig': None})
    sig = _files_signature_for(source)
    if cache.get('sig') != sig:
        routes = _load_routes_for_source(source)
        adj, label_map, nodes = _build_graph(routes)
        cache.update({
            'sig': sig,
            'routes': routes,
            'adj': adj,
            'label_map': label_map,
            'nodes': nodes,
            'ts': time.time(),
        })
    return cache['routes'], cache['adj'], cache['label_map'], cache['nodes']


def _find_best_key(label_map: Dict[str, set], query: str) -> Optional[str]:
    """หาคีย์ปกติที่ตรงกับข้อความค้น (เริ่มต้น/ปลายทาง)"""
    q = _norm(query)
    if not q:
        return None
    if q in label_map:
        return q
    for k, originals in label_map.items():
        for o in originals:
            if _norm(o).startswith(q):
                return k
    for k, originals in label_map.items():
        for o in originals:
            if q in _norm(o):
                return k
    return None


def _bfs(adj: Dict[str, List[Dict[str, Any]]], start: str, end: str):
    """วิ่ง BFS หาเส้นทางสั้นสุดตามจำนวน segment พร้อมยอดรวมระยะ/เวลา/พลังงาน"""
    from collections import deque
    q = deque([start])
    prev: Dict[str, tuple] = {}
    seen = {start}
    while q:
        u = q.popleft()
        if u == end:
            break
        for s in adj.get(u, []) or []:
            v = _norm(str(s.get('to','')))
            if v and v not in seen:
                seen.add(v)
                prev[v] = (u, s)
                q.append(v)
    if end not in prev and start != end:
        return None
    path: List[Dict[str, Any]] = []
    cur = end
    while cur != start:
        p = prev.get(cur)
        if not p:
            # not connected
            return None
        path.append(p[1])
        cur = p[0]
    path.reverse()
    totalDist = sum(float(s.get('distance_km') or 0) for s in path)
    totalTime = sum(float(s.get('travel_time_min') or 0) for s in path)
    totalEnergy = sum(float(s.get('energy_kwh') or 0) for s in path)
    totalCost = sum(float(s.get('ev_cost_thb') or 0) for s in path)
    return {
        'path': path,
        'totalDist': totalDist,
        'totalTime': totalTime,
        'totalEnergy': totalEnergy,
        'totalCost': totalCost,
    }


@router.get("/sources")
def list_sources():
    """แสดงสถานะไฟล์/โฟลเดอร์แหล่งข้อมูลเส้นทางที่รองรับ"""
    dd = _data_dir()
    out = []
    for key, (fname, th) in SOURCES.items():
        path = os.path.join(dd, fname)
        exists = os.path.exists(path)
        out.append({ 'key': key, 'name_th': th, 'file': fname, 'exists': exists })
    # Append external dirs status
    for key, d in _external_dirs().items():
        out.append({ 'key': key, 'name_th': key.replace('-ext','').replace('-', ' ').title(), 'file': d, 'exists': os.path.isdir(d) })
    # Append aggregated files status
    for prov_key, meta in _aggregated_files().items():
        out.append({
            'key': f'{prov_key}-agg',
            'name_th': f'{prov_key} (agg)'.replace('-', ' '),
            'file': meta.get('json', ''),
            'exists': bool(meta.get('json') and os.path.exists(meta.get('json','')))
        })
    # Mention base scan path for convenience
    out.append({
        'key': 'output-base-scan',
        'name_th': 'output base scan',
        'file': _output_base(),
        'exists': os.path.isdir(_output_base())
    })
    return out


@router.get('')
def get_routes(source: str = Query('all', description='Source key or all')):
    """คืนชุด route ตาม source (all = รวมทุกแหล่ง)"""
    dd = _data_dir()
    items: List[Dict[str, Any]] = []
    if source in (None, '', 'all', 'ALL'):
        # Include built-in JSON bundles
        for key, meta in SOURCES.items():
            path = os.path.join(dd, meta[0])
            items.extend(_load_file(path))
        # Include external per-file segments
        ext = _load_external_segments()
        # Wrap each external segment as a single-route container for frontend compatibility
        wrapped = [{ 'agent_id': 0, 'segments': [seg] } for seg in ext if isinstance(seg, dict)]
        # Include aggregated files (if present)
        aggs = _load_aggregated_segments()
        # Also include any additional JSONs anywhere under OUTPUT_ROUTES_DIR
        base_any = _load_output_dir_segments()
        return items + wrapped + aggs + base_any
    # Single source: either built-in or external
    if source.endswith('-ext'):
        ext = _load_external_segments()
        return [{ 'agent_id': 0, 'segments': [seg] } for seg in ext]
    if source.endswith('-agg'):
        return _load_aggregated_segments()
    if source == 'output-base-scan':
        return _load_output_dir_segments()
    meta = SOURCES.get(source)
    if not meta:
        raise HTTPException(status_code=400, detail=f'Unknown source: {source}')
    path = os.path.join(dd, meta[0])
    return _load_file(path)


def _try_find_geojson_for(from_name: str, to_name: str) -> Optional[str]:
    """หาคู่ GeoJSON ที่อยู่ข้างไฟล์ JSON ภายนอก (ชื่อเดียวกัน)"""
    # Look for a file in external dirs whose sibling .geojson matches
    f_norm = (from_name or '').strip().lower()
    t_norm = (to_name or '').strip().lower()
    for _, d in _external_dirs().items():
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if not name.lower().endswith('.json'):
                continue
            path = os.path.join(d, name)
            try:
                with open(path, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
            except Exception:
                continue
            candidates = data if isinstance(data, list) else [data]
            for obj in candidates:
                if not isinstance(obj, dict):
                    continue
                fr = str(obj.get('from','')).strip().lower()
                to = str(obj.get('to','')).strip().lower()
                if fr == f_norm and to == t_norm:
                    base, _ = os.path.splitext(path)
                    gj = base + '.geojson'
                    if os.path.exists(gj):
                        return gj
    return None


def _find_feature_in_aggregated_geojson(from_name: str, to_name: str) -> Optional[Dict[str, Any]]:
    """ค้นหา feature ตรงชื่อจากไฟล์ aggregate geojson"""
    f_norm = (from_name or '').strip().lower()
    t_norm = (to_name or '').strip().lower()
    for meta in _aggregated_files().values():
        gj = meta.get('geojson')
        if not gj or not os.path.exists(gj):
            continue
        try:
            with open(gj, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
        features: List[Dict[str, Any]] = []
        if isinstance(data, dict) and data.get('type') == 'FeatureCollection':
            feats = data.get('features') or []
            if isinstance(feats, list):
                features = [ft for ft in feats if isinstance(ft, dict)]
        elif isinstance(data, dict) and data.get('type') == 'Feature':
            features = [data]
        for ft in features:
            props = ft.get('properties') or {}
            fr = str(props.get('from','')).strip().lower()
            to = str(props.get('to','')).strip().lower()
            if fr == f_norm and to == t_norm:
                return ft
    return None


@router.get('/geojson')
def get_geojson(from_name: str = Query(...), to_name: str = Query(...), source: str = Query('all-agg')):
    """คืน GeoJSON ของเส้นทางเริ่ม-ปลายตามข้อมูล DB/ไฟล์ที่มี"""
    db_feature = _get_geojson_from_db(from_name, to_name, source)
    if db_feature:
        return { 'type': 'FeatureCollection', 'features': [db_feature] }
    # Try sibling-per-segment geojson next to external json
    gj_path = _try_find_geojson_for(from_name, to_name)
    if gj_path:
        try:
            with open(gj_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            raise HTTPException(status_code=500, detail='Invalid GeoJSON')
        return data
    # Fallback: search in aggregated geojson files and return matching feature
    ft = _find_feature_in_aggregated_geojson(from_name, to_name)
    if ft:
        return { 'type': 'FeatureCollection', 'features': [ft] }
    raise HTTPException(status_code=404, detail='GeoJSON not found')


@router.get('/nodes')
def get_nodes(source: str = Query('all-agg')):
    """คืนชื่อ node ทั้งหมดเพื่อนำไป autocomplete"""
    _, _, _, nodes = _get_graph_cached(source)
    return nodes


@router.get('/search')
def search_route(
    from_name: str = Query(...),
    to_name: str = Query(...),
    source: str = Query("all-agg"),
):
    """ค้นหาเส้นทางที่เชื่อม from->to จากแหล่งข้อมูลที่เลือก"""
    _, adj, label_map, _ = _get_graph_cached(source)
    sk = _find_best_key(label_map, from_name)
    ek = _find_best_key(label_map, to_name)
    if not sk or not ek:
        raise HTTPException(status_code=404, detail='ไม่พบจุดเริ่มต้นหรือปลายทางในข้อมูล')
    res = _bfs(adj, sk, ek)
    if not res:
        raise HTTPException(status_code=404, detail='ไม่พบเส้นทางตามข้อมูล')
    return res
