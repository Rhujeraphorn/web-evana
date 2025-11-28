import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from ..schemas import AgentDetail, AgentLog as AgentLogSchema, LatLng, AgentStop
from ..db import get_db
from ..models import Agent, AgentLog, AgentRoute

router = APIRouter(prefix='/api/agents', tags=['agents'])

def _load_polyline(db: Session, agent_id: int) -> List[LatLng]:
    stmt = (
        select(func.ST_AsGeoJSON(AgentRoute.geom))
        .where(AgentRoute.agent_id == agent_id)
        .order_by(AgentRoute.day.asc().nullsfirst(), AgentRoute.t_start_min.asc().nullsfirst())
    )
    points: List[LatLng] = []
    for geo_json in db.execute(stmt).scalars().all():
        if not geo_json:
            continue
        try:
            data = json.loads(geo_json)
        except Exception:
            continue
        coords = data.get('coordinates') or []
        for lon, lat in coords:
            if not points or points[-1].lat != float(lat) or points[-1].lon != float(lon):
                points.append(LatLng(lat=float(lat), lon=float(lon)))
    return points

def _load_stops(db: Session, agent_id: int) -> List[AgentStop]:
    stmt = (
        select(AgentRoute.target, func.ST_AsGeoJSON(AgentRoute.geom))
        .where(AgentRoute.agent_id == agent_id)
        .order_by(AgentRoute.day.asc().nullsfirst(), AgentRoute.t_start_min.asc().nullsfirst())
    )
    stops: List[AgentStop] = []
    for target, geo_json in db.execute(stmt).all():
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
        if lat is None or lon is None:
            continue
        label = target or f'จุดที่ {len(stops) + 1}'
        stops.append(AgentStop(label=label, lat=float(lat), lon=float(lon)))
    return stops

@router.get('/{agent_id}', response_model=AgentDetail)
def get_agent(agent_id: int, day: Optional[int] = Query(None), db: Session = Depends(get_db)):
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
    polyline = _load_polyline(db, agent_id)
    stops = _load_stops(db, agent_id)
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
    return _load_polyline(db, agent_id)

@router.get('/{agent_id}/maps-link')
def agent_maps_link(agent_id: int, day: Optional[int] = Query(None), db: Session = Depends(get_db)):
    pts = _load_polyline(db, agent_id)
    if not pts:
        lat, lon = 18.79, 98.99
        return RedirectResponse(f'https://www.google.com/maps/?q={lat},{lon}', status_code=302)
    coords = [(p.lat, p.lon) for p in pts]
    if len(coords) == 1:
        lat, lon = coords[0]
        return RedirectResponse(f'https://www.google.com/maps/?q={lat},{lon}', status_code=302)
    path = '/'.join([f'{lat},{lon}' for lat, lon in coords[:10]])
    return RedirectResponse(f'https://www.google.com/maps/dir/{path}', status_code=302)
