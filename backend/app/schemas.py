from pydantic import BaseModel
from typing import Optional, List

class LatLng(BaseModel):
    lat: float
    lon: float

class AgentStop(LatLng):
    label: Optional[str] = None

class AgentCard(BaseModel):
    id: int
    title: str
    style: str
    total_km: float
    days: int
    poi_tags: List[str]
    points: int
    province_slug: str

class AgentLog(BaseModel):
    ts_text: str
    day: int
    action: str
    poi_name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

class AgentDetail(BaseModel):
    id: int
    title: str
    style: str
    total_km: float
    days: int
    timeline: List[AgentLog]
    polyline: Optional[List[LatLng]] = None
    stops: Optional[List[AgentStop]] = None
