"""ORM model สำหรับตารางหลักของฐานข้อมูล"""
from sqlalchemy import Column, Integer, Text, Float, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Province(Base):
    """จังหวัดที่ใช้ผูกกับทุกข้อมูลย่อย"""
    __tablename__ = 'provinces'
    id = Column(Integer, primary_key=True)
    slug_en = Column(Text, unique=True, nullable=False)
    name_th = Column(Text, nullable=False)

class Charger(Base):
    """สถานีชาร์จรถ EV"""
    __tablename__ = 'chargers'
    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    type = Column(Text)
    kw = Column(Numeric)
    capacity = Column(Integer)
    lat = Column(Float)
    lon = Column(Float)
    province_id = Column(Integer, ForeignKey('provinces.id'))
    brand = Column(Text)
    address = Column(Text)

class Attraction(Base):
    """แหล่งท่องเที่ยว/จุดสนใจ"""
    __tablename__ = 'attractions'
    id = Column(Text, primary_key=True)
    name_th = Column(Text)
    name_en = Column(Text)
    kind = Column(Text)
    lat = Column(Float)
    lon = Column(Float)
    province_id = Column(Integer, ForeignKey('provinces.id'))
    source_id = Column(Text)
    address_th = Column(Text)
    province_th = Column(Text)
    district_th = Column(Text)
    subdistrict_th = Column(Text)
    address_road = Column(Text)
    postcode = Column(Text)
    tel = Column(Text)
    email = Column(Text)
    start_end = Column(Text)
    hilight = Column(Text)
    reward = Column(Text)
    suitable_duration = Column(Text)
    market_limitation = Column(Text)
    market_chance = Column(Text)
    traveler_pre = Column(Text)
    website = Column(Text)
    facebook = Column(Text)
    instagram = Column(Text)
    tiktok = Column(Text)
    detail_th = Column(Text)
    nearby_location = Column(Text)
    type_th = Column(Text)
    region_th = Column(Text)

class Food(Base):
    """ร้านอาหาร"""
    __tablename__ = 'foods'
    id = Column(Text, primary_key=True)
    name_th = Column(Text)
    name_en = Column(Text)
    price_range = Column(Text)
    lat = Column(Float)
    lon = Column(Float)
    province_id = Column(Integer, ForeignKey('provinces.id'))
    open_hours_json = Column(Text)

class Cafe(Base):
    """คาเฟ่"""
    __tablename__ = 'cafes'
    id = Column(Text, primary_key=True)
    name_th = Column(Text)
    name_en = Column(Text)
    lat = Column(Float)
    lon = Column(Float)
    province_id = Column(Integer, ForeignKey('provinces.id'))
    open_hours_json = Column(Text)

class Hotel(Base):
    """โรงแรม/ที่พัก"""
    __tablename__ = 'hotels'
    id = Column(Text, primary_key=True)
    name_th = Column(Text)
    name_en = Column(Text)
    stars = Column(Integer)
    phone = Column(Text)
    address = Column(Text)
    lat = Column(Float)
    lon = Column(Float)
    province_id = Column(Integer, ForeignKey('provinces.id'))

class Agent(Base):
    """เส้นทางตัวอย่าง (agent) ที่มี metadata"""
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    label = Column(Text)
    style = Column(Text)
    days = Column(Integer)
    total_km = Column(Numeric)
    province_id = Column(Integer, ForeignKey('provinces.id'))

class AgentLog(Base):
    """บันทึกเหตุการณ์ในแต่ละวันของ agent"""
    __tablename__ = 'agent_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    ts_text = Column(Text)
    day_num = Column(Integer)
    action = Column(Text)
    poi_name = Column(Text)
    poi_id = Column(Text)
    lat = Column(Float)
    lon = Column(Float)

class AgentRoute(Base):
    """เส้นทางรายขั้นของ agent รวมเวลาช่วงและระยะทาง"""
    __tablename__ = 'agent_routes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    day = Column(Integer)
    action = Column(Text)
    target = Column(Text)
    poi_type_th = Column(Text)
    t_start_min = Column(Numeric)
    t_end_min = Column(Numeric)
    distance_m = Column(Numeric)
    geom = Column(Text)
