"""API สถานีชาร์จรถ EV"""
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List
from sqlalchemy import select, or_, asc
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Charger, Province
from .. import demo_data

router = APIRouter(prefix='/api/chargers', tags=['chargers'])

@router.get('')
def list_chargers(province: Optional[str] = None, q: Optional[str] = None, limit: int = 200, db: Session = Depends(get_db)):
    """ค้นหาสถานีชาร์จทั้งหมด รองรับกรองจังหวัด/คำค้น"""
    stmt = select(Charger, Province.slug_en).join(Province, Province.id == Charger.province_id)
    if province:
        stmt = stmt.where(Province.slug_en == province)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Charger.name.ilike(like), Charger.brand.ilike(like), Charger.address.ilike(like)))
    stmt = stmt.order_by(asc(Charger.name)).limit(limit)
    try:
        rows = db.execute(stmt).all()
        return [{ 'id': c.id, 'name': c.name, 'type': c.type, 'kw': float(c.kw) if c.kw is not None else None, 'capacity': c.capacity, 'lat': c.lat, 'lon': c.lon, 'province': slug } for c, slug in rows]
    except Exception:
        items = demo_data.CHARGERS
        if province:
            items = [i for i in items if i['province'] == province]
        if q:
            ql = q.lower()
            items = [i for i in items if ql in (i.get('name','').lower())]
        return items[:limit]

@router.get('/{province}')
def chargers_by_province(province: str, db: Session = Depends(get_db)):
    """ดึงสถานีชาร์จในจังหวัดที่กำหนด"""
    stmt = select(Charger).join(Province, Province.id == Charger.province_id).where(Province.slug_en == province)
    try:
        rows = db.execute(stmt).scalars().all()
        return [{ 'id': c.id, 'name': c.name, 'type': c.type, 'kw': float(c.kw) if c.kw is not None else None, 'capacity': c.capacity, 'lat': c.lat, 'lon': c.lon, 'province': province } for c in rows]
    except Exception:
        items = [i for i in demo_data.CHARGERS if i['province'] == province]
        return items

@router.get('/{province}/{cid}')
def charger_detail(province: str, cid: str, db: Session = Depends(get_db)):
    """รายละเอียดสถานีชาร์จรายตัว"""
    stmt = select(Charger).join(Province, Province.id == Charger.province_id).where(Province.slug_en == province, Charger.id == cid)
    try:
        c = db.execute(stmt).scalars().first()
        if not c:
            raise HTTPException(status_code=404, detail='Not found')
        return { 'id': c.id, 'name': c.name, 'type': c.type, 'kw': float(c.kw) if c.kw is not None else None, 'capacity': c.capacity, 'lat': c.lat, 'lon': c.lon, 'province': province }
    except Exception:
        for i in demo_data.CHARGERS:
            if i['province'] == province and i['id'] == cid:
                return i
        raise HTTPException(status_code=404, detail='Not found')
