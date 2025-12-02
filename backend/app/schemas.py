"""Pydantic schema สำหรับ serialize/validate response ของ API"""
from pydantic import BaseModel
from typing import Optional, List

class LatLng(BaseModel):
    """คู่พิกัด lat/lon"""
    lat: float
    lon: float

class AgentStop(LatLng):
    """จุดแวะบนเส้นทางพร้อมป้ายชื่อ"""
    label: Optional[str] = None

class AgentCard(BaseModel):
    """การ์ดสรุป agent ที่โชว์ในหน้า list"""
    id: int
    title: str
    style: str
    total_km: float
    days: int
    poi_tags: List[str]
    points: int
    province_slug: str

class AgentLog(BaseModel):
    """บันทึกกิจกรรมรายขั้น"""
    ts_text: str
    day: int
    action: str
    poi_name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

class AgentDetail(BaseModel):
    """รายละเอียด agent ที่รวม timeline และ polyline"""
    id: int
    title: str
    style: str
    total_km: float
    days: int
    timeline: List[AgentLog]
    polyline: Optional[List[LatLng]] = None
    stops: Optional[List[AgentStop]] = None
