"""API สำหรับข้อมูล POI (จังหวัด, แหล่งท่องเที่ยว, ร้านอาหาร, คาเฟ่, โรงแรม)"""
import json
from typing import Optional, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_, asc, func
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Attraction, Province, Food, Cafe, Hotel
from ..config import PROVINCE_SEED
from .. import demo_data

router = APIRouter(prefix='/api', tags=['pois'])

SLUG_TO_THAI: Dict[str, str] = { slug: th for slug, th in PROVINCE_SEED }


def _parse_open_hours(raw: Optional[str]) -> Dict[str, str]:
    """แปลงข้อมูลเวลาเปิดปิด (json/string/dict) ให้อยู่รูปแบบเดียว"""
    default = {'open': '', 'close': ''}
    if not raw:
        return default
    if isinstance(raw, dict):
        return {
            'open': str(raw.get('open', '')).strip(),
            'close': str(raw.get('close', '')).strip(),
        }
    try:
        data = json.loads(raw)
        return {
            'open': str(data.get('open', '')).strip(),
            'close': str(data.get('close', '')).strip(),
        }
    except Exception:
        return default


@router.get('/provinces')
def list_provinces(db: Session = Depends(get_db)):
    """ดึงรายการจังหวัด ใช้ฐานข้อมูลก่อน ถ้าไม่มีใช้ seed"""
    # Try DB first
    try:
        rows = db.execute(select(Province).order_by(asc(Province.name_th))).scalars().all()
        if rows:
            return [{ 'slug': p.slug_en, 'name_th': p.name_th } for p in rows]
    except Exception:
        return demo_data.PROVINCES
    # Fallback to seed
    return [{ 'slug': s, 'name_th': th } for s, th in PROVINCE_SEED]


@router.get('/attractions')
def list_attractions(province: Optional[str] = None, q: Optional[str] = None, kind: Optional[str] = None, limit: int = 200, db: Session = Depends(get_db)):
    """ค้นหาแหล่งท่องเที่ยวตามจังหวัด/คำค้น/ชนิด"""
    stmt = select(Attraction, Province.slug_en, Province.name_th).join(Province, Province.id == Attraction.province_id)
    if province:
        stmt = stmt.where(Province.slug_en == province)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Attraction.name_th.ilike(like), Attraction.name_en.ilike(like)))
    if kind:
        stmt = stmt.where(Attraction.kind == kind)
    stmt = stmt.order_by(asc(Attraction.name_th)).limit(limit)
    try:
        rows = db.execute(stmt).all()
        results = []
        for attr, slug, province_name_th in rows:
            results.append({
                'id': attr.id,
                'name_th': attr.name_th,
                'name_en': attr.name_en,
                'kind': attr.kind,
                'lat': attr.lat,
                'lon': attr.lon,
                'province': slug,
                'province_th': attr.province_th or province_name_th,
                'address_th': attr.address_th,
                'district_th': attr.district_th,
                'subdistrict_th': attr.subdistrict_th,
            })
        return results
    except Exception:
        items = demo_data.ATTRACTIONS
        if province:
            items = [i for i in items if i['province'] == province]
        if q:
            ql = q.lower()
            items = [i for i in items if ql in (i.get('name_th','').lower() + i.get('name_en','').lower())]
        if kind:
            items = [i for i in items if i.get('kind') == kind]
        return items[:limit]


@router.get('/attractions/count')
def count_attractions(province: Optional[str] = None, q: Optional[str] = None, db: Session = Depends(get_db)):
    """นับจำนวนแหล่งท่องเที่ยว แยกตาม kind"""
    stmt = select(
        func.count(Attraction.id),
        func.count(func.nullif(Attraction.kind != 'CTA', True)).label('cta'),
        func.count(func.nullif(Attraction.kind != 'AVT', True)).label('avt'),
        func.count(func.nullif(Attraction.kind != 'NTA', True)).label('nta'),
    ).join(Province, Province.id == Attraction.province_id)
    if province:
        stmt = stmt.where(Province.slug_en == province)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Attraction.name_th.ilike(like), Attraction.name_en.ilike(like)))
    try:
        total, cta, avt, nta = db.execute(stmt).one()
        return {
            'total': int(total or 0),
            'cta': int(cta or 0),
            'avt': int(avt or 0),
            'nta': int(nta or 0),
        }
    except Exception:
        items = demo_data.ATTRACTIONS
        if province:
            items = [i for i in items if i['province'] == province]
        if q:
            ql = q.lower()
            items = [i for i in items if ql in (i.get('name_th','').lower() + i.get('name_en','').lower())]
        return {
            'total': len(items),
            'cta': len([i for i in items if i.get('kind') == 'CTA']),
            'avt': len([i for i in items if i.get('kind') == 'AVT']),
            'nta': len([i for i in items if i.get('kind') == 'NTA']),
        }


@router.get('/attractions/{province}/{slug_or_id}')
def attraction_detail(province: str, slug_or_id: str, db: Session = Depends(get_db)):
    """ดึงรายละเอียดแหล่งท่องเที่ยวรายตัว (ใช้ id หรือ source_id ก็ได้)"""
    stmt = (
        select(Attraction)
        .join(Province, Province.id == Attraction.province_id)
        .where(Province.slug_en == province)
        .where(or_(Attraction.id == slug_or_id, Attraction.source_id == slug_or_id))
    )
    try:
        attr = db.execute(stmt).scalars().first()
        if not attr:
            raise HTTPException(status_code=404, detail='Not found')
        province_th = attr.province_th or SLUG_TO_THAI.get(province, '')
        return {
            'id': attr.id,
            'name_th': attr.name_th,
            'name_en': attr.name_en,
            'province': province,
            'province_th': province_th,
            'lat': attr.lat,
            'lon': attr.lon,
            'kind': attr.kind,
            'type_th': attr.type_th,
            'detail_th': attr.detail_th,
            'nearby_location': attr.nearby_location,
            'address_th': attr.address_th,
            'address_road': attr.address_road,
            'postcode': attr.postcode,
            'tel': attr.tel,
            'email': attr.email,
            'start_end': attr.start_end,
            'hilight': attr.hilight,
            'reward': attr.reward,
            'suitable_duration': attr.suitable_duration,
            'market_limitation': attr.market_limitation,
            'market_chance': attr.market_chance,
            'traveler_pre': attr.traveler_pre,
            'website': attr.website,
            'facebook': attr.facebook,
            'instagram': attr.instagram,
            'tiktok': attr.tiktok,
            'region_th': attr.region_th,
            'district_th': attr.district_th,
            'subdistrict_th': attr.subdistrict_th,
        }
    except Exception:
        for i in demo_data.ATTRACTIONS:
            if i['province'] == province and (i['id'] == slug_or_id or i.get('name_en') == slug_or_id):
                i = i.copy()
                i.setdefault('province_th', SLUG_TO_THAI.get(province, ''))
                return i
        raise HTTPException(status_code=404, detail='Not found')


@router.get('/food')
def list_food(province: Optional[str] = None, q: Optional[str] = None, limit: int = 200, db: Session = Depends(get_db)):
    """รายการร้านอาหารพร้อมเวลาทำการ"""
    stmt = select(Food, Province.slug_en).join(Province, Province.id == Food.province_id)
    if province:
        stmt = stmt.where(Province.slug_en == province)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Food.name_th.ilike(like), Food.name_en.ilike(like)))
    stmt = stmt.order_by(asc(Food.name_th)).limit(limit)
    try:
        rows = db.execute(stmt).all()
        items = []
        for food, slug in rows:
            items.append({
                'id': food.id,
                'name_th': food.name_th,
                'name_en': food.name_en,
                'province': slug,
                'lat': food.lat,
                'lon': food.lon,
                'open_hours': _parse_open_hours(food.open_hours_json),
            })
        return items
    except Exception:
        items = demo_data.FOODS
        if province:
            items = [i for i in items if i['province'] == province]
        if q:
            ql = q.lower()
            items = [i for i in items if ql in (i.get('name_th','').lower() + i.get('name_en','').lower())]
        return items[:limit]


@router.get('/food/count')
def count_food(province: Optional[str] = None, q: Optional[str] = None, db: Session = Depends(get_db)):
    """นับจำนวนร้านอาหารตามจังหวัด/คำค้น"""
    stmt = select(func.count(Food.id)).join(Province, Province.id == Food.province_id)
    if province:
        stmt = stmt.where(Province.slug_en == province)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Food.name_th.ilike(like), Food.name_en.ilike(like)))
    try:
        total = db.execute(stmt).scalar() or 0
        return {'total': int(total)}
    except Exception:
        items = demo_data.FOODS
        if province:
            items = [i for i in items if i['province'] == province]
        if q:
            ql = q.lower()
            items = [i for i in items if ql in (i.get('name_th','').lower() + i.get('name_en','').lower())]
        return {'total': len(items)}


@router.get('/food/{province}/{slug_or_id}')
def food_detail(province: str, slug_or_id: str, db: Session = Depends(get_db)):
    """รายละเอียดร้านอาหารรายตัว"""
    stmt = select(Food).join(Province, Province.id == Food.province_id).where(Province.slug_en == province, Food.id == slug_or_id)
    try:
        food = db.execute(stmt).scalars().first()
        if not food:
            raise HTTPException(status_code=404, detail='Not found')
        return {
            'id': food.id,
            'name_th': food.name_th,
            'name_en': food.name_en,
            'province': province,
            'lat': food.lat,
            'lon': food.lon,
            'price_range': food.price_range,
            'open_hours': _parse_open_hours(food.open_hours_json),
        }
    except Exception:
        for i in demo_data.FOODS:
            if i['province'] == province and i['id'] == slug_or_id:
                return i
        raise HTTPException(status_code=404, detail='Not found')


@router.get('/cafes')
def list_cafes(province: Optional[str] = None, q: Optional[str] = None, limit: int = 200, db: Session = Depends(get_db)):
    """รายการคาเฟ่"""
    stmt = select(Cafe, Province.slug_en).join(Province, Province.id == Cafe.province_id)
    if province:
        stmt = stmt.where(Province.slug_en == province)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Cafe.name_th.ilike(like), Cafe.name_en.ilike(like)))
    stmt = stmt.order_by(asc(Cafe.name_th)).limit(limit)
    try:
        rows = db.execute(stmt).all()
        return [{ 'id': c.id, 'name_th': c.name_th, 'name_en': c.name_en, 'province': slug, 'lat': c.lat, 'lon': c.lon } for c, slug in rows]
    except Exception:
        items = demo_data.CAFES
        if province:
            items = [i for i in items if i['province'] == province]
        if q:
            ql = q.lower()
            items = [i for i in items if ql in (i.get('name_th','').lower() + i.get('name_en','').lower())]
        return items[:limit]


@router.get('/cafes/count')
def count_cafes(province: Optional[str] = None, q: Optional[str] = None, db: Session = Depends(get_db)):
    """นับจำนวนคาเฟ่ตามจังหวัด/คำค้น"""
    stmt = select(func.count(Cafe.id)).join(Province, Province.id == Cafe.province_id)
    if province:
        stmt = stmt.where(Province.slug_en == province)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Cafe.name_th.ilike(like), Cafe.name_en.ilike(like)))
    try:
        total = db.execute(stmt).scalar() or 0
        return {'total': int(total)}
    except Exception:
        items = demo_data.CAFES
        if province:
            items = [i for i in items if i['province'] == province]
        if q:
            ql = q.lower()
            items = [i for i in items if ql in (i.get('name_th','').lower() + i.get('name_en','').lower())]
        return {'total': len(items)}


@router.get('/cafes/{province}/{slug_or_id}')
def cafe_detail(province: str, slug_or_id: str, db: Session = Depends(get_db)):
    """รายละเอียดคาเฟ่"""
    stmt = select(Cafe).join(Province, Province.id == Cafe.province_id).where(Province.slug_en == province, Cafe.id == slug_or_id)
    try:
        c = db.execute(stmt).scalars().first()
        if not c:
            raise HTTPException(status_code=404, detail='Not found')
        return { 'id': c.id, 'name_th': c.name_th, 'name_en': c.name_en, 'province': province, 'lat': c.lat, 'lon': c.lon }
    except Exception:
        for i in demo_data.CAFES:
            if i['province'] == province and i['id'] == slug_or_id:
                return i
        raise HTTPException(status_code=404, detail='Not found')


@router.get('/hotels')
def list_hotels(province: Optional[str] = None, q: Optional[str] = None, limit: int = 200, db: Session = Depends(get_db)):
    """รายการโรงแรม/ที่พัก"""
    stmt = select(Hotel, Province.slug_en).join(Province, Province.id == Hotel.province_id)
    if province:
        stmt = stmt.where(Province.slug_en == province)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Hotel.name_th.ilike(like), Hotel.name_en.ilike(like)))
    stmt = stmt.order_by(
        # push rowsที่มีชื่อไทย (ไม่ว่าง/ไม่ null) ขึ้นก่อน
        asc((Hotel.name_th == None) | (Hotel.name_th == '')),
        asc(Hotel.name_th),
        asc(Hotel.name_en)
    ).limit(limit)
    try:
        rows = db.execute(stmt).all()
        return [{ 'id': h.id, 'name_th': h.name_th, 'name_en': h.name_en, 'province': slug, 'lat': h.lat, 'lon': h.lon, 'stars': h.stars, 'phone': h.phone, 'address': h.address } for h, slug in rows]
    except Exception:
        items = demo_data.HOTELS
        if province:
            items = [i for i in items if i['province'] == province]
        if q:
            ql = q.lower()
            items = [i for i in items if ql in (i.get('name_th','').lower() + i.get('name_en','').lower())]
        return items[:limit]


@router.get('/hotels/count')
def count_hotels(province: Optional[str] = None, q: Optional[str] = None, db: Session = Depends(get_db)):
    """นับจำนวนโรงแรมตามจังหวัด/คำค้น"""
    stmt = select(func.count(Hotel.id)).join(Province, Province.id == Hotel.province_id)
    if province:
        stmt = stmt.where(Province.slug_en == province)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Hotel.name_th.ilike(like), Hotel.name_en.ilike(like)))
    try:
        total = db.execute(stmt).scalar() or 0
        return {'total': int(total)}
    except Exception:
        items = demo_data.HOTELS
        if province:
            items = [i for i in items if i['province'] == province]
        if q:
            ql = q.lower()
            items = [i for i in items if ql in (i.get('name_th','').lower() + i.get('name_en','').lower())]
        return {'total': len(items)}


@router.get('/hotels/{province}/{slug_or_id}')
def hotel_detail(province: str, slug_or_id: str, db: Session = Depends(get_db)):
    """รายละเอียดโรงแรมรายตัว"""
    stmt = select(Hotel).join(Province, Province.id == Hotel.province_id).where(Province.slug_en == province, Hotel.id == slug_or_id)
    try:
        h = db.execute(stmt).scalars().first()
        if not h:
            raise HTTPException(status_code=404, detail='Not found')
        return { 'id': h.id, 'name_th': h.name_th, 'name_en': h.name_en, 'province': province, 'lat': h.lat, 'lon': h.lon, 'stars': h.stars, 'phone': h.phone, 'address': h.address }
    except Exception:
        for i in demo_data.HOTELS:
            if i['province'] == province and i['id'] == slug_or_id:
                return i
        raise HTTPException(status_code=404, detail='Not found')
