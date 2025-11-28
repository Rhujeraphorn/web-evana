from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List
from sqlalchemy import select, or_, asc
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Charger, Province

router = APIRouter(prefix='/api/chargers', tags=['chargers'])

@router.get('')
def list_chargers(province: Optional[str] = None, q: Optional[str] = None, limit: int = 200, db: Session = Depends(get_db)):
    stmt = select(Charger, Province.slug_en).join(Province, Province.id == Charger.province_id)
    if province:
        stmt = stmt.where(Province.slug_en == province)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Charger.name.ilike(like), Charger.brand.ilike(like), Charger.address.ilike(like)))
    stmt = stmt.order_by(asc(Charger.name)).limit(limit)
    rows = db.execute(stmt).all()
    return [{ 'id': c.id, 'name': c.name, 'type': c.type, 'kw': float(c.kw) if c.kw is not None else None, 'capacity': c.capacity, 'lat': c.lat, 'lon': c.lon, 'province': slug } for c, slug in rows]

@router.get('/{province}')
def chargers_by_province(province: str, db: Session = Depends(get_db)):
    stmt = select(Charger).join(Province, Province.id == Charger.province_id).where(Province.slug_en == province)
    rows = db.execute(stmt).scalars().all()
    return [{ 'id': c.id, 'name': c.name, 'type': c.type, 'kw': float(c.kw) if c.kw is not None else None, 'capacity': c.capacity, 'lat': c.lat, 'lon': c.lon, 'province': province } for c in rows]

@router.get('/{province}/{cid}')
def charger_detail(province: str, cid: str, db: Session = Depends(get_db)):
    stmt = select(Charger).join(Province, Province.id == Charger.province_id).where(Province.slug_en == province, Charger.id == cid)
    c = db.execute(stmt).scalars().first()
    if not c:
        raise HTTPException(status_code=404, detail='Not found')
    return { 'id': c.id, 'name': c.name, 'type': c.type, 'kw': float(c.kw) if c.kw is not None else None, 'capacity': c.capacity, 'lat': c.lat, 'lon': c.lon, 'province': province }
