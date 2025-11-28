-- Production-safe seed template (no TRUNCATE, idempotent inserts)
-- Customize with your real data before running in production.
-- Run with: psql -U <user> -d <db> -f backend/sql/seed_prod_template.sql

BEGIN;

-- Ensure PostGIS is available for geometry columns
CREATE EXTENSION IF NOT EXISTS postgis;

-- Provinces (static list)
INSERT INTO provinces (slug_en, name_th)
VALUES
  ('chiang-mai', 'เชียงใหม่'),
  ('lamphun', 'ลำพูน'),
  ('lampang', 'ลำปาง'),
  ('mae-hong-son', 'แม่ฮ่องสอน')
ON CONFLICT (slug_en) DO NOTHING;

-- Chargers (replace with real data)
INSERT INTO chargers (id, name, type, kw, capacity, lat, lon, province_id, brand, address)
VALUES
  ('<your-id>', '<name>', 'DC', 120, 4, 18.7697, 98.9740, 1, 'EA Anywhere', 'Central Airport, Chiang Mai')
ON CONFLICT (id) DO NOTHING;

-- Attractions / POIs (replace with real data)
INSERT INTO attractions (id, name_th, name_en, kind, lat, lon, province_id, source_id, address_th, district_th, subdistrict_th, province_th, detail_th, type_th, region_th)
VALUES
  ('<poi-id>', '<ชื่อสถานที่>', '<English name>', 'CTA', 18.8040, 98.9215, 1, '<source>', '<address>', '<district>', '<subdistrict>', '<province>', '<detail>', '<type_th>', 'เหนือ')
ON CONFLICT (id) DO NOTHING;

-- Foods
INSERT INTO foods (id, name_th, name_en, price_range, lat, lon, province_id, open_hours_json)
VALUES
  ('<food-id>', '<ชื่อร้าน>', '<English name>', '$$', 18.7952, 98.9888, 1, '{"open": "10:00", "close": "20:00"}')
ON CONFLICT (id) DO NOTHING;

-- Cafes
INSERT INTO cafes (id, name_th, name_en, lat, lon, province_id, open_hours_json)
VALUES
  ('<cafe-id>', '<ชื่อคาเฟ่>', '<English name>', 18.7945, 98.9699, 1, '{"open": "07:00", "close": "18:00"}')
ON CONFLICT (id) DO NOTHING;

-- Hotels
INSERT INTO hotels (id, name_th, name_en, stars, phone, address, lat, lon, province_id)
VALUES
  ('<hotel-id>', '<ชื่อโรงแรม>', '<English name>', 4, '<+66-xxx>', '<full address>', 18.7969, 98.9690, 1)
ON CONFLICT (id) DO NOTHING;

-- Agents (itineraries)
INSERT INTO agents (id, label, style, days, total_km, province_id)
VALUES
  (10001, '<ชื่อทริป>', 'cta', 3, 320, 1)
ON CONFLICT (id) DO NOTHING;

-- Agent logs (timeline)
INSERT INTO agent_logs (agent_id, ts_text, day_num, action, poi_name, poi_id, lat, lon)
VALUES
  (10001, '08:00', 1, 'เริ่มต้นที่โรงแรม', '<hotel name>', '<hotel-id>', 18.7969, 98.9690),
  (10001, '09:00', 1, 'แวะจิบกาแฟ', '<cafe name>', '<cafe-id>', 18.7945, 98.9699)
ON CONFLICT (agent_id, ts_text, poi_id) DO NOTHING;

-- Agent routes (polyline segments; PostGIS required)
INSERT INTO agent_routes (agent_id, day, action, target, poi_type_th, t_start_min, t_end_min, distance_m, geom)
VALUES
  (10001, 1, 'เริ่มจากโรงแรม', '<hotel name>', 'โรงแรม', 480, 540, 0, ST_SetSRID(ST_GeomFromText('POINT(98.9690 18.7969)'), 4326)),
  (10001, 1, 'ไปคาเฟ่', '<cafe name>', 'คาเฟ่', 540, 600, 12000, ST_SetSRID(ST_GeomFromText('LINESTRING(98.9690 18.7969, 98.9699 18.7945)'), 4326))
ON CONFLICT (agent_id, day, t_start_min, target) DO NOTHING;

COMMIT;
