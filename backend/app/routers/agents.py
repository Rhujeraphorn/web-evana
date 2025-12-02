"""API สำหรับข้อมูล agent (เส้นทางตัวอย่าง)"""
import json
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from ..schemas import AgentDetail, AgentLog as AgentLogSchema, LatLng, AgentStop
from ..db import get_db
from ..models import Agent, AgentLog, AgentRoute, Charger, Attraction, Food, Cafe, Hotel

router = APIRouter(prefix='/api/agents', tags=['agents'])

def _load_polyline(db: Session, agent_id: int, day: Optional[int] = None) -> List[LatLng]:
    """โหลดพิกัด polyline จากตาราง agent_routes (รองรับเลือกวัน)"""
    def _fetch(day_value: Optional[int]):
        stmt = (
            select(func.ST_AsGeoJSON(AgentRoute.geom))
            .where(AgentRoute.agent_id == agent_id)
            .order_by(AgentRoute.day.asc().nullsfirst(), AgentRoute.t_start_min.asc().nullsfirst())
        )
        if day_value is not None:
            stmt = stmt.where(AgentRoute.day == day_value)
        return db.execute(stmt).scalars().all()

    def _append_points(rows: List[str], acc: List[LatLng]):
        for geo_json in rows:
            if not geo_json:
                continue
            try:
                data = json.loads(geo_json)
            except Exception:
                continue
            coords = data.get('coordinates') or []
            for lon, lat in coords:
                if not acc or acc[-1].lat != float(lat) or acc[-1].lon != float(lon):
                    acc.append(LatLng(lat=float(lat), lon=float(lon)))

    points: List[LatLng] = []
    _append_points(_fetch(day), points)
    # Some imported routes use 0-based day indexing. If the requested day is empty, try day-1 as a fallback.
    if not points and day is not None and day > 0:
        _append_points(_fetch(day - 1), points)
    return points

def _find_poi_by_name(db: Session, name: Optional[str]):
    """
    Look up a POI by name across all CSV-backed tables to reuse canonical name/coords.
    Returns dict(label, lat, lon) or None.
    """
    if not name:
        return None
    name_norm = name.strip()
    if not name_norm:
        return None
    candidates = [
        (Charger, Charger.name),
        (Attraction, Attraction.name_th),
        (Food, Food.name_th),
        (Cafe, Cafe.name_th),
        (Hotel, Hotel.name_th),
    ]
    for model, col in candidates:
        row = db.execute(
            select(col, model.lat, model.lon).where(func.lower(col) == func.lower(name_norm)).limit(1)
        ).first()
        if row and row[1] is not None and row[2] is not None:
            return {'label': row[0], 'lat': float(row[1]), 'lon': float(row[2])}
    for model, col in candidates:
        row = db.execute(
            select(col, model.lat, model.lon).where(col.ilike(f'%{name_norm}%')).limit(1)
        ).first()
        if row and row[1] is not None and row[2] is not None:
            return {'label': row[0], 'lat': float(row[1]), 'lon': float(row[2])}
    return None


def _load_stops(db: Session, agent_id: int, day: Optional[int] = None) -> List[AgentStop]:
    """รวมจุดแวะจาก route + timeline เพื่อแสดง pin บนแผนที่"""
    poi_stmt = select(AgentLog.poi_name).where(AgentLog.agent_id == agent_id)
    log_point_stmt = select(AgentLog.poi_name, AgentLog.lat, AgentLog.lon).where(
        AgentLog.agent_id == agent_id, AgentLog.lat.isnot(None), AgentLog.lon.isnot(None)
    )
    if day is not None:
        poi_stmt = poi_stmt.where(AgentLog.day_num == day)
        log_point_stmt = log_point_stmt.where(AgentLog.day_num == day)

    poi_names = [pn for pn in db.execute(poi_stmt).scalars().all() if pn]
    log_points = [(pn, lat, lon) for pn, lat, lon in db.execute(log_point_stmt).all()]
    # ดึงชื่อโรงแรมเริ่มทริปจาก log แรก (ถ้าพอรู้จาก action)
    start_stmt = select(AgentLog.poi_name, AgentLog.action).where(AgentLog.agent_id == agent_id)
    if day is not None:
        start_stmt = start_stmt.where(AgentLog.day_num == day)
    start_names: List[str] = []
    for pn, act in db.execute(start_stmt).all():
        if pn:
            start_names.append(pn)
            continue
        if act:
            m = re.search(r"เริ่มทริป.*เริ่มจากโรงแรม[:\s]+([^(\s]+.*?)(?:\sแบต|\(|$)", act)
            if m:
                start_names.append(m.group(1).strip())
    if start_names:
        poi_names = list(dict.fromkeys(start_names + poi_names))  # preserve order, avoid dup

    def _fetch_route_rows(day_value: Optional[int]):
        stmt = (
            select(AgentRoute.target, func.ST_AsGeoJSON(AgentRoute.geom))
            .where(AgentRoute.agent_id == agent_id)
            .order_by(AgentRoute.day.asc().nullsfirst(), AgentRoute.t_start_min.asc().nullsfirst())
        )
        if day_value is not None:
            stmt = stmt.where(AgentRoute.day == day_value)
        return db.execute(stmt).all()

    route_rows = _fetch_route_rows(day)
    if not route_rows and day is not None and day > 0:
        route_rows = _fetch_route_rows(day - 1)
    stops: List[AgentStop] = []
    seen = set()
    norm_label = lambda v: (v or '').strip().lower()

    def add_stop(label: str, lat_val: float, lon_val: float):
        key = (round(lat_val, 6), round(lon_val, 6))
        if key in seen:
            return
        seen.add(key)
        stops.append(AgentStop(label=label, lat=float(lat_val), lon=float(lon_val)))

    # 1) ใช้ visited_pois (timeline) หาในตาราง POI จริงก่อน เพื่อให้ตำแหน่งตรงไฟล์ CSV
    for pn in poi_names:
        match = _find_poi_by_name(db, pn)
        if not match:
            continue
        label = match['label'] or pn
        add_stop(label, match['lat'], match['lon'])

    # 2) ตำแหน่งจาก geometry ของเส้นทาง (agent_routes)
    for target, geo_json in route_rows:
        if not geo_json:
            continue
        try:
            data = json.loads(geo_json)
        except Exception:
            continue
        coords = data.get('coordinates')
        if not coords:
            continue
        lat = lon = None
        if data.get('type') == 'LineString' and isinstance(coords, list):
            last = coords[-1]
            if isinstance(last, list) and len(last) >= 2:
                lon, lat = last[0], last[1]
        elif data.get('type') == 'Point' and isinstance(coords, list) and len(coords) >= 2:
            lon, lat = coords[0], coords[1]
        elif isinstance(coords, list) and len(coords) and isinstance(coords[0], list):
            last = coords[-1]
            if isinstance(last, list) and len(last):
                candidate = last[-1] if isinstance(last[0], list) else last
                if len(candidate) >= 2:
                    lon, lat = candidate[0], candidate[1]
        fallback_name = poi_names[len(stops)] if len(poi_names) > len(stops) else None
        preferred_label = target or fallback_name

        poi_match = _find_poi_by_name(db, preferred_label) or _find_poi_by_name(db, fallback_name)
        if poi_match:
            label = poi_match['label']
            lat = poi_match['lat']
            lon = poi_match['lon']
        else:
            label = preferred_label or f'จุดที่ {len(stops) + 1}'

        if lat is None or lon is None:
            continue
        add_stop(label, float(lat), float(lon))

    # 3) เติมจาก AgentLog ที่มี lat/lon เพื่อครอบคลุมกรณีชื่อไม่เจอในตาราง
    for pn, lat, lon in log_points:
        if lat is None or lon is None:
            continue
        label = pn or f'จุดที่ {len(stops) + 1}'
        add_stop(label, float(lat), float(lon))

    # 4) ถ้ายังไม่เจอหมุดเริ่มทริป (โรงแรม) เลย ให้ fallback ใช้พิกัดจุดแรกของ polyline
    if start_names:
        start_norms = [norm_label(s) for s in start_names if s]
        start_already = any(norm_label(s.label) in start_norms for s in stops if getattr(s, 'label', None))
        if not start_already:
            poly = _load_polyline(db, agent_id, day)
            if poly:
                p0 = poly[0]
                add_stop(start_names[0], float(p0.lat), float(p0.lon))

    return stops

@router.get('/{agent_id}', response_model=AgentDetail)
def get_agent(agent_id: int, day: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """รายละเอียด agent พร้อม timeline, polyline และจุดแวะ"""
    a = db.execute(select(Agent).where(Agent.id == agent_id)).scalars().first()
    if not a:
        raise HTTPException(status_code=404, detail='Not found')
    stmt = select(AgentLog).where(AgentLog.agent_id == agent_id).order_by(AgentLog.id.asc())
    if day is not None:
        stmt = stmt.where(AgentLog.day_num == day)
    rows = db.execute(stmt).scalars().all()
    logs: List[AgentLogSchema] = [
        AgentLogSchema(ts_text=r.ts_text or '', day=r.day_num or 0, action=r.action or '', poi_name=r.poi_name, lat=r.lat, lon=r.lon)
        for r in rows
    ]
    polyline = _load_polyline(db, agent_id, day)
    stops = _load_stops(db, agent_id, day)
    return AgentDetail(
        id=a.id,
        title=a.label or f'Agent #{a.id}',
        style=a.style or 'mix',
        total_km=float(a.total_km or 0),
        days=a.days or 0,
        timeline=logs,
        polyline=polyline,
        stops=stops,
    )

@router.get('/{agent_id}/polyline', response_model=List[LatLng])
def agent_polyline(agent_id: int, db: Session = Depends(get_db)):
    """คืนเส้น polyline ล้วน ๆ"""
    return _load_polyline(db, agent_id)

@router.get('/{agent_id}/maps-link')
def agent_maps_link(agent_id: int, day: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """redirect ไป Google Maps ด้วยเส้นทางของ agent"""
    pts = _load_polyline(db, agent_id, day)
    if not pts:
        lat, lon = 18.79, 98.99
        return RedirectResponse(f'https://www.google.com/maps/?q={lat},{lon}', status_code=302)
    coords = [(p.lat, p.lon) for p in pts]
    if len(coords) == 1:
        lat, lon = coords[0]
        return RedirectResponse(f'https://www.google.com/maps/?q={lat},{lon}', status_code=302)
    path = '/'.join([f'{lat},{lon}' for lat, lon in coords[:10]])
    return RedirectResponse(f'https://www.google.com/maps/dir/{path}', status_code=302)
