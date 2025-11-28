CREATE TABLE IF NOT EXISTS provinces (
  id SERIAL PRIMARY KEY,
  slug_en TEXT UNIQUE NOT NULL,
  name_th TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chargers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT CHECK (type IN ('AC','DC')),
  kw NUMERIC,
  capacity INT,
  lat DOUBLE PRECISION,
  lon DOUBLE PRECISION,
  province_id INT REFERENCES provinces(id),
  brand TEXT, address TEXT
);

CREATE TABLE IF NOT EXISTS attractions (
  id TEXT PRIMARY KEY,
  name_th TEXT, name_en TEXT,
  kind TEXT CHECK (kind IN ('CTA','NTA','AVT')),
  lat DOUBLE PRECISION, lon DOUBLE PRECISION,
  province_id INT REFERENCES provinces(id),
  source_id TEXT,
  address_th TEXT,
  province_th TEXT,
  district_th TEXT,
  subdistrict_th TEXT,
  address_road TEXT,
  postcode TEXT,
  tel TEXT,
  email TEXT,
  start_end TEXT,
  hilight TEXT,
  reward TEXT,
  suitable_duration TEXT,
  market_limitation TEXT,
  market_chance TEXT,
  traveler_pre TEXT,
  website TEXT,
  facebook TEXT,
  instagram TEXT,
  tiktok TEXT,
  detail_th TEXT,
  nearby_location TEXT,
  type_th TEXT,
  region_th TEXT
);

ALTER TABLE attractions ADD COLUMN IF NOT EXISTS source_id TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS address_th TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS province_th TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS district_th TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS subdistrict_th TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS address_road TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS postcode TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS tel TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS email TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS start_end TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS hilight TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS reward TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS suitable_duration TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS market_limitation TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS market_chance TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS traveler_pre TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS website TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS facebook TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS instagram TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS tiktok TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS detail_th TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS nearby_location TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS type_th TEXT;
ALTER TABLE attractions ADD COLUMN IF NOT EXISTS region_th TEXT;

-- foods
CREATE TABLE IF NOT EXISTS foods (
  id TEXT PRIMARY KEY,
  name_th TEXT, name_en TEXT,
  price_range TEXT,
  lat DOUBLE PRECISION, lon DOUBLE PRECISION,
  province_id INT REFERENCES provinces(id),
  open_hours_json JSONB
);

-- cafes
CREATE TABLE IF NOT EXISTS cafes (
  id TEXT PRIMARY KEY,
  name_th TEXT, name_en TEXT,
  lat DOUBLE PRECISION, lon DOUBLE PRECISION,
  province_id INT REFERENCES provinces(id),
  open_hours_json JSONB
);

-- hotels
CREATE TABLE IF NOT EXISTS hotels (
  id TEXT PRIMARY KEY,
  name_th TEXT, name_en TEXT,
  stars INT,
  phone TEXT, address TEXT,
  lat DOUBLE PRECISION, lon DOUBLE PRECISION,
  province_id INT REFERENCES provinces(id)
);

CREATE TABLE IF NOT EXISTS agents (
  id INT PRIMARY KEY,
  label TEXT, style TEXT, days INT, total_km NUMERIC,
  province_id INT REFERENCES provinces(id)
);

CREATE TABLE IF NOT EXISTS agent_logs (
  id BIGSERIAL PRIMARY KEY,
  agent_id INT REFERENCES agents(id),
  ts_text TEXT, day_num INT,
  action TEXT, poi_name TEXT, poi_id TEXT,
  lat DOUBLE PRECISION, lon DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS agent_routes (
  id BIGSERIAL PRIMARY KEY,
  agent_id INT REFERENCES agents(id) ON DELETE CASCADE,
  day INT,
  action TEXT,
  target TEXT,
  poi_type_th TEXT,
  t_start_min NUMERIC,
  t_end_min NUMERIC,
  distance_m NUMERIC,
  geom geometry(LINESTRING, 4326)
);

CREATE INDEX IF NOT EXISTS agent_routes_agent_idx ON agent_routes(agent_id, day);
CREATE INDEX IF NOT EXISTS agent_routes_geom_idx ON agent_routes USING GIST (geom);

-- Routes aggregated from JSON/GeoJSON
CREATE TABLE IF NOT EXISTS route_segments (
  id BIGSERIAL PRIMARY KEY,
  province TEXT NOT NULL,
  source_file TEXT,
  seg_id BIGINT,
  from_name TEXT NOT NULL,
  to_name TEXT NOT NULL,
  distance_km NUMERIC,
  travel_time_min NUMERIC,
  energy_kwh NUMERIC,
  ev_cost_thb NUMERIC,
  attrs JSONB
);

CREATE INDEX IF NOT EXISTS route_segments_from_to_idx
  ON route_segments (province, lower(from_name), lower(to_name));

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE TABLE IF NOT EXISTS route_geoms (
  id BIGSERIAL PRIMARY KEY,
  province TEXT NOT NULL,
  source_file TEXT,
  from_name TEXT NOT NULL,
  to_name TEXT NOT NULL,
  geom geometry(LINESTRING, 4326),
  attrs JSONB
);

CREATE INDEX IF NOT EXISTS route_geoms_from_to_idx
  ON route_geoms (province, lower(from_name), lower(to_name));
CREATE INDEX IF NOT EXISTS route_geoms_geom_idx
  ON route_geoms USING GIST (geom);
