"""API ค้นหา agent/timeline และรายการแนะนำ"""
from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from sqlalchemy import select, func, or_, desc
from sqlalchemy.orm import Session
from ..schemas import AgentCard
from ..db import get_db
from ..models import Agent, AgentLog, Province
from .. import demo_data

def _demo_agents():
    if demo_data.AGENTS:
        return demo_data.AGENTS
    return demo_data.load_route_agents()

router = APIRouter(prefix='/api/agents', tags=['agents'])
FEATURED_PROVINCES = ['chiang-mai','lamphun','lampang','mae-hong-son']

@router.get('/search', response_model=List[AgentCard])
def search_agents(
    q: str = Query(..., min_length=1),
    province: Optional[str] = None,
    limit: Optional[int] = Query(None, ge=1),
    same_hotel: bool = Query(False, alias='sameHotel'),
    db: Session = Depends(get_db),
):
    """ค้นหา agent ด้วยคำหลัก (กรองจังหวัดได้)"""
    like = f"%{q}%"
    # first/last log ต่อ agent (ใช้ทั้งการ boost และ filter start/end)
    boundary_log_subq = (
        select(
            AgentLog.agent_id,
            func.min(AgentLog.id).label('first_log_id'),
            func.max(AgentLog.id).label('last_log_id'),
        )
        .group_by(AgentLog.agent_id)
        .subquery()
    )
    start_match_subq = (
        select(AgentLog.agent_id, func.count('*').label('start_hits'))
        .join(boundary_log_subq, AgentLog.id == boundary_log_subq.c.first_log_id)
        .where(or_(AgentLog.poi_name.ilike(like), AgentLog.action.ilike(like)))
        .group_by(AgentLog.agent_id)
        .subquery()
    )
    end_match_subq = (
        select(AgentLog.agent_id)
        .join(boundary_log_subq, AgentLog.id == boundary_log_subq.c.last_log_id)
        .where(or_(AgentLog.poi_name.ilike(like), AgentLog.action.ilike(like)))
        .subquery()
    )
    # find agents with logs matching poi_name or action
    hits_subq = (
        select(AgentLog.agent_id, func.count('*').label('hits'))
        .where(or_(AgentLog.poi_name.ilike(like), AgentLog.action.ilike(like)))
        .group_by(AgentLog.agent_id)
        .subquery()
    )
    stmt = (
        select(Agent, hits_subq.c.hits, Province.slug_en, func.coalesce(start_match_subq.c.start_hits, 0).label('start_hits'))
        .join(hits_subq, hits_subq.c.agent_id == Agent.id)
        .join(Province, Province.id == Agent.province_id)
        .outerjoin(start_match_subq, start_match_subq.c.agent_id == Agent.id)
        .order_by(desc('start_hits'), hits_subq.c.hits.desc())
    )
    if limit:
        stmt = stmt.limit(limit)
    if same_hotel:
        # ต้องเริ่มและจบทริปด้วย POI ที่ตรงกับคำค้น (เช่น โรงแรมเดียวกัน)
        stmt = (
            stmt.join(end_match_subq, end_match_subq.c.agent_id == Agent.id)
            .where(start_match_subq.c.start_hits.isnot(None))
        )
    if province:
        stmt = stmt.where(Province.slug_en == province)
    try:
        rows = db.execute(stmt).all()
        if not rows:
            raise RuntimeError("no-agent-rows")
    except Exception:
        items = _demo_agents()
        if province:
            items = [a for a in items if a.get('province_slug') == province]
        ql = q.lower()
        items = [a for a in items if ql in ' '.join(a.get('poi_tags', [])).lower() or ql in a.get('label','').lower()]
        if limit:
            items = items[:limit]
        if same_hotel:
            pass
        return [AgentCard(
            id=a['id'],
            title=a.get('label', f"Agent #{a['id']}"),
            style=a.get('style','mix'),
            total_km=float(a.get('total_km',0)),
            days=a.get('days',0),
            poi_tags=a.get('poi_tags',[]),
            points=len(a.get('poi_tags',[])),
            province_slug=a.get('province_slug',''),
        ) for a in items]

    # collect top tags per agent (distinct poi_names with highest frequency among matching logs)
    results: List[AgentCard] = []
    for agent, hits, slug, start_hits in rows:
        tags_stmt = (
            select(AgentLog.poi_name, AgentLog.action, func.count('*').label('c'))
            .where(AgentLog.agent_id == agent.id, or_(AgentLog.poi_name.ilike(like), AgentLog.action.ilike(like)))
            .group_by(AgentLog.poi_name, AgentLog.action)
            .order_by(func.count('*').desc())
            .limit(5)
        )
        tag_rows = db.execute(tags_stmt).all()
        poi_tags = []
        for pn, act, _c in tag_rows:
            if pn:
                poi_tags.append(pn)
            else:
                label = (act or '').split('(')[0].strip()
                if label:
                    poi_tags.append(label[:40])
        results.append(AgentCard(
            id=agent.id,
            title=agent.label or f'Agent #{agent.id}',
            style=agent.style or 'mix',
            total_km=float(agent.total_km or 0),
            days=agent.days or 0,
            poi_tags=poi_tags,
            points=int(hits or 0),
            province_slug=slug,
        ))
    return results

@router.get('/suggest')
def suggest_poi(q: str = Query(..., min_length=1), limit: int = 8, db: Session = Depends(get_db)):
    """เสนอชื่อ POI จาก log ที่ตรงกับคำค้น"""
    like = f"%{q}%"
    # aggregate distinct poi names matching query across all agents
    stmt = (
        select(AgentLog.poi_name, func.count('*').label('c'))
        .where(AgentLog.poi_name.isnot(None), AgentLog.poi_name.ilike(like))
        .group_by(AgentLog.poi_name)
        .order_by(func.count('*').desc())
        .limit(limit)
    )
    try:
        rows = db.execute(stmt).all()
        return [pn for pn, _c in rows if pn]
    except Exception:
        ql = q.lower()
        names = []
        for a in demo_data.AGENTS:
            for pn in a.get('poi_tags', []):
                if ql in pn.lower():
                    names.append(pn)
        return list(dict.fromkeys(names))[:limit]

@router.get('/featured', response_model=List[AgentCard])
def featured_agents(limit: int = 12, db: Session = Depends(get_db)):
    """ดึง agent แนะนำสำหรับ 4 จังหวัดหลัก"""
    stmt = (
        select(Agent, Province.slug_en)
        .join(Province, Province.id == Agent.province_id)
        .where(Province.slug_en.in_(FEATURED_PROVINCES))
        .order_by(Province.slug_en.asc(), desc(Agent.total_km))
        .limit(limit)
    )
    try:
        rows = db.execute(stmt).all()
        if not rows:
            raise RuntimeError("no-agent-rows")
    except Exception:
        items = [a for a in _demo_agents() if a.get('province_slug') in FEATURED_PROVINCES][:limit]
        return [AgentCard(
            id=a['id'],
            title=a.get('label', f"Agent #{a['id']}"),
            style=a.get('style','mix'),
            total_km=float(a.get('total_km',0)),
            days=a.get('days',0),
            poi_tags=a.get('poi_tags',[]),
            points=len(a.get('poi_tags',[])),
            province_slug=a.get('province_slug',''),
        ) for a in items]
    results: List[AgentCard] = []
    for agent, slug in rows:
        tags_stmt = (
            select(AgentLog.poi_name, AgentLog.action, func.count('*').label('c'))
            .where(AgentLog.agent_id == agent.id)
            .group_by(AgentLog.poi_name, AgentLog.action)
            .order_by(func.count('*').desc())
            .limit(5)
        )
        tag_rows = db.execute(tags_stmt).all()
        poi_tags: List[str] = []
        for pn, act, _c in tag_rows:
            if pn:
                poi_tags.append(pn)
            else:
                label = (act or '').split('(')[0].strip()
                if label:
                    poi_tags.append(label[:40])
        results.append(AgentCard(
            id=agent.id,
            title=agent.label or f'Agent #{agent.id}',
            style=agent.style or 'mix',
            total_km=float(agent.total_km or 0),
            days=agent.days or 0,
            poi_tags=poi_tags,
            points=len(poi_tags),
            province_slug=slug,
        ))
    return results
